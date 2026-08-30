"""
P2.9.1 — Curiosity Scorer

Scores how novel/curious a situation is based on prediction error from world model.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CuriosityScore:
    """A curiosity score for a situation."""
    situation_id: str
    score: float  # 0.0 to 1.0
    prediction_error: float
    novelty: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class CuriosityScorer:
    """Scores situation novelty using prediction error."""

    def __init__(self, decay_rate: float = 0.01) -> None:
        self.decay_rate = decay_rate
        self.known_situations: dict[str, float] = {}  # situation_hash -> predicted_value
        self.score_history: list[CuriosityScore] = []

    def compute_novelty(self, situation: dict[str, Any]) -> float:
        """Compute novelty of a situation (0.0 = familiar, 1.0 = completely novel)."""
        situation_hash = self._hash_situation(situation)
        if situation_hash not in self.known_situations:
            return 1.0  # Completely novel
        # Familiarity decays over time
        familiarity = self.known_situations[situation_hash]
        return max(0.0, 1.0 - familiarity)

    def compute_prediction_error(self, predicted: float, actual: float) -> float:
        """Compute prediction error between expected and actual outcome."""
        return abs(predicted - actual)

    def score(self, situation: dict[str, Any], predicted: float | None = None, actual: float | None = None) -> CuriosityScore:
        """Score a situation for curiosity."""
        novelty = self.compute_novelty(situation)
        prediction_error = 0.0
        if predicted is not None and actual is not None:
            prediction_error = self.compute_prediction_error(predicted, actual)

        # Curiosity = weighted combination of novelty and prediction error
        score = novelty * 0.6 + prediction_error * 0.4
        score = min(1.0, max(0.0, score))

        result = CuriosityScore(
            situation_id=self._hash_situation(situation),
            score=score,
            prediction_error=prediction_error,
            novelty=novelty,
        )
        self.score_history.append(result)

        # Update known situations
        situation_hash = self._hash_situation(situation)
        self.known_situations[situation_hash] = min(
            1.0, self.known_situations.get(situation_hash, 0.0) + 0.1
        )

        return result

    def _hash_situation(self, situation: dict[str, Any]) -> str:
        """Create a hash for a situation."""
        import hashlib
        import json
        return hashlib.md5(json.dumps(situation, sort_keys=True, default=str).encode()).hexdigest()[:12]

    def get_history(self, limit: int = 100) -> list[CuriosityScore]:
        """Get recent curiosity scores."""
        return self.score_history[-limit:]
