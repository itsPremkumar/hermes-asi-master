"""Tests for failure_model.py."""

import pytest
from v9.learning.failure_model import FailureModel, FailurePrediction
from v9.learning.trajectory_store import Trajectory, TrajectoryStep


class TestFailurePrediction:
    """Tests for FailurePrediction."""

    def test_prediction_fields(self):
        pred = FailurePrediction(
            capability="python",
            probability=0.8,
            failure_type="syntax_error",
            description="Missing semicolon",
            suggested_preventions=["Use linter"],
        )
        assert pred.capability == "python"
        assert pred.probability == 0.8

    def test_prediction_to_dict(self):
        pred = FailurePrediction(
            capability="python",
            probability=0.5,
            failure_type="logic_error",
            description="Wrong output",
            suggested_preventions=["Add tests"],
        )
        d = pred.to_dict()
        assert d["capability"] == "python"
        assert d["probability"] == 0.5


class TestFailureModel:
    """Tests for FailureModel."""

    def test_learn_from_trajectory(self):
        model = FailureModel()
        traj = Trajectory(
            task="Write code with syntax error",
            steps=[TrajectoryStep(step_num=0, action="code", observation="", result="syntax error in line 5", success=False)],
            success=False,
        )
        model.learn_from_trajectory(traj)
        assert len(model.failure_history) == 1

    def test_learn_from_success_ignored(self):
        model = FailureModel()
        traj = Trajectory(task="Test", steps=[], success=True)
        model.learn_from_trajectory(traj)
        assert len(model.failure_history) == 0

    def test_predict_failure_no_history(self):
        model = FailureModel()
        pred = model.predict_failure("python")
        assert isinstance(pred, FailurePrediction)
        assert pred.probability == 0.1

    def test_predict_failure_with_history(self):
        model = FailureModel()
        traj = Trajectory(
            task="Write code with syntax error",
            steps=[TrajectoryStep(step_num=0, action="code", observation="", result="syntax error", success=False)],
            success=False,
        )
        model.learn_from_trajectory(traj)
        pred = model.predict_failure("coding")
        assert pred.probability > 0.05

    def test_classify_failure_timeout(self):
        model = FailureModel()
        traj = Trajectory(
            task="Long running task",
            steps=[TrajectoryStep(step_num=0, action="run", observation="", result="operation timed out", success=False)],
            success=False,
        )
        failure_type = model._classify_failure(traj)
        assert failure_type == "timeout"

    def test_classify_failure_syntax(self):
        model = FailureModel()
        traj = Trajectory(
            task="Code with bug",
            steps=[TrajectoryStep(step_num=0, action="code", observation="", result="invalid syntax", success=False)],
            success=False,
        )
        failure_type = model._classify_failure(traj)
        assert failure_type == "syntax_error"

    def test_classify_failure_unknown(self):
        model = FailureModel()
        traj = Trajectory(
            task="Mysterious task",
            steps=[TrajectoryStep(step_num=0, action="a", observation="", result="something happened", success=False)],
            success=False,
        )
        failure_type = model._classify_failure(traj)
        assert failure_type == "unknown"

    def test_extract_capability_code(self):
        model = FailureModel()
        cap = model._extract_capability("Write code for a function")
        assert cap == "coding"

    def test_extract_capability_debug(self):
        model = FailureModel()
        cap = model._extract_capability("Debug the error in production")
        assert cap == "debugging"

    def test_extract_capability_general(self):
        model = FailureModel()
        cap = model._extract_capability("Do something vague")
        assert cap == "general"

    def test_get_most_problematic(self):
        model = FailureModel()
        for _ in range(5):
            traj = Trajectory(
                task="Code with syntax error",
                steps=[TrajectoryStep(step_num=0, action="code", observation="", result="syntax error", success=False)],
                success=False,
            )
            model.learn_from_trajectory(traj)
        problematic = model.get_most_problematic(n=3)
        assert len(problematic) > 0

    def test_get_failure_statistics(self):
        model = FailureModel()
        traj = Trajectory(
            task="Test",
            steps=[TrajectoryStep(step_num=0, action="a", observation="", result="syntax error", success=False)],
            success=False,
        )
        model.learn_from_trajectory(traj)
        stats = model.get_failure_statistics()
        assert stats["total_failures"] == 1
        assert "syntax_error" in stats["failure_counts"]

    def test_failure_patterns_exist(self):
        model = FailureModel()
        assert "timeout" in model.FAILURE_PATTERNS
        assert "syntax_error" in model.FAILURE_PATTERNS
        assert "runtime_error" in model.FAILURE_PATTERNS
