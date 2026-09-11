"""Data models for DORA metrics collection."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class DeploymentRecord:
    """One deployment event."""

    id: str
    timestamp: datetime
    environment: str  # production, staging, etc.
    status: str  # success, failed, rolled_back
    lead_time_hours: float  # commit to deploy
    change_failed: bool = False
    restore_time_hours: Optional[float] = None


@dataclass
class DORAResult:
    """Aggregated DORA metrics over a window."""

    deployment_frequency: dict  # e.g. {"daily": 0.8, "weekly": 3.2}
    median_lead_time_hours: float
    change_fail_rate: float  # 0.0 - 1.0
    median_restore_hours: Optional[float]

    # Bounding bands per DORA research
    @property
    def lead_time_band(self) -> str:
        if self.median_lead_time_hours <= 1:
            return "elite (< 1 hour)"
        if self.median_lead_time_hours <= 24:
            return "high (1-24 hours)"
        if self.median_lead_time_hours <= 168:
            return "medium (1-7 days)"
        return "low (> 7 days)"

    @property
    def deployment_band(self) -> str:
        freq = self.deployment_frequency.get("daily", 0)
        if freq >= 1:
            return "elite (multiple/day)"
        if freq >= 0.5:
            return "high (once/day)"
        if freq >= 0.1:
            return "medium (1/week)"
        return "low (< 1/week)"

    @property
    def failure_band(self) -> str:
        if self.change_fail_rate <= 0.05:
            return "elite (< 5%)"
        if self.change_fail_rate <= 0.15:
            return "high (5-15%)"
        if self.change_fail_rate <= 0.45:
            return "medium (15-45%)"
        return "low (> 45%)"

    @property
    def restore_band(self) -> str:
        if self.median_restore_hours is None:
            return "no data"
        if self.median_restore_hours <= 1:
            return "elite (< 1 hour)"
        if self.median_restore_hours <= 24:
            return "high (1-24 hours)"
        if self.median_restore_hours <= 72:
            return "medium (1-3 days)"
        return "low (> 3 days)"


@dataclass
class DORAConfig:
    """Configuration for DORA collection."""

    window_days: int = 28
    production_env: str = "production"
    min_deployments_for_band: int = 3