"""Team Health collector — survey aggregation and health scoring."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Sequence

from .models import HealthQuestion, HealthResponse, HealthScore


# Default survey questions — one per category
DEFAULT_QUESTIONS: list[HealthQuestion] = [
    HealthQuestion(
        id="morale-1",
        text="I feel motivated to do my best work on this team",
        category="morale",
    ),
    HealthQuestion(
        id="clarity-1",
        text="I have clear goals and priorities for this sprint",
        category="clarity",
    ),
    HealthQuestion(
        id="tools-1",
        text="I have the tools and infrastructure I need",
        category="tools",
    ),
    HealthQuestion(
        id="process-1",
        text="Our team processes are efficient and not bureaucratic",
        category="process",
    ),
    HealthQuestion(
        id="growth-1",
        text="I have opportunities to learn and grow",
        category="growth",
    ),
]


def load_questions(path: Optional[Path]) -> list[HealthQuestion]:
    if path is None or not path.exists():
        return list(DEFAULT_QUESTIONS)
    raw = json.loads(path.read_text())
    return [HealthQuestion(**q) for q in raw]


def load_responses(path: Path) -> list[HealthResponse]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    responses = []
    for r in raw:
        responses.append(
            HealthResponse(
                question_id=r["question_id"],
                team_member=r["team_member"],
                value=float(r["value"]),
                comment=r.get("comment", ""),
                timestamp=datetime.fromisoformat(r.get("timestamp", datetime.utcnow().isoformat())),
            )
        )
    return responses


class TeamHealthCollector:
    """Collects and scores team health from survey responses."""

    def __init__(
        self,
        questions: Optional[list[HealthQuestion]] = None,
        window_days: int = 90,
    ) -> None:
        self.questions = questions or list(DEFAULT_QUESTIONS)
        self.window_days = window_days

    def collect(
        self, responses: Sequence[HealthResponse]
    ) -> HealthScore:
        cutoff = datetime.utcnow() - timedelta(days=self.window_days)
        window = [r for r in responses if r.timestamp >= cutoff]

        if not window:
            return HealthScore(
                overall=0,
                categories={},
                responses_count=0,
                trend="stable",
            )

        # Per-category scores (average, scaled to 0-100)
        cats: dict[str, list[float]] = {}
        for r in window:
            q = next(
                (q for q in self.questions if q.id == r.question_id), None
            )
            if q is None:
                continue
            scale = q.scale_max
            pct = (r.value / scale) * 100
            cats.setdefault(q.category, []).append(pct)

        categories = {
            cat: round(sum(vals) / len(vals), 1)
            for cat, vals in cats.items()
            if vals
        }

        overall = round(
            sum(categories.values()) / len(categories), 1
        ) if categories else 0.0

        # Trend: compare last 30 days vs prior 30 days
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        recent = [r for r in window if r.timestamp >= recent_cutoff]
        prior = [r for r in window if r.timestamp < recent_cutoff]

        def _avg_score(rs: list[HealthResponse]) -> float:
            if not rs:
                return overall
            total = 0.0
            count = 0
            for r in rs:
                q = next((q for q in self.questions if q.id == r.question_id), None)
                if q is None:
                    continue
                total += (r.value / q.scale_max) * 100
                count += 1
            return total / count if count else overall

        recent_avg = _avg_score(recent)
        prior_avg = _avg_score(prior)

        if recent_avg > prior_avg + 3:
            trend = "improving"
        elif recent_avg < prior_avg - 3:
            trend = "declining"
        else:
            trend = "stable"

        # Flag risks: categories below 50
        flag_risks = [
            cat for cat, score in categories.items() if score < 50
        ]

        return HealthScore(
            overall=overall,
            categories=categories,
            responses_count=len(window),
            trend=trend,
            flag_risks=flag_risks,
        )