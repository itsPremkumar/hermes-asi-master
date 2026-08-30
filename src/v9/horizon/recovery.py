"""
v9 Long-Horizon Engineering — Recovery System

Failure recovery system for long-running workflows.
Supports exponential backoff, fallback strategies, and graceful degradation.
"""

from __future__ import annotations
import asyncio
import enum
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)


class FailureType(enum.Enum):
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    RESOURCE = "resource"
    LOGIC = "logic"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class RecoveryStrategy(enum.Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    DEGRADE = "degrade"


@dataclass
class FailureEvent:
    id: str
    task_id: str
    failure_type: FailureType
    message: str
    timestamp: float
    context: dict = field(default_factory=dict)
    recoverable: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:12]


@dataclass
class RecoveryResult:
    success: bool
    strategy: RecoveryStrategy
    attempts: int
    total_delay: float
    final_output: Any = None
    final_error: Optional[str] = None
    recovery_id: str = ""

    def __post_init__(self):
        if not self.recovery_id:
            self.recovery_id = str(uuid.uuid4())[:12]


class BackoffStrategy:
    """Compute retry delays."""

    @staticmethod
    def exponential(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
        delay = base * (2 ** attempt)
        return min(delay, max_delay)

    @staticmethod
    def linear(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
        delay = base * (attempt + 1)
        return min(delay, max_delay)

    @staticmethod
    def constant(attempt: int, delay: float = 1.0) -> float:
        return delay

    @staticmethod
    def jitter(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
        import random
        exp = base * (2 ** attempt)
        return min(random.uniform(0, exp), max_delay)


class FallbackRegistry:
    """Registry for fallback handlers."""

    def __init__(self):
        self._fallbacks: dict[str, Callable] = {}

    def register(self, task_id: str, fallback: Callable):
        """Register a fallback handler."""
        self._fallbacks[task_id] = fallback

    def get(self, task_id: str) -> Optional[Callable]:
        """Get fallback handler."""
        return self._fallbacks.get(task_id)

    def has(self, task_id: str) -> bool:
        """Check if fallback exists."""
        return task_id in self._fallbacks


class RecoveryManager:
    """Manage failure recovery."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_base: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.max_delay = max_delay
        self.jitter = jitter
        self._fallbacks = FallbackRegistry()
        self._history: list[RecoveryResult] = []
        self._failure_counts: dict[FailureType, int] = {}

    @property
    def failure_counts(self) -> dict[FailureType, int]:
        return dict(self._failure_counts)

    def register_fallback(self, task_id: str, fallback: Callable):
        """Register a fallback handler for a task."""
        self._fallbacks.register(task_id, fallback)

    async def execute_with_recovery(
        self,
        task_id: str,
        func: Callable[..., Awaitable[Any]],
        *args,
        fallback: Optional[Callable] = None,
        **kwargs,
    ) -> RecoveryResult:
        """Execute a function with automatic recovery."""
        attempts = 0
        total_delay = 0.0
        last_error = None

        while attempts <= self.max_retries:
            try:
                output = await func(*args, **kwargs)
                return RecoveryResult(
                    success=True,
                    strategy=RecoveryStrategy.RETRY,
                    attempts=attempts + 1,
                    total_delay=total_delay,
                    final_output=output,
                )
            except Exception as e:
                last_error = str(e)
                failure_type = self._classify_error(e)
                self._failure_counts[failure_type] = self._failure_counts.get(failure_type, 0) + 1

                logger.warning(
                    f"Task {task_id} failed (attempt {attempts + 1}): {e}"
                )

                if attempts >= self.max_retries:
                    break

                # Compute backoff
                if self.jitter:
                    delay = BackoffStrategy.jitter(attempts, self.backoff_base, self.max_delay)
                else:
                    delay = BackoffStrategy.exponential(attempts, self.backoff_base, self.max_delay)

                total_delay += delay
                await asyncio.sleep(delay)
                attempts += 1

        # Try fallback
        fb = fallback or self._fallbacks.get(task_id)
        if fb:
            try:
                output = await fb(*args, **kwargs)
                result = RecoveryResult(
                    success=True,
                    strategy=RecoveryStrategy.FALLBACK,
                    attempts=attempts + 1,
                    total_delay=total_delay,
                    final_output=output,
                )
                self._history.append(result)
                return result
            except Exception as e:
                last_error = f"Fallback also failed: {e}"

        result = RecoveryResult(
            success=False,
            strategy=RecoveryStrategy.ABORT,
            attempts=attempts + 1,
            total_delay=total_delay,
            final_error=last_error,
        )
        self._history.append(result)
        return result

    def _classify_error(self, error: Exception) -> FailureType:
        """Classify an error into a failure type."""
        error_str = str(error).lower()
        if "timeout" in error_str:
            return FailureType.TIMEOUT
        elif "rate" in error_str or "limit" in error_str:
            return FailureType.RATE_LIMIT
        elif "network" in error_str or "connection" in error_str:
            return FailureType.NETWORK
        elif "resource" in error_str or "memory" in error_str:
            return FailureType.RESOURCE
        elif "permission" in error_str or "auth" in error_str:
            return FailureType.PERMISSION
        else:
            return FailureType.UNKNOWN

    def get_history(self) -> list[RecoveryResult]:
        """Get recovery history."""
        return list(self._history)

    def to_dict(self) -> dict:
        return {
            "max_retries": self.max_retries,
            "backoff_base": self.backoff_base,
            "max_delay": self.max_delay,
            "jitter": self.jitter,
            "failure_counts": {k.value: v for k, v in self._failure_counts.items()},
            "history": [
                {
                    "success": r.success,
                    "strategy": r.strategy.value,
                    "attempts": r.attempts,
                    "total_delay": r.total_delay,
                    "final_error": r.final_error,
                }
                for r in self._history
            ],
        }


class GracefulDegradation:
    """Graceful degradation strategies."""

    @staticmethod
    def reduce_quality(output: Any) -> Any:
        """Reduce output quality (e.g., shorter response)."""
        if isinstance(output, str):
            return output[:500] + "..." if len(output) > 500 else output
        return output

    @staticmethod
    def use_cached(output: Any, cache: dict) -> Any:
        """Use cached result if available."""
        return cache.get("last_result", output)

    @staticmethod
    def partial_complete(completed_steps: list, total_steps: int) -> dict:
        """Return partial completion status."""
        return {
            "status": "partial",
            "completed": len(completed_steps),
            "total": total_steps,
            "progress": len(completed_steps) / max(total_steps, 1),
            "results": completed_steps,
        }
