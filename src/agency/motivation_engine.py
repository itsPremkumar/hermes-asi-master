"""
P2.9 — Motivation Engine (Full Spec)

Intrinsic and extrinsic reward modeling for autonomous exploration.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def atomic_file_write(path: str, data: dict | list) -> None:
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


@dataclass
class RewardSignal:
    """A reward signal from any source."""
    source: str
    value: float
    description: str = ""
    timestamp: float = field(default_factory=time.time)


class MotivationEngine:
    """Intrinsic + extrinsic reward modeling with arbitration."""

    def __init__(self, storage_path: str = "./state/motivation") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self.intrinsic_weight = 0.4
        self.extrinsic_weight = 0.6
        self.exploration_rate = 0.2
        self.min_exploration = 0.05
        self.token_budget_factor = 1.0
        self.reward_history: list[RewardSignal] = []
        self.intrinsic_state: dict[str, Any] = {}
        self.extrinsic_state: dict[str, Any] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "motivation_state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                self.intrinsic_weight = data.get("intrinsic_weight", 0.4)
                self.extrinsic_weight = data.get("extrinsic_weight", 0.6)
                self.exploration_rate = data.get("exploration_rate", 0.2)
                self.intrinsic_state = data.get("intrinsic_state", {})
                self.extrinsic_state = data.get("extrinsic_state", {})
            except (json.JSONDecodeError, KeyError):
                pass
        self._loaded = True

    def _save(self) -> None:
        state_path = os.path.join(self.storage_path, "motivation_state.json")
        data = {
            "intrinsic_weight": self.intrinsic_weight,
            "extrinsic_weight": self.extrinsic_weight,
            "exploration_rate": self.exploration_rate,
            "intrinsic_state": self.intrinsic_state,
            "extrinsic_state": self.extrinsic_state,
            "version": "1.0",
        }
        atomic_file_write(state_path, data)

    def compute_intrinsic_reward(self, prediction_error: float, novelty: float) -> float:
        """Compute intrinsic reward from prediction error and novelty."""
        return min(1.0, prediction_error * 0.6 + novelty * 0.4)

    def compute_extrinsic_reward(self, goal_distance: float, milestone_bonus: float = 0.0) -> float:
        """Compute extrinsic reward from goal distance."""
        return min(1.0, (1.0 - goal_distance) * 0.7 + milestone_bonus * 0.3)

    def arbitrate(self, intrinsic: float, extrinsic: float) -> float:
        """Combine intrinsic and extrinsic signals."""
        # Budget-aware: reduce exploration when budget low
        exploration_penalty = max(0, 1.0 - self.token_budget_factor) * 0.3
        rate = max(self.min_exploration, self.exploration_rate - exploration_penalty)
        composite = intrinsic * self.intrinsic_weight + extrinsic * self.extrinsic_weight
        composite *= (1.0 - rate * 0.5)  # slight reduction during exploration
        return composite

    def should_explore(self) -> bool:
        """Decide whether to explore."""
        import random
        return random.random() < self.exploration_rate

    def update_budget_factor(self, budget_remaining: float, budget_total: float) -> None:
        """Update token budget factor."""
        self.token_budget_factor = budget_remaining / max(budget_total, 1)
        self._save()

    def record_reward(self, source: str, value: float, description: str = "") -> None:
        """Record a reward signal."""
        with self._lock:
            signal = RewardSignal(source=source, value=value, description=description)
            self.reward_history.append(signal)
            self._save()

    def get_stats(self) -> dict[str, Any]:
        """Get motivation statistics."""
        return {
            "intrinsic_weight": self.intrinsic_weight,
            "extrinsic_weight": self.extrinsic_weight,
            "exploration_rate": self.exploration_rate,
            "token_budget_factor": self.token_budget_factor,
            "total_rewards": len(self.reward_history),
        }
