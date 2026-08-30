"""
P2 Agency & Action — Action Selection & Arbitration

Select best action from multiple competing options using expected value, risk, and constraints.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ActionOption:
    """An available action option."""
    id: str
    name: str
    description: str = ""
    expected_value: float = 0.5
    risk: float = 0.5  # 0.0 = safe, 1.0 = risky
    cost: float = 0.5  # resource cost
    constraints: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "expected_value": self.expected_value,
            "risk": self.risk,
            "cost": self.cost,
            "constraints": self.constraints,
            "preconditions": self.preconditions,
        }


class ActionSelectionEngine:
    """Context-aware action selection under uncertainty."""

    def __init__(self, risk_tolerance: float = 0.5, exploration_rate: float = 0.1) -> None:
        self.risk_tolerance = risk_tolerance
        self.exploration_rate = exploration_rate
        self.selection_history: list[dict[str, Any]] = []
        self.action_outcomes: dict[str, list[float]] = {}  # action_id -> list of outcomes

    def evaluate_action(self, action: ActionOption, context: dict[str, Any] | None = None) -> float:
        """Calculate a score for an action based on multiple factors."""
        score = action.expected_value * 0.4  # value component

        # Risk penalty (higher risk = lower score, based on tolerance)
        risk_penalty = max(0, action.risk - self.risk_tolerance) * 0.3
        score -= risk_penalty

        # Cost penalty
        cost_penalty = action.cost * 0.2
        score -= cost_penalty

        # Historical success rate bonus
        if action.id in self.action_outcomes:
            outcomes = self.action_outcomes[action.id]
            success_rate = sum(1 for o in outcomes if o > 0.5) / len(outcomes)
            score += success_rate * 0.2

        # Context bonus
        if context:
            context_tags = context.get("tags", [])
            if any(tag in action.metadata.get("tags", []) for tag in context_tags):
                score += 0.1

        return max(0.0, min(1.0, score))

    def select_action(
        self,
        options: list[ActionOption],
        context: dict[str, Any] | None = None,
    ) -> ActionOption | None:
        """Select the best action from available options."""
        if not options:
            return None

        # Filter by preconditions
        feasible = [
            opt for opt in options
            if self._check_preconditions(opt, context)
        ]
        if not feasible:
            return None

        # Evaluate all options
        scored = [(opt, self.evaluate_action(opt, context)) for opt in feasible]

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Record selection
        self.selection_history.append({
            "selected": scored[0][0].name if scored else None,
            "score": scored[0][1] if scored else 0,
            "options_count": len(options),
            "feasible_count": len(feasible),
        })

        return scored[0][0] if scored else None

    def _check_preconditions(self, action: ActionOption, context: dict[str, Any] | None) -> bool:
        """Check if action preconditions are met."""
        if not action.preconditions:
            return True
        if not context:
            return False
        available = context.get("capabilities", [])
        return all(pre in available for pre in action.preconditions)

    def record_outcome(self, action_id: str, outcome: float) -> None:
        """Record the outcome of an action for future learning."""
        if action_id not in self.action_outcomes:
            self.action_outcomes[action_id] = []
        self.action_outcomes[action_id].append(outcome)

    def get_success_rate(self, action_id: str) -> float:
        """Get historical success rate for an action."""
        outcomes = self.action_outcomes.get(action_id, [])
        if not outcomes:
            return 0.5
        return sum(1 for o in outcomes if o > 0.5) / len(outcomes)

    def get_stats(self) -> dict[str, Any]:
        """Get selection statistics."""
        return {
            "total_selections": len(self.selection_history),
            "actions_tracked": len(self.action_outcomes),
            "avg_success_rate": (
                sum(self.get_success_rate(aid) for aid in self.action_outcomes) / len(self.action_outcomes)
                if self.action_outcomes else 0.0
            ),
        }
