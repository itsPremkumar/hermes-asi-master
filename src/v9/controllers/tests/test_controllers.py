"""Tests for v9 controllers — base, registry, and all 16 controllers."""

import os
import sys
import time

import pytest

# Add src/ to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from v9.controllers import ControllerBase, ControllerMetadata, controller
from v9.controllers.registry import ControllerRegistry
from v9.controllers.controllers import (
    LoopController,
    ResourceController,
    BudgetController,
    ErrorController,
    FlowController,
    EventController,
    RetryController,
    ConcurrencyController,
    TimeoutController,
    ValidationController,
    CircuitBreakerController,
    RateLimiterController,
    StateController,
    PipelineController,
    FallbackController,
    ApprovalController,
)


# ===================================================================
# ControllerMetadata tests
# ===================================================================

class TestControllerMetadata:
    def test_create_metadata(self):
        m = ControllerMetadata(name="test", version="1.0.0", description="Test")
        assert m.name == "test"
        assert m.version == "1.0.0"
        assert m.level == 1
        assert m.requires_approval is False

    def test_requires_approval_level_10(self):
        m = ControllerMetadata(name="risky", level=10)
        assert m.requires_approval is True

    def test_to_dict(self):
        m = ControllerMetadata(name="test", version="2.0.0")
        d = m.to_dict()
        assert d["name"] == "test"
        assert d["version"] == "2.0.0"

    def test_from_dict(self):
        d = {"name": "test", "version": "1.0.0", "description": "desc", "level": 3}
        m = ControllerMetadata.from_dict(d)
        assert m.name == "test"
        assert m.level == 3


# ===================================================================
# ControllerBase tests
# ===================================================================

class TestControllerBase:
    def test_base_requires_metadata(self):
        with pytest.raises(ValueError):
            class BadController(ControllerBase):
                def run(self, state):
                    return state
            BadController()

    def test_controller_decorator(self):
        @controller(name="decorated", description="test")
        class DecoratedController(ControllerBase):
            def run(self, state):
                return state

        assert DecoratedController.METADATA.name == "decorated"
        assert DecoratedController.METADATA.description == "test"

    def test_controller_name_property(self):
        ctrl = LoopController()
        assert ctrl.name == "loop"

    def test_controller_level_property(self):
        ctrl = ApprovalController()
        assert ctrl.level == 5

    def test_controller_to_dict(self):
        ctrl = LoopController()
        d = ctrl.to_dict()
        assert d["metadata"]["name"] == "loop"
        assert d["class"] == "LoopController"


# ===================================================================
# ControllerRegistry tests
# ===================================================================

