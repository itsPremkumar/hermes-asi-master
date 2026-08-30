"""v9 · Engineering Control Plane — 16 Engineering Controllers.

Each controller is a pluggable module implementing ControllerBase.
Controllers handle: loops, resources, budget, errors, flow, events, retry,
concurrency, timeouts, validation, circuit breaker, rate limiting, state,
pipeline, fallback, and approval.
"""

from __future__ import annotations

import math
import time
import uuid
from typing import Any, Optional

from . import ControllerBase, controller


# ---------------------------------------------------------------------------
# 1. LoopController
# ---------------------------------------------------------------------------

@controller(
    name="loop",
    version="1.0.0",
    description="Controls iteration loops (for/while) with safety limits.",
    level=1,
    tags=["core", "iteration"],
)
class LoopController(ControllerBase):
    """Controls iteration loops with max iteration safety limits."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute loop iteration with safety checks."""
        iterations = state.get("iterations", 0)
        max_iterations = state.get("max_iterations", 100)
        loop_body = state.get("loop_body", None)

        if iterations >= max_iterations:
            state["status"] = "max_iterations_reached"
            return state

        if loop_body and callable(loop_body):
            try:
                result = loop_body(state)
                if result is not None:
                    state.update(result)
            except Exception as e:
                state["error"] = str(e)
                state["status"] = "error"
                return state

        state["iterations"] = iterations + 1
        state["status"] = "running"
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if "max_iterations" in state and state["max_iterations"] <= 0:
            errors.append("max_iterations must be positive")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 2. ResourceController
# ---------------------------------------------------------------------------

@controller(
    name="resource",
    version="1.0.0",
    description="Manages resource allocation (CPU, memory, tokens).",
    level=2,
    tags=["core", "resources"],
)
class ResourceController(ControllerBase):
    """Manages and tracks resource allocation."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Allocate or deallocate resources."""
        action = state.get("resource_action", "check")
        resources = state.get("resources", {})

        if action == "allocate":
            resource_type = state.get("resource_type", "generic")
            amount = state.get("amount", 0)
            current = resources.get(resource_type, 0)
            max_available = state.get("max_resources", {}).get(resource_type, 100)
            if current + amount <= max_available:
                resources[resource_type] = current + amount
                state["allocation_status"] = "allocated"
            else:
                state["allocation_status"] = "insufficient"
        elif action == "deallocate":
            resource_type = state.get("resource_type", "generic")
            amount = state.get("amount", 0)
            current = resources.get(resource_type, 0)
            resources[resource_type] = max(0, current - amount)
            state["allocation_status"] = "deallocated"
        elif action == "check":
            state["allocation_status"] = "checked"

        state["resources"] = resources
        state["total_allocated"] = sum(resources.values())
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("resource_action") not in ("check", "allocate", "deallocate"):
            errors.append("resource_action must be check, allocate, or deallocate")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 3. BudgetController
# ---------------------------------------------------------------------------

@controller(
    name="budget",
    version="1.0.0",
    description="Tracks and enforces token/budget limits.",
    level=2,
    tags=["core", "budget"],
)
class BudgetController(ControllerBase):
    """Tracks budget consumption and enforces limits."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Track budget consumption."""
        budget_total = state.get("budget_total", 1000)
        budget_used = state.get("budget_used", 0)
        cost = state.get("cost", 0)

        budget_used += cost
        state["budget_used"] = budget_used
        state["budget_remaining"] = max(0, budget_total - budget_used)
        state["budget_consumed_pct"] = budget_used / max(budget_total, 1)

        if budget_used > budget_total:
            state["budget_status"] = "exceeded"
        elif budget_used > budget_total * 0.9:
            state["budget_status"] = "critical"
        elif budget_used > budget_total * 0.7:
            state["budget_status"] = "warning"
        else:
            state["budget_status"] = "ok"

        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("budget_total", 0) < 0:
            errors.append("budget_total must be non-negative")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 4. ErrorController
# ---------------------------------------------------------------------------

