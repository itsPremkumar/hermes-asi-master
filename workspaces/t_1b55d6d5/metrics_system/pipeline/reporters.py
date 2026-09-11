"""Report reporters — console, JSON, Markdown."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..dora.models import DORAResult
from ..flow.models import FlowResult
from ..team_health.models import HealthScore


@dataclass
class ReportBundle:
    generated_at: datetime
    dora: DORAResult
    flow: FlowResult
    health: HealthScore

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at.isoformat(),
            "dora": {
                "deployment_frequency": self.dora.deployment_frequency,
                "median_lead_time_hours": self.dora.median_lead_time_hours,
                "change_fail_rate": self.dora.change_fail_rate,
                "median_restore_hours": self.dora.median_restore_hours,
                "lead_time_band": self.dora.lead_time_band,
                "deployment_band": self.dora.deployment_band,
                "failure_band": self.dora.failure_band,
                "restore_band": self.dora.restore_band,
            },
            "flow": {
                "cycle_time_hours": self.flow.cycle_time_hours,
                "throughput": self.flow.throughput,
                "wip": self.flow.wip,
                "load": self.flow.load,
                "efficiency": self.flow.efficiency,
                "cycle_time_band": self.flow.cycle_time_band,
                "throughput_band": self.flow.throughput_band,
            },
            "health": {
                "overall": self.health.overall,
                "categories": self.health.categories,
                "responses_count": self.health.responses_count,
                "trend": self.health.trend,
                "flag_risks": self.health.flag_risks,
                "level": self.health.level,
            },
        }


class ConsoleReporter:
    """Prints compact report to stdout."""

    def write(self, bundle: ReportBundle) -> None:
        from ..dashboard.renderer import DashboardRenderer

        renderer = DashboardRenderer()
        print(renderer.render_console(
            dora=bundle.dora,
            flow=bundle.flow,
            health=bundle.health,
        ))


class JSONReporter:
    """Writes JSON report to file."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir

    def write(self, bundle: ReportBundle) -> Optional[str]:
        data = bundle.to_dict()
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "report.json"
            path.write_text(json.dumps(data, indent=2))
            return str(path)
        return None


class MarkdownReporter:
    """Writes Markdown dashboard to file."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir

    def write(self, bundle: ReportBundle) -> Optional[str]:
        from ..dashboard.renderer import DashboardRenderer
        from ..dashboard.config import DashboardConfig

        renderer = DashboardRenderer()
        md = renderer.render_markdown(
            dora=bundle.dora,
            flow=bundle.flow,
            health=bundle.health,
        )
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "dashboard.md"
            path.write_text(md)
            return str(path)
        return None