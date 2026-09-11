"""Data models for Flow metrics."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WorkItem:
    """A single work item (ticket, story, PR)."""

    id: str
    title: str
    created: datetime
    started: Optional[datetime] = None
    done: Optional[datetime] = None
    wip_hours: float = 0.0  # total time in "in-progress"
    status: str = "todo"  # todo, in_progress, done, blocked
    assignee: str = ""
    story_points: float = 0.0


@dataclass
class FlowResult:
    """Aggregated Flow metrics over a window."""

    cycle_time_hours: float  # median time from start to done
    throughput: float  # items completed per week
    wip: int  # current items in progress
    load: float  # total story points in progress
    efficiency: float  # productive time / total lead time, 0-1

    @property
    def cycle_time_band(self) -> str:
        if self.cycle_time_hours <= 24:
            return "elite (< 1 day)"
        if self.cycle_time_hours <= 72:
            return "high (1-3 days)"
        if self.cycle_time_hours <= 168:
            return "medium (1 week)"
        return "low (> 1 week)"

    @property
    def throughput_band(self) -> str:
        if self.throughput >= 10:
            return "elite (> 10/week)"
        if self.throughput >= 5:
            return "high (5-10/week)"
        if self.throughput >= 2:
            return "medium (2-5/week)"
        return "low (< 2/week)"