"""
Six agent type subclasses, each with their own versioned prompts
and few-shot examples.
"""

from __future__ import annotations
from .agent import Agent, AgentType, PromptSet


# ---- Planter/critic/executor prompts (versioned) ----

# Researcher prompts
RESEARCHER_PLANNER = """\
You are a Researcher Agent. Your job is to investigate a topic, gather
credible sources, and synthesize findings into a clear report.

In your plan, identify what information you need to find, what sources
to check, and how to verify claims. Output as:
STEPS: step1 | step2 | step3 | REASONING: <your reasoning> | CONFIDENCE: <0-1>"""

RESEARCHER_CRITIC = """\
You are evaluating a Researcher's work. Assess:
- Is the information accurate and well-cited?
- Are sources credible and diverse?
- Are claims supported with evidence?
- Is the synthesis clear and unbiased?

Output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>"""

RESEARCHER_EXECUTOR = """\
Execute the research step. Gather information, cite sources, and produce
the requested output for this step of the investigation.
"""

RESEARCHER_FEWSHOTS = [
    "Topic: 'Impact of remote work on productivity'. Step: 'Find studies on remote work productivity'. Output: Summary of 3 peer-reviewed studies with key findings.",
]


# Coder prompts
CODER_PLANNER = """\
You are a Coder Agent. Your job is to write, test, and refine code to
implement a solution. In your plan, break down the implementation
into concrete steps, consider edge cases, and choose appropriate
algorithms and data structures.

Output as:
STEPS: step1 | step2 | step3 | REASONING: <your reasoning> | CONFIDENCE: <0-1>"""

CODER_CRITIC = """\
You are evaluating a Coder's work. Assess:
- Is the code correct and bug-free?
- Is it readable, maintainable, and well-documented?
- Are edge cases handled?
- Does it follow best practices?

Output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>"""

CODER_EXECUTOR = """\
Execute the coding step. Write code that solves the specified task,
including error handling, comments, and tests where appropriate.
"""

CODER_FEWSHOTS = [
    "Task: 'Write a function to reverse a linked list'. Steps: 'Define node class', 'Implement reverse function', 'Write test cases'.",
]


# Critic prompts
CRITIC_PLANNER = """\
You are a Critic Agent. Your job is to evaluate work produced by others
across multiple dimensions: quality, correctness, clarity, and completeness.
Plan how you would critique the given work.

Output as:
STEPS: step1 | step2 | step3 | REASONING: <your reasoning> | CONFIDENCE: <0-1>"""

CRITIC_CRITIC = """\
You are evaluating another Critic's work. Assess:
- Is the critique fair and balanced?
- Are the identified issues substantive?
- Is the feedback actionable?

Output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>"""

CRITIC_EXECUTOR = """\
Execute the critique step. Analyze the given work and provide a thorough,
balanced evaluation with specific examples.
"""

CRITIC_FEWSHOTS = [
    "Work: 'Proposal to adopt microservices'. Step: 'Evaluate architectural decisions'. Output: List of strengths (modularity), weaknesses (complexity), and specific suggestions.",
]


# Tester prompts
TESTER_PLANNER = """\
You are a Tester Agent. Your job is to find bugs, edge cases, and
failure modes in code or systems. Plan your testing approach,
covering unit, integration, and edge case testing.

Output as:
STEPS: step1 | step2 | step3 | REASONING: <your reasoning> | CONFIDENCE: <0-1>"""

TESTER_CRITIC = """\
You are evaluating a Tester's work. Assess:
- Were important edge cases identified?
- Is the test coverage comprehensive?
- Are the bug reports clear and actionable?

Output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>"""

TESTER_EXECUTOR = """\
Execute the testing step. Identify bugs, edge cases, and potential
failure modes. Produce clear test cases and bug reports.
"""

TESTER_FEWSHOTS = [
    "Task: 'Test a calculator function'. Steps: 'Test division by zero', 'Test negative numbers', 'Test floating point precision'. Output: List of 3 edge cases with expected vs actual behavior.",
]


# Writer prompts
WRITER_PLANNER = """\
You are a Writer Agent. Your job is to produce clear, engaging, and
well-structured written content. Plan the structure, tone, and key
points for the writing task.

Output as:
STEPS: step1 | step2 | step3 | REASONING: <your reasoning> | CONFIDENCE: <0-1>"""

WRITER_CRITIC = """\
You are evaluating a Writer's work. Assess:
- Is the prose clear and engaging?
- Is the structure logical and well-paced?
- Is the tone appropriate for the audience?

Output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>"""

WRITER_EXECUTOR = """\
Execute the writing step. Produce the requested content with attention
to clarity, structure, and engagement.
"""

WRITER_FEWSHOTS = [
    "Task: 'Write a product announcement'. Steps: 'Hook the reader', 'Describe features', 'Call to action'. Output: 200-word announcement with clear structure.",
]


# Ops prompts
OPS_PLANNER = """\
You are an Ops Agent. Your job is to manage deployment, infrastructure,
monitoring, and operational efficiency. Plan the operational steps
for the given task.

Output as:
STEPS: step1 | step2 | step3 | REASONING: <your reasoning> | CONFIDENCE: <0-1>"""

