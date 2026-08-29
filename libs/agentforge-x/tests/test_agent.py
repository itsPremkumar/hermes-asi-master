"""Tests for the core Agent kernel loop."""

import pytest
from agentforge_x.agent import (
    Agent, AgentState, AgentType, Plan, Action, Critique, PromptSet, JudgeResult,
)
from agentforge_x.mock import MockLLM, AgentMockLLM, JudgeMockLLM


class TestAgentKernelLoop:
    """Tests for the sense -> plan -> act -> critique loop."""

    def test_agent_initial_state(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        assert agent.state == AgentState.IDLE
        assert agent.history == []
        assert agent.name == "coder"

    def test_sense_produces_observation(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        obs = agent.sense("test input")
        assert obs["input"] == "test input"
        assert obs["iteration"] == 0
        assert agent.state == AgentState.SENSING

    def test_plan_produces_plan(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        obs = agent.sense("test")
        plan = agent.plan(obs)
        assert isinstance(plan, Plan)
        assert len(plan.steps) > 0
        assert 0 <= plan.confidence <= 1

    def test_act_produces_action(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        plan = Plan(steps=["step1"], reasoning="test", confidence=0.8)
        action = agent.act(plan)
        assert isinstance(action, Action)
        assert action.tool == "executor"

    def test_critique_produces_judge_result(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        action = Action(tool="executor", args={"step": "s"}, result="done")
        critique = agent.critique(action)
        assert isinstance(critique, JudgeResult)
        assert 0 <= critique.score <= 1

    def test_run_completes_full_loop(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts, max_iterations=2)
        result = agent.run("test task")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE
        assert len(agent.history) > 0

    def test_run_with_mock_llm(self):
        llm = AgentMockLLM()
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts, llm=llm, max_iterations=1)
        result = agent.run("test task")
        assert isinstance(result, str)
        assert agent.state == AgentState.DONE
        assert llm.call_count > 0

    def test_max_iterations_respected(self):
        llm = AgentMockLLM()
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts, llm=llm, max_iterations=5)
        agent.run("test")
        # Should not exceed max_iterations
        assert agent.iteration_count <= 5

    def test_history_grows_with_each_step(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts, max_iterations=1)
        agent.run("test")
        # Each iteration: sense + plan + act + critique = 4 history entries
        assert len(agent.history) == 4

    def test_final_result_property(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts, max_iterations=1)
        agent.run("test")
        assert agent.final_result != ""


class TestPlanParsing:
    """Tests for the plan parsing logic."""

    def test_parse_structured_plan(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        response = "STEPS: step1 | step2 | step3 | REASONING: Good approach | CONFIDENCE: 0.9"
        plan = agent._parse_plan(response)
        assert plan.steps == ["step1", "step2", "step3"]
        assert plan.reasoning == "Good approach"
        assert plan.confidence == 0.9

    def test_parse_plan_with_extra_whitespace(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        response = "STEPS:  step1  |  step2  | REASONING:  Some reasoning  | CONFIDENCE: 0.7"
        plan = agent._parse_plan(response)
        assert plan.steps == ["step1", "step2"]
        assert plan.reasoning == "Some reasoning"
        assert plan.confidence == 0.7

    def test_parse_plan_fallback(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        response = "Just a plain text response without structure"
        plan = agent._parse_plan(response)
        assert len(plan.steps) == 1
        assert plan.steps[0] == response
        assert plan.confidence == 0.5


class TestCritiqueParsing:
    """Tests for the critique parsing logic."""

    def test_parse_structured_critique(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        response = "SCORE: 0.85 | FEEDBACK: Great work | STRENGTHS: clear, thorough | WEAKNESSES: minor"
        critique = agent._parse_critique(response)
        assert critique.score == 0.85
        assert critique.feedback == "Great work"
        assert "clear" in critique.strengths
        assert "minor" in critique.weaknesses

    def test_parse_critique_fallback(self):
        prompts = PromptSet(
            planner_prompt="Plan: {input}",
            critic_prompt="Critique: {action}",
            executor_prompt="Execute: {step}",
        )
        agent = Agent(agent_type=AgentType.CODER, prompts=prompts)
        response = "Just some feedback text"
        critique = agent._parse_critique(response)
        assert critique.score == 0.5
        assert critique.feedback == response
