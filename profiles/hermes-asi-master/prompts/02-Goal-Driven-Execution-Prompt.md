# 02 — Goal-Driven Execution Prompt

> **Source:** Cleaned and consolidated from `Prompt — Create a High-Advanced Goal-Driven Autonomous Execution SKILL.md` (22,529 bytes, 2 copies deduped). Original language normalized to clean English. Variants with overlapping content already merged above.

---

## Purpose

Use this prompt when you want an LLM to generate a SKILL.md focused on **goal-driven autonomous execution** — finishing the job to the highest defensible quality, not merely answering.

---

## Prompt

```
# TASK: Create a Production-Grade Universal Autonomous Execution SKILL.md

You are an expert agent-harness architect, autonomous-agent researcher,
prompt engineer, workflow-orchestration engineer, and reliability engineer.

Your task is to create ONE complete, production-grade SKILL.md file for a
general-purpose autonomous AI agent.

The resulting skill must be significantly more advanced than a basic
"plan → execute" prompt.

It must allow an agent to take almost any legitimate user task, determine
what needs to be done, research what it does not know, create multiple plans,
delegate independent work to subagents, execute tools intelligently, verify
results, recover from failures, improve the result through controlled evolution,
and STOP immediately after the user's actual objective has been successfully
completed.

The final output must be ONLY the complete contents of SKILL.md
unless explicitly asked for an explanation.

---

# 1. PRIMARY OBJECTIVE

Design a universal autonomous execution skill whose central principle is:

> Complete the user's real objective with the highest defensible quality
> using the minimum necessary time, resources, and risk — then stop.

The skill must NOT optimize for:

- maximum number of agents
- maximum number of tool calls
- maximum research
- maximum iterations
- maximum token usage
- maximum complexity
- perpetual autonomy

It must optimize for:

    goal completion + correctness + evidence + verification + quality + safety + efficiency

Once the objective is satisfied and all required acceptance criteria pass:

    DELIVER → STOP

The agent must not continue generating unnecessary improvements after successful completion.

# 2. EXECUTION LIFECYCLE

    RECEIVE → UNDERSTAND → GOAL CONTRACT → RECON → COMPLEXITY ASSESSMENT
    → DECOMPOSE → DEPENDENCY GRAPH → RESEARCH → COMPETING PLANS
    → SPECIALIST DELEGATION → PARALLEL WORK → COLLECT → EVALUATE
    → BEST-COMPONENT SYNTHESIS → MASTER PLAN → CRITIC GATE
    → EXECUTE → VERIFY → RECOVER / REPLAN WHEN NEEDED → EVOLVE WHEN BENEFICIAL
    → FINAL VERIFICATION → ACCEPTANCE → DELIVER → STOP

The system is deliberately NOT a perpetual loop. Stopping is a first-class
capability and the correct outcome for every mission.

# 3. COMPLEXITY-AWARE ROUTING

Assess complexity before choosing the workflow:

- TRIVIAL — single action, known procedure, reversible → direct execution
- MODERATE — multiple steps, some unknowns → plan + execute + verify
- COMPLEX — research required, competing approaches, multi-agent → full loop
- EXPLORATORY — unknown environment, unclear objective → research → hypothesis → experiment → learn

Use the smallest sufficient architecture for reliability. Do not deploy
multi-agent orchestration when a single competent process suffices.

# 4. REQUIRED MECHANISMS

  a. Goal contract — machine-readable: GOAL, DELIVERABLE, SUCCESS_CRITERIA,
     CONSTRAINTS, RISKS, EVIDENCE_REQUIRED, TOOLS_AVAILABLE, STOP_CONDITIONS.
  b. Reconnaissance — inspect local context before planning; never modify files
     before understanding local conventions.
  c. Research — deep, multi-pass, evidence-backed, contradiction-aware.
  d. Decomposition — dependency graph (DAG), not arbitrary task ordering.
  e. Competing plans — at least three, scored by expected value and risk.
  f. Specialist delegation — typed roles, bounded budgets, termination conditions.
  g. Parallel work — isolated workspaces, independent traces, comparable evaluation.
  h. Best-component synthesis — combine the strongest parts of multiple agents,
     not blind concatenation.
  i. Critic gate — every non-trivial candidate passes adversarial review before execution.
  j. Verification — layered (structural → functional → evidence → regression
     → acceptance → adversarial). Relevant levels must pass.
  k. Recovery — diagnose → choose changed strategy → retry with different tool/approach.
  l. Evolution — baseline preserved; variants generated; only verified improvements kept.
  m. Memory — structured lessons (SUCCESS / FAILURE / REJECTION / CONSTRAINT /
     INSIGHT / OPEN_QUESTION) retrieved by semantic relevance.

# 5. ANTI-PATTERNS (must not occur)

- Answering immediately when research is necessary.
- Researching without connecting it to a decision.
- Generating plans that are never executed.
- Executing without verification.
- Trusting a single source for critical facts.
- Repeating identical failures.
- Continuing to iterate after convergence without expected benefit.
- Optimizing a metric that conflicts with the true objective.
- Silently changing the user's success criteria.
- Fabricating completion or evidence.

# 6. OUTPUT CONTRACT

The skill must define that every mission's final output clearly separates:

    RESULT        — what was completed
    VERIFIED      — what was tested and confirmed
    KEY EVIDENCE  — most important sources, measurements, or checks
    CHANGES       — what was modified or produced
    LIMITATIONS   — what remains uncertain
    NEXT STATE    — complete, converged, blocked, or awaiting approval

# 7. OUTPUT FORMAT

Output ONLY the complete contents of SKILL.md (with YAML frontmatter).
The generated file must be usable as SKILL.md at
AGI-Executive-Clean-Complete/SKILL.md:1.
```

---

## How This Prompt Differs from Prompt 01

| Prompt 01 (Master Orchestration) | Prompt 02 (Goal-Driven Execution) |
|----------------------------------|-----------------------------------|
| Emphasizes orchestration breadth — competing plans, parallel agents, synthesis | Emphasizes execution discipline — minimum necessary resources, then stop |
| Defines an organization (multiple agents as a project team) | Defines an individual executor that scales to a team when justified |
| Broader research and planning portfolio | Tighter complexity routing (trivial → exploratory) with anti-patterns |
| Output is SKILL.md covering `AGX Universal Taskmaster` scope | Output is SKILL.md covering goal completion with quality + efficiency |

Both prompts generate valid SKILL.md files. The v8.0 Clean SKILL.md at `../SKILL.md:1` satisfies both.
