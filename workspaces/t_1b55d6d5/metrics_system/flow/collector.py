"""Flow metrics collector — cycle time, throughput, WIP, load, efficiency."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Sequence

from .models import FlowResult, WorkItem


def load_work_items(path: Path) -> list[WorkItem]:
    """Load work items from a JSON file."""
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    items = []
    for item in raw:
        started = (
            datetime.fromisoformat(item["started"])
            if item.get("started")
            else None
        )
        done = (
            datetime.fromisoformat(item["done"]) if item.get("done") else None
        )
        items.append(
            WorkItem(
                id=item["id"],
                title=item.get("title", ""),
                created=datetime.fromisoformat(item["created"]),
                started=started,
                done=done,
                wip_hours=float(item.get("wip_hours", 0)),
                status=item.get("status", "todo"),
                assignee=item.get("assignee", ""),
                story_points=float(item.get("story_points", 0)),
            )
        )
    return items


class FlowMetricsCollector:
    """Computes Flow metrics from work item data."""

    def __init__(self, window_days: int = 28) -> None:
        self.window_days = window_days

    def collect(
        self, items: Sequence[WorkItem]
    ) -> FlowResult:
        cutoff = datetime.utcnow() - timedelta(days=self.window_days)
        window = [i for i in items if i.created >= cutoff]
        done = [i for i in window if i.status == "done" and i.done]

        # Cycle time: median start-to-done for completed items
        cycles = []
        productive_hours = 0.0
        total_lead_hours = 0.0
        for i in done:
            delta = (i.done - i.started).total_seconds() / 3600 if i.started else 0
            cycles.append(delta)
            lead = (i.done - i.created).total_seconds() / 3600
            total_lead_hours += lead
            productive_hours += delta

        median_cycle = (
            float(sorted(cycles)[len(cycles) // 2]) if cycles else 0.0
        )

        # Throughput — completed per week
        weeks = max(
            1,
            (datetime.utcnow() - min((i.created for i in done), default=datetime.utcnow())).days
            / 7,
        )
        throughput = len(done) / weeks

        # Current WIP and load
        wip_items = [i for i in window if i.status == "in_progress"]
        wip = len(wip_items)
        load = sum(i.story_points for i in wip_items)

        # Efficiency
        efficiency = (
            round(productive_hours / total_lead_hours, 2)
            if total_lead_hours > 0
            else 0.0
        )

        return FlowResult(
            cycle_time_hours=median_cycle,
            throughput=round(throughput, 2),
            wip=wip,
            load=load,
            efficiency=efficiency,
        )