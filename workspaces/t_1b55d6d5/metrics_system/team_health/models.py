"""Data models for Team Health metrics."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class HealthQuestion:
    """A single survey question."""

    id: str
    text: str
    category: str  # morale, clarity, tools, process, growth
    scale_max: int = 5  # 1..N Likert scale


@dataclass
class HealthResponse:
    """One team member's response to a question."""

    question_id: str
    team_member: str
    value: float
    comment: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HealthScore:
    """Aggregated health score for a team."""

    overall: float  # 0-100
    categories: dict[str, float]  # category -> score 0-100
    responses_count: int
    trend: str  # improving, stable, declining
    flag_risks: list[str] = field(default_factory=list)

    @property
    def level(self) -> str:
        if self.overall >= 80:
            return "healthy"
        if self.overall >= 60:
            return "at-risk"
        return "critical"