"""
P2 Agency & Action — Goal Decomposition Planner

Hierarchical goal/subgoal decomposition with dynamic replanning.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Goal:
    """A goal with subgoals and status tracking."""
    id: str
    description: str
    status: str = "pending"  # pending, active, completed, failed
    priority: float = 0.5
    subgoals: list["Goal"] = field(default_factory=list)
    parent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    retry_count: int = 0
    max_retries: int = 3

    def add_subgoal(self, description: str, priority: float = 0.5) -> "Goal":
        """Add a subgoal."""
        sub = Goal(
            id=str(uuid.uuid4().hex[:8]),
            description=description,
            priority=priority,
            parent_id=self.id,
        )
        self.subgoals.append(sub)
        return sub

    def is_leaf(self) -> bool:
        return len(self.subgoals) == 0

    def is_complete(self) -> bool:
        if self.status == "completed":
            return True
        if self.subgoals:
            return all(sg.is_complete() for sg in self.subgoals)
        return False

    def get_progress(self) -> float:
        """Calculate progress (0.0 to 1.0)."""
        if self.status == "completed":
            return 1.0
        if not self.subgoals:
            return 0.0 if self.status == "pending" else 0.5
        return sum(sg.get_progress() for sg in self.subgoals) / len(self.subgoals)

    def get_next_pending(self) -> "Goal | None":
        """Get the next pending subgoal (depth-first)."""
        if self.status == "pending" and self.is_leaf():
            return self
        for sg in self.subgoals:
            if sg.status == "pending":
                result = sg.get_next_pending()
                if result:
                    return result
        return None


class GoalDecompositionPlanner:
    """Hierarchical planner with dynamic replanning capabilities."""

    def __init__(self, max_depth: int = 5) -> None:
        self.max_depth = max_depth
        self.goals: dict[str, Goal] = {}
        self.active_goal_id: str | None = None
        self.plan_history: list[dict[str, Any]] = []

    def create_goal(self, description: str, priority: float = 0.5) -> Goal:
        """Create a new top-level goal."""
        goal = Goal(
            id=str(uuid.uuid4().hex[:8]),
            description=description,
            priority=priority,
        )
        self.goals[goal.id] = goal
        return goal

    def decompose(self, goal_id: str, subgoals: list[str]) -> list[Goal]:
        """Decompose a goal into subgoals."""
        goal = self.goals.get(goal_id)
        if not goal:
            return []
        for sub_desc in subgoals:
            goal.add_subgoal(sub_desc)
        self.plan_history.append({
            "action": "decompose",
            "goal_id": goal_id,
            "subgoals": subgoals,
        })
        return goal.subgoals

    def get_active_goal(self) -> Goal | None:
        """Get the current active goal."""
        if self.active_goal_id:
            return self.goals.get(self.active_goal_id)
        return None

    def complete_goal(self, goal_id: str, result: Any = None) -> None:
        """Mark a goal as completed."""
        goal = self.goals.get(goal_id)
        if goal:
            goal.status = "completed"
            goal.result = result
            self.plan_history.append({
                "action": "complete",
                "goal_id": goal_id,
            })

    def fail_goal(self, goal_id: str) -> None:
        """Mark a goal as failed."""
        goal = self.goals.get(goal_id)
        if goal:
            goal.status = "failed"
            goal.retry_count += 1
            self.plan_history.append({
                "action": "fail",
                "goal_id:": goal_id,
                "retry_count": goal.retry_count,
            })

    def replan(self, goal_id: str, new_subgoals: list[str]) -> list[Goal]:
        """Replan by replacing subgoals of a goal."""
        goal = self.goals.get(goal_id)
        if not goal:
            return []
        # Clear failed/pending subgoals
        goal.subgoals = []
        for sub_desc in new_subgoals:
            goal.add_subgoal(sub_desc)
        goal.status = "pending"
        self.plan_history.append({
            "action": "replan",
            "goal_id": goal_id,
            "new_subgoals": new_subgoals,
        })
        return goal.subgoals

    def get_progress(self, goal_id: str | None = None) -> float:
        """Get progress of a goal or overall."""
        if goal_id:
            goal = self.goals.get(goal_id)
            return goal.get_progress() if goal else 0.0
        if not self.goals:
            return 0.0
        return sum(g.get_progress() for g in self.goals.values()) / len(self.goals)

    def get_all_pending(self) -> list[Goal]:
        """Get all pending leaf goals."""
        pending = []
        for goal in self.goals.values():
            if goal.status == "pending" and goal.is_leaf():
                pending.append(goal)
        return pending
