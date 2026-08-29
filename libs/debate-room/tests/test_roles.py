"""Tests for Role classes: Proposer, Critic, Judge, BaseRole."""

import pytest
import json
from debate_room.roles import (
    Proposer, Critic, Judge, BaseRole,
    ProposerConfig, CriticConfig, JudgeConfig,
    Message, LLMResponse, RoleConfig,
)
from debate_room.mock import MockLLM


class TestBaseRole:
    """Tests for the abstract BaseRole class and its mechanics."""

    def test_base_role_is_abstract(self):
        with pytest.raises(TypeError):
            BaseRole(RoleConfig(name="test", system_prompt="test"))

    def test_add_to_history(self):
        class DummyRole(BaseRole):
            def act(self, context, round_num):
                return LLMResponse(content="dummy")
        role = DummyRole(RoleConfig(name="dummy", system_prompt="test"))
        msg = Message(role="dummy", content="hello", round_num=1)
        role.add_to_history(msg)
        assert len(role.history) == 1
        assert role.history[0].content == "hello"

    def test_reset_history(self):
        class DummyRole(BaseRole):
            def act(self, context, round_num):
                return LLMResponse(content="dummy")
        role = DummyRole(RoleConfig(name="dummy", system_prompt="test"))
        role.add_to_history(Message(role="dummy", content="msg1", round_num=1))
        role.add_to_history(Message(role="dummy", content="msg2", round_num=2))
        assert len(role.history) == 2
        role.reset_history()
        assert len(role.history) == 0

    def test_name_property(self):
        class DummyRole(BaseRole):
            def act(self, context, round_num):
                return LLMResponse(content="dummy")
        role = DummyRole(RoleConfig(name="MyRole", system_prompt="test"))
        assert role.name == "MyRole"

    def test_empty_history_initially(self):
        class DummyRole(BaseRole):
            def act(self, context, round_num):
                return LLMResponse(content="dummy")
        role = DummyRole(RoleConfig(name="dummy", system_prompt="test"))
        assert role.history == []


class TestProposer:
    """Tests for the Proposer role."""

    def test_act_round_zero_no_context(self):
        llm = MockLLM(responses=["Initial proposal content"])
        prop = Proposer(llm=llm)
        resp = prop.act([], round_num=0)
        assert isinstance(resp, LLMResponse)
        assert "Initial proposal content" in resp.content
        assert len(prop.history) == 1

    def test_act_with_context(self):
        llm = MockLLM(responses=["Refined proposal"])
        prop = Proposer(llm=llm)
        history = [
            Message(role="proposer", content="Initial proposal", round_num=0),
            Message(role="critic", content="Critique here", round_num=0),
        ]
        resp = prop.act(history, round_num=1)
        assert "Refined proposal" in resp.content

    def test_act_without_llm_uses_placeholder(self):
        prop = Proposer()
        resp = prop.act([], round_num=0)
        assert "Proposer round 0" in resp.content
        assert "Placeholder" in resp.content

    def test_history_grows_on_each_act(self):
        llm = MockLLM(responses=["r1", "r2", "r3"])
        prop = Proposer(llm=llm)
        prop.act([], 0)
        assert len(prop.history) == 1
        prop.act([Message(role="crit", content="x", round_num=0)], 1)
        assert len(prop.history) == 2
        prop.act([Message(role="crit", content="y", round_num=1)], 2)
        assert len(prop.history) == 3

    def test_default_config_values(self):
        prop = Proposer()
        assert prop.config.name == "Proposer"
        assert prop.config.temperature == 0.7
        assert prop.config.max_tokens == 512
        assert len(prop.config.system_prompt) > 0

    def test_custom_config(self):
        config = ProposerConfig(name="MyProp", temperature=0.5, max_tokens=256)
        prop = Proposer(config=config)
        assert prop.config.name == "MyProp"
        assert prop.config.temperature == 0.5
        assert prop.config.max_tokens == 256


class TestCritic:
    """Tests for the Critic role."""

    def test_act_with_context(self):
        llm = MockLLM(responses=["Critique of the proposal"])
        crit = Critic(llm=llm)
        history = [
            Message(role="proposer", content="Proposal text", round_num=0),
        ]
        resp = crit.act(history, round_num=0)
        assert "Critique" in resp.content

    def test_act_without_context_waits(self):
        crit = Critic()
        resp = crit.act([], round_num=0)
        assert "Waiting" in resp.content

    def test_act_without_llm_uses_placeholder(self):
        crit = Critic()
        resp = crit.act([Message(role="p", content="x", round_num=0)], 1)
        assert "Critic round 1" in resp.content

    def test_default_config_values(self):
        crit = Critic()
        assert crit.config.name == "Critic"
        assert crit.config.temperature == 0.7

    def test_custom_config(self):
        config = CriticConfig(name="MyCrit", temperature=0.9)
        crit = Critic(config=config)
        assert crit.config.name == "MyCrit"
        assert crit.config.temperature == 0.9


class TestJudge:
    """Tests for the Judge role."""

    def test_act_returns_json_verdict(self):
        judge_json = '{"verdict": "accept", "score": 0.9, "explanation": "Well argued"}'
        llm = MockLLM(responses=[judge_json])
        judge = Judge(llm=llm)
        history = [
            Message(role="proposer", content="Final proposal", round_num=2),
            Message(role="critic", content="Critique", round_num=2),
        ]
        resp = judge.act(history, round_num=3)
        data = json.loads(resp.content)
        assert data["verdict"] == "accept"
        assert data["score"] == 0.9
        assert data["explanation"] == "Well argued"

    def test_act_without_llm_uses_placeholder(self):
        judge = Judge()
        resp = judge.act([Message(role="p", content="x", round_num=0)], 1)
        data = json.loads(resp.content)
        assert data["verdict"] == "accept"
        assert data["score"] == 0.5

    def test_default_config_values(self):
        judge = Judge()
        assert judge.config.name == "Judge"
        assert judge.config.temperature == 0.3
        assert judge.config.max_tokens == 256

    def test_judge_includes_all_history(self):
        llm = MockLLM(responses=['{"verdict": "reject", "score": 0.2, "explanation": "no"}'])
        judge = Judge(llm=llm)
        history = [
            Message(role="proposer", content="round 0 prop", round_num=0),
            Message(role="critic", content="round 0 crit", round_num=0),
            Message(role="proposer", content="round 1 prop", round_num=1),
            Message(role="critic", content="round 1 crit", round_num=1),
        ]
        resp = judge.act(history, round_num=2)
        # The prompt sent to LLM should contain all messages
        prompt = llm.prompts_seen[-1]
        assert "round 0 prop" in prompt
        assert "round 0 crit" in prompt
        assert "round 1 prop" in prompt
        assert "round 1 crit" in prompt
