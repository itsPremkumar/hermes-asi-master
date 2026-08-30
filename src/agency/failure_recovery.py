"""
P2 Agency & Action — Failure Recovery & Fallback

Graceful degradation when actions fail, alternative plan generation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class FailureRecord:
    """Record of an action failure."""
    id: str
    action_name: str
    error_type: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    recovered: bool = False

    def __post_init__(self) -> None:
        if not self.timestamp:
            import time
            self.timestamp = time.time()


class FailureRecoveryEngine:
    """Autonomous error detection and recovery strategies."""

    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries
        self.failure_log: list[FailureRecord] = []
        self.recovery_strategies: dict[str, Callable] = {}
        self.fallback_plans: dict[str, list[str]] = {}

    def register_strategy(self, error_type: str, strategy: Callable) -> None:
        """Register a recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy

    def register_fallback_plan(self, action_name: str, fallback_steps: list[str]) -> None:
        """Register a fallback plan for an action."""
        self.fallback_plans[action_name] = fallback_steps

    def detect_failure(self, result: Any, context: dict[str, Any] | None = None) -> Optional[FailureRecord]:
        """Detect if a result constitutes a failure."""
        error_type = "unknown"
        message = ""

        if isinstance(result, Exception):
            error_type = type(result).__name__
            message = str(result)
        elif isinstance(result, dict) and result.get("status") == "error":
            error_type = result.get("error_type", "error")
            message = result.get("message", "")
        elif isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], Exception):
            error_type = type(result[1]).__name__
            message = str(result[1])
        else:
            return None  # not a failure

        record = FailureRecord(
            id=str(uuid.uuid4().hex[:8]),
            action_name=context.get("action", "unknown") if context else "unknown",
            error_type=error_type,
            message=message,
            context=context or {},
        )
        self.failure_log.append(record)
        return record

    def recover(self, failure: FailureRecord) -> dict[str, Any]:
        """Attempt to recover from a failure."""
        # Try registered strategy
        if failure.error_type in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[failure.error_type]
                result = strategy(failure)
                failure.recovered = True
                return {"status": "recovered", "strategy": failure.error_type, "result": result}
            except Exception as e:
                return {"status": "strategy_failed", "error": str(e)}

        # Try fallback plan
        if failure.action_name in self.fallback_plans:
            return {
                "status": "fallback",
                "steps": self.fallback_plans[failure.action_name],
            }

        # Generic retry suggestion
        return {
            "status": "unrecovered",
            "suggestion": f"Retry {failure.action_name} or try alternative",
        }

    def get_failure_stats(self) -> dict[str, Any]:
        """Get failure statistics."""
        if not self.failure_log:
            return {"total": 0, "recovered": 0, "by_type": {}}

        by_type: dict[str, int] = {}
        for f in self.failure_log:
            by_type[f.error_type] = by_type.get(f.error_type, 0) + 1

        return {
            "total": len(self.failure_log),
            "recovered": sum(1 for f in self.failure_log if f.recovered),
            "by_type": by_type,
            "recovery_rate": (
                sum(1 for f in self.failure_log if f.recovered) / len(self.failure_log)
            ),
        }

    def get_recent_failures(self, limit: int = 10) -> list[FailureRecord]:
        """Get most recent failures."""
        return self.failure_log[-limit:]

    def clear(self) -> None:
        """Clear failure history."""
        self.failure_log = []
