"""
P2.10 — Hierarchical Planner (Full Spec)

Multi-horizon planning with adaptive decomposition and dynamic replanning.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import uuid
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
class Goal:
    """A goal in the hierarchy."""
    id: str
    description: str
    status: str = "pending"  # pending, active, completed, failed
    priority: float = 0.5
    depth: int = 0
    parent_id: str | None = None
    subgoals: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Goal":
        return cls(**d)


@dataclass
class Plan:
    """A plan composed of ordered subgoals."""
    id: str
    goal_id: str
    steps: list[str] = field(default_factory=list)
    status: str = "active"
    created_at: float = field(default_factory=time.time)


class HierarchicalPlanner:
    """Multi-horizon planner with adaptive decomposition."""

    def __init__(self, storage_path: str = "./state/plans", max_depth: int = 4) -> None:
        self.storage_path = storage_path
        self.max_depth = max_depth
        self._lock = threading.RLock()
        self.goals: dict[str, Goal] = {}
        self.plans: dict[str, Plan] = {}
        self.plan_history: list[dict[str, Any]] = []
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "plan_state.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for goal_data in data.get("goals", []):
                    goal = Goal.from_dict(goal_data)
                    self.goals[goal.id] = goal
            except (json.JSONDecodeError, KeyError):
                pass
        self._loaded = True

    def _save(self) -> None:
        state_path = os.path.join(self.storage_path, "plan_state.json")
        data = {
            "goals": [g.to_dict() for g in self.goals.values()],
            "version": "1.0",
        }
        atomic_file_write(state_path, data)

    def create_goal(self, description: str, priority: float = 0.5, parent_id: str | None = None) -> Goal:
        """Create a new goal."""
        goal = Goal(
            id=str(uuid.uuid4().hex[:8]),
            description=description,
            priority=priority,
            parent_id=parent_id,
            depth=self._get_depth(parent_id) + 1 if parent_id else 0,
        )
        self.goals[goal.id] = goal
        if parent_id and parent_id in self.goals:
            self.goals[parent_id].subgoals.append(goal.id)
        self._save()
        return goal

    def _get_depth(self, goal_id: str | None) -> int:
        if not goal_id or goal_id not in self.goals:
            return 0
        return self.goals[goal_id].depth

    def decompose(self, goal_id: str, subgoals: list[str]) -> None:
        """Decompose a goal into subgoals."""
        goal = self.goals.get(goal_id)
        if not goal or goal.depth >= self.max_depth:
            return
        for sub_desc in subgoals:
            sub = self.create_goal(sub_desc, parent_id=goal_id)
            goal.subgoals.append(sub.id)
        self._save()

    def get_next_pending(self, goal_id: str | None = None) -> Goal | None:
        """Get the next pending goal (depth-first)."""
        if goal_id:
            goal = self.goals.get(goal_id)
            if not goal:
                return None
            if goal.status == "pending" and not goal.subgoals:
                return goal
            for sub_id in goal.subgoals:
                result = self.get_next_pending(sub_id)
                if result:
                    return result
            return None
        # Find top-level pending goals
        for goal in self.goals.values():
            if goal.parent_id is None and goal.status == "pending":
                result = self.get_next_pending(goal.id)
                if result:
                    return result
        return None

    def complete_goal(self, goal_id: str, result: Any = None) -> None:
        """Mark a goal as completed."""
        goal = self.goals.get(goal_id)
        if goal:
            goal.status = "completed"
            goal.result = result
            self._save()

    def fail_goal(self, goal_id: str) -> None:
        """Mark a goal as failed."""
        goal = self.goals.get(goal_id)
        if goal:
            goal.status = "failed"
            goal.retry_count += 1
            self._save()

    def replan(self, goal_id: str, new_subgoals: list[str]) -> None:
        """Replan by replacing subgoals of a failed goal."""
        goal = self.goals.get(goal_id)
        if not goal:
            return
        # Remove old subgoals
        for sub_id in goal.subgoals:
            if sub_id in self.goals:
                del self.goals[sub_id]
        goal.subgoals = []
        goal.status = "pending"
        self.decompose(goal_id, new_subgoals)
        self._save()

    def get_progress(self, goal_id: str | None = None) -> float:
        """Calculate progress of a goal tree."""
        if goal_id:
            goal = self.goals.get(goal_id)
            if not goal:
                return 0.0
            if goal.status == "completed":
                return 1.0
            if not goal.subgoals:
                return 0.0
            return sum(self.get_progress(sid) for sid in goal.subgoals) / len(goal.subgoals)
        if not self.goals:
            return 0.0
        top_level = [g for g in self.goals.values() if g.parent_id is None]
        return sum(self.get_progress(g.id) for g in top_level) / len(top_level)
