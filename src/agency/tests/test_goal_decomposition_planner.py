"""Tests for goal_decomposition_planner.py."""
import pytest
from agency.goal_decomposition_planner import Goal, GoalDecompositionPlanner


class TestGoal:
    def test_create(self):
        g = Goal(id="g1", description="Test goal")
        assert g.id == "g1"
        assert g.description == "Test goal"
        assert g.status == "pending"

    def test_add_subgoal(self):
        g = Goal(id="g1", description="Parent")
        sub = g.add_subgoal("Child goal")
        assert sub.parent_id == "g1"
        assert sub.description == "Child goal"
        assert len(g.subgoals) == 1

    def test_is_leaf(self):
        g = Goal(id="g1", description="Test")
        assert g.is_leaf() is True
        g.add_subgoal("Child")
        assert g.is_leaf() is False

    def test_is_complete_leaf(self):
        g = Goal(id="g1", description="Test", status="completed")
        assert g.is_complete() is True

    def test_is_complete_parent(self):
        g = Goal(id="g1", description="Parent")
        g.add_subgoal("Child 1")
        g.add_subgoal("Child 2")
        g.subgoals[0].status = "completed"
        g.subgoals[1].status = "completed"
        assert g.is_complete() is True

    def test_get_progress_leaf_pending(self):
        g = Goal(id="g1", description="Test", status="pending")
        assert g.get_progress() == 0.0

    def test_get_progress_leaf_completed(self):
        g = Goal(id="g1", description="Test", status="completed")
        assert g.get_progress() == 1.0

    def test_get_progress_parent(self):
        g = Goal(id="g1", description="Parent")
        g.add_subgoal("Child 1")
        g.subgoals[0].status = "completed"
        assert g.get_progress() == 0.5

    def test_get_next_pending(self):
        g = Goal(id="g1", description="Parent")
        g.add_subgoal("Child 1")
        g.add_subgoal("Child 2")
        next_goal = g.get_next_pending()
        assert next_goal is not None
        assert next_goal.description == "Child 1"


class TestGoalDecompositionPlanner:
    def test_create_goal(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Test goal")
        assert g.id in planner.goals
        assert g.description == "Test goal"

    def test_decompose(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Parent")
        subgoals = planner.decompose(g.id, ["Sub 1", "Sub 2"])
        assert len(subgoals) == 2
        assert g.subgoals[0].description == "Sub 1"

    def test_complete_goal(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Test")
        planner.complete_goal(g.id, result="done")
        assert planner.goals[g.id].status == "completed"
        assert planner.goals[g.id].result == "done"

    def test_fail_goal(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Test")
        planner.fail_goal(g.id)
        assert planner.goals[g.id].status == "failed"
        assert planner.goals[g.id].retry_count == 1

    def test_replan(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Parent")
        planner.decompose(g.id, ["Old Sub"])
        planner.fail_goal(g.subgoals[0].id)
        planner.replan(g.id, ["New Sub 1", "New Sub 2"])
        assert len(planner.goals[g.id].subgoals) == 2

    def test_get_progress(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Parent")
        g.add_subgoal("Child 1")
        g.subgoals[0].status = "completed"
        assert planner.get_progress(g.id) == 0.5

    def test_get_all_pending(self):
        planner = GoalDecompositionPlanner()
        g = planner.create_goal("Parent")
        g.add_subgoal("Child 1")
        g.add_subgoal("Child 2")
        pending = planner.get_all_pending()
        assert len(pending) == 2
