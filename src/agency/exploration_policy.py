"""
P2.9.4 — Exploration Policy

Policy for when to explore vs exploit based on motivation signals.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any


@dataclass
class ExplorationDecision:
    """Decision to explore or exploit."""
    action: str  # "explore" or "exploit"
    confidence: float
    reason: str


class ExplorationPolicy:
    """Epsilon-greedy exploration policy with motivation modulation."""

    def __init__(self, base_exploration_rate: float = 0.2, min_rate: float = 0.05) -> None:
        self.base_rate = base_exploration_rate
        self.min_rate = min_rate
        self.exploration_count = 0
        self.exploit_count = 0

    def should_explore(self, motivation: float, competence: float) -> ExplorationDecision:
        """Decide whether to explore or exploit."""
        # Higher motivation = more exploration
        # Higher competence = less exploration (more exploitation)
        rate = self.base_rate * motivation * (1.0 - competence * 0.5)
        rate = max(self.min_rate, min(0.8, rate))

        if random.random() < rate:
            self.exploration_count += 1
            return ExplorationDecision(
                action="explore",
                confidence=rate,
                reason=f"Exploration rate {rate:.2f} (motivation={motivation:.2f}, competence={competence:.2f})",
            )
        self.exploit_count += 1
        return ExplorationDecision(
            action="exploit",
            confidence=1.0 - rate,
            reason=f"Exploiting (rate={rate:.2f})",
        )

    def get_stats(self) -> dict[str, int]:
        return {
            "explorations": self.exploration_count,
            "exploits": self.exploit_count,
        }
