"""Tests for failure_recovery.py."""
import pytest
from agency.failure_recovery import FailureRecoveryEngine, FailureRecord


class TestFailureRecord:
    def test_create(self):
        r = FailureRecord(id="f1", action_name="test", error_type="ValueError", message="bad")
        assert r.id == "f1"
        assert r.action_name == "test"
        assert r.recovered is False


class TestFailureRecoveryEngine:
    def test_create(self):
        engine = FailureRecoveryEngine()
        assert engine.max_retries == 3
        assert len(engine.failure_log) == 0

    def test_register_strategy(self):
        engine = FailureRecoveryEngine()
        engine.register_strategy("ValueError", lambda f: "fixed")
        assert "ValueError" in engine.recovery_strategies

    def test_register_fallback(self):
        engine = FailureRecoveryEngine()
        engine.register_fallback_plan("api_call", ["fallback_1", "fallback_2"])
        assert "api_call" in engine.fallback_plans

    def test_detect_failure_exception(self):
        engine = FailureRecoveryEngine()
        result = ValueError("something failed")
        record = engine.detect_failure(result, context={"action": "test"})
        assert record is not None
        assert record.error_type == "ValueError"

    def test_detect_failure_dict(self):
        engine = FailureRecoveryEngine()
        result = {"status": "error", "message": "failed"}
        record = engine.detect_failure(result)
        assert record is not None

    def test_detect_failure_tuple(self):
        engine = FailureRecoveryEngine()
        result = ("data", ValueError("inner error"))
        record = engine.detect_failure(result)
        assert record is not None
        assert record.error_type == "ValueError"

    def test_detect_failure_none_for_success(self):
        engine = FailureRecoveryEngine()
        assert engine.detect_failure(("data", None)) is None
        assert engine.detect_failure({"status": "ok"}) is None

    def test_recover_with_strategy(self):
        engine = FailureRecoveryEngine()
        engine.register_strategy("ValueError", lambda f: "recovered")
        failure = engine.detect_failure(ValueError("test"), context={"action": "t"})
        result = engine.recover(failure)
        assert result["status"] == "recovered"
        assert failure.recovered is True

    def test_recover_with_fallback(self):
        engine = FailureRecoveryEngine()
        engine.register_fallback_plan("failing_action", ["step1", "step2"])
        failure = FailureRecord(id="f1", action_name="failing_action", error_type="Any", message="x")
        result = engine.recover(failure)
        assert result["status"] == "fallback"

    def test_recover_unrecovered(self):
        engine = FailureRecoveryEngine()
        failure = FailureRecord(id="f1", action_name="x", error_type="Unknown", message="y")
        result = engine.recover(failure)
        assert result["status"] == "unrecovered"

    def test_failure_stats(self):
        engine = FailureRecoveryEngine()
        engine.detect_failure(ValueError("a"), {"action": "x"})
        engine.detect_failure(ValueError("b"), {"action": "y"})
        stats = engine.get_failure_stats()
        assert stats["total"] == 2
        assert "ValueError" in stats["by_type"]

    def test_get_recent_failures(self):
        engine = FailureRecoveryEngine()
        engine.detect_failure(Exception("1"), {"action": "a"})
        engine.detect_failure(Exception("2"), {"action": "b"})
        recent = engine.get_recent_failures(limit=5)
        assert len(recent) == 2

    def test_clear(self):
        engine = FailureRecoveryEngine()
        engine.detect_failure(Exception("x"), {"action": "a"})
        engine.clear()
        assert len(engine.failure_log) == 0
