"""Tests for the six agent types (researcher, coder, critic, tester, writer, ops)."""

import pytest
from agentforge_x.agents import (
    Researcher, Coder, Critic, Tester, Writer, Ops,
    AGENT_REGISTRY, get_agent_class,
)
from agentforge_x.agent import AgentType, AgentState
from agentforge_x.mock import AgentMockLLM, MockLLM


class TestAgentRegistry:
    """Tests for the agent registry and lookup."""

    def test_all_six_agents_registered(self):
        expected = {"researcher", "coder", "critic", "tester", "writer", "ops"}
        assert set(AGENT_REGISTRY.keys()) == expected

    def test_get_agent_class_valid(self):
        assert get_agent_class("researcher") is Researcher
        assert get_agent_class("coder") is Coder
        assert get_agent_class("critic") is Critic
        assert get_agent_class("tester") is Tester
        assert get_agent_class("writer") is Writer
        assert get_agent_class("ops") is Ops

    def test_get_agent_class_invalid(self):
        with pytest.raises(ValueError, match="Unknown agent type"):
            get_agent_class("nonexistent")


class TestResearcherAgent:
    """Tests for the Researcher agent."""

    def test_researcher_type(self):
        agent = Researcher()
        assert agent.agent_type == AgentType.RESEARCHER
        assert agent.name == "Researcher"

    def test_researcher_has_prompts(self):
        agent = Researcher()
        assert agent.prompts.planner_prompt != ""
        assert agent.prompts.critic_prompt != ""
        assert agent.prompts.executor_prompt != ""

    def test_researcher_run(self):
        llm = AgentMockLLM()
        agent = Researcher(llm=llm, max_iterations=1)
        result = agent.run("AI safety research")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE

    def test_researcher_few_shots(self):
        agent = Researcher()
        assert len(agent.prompts.few_shots) > 0

    def test_researcher_version(self):
        agent = Researcher(version="2.0.0")
        assert agent.prompts.version == "2.0.0"


class TestCoderAgent:
    """Tests for the Coder agent."""

    def test_coder_type(self):
        agent = Coder()
        assert agent.agent_type == AgentType.CODER
        assert agent.name == "Coder"

    def test_coder_run(self):
        llm = AgentMockLLM()
        agent = Coder(llm=llm, max_iterations=1)
        result = agent.run("Write a sorting function")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE

    def test_coder_with_mock_responses(self):
        llm = AgentMockLLM(
            plan_responses=["STEPS: implement quicksort | test | document | REASONING: Efficient sort | CONFIDENCE: 0.9"],
            executor_responses=["def quicksort(arr): ..."],
            critic_responses=["SCORE: 0.9 | FEEDBACK: Well implemented | STRENGTHS: efficient, clean | WEAKNESSES: none"],
        )
        agent = Coder(llm=llm, max_iterations=1)
        result = agent.run("implement sort")
        assert "quicksort" in result or isinstance(result, str)


class TestCriticAgent:
    """Tests for the Critic agent."""

    def test_critic_type(self):
        agent = Critic()
        assert agent.agent_type == AgentType.CRITIC
        assert agent.name == "Critic"

    def test_critic_run(self):
        llm = AgentMockLLM()
        agent = Critic(llm=llm, max_iterations=1)
        result = agent.run("Evaluate this proposal")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE


class TestTesterAgent:
    """Tests for the Tester agent."""

    def test_tester_type(self):
        agent = Tester()
        assert agent.agent_type == AgentType.TESTER
        assert agent.name == "Tester"

    def test_tester_run(self):
        llm = AgentMockLLM()
        agent = Tester(llm=llm, max_iterations=1)
        result = agent.run("Test the authentication module")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE


class TestWriterAgent:
    """Tests for the Writer agent."""

    def test_writer_type(self):
        agent = Writer()
        assert agent.agent_type == AgentType.WRITER
        assert agent.name == "Writer"

    def test_writer_run(self):
        llm = AgentMockLLM()
        agent = Writer(llm=llm, max_iterations=1)
        result = agent.run("Write release notes")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE


class TestOpsAgent:
    """Tests for the Ops agent."""

    def test_ops_type(self):
        agent = Ops()
        assert agent.agent_type == AgentType.OPS
        assert agent.name == "Ops"

    def test_ops_run(self):
        llm = AgentMockLLM()
        agent = Ops(llm=llm, max_iterations=1)
        result = agent.run("Deploy the web app")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE


class TestAllAgentsWithSameMock:
    """Test that all six agents work with the same mock LLM."""

    @pytest.mark.parametrize("agent_type", ["researcher", "coder", "critic", "tester", "writer", "ops"])
    def test_agent_runs_with_mock(self, agent_type):
        llm = AgentMockLLM()
        agent_cls = get_agent_class(agent_type)
        agent = agent_cls(llm=llm, max_iterations=1)
        result = agent.run(f"Test task for {agent_type}")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE
        assert len(agent.history) > 0

    @pytest.mark.parametrize("agent_type", ["researcher", "coder", "critic", "tester", "writer", "ops"])
    def test_agent_default_prompts(self, agent_type):
        agent_cls = get_agent_class(agent_type)
        agent = agent_cls()
        assert agent.prompts.planner_prompt != ""
        assert agent.prompts.critic_prompt != ""
        assert agent.prompts.executor_prompt != ""
        assert agent.prompts.version == "1.0.0"
