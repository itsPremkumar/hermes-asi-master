"""Tests for the CI/CD orchestrator."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from orchestrator.deploy_orchestrator import (
    BlueGreenOrchestrator,
    DeployColor,
    DeploymentConfig,
    VaultClient,
)
from monitoring.monitor import DeploymentEvent, DeploymentMonitor
from vault.secrets import SecretManager


# ── DeploymentConfig ────────────────────────────────────────────────────────


def test_deployment_config_defaults():
    config = DeploymentConfig(app_name="test", namespace="default", image="img", tag="v1", color=DeployColor.BLUE)
    assert config.app_name == "test"
    assert config.namespace == "default"
    assert config.replicas == 2
    assert config.health_path == "/healthz"


def test_deployment_config_custom_env():
    config = DeploymentConfig(
        app_name="test", namespace="ns", image="img", tag="v1",
        color=DeployColor.GREEN, env={"FOO": "bar"}, port=9090,
    )
    assert config.env == {"FOO": "bar"}
    assert config.port == 9090


# ── BlueGreenOrchestrator ───────────────────────────────────────────────────


def test_blue_green_orchestrator_creation():
    config = DeploymentConfig(app_name="test", namespace="default", image="img", tag="v1", color=DeployColor.BLUE)
    orch = BlueGreenOrchestrator(config)
    assert orch.config.color == DeployColor.BLUE


def test_opposite_color():
    config = DeploymentConfig(app_name="test", namespace="default", image="img", tag="v1", color=DeployColor.BLUE)
    orch = BlueGreenOrchestrator(config)
    assert orch._opposite("blue") == "green"
    assert orch._opposite("green") == "blue"


@patch("orchestrator.deploy_orchestrator.K8sClient")
@patch("orchestrator.deploy_orchestrator.VaultClient")
def test_orchestrator_health_check_blue(MockVault, MockK8s):
    """Orchestrator passes when target is healthy."""
    mock_k8s = MagicMock()
    mock_k8s.apps_v1.return_value.read_namespaced_deployment.return_value.status.ready_replicas = 2
    MockK8s.return_value = mock_k8s

    mock_vault = MagicMock()
    mock_vault.get_secret.return_value = {"path": "vault", "secrets": {}}
    MockVault.return_value = mock_vault

    config = DeploymentConfig(app_name="test", namespace="default", image="img", tag="v1", color=DeployColor.BLUE)
    orch = BlueGreenOrchestrator(config, vault=mock_vault)
    result = orch.deploy(dry_run=True)

    assert result["status"] == "dry-run"
    assert "manifest" in result
    assert result["manifest"]["metadata"]["name"] == "test-blue"


@patch("orchestrator.deploy_orchestrator.K8sClient")
@patch("orchestrator.deploy_orchestrator.VaultClient")
def test_orchestrator_health_check_fails_then_rollback(MockVault, MockK8s):
    """Orchestrator rolls back when health check fails."""
    mock_k8s = MagicMock()
    mock_k8s.apps_v1.return_value.read_namespaced_deployment.return_value.status.ready_replicas = 0
    MockK8s.return_value = mock_k8s

    mock_vault = MagicMock()
    mock_vault.get_secret.return_value = {"path": "vault", "secrets": {}}
    MockVault.return_value = mock_vault

    config = DeploymentConfig(
        app_name="test", namespace="default", image="img", tag="v1",
        color=DeployColor.BLUE, readiness_timeout=2,
    )
    orch = BlueGreenOrchestrator(config, vault=mock_vault)
    result = orch.deploy(dry_run=False)

    assert result["status"] == "rolled-back"
    mock_k8s.core_v1.return_value.patch_namespaced_service.assert_called_once()


# ── VaultClient ─────────────────────────────────────────────────────────────


@patch("orchestrator.deploy_orchestrator.VaultClient._get_client")
def test_vault_client_authenticated(MockHvac):
    mock_client = MagicMock()
    mock_client.is_authenticated.return_value = True
    MockHvac.return_value = mock_client

    vault = VaultClient(addr="http://vault:8200", token="test-token")
    assert vault.is_authenticated() is True


@patch("orchestrator.deploy_orchestrator.VaultClient._get_client")
def test_vault_client_unauthenticated(MockHvac):
    mock_client = MagicMock()
    mock_client.is_authenticated.return_value = False
    MockHvac.return_value = mock_client

    vault = VaultClient(addr="http://vault:8200", token="bad")
    assert vault.is_authenticated() is False


@patch("orchestrator.deploy_orchestrator.VaultClient._get_client")
def test_vault_get_secret(MockHvac):
    mock_client = MagicMock()
    mock_client.secrets.kv.v2.read_secret_version.return_value = {
        "data": {"data": {"DB_PASS": "secret123"}}
    }
    MockHvac.return_value = mock_client

    vault = VaultClient(addr="http://vault:8200", token="test-token")
    result = vault.get_secret("secret/data/myapp")
    assert result == {"DB_PASS": "secret123"}


def test_vault_get_secret_import_error(monkeypatch):
    """Falls back to empty dict when hvac is not installed."""
    import importlib
    import sys
    # Block hvac import entirely
    sys.modules['hvac'] = None
    monkeypatch.setitem(sys.modules, 'hvac', None)
    vault = VaultClient(addr="http://vault:8200", token="test")
    result = vault.get_secret("secret/data/myapp")
    assert result == {}
    if 'hvac' in sys.modules:
        del sys.modules['hvac']


# ── DeploymentMonitor ───────────────────────────────────────────────────────


def test_monitor_records_event():
    monitor = DeploymentMonitor()
    event = DeploymentEvent(event_type="deploy", status="success", message="Deployed blue")
    monitor.record(event)
    assert len(monitor.events) == 1


def test_monitor_health_summary():
    monitor = DeploymentMonitor()
    monitor.record(DeploymentEvent(event_type="deploy", status="success", message="ok"))
    monitor.record(DeploymentEvent(event_type="deploy", status="success", message="ok"))
    monitor.record(DeploymentEvent(event_type="deploy", status="failed", message="fail"))
    summary = monitor.health_summary()
    assert summary["total_events"] == 3
    assert summary["success_rate"] == pytest.approx(66.67, abs=0.01)
    assert summary["failure_rate"] == pytest.approx(33.33, abs=0.01)


def test_monitor_consecutive_failures_alert():
    monitor = DeploymentMonitor()
    for _ in range(3):
        monitor.record(DeploymentEvent(event_type="deploy", status="failed", message="fail"))
    assert monitor._failure_count == 3
    summary = monitor.health_summary()
    assert summary["consecutive_failures"] == 3


# ── SecretManager ───────────────────────────────────────────────────────────


@patch.dict(os.environ, {"APP_DB_PASSWORD": "env_secret"})
def test_secret_manager_env_fallback():
    mgr = SecretManager(vault_addr="", vault_token="")
    result = mgr.get_secret("app/db")
    assert result.get("APP_DB_PASSWORD") == "env_secret"


def test_secret_manager_cache():
    mgr = SecretManager()
    with patch.object(mgr, "_read_vault", return_value={"key": "val"}) as mock_read:
        mgr.get_secret("path", mount="secret")
        mgr.get_secret("path", mount="secret")
        assert mock_read.call_count == 1


def test_secret_manager_rotate():
    mgr = SecretManager()
    with patch.object(mgr, "_read_vault", return_value={"key": "val"}):
        mgr.get_secret("path", mount="secret")
    assert mgr.rotate_secret("path", mount="secret") is True
    # Next read should hit vault again
    with patch.object(mgr, "_read_vault", return_value={"key": "new"}) as mock_read:
        mgr.get_secret("path", mount="secret")
        assert mock_read.call_count == 1