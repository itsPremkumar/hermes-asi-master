"""Monitoring & alerting for the CI/CD orchestrator."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class DeploymentEvent:
    timestamp: float = field(default_factory=time.time)
    event_type: str = ""
    color: str = ""
    status: str = ""
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat(),
            "event_type": self.event_type,
            "color": self.color,
            "status": self.status,
            "message": self.message,
            "metadata": self.metadata,
        }


class DeploymentMonitor:
    """Tracks deployment events and emits alerts."""

    def __init__(self):
        self.events: list[DeploymentEvent] = []
        self.alert_threshold = 3  # consecutive failures before alert
        self._failure_count = 0

    def record(self, event: DeploymentEvent) -> None:
        """Record a deployment event."""
        self.events.append(event)
        logger.info("[%s] %s — %s", event.event_type, event.status, event.message)

        if event.status == "failed":
            self._failure_count += 1
            if self._failure_count >= self.alert_threshold:
                self._trigger_alert("consecutive_failures", f"{self._failure_count} failures in a row")
        else:
            self._failure_count = 0

    def get_events(self, event_type: Optional[str] = None) -> list[dict[str, Any]]:
        """Return events, optionally filtered by type."""
        if event_type:
            return [e.to_dict() for e in self.events if e.event_type == event_type]
        return [e.to_dict() for e in self.events]

    def recent_failures(self, window_seconds: int = 300) -> list[dict[str, Any]]:
        """Return failures in the last N seconds."""
        cutoff = time.time() - window_seconds
        return [
            e.to_dict()
            for e in self.events
            if e.status == "failed" and e.timestamp >= cutoff
        ]

    def health_summary(self) -> dict[str, Any]:
        """Return a health summary of all deployments."""
        total = len(self.events)
        failed = sum(1 for e in self.events if e.status == "failed")
        success = sum(1 for e in self.events if e.status == "success")
        return {
            "total_events": total,
            "success_rate": (success / total * 100) if total > 0 else 100.0,
            "failure_rate": (failed / total * 100) if total > 0 else 0.0,
            "consecutive_failures": self._failure_count,
            "recent_failures_5m": len(self.recent_failures(300)),
        }

    def _trigger_alert(self, alert_type: str, message: str) -> None:
        """Emit an alert."""
        logger.warning("ALERT [%s]: %s", alert_type, message)


def check_deployment_health(app_name: str, namespace: str, color: str) -> dict[str, Any]:
    """Check the health of a deployment."""
    try:
        from kubernetes import client, config
        try:
            config.load_incluster_config()
        except Exception:
            config.load_kube_config()

        apps_v1 = client.AppsV1Api()
        dep = apps_v1.read_namespaced_deployment(
            name=f"{app_name}-{color}", namespace=namespace
        )
        ready = dep.status.ready_replicas or 0
        desired = dep.spec.replicas or 0
        return {
            "healthy": ready >= desired,
            "ready_replicas": ready,
            "desired_replicas": desired,
            "color": color,
        }
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return {"healthy": False, "error": str(e), "color": color}