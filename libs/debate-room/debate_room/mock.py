"""
Mock LLM implementations for testing the debate framework.

These mocks allow deterministic control over LLM outputs, enabling
precise testing of the debate loop logic without requiring real model calls.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class LLMMetrics:
    """Track metrics about LLM calls for test assertions."""
    call_count: int = 0
    prompts_seen: list[str] = field(default_factory=list)


class MockLLM:
    """
    A mock LLM that returns predetermined responses in sequence,
    or generates responses based on a function.

    Usage:
        # Sequential responses
        llm = MockLLM(responses=["resp1", "resp2", "resp3"])

        # Or functional
        llm = MockLLM(func=lambda prompt: f"Echo: {len(prompt)}")

        # Or callable
        llm = MockLLM(callable=lambda prompt: "fixed response")
    """

    def __init__(
        self,
        responses: list[str] | None = None,
        func: Callable[[str], str] | None = None,
        callable_fn: Callable[[str], str] | None = None,
        raise_on_call: Exception | None = None,
    ):
        if responses is not None and func is not None:
            raise ValueError("Cannot specify both 'responses' and 'func'")
        if responses is not None and callable_fn is not None:
            raise ValueError("Cannot specify both 'responses' and 'callable_fn'")
        if func is not None and callable_fn is not None:
            raise ValueError("Cannot specify both 'func' and 'callable_fn'")

        self._responses = responses or []
        self._func = func or callable_fn
        self._call_index = 0
        self.metrics = LLMMetrics()
        self._raise_on_call = raise_on_call

    def __call__(self, prompt: str) -> str:
        """Simulate an LLM call. Returns the next response or computed result."""
        self.metrics.call_count += 1
        self.metrics.prompts_seen.append(prompt)

        if self._raise_on_call is not None:
            raise self._raise_on_call

        if self._func is not None:
            return self._func(prompt)

        if self._call_index < len(self._responses):
            result = self._responses[self._call_index]
            self._call_index += 1
            return result

        # Default: cycle or return empty if no responses
        return ""

    @property
    def call_count(self) -> int:
        return self.metrics.call_count

    @property
    def prompts_seen(self) -> list[str]:
        return self.metrics.prompts_seen

    def reset(self) -> None:
        """Reset the call index and metrics."""
        self._call_index = 0
        self.metrics = LLMMetrics()


class JudgeMockLLM(MockLLM):
    """
    A specialized mock LLM for the judge role that returns valid JSON verdicts.
    """

    def __init__(self, verdict: str = "accept", score: float = 0.8, explanation: str = "Mock judgment"):
        responses = [
            f'{{"verdict": "{verdict}", "score": {score}, "explanation": "{explanation}"}}'
        ]
        super().__init__(responses=responses)


class ProposerMockLLM(MockLLM):
    """
    A specialized mock LLM for the proposer that generates proposal-like text.
    """

    def __init__(self, proposals: list[str] | None = None):
        if proposals is None:
            proposals = [
                "Proposal: We should implement a microservices architecture.",
                "Revised proposal: Given the feedback, we should use a hybrid approach.",
                "Final proposal: After considering criticisms, we maintain our position with adjustments.",
            ]
        super().__init__(responses=proposals)


class CriticMockLLM(MockLLM):
    """
    A specialized mock LLM for the critic that generates critique-like text.
    """

    def __init__(self, critiques: list[str] | None = None):
        if critiques is None:
            critiques = [
                "Criticism 1: The microservices approach has high operational complexity.",
                "Criticism 2: The hybrid model introduces coupling risks between components.",
            ]
        super().__init__(responses=critiques)