@controller(
    name="error",
    version="1.0.0",
    description="Handles error detection, classification, and recovery.",
    level=3,
    tags=["core", "error-handling"],
)
class ErrorController(ControllerBase):
    """Detects and classifies errors with recovery strategies."""

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Detect and classify error."""
        error = state.get("error")
        if error is None:
            state["error_handled"] = False
            return state

        error_type = type(error).__name__ if isinstance(error, Exception) else "unknown"
        severity = self._classify_severity(error)

        state["error_handled"] = True
        state["error_type"] = error_type
        state["error_severity"] = severity
        state["error_timestamp"] = time.time()
        state["error_id"] = str(uuid.uuid4().hex[:8])

        # Recovery strategy based on severity
        if severity == self.SEVERITY_LOW:
            state["recovery_action"] = "retry"
        elif severity == self.SEVERITY_MEDIUM:
            state["recovery_action"] = "fallback"
        elif severity == self.SEVERITY_HIGH:
            state["recovery_action"] = "abort_and_notify"
        else:
            state["recovery_action"] = "shutdown"

        return state

    def _classify_severity(self, error: Any) -> str:
        if isinstance(error, (ValueError, TypeError)):
            return self.SEVERITY_LOW
        elif isinstance(error, (KeyError, IndexError, AttributeError)):
            return self.SEVERITY_MEDIUM
        elif isinstance(error, (RuntimeError, OSError)):
            return self.SEVERITY_HIGH
        else:
            return self.SEVERITY_CRITICAL


# ---------------------------------------------------------------------------
# 5. FlowController
# ---------------------------------------------------------------------------

@controller(
    name="flow",
    version="1.0.0",
    description="Manages control flow (if/else, switch) decisions.",
    level=1,
    tags=["core", "flow-control"],
)
class FlowController(ControllerBase):
    """Manages conditional control flow branching."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Evaluate flow condition and branch."""
        branches = state.get("branches", [])
        default_branch = state.get("default_branch", None)

        for branch in branches:
            condition = branch.get("condition")
            if condition and callable(condition) and condition(state):
                state["selected_branch"] = branch.get("name", "unnamed")
                action = branch.get("action")
                if action and callable(action):
                    result = action(state)
                    if result:
                        state.update(result)
                return state

        # No branch matched
        if default_branch:
            state["selected_branch"] = default_branch.get("name", "default")
            action = default_branch.get("action")
            if action and callable(action):
                result = action(state)
                if result:
                    state.update(result)
        else:
            state["selected_branch"] = "none"

        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        branches = state.get("branches", [])
        for i, branch in enumerate(branches):
            if "condition" not in branch:
                errors.append(f"Branch {i} missing 'condition'")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 6. EventController
# ---------------------------------------------------------------------------

@controller(
    name="event",
    version="1.0.0",
    description="Event dispatch and handler management.",
    level=2,
    tags=["core", "events"],
)
class EventController(ControllerBase):
    """Event dispatch and handler management."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Dispatch event to registered handlers."""
        event = state.get("event")
        if event is None:
            state["event_dispatched"] = False
            return state

        handlers = state.get("event_handlers", {})
        event_type = event.get("type", "unknown") if isinstance(event, dict) else str(event)

        handler = handlers.get(event_type)
        result = None
        if handler and callable(handler):
            result = handler(event)

        state["event_dispatched"] = True
        state["event_type"] = event_type
        state["event_result"] = result
        state["event_timestamp"] = time.time()
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        handlers = state.get("event_handlers", {})
        if not isinstance(handlers, dict):
            errors.append("event_handlers must be a dict")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 7. RetryController
# ---------------------------------------------------------------------------

@controller(
    name="retry",
    version="1.0.0",
    description="Retry logic with exponential backoff.",
    level=2,
    tags=["core", "retry"],
)
class RetryController(ControllerBase):
    """Retry with exponential backoff and jitter."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute retry logic."""
        max_retries = state.get("max_retries", 3)
        retry_count = state.get("retry_count", 0)
        base_delay = state.get("base_delay", 1.0)
        last_error = state.get("last_error")

        if last_error is None or retry_count >= max_retries:
            state["retry_status"] = "no_retry" if last_error is None else "max_retries_exceeded"
            return state

        delay = base_delay * (2 ** retry_count)
        state["retry_count"] = retry_count + 1
        state["retry_delay"] = delay
        state["retry_status"] = "will_retry"
        state["next_retry_at"] = time.time() + delay
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("max_retries", 0) < 0:
            errors.append("max_retries must be non-negative")
        if state.get("base_delay", 0) < 0:
            errors.append("base_delay must be non-negative")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 8. ConcurrencyController
