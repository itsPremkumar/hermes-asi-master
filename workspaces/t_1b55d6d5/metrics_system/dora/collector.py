"""DORA metrics collector — computes Deployment Frequency, Lead Time,
Change Failure Rate, and Time to Restore from deployment records."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Sequence

from .models import DORAConfig, DORAResult, DeploymentRecord


def load_deployments(path: Path) -> list[DeploymentRecord]:
    """Load deployment records from a JSON file."""
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    records = []
    for item in raw:
        records.append(
            DeploymentRecord(
                id=item["id"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                environment=item.get("environment", "production"),
                status=item.get("status", "success"),
                lead_time_hours=float(item.get("lead_time_hours", 0)),
                change_failed=item.get("change_failed", False),
                restore_time_hours=item.get("restore_time_hours"),
            )
        )
    return records


class DORAMetricsCollector:
    """Collects and computes DORA metrics over a configurable window."""

    def __init__(self, config: Optional[DORAConfig] = None) -> None:
        self.config = config or DORAConfig()

    def collect(
        self, deployments: Sequence[DeploymentRecord]
    ) -> DORAResult:
        cutoff = datetime.utcnow() - timedelta(days=self.config.window_days)
        window = [d for d in deployments if d.timestamp >= cutoff]
        prod = [d for d in window if d.environment == self.config.production_env]

        if not prod:
            return DORAResult(
                deployment_frequency={},
                median_lead_time_hours=0,
                change_fail_rate=0,
                median_restore_hours=None,
            )

        # Deployment frequency — deployments per day
        days = max(
            1,
            (datetime.utcnow() - min(d.timestamp for d in prod)).days,
        )
        freq_per_day = len(prod) / days

        # Lead time — median commit-to-deploy hours
        lead_times = sorted(d.lead_time_hours for d in prod if d.lead_time_hours > 0)
        median_lead = (
            float(lead_times[len(lead_times) // 2]) if lead_times else 0.0
        )

        # Change failure rate
        failures = sum(1 for d in prod if d.change_failed)
        fail_rate = failures / len(prod)

        # Time to restore — median restore time for failed deploys
        restores = sorted(
            d.restore_time_hours
            for d in prod
            if d.change_failed and d.restore_time_hours is not None
        )
        median_restore = (
            float(restores[len(restores) // 2]) if restores else None
        )

        return DORAResult(
            deployment_frequency={
                "daily": round(freq_per_day, 2),
                "weekly": round(freq_per_day * 7, 2),
            },
            median_lead_time_hours=median_lead,
            change_fail_rate=round(fail_rate, 4),
            median_restore_hours=median_restore,
        )