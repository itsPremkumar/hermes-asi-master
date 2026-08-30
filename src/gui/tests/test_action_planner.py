"""Tests for action_planner.py."""
import pytest
from gui.action_planner import ActionPlanner, ActionPlan, ActionStep


class TestActionStep:
    def test_create(self):
        step = ActionStep(id="s1", action="click", description="Click button")
        assert step.id == "s1"
        assert step.action == "click"
        assert step.status == "pending"

    def test_to_dict(self):
        step = ActionStep(id="s1", action="click")
        d = step.to_dict()
        assert d["id"] == "s1"
        assert d["action"] == "click"


class TestActionPlan:
    def test_create(self):
        plan = ActionPlan(id="p1", name="test plan")
        assert plan.id == "p1"
        assert plan.name == "test plan"
        assert plan.status == "draft"

    def test_add_step(self):
        plan = ActionPlan(id="p1", name="test")
        step = plan.add_step("click", "Click button")
        assert len(plan.steps) == 1
        assert step.action == "click"

    def test_get_next_step(self):
        plan = ActionPlan(id="p1", name="test")
        plan.add_step("click", "Click")
        plan.add_step("type", "Type text")
        next_step = plan.get_next_step()
        assert next_step is not None
        assert next_step.action == "click"

    def test_complete_step(self):
        plan = ActionPlan(id="p1", name="test")
        step = plan.add_step("click", "Click")
        assert plan.complete_step(step.id)
        assert step.status == "completed"

    def test_fail_step(self):
        plan = ActionPlan(id="p1", name="test")
        step = plan.add_step("click", "Click")
        assert plan.fail_step(step.id)
        assert step.status == "failed"

    def test_get_progress(self):
        plan = ActionPlan(id="p1", name="test")
        step1 = plan.add_step("click", "Click")
        step2 = plan.add_step("type", "Type")
        assert plan.get_progress() == 0.0
        plan.complete_step(step1.id)
        assert plan.get_progress() == 0.5
        plan.complete_step(step2.id)
        assert plan.get_progress() == 1.0

    def test_is_complete(self):
        plan = ActionPlan(id="p1", name="test")
        step = plan.add_step("click", "Click")
        assert not plan.is_complete()
        plan.complete_step(step.id)
        assert plan.is_complete()

    def test_reset(self):
        plan = ActionPlan(id="p1", name="test")
        step = plan.add_step("click", "Click")
        plan.complete_step(step.id)
        assert step.status == "completed"
        plan.reset()
        assert step.status == "pending"


class TestActionPlanner:
    def test_create(self):
        planner = ActionPlanner()
        assert len(planner.plans) == 0

    def test_create_plan(self):
        planner = ActionPlanner()
        plan = planner.create_plan("test")
        assert plan.id in planner.plans
        assert plan.name == "test"

    def test_get_plan(self):
        planner = ActionPlanner()
        created = planner.create_plan("test")
        retrieved = planner.get_plan(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_delete_plan(self):
        planner = ActionPlanner()
        plan = planner.create_plan("test")
        assert planner.delete_plan(plan.id)
        assert plan.id not in planner.plans

    def test_list_plans(self):
        planner = ActionPlanner()
        planner.create_plan("plan1")
        planner.create_plan("plan2")
        assert len(planner.list_plans()) == 2

    def test_execute_next(self):
        planner = ActionPlanner()
        plan = planner.create_plan("test")
        plan.add_step("click", "Click")
        step = planner.execute_next(plan.id)
        assert step is not None
        assert step.status == "running"

    def test_complete_current(self):
        planner = ActionPlanner()
        plan = planner.create_plan("test")
        plan.add_step("click", "Click")
        planner.execute_next(plan.id)
        assert planner.complete_current(plan.id)
        assert plan.steps[0].status == "completed"
