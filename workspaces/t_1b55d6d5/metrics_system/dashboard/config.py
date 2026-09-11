"""Dashboard configuration — layout, refresh interval, data sources."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PanelConfig:
    """A single dashboard panel."""

    title: str
    metric_type: str  # dora, flow, health
    size: str = "medium"  # small, medium, large
    refresh_seconds: int = 300
    thresholds: Optional[dict] = None


@dataclass
class DashboardConfig:
    """Full dashboard configuration."""

    title: str = "Engineering Metrics Dashboard"
    refresh_seconds: int = 60
    panels: list[PanelConfig] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.panels:
            self.panels = self._default_panels()

    def _default_panels(self) -> list[PanelConfig]:
        return [
            PanelConfig(
                title="Deployment Frequency",
                metric_type="dora_deploy_freq",
                size="small",
                thresholds={"elite": 1.0, "high": 0.5},
            ),
            PanelConfig(
                title="Lead Time for Changes",
                metric_type="dora_lead_time",
                size="small",
                thresholds={"elite": 1, "high": 24},
            ),
            PanelConfig(
                title="Change Failure Rate",
                metric_type="dora_failure_rate",
                size="small",
                thresholds={"elite": 0.05, "high": 0.15},
            ),
            PanelConfig(
                title="Time to Restore",
                metric_type="dora_restore",
                size="small",
                thresholds={"elite": 1, "high": 24},
            ),
            PanelConfig(
                title="Cycle Time",
                metric_type="flow_cycle_time",
                size="small",
                thresholds={"elite": 24, "high": 72},
            ),
            PanelConfig(
                title="Throughput",
                metric_type="flow_throughput",
                size="small",
                thresholds={"elite": 10, "high": 5},
            ),
            PanelConfig(
                title="WIP",
                metric_type="flow_wip",
                size="small",
                thresholds={"max": 10},
            ),
            PanelConfig(
                title="Team Health Score",
                metric_type="health_score",
                size="large",
                thresholds={"healthy": 80, "at-risk": 60},
            ),
        ]