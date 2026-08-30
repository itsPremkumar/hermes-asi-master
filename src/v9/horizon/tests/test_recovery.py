"""
Tests for Recovery System.
Test count: 14
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v9.horizon.recovery import (
    BackoffStrategy,
    FailureEvent,
    FailureType,
    FallbackRegistry,
    GracefulDegradation,
    RecoveryManager,
    RecoveryResult,
    RecoveryStrategy,
)


def async_run(coro):
    """Helper to run async functions in tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestBackoffStrategy:
    def test_exponential(self):
        assert BackoffStrategy.exponential(0) == 1.0
        assert BackoffStrategy.exponential(1) == 2.0
        assert BackoffStrategy.exponential(2) == 4.0

    def test_exponential_max(self):
        assert BackoffStrategy.exponential(10, max_delay=60.0) == 60.0

    def test_linear(self):
        assert BackoffStrategy.linear(0) == 1.0
        assert BackoffStrategy.linear(1) == 2.0
        assert BackoffStrategy.linear(2) == 3.0

    def test_constant(self):
        assert BackoffStrategy.constant(0, 2.0) == 2.0
        assert BackoffStrategy.constant(5, 2.0) == 2.0

    def test_jitter(self):
        delay = BackoffStrategy.jitter(2, base=1.0, max_delay=60.0)
        assert delay >= 0
        delay = BackoffStrategy.jitter(10, base=1.0, max_delay=5.0)
        assert delay <= 5.0


class TestFailureEvent:
    def test_create_failure_event(self):
        event = FailureEvent(
            id="f1",
            task_id="t1",
            failure_type=FailureType.NETWORK,
            message="Connection failed",
            timestamp=1234567890.0,
        )
        assert event.id == "f1"
        assert event.failure_type == FailureType.NETWORK
        assert event.recoverable is True

    def test_failure_event_auto_id(self):
        event = FailureEvent(
            id="",
            task_id="t1",
            failure_type=FailureType.TIMEOUT,
            message="Timed out",
            timestamp=0.0,
        )
        assert len(event.id) > 0


class TestFallbackRegistry:
    def test_register_and_get(self):
        registry = FallbackRegistry()

        def fallback():
            return "fallback"

        registry.register("task1", fallback)
        assert registry.get("task1") is fallback

    def test_has(self):
        registry = FallbackRegistry()
        assert registry.has("nonexistent") is False

        def fallback():
            pass

        registry.register("task1", fallback)
        assert registry.has("task1") is True


class TestRecoveryManager:
    def test_create_manager(self):
        manager = RecoveryManager(max_retries=3, backoff_base=1.0, max_delay=30.0)
        assert manager.max_retries == 3
        assert manager.backoff_base == 1.0
        assert manager.max_delay == 30.0

    async def _success(self):
        return "success"

    def test_execute_success(self):
        async def run():
            manager = RecoveryManager()
            result = await manager.execute_with_recovery("t1", self._success)
            assert result.success is True
            assert result.final_output == "success"
            assert result.attempts == 1
        async_run(run())

    async def _fail_twice(self):
        if not hasattr(self, '_call_count'):
            self._call_count = 0
        self._call_count += 1
        if self._call_count < 3:
            raise ValueError("Fail")
        return "success"

    def test_execute_retry_then_success(self):
        async def run():
            manager = RecoveryManager(max_retries=3, backoff_base=0.01)
            result = await manager.execute_with_recovery("t1", self._fail_twice)
            assert result.success is True
            assert result.final_output == "success"
            assert result.attempts == 3
        async_run(run())

    async def _always_fail(self):
        raise RuntimeError("Always fails")

    def test_execute_fails_after_retries(self):
        async def run():
            manager = RecoveryManager(max_retries=2, backoff_base=0.01)
            result = await manager.execute_with_recovery("t1", self._always_fail)
            assert result.success is False
            assert result.attempts == 3  # initial + 2 retries
            assert result.final_error is not None
        async_run(run())

    def test_execute_with_fallback(self):
        async def run():
            async def fallback():
                return "fallback_result"
            manager = RecoveryManager(max_retries=0)
            result = await manager.execute_with_recovery(
                "t1", self._always_fail, fallback=fallback
            )
            assert result.success is True
            assert result.final_output == "fallback_result"
            assert result.strategy == RecoveryStrategy.FALLBACK
        async_run(run())

    def test_failure_counts(self):
        async def run():
            manager = RecoveryManager(max_retries=0)
            await manager.execute_with_recovery("t1", self._always_fail)
            counts = manager.failure_counts
            assert FailureType.UNKNOWN in counts
            assert counts[FailureType.UNKNOWN] == 1
        async_run(run())

    def test_get_history(self):
        async def run():
            manager = RecoveryManager(max_retries=0)
            await manager.execute_with_recovery("t1", self._always_fail)
            history = manager.get_history()
            assert len(history) == 1
            assert history[0].success is False
        async_run(run())


class TestGracefulDegradation:
    def test_reduce_quality(self):
        output = "x" * 1000
        result = GracefulDegradation.reduce_quality(output)
        assert len(result) < len(output)

    def test_use_cached(self):
        cache = {"last_result": "cached"}
        result = GracefulDegradation.use_cached("new", cache)
        assert result == "cached"

    def test_partial_complete(self):
        result = GracefulDegradation.partial_complete([1, 2, 3], 10)
        assert result["status"] == "partial"
        assert result["completed"] == 3
        assert result["total"] == 10
        assert result["progress"] == 0.3

    def test_partial_complete_zero_total(self):
        result = GracefulDegradation.partial_complete([], 0)
        assert result["progress"] == 0
