"""
Mock LLM implementations for testing agentforge-x.

Provides deterministic mocks for the six agent types and the judge,
enabling precise testing of the kernel loop without real model calls.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class LLMMetrics:
    """Track metrics about LLM calls for test assertions."""
    call_count: int = 0
    prompts_seen: list[str] = field(default_factory=list)


class MockLLM:
    """
    A mock LLM that returns predetermined responses in sequence,
    or generates responses based on a function.
    """

    def __init__(
        self,
        responses: list[str] | None = None,
        func: Callable[[str], str] | None = None,
        raise_on_call: Exception | None = None,
    ):
        if responses is not None and func is not None:
            raise ValueError("Cannot specify both 'responses' and 'func'")

        self._responses = responses or []
        self._func = func
        self._call_index = 0
        self.metrics = LLMMetrics()
        self._raise_on_call = raise_on_call

    def __call__(self, prompt: str) -> str:
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

        return ""

    @property
    def call_count(self) -> int:
        return self.metrics.call_count

    @property
    def prompts_seen(self) -> list[str]:
        return self.metrics.prompts_seen

    def reset(self) -> None:
        self._call_index = 0
        self.metrics = LLMMetrics()


class AgentMockLLM(MockLLM):
    """
    A mock LLM that produces structured agent output:
    - For planner prompts: returns STEPS/REASONING/CONFIDENCE format
    - For executor prompts: returns execution results
    - For critic prompts: returns SCORE/FEEDBACK/STRENGTHS/WEAKNESSES format
    """

    def __init__(
        self,
        plan_responses: list[str] | None = None,
        executor_responses: list[str] | None = None,
        critic_responses: list[str] | None = None,
    ):
        self._plan_responses = plan_responses or [
            "STEPS: step1 | step2 | step3 | REASONING: Sound approach | CONFIDENCE: 0.8",
        ]
        self._executor_responses = executor_responses or [
            "Execution complete. Result: task accomplished.",
        ]
        self._critic_responses = critic_responses or [
            "SCORE: 0.85 | FEEDBACK: Good work | STRENGTHS: clear, thorough | WEAKNESSES: minor detail missing",
        ]
        self._plan_idx = 0
        self._exec_idx = 0
        self._crit_idx = 0
        self.metrics = LLMMetrics()

    def __call__(self, prompt: str) -> str:
        self.metrics.call_count += 1
        self.metrics.prompts_seen.append(prompt)

        if "STEPS:" in prompt or "Plan" in prompt or "plan" in prompt:
            if self._plan_idx < len(self._plan_responses):
                result = self._plan_responses[self._plan_idx]
                self._plan_idx += 1
                return result
            return self._plan_responses[-1] if self._plan_responses else "STEPS: noop | REASONING: none | CONFIDENCE: 0.5"

        if "Execute" in prompt or "execute" in prompt or "step" in prompt.lower():
            if self._exec_idx < len(self._executor_responses):
                result = self._executor_responses[self._exec_idx]
                self._exec_idx += 1
                return result
            return self._executor_responses[-1] if self._executor_responses else "Execution complete."

        if "SCORE:" in prompt or "Evaluate" in prompt or "critique" in prompt.lower():
            if self._crit_idx < len(self._critic_responses):
                result = self._critic_responses[self._crit_idx]
                self._crit_idx += 1
                return result
            return self._critic_responses[-1] if self._critic_responses else "SCORE: 0.5 | FEEDBACK: ok | STRENGTHS: adequate | WEAKNESSES: none"

        return "Default mock response"


class JudgeMockLLM(MockLLM):
    """
    A mock LLM for the judge that returns valid JSON verdicts
    matching the debate-room ConsensusScore format.
    """

    def __init__(self, verdict: str = "accept", score: float = 0.8,
                 explanation: str = "Mock judgment", evidence: list[str] | None = None):
        import json
        responses = [
            json.dumps({
                "verdict": verdict,
                "score": score,
                "explanation": explanation,
                "evidence": evidence or ["Mock evidence quote"],
            })
        ]
        super().__init__(responses=responses)
