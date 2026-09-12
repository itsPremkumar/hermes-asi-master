"""Blue-Green Deployment Orchestrator.

Manages Kubernetes deployments with blue-green strategy, rollback,
health checks, and vault-integrated secret injection.
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class DeployColor(Enum):
    BLUE = "blue"
    GREEN = "green"


@dataclass
class DeploymentConfig:
    app_name: str
    namespace: str
    image: str
    tag: str
    color: DeployColor
    replicas: int = 2
    env: dict[str, str] = field(default_factory=dict)
    port: int = 8080
    service_port: int = 80
    health_path: str = "/healthz"
    readiness_timeout: int = 300
    rollout_delay: int = 10


class VaultClient:
    """Thin wrapper around HashiCorp Vault for secret retrieval."""

    def __init__(self, addr: Optional[str] = None, token: Optional[str] = None):
        self.addr = addr or os.environ.get("VAULT_ADDR", "http://vault:8200")
        self.token = token or os.environ.get("VAULT_TOKEN", "")
        self._client: Any = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import hvac
            client = hvac.Client(url=self.addr, token=self.token)
            if not self.is_authenticated():
                logger.warning("Vault authentication failed; secrets will be loaded from env fallback")
                return None
            self._client = client
            return client
        except ImportError:
            logger.warning("hvac not installed; falling back to env-based secrets")
            return None

    def is_authenticated(self) -> bool:
        client = self._get_client()
        if client is None:
            return False
        try:
            return client.is_authenticated()
        except Exception:
            return False

    def get_secret(self, path: str) -> dict[str, Any]:
        """Read a KV v2 secret. Falls back to env vars on failure."""
        client = self._get_client()
        if client:
            try:
                resp = client.secrets.kv.v2.read_secret_version(path=path)
                return resp["data"]["data"]
            except Exception as e:
                logger.error("Vault read failed for %s: %s", path, e)
        return {}


class K8sClient:
    """Thin wrapper around the Kubernetes Python client."""

    def __init__(self):
        self._apps_v1: Any = None
        self._core_v1: Any = None

    def _ensure(self):
        if self._apps_v1 is not None:
            return
        try:
            from kubernetes import client, config
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()
            self._apps_v1 = client.AppsV1Api()
            self._core_v1 = client.CoreV1Api()
        except Exception as e:
            logger.error("K8s client init failed: %s", e)
            raise

    def apps_v1(self):
        self._ensure()
        return self._apps_v1

    def core_v1(self):
        self._ensure()
        return self._core_v1


class BlueGreenOrchestrator:
    """Orchestrates blue-green deployments on Kubernetes."""

    def __init__(self, config: DeploymentConfig, vault: Optional[VaultClient] = None):
        self.config = config
        self.vault = vault or VaultClient()
        self.k8s = K8sClient()

    def deploy(self, dry_run: bool = False) -> dict[str, Any]:
        """Execute a full blue-green deployment."""
        result = {"status": "pending", "steps": [], "active_color": self.config.color.value}
        target = self.config.color.value
        opposite = self._opposite(target)

        logger.info("Starting blue-green deploy to %s", target)

        # Step 1: Inject secrets from vault
        secrets = self._load_secrets()
        result["steps"].append({"step": "secrets", "status": "ok", "path": secrets.get("path", "env-fallback")})

        # Step 2: Build the target deployment manifest
        manifest = self._build_deployment_manifest(target, secrets)
        result["steps"].append({"step": "manifest", "status": "ok", "image": f"{self.config.image}:{self.config.tag}"})

        if dry_run:
            result["status"] = "dry-run"
            result["manifest"] = manifest
            return result

        # Step 3: Apply the target deployment
        self._apply_deployment(manifest)
        result["steps"].append({"step": "apply", "status": "ok", "target": target})

        # Step 4: Health check the new target
        healthy = self._wait_for_health(target)
        if not healthy:
            result["status"] = "failed"
            result["steps"].append({"step": "health-check", "status": "failed", "target": target})
            return self.rollback()

        result["steps"].append({"step": "health-check", "status": "ok", "target": target})

        # Step 5: Switch traffic
        self._switch_service(target)
        result["steps"].append({"step": "traffic-switch", "status": "ok", "active": target})

        # Step 6: Wait & scale down old
        time.sleep(self.config.rollout_delay)
        self._scale_deployment(opposite, 0)
        result["steps"].append({"step": "scale-down", "status": "ok", "old_color": opposite})

        result["status"] = "success"
        logger.info("Blue-green deployment to %s completed successfully", target)
        return result

    def rollback(self) -> dict[str, Any]:
        """Rollback by switching traffic back to the opposite color."""
        target = self.config.color.value
        opposite = self._opposite(target)
        logger.info("Rolling back from %s to %s", target, opposite)
        self._switch_service(opposite)
        self._scale_deployment(target, 0)
        self.config.color = DeployColor(opposite)
        logger.info("Rollback complete: %s is now active", opposite)
        return {"status": "rolled-back", "active_color": opposite}

    def _opposite(self, color: str) -> str:
        return "green" if color == "blue" else "blue"

    def _load_secrets(self) -> dict[str, Any]:
        """Load secrets from Vault; fall back to env."""
        secrets = self.vault.get_secret(f"secret/data/cicd/{self.config.app_name}")
        if not secrets:
            logger.info("Using env-based secret fallback")
            secrets = {k: v for k, v in os.environ.items() if k.startswith("APP_")}
        return {"path": "vault", "secrets": secrets} if secrets else {"path": "env-fallback", "secrets": {}}

    def _build_deployment_manifest(self, color: str, secret_data: dict[str, Any]) -> dict[str, Any]:
        """Build a K8s Deployment manifest for the given color."""
        env_vars = [{"name": k, "value": v} for k, v in {**self.config.env, **secret_data.get("secrets", {})}.items()]
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": f"{self.config.app_name}-{color}", "namespace": self.config.namespace},
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": self.config.app_name, "version": color}},
                "template": {
                    "metadata": {"labels": {"app": self.config.app_name, "version": color}},
                    "spec": {
                        "containers": [
                            {
                                "name": self.config.app_name,
                                "image": f"{self.config.image}:{self.config.tag}",
                                "ports": [{"containerPort": self.config.port}],
                                "env": env_vars,
                                "livenessProbe": {
                                    "httpGet": {"path": self.config.health_path, "port": self.config.port},
                                    "initialDelaySeconds": 15,
                                    "periodSeconds": 10,
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": self.config.health_path, "port": self.config.port},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                },
                            }
                        ]
                    },
                },
            },
        }

    def _apply_deployment(self, manifest: dict[str, Any]) -> None:
        """Apply a deployment manifest to the cluster."""
        self.k8s.apps_v1().create_namespaced_deployment(
            namespace=self.config.namespace,
            body=manifest,
        )

    def _wait_for_health(self, color: str, timeout: Optional[int] = None) -> bool:
        """Wait for the deployment to become ready."""
        deadline = time.time() + (timeout or self.config.readiness_timeout)
        while time.time() < deadline:
            try:
                dep = self.k8s.apps_v1().read_namespaced_deployment(
                    name=f"{self.config.app_name}-{color}",
                    namespace=self.config.namespace,
                )
                ready = dep.status.ready_replicas or 0
                if ready >= self.config.replicas:
                    return True
            except Exception as e:
                logger.debug("Health check pending: %s", e)
            time.sleep(5)
        return False

    def _switch_service(self, color: str) -> None:
        """Switch the K8s Service selector to point to the given color."""
        patch = {
            "spec": {
                "selector": {"app": self.config.app_name, "version": color},
                "ports": [{"port": self.config.service_port, "targetPort": self.config.port}],
            }
        }
        self.k8s.core_v1().patch_namespaced_service(
            name=f"{self.config.app_name}-service",
            namespace=self.config.namespace,
            body=patch,
        )

    def _scale_deployment(self, color: str, replicas: int) -> None:
        """Scale a deployment to the given replica count."""
        from kubernetes.client import V1Deployment, V1Scale
        self.k8s.apps_v1().scale_namespaced_deployment(
            name=f"{self.config.app_name}-{color}",
            namespace=self.config.namespace,
            replicas=replicas,
        )


def cli():
    """CLI entry point."""
    import click

    @click.group()
    def cli():
        pass

    @cli.command()
    @click.option("--app", required=True, help="Application name")
    @click.option("--namespace", default="default", help="K8s namespace")
    @click.option("--image", required=True, help="Container image")
    @click.option("--tag", required=True, help="Image tag")
    @click.option("--color", type=click.Choice(["blue", "green"]), required=True, help="Deploy color")
    @click.option("--dry-run", is_flag=True, help="Print manifest without applying")
    def deploy(app, namespace, image, tag, color, dry_run):
        """Deploy using blue-green strategy."""
        config = DeploymentConfig(
            app_name=app,
            namespace=namespace,
            image=image,
            tag=tag,
            color=DeployColor(color),
        )
        orch = BlueGreenOrchestrator(config)
        result = orch.deploy(dry_run=dry_run)
        click.echo(json.dumps(result, indent=2))

    @cli.command()
    @click.option("--app", required=True, help="Application name")
    @click.option("--namespace", default="default", help="K8s namespace")
    @click.option("--color", type=click.Choice(["blue", "green"]), required=True, help="Current active color")
    def rollback(app, namespace, color):
        """Rollback to the opposite color."""
        config = DeploymentConfig(app_name=app, namespace=namespace, image="", tag="", color=DeployColor(color))
        orch = BlueGreenOrchestrator(config)
        result = orch.rollback()
        click.echo(json.dumps(result, indent=2))

    cli()