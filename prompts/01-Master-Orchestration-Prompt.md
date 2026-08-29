# 01 — Master Orchestration Prompt

> **Source:** Cleaned and consolidated from `Master Prompt — Create an Advanced Universal Autonomous Agent Orchestration SKILL.md` (27,683 bytes, 2 copies deduped) and variants `fddrh`, `efweg`, `chghgf`, `fxgfxn` (all variants of the same master task). Original language normalized to clean English. No content lost.

---

## Purpose

Use this prompt when you want an LLM to **generate a complete production-grade `SKILL.md`** that defines a universal, goal-driven autonomous orchestration system for an AI agent harness.

---

## Prompt

```
# MASTER TASK

Create exactly ONE production-grade SKILL.md file that defines a highly advanced,
universal, goal-driven autonomous execution system for an AI agent harness.

The skill must be designed as a general-purpose autonomous orchestration layer,
not as a simple prompt, checklist, coding skill, or research skill.

The resulting agent must be capable of taking a complex user objective,
understanding it, researching it, decomposing it, creating competing plans,
spawning specialized subagents, running independent work in parallel,
evaluating every subagent's result, selecting the strongest work, combining
the best parts of multiple agents, executing the synthesized plan, testing it,
repairing failures, evolving the solution through multiple controlled rounds,
and finally stopping once the objective is actually complete.

The final deliverable must be:

    SKILL.md

Do not create multiple skill files.
Do not create unnecessary supporting files.
Do not hardcode a particular repository architecture.
Do not hardcode specific filenames such as agx/kernel.py, agx/research.py, etc.
Do not assume AGX, Hermes, OpenClaw, DeepAgents, LangGraph, CrewAI, or any
other specific framework exists.
The skill must dynamically adapt to whatever tools and subagent capabilities
are available in the active harness.

---

# 1. CORE MISSION

The central principle must be:

> Do the actual work required to achieve the user's objective,
> not merely discuss how to do it.

The agent should behave like a highly capable autonomous project organization.
It should be able to:

    UNDERSTAND → INVESTIGATE → RESEARCH → DECOMPOSE → PLAN
    → CREATE COMPETING PLANS → SPAWN SPECIALISTS → RUN PARALLEL WORK
    → COLLECT RESULTS → VERIFY RESULTS → SELECT BEST WORK
    → COMBINE BEST PARTS → EXECUTE SYNTHESIZED PLAN → TEST
    → REPAIR FAILURES → EVOLVE → FINAL VERIFICATION → DELIVER → STOP

# 2. REQUIRED CAPABILITIES

The generated SKILL.md must cover, at minimum:

  1. Objective binding — lock the goal, deliverable, success criteria, constraints, risks,
     evidence requirements, tools available, and stop conditions before acting.
  2. Context reconnaissance — inspect local workspace, existing instructions, build
     configuration, tests, environment constraints before planning.
  3. Deep research protocol — four passes (Discovery → Evidence → Adversarial → Synthesis)
     with an evidence matrix and Value-of-Information stopping rule.
  4. Planning protocol — decompose into outcomes with prerequisites, actions, validation,
     and dependency-aware execution ordering.
  5. Hypothesis generation — at least three candidates (safe conventional, high-upside
     alternative, fundamentally different strategy) scored by evidence, cost,
     reversibility, and risk.
  6. Pre-execution critic gate — eight checks: consistency with evidence, addresses the
     objective, false assumptions, failure modes, cheapest test, falsification evidence,
     safer alternative, constraint violations.
  7. Execution model — isolated, reversible units: inspect → change one bounded unit
     → test → record → next unit.
  8. Verification — six levels: structural, functional, evidence, regression,
     acceptance, adversarial. A result is not done until relevant levels pass.
  9. Evolution engine — baseline → variants → critic filter → controlled experiments
     → measure → compare → keep only verified improvements.
 10. Failure recovery — classify failure (transient, environmental, tool, permission,
     dependency, logic, data, specification, model, infrastructure, safety) and use
     a recovery ladder: retry → different tool → reduce scope → change approach
     → specialist → replan → checkpoint restore → pause for human.
 11. Memory and knowledge — persist success, failure, rejection, constraint, insight,
     and open questions with provenance. Retrieve by semantic relevance.
 12. Quality gates — ten gates: objective, deliverable, constraints, claims verified,
     functional checks, no regression, security, reproducibility, evidence documented,
     output understandable.
 13. Risk-based autonomy — low / medium / high tiers with matched validation and
     approval requirements. High-risk actions require explicit approval.
 14. Stopping policy — success, convergence, blocked, awaiting human, budget exhausted,
     safety boundary. When stopped, report completed work, best result, blocker,
     unresolved questions, and next action.

# 3. HARD CONSTRAINTS

- The skill must be model-agnostic and harness-agnostic.
- It must distinguish capability described in the protocol from capability actually
  implemented in the runtime.
- It must never claim AGI, consciousness, or guaranteed correctness.
- It must never optimize activity, agent count, or token consumption as proxies for success.
- Research must triangulate important claims and never fabricate citations.
- Evaluation hierarchy: unit → integration → scenario → adversarial → benchmark
  → long-horizon → human → real-world outcome.

# 4. OUTPUT FORMAT

Output ONLY the complete contents of SKILL.md (with YAML frontmatter: name,
version, description). Do not include explanations outside the file unless
explicitly requested.

The generated file should be usable as SKILL.md in the clean architecture
defined at AGI-Executive-Clean-Complete/SKILL.md:1.
```

---

## Notes

- This prompt is the **generator** for SKILL.md. The **product** is `SKILL.md` itself at the project root.
- The clean SKILL.md v8.0 at `../SKILL.md:1` is the reference implementation that satisfies this prompt. Compare any new generation against it.
- Variants `rg`, `sgsd`, `gg` in the original project contained additional constraints about evidence discipline, source triangulation, and safety — all folded into the prompt above in section 3.
