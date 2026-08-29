"""Tests for the Judge module (rubric-based evaluation)."""

import pytest
import json
from agentforge_x.judge import Judge, Verdict, RubricCriterion, RubricScore
from agentforge_x.mock import MockLLM, JudgeMockLLM


class TestVerdict:
    """Tests for Verdict parsing and serialization."""

    def test_verdict_from_json_str(self):
        json_str = '{"verdict": "accept", "score": 0.85, "explanation": "Good work", "evidence": ["quote1"]}'
        verdict = Verdict.from_json_str(json_str)
        assert verdict.verdict == "accept"
        assert verdict.score == 0.85
        assert verdict.explanation == "Good work"
        assert verdict.evidence == ["quote1"]

    def test_verdict_to_json_str(self):
        verdict = Verdict(verdict="reject", score=0.3, explanation="Poor", evidence=["bad quote"])
        json_str = verdict.to_json_str()
        data = json.loads(json_str)
        assert data["verdict"] == "reject"
        assert data["score"] == 0.3

    def test_verdict_to_consensus_score(self):
        """Test conversion to debate-room ConsensusScore format."""
        verdict = Verdict(verdict="accept", score=0.9, explanation="Excellent")
        consensus = verdict.to_consensus_score()
        assert consensus.verdict == "accept"
        assert consensus.score == 0.9
        assert consensus.explanation == "Excellent"

    def test_verdict_with_empty_evidence(self):
        json_str = '{"verdict": "reject", "score": 0.2, "explanation": "Bad"}'
        verdict = Verdict.from_json_str(json_str)
        assert verdict.evidence == []

    def test_verdict_with_multiple_evidence(self):
        json_str = '{"verdict": "accept", "score": 0.8, "explanation": "Good", "evidence": ["q1", "q2", "q3"]}'
        verdict = Verdict.from_json_str(json_str)
        assert len(verdict.evidence) == 3


class TestJudge:
    """Tests for the Judge class."""

    def test_judge_default_criteria(self):
        judge = Judge()
        assert len(judge.criteria) == 4
        assert judge.criteria[0].name == "correctness"
        assert judge.criteria[1].name == "clarity"
        assert judge.criteria[2].name == "completeness"
        assert judge.criteria[3].name == "quality"

    def test_judge_custom_criteria(self):
        criteria = [
            RubricCriterion(name="accuracy", description="Is it accurate?", weight=0.5),
            RubricCriterion(name="speed", description="Is it fast?", weight=0.5),
        ]
        judge = Judge(criteria=criteria)
        assert len(judge.criteria) == 2
        assert judge.criteria[0].name == "accuracy"

    def test_judge_default_threshold(self):
        judge = Judge()
        assert judge.score_threshold == 0.7

    def test_judge_custom_threshold(self):
        judge = Judge(score_threshold=0.85)
        assert judge.score_threshold == 0.85

    def test_judge_evaluate_with_mock(self):
        llm = JudgeMockLLM(verdict="accept", score=0.9, explanation="Well done", evidence=["good point"])
        judge = Judge(llm=llm)
        verdict = judge.evaluate("Some work output", context="Some context")
        assert verdict.verdict == "accept"
        assert verdict.score == 0.9
        assert verdict.explanation == "Well done"
        assert verdict.evidence == ["good point"]

    def test_judge_evaluate_without_llm(self):
        judge = Judge()
        verdict = judge.evaluate("work")
        assert verdict.verdict == "accept"
        assert verdict.score == 0.5
        assert "Placeholder" in verdict.explanation

    def test_judge_evaluate_with_critique(self):
        from agentforge_x.agent import JudgeResult
        judge = Judge(score_threshold=0.7)
        critique = JudgeResult(score=0.85, feedback="Great work", strengths=["clear"], weaknesses=["minor"])
        verdict = judge.evaluate_with_critique(critique)
        assert verdict.verdict == "accept"
        assert verdict.score == 0.85

    def test_judge_evaluate_with_critique_below_threshold(self):
        from agentforge_x.agent import JudgeResult
        judge = Judge(score_threshold=0.7)
        critique = JudgeResult(score=0.5, feedback="Needs work", strengths=[], weaknesses=["unclear"])
        verdict = judge.evaluate_with_critique(critique)
        assert verdict.verdict == "reject"
        assert verdict.score == 0.5

    def test_judge_build_prompt_includes_criteria(self):
        judge = Judge()
        prompt = judge._build_prompt("work output", "context")
        assert "correctness" in prompt
        assert "clarity" in prompt
        assert "completeness" in prompt
        assert "quality" in prompt

    def test_judge_build_prompt_includes_work_and_context(self):
        judge = Judge()
        prompt = judge._build_prompt("my work output", "my context")
        assert "my work output" in prompt
        assert "my context" in prompt


class TestRubricScore:
    """Tests for RubricScore."""

    def test_rubric_score_fields(self):
        score = RubricScore(
            criterion_scores={"accuracy": 0.9, "speed": 0.7},
            overall_score=0.8,
            verdict="accept",
            feedback="Good",
            evidence=["quote"],
        )
        assert score.criterion_scores["accuracy"] == 0.9
        assert score.overall_score == 0.8
        assert score.verdict == "accept"

    def test_rubric_score_with_empty_criteria(self):
        score = RubricScore(
            criterion_scores={},
            overall_score=0.5,
            verdict="reject",
            feedback="Bad",
        )
        assert score.criterion_scores == {}
        assert score.evidence == []


class TestJudgeIntegration:
    """Integration tests for Judge with agent outputs."""

    def test_judge_accepts_high_quality_work(self):
        llm = JudgeMockLLM(verdict="accept", score=0.95, explanation="Excellent", evidence=["well-structured", "thorough"])
        judge = Judge(llm=llm)
        verdict = judge.evaluate("High quality output", context="Task: write documentation")
        assert verdict.verdict == "accept"
        assert verdict.score >= 0.7

    def test_judge_rejects_low_quality_work(self):
        llm = JudgeMockLLM(verdict="reject", score=0.3, explanation="Poor quality", evidence=["incomplete", "unclear"])
        judge = Judge(llm=llm)
        verdict = judge.evaluate("Low quality output", context="Task: write documentation")
        assert verdict.verdict == "reject"
        assert verdict.score < 0.7

    def test_judge_evaluates_multiple_criteria(self):
        """Test that judge correctly evaluates work against multiple criteria."""
        judge = Judge()
        prompt = judge._build_prompt("Code that implements quicksort", context="Write a sorting function")
        # Verify all criteria are in the prompt
        for criterion in judge.criteria:
            assert criterion.name in prompt
