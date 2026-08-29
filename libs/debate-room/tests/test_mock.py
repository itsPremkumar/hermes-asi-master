"""Tests for the MockLLM class."""

import pytest
from debate_room.mock import MockLLM, JudgeMockLLM, ProposerMockLLM, CriticMockLLM, LLMMetrics


class TestMockLLM:
    """Tests for the core MockLLM behavior."""

    def test_sequential_responses(self):
        llm = MockLLM(responses=["a", "b", "c"])
        assert llm("p1") == "a"
        assert llm("p2") == "b"
        assert llm("p3") == "c"

    def test_cycling_when_exhausted(self):
        llm = MockLLM(responses=["x", "y"])
        assert llm("p1") == "x"
        assert llm("p2") == "y"
        # Past responses — should return empty string (cycling not supported)
        assert llm("p3") == ""

    def test_empty_responses_returns_empty(self):
        llm = MockLLM()
        assert llm("anything") == ""

    def test_func_mode(self):
        llm = MockLLM(func=lambda p: f"echo:{p}")
        assert llm("hello") == "echo:hello"
        assert llm("world") == "echo:world"

    def test_func_overrides_responses(self):
        """If func is provided, it should be used even if responses also given."""
        llm = MockLLM(func=lambda p: "func-result")
        assert llm("p") == "func-result"

    def test_cannot_specify_both_responses_and_func(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            MockLLM(responses=["a"], func=lambda p: "b")

    def test_cannot_specify_both_responses_and_callable(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            MockLLM(responses=["a"], callable_fn=lambda p: "b")

    def test_cannot_specify_both_func_and_callable(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            MockLLM(func=lambda p: "a", callable_fn=lambda p: "b")

    def test_raise_on_call(self):
        llm = MockLLM(raise_on_call=RuntimeError("simulated failure"))
        with pytest.raises(RuntimeError, match="simulated failure"):
            llm("prompt")

    def test_call_count_tracking(self):
        llm = MockLLM(responses=["a", "b"])
        llm("p1")
        llm("p2")
        llm("p3")
        assert llm.call_count == 3

    def test_prompts_seen_tracking(self):
        llm = MockLLM(responses=["a"])
        llm("prompt1")
        llm("prompt2")
        assert len(llm.prompts_seen) == 2
        assert "prompt1" in llm.prompts_seen[0]
        assert "prompt2" in llm.prompts_seen[1]

    def test_reset_clears_state(self):
        llm = MockLLM(responses=["a", "b", "c"])
        llm("p1")
        llm("p2")
        assert llm.call_count == 2
        llm.reset()
        assert llm.call_count == 0
        assert len(llm.prompts_seen) == 0
        # Index should be reset so responses work again
        assert llm("p1") == "a"


class TestSpecializedMocks:
    """Tests for the specialized mock LLMs."""

    def test_judge_mock_returns_valid_json(self):
        llm = JudgeMockLLM(verdict="reject", score=0.3, explanation="Too flawed")
        result = llm("prompt")
        import json
        data = json.loads(result)
        assert data["verdict"] == "reject"
        assert data["score"] == 0.3
        assert data["explanation"] == "Too flawed"

    def test_judge_mock_default_accept(self):
        llm = JudgeMockLLM()
        result = llm("prompt")
        import json
        data = json.loads(result)
        assert data["verdict"] == "accept"

    def test_proposer_mock_default_responses(self):
        llm = ProposerMockLLM()
        r1 = llm("p1")
        r2 = llm("p2")
        r3 = llm("p3")
        assert r1 != ""
        assert r2 != ""
        assert r3 != ""

    def test_proposer_mock_custom_responses(self):
        llm = ProposerMockLLM(
            proposals=["Custom proposal 1", "Custom proposal 2"]
        )
        assert llm("p1") == "Custom proposal 1"
        assert llm("p2") == "Custom proposal 2"

    def test_critic_mock_default_responses(self):
        llm = CriticMockLLM()
        r1 = llm("p1")
        r2 = llm("p2")
        assert r1 != ""
        assert r2 != ""

    def test_critic_mock_custom_responses(self):
        llm = CriticMockLLM(critiques=["Critique A", "Critique B"])
        assert llm("p1") == "Critique A"
        assert llm("p2") == "Critique B"
