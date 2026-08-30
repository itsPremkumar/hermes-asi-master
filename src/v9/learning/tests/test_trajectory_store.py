"""Tests for trajectory_store.py."""

import pytest
from v9.learning.trajectory_store import TrajectoryStore, Trajectory, TrajectoryStep


class TestTrajectoryStep:
    """Tests for TrajectoryStep."""

    def test_step_fields(self):
        step = TrajectoryStep(
            step_num=1,
            action="implement",
            observation="code written",
            result="success",
            success=True,
        )
        assert step.step_num == 1
        assert step.action == "implement"
        assert step.success is True

    def test_step_to_dict(self):
        step = TrajectoryStep(
            step_num=1,
            action="a",
            observation="o",
            result="r",
            success=True,
        )
        d = step.to_dict()
        assert d["action"] == "a"
        assert d["success"] is True


class TestTrajectory:
    """Tests for Trajectory."""

    def test_trajectory_fields(self):
        traj = Trajectory(
            task="test task",
            steps=[TrajectoryStep(step_num=0, action="a", observation="o", result="r", success=True)],
            success=True,
        )
        assert traj.task == "test task"
        assert traj.step_count == 1
        assert traj.success_rate == 1.0

    def test_trajectory_success_rate(self):
        traj = Trajectory(
            task="test",
            steps=[
                TrajectoryStep(step_num=0, action="a", observation="o", result="r", success=True),
                TrajectoryStep(step_num=1, action="b", observation="o", result="r", success=False),
            ],
            success=False,
        )
        assert traj.success_rate == 0.5

    def test_trajectory_id_generated(self):
        traj = Trajectory(task="test", steps=[], success=True)
        assert traj.trajectory_id != ""
        assert len(traj.trajectory_id) == 12

    def test_trajectory_to_dict(self):
        traj = Trajectory(task="test", steps=[], success=True)
        d = traj.to_dict()
        assert d["task"] == "test"
        assert d["success"] is True


class TestTrajectoryStore:
    """Tests for TrajectoryStore."""

    def test_add_trajectory(self):
        store = TrajectoryStore()
        traj = Trajectory(task="test", steps=[], success=True)
        tid = store.add(traj)
        assert tid in store.trajectories

    def test_get_trajectory(self):
        store = TrajectoryStore()
        traj = Trajectory(task="test", steps=[], success=True)
        tid = store.add(traj)
        retrieved = store.get(tid)
        assert retrieved is not None
        assert retrieved.task == "test"

    def test_remove_trajectory(self):
        store = TrajectoryStore()
        traj = Trajectory(task="test", steps=[], success=True)
        tid = store.add(traj)
        assert store.remove(tid) is True
        assert store.get(tid) is None

    def test_find_by_task(self):
        store = TrajectoryStore()
        traj = Trajectory(task="Write code", steps=[], success=True)
        store.add(traj)
        results = store.find_by_task("Write code")
        assert len(results) == 1

    def test_find_successful(self):
        store = TrajectoryStore()
        store.add(Trajectory(task="t1", steps=[], success=True))
        store.add(Trajectory(task="t2", steps=[], success=False))
        assert len(store.find_successful()) == 1

    def test_find_failed(self):
        store = TrajectoryStore()
        store.add(Trajectory(task="t1", steps=[], success=True))
        store.add(Trajectory(task="t2", steps=[], success=False))
        assert len(store.find_failed()) == 1

    def test_search(self):
        store = TrajectoryStore()
        traj = Trajectory(
            task="Write code",
            steps=[TrajectoryStep(step_num=0, action="implement sort", observation="", result="", success=True)],
            success=True,
        )
        store.add(traj)
        results = store.search("sort")
        assert len(results) == 1

    def test_get_statistics(self):
        store = TrajectoryStore()
        store.add(Trajectory(task="t1", steps=[], success=True))
        store.add(Trajectory(task="t2", steps=[], success=False))
        stats = store.get_statistics()
        assert stats["total"] == 2
        assert stats["successful"] == 1
        assert stats["failed"] == 1

    def test_clear(self):
        store = TrajectoryStore()
        store.add(Trajectory(task="t1", steps=[], success=True))
        store.clear()
        assert len(store) == 0

    def test_max_size(self):
        store = TrajectoryStore(max_size=3)
        for i in range(5):
            store.add(Trajectory(task=f"t{i}", steps=[], success=True))
        assert len(store) == 3
