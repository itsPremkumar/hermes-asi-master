"""
t_8d067e7d — Action Planner for GUI

Single-file action planner with 8 tests. No goal_mode dependency.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ActionStep:
    """A single action step."""
    id: str
    action: str
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "action": self.action,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status,
        }


@dataclass
class ActionPlan:
    """A plan composed of action steps."""
    id: str
    name: str
    steps: list[ActionStep] = field(default_factory=list)
    status: str = "draft"  # draft, executing, completed, failed

    def add_step(self, action: str, description: str = "", parameters: dict[str, Any] | None = None) -> ActionStep:
        step = ActionStep(
            id=str(uuid.uuid4().hex[:8]),
            action=action,
            description=description,
            parameters=parameters or {},
        )
        self.steps.append(step)
        return step

    def get_next_step(self) -> Optional[ActionStep]:
        for step in self.steps:
            if step.status == "pending":
                return step
        return None

    def complete_step(self, step_id: str) -> bool:
        for step in self.steps:
            if step.id == step_id:
                step.status = "completed"
                return True
        return False

    def fail_step(self, step_id: str) -> bool:
        for step in self.steps:
            if step.id == step_id:
                step.status = "failed"
                return True
        return False

    def get_progress(self) -> float:
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == "completed")
        return completed / len(self.steps)

    def is_complete(self) -> bool:
        return all(s.status == "completed" for s in self.steps)

    def reset(self) -> None:
        for step in self.steps:
            step.status = "pending"
        self.status = "draft"


class ActionPlanner:
    """Create and manage action plans."""

    def __init__(self) -> None:
        self.plans: dict[str, ActionPlan] = {}

    def create_plan(self, name: str) -> ActionPlan:
        plan = ActionPlan(id=str(uuid.uuid4().hex[:8]), name=name)
        self.plans[plan.id] = plan
        return plan

    def get_plan(self, plan_id: str) -> Optional[ActionPlan]:
        return self.plans.get(plan_id)

    def delete_plan(self, plan_id: str) -> bool:
        if plan_id in self.plans:
            del self.plans[plan_id]
            return True
        return False

    def list_plans(self) -> list[ActionPlan]:
        return list(self.plans.values())

    def execute_next(self, plan_id: str) -> Optional[ActionStep]:
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        step = plan.get_next_step()
        if step:
            step.status = "running"
        return step

    def complete_current(self, plan_id: str) -> bool:
        plan = self.plans.get(plan_id)
        if not plan:
            return False
        for step in plan.steps:
            if step.status == "running":
                step.status = "completed"
                return True
        return False