class TestControllerRegistry:
    def test_register_and_get(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        ctrl = reg.get("loop")
        assert ctrl is not None
        assert isinstance(ctrl, LoopController)

    def test_register_non_controller_raises(self):
        reg = ControllerRegistry()
        with pytest.raises(TypeError):
            reg.register(str)

    def test_unregister(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        assert reg.unregister("loop") is True
        assert reg.get("loop") is None

    def test_list_controllers(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        reg.register(BudgetController)
        lst = reg.list_controllers()
        assert len(lst) == 2
        names = {m.name for m in lst}
        assert "loop" in names
        assert "budget" in names

    def test_list_by_level(self):
        reg = ControllerRegistry()
        reg.register(LoopController)  # level 1
        reg.register(ApprovalController)  # level 5
        level1 = reg.list_by_level(1)
        assert len(level1) == 1
        assert level1[0].name == "loop"

    def test_contains(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        assert "loop" in reg
        assert "nonexistent" not in reg

    def test_len(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        reg.register(BudgetController)
        assert len(reg) == 2

    def test_iter(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        reg.register(BudgetController)
        names = list(reg)
        assert "loop" in names
        assert "budget" in names

    def test_clear(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        reg.clear()
        assert len(reg) == 0

    def test_discover(self):
        reg = ControllerRegistry()
        count = reg.discover("v9.controllers")
        assert count >= 16  # All 16 controllers should be discovered

    def test_get_class(self):
        reg = ControllerRegistry()
        reg.register(LoopController)
        cls = reg.get_class("loop")
        assert cls is LoopController


# ===================================================================
# LoopController tests
# ===================================================================

class TestLoopController:
    def test_basic_iteration(self):
        ctrl = LoopController()
        state = {"iterations": 0, "max_iterations": 5}
        result = ctrl.run(state)
        assert result["iterations"] == 1
        assert result["status"] == "running"

    def test_max_iterations_reached(self):
        ctrl = LoopController()
        state = {"iterations": 5, "max_iterations": 5}
        result = ctrl.run(state)
        assert result["status"] == "max_iterations_reached"

    def test_with_loop_body(self):
        ctrl = LoopController()
        state = {
            "iterations": 0,
            "max_iterations": 3,
            "loop_body": lambda s: {"counter": s.get("counter", 0) + 1},
            "counter": 0,
        }
        result = ctrl.run(state)
        assert result["counter"] == 1

    def test_invalid_max_iterations(self):
        ctrl = LoopController()
        valid, errors = ctrl.validate({"max_iterations": -1})
        assert valid is False
        assert len(errors) > 0


# ===================================================================
# ResourceController tests
# ===================================================================

class TestResourceController:
    def test_allocate(self):
        ctrl = ResourceController()
        state = {
            "resource_action": "allocate",
            "resource_type": "cpu",
            "amount": 10,
            "resources": {},
            "max_resources": {"cpu": 100},
        }
        result = ctrl.run(state)
        assert result["allocation_status"] == "allocated"
        assert result["resources"]["cpu"] == 10

    def test_allocate_insufficient(self):
        ctrl = ResourceController()
        state = {
            "resource_action": "allocate",
            "resource_type": "cpu",
            "amount": 50,
            "resources": {"cpu": 80},
            "max_resources": {"cpu": 100},
        }
        result = ctrl.run(state)
        assert result["allocation_status"] == "insufficient"

    def test_deallocate(self):
        ctrl = ResourceController()
        state = {
            "resource_action": "deallocate",
            "resource_type": "cpu",
            "amount": 5,
            "resources": {"cpu": 20},
        }
        result = ctrl.run(state)
        assert result["allocation_status"] == "deallocated"
        assert result["resources"]["cpu"] == 15

    def test_check(self):
        ctrl = ResourceController()
        state = {"resource_action": "check", "resources": {"cpu": 10}}
        result = ctrl.run(state)
        assert result["allocation_status"] == "checked"
        assert result["total_allocated"] == 10

    def test_invalid_action(self):
        ctrl = ResourceController()
        valid, errors = ctrl.validate({"resource_action": "invalid"})
        assert valid is False


# ===================================================================
# BudgetController tests
# ===================================================================

class TestBudgetController:
    def test_budget_ok(self):
        ctrl = BudgetController()
        state = {"budget_total": 1000, "budget_used": 100, "cost": 50}
        result = ctrl.run(state)
        assert result["budget_status"] == "ok"
        assert result["budget_used"] == 150

    def test_budget_warning(self):
        ctrl = BudgetController()
        state = {"budget_total": 1000, "budget_used": 700, "cost": 50}
        result = ctrl.run(state)
        assert result["budget_status"] == "warning"

    def test_budget_critical(self):
        ctrl = BudgetController()
        state = {"budget_total": 1000, "budget_used": 900, "cost": 50}
        result = ctrl.run(state)
        assert result["budget_status"] == "critical"

    def test_budget_exceeded(self):
        ctrl = BudgetController()
        state = {"budget_total": 1000, "budget_used": 1000, "cost": 100}
        result = ctrl.run(state)
        assert result["budget_status"] == "exceeded"
        assert result["budget_remaining"] == 0

    def test_consumed_pct(self):
        ctrl = BudgetController()
        state = {"budget_total": 1000, "budget_used": 500, "cost": 0}
        result = ctrl.run(state)
        assert result["budget_consumed_pct"] == 0.5


# ===================================================================
# ErrorController tests
# ===================================================================

class TestErrorController:
    def test_no_error(self):
        ctrl = ErrorController()
        state = {}
        result = ctrl.run(state)
        assert result["error_handled"] is False

    def test_handle_value_error(self):
        ctrl = ErrorController()
        state = {"error": ValueError("bad input")}
        result = ctrl.run(state)
        assert result["error_handled"] is True
        assert result["error_type"] == "ValueError"
        assert result["error_severity"] == "low"
        assert result["recovery_action"] == "retry"

    def test_handle_runtime_error(self):
        ctrl = ErrorController()
        state = {"error": RuntimeError("system failure")}
        result = ctrl.run(state)
        assert result["error_severity"] == "high"
        assert result["recovery_action"] == "abort_and_notify"

    def test_handle_critical_error(self):
        ctrl = ErrorController()
        state = {"error": MemoryError("out of memory")}
        result = ctrl.run(state)
        assert result["error_severity"] == "critical"
        assert result["recovery_action"] == "shutdown"

    def test_error_has_id(self):
        ctrl = ErrorController()
        state = {"error": ValueError("test")}
        result = ctrl.run(state)
        assert "error_id" in result
        assert "error_timestamp" in result


# ===================================================================
# FlowController tests
# ===================================================================

class TestFlowController:
    def test_branch_selection(self):
        ctrl = FlowController()
        state = {
            "branches": [
                {
                    "name": "branch_a",
                    "condition": lambda s: s.get("value") > 10,
                    "action": lambda s: {"result": "a"},
                },
                {
                    "name": "branch_b",
                    "condition": lambda s: s.get("value") <= 10,
                    "action": lambda s: {"result": "b"},
                },
            ],
            "value": 15,
        }
        result = ctrl.run(state)
        assert result["selected_branch"] == "branch_a"
        assert result["result"] == "a"

    def test_default_branch(self):
        ctrl = FlowController()
        state = {
            "branches": [
                {
                    "name": "branch_a",
                    "condition": lambda s: False,
                }
            ],
            "default_branch": {"name": "default", "action": lambda s: {"result": "default"}},
        }
        result = ctrl.run(state)
        assert result["selected_branch"] == "default"
        assert result["result"] == "default"

    def test_no_match_no_default(self):
        ctrl = FlowController()
        state = {
            "branches": [
                {"name": "a", "condition": lambda s: False}
            ]
        }
        result = ctrl.run(state)
        assert result["selected_branch"] == "none"

    def test_validation(self):
        ctrl = FlowController()
        valid, errors = ctrl.validate({"branches": [{"name": "a"}]})
        assert valid is False
        assert len(errors) > 0


# ===================================================================
# EventController tests
# ===================================================================

class TestEventController:
    def test_dispatch_event(self):
        ctrl = EventController()
        state = {
            "event": {"type": "click", "data": "button1"},
            "event_handlers": {"click": lambda e: "handled"},
        }
        result = ctrl.run(state)
        assert result["event_dispatched"] is True
        assert result["event_type"] == "click"
        assert result["event_result"] == "handled"

    def test_no_event(self):
        ctrl = EventController()
        state = {}
        result = ctrl.run(state)
        assert result["event_dispatched"] is False

    def test_no_handler(self):
        ctrl = EventController()
        state = {
            "event": {"type": "unknown"},
            "event_handlers": {},
        }
        result = ctrl.run(state)
        assert result["event_dispatched"] is True
        assert result["event_result"] is None

    def test_invalid_handlers(self):
        ctrl = EventController()
        valid, errors = ctrl.validate({"event_handlers": "not_a_dict"})
        assert valid is False


# ===================================================================
# RetryController tests
# ===================================================================

class TestRetryController:
    def test_will_retry(self):
        ctrl = RetryController()
        state = {"max_retries": 3, "retry_count": 0, "last_error": "timeout", "base_delay": 1.0}
        result = ctrl.run(state)
        assert result["retry_status"] == "will_retry"
        assert result["retry_count"] == 1
        assert result["retry_delay"] == 1.0

    def test_exponential_backoff(self):
        ctrl = RetryController()
        state = {"max_retries": 5, "retry_count": 2, "last_error": "timeout", "base_delay": 1.0}
        result = ctrl.run(state)
        assert result["retry_delay"] == 4.0  # 1.0 * 2^2

    def test_max_retries_exceeded(self):
        ctrl = RetryController()
        state = {"max_retries": 3, "retry_count": 3, "last_error": "timeout"}
        result = ctrl.run(state)
        assert result["retry_status"] == "max_retries_exceeded"

    def test_no_error_no_retry(self):
        ctrl = RetryController()
        state = {"max_retries": 3, "retry_count": 0, "last_error": None}
        result = ctrl.run(state)
        assert result["retry_status"] == "no_retry"

    def test_invalid_max_retries(self):
        ctrl = RetryController()
        valid, errors = ctrl.validate({"max_retries": -1})
        assert valid is False


# ===================================================================
# ConcurrencyController tests
# ===================================================================

class TestConcurrencyController:
    def test_acquire_worker(self):
        ctrl = ConcurrencyController()
        state = {"max_workers": 4, "active_workers": 1, "concurrency_action": "acquire"}
        result = ctrl.run(state)
        assert result["worker_acquired"] is True
        assert result["active_workers"] == 2

    def test_acquire_full(self):
        ctrl = ConcurrencyController()
        state = {"max_workers": 4, "active_workers": 4, "concurrency_action": "acquire"}
        result = ctrl.run(state)
        assert result["worker_acquired"] is False

    def test_release_worker(self):
        ctrl = ConcurrencyController()
        state = {"max_workers": 4, "active_workers": 2, "concurrency_action": "release"}
        result = ctrl.run(state)
        assert result["active_workers"] == 1

    def test_utilization(self):
        ctrl = ConcurrencyController()
        state = {"max_workers": 4, "active_workers": 2, "concurrency_action": "check"}
        result = ctrl.run(state)
        assert result["utilization"] == 0.5
        assert result["available_workers"] == 2

    def test_invalid_action(self):
        ctrl = ConcurrencyController()
        valid, errors = ctrl.validate({"concurrency_action": "invalid"})
        assert valid is False


# ===================================================================
# TimeoutController tests
# ===================================================================

class TestTimeoutController:
    def test_within_timeout(self):
        ctrl = TimeoutController()
        now = time.time()
        state = {"timeout_seconds": 30.0, "start_time": now - 5.0, "current_time": now}
        result = ctrl.run(state)
        assert result["timed_out"] is False
        assert result["timeout_status"] == "ok"

    def test_timed_out(self):
        ctrl = TimeoutController()
        now = time.time()
        state = {"timeout_seconds": 10.0, "start_time": now - 20.0, "current_time": now}
        result = ctrl.run(state)
        assert result["timed_out"] is True
        assert result["timeout_status"] == "timed_out"

    def test_critical_remaining(self):
        ctrl = TimeoutController()
        now = time.time()
        state = {"timeout_seconds": 10.0, "start_time": now - 8.5, "current_time": now}
        result = ctrl.run(state)
        assert result["timeout_status"] == "critical"

    def test_invalid_timeout(self):
        ctrl = TimeoutController()
        valid, errors = ctrl.validate({"timeout_seconds": -1})
        assert valid is False


# ===================================================================
# ValidationController tests
# ===================================================================

class TestValidationController:
    def test_valid_data(self):
        ctrl = ValidationController()
        state = {
            "schema": {
                "name": {"required": True, "type": str},
                "age": {"type": int, "min": 0, "max": 150},
            },
            "data": {"name": "Alice", "age": 30},
        }
        result = ctrl.run(state)
        assert result["valid"] is True
        assert len(result["validation_errors"]) == 0

    def test_missing_required(self):
        ctrl = ValidationController()
        state = {
            "schema": {"name": {"required": True}},
            "data": {},
        }
        result = ctrl.run(state)
        assert result["valid"] is False
        assert "required" in result["validation_errors"][0].lower()

    def test_type_mismatch(self):
        ctrl = ValidationController()
        state = {
            "schema": {"age": {"type": int}},
            "data": {"age": "thirty"},
        }
        result = ctrl.run(state)
        assert result["valid"] is False

    def test_range_violation(self):
        ctrl = ValidationController()
        state = {
            "schema": {"score": {"type": int, "min": 0, "max": 100}},
            "data": {"score": 150},
        }
        result = ctrl.run(state)
        assert result["valid"] is False

    def test_custom_validator(self):
        ctrl = ValidationController()
        state = {
            "schema": {
                "email": {"validator": lambda v: "@" in v},
            },
            "data": {"email": "invalid"},
        }
        result = ctrl.run(state)
        assert result["valid"] is False


# ===================================================================
# CircuitBreakerController tests
# ===================================================================

class TestCircuitBreakerController:
    def test_closed_to_open(self):
        ctrl = CircuitBreakerController()
        state = {
            "failure_threshold": 3,
            "failure_count": 3,
            "circuit_state": "closed",
        }
        result = ctrl.run(state)
        assert result["circuit_state"] == "open"
        assert result["circuit_allow_request"] is False

    def test_open_to_half_open(self):
        ctrl = CircuitBreakerController()
        state = {
            "failure_threshold": 3,
            "failure_count": 3,
            "circuit_state": "open",
            "last_failure_time": time.time() - 60,
            "recovery_timeout": 30.0,
        }
        result = ctrl.run(state)
        assert result["circuit_state"] == "half_open"

    def test_closed_allows_request(self):
        ctrl = CircuitBreakerController()
        state = {
            "failure_threshold": 5,
            "failure_count": 0,
            "circuit_state": "closed",
        }
        result = ctrl.run(state)
        assert result["circuit_allow_request"] is True

    def test_invalid_threshold(self):
        ctrl = CircuitBreakerController()
        valid, errors = ctrl.validate({"failure_threshold": 0})
        assert valid is False


# ===================================================================
# RateLimiterController tests
# ===================================================================

class TestRateLimiterController:
    def test_within_limit(self):
        ctrl = RateLimiterController()
        state = {
            "max_requests": 10,
            "window_seconds": 60.0,
            "request_history": [],
            "current_time": time.time(),
        }
        result = ctrl.run(state)
        assert result["request_accepted"] is True
        assert result["rate_limit_remaining"] == 9

    def test_exceeds_limit(self):
        ctrl = RateLimiterController()
        now = time.time()
        state = {
            "max_requests": 2,
            "window_seconds": 60.0,
            "request_history": [now - 5, now - 3],
            "current_time": now,
        }
        result = ctrl.run(state)
        assert result["request_accepted"] is False
        assert result["rate_limit_exceeded"] is True

    def test_expired_requests_removed(self):
        ctrl = RateLimiterController()
        now = time.time()
        state = {
            "max_requests": 10,
            "window_seconds": 60.0,
            "request_history": [now - 120, now - 90, now - 5],
            "current_time": now,
        }
        result = ctrl.run(state)
        # Expired removed + new request accepted = 1 remaining + 1 new
        assert len(result["request_history"]) == 2
        assert result["request_accepted"] is True

    def test_invalid_max_requests(self):
        ctrl = RateLimiterController()
        valid, errors = ctrl.validate({"max_requests": 0})
        assert valid is False


# ===================================================================
# StateController tests
# ===================================================================

class TestStateController:
    def test_valid_transition(self):
        ctrl = StateController()
        state = {
            "current_state": "idle",
            "transitions": {"idle": {"start": "running"}},
            "trigger": "start",
        }
        result = ctrl.run(state)
        assert result["transitioned"] is True
        assert result["current_state"] == "running"
        assert result["previous_state"] == "idle"

    def test_invalid_transition(self):
        ctrl = StateController()
        state = {
            "current_state": "idle",
            "transitions": {"idle": {"start": "running"}},
            "trigger": "stop",
        }
        result = ctrl.run(state)
        assert result["transitioned"] is False
        assert "transition_error" in result

    def test_no_trigger(self):
        ctrl = StateController()
        state = {"current_state": "idle", "transitions": {}}
        result = ctrl.run(state)
        assert result["transitioned"] is False

    def test_validation(self):
        ctrl = StateController()
        valid, errors = ctrl.validate({})
        assert valid is False
        assert len(errors) == 2


# ===================================================================
# PipelineController tests
# ===================================================================

class TestPipelineController:
    def test_execute_stage(self):
        ctrl = PipelineController()
        state = {
            "stages": [
                {"name": "stage1", "func": lambda s: {"step1": True}},
                {"name": "stage2", "func": lambda s: {"step2": True}},
            ],
            "current_stage_idx": 0,
        }
        result = ctrl.run(state)
        assert result["pipeline_status"] == "running"
        assert result["last_stage"] == "stage1"
        assert result["last_stage_success"] is True
        assert result["current_stage_idx"] == 1

    def test_pipeline_completed(self):
        ctrl = PipelineController()
        state = {
            "stages": [{"name": "stage1", "func": lambda s: {}}],
            "current_stage_idx": 1,
        }
        result = ctrl.run(state)
        assert result["pipeline_status"] == "completed"

    def test_stage_failure(self):
        ctrl = PipelineController()
        
        def failing_func(s):
            raise RuntimeError("fail")
        
        state = {
            "stages": [
                {"name": "bad_stage", "func": failing_func},
            ],
            "current_stage_idx": 0,
            "fail_fast": True,
        }
        result = ctrl.run(state)
        assert result["pipeline_status"] == "failed"
        assert result["last_stage_success"] is False

    def test_validation(self):
        ctrl = PipelineController()
        valid, errors = ctrl.validate({"stages": [{"func": lambda s: {}}]})
        assert valid is False


# ===================================================================
# FallbackController tests
# ===================================================================

class TestFallbackController:
    def test_primary_succeeds(self):
        ctrl = FallbackController()
        state = {
            "primary_action": lambda s: {"result": "primary"},
            "fallbacks": [lambda s: {"result": "fallback"}],
        }
        result = ctrl.run(state)
        assert result["fallback_status"] == "primary_succeeded"
        assert result["result"] == "primary"

    def test_fallback_used(self):
        ctrl = FallbackController()
        
        def failing_primary(s):
            raise RuntimeError("fail")
        
        state = {
            "primary_action": failing_primary,
            "fallbacks": [lambda s: {"result": "fallback"}],
        }
        result = ctrl.run(state)
        assert result["fallback_status"] == "fallback_0_succeeded"
        assert result["result"] == "fallback"

    def test_all_failed(self):
        ctrl = FallbackController()
        
        def failing_primary(s):
            raise RuntimeError("fail")
        
        def failing_fallback(s):
            raise RuntimeError("fail2")
        
        state = {
            "primary_action": failing_primary,
            "fallbacks": [failing_fallback],
        }
        result = ctrl.run(state)
        assert result["fallback_status"] == "all_failed"

    def test_validation(self):
        ctrl = FallbackController()
        valid, errors = ctrl.validate({})
        assert valid is False


# ===================================================================
# ApprovalController tests
# ===================================================================

class TestApprovalController:
    def test_approval_not_required(self):
        ctrl = ApprovalController()
        state = {"risk_level": 2, "approval_required_above": 4}
        result = ctrl.run(state)
        assert result["approval_required"] is False
        assert result["operation_allowed"] is True

    def test_approval_required_approved(self):
        ctrl = ApprovalController()
        state = {
            "risk_level": 5,
            "approval_required_above": 4,
            "approval_status": "approved",
        }
        result = ctrl.run(state)
        assert result["approval_required"] is True
        assert result["operation_allowed"] is True

    def test_approval_required_rejected(self):
        ctrl = ApprovalController()
        state = {
            "risk_level": 5,
            "approval_required_above": 4,
            "approval_status": "rejected",
        }
        result = ctrl.run(state)
        assert result["operation_allowed"] is False

    def test_approval_pending(self):
        ctrl = ApprovalController()
        state = {
            "risk_level": 5,
            "approval_required_above": 4,
            "approval_status": "pending",
        }
        result = ctrl.run(state)
        assert result["operation_allowed"] is False

    def test_invalid_risk_level(self):
        ctrl = ApprovalController()
        valid, errors = ctrl.validate({"risk_level": 15})
        assert valid is False
