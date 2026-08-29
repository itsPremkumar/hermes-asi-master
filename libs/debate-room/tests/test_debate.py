"""Tests for the Debate loop, DebateResult, ConsensusScore, and factory functions."""

import pytest
import json
from debate_room.roles import Proposer, Critic, Judge, Message, LLMResponse
from debate_room.mock import MockLLM, JudgeMockLLM, ProposerMockLLM, CriticMockLLM
from debate_room.debate import (
    Debate, DebateResult, RoundResult, ConsensusScore,
    build_mock_debate, build_judge_mock_debate,
)


class TestConsensusScore:
    """Tests for ConsensusScore parsing."""

    def test_from_json_str_valid(self):
        json_str = '{"verdict": "accept", "score": 0.85, "explanation": "Good"}'
        score = ConsensusScore.from_json_str(json_str)
        assert score.verdict == "accept"
        assert score.score == 0.85
        assert score.explanation == "Good"

    def test_from_json_str_reject(self):
        json_str = '{"verdict": "reject", "score": 0.3, "explanation": "Flawed"}'
        score = ConsensusScore.from_json_str(json_str)
        assert score.verdict == "reject"
        assert score.score == 0.3

    def test_from_json_str_score_is_float(self):
        json_str = '{"verdict": "accept", "score": 0.75, "explanation": "ok"}'
        score = ConsensusScore.from_json_str(json_str)
        assert isinstance(score.score, float)

    def test_from_json_str_with_missing_explanation(self):
        json_str = '{"verdict": "accept", "score": 0.5}'
        score = ConsensusScore.from_json_str(json_str)
        assert score.explanation == ""


class TestRoundResult:
    """Tests for RoundResult dataclass."""

    def test_round_result_fields(self):
        prop_resp = LLMResponse(content="prop content")
        crit_resp = LLMResponse(content="crit content")
        prop_msg = Message(role="proposer", content="prop content", round_num=1)
        crit_msg = Message(role="critic", content="crit content", round_num=1)

        rr = RoundResult(
            round_num=1,
            proposer_response=prop_resp,
            critic_response=crit_resp,
            proposer_message=prop_msg,
            critic_message=crit_msg,
        )
        assert rr.round_num == 1
        assert rr.proposer_response.content == "prop content"
        assert rr.critic_response.content == "crit content"


class TestDebate:
    """Tests for the core Debate loop."""

    def test_debate_one_round(self):
        debate = build_judge_mock_debate(
            topic="test topic",
            k_rounds=1,
            verdict="accept",
            score=0.9,
            explanation="One round test",
        )
        result = debate.run()
        assert result.topic == "test topic"
        assert result.total_rounds == 1
        assert len(result.rounds) == 1
        assert len(result.final_history) == 3  # proposer + critic + judge

    def test_debate_three_rounds(self):
        debate = build_judge_mock_debate(
            topic="topic 3",
            k_rounds=3,
        )
        result = debate.run()
        assert result.total_rounds == 3
        assert len(result.rounds) == 3
        # 3 rounds × 2 messages (prop + critic) + 1 judge = 7
        assert len(result.final_history) == 7

    def test_debate_history_order(self):
        prop_responses = ["proposal 0", "refined 1", "final 2"]
        crit_responses = ["critique 0", "critique 1", "critique 2"]
        judge_json = '{"verdict": "accept", "score": 0.7, "explanation": "done"}'

        debate = build_mock_debate(
            topic="ordering test",
            k_rounds=3,
            proposer_responses=prop_responses,
            critic_responses=crit_responses,
            judge_response=judge_json,
        )
        result = debate.run()
        roles = [msg.role for msg in result.final_history]
        # Expected: prop, crit, prop, crit, prop, crit, judge
        assert roles == ["proposer", "critic", "proposer", "critic", "proposer", "critic", "judge"]

    def test_debate_round_numbers(self):
        debate = build_judge_mock_debate(topic="rounds test", k_rounds=2)
        result = debate.run()
        rounds = [r.round_num for r in result.rounds]
        assert rounds == [0, 1]

    def test_debate_result_has_consensus(self):
        debate = build_judge_mock_debate(
            topic="consensus test",
            k_rounds=2,
            verdict="reject",
            score=0.4,
            explanation="Rejected due to flaws",
        )
        result = debate.run()
        assert result.consensus is not None
        assert result.consensus.verdict == "reject"
        assert result.consensus.score == 0.4
        assert "flaws" in result.consensus.explanation

    def test_debate_result_has_judge_response(self):
        debate = build_judge_mock_debate(topic="test", k_rounds=1)
        result = debate.run()
        assert result.judge_response is not None
        assert isinstance(result.judge_response, LLMResponse)

    def test_debate_invalid_k_rounds_zero(self):
        with pytest.raises(ValueError, match="k_rounds must be at least 1"):
            Debate(topic="test", k_rounds=0)

    def test_debate_invalid_k_rounds_negative(self):
        with pytest.raises(ValueError, match="k_rounds must be at least 1"):
            Debate(topic="test", k_rounds=-5)

    def test_debate_uses_default_roles_when_none_provided(self):
        # Create a debate with default roles (no LLM) and minimal rounds
        debate = Debate(topic="defaults", k_rounds=1)
        # The placeholder LLMs will produce content
        result = debate.run()
        assert result.topic == "defaults"
        assert result.consensus is not None
        # Placeholder judge returns accept with score 0.5
        assert result.consensus.verdict == "accept"

    def test_debate_custom_roles(self):
        prop_llm = MockLLM(responses=["custom proposal"])
        crit_llm = MockLLM(responses=["custom critique"])
        judge_llm = MockLLM(
            responses=['{"verdict": "reject", "score": 0.1, "explanation": "bad"}']
        )
        debate = Debate(
            topic="custom roles",
            k_rounds=1,
            proposer=Proposer(llm=prop_llm),
            critic=Critic(llm=crit_llm),
            judge=Judge(llm=judge_llm),
        )
        result = debate.run()
        assert result.consensus.verdict == "reject"
        assert result.consensus.score == 0.1

    def test_debate_add_initial_context(self):
        debate = build_judge_mock_debate(topic="context test", k_rounds=1)
        initial_msg = Message(role="user", content="Some framing context", round_num=0)
        debate.add_initial_context(initial_msg)
        # The initial context should be in history before run
        assert len(debate.history) == 1
        result = debate.run()
        # After run: 1 (initial) + 2 (prop+crit) + 1 (judge) = 4
        assert len(result.final_history) == 4
        assert result.final_history[0].role == "user"
        assert result.final_history[0].content == "Some framing context"


