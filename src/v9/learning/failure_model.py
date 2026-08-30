"""
failure_model.py — Model and predict failures.

Learns from failed trajectories to predict and prevent future failures.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import re


@dataclass
class FailurePrediction:
    """A predicted failure."""
    capability: str
    probability: float  # 0.0 to 1.0
    failure_type: str
    description: str
    suggested_preventions: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "probability": self.probability,
            "failure_type": self.failure_type,
            "description": self.description,
            "suggested_preventions": self.suggested_preventions,
        }


class FailureModel:
    """
    Models and predicts failures.

    Learns from failed trajectories to predict future failures.
    """

    # Common failure patterns
    FAILURE_PATTERNS = {
        "timeout": {
            "patterns": ["timeout", "timed out", "deadline exceeded"],
            "description": "Operation exceeded time limit",
            "preventions": ["Set explicit time limits", "Use async operations", "Add progress tracking"],
        },
        "syntax_error": {
            "patterns": ["syntax error", "invalid syntax", "parse error"],
            "description": "Code has syntax errors",
            "preventions": ["Use a linter", "Run syntax check before execution", "Use IDE with syntax highlighting"],
        },
        "runtime_error": {
            "patterns": ["runtime error", "exception", "null pointer", "index out of range"],
            "description": "Error during execution",
            "preventions": ["Add error handling", "Write unit tests", "Use type hints"],
        },
        "logic_error": {
            "patterns": ["wrong output", "incorrect result", "unexpected behavior"],
            "description": "Output is incorrect",
            "preventions": ["Write integration tests", "Add assertions", "Manual code review"],
        },
        "resource_exhaustion": {
            "patterns": ["out of memory", "disk full", "connection refused"],
            "description": "System resources exhausted",
            "preventions": ["Add resource monitoring", "Implement retry logic", "Use connection pooling"],
        },
        "permission_error": {
            "patterns": ["permission denied", "access denied", "unauthorized"],
            "description": "Insufficient permissions",
            "preventions": ["Check permissions before operation", "Use least privilege principle", "Add auth checks"],
        },
    }

    def __init__(self):
        self.failure_history: list[dict[str, Any]] = []
        self.failure_counts: dict[str, int] = {}
        self.capability_failures: dict[str, list[str]] = {}

    def learn_from_trajectory(self, trajectory: Any) -> None:
        """
        Learn from a failed trajectory.

        Args:
            trajectory: A failed Trajectory object
        """
        if trajectory.success:
            return

        failure_type = self._classify_failure(trajectory)
        capability = self._extract_capability(trajectory.task)

        self.failure_history.append({
            "task": trajectory.task,
            "failure_type": failure_type,
            "capability": capability,
        })

        self.failure_counts[failure_type] = self.failure_counts.get(failure_type, 0) + 1

        if capability not in self.capability_failures:
            self.capability_failures[capability] = []
        self.capability_failures[capability].append(failure_type)

    def _classify_failure(self, trajectory: Any) -> str:
        """Classify the failure type from a trajectory."""
        all_text = trajectory.task.lower()
        for step in trajectory.steps:
            all_text += " " + step.result.lower()
            all_text += " " + step.observation.lower()

        for failure_type, info in self.FAILURE_PATTERNS.items():
            for pattern in info["patterns"]:
                if pattern in all_text:
                    return failure_type

        return "unknown"

    def _extract_capability(self, task: str) -> str:
        """Extract the capability from a task description."""
        task_lower = task.lower()
        capability_keywords = {
            "coding": ["code", "implement", "function", "class", "algorithm"],
            "debugging": ["debug", "fix", "error", "bug", "issue"],
            "testing": ["test", "verify", "validate", "check"],
            "deployment": ["deploy", "release", "ship", "publish"],
            "data": ["data", "parse", "transform", "process"],
            "api": ["api", "endpoint", "request", "response"],
            "ui": ["ui", "interface", "design", "layout"],
            "database": ["database", "sql", "query", "schema"],
            "auth": ["auth", "login", "token", "permission"],
        }
        for cap, keywords in capability_keywords.items():
            if any(kw in task_lower for kw in keywords):
                return cap
        return "general"

    def predict_failure(
        self,
        capability: str,
        task_description: str = "",
    ) -> FailurePrediction:
        """
        Predict the likelihood of failure for a capability.

        Args:
            capability: The capability to check
            task_description: Optional task description

        Returns:
            FailurePrediction with probability and suggestions
        """
        # Get failure history for this capability
        past_failures = self.capability_failures.get(capability, [])
        total_failures = len(past_failures)

        if total_failures == 0:
            return FailurePrediction(
                capability=capability,
                probability=0.1,
                failure_type="unknown",
                description=f"No failure history for {capability}",
                suggested_preventions=["Proceed with standard precautions"],
            )

        # Calculate failure probability
        probability = min(0.9, total_failures / (total_failures + 10))

        # Find most common failure type
        from collections import Counter
        failure_counter = Counter(past_failures)
        most_common = failure_counter.most_common(1)[0]

        failure_info = self.FAILURE_PATTERNS.get(most_common[0], {
            "description": "Unknown failure",
            "preventions": ["Review past failures"],
        })

        return FailurePrediction(
            capability=capability,
            probability=probability,
            failure_type=most_common[0],
            description=failure_info["description"],
            suggested_preventions=failure_info["preventions"],
            metadata={"failure_count": total_failures},
        )

    def get_most_problematic(self, n: int = 5) -> list[tuple[str, int]]:
        """Get the most problematic capabilities."""
        counts = [(cap, len(fails)) for cap, fails in self.capability_failures.items()]
        counts.sort(key=lambda x: x[1], reverse=True)
        return counts[:n]

    def get_failure_statistics(self) -> dict[str, Any]:
        """Get failure statistics."""
        return {
            "total_failures": len(self.failure_history),
            "failure_counts": dict(self.failure_counts),
            "capability_failures": {k: len(v) for k, v in self.capability_failures.items()},
        }