# ---------------------------------------------------------------------------

@controller(
    name="concurrency",
    version="1.0.0",
    description="Manages parallel execution limits and worker pools.",
    level=3,
    tags=["core", "parallel"],
)
class ConcurrencyController(ControllerBase):
    """Manages concurrency limits and worker allocation."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Allocate/deallocate concurrent workers."""
        max_workers = state.get("max_workers", 4)
        active_workers = state.get("active_workers", 0)
        action = state.get("concurrency_action", "check")

        if action == "acquire":
            if active_workers < max_workers:
                state["active_workers"] = active_workers + 1
                state["worker_acquired"] = True
            else:
                state["worker_acquired"] = False
        elif action == "release":
            state["active_workers"] = max(0, active_workers - 1)
            state["worker_acquired"] = False
        elif action == "check":
            pass

        state["available_workers"] = max_workers - state.get("active_workers", 0)
        state["utilization"] = state.get("active_workers", 0) / max(max_workers, 1)
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("max_workers", 0) <= 0:
            errors.append("max_workers must be positive")
        if state.get("concurrency_action") not in ("check", "acquire", "release"):
            errors.append("concurrency_action must be check, acquire, or release")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 9. TimeoutController
# ---------------------------------------------------------------------------

@controller(
    name="timeout",
    version="1.0.0",
    description="Enforces operation timeouts.",
    level=2,
    tags=["core", "timeout"],
)
class TimeoutController(ControllerBase):
    """Enforces time limits on operations."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check and enforce timeout."""
        timeout_seconds = state.get("timeout_seconds", 30.0)
        start_time = state.get("start_time", time.time())
        current_time = state.get("current_time", time.time())

        elapsed = current_time - start_time
        remaining = max(0, timeout_seconds - elapsed)

        state["elapsed_seconds"] = elapsed
        state["remaining_seconds"] = remaining
        state["timed_out"] = elapsed >= timeout_seconds

        if state["timed_out"]:
            state["timeout_status"] = "timed_out"
        elif remaining < timeout_seconds * 0.2:
            state["timeout_status"] = "critical"
        elif remaining < timeout_seconds * 0.5:
            state["timeout_status"] = "warning"
        else:
            state["timeout_status"] = "ok"

        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("timeout_seconds", 0) <= 0:
            errors.append("timeout_seconds must be positive")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 10. ValidationController
# ---------------------------------------------------------------------------

@controller(
    name="validation",
    version="1.0.0",
    description="Input/output validation with schema checks.",
    level=1,
    tags=["core", "validation"],
)
class ValidationController(ControllerBase):
    """Validates inputs and outputs against schemas."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Validate state against schema rules."""
        schema = state.get("schema", {})
        data = state.get("data", {})
        strict = state.get("strict", False)

        errors = []
        warnings = []

        for field_name, rules in schema.items():
            value = data.get(field_name)

            # Required check
            if rules.get("required", False) and value is None:
                errors.append(f"Field '{field_name}' is required")
                continue

            if value is None:
                continue

            # Type check
            expected_type = rules.get("type")
            if expected_type and not isinstance(value, expected_type):
                errors.append(
                    f"Field '{field_name}' expected {expected_type.__name__}, got {type(value).__name__}"
                )
                continue

            # Range check
            min_val = rules.get("min")
            max_val = rules.get("max")
            if min_val is not None and value < min_val:
                errors.append(f"Field '{field_name}' value {value} below min {min_val}")
            if max_val is not None and value > max_val:
                errors.append(f"Field '{field_name}' value {value} above max {max_val}")

            # Pattern check
            pattern = rules.get("pattern")
            if pattern and isinstance(value, str):
                import re
                if not re.match(pattern, value):
                    errors.append(f"Field '{field_name}' does not match pattern '{pattern}'")

            # Custom validator
            validator = rules.get("validator")
            if validator and callable(validator):
                try:
                    if not validator(value):
                        errors.append(f"Field '{field_name}' failed custom validation")
                except Exception as e:
                    errors.append(f"Field '{field_name}' validator error: {e}")

        state["valid"] = len(errors) == 0
        state["validation_errors"] = errors
        state["validation_warnings"] = warnings
        state["validation_timestamp"] = time.time()

        if strict and warnings:
            state["valid"] = False
            state["validation_errors"].extend(warnings)

        return state