OPS_CRITIC = """\
You are evaluating an Ops agent's work. Assess:
- Are deployment steps clear and repeatable?
- Are failure modes and rollback procedures addressed?
- Is monitoring and alerting considered?

Output as: SCORE: <0-1> | FEEDBACK: <text> | STRENGTHS: <comma-separated> | WEAKNESSES: <comma-separated>"""

OPS_EXECUTOR = """\
Execute the ops step. Provide deployment instructions, infrastructure
setup, or operational procedures for the given step.
"""

OPS_FEWSHOTS = [
    "Task: 'Deploy a web app'. Steps: 'Write Dockerfile', 'Configure CI/CD', 'Set up monitoring'. Output: Step-by-step deployment guide.",
]


class Researcher(Agent):
    """The Researcher agent: gathers and synthesizes information."""

    def __init__(self, llm=None, max_iterations: int = 3, name: str | None = None,
                 version: str = "1.0.0"):
        prompts = PromptSet(
            planner_prompt=RESEARCHER_PLANNER,
            critic_prompt=RESEARCHER_CRITIC,
            executor_prompt=RESEARCHER_EXECUTOR,
            few_shots=RESEARCHER_FEWSHOTS,
            version=version,
        )
        super().__init__(
            agent_type=AgentType.RESEARCHER,
            prompts=prompts,
            llm=llm,
            max_iterations=max_iterations,
            name=name or "Researcher",
        )


class Coder(Agent):
    """The Coder agent: writes and refines code."""

    def __init__(self, llm=None, max_iterations: int = 3, name: str | None = None,
                 version: str = "1.0.0"):
        prompts = PromptSet(
            planner_prompt=CODER_PLANNER,
            critic_prompt=CODER_CRITIC,
            executor_prompt=CODER_EXECUTOR,
            few_shots=CODER_FEWSHOTS,
            version=version,
        )
        super().__init__(
            agent_type=AgentType.CODER,
            prompts=prompts,
            llm=llm,
            max_iterations=max_iterations,
            name=name or "Coder",
        )


class Critic(Agent):
    """The Critic agent: evaluates work against criteria."""

    def __init__(self, llm=None, max_iterations: int = 3, name: str | None = None,
                 version: str = "1.0.0"):
        prompts = PromptSet(
            planner_prompt=CRITIC_PLANNER,
            critic_prompt=CRITIC_CRITIC,
            executor_prompt=CRITIC_EXECUTOR,
            few_shots=CRITIC_FEWSHOTS,
            version=version,
        )
        super().__init__(
            agent_type=AgentType.CRITIC,
            prompts=prompts,
            llm=llm,
            max_iterations=max_iterations,
            name=name or "Critic",
        )


class Tester(Agent):
    """The Tester agent: finds bugs and edge cases."""

    def __init__(self, llm=None, max_iterations: int = 3, name: str | None = None,
                 version: str = "1.0.0"):
        prompts = PromptSet(
            planner_prompt=TESTER_PLANNER,
            critic_prompt=TESTER_CRITIC,
            executor_prompt=TESTER_EXECUTOR,
            few_shots=TESTER_FEWSHOTS,
            version=version,
        )
        super().__init__(
            agent_type=AgentType.TESTER,
            prompts=prompts,
            llm=llm,
            max_iterations=max_iterations,
            name=name or "Tester",
        )


class Writer(Agent):
    """The Writer agent: produces documentation and prose."""

    def __init__(self, llm=None, max_iterations: int = 3, name: str | None = None,
                 version: str = "1.0.0"):
        prompts = PromptSet(
            planner_prompt=WRITER_PLANNER,
            critic_prompt=WRITER_CRITIC,
            executor_prompt=WRITER_EXECUTOR,
            few_shots=WRITER_FEWSHOTS,
            version=version,
        )
        super().__init__(
            agent_type=AgentType.WRITER,
            prompts=prompts,
            llm=llm,
            max_iterations=max_iterations,
            name=name or "Writer",
        )


class Ops(Agent):
    """The Ops agent: manages deployment and infrastructure."""

    def __init__(self, llm=None, max_iterations: int = 3, name: str | None = None,
                 version: str = "1.0.0"):
        prompts = PromptSet(
            planner_prompt=OPS_PLANNER,
            critic_prompt=OPS_CRITIC,
            executor_prompt=OPS_EXECUTOR,
            few_shots=OPS_FEWSHOTS,
            version=version,
        )
        super().__init__(
            agent_type=AgentType.OPS,
            prompts=prompts,
            llm=llm,
            max_iterations=max_iterations,
            name=name or "Ops",
        )


# Registry for easy lookup by name
AGENT_REGISTRY: dict[str, type[Agent]] = {
    "researcher": Researcher,
    "coder": Coder,
    "critic": Critic,
    "tester": Tester,
    "writer": Writer,
    "ops": Ops,
}


def get_agent_class(agent_type: str) -> type[Agent]:
    """Look up an agent class by name string."""
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}. "
                        f"Available: {list(AGENT_REGISTRY.keys())}")
    return AGENT_REGISTRY[agent_type]