class TestDebateResult:
    """Tests for the DebateResult dataclass."""

    def test_default_values(self):
        dr = DebateResult(topic="default")
        assert dr.topic == "default"
        assert dr.rounds == []
        assert dr.final_history == []
        assert dr.consensus is None
        assert dr.judge_response is None
        assert dr.total_rounds == 0

    def test_populated_result(self):
        dr = DebateResult(topic="test", total_rounds=5)
        dr.consensus = ConsensusScore(
            verdict="accept", score=0.9, explanation="done"
        )
        dr.total_rounds = 5
        assert dr.total_rounds == 5
        assert dr.consensus.score == 0.9


class TestFactoryFunctions:
    """Tests for build_mock_debate and build_judge_mock_debate."""

    def test_build_mock_debate_with_all_custom(self):
        debate = build_mock_debate(
            topic="factory test",
            k_rounds=2,
            proposer_responses=["p0", "p1"],
            critic_responses=["c0", "c1"],
            judge_response='{"verdict": "accept", "score": 0.8, "explanation": "ok"}',
        )
        result = debate.run()
        assert result.consensus.verdict == "accept"
        assert result.consensus.score == 0.8
        assert len(result.rounds) == 2

    def test_build_judge_mock_debate_reject(self):
        debate = build_judge_mock_debate(
            topic="reject test",
            k_rounds=1,
            verdict="reject",
            score=0.2,
        )
        result = debate.run()
        assert result.consensus.verdict == "reject"
        assert result.consensus.score == 0.2

    def test_build_judge_mock_debate_defaults(self):
        debate = build_judge_mock_debate(topic="defaults", k_rounds=1)
        result = debate.run()
        assert result.consensus.verdict == "accept"
        assert result.consensus.score == 0.8
        # Default proposer responses should produce non-empty content
        for msg in result.final_history:
            assert msg.content != ""

    def test_build_judge_mock_debate_custom_responses(self):
        debate = build_judge_mock_debate(
            topic="custom",
            k_rounds=2,
            proposer_responses=["Proposal A", "Proposal B"],
            critic_responses=["Critique A", "Critique B"],
        )
        result = debate.run()
        # Check the messages match the custom responses
        prop_msgs = [m for m in result.final_history if m.role == "proposer"]
        crit_msgs = [m for m in result.final_history if m.role == "critic"]
        assert prop_msgs[0].content == "Proposal A"
        assert prop_msgs[1].content == "Proposal B"
        assert crit_msgs[0].content == "Critique A"
        assert crit_msgs[1].content == "Critique B"