# ---------------------------------------------------------------------------
# 11. CircuitBreakerController
# ---------------------------------------------------------------------------

@controller(
    name="circuit_breaker",
    version="1.0.0",
    description="Circuit breaker pattern for fault tolerance.",
    level=4,
    tags=["core", "fault-tolerance"],
)
class CircuitBreakerController(ControllerBase):
    """Circuit breaker pattern to prevent cascade failures."""

    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Update circuit breaker state."""
        failure_threshold = state.get("failure_threshold", 5)
        recovery_timeout = state.get("recovery_timeout", 30.0)
        failure_count = state.get("failure_count", 0)
        last_failure_time = state.get("last_failure_time", 0.0)
        current_state = state.get("circuit_state", self.STATE_CLOSED)

        current_time = time.time()

        if current_state == self.STATE_CLOSED:
            if failure_count >= failure_threshold:
                current_state = self.STATE_OPEN
                state["circuit_opened_at"] = current_time
        elif current_state == self.STATE_OPEN:
            if current_time - last_failure_time >= recovery_timeout:
                current_state = self.STATE_HALF_OPEN
        elif current_state == self.STATE_HALF_OPEN:
            # Will be updated by the result of the next request
            pass

        state["circuit_state"] = current_state
        state["circuit_allow_request"] = current_state != self.STATE_OPEN
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("failure_threshold", 0) <= 0:
            errors.append("failure_threshold must be positive")
        if state.get("recovery_timeout", 0) < 0:
            errors.append("recovery_timeout must be non-negative")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 12. RateLimiterController
# ---------------------------------------------------------------------------

@controller(
    name="rate_limiter",
    version="1.0.0",
    description="Rate limiting for API calls and operations.",
    level=2,
    tags=["core", "rate-limiting"],
)
class RateLimiterController(ControllerBase):
    """Token bucket rate limiter."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Process rate limit check."""
        max_requests = state.get("max_requests", 100)
        window_seconds = state.get("window_seconds", 60.0)
        request_history: list[float] = state.get("request_history", [])
        current_time = state.get("current_time", time.time())

        # Remove expired timestamps
        cutoff = current_time - window_seconds
        request_history = [t for t in request_history if t > cutoff]

        current_count = len(request_history)
        state["rate_limit_exceeded"] = current_count >= max_requests

        if not state["rate_limit_exceeded"]:
            request_history.append(current_time)
            state["request_accepted"] = True
        else:
            state["request_accepted"] = False
            # Calculate retry-after
            if request_history:
                oldest = min(request_history)
                state["retry_after"] = window_seconds - (current_time - oldest)
            else:
                state["retry_after"] = window_seconds

        state["request_history"] = request_history
        state["rate_limit_remaining"] = max(0, max_requests - len(request_history))
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("max_requests", 0) <= 0:
            errors.append("max_requests must be positive")
        if state.get("window_seconds", 0) <= 0:
            errors.append("window_seconds must be positive")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 13. StateController
# ---------------------------------------------------------------------------

@controller(
    name="state_machine",
    version="1.0.0",
    description="State machine management with transitions.",
    level=2,
    tags=["core", "state-machine"],
)
class StateController(ControllerBase):
    """Finite state machine management."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Process state transition."""
        current = state.get("current_state")
        transitions = state.get("transitions", {})
        trigger = state.get("trigger")

        if trigger is None:
            state["transitioned"] = False
            return state

        available = transitions.get(current, {})
        next_state = available.get(trigger)

        if next_state is None:
            state["transitioned"] = False
            state["transition_error"] = f"No transition from '{current}' on '{trigger}'"
        else:
            state["previous_state"] = current
            state["current_state"] = next_state
            state["transitioned"] = True
            state["transition_trigger"] = trigger
            state["transition_timestamp"] = time.time()

        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if "current_state" not in state:
            errors.append("current_state is required")
        if "transitions" not in state:
            errors.append("transitions is required")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 14. PipelineController
