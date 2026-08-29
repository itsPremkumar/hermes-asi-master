"""
Core debate loop implementation: k-round debate, consensus scoring,
and result aggregation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from .base import BaseRole, LLMResponse, Message
from .roles import Proposer, Critic, Judge, ProposerConfig, CriticConfig, JudgeConfig
from .mock import MockLLM


@dataclass
class ConsensusScore:
    """Consensus scoring result from the judge."""
    verdict: str  # "accept" or "reject"
    score: float  # 0.0 to 1.0
    explanation: str

    @classmethod
    def from_json_str(cls, json_str: str) -> "ConsensusScore":
        """Parse a JSON string from the judge into a ConsensusScore."""
        import json
        data = json.loads(json_str)
        return cls(
            verdict=data["verdict"],
            score=float(data["score"]),
            explanation=data.get("explanation", ""),
        )


@dataclass
class RoundResult:
    """Result of a single debate round."""
    round_num: int
    proposer_response: LLMResponse
    critic_response: LLMResponse
    proposer_message: Message
    critic_message: Message


@dataclass
class DebateResult:
    """Final result of a completed debate."""
    topic: str
    rounds: list[RoundResult] = field(default_factory=list)
    final_history: list[Message] = field(default_factory=list)
    consensus: ConsensusScore | None = None
    judge_response: LLMResponse | None = None
    total_rounds: int = 0


class Debate:
    """
    Manages a k-round debate between a Proposer and Critic,
    with a final judgment by the Judge.

    The debate proceeds as follows:
    - Round 0: Proposer presents initial proposal
    - Round 0: Critic critiques the proposal
    - Round 1..k-1: Proposer refines, Critic critiques
    - Final: Judge evaluates and assigns consensus score
    """

    def __init__(
        self,
        topic: str,
        k_rounds: int = 3,
        proposer: Proposer | None = None,
        critic: Critic | None = None,
        judge: Judge | None = None,
    ):
        if k_rounds < 1:
            raise ValueError("k_rounds must be at least 1")

        self.topic = topic
        self.k_rounds = k_rounds
        self.proposer = proposer or Proposer()
        self.critic = critic or Critic()
        self.judge = judge or Judge()
        self.history: list[Message] = []
        self.rounds: list[RoundResult] = []
        self._round_counter = 0

    def run(self) -> DebateResult:
        """Execute the full k-round debate and return the result."""
        result = DebateResult(topic=self.topic)

        # Round 0: Proposer opens
        prop_resp = self.proposer.act([], round_num=0)
        prop_msg = Message(role="proposer", content=prop_resp.content, round_num=0)
        self.history.append(prop_msg)

        # Round 0: Critic critiques
        crit_resp = self.critic.act(self.history, round_num=0)
        crit_msg = Message(role="critic", content=crit_resp.content, round_num=0)
        self.history.append(crit_msg)

        round0 = RoundResult(
            round_num=0,
            proposer_response=prop_resp,
            critic_response=crit_resp,
            proposer_message=prop_msg,
            critic_message=crit_msg,
        )
        self.rounds.append(round0)
        result.rounds.append(round0)

        # Rounds 1..k-1
        for r in range(1, self.k_rounds):
            prop_resp = self.proposer.act(self.history, round_num=r)
            prop_msg = Message(role="proposer", content=prop_resp.content, round_num=r)
            self.history.append(prop_msg)

            crit_resp = self.critic.act(self.history, round_num=r)
            crit_msg = Message(role="critic", content=crit_resp.content, round_num=r)
            self.history.append(crit_msg)

            round_result = RoundResult(
                round_num=r,
                proposer_response=prop_resp,
                critic_response=crit_resp,
                proposer_message=prop_msg,
                critic_message=crit_msg,
            )
            self.rounds.append(round_result)
            result.rounds.append(round_result)

        # Judge evaluates
        judge_resp = self.judge.act(self.history, round_num=self.k_rounds)
        judge_msg = Message(role="judge", content=judge_resp.content, round_num=self.k_rounds)
        self.history.append(judge_msg)

        result.final_history = list(self.history)
        result.judge_response = judge_resp
        result.consensus = ConsensusScore.from_json_str(judge_resp.content)
        result.total_rounds = self.k_rounds

        return result

    def add_initial_context(self, msg: Message) -> None:
        """Add initial context (e.g., user-provided topic framing) to the debate."""
        msg.role = "user"
        self.history.append(msg)


# ---- Factory functions for building debates with mocks ----

def build_mock_debate(
    topic: str,
    k_rounds: int = 3,
    proposer_responses: list[str] | None = None,
    critic_responses: list[str] | None = None,
    judge_response: str | None = None,
) -> Debate:
    """Build a Debate with mock LLMs for testing."""
    from .mock import ProposerMockLLM, CriticMockLLM, JudgeMockLLM
    prop_llm = MockLLM(responses=proposer_responses) if proposer_responses else ProposerMockLLM()
    crit_llm = MockLLM(responses=critic_responses) if critic_responses else CriticMockLLM()
    judge_llm = MockLLM(responses=[judge_response]) if judge_response else JudgeMockLLM()

    proposer = Proposer(llm=prop_llm)
    critic = Critic(llm=crit_llm)
    judge = Judge(llm=judge_llm)

    return Debate(
        topic=topic,
        k_rounds=k_rounds,
        proposer=proposer,
        critic=critic,
        judge=judge,
    )


def build_judge_mock_debate(
    topic: str,
    k_rounds: int = 3,
    verdict: str = "accept",
    score: float = 0.8,
    explanation: str = "Mock judgment",
    proposer_responses: list[str] | None = None,
    critic_responses: list[str] | None = None,
) -> Debate:
    """Build a Debate with a judge that returns a specific verdict."""
    import json
    judge_json = json.dumps({
        "verdict": verdict,
        "score": score,
        "explanation": explanation,
    })

    return build_mock_debate(
        topic=topic,
        k_rounds=k_rounds,
        proposer_responses=proposer_responses,
        critic_responses=critic_responses,
        judge_response=judge_json,
    )
