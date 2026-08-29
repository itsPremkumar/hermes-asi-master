"""
agentforge-x: Six-agent fleet with versioned prompts, rubric judging,
and a thin kernel loop.

Agents:
- Researcher: Gathers and synthesizes information
- Coder: Writes and refines code
- Critic: Evaluates work against criteria
- Tester: Finds bugs and edge cases
- Writer: Produces documentation and prose
- Ops: Manages deployment and infrastructure

Each agent is a thin kernel loop: sense -> plan -> act -> critique -> repeat.
"""

from agentforge_x.agent import Agent, AgentState, AgentType, Plan, Action, Critique, PromptSet, JudgeResult
from agentforge_x.judge import Judge, RubricScore, Verdict, RubricCriterion
from agentforge_x.presets import Preset, load_presets, get_preset
from agentforge_x.mock import MockLLM, AgentMockLLM, JudgeMockLLM

__version__ = "1.0.0"
__all__ = [
    "Agent",
    "AgentState",
    "AgentType",
    "Plan",
    "Action",
    "Critique",
    "PromptSet",
    "JudgeResult",
    "Judge",
    "RubricScore",
    "Verdict",
    "RubricCriterion",
    "Preset",
    "load_presets",
    "get_preset",
    "MockLLM",
    "AgentMockLLM",
    "JudgeMockLLM",
]
