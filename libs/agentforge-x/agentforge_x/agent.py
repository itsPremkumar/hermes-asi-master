"""
Core Agent class implementing the thin kernel loop:
sense -> plan -> act -> critique -> repeat

Each agent type (researcher, coder, critic, tester, writer, ops)
is a subclass that provides its specific planner/critic/executor prompts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class AgentType(str, Enum):
    """The six agent types in the agentforge-x fleet."""
    RESEARCHER = "researcher"
    CODER = "coder"
    CRITIC = "critic"
    TESTER = "tester"
    WRITER = "writer"
    OPS = "ops"


class AgentState(str, Enum):
    """States in the kernel loop."""
    IDLE = "idle"
    SENSING = "sensing"
    PLANNING = "planning"
    ACTING = "acting"
    CRITIQUING = "critiquing"
    DONE = "done"
    ERROR = "error"


@dataclass
class Plan:
    """A plan produced by the planner prompt."""
    steps: list[str]
    reasoning: str
    confidence: float  # 0.0 to 1.0


@dataclass
class Action:
    """An action produced by the executor."""
    tool: str
    args: dict[str, Any]
    result: str = ""
    success: bool = True


@dataclass
class Critique:
    """A critique of the agent's work."""
    score: float  # 0.0 to 1.0
    feedback: str
    strengths: list[str]
    weaknesses: list[str]


@dataclass
class PromptSet:
    """Versioned set of prompts for an agent."""
    planner_prompt: str
    critic_prompt: str
    executor_prompt: str
    few_shots: list[str] = field(default_factory=list)
    version: str = "1.0.0"


class JudgeResult:
    """Result from the critic/judge evaluation."""
    def __init__(self, score: float, feedback: str, strengths: list[str] | None = None,
                 weaknesses: list[str] | None = None):
        self.score = score
        self.feedback = feedback
        self.strengths = strengths or []
        self.weaknesses = weaknesses or []

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "feedback": self.feedback,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


class Agent:
    """
    A thin kernel-loop agent. Subclasses define their prompt set
    and optionally override the kernel steps.

    Kernel loop:
        sense -> plan -> act -> critique -> [repeat | done]
    """

    def __init__(
        self,
        agent_type: AgentType,
        prompts: PromptSet,
        llm: Optional[Callable[[str], str]] = None,
        max_iterations: int = 3,
        name: Optional[str] = None,
    ):
        self.agent_type = agent_type
        self.prompts = prompts
        self.llm = llm
        self.max_iterations = max_iterations
        self.name = name or agent_type.value
        self.state: AgentState = AgentState.IDLE
        self.history: list[dict[str, Any]] = []
        self._iteration = 0
        self._final_result: Optional[str] = None

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with a prompt. Falls back to placeholder if no LLM."""
        if self.llm is None:
            return f"[{self.name}] Placeholder response for: {prompt[:60]}..."
        return self.llm(prompt)

    def sense(self, input_text: str) -> dict[str, Any]:
        """Sense: ingest input and produce observations."""
        self.state = AgentState.SENSING
        observation = {
            "input": input_text,
            "iteration": self._iteration,
        }
        self.history.append({"step": "sense", "data": observation})
        return observation

    def plan(self, observation: dict[str, Any]) -> Plan:
        """Plan: produce a plan using the planner prompt."""
        self.state = AgentState.PLANNING
        prompt = self._build_plan_prompt(observation)
        response = self._call_llm(prompt)

        # Parse the plan response — for mock LLMs, we parse structured output
        plan = self._parse_plan(response)
        self.history.append({"step": "plan", "data": plan})
        return plan

    def act(self, plan: Plan) -> Action:
        """Act: execute a step of the plan using the executor prompt."""
        self.state = AgentState.ACTING
        if not plan.steps:
            action = Action(tool="noop", args={"reason": "no steps to execute"})
        else:
            step = plan.steps[min(self._iteration, len(plan.steps) - 1)]
            prompt = self._build_executor_prompt(step, plan)
            response = self._call_llm(prompt)
            action = Action(tool="executor", args={"step": step}, result=response)

        self.history.append({"step": "act", "data": action})
        return action

    def critique(self, action: Action) -> JudgeResult:
        """Critique: evaluate the action using the critic prompt."""
        self.state = AgentState.CRITIQUING
        prompt = self._build_critic_prompt(action)
        response = self._call_llm(prompt)
        critique = self._parse_critique(response)
        self.history.append({"step": "critique", "data": critique})
        return critique

    def run(self, input_text: str) -> str:
        """Execute the full kernel loop and return the final result."""
        self.state = AgentState.IDLE
        self._iteration = 0

        for i in range(self.max_iterations):
            self._iteration = i
            observation = self.sense(input_text)
            plan = self.plan(observation)
            action = self.act(plan)
            critique = self.critique(action)

            # If critique score is high enough, stop iterating
            if critique.score >= 0.8:
                self._final_result = action.result
                self.state = AgentState.DONE
                return self._final_result

        # Max iterations reached
        self._final_result = action.result if 'action' in locals() else ""
        self.state = AgentState.DONE
        return self._final_result

    def _build_plan_prompt(self, observation: dict[str, Any]) -> str:
        """Build the planner prompt with context."""
        prompt = f"{self.prompts.planner_prompt}\n\n"
        if self.prompts.few_shots:
            prompt += "Few-shot examples:\n"
            for fs in self.prompts.few_shots:
                prompt += f"- {fs}\n"
        prompt += f"\nInput: {observation['input']}\n"
        prompt += f"Iteration: {observation['iteration']}\n"
        prompt += "\nPlan (output as: STEPS: step1 | step2 | step3 | REASONING: <text> | CONFIDENCE: <0-1>):"
        return prompt

    def _build_executor_prompt(self, step: str, plan: Plan) -> str:
        """Build the executor prompt."""
        prompt = f"{self.prompts.executor_prompt}\n\n"
        if self.prompts.few_shots:
            prompt += "Few-shot examples:\n"
            for fs in self.prompts.few_shots:
                prompt += f"- {fs}\n"
        prompt += f"\nPlan steps: {' | '.join(plan.steps)}\n"
        prompt += f"Reasoning: {plan.reasoning}\n"
        prompt += f"Current step: {step}\n"
        prompt += "\nExecute this step and return your result:"
        return prompt

    def _build_critic_prompt(self, action: Action) -> str:
        """Build the critic prompt."""
        prompt = f"{self.prompts.critic_prompt}\n\n"
        if self.prompts.few_shots:
            prompt += "Few-shot examples:\n"
            for fs in self.prompts.few_shots:
                prompt += f"- {fs}\n"
        prompt += f"\nAction taken: {action.result}\n"
        prompt += f"Tool: {action.tool}\n"
        prompt += f"Args: {action.args}\n"
        prompt += "\nEvaluate (output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>):"
        return prompt

    def _parse_plan(self, response: str) -> Plan:
        """Parse a plan response string into a Plan object."""
        import re

        # Look for structured format: STEPS: ... | REASONING: ... | CONFIDENCE: ...
        steps_match = re.search(r'STEPS:\s*(.+?)(?:\s*\|\s*REASONING:|$)', response)
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\s*\|\s*CONFIDENCE:|$)', response)
        confidence_match = re.search(r'CONFIDENCE:\s*([0-9.]+)', response)

        if steps_match:
            steps = [s.strip() for s in steps_match.group(1).split('|')]
            steps = [s for s in steps if s]  # Remove empty
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
        else:
            # Fallback: treat entire response as a single-step plan
            steps = [response.strip()]
            reasoning = "Parsed from raw response"
            confidence = 0.5

        return Plan(steps=steps, reasoning=reasoning, confidence=confidence)

    def _parse_critique(self, response: str) -> JudgeResult:
        """Parse a critique response string into a JudgeResult."""
        import re

        score_match = re.search(r'SCORE:\s*([0-9.]+)', response)
        feedback_match = re.search(r'FEEDBACK:\s*(.+?)(?:\s*\|\s*STRENGTHS:|$)', response)
        strengths_match = re.search(r'STRENGTHS:\s*(.+?)(?:\s*\|\s*WEAKNESSES:|$)', response)
        weaknesses_match = re.search(r'WEAKNESSES:\s*(.+)', response)

        score = float(score_match.group(1)) if score_match else 0.5
        feedback = feedback_match.group(1).strip() if feedback_match else response.strip()
        strengths = [s.strip() for s in strengths_match.group(1).split(',')] if strengths_match else []
        strengths = [s for s in strengths if s]
        weaknesses = [s.strip() for s in weaknesses_match.group(1).split(',')] if weaknesses_match else []
        weaknesses = [s for s in weaknesses if s]

        return JudgeResult(score=score, feedback=feedback, strengths=strengths, weaknesses=weaknesses)

    @property
    def final_result(self) -> str:
        return self._final_result or ""

    @property
    def iteration_count(self) -> int:
        return self._iteration + 1 if self.state == AgentState.DONE else self._iteration
