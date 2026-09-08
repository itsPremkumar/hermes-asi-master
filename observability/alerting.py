"""
Observability & Evaluation Layer — Alert Manager.

Provides alerting with threshold and anomaly detection.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import threading
import uuid


@dataclass
class AlertRule:
    """An alert rule."""
    rule_id: str
    name: str
    condition: str
    severity: str
    channels: list[str]
    enabled: bool = True


@dataclass
class Alert:
    """An active alert."""
    alert_id: str
    rule_id: str
    name: str
    severity: str
    message: str
    triggered_at: str
    status: str = "active"
    channels: list[str] = field(default_factory=list)


class AlertManager:
    """Alert manager for monitoring and notification."""

    def __init__(self):
        self._rules: dict[str, AlertRule] = {}
        self._active_alerts: dict[str, Alert] = {}
        self._lock = threading.Lock()

    def create_alert(
        self,
        name: str,
        condition: str,
        severity: str,
        channels: list[str],
    ) -> AlertRule:
        """Create an alert rule."""
        rule = AlertRule(
            rule_id=str(uuid.uuid4())[:8],
            name=name,
            condition=condition,
            severity=severity,
            channels=channels,
        )

        with self._lock:
            self._rules[rule.rule_id] = rule

        return rule

    def evaluate_alerts(self, metrics: dict[str, float]) -> list[Alert]:
        """Evaluate all alert rules against current metrics."""
        triggered = []

        with self._lock:
            rules = list(self._rules.values())

        for rule in rules:
            if not rule.enabled:
                continue

            # Simple threshold evaluation
            # Format: "metric_name > value" or "metric_name < value"
            try:
                parts = rule.condition.split()
                if len(parts) == 3:
                    metric_name, operator, threshold = parts
                    threshold = float(threshold)
                    current_value = metrics.get(metric_name, 0)

                    triggered_now = False
                    if operator == ">" and current_value > threshold:
                        triggered_now = True
                    elif operator == "<" and current_value < threshold:
                        triggered_now = True
                    elif operator == "==" and current_value == threshold:
                        triggered_now = True

                    if triggered_now:
                        alert = Alert(
                            alert_id=str(uuid.uuid4())[:8],
                            rule_id=rule.rule_id,
                            name=rule.name,
                            severity=rule.severity,
                            message=f"{metric_name} is {operator} {threshold} (current: {current_value})",
                            triggered_at=datetime.utcnow().isoformat() + "Z",
                            channels=rule.channels,
                        )
                        triggered.append(alert)
                        with self._lock:
                            self._active_alerts[alert.alert_id] = alert

            except (ValueError, IndexError):
                continue

        return triggered

    def send_notification(self, alert: Alert):
        """Send notification for an alert."""
        # In production, this would send to Slack, PagerDuty, email, etc.
        pass

    def get_active_alerts(self, severity: Optional[str] = None) -> list[Alert]:
        """Get active alerts."""
        with self._lock:
            alerts = list(self._active_alerts.values())

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return alerts

    def resolve_alert(self, alert_id: str):
        """Resolve an active alert."""
        with self._lock:
            if alert_id in self._active_alerts:
                self._active_alerts[alert_id].status = "resolved"
