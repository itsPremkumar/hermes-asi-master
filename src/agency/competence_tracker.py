"""
P2.9.2 — Competence Tracker

Tracks agent competence in different domains.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CompetenceEstimate:
    """Estimated competence in a domain."""
    domain: str
    estimated: float  # 0.0 to 1.0
    actual: float  # 0.0 to 1.0
    sample_count: int = 0
    timestamp: float = field(default_factory=time.time)


class CompetenceTracker:
    """Track agent competence across domains."""

    def __init__(self) -> None:
        self.competences: dict[str, dict[str, float]] = {}  # domain -> {successes, attempts, competence}
        self.history: list[CompetenceEstimate] = []

    def record_attempt(self, domain: str, success: bool) -> None:
        """Record an attempt in a domain."""
        if domain not in self.competences:
            self.competences[domain] = {"successes": 0.0, "attempts": 0.0}
        self.competences[domain]["attempts"] += 1
        if success:
            self.competences[domain]["successes"] += 1

    def get_competence(self, domain: str) -> float:
        """Get estimated competence in a domain (0.0 to 1.0)."""
        if domain not in self.competences:
            return 0.5  # Unknown domain
        stats = self.competences[domain]
        if stats["attempts"] == 0:
            return 0.5
        # Wilson score lower bound for 95% confidence
        n = stats["attempts"]
        p = stats["successes"] / n
        z = 1.96  # 95% confidence
        denominator = 1 + z * z / n
        centre = p + z * z / (2 * n)
        spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
        return max(0.0, (centre - spread) / denominator)

    def estimate_accuracy(self, domain: str, actual_performance: float) -> float:
        """Calculate estimation accuracy vs actual performance."""
        estimated = self.get_competence(domain)
        return 1.0 - abs(estimated - actual_performance)

    def get_all_competences(self) -> dict[str, float]:
        """Get all domain competences."""
        return {domain: self.get_competence(domain) for domain in self.competences}
