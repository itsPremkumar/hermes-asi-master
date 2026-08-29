"""Edge case and integration tests for the debate framework."""

import pytest
import json
from debate_room.roles import Proposer, Critic, Judge, Message, LLMResponse
from debate_room.mock import MockLLM
from debate_room.debate import Debate, build_mock_debate, build_judge_mock_debate


class TestEdgeCaseScenarios:
    """Edge case tests for unusual scenarios."""

    def test_debate_with_very_long_proposals(self):
        """Test that the debate handles very long proposal text."""
        long_text = "A" * 10000
        debate = build_mock_debate(
            topic="long text test",
            k_rounds=1,
            proposer_responses=[long_text],
            critic_responses=["Short critique"],
            judge_response='{"verdict": "accept", "score": 0.5, "explanation": "ok"}',
        )
        result = debate.run()
        assert result.consensus is not None
        # The long text should appear in history
        prop_msgs = [m for m in result.final_history if m.role == "proposer"]
        assert prop_msgs[0].content == long_text

    def test_debate_with_empty_string_responses(self):
        """Test that the debate handles empty string LLM responses."""
        debate = build_mock_debate(
            topic="empty responses",
            k_rounds=1,
            proposer_responses=[""],
            critic_responses=[""],
            judge_response='{"verdict": "accept", "score": 0.5, "explanation": ""}',
        )
        result = debate.run()
        assert result.consensus.explanation == ""
        prop_msgs = [m for m in result.final_history if m.role == "proposer"]
        assert prop_msgs[0].content == ""

    def test_debate_with_unicode_content(self):
        """Test handling of unicode characters in responses."""
        unicode_text = "Proposal with unicode: 日本語 🧠 ελληνικά"
        debate = build_mock_debate(
            topic="unicode test",
            k_rounds=1,
            proposer_responses=[unicode_text],
            critic_responses=["Critique:  critique 批判"],
            judge_response='{"verdict": "accept", "score": 0.5, "explanation": "unicode-ok"}',
        )
        result = debate.run()
        prop_msgs = [m for m in result.final_history if m.role == "proposer"]
        assert prop_msgs[0].content == unicode_text

    def test_debate_with_special_json_characters_in_explanation(self):
        """Test that judge explanation with quotes and newlines is handled."""
        judge_json = json.dumps({
            "verdict": "accept",
            "score": 0.9,
            "explanation": 'Good "quote" and \\n newline',
        })
        debate = build_mock_debate(
            topic="json special chars",
            k_rounds=1,
            judge_response=judge_json,
        )
        result = debate.run()
        assert result.consensus.explanation == 'Good "quote" and \\n newline'

    def test_debate_with_score_zero(self):
        """Test edge case where judge gives score 0.0."""
        debate = build_judge_mock_debate(
            topic="zero score",
            k_rounds=1,
            verdict="reject",
            score=0.0,
        )
        result = debate.run()
        assert result.consensus.score == 0.0
        assert result.consensus.verdict == "reject"

    def test_debate_with_score_one(self):
        """Test edge case where judge gives score 1.0."""
        debate = build_judge_mock_debate(
            topic="perfect score",
            k_rounds=1,
            verdict="accept",
            score=1.0,
        )
        result = debate.run()
        assert result.consensus.score == 1.0
        assert result.consensus.verdict == "accept"

    def test_debate_proposer_sees_full_history(self):
        """Test that the proposer in round N sees all preceding messages."""
        received_prompts = []

        def track_prompts(prompt):
            received_prompts.append(prompt)
            return f"Response to prompt #{len(received_prompts)}"

        prop_llm = MockLLM(func=track_prompts)
        crit_llm = MockLLM(func=lambda p: "Critique response")
        judge_llm = MockLLM(
            func=lambda p: '{"verdict": "accept", "score": 0.5, "explanation": "fine"}'
        )

        debate = Debate(
            topic="history visibility",
            k_rounds=3,
            proposer=Proposer(llm=prop_llm),
            critic=Critic(llm=crit_llm),
            judge=Judge(llm=judge_llm),
        )
        result = debate.run()

        # Round 0 proposer prompt should NOT mention prior history (no history)
        assert "Debate History" not in received_prompts[0]

        # Round 1 proposer prompt should contain round 0 messages
        assert "r0" in received_prompts[1] or "R0" in received_prompts[1]

        # Round 2 proposer prompt should contain round 0 and round 1 messages
        assert "r0" in received_prompts[2] or "R0" in received_prompts[2]
        assert "r1" in received_prompts[2] or "R1" in received_prompts[2]

    def test_debate_judge_prompt_contains_all_rounds(self):
        """Test that the judge sees the complete debate history."""
        prop_llm = MockLLM(func=lambda p: "Proposal")
        crit_llm = MockLLM(func=lambda p: "Critique")
        judge_prompts = []
        judge_llm = MockLLM(
            func=lambda p: judge_prompts.append(p) or '{"verdict": "accept", "score": 0.5, "explanation": "ok"}'
        )

        debate = Debate(
            topic="judge sees all",
            k_rounds=3,
            proposer=Proposer(llm=prop_llm),
            critic=Critic(llm=crit_llm),
            judge=Judge(llm=judge_llm),
        )
        result = debate.run()

        judge_prompt = judge_prompts[-1]
        # The judge should see all messages
        assert "Proposal" in judge_prompt
        assert "Critique" in judge_prompt

    def test_multiple_debates_do_not_share_state(self):
        """Test that separate Debate instances don't share internal state."""
        prop_responses = ["A1", "A2", "A3"]
        debate1 = build_mock_debate(
            topic="debate1",
            k_rounds=2,
            proposer_responses=list(prop_responses),
            critic_responses=["B1", "B2"],
            judge_response='{"verdict": "accept", "score": 0.7, "explanation": "ok"}',
        )
        result1 = debate1.run()

        debate2 = build_mock_debate(
            topic="debate2",
            k_rounds=2,
            proposer_responses=list(prop_responses),
            critic_responses=["B1", "B2"],
            judge_response='{"verdict": "reject", "score": 0.3, "explanation": "no"}',
        )
        result2 = debate2.run()

        assert result1.consensus.verdict == "accept"
        assert result2.consensus.verdict == "reject"
        assert result1.topic != result2.topic
        # Proposer histories should be independent
        assert len(debate1.proposer.history) != 0
        assert len(debate2.proposer.history) != 0
        # They should not be the same object
        assert debate1.proposer is not debate2.proposer
