"""Tests for the SelfEvaluator module."""

import pytest
from phase7.self_eval import SelfEvaluator, EvaluationResult, RubricCriterion


class TestEvaluationResult:
    """Tests for the EvaluationResult dataclass."""

    def test_evaluation_result_fields(self):
        result = EvaluationResult(
            score=0.85,
            verdict="pass",
            feedback="Good work",
            strengths=["clear", "thorough"],
            weaknesses=["minor detail missing"],
            suggestions=["add more examples"],
        )
        assert result.score == 0.85
        assert result.verdict == "pass"
        assert result.feedback == "Good work"
        assert len(result.strengths) == 2
        assert len(result.weaknesses) == 1
        assert len(result.suggestions) == 1

    def test_evaluation_result_to_dict(self):
        result = EvaluationResult(
            score=0.9,
            verdict="pass",
            feedback="Excellent",
            strengths=["s1"],
            weaknesses=["w1"],
            suggestions=["su1"],
        )
        d = result.to_dict()
        assert d["score"] == 0.9
        assert d["verdict"] == "pass"
        assert d["strengths"] == ["s1"]

    def test_evaluation_result_with_metadata(self):
        result = EvaluationResult(
            score=0.5,
            verdict="fail",
            feedback="Needs work",
            strengths=[],
            weaknesses=[],
            suggestions=[],
            metadata={"task_id": "123"},
        )
        assert result.metadata["task_id"] == "123"


class TestSelfEvaluator:
    """Tests for the SelfEvaluator class."""

    def test_default_criteria(self):
        evaluator = SelfEvaluator()
        assert len(evaluator.criteria) == 5
        assert evaluator.criteria[0].name == "correctness"
        assert evaluator.criteria[1].name == "completeness"

    def test_custom_criteria(self):
        criteria = [
            RubricCriterion(name="accuracy", description="Is it accurate?", weight=0.5),
            RubricCriterion(name="speed", description="Is it fast?", weight=0.5),
        ]
        evaluator = SelfEvaluator(criteria=criteria)
        assert len(evaluator.criteria) == 2
        assert evaluator.criteria[0].name == "accuracy"

    def test_default_pass_threshold(self):
        evaluator = SelfEvaluator()
        assert evaluator.pass_threshold == 0.7

    def test_custom_pass_threshold(self):
        evaluator = SelfEvaluator(pass_threshold=0.8)
        assert evaluator.pass_threshold == 0.8

    def test_evaluate_deterministic_short_output(self):
        evaluator = SelfEvaluator()
        result = evaluator.evaluate("short", "task")
        assert isinstance(result, EvaluationResult)
        assert 0 <= result.score <= 1
        assert result.verdict in ["pass", "fail"]

    def test_evaluate_deterministic_long_output(self):
        evaluator = SelfEvaluator()
        long_output = "A" * 200
        result = evaluator.evaluate(long_output, "task")
        assert result.score > 0.4  # Longer output should score higher

    def test_evaluate_deterministic_structured_output(self):
        evaluator = SelfEvaluator()
        structured_output = "- Point 1\n- Point 2\n- Point 3"
        result = evaluator.evaluate(structured_output, "task")
        assert result.score > 0.5  # Structured output should score higher

    def test_evaluate_deterministic_with_code(self):
        evaluator = SelfEvaluator()
        code_output = "Here is the code:\n```python\ndef foo(): pass\n```"
        result = evaluator.evaluate(code_output, "task")
        assert result.score > 0.5  # Code blocks should boost score

    def test_evaluate_deterministic_relevant_output(self):
        evaluator = SelfEvaluator()
        relevant_output = "The research shows that machine learning algorithms improve with more data"
        result = evaluator.evaluate(relevant_output, "research machine learning algorithms")
        assert result.score > 0.5  # Relevant output should score higher

    def test_evaluate_deterministic_irrelevant_output(self):
        evaluator = SelfEvaluator()
        irrelevant_output = "The weather is nice today and I like pizza"
        result = evaluator.evaluate(irrelevant_output, "research quantum computing")
        assert result.score < 0.6  # Irrelevant output should score lower

    def test_evaluate_with_llm(self):
        """Test evaluation with a mock LLM."""
        import json
        llm = lambda p: json.dumps({
            "score": 0.9,
            "verdict": "pass",
            "feedback": "Excellent work",
            "strengths": ["clear", "thorough"],
            "weaknesses": ["minor"],
            "suggestions": ["add examples"],
        })
        evaluator = SelfEvaluator(llm=llm)
        result = evaluator.evaluate("output", "task")
        assert result.score == 0.9
        assert result.verdict == "pass"
        assert result.feedback == "Excellent work"
        assert "clear" in result.strengths

    def test_evaluate_with_llm_invalid_json(self):
        """Test evaluation when LLM returns invalid JSON."""
        llm = lambda p: "This is not JSON but has score 0.75 in it"
        evaluator = SelfEvaluator(llm=llm)
        result = evaluator.evaluate("output", "task")
        assert isinstance(result, EvaluationResult)
        assert 0 <= result.score <= 1

    def test_evaluate_pass_verdict(self):
        """Test that score above threshold gives pass verdict."""
        evaluator = SelfEvaluator(pass_threshold=0.5)
        result = evaluator.evaluate("A" * 200, "task")
        if result.score >= 0.5:
            assert result.verdict == "pass"

    def test_evaluate_fail_verdict(self):
        """Test that score below threshold gives fail verdict."""
        evaluator = SelfEvaluator(pass_threshold=0.99)
        result = evaluator.evaluate("short", "task")
        assert result.verdict == "fail"

    def test_evaluate_includes_suggestions_for_low_scores(self):
        """Test that low-scoring evaluations include suggestions."""
        evaluator = SelfEvaluator()
        result = evaluator.evaluate("x", "task")
        if result.score < 0.7:
            assert len(result.suggestions) > 0
