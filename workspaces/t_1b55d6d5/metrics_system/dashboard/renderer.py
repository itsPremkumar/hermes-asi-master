"""Dashboard renderer — produces markdown and console views."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..dora.models import DORAResult
from ..flow.models import FlowResult
from ..team_health.models import HealthScore
from .config import DashboardConfig


class DashboardRenderer:
    """Renders the engineering metrics dashboard."""

    def __init__(self, config: Optional[DashboardConfig] = None) -> None:
        self.config = config or DashboardConfig()

    def render_markdown(
        self,
        dora: Optional[DORAResult] = None,
        flow: Optional[FlowResult] = None,
        health: Optional[HealthScore] = None,
    ) -> str:
        lines = [
            f"# {self.config.title}",
            f"*Last updated: {datetime.utcnow().isoformat()}Z*\n",
        ]

        # DORA section
        lines.append("## DORA Metrics")
        if dora:
            lines.append(f"- **Deployment Frequency**: {dora.deployment_frequency.get('daily', 0)}/day — {dora.deployment_band}")
            lines.append(f"- **Lead Time**: {dora.median_lead_time_hours:.1f}h — {dora.lead_time_band}")
            lines.append(f"- **Change Failure Rate**: {dora.change_fail_rate:.1%} — {dora.failure_band}")
            lines.append(f"- **Time to Restore**: {dora.median_restore_hours or 'N/A'}h — {dora.restore_band}")
        else:
            lines.append("_No DORA data available._")
        lines.append("")

        # Flow section
        lines.append("## Flow Metrics")
        if flow:
            lines.append(f"- **Cycle Time**: {flow.cycle_time_hours:.1f}h — {flow.cycle_time_band}")
            lines.append(f"- **Throughput**: {flow.throughput:.1f}/week — {flow.throughput_band}")
            lines.append(f"- **WIP**: {flow.wip} items (load: {flow.load:.1f} pts)")
            lines.append(f"- **Efficiency**: {flow.efficiency:.0%}")
        else:
            lines.append("_No Flow data available._")
        lines.append("")

        # Team Health section
        lines.append("## Team Health")
        if health:
            lines.append(f"- **Overall Score**: {health.overall}/100 — {health.level}")
            lines.append(f"- **Trend**: {health.trend}")
            for cat, score in health.categories.items():
                lines.append(f"  - {cat}: {score}/100")
            if health.flag_risks:
                lines.append(f"- **Risks**: {', '.join(health.flag_risks)}")
        else:
            lines.append("_No health survey data available._")
        lines.append("")

        return "\n".join(lines)

    def render_console(
        self,
        dora: Optional[DORAResult] = None,
        flow: Optional[FlowResult] = None,
        health: Optional[HealthScore] = None,
    ) -> str:
        """Compact single-line summary for terminal output."""
        parts = ["[Engineering Metrics]"]
        if dora:
            parts.append(f"DF={dora.deployment_frequency.get('daily', 0)}/d")
            parts.append(f"LT={dora.median_lead_time_hours:.0f}h")
            parts.append(f"CFR={dora.change_fail_rate:.0%}")
        if flow:
            parts.append(f"CT={flow.cycle_time_hours:.0f}h")
            parts.append(f"TP={flow.throughput:.1f}/wk")
        if health:
            parts.append(f"Health={health.overall}/100({health.level})")
        return " | ".join(parts)