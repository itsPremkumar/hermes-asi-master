"""Concrete role implementations: Proposer, Critic, Judge."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from .base import BaseRole, LLMResponse, Message, RoleConfig


# ---- System prompts ----

PROPOSER_PROMPT = """\
You are the Proposer in a structured debate. Your job is to present a position,
defend it against criticism, refine it across rounds, and ultimately produce
a clear proposal. In each round you will receive the full message history of
the debate so far. You should:
1. Address points raised by the Critic in the previous round.
2. Refine or adjust your proposal based on valid criticism.
3. Restate your key position clearly.
Be concise but thorough."""


CRITIC_PROMPT = """\
You are the Critic in a structured debate. Your job is to find weaknesses,
flaws, and gaps in the Proposer's position. In each round you will receive
the full message history. You should:
1. Identify the strongest points from the Proposer's latest statement.
2. Find specific weaknesses, logical fallacies, or unaddressed concerns.
3. Propose concrete refinements or counter-examples.
Be rigorous and constructive. Do not simply disagree — provide reasons."""


JUDGE_PROMPT = """\
You are the Judge in a structured debate. Your job is to evaluate the final
state of the debate between the Proposer and Critic, and assign:
1. A final verdict — either "accept" or "reject" the proposal.
2. A consensus score between 0.0 and 1.0 indicating overall agreement.
3. A brief explanation citing evidence from the debate transcript.

Respond ONLY in strict JSON:
{"verdict": "accept"|"reject", "score": <float 0-1>, "explanation": "<string>"}"""


@dataclass
class ProposerConfig(RoleConfig):
    def __init__(self, name: str = "Proposer", temperature: float = 0.7, max_tokens: int = 512):
        super().__init__(
            name=name,
            system_prompt=PROPOSER_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )


@dataclass
class CriticConfig(RoleConfig):
    def __init__(self, name: str = "Critic", temperature: float = 0.7, max_tokens: int = 512):
        super().__init__(
            name=name,
            system_prompt=CRITIC_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )


@dataclass
class JudgeConfig(RoleConfig):
    def __init__(self, name: str = "Judge", temperature: float = 0.3, max_tokens: int = 256):
        super().__init__(
            name=name,
            system_prompt=JUDGE_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )


class Proposer(BaseRole):
    """The Proposer presents and defends a position."""

    def __init__(self, config: ProposerConfig | None = None, llm: Any = None):
        super().__init__(config or ProposerConfig())
        self.llm = llm

    def act(self, context: list[Message], round_num: int) -> LLMResponse:
        """Generate a proposal or response based on debate context."""
        if round_num == 0 and not context:
            # Opening statement — no prior context
            prompt = f"{self.config.system_prompt}\n\nRound 0: Present your initial proposal on the topic."
        else:
            # Build context from message history
            history_text = self._format_context(context)
            prompt = (
                f"{self.config.system_prompt}\n\n"
                f"Debate History:\n{history_text}\n\n"
                f"Round {round_num}: Respond to the critic's latest points "
                f"and refine your proposal."
            )

        if self.llm is None:
            # Fallback when no LLM is set — produce a deterministic placeholder
            content = f"[Proposer round {round_num}] Placeholder proposal response"
        else:
            content = self.llm(prompt)

        msg = Message(role=self.config.name, content=content, round_num=round_num)
        self.add_to_history(msg)
        return LLMResponse(content=content)

    @staticmethod
    def _format_context(context: list[Message]) -> str:
        lines = []
        for msg in context:
            lines.append(f"[{msg.role} r{msg.round_num}] {msg.content}")
        return "\n".join(lines)


class Critic(BaseRole):
    """The Critic finds flaws and weaknesses in the Proposer's position."""

    def __init__(self, config: CriticConfig | None = None, llm: Any = None):
        super().__init__(config or CriticConfig())
        self.llm = llm

    def act(self, context: list[Message], round_num: int) -> LLMResponse:
        """Critique the Proposer's latest statement."""
        if not context:
            prompt = f"{self.config.system_prompt}\n\nNo proposal yet — wait for the proposer."
            content = "Waiting for proposer's initial statement."
        else:
            history_text = self._format_context(context)
            prompt = (
                f"{self.config.system_prompt}\n\n"
                f"Debate History:\n{history_text}\n\n"
                f"Round {round_num}: Critique the proposer's position. "
                f"Find weaknesses and suggest improvements."
            )
            if self.llm is None:
                content = f"[Critic round {round_num}] Placeholder critique"
            else:
                content = self.llm(prompt)

        msg = Message(role=self.config.name, content=content, round_num=round_num)
        self.add_to_history(msg)
        return LLMResponse(content=content)

    @staticmethod
    def _format_context(context: list[Message]) -> str:
        lines = []
        for msg in context:
            lines.append(f"[{msg.role} r{msg.round_num}] {msg.content}")
        return "\n".join(lines)


class Judge(BaseRole):
    """The Judge evaluates the final debate and produces a verdict."""

    def __init__(self, config: JudgeConfig | None = None, llm: Any = None):
        super().__init__(config or JudgeConfig())
        self.llm = llm

    def act(self, context: list[Message], round_num: int) -> LLMResponse:
        """Evaluate the debate and return a structured verdict."""
        history_text = self._format_context(context)
        prompt = (
            f"{self.config.system_prompt}\n\n"
            f"Debate Transcript:\n{history_text}\n\n"
            f"Evaluate the final state and return your verdict as strict JSON."
        )

        if self.llm is None:
            content = '{"verdict": "accept", "score": 0.5, "explanation": "Placeholder judgment"}'
        else:
            content = self.llm(prompt)

        msg = Message(role=self.config.name, content=content, round_num=round_num)
        self.add_to_history(msg)
        return LLMResponse(content=content)

    @staticmethod
    def _format_context(context: list[Message]) -> str:
        lines = []
        for msg in context:
            lines.append(f"[{msg.role} r{msg.round_num}] {msg.content}")
        return "\n".join(lines)