# ---------------------------------------------------------------------------

@controller(
    name="pipeline",
    version="1.0.0",
    description="Multi-stage pipeline execution with error handling.",
    level=3,
    tags=["core", "pipeline"],
)
class PipelineController(ControllerBase):
    """Multi-stage sequential pipeline."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute next pipeline stage."""
        stages: list[dict[str, Any]] = state.get("stages", [])
        current_stage_idx = state.get("current_stage_idx", 0)
        fail_fast = state.get("fail_fast", True)

        if current_stage_idx >= len(stages):
            state["pipeline_status"] = "completed"
            return state

        stage = stages[current_stage_idx]
        stage_name = stage.get("name", f"stage_{current_stage_idx}")
        stage_func = stage.get("func")

        try:
            if stage_func and callable(stage_func):
                result = stage_func(state)
                if result and isinstance(result, dict):
                    state.update(result)
            state["current_stage_idx"] = current_stage_idx + 1
            state["pipeline_status"] = "running"
            state["last_stage"] = stage_name
            state["last_stage_success"] = True
        except Exception as e:
            state["pipeline_status"] = "failed"
            state["last_stage"] = stage_name
            state["last_stage_success"] = False
            state["pipeline_error"] = str(e)
            state["failed_stage_idx"] = current_stage_idx

            if not fail_fast:
                state["current_stage_idx"] = current_stage_idx + 1

        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        stages = state.get("stages", [])
        for i, stage in enumerate(stages):
            if "name" not in stage:
                errors.append(f"Stage {i} missing 'name'")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 15. FallbackController
# ---------------------------------------------------------------------------

@controller(
    name="fallback",
    version="1.0.0",
    description="Fallback strategies when primary action fails.",
    level=3,
    tags=["core", "fallback"],
)
class FallbackController(ControllerBase):
    """Fallback strategy management."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Try primary action, fall back on failure."""
        primary = state.get("primary_action")
        fallbacks: list = state.get("fallbacks", [])
        error = state.get("error")

        if error is None and primary and callable(primary):
            try:
                result = primary(state)
                state["fallback_status"] = "primary_succeeded"
                if result and isinstance(result, dict):
                    state.update(result)
                return state
            except Exception as e:
                state["error"] = str(e)
                error = str(e)

        # Try fallbacks in order
        for i, fallback in enumerate(fallbacks):
            if callable(fallback):
                try:
                    result = fallback(state)
                    state["fallback_status"] = f"fallback_{i}_succeeded"
                    state["fallback_used"] = i
                    if result and isinstance(result, dict):
                        state.update(result)
                    state.pop("error", None)
                    return state
                except Exception as e:
                    state[f"fallback_{i}_error"] = str(e)
                    continue

        state["fallback_status"] = "all_failed"
        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if state.get("primary_action") is None and not state.get("fallbacks"):
            errors.append("Either primary_action or fallbacks required")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# 16. ApprovalController
# ---------------------------------------------------------------------------

@controller(
    name="approval",
    version="1.0.0",
    description="Human approval gate for risky operations.",
    level=5,
    tags=["core", "approval"],
)
class ApprovalController(ControllerBase):
    """Gate operations requiring human approval."""

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check if approval is required and process."""
        risk_level = state.get("risk_level", 1)
        approval_required_above = state.get("approval_required_above", 4)
        approval_status = state.get("approval_status", "pending")

        state["approval_required"] = risk_level >= approval_required_above

        if state["approval_required"]:
            if approval_status == "approved":
                state["approval_result"] = "approved"
                state["operation_allowed"] = True
            elif approval_status == "rejected":
                state["approval_result"] = "rejected"
                state["operation_allowed"] = False
            else:
                state["approval_result"] = "pending"
                state["operation_allowed"] = False
        else:
            state["approval_result"] = "not_required"
            state["operation_allowed"] = True

        return state

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        risk_level = state.get("risk_level", 1)
        if not isinstance(risk_level, (int, float)) or risk_level < 0 or risk_level > 10:
            errors.append("risk_level must be a number between 0 and 10")
        return len(errors) == 0, errors
