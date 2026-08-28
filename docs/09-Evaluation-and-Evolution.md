# 09 — Evaluation and Evolution

## Evaluation-First Architecture

Every serious capability requires an evaluator:

```
capability → task distribution → candidate → evaluator → metric → baseline → regression test
```

**Never optimize a system without measuring whether it improved.**

An evaluator tests the **actual acceptance criteria**, not merely reassuring signals.

---

## Evaluation Hierarchy

| Level | Type | What It Checks |
|-------|------|----------------|
| L1 | Unit tests | Does this component behave correctly in isolation? |
| L2 | Integration tests | Do components work together? |
| L3 | Scenario tests | Does the end-to-end workflow succeed on realistic inputs? |
| L4 | Adversarial tests | Does it survive edge cases, contradictory inputs, injection attempts? |
| L5 | Benchmark tests | How does it compare to standardized external suites? |
| L6 | Long-horizon tests | Does it remain coherent across hours or days of autonomous operation? |
| L7 | Human evaluation | Does the result satisfy the human's intended outcome? |
| L8 | Real-world outcome | Did the verified state change actually occur in the environment? |

Always use the **lowest level that provides adequate signal**. Do not skip L1–L3 and rely only on L5.

---

## Benchmark Portfolio

Depending on capability, use or adapt:

| Benchmark | Domain |
|-----------|--------|
| SWE-bench / SWE-bench Verified | Software engineering |
| OSWorld | Computer-use and desktop interaction |
| WebArena / WebVoyager | Web navigation |
| AgentBench | General agent capabilities |
| AgentDojo | Prompt injection and tool-use security |
| ToolSandbox | Tool-calling correctness |
| GAIA | General AI assistant reasoning |
| BrowseComp-like research evaluations | Research quality |
| Domain-specific benchmarks | Your mission domain |
| Custom task suites | Your harness and tools |

The best benchmark is one that **correlates with your real mission outcomes**. A high score from a broken evaluator is not evidence of success.

---

## Quality Gates (Minimum Ten)

```
G1: Objective satisfied?
G2: Required deliverable produced?
G3: Constraints respected?
G4: Important claims verified?
G5: Functional / structural checks passed?
G6: No known critical regression?
G7: Security / privacy constraints respected?
G8: Result reproducible or explainable?
G9: Evidence and limitations documented?
G10: Final output understandable to the user?
```

Candidate promotion requires:

```
improvement AND reproducibility AND no critical regression
AND budget compliance AND policy compliance
```

High-impact changes additionally require: isolated testing, rollback capability, staged rollout, monitoring, and independent review.

---

## Continuous Evaluation

Maintain a benchmark suite for the actual agent. Evaluate:

```
task success, factual accuracy, tool correctness, planning quality, recovery rate,
verification quality, calibration, memory retrieval, transfer, cost efficiency,
latency, safety compliance
```

Run: `new benchmark + old benchmark + failure regression suite + safety suite`. Do not optimize a new benchmark while degrading general reliability.

### Capability Matrix

Maintain a live capability matrix:

```yaml
capability:
  task_family: ""
  performance: 0.0
  confidence_interval: []
  evidence: []
  last_tested: ""
  failure_modes: []
  best_model: ""
  best_strategy: ""
```

This becomes the agent's empirical self-knowledge.

### Generality Evaluation

Evaluate across: familiar tasks, unfamiliar tasks, transfer tasks, adversarial tasks, long-horizon tasks, changing environments, tool-rich, tool-poor, hidden-rule, recovery-required, collaboration-required tasks.

Measure: `breadth, depth, tail performance, transfer, robustness, sample efficiency, adaptation speed, autonomy, cost, failure severity`. AGI-like progress is not reducible to a single benchmark number.

---

## Evolution

### Candidate Evolution (AlphaEvolve / AVO Pattern)

For testable candidates:

```
baseline → inspect → form improvement hypothesis → generate variation
→ execute → measure → compare → retain/reject → record lineage → repeat
```

This generalizes the Agentic Variation Operator pattern: the agent decides what to inspect, modify, test, and retain rather than relying on one hard-coded mutation operator.

### Candidate Lineage

Every evolving artifact has ancestry:

```yaml
candidate:
  id: ""
  parent: ""
  changes: []
  hypothesis: ""
  benchmark: ""
  result: ""
  regression_tests: []
  status: baseline | candidate | accepted | rejected | rolled_back
```

Never lose the ability to reproduce why a candidate was accepted.

### Frontier Search

Maintain multiple promising candidates rather than following one path:

- **Best-known** — always keep the best survivor
- **Top-k** — keep the k best
- **Diverse exploration** — keep candidates that differ meaningfully
- **Epsilon-greedy** — mostly exploit, occasionally explore
- **Softmax exploration** — probabilistic selection weighted by score
- **Pareto selection** — retain candidates best on different objectives

### Protected Invariants

The agent may optimize performance but may **never** optimize away: authorization, auditability, safety boundaries, isolation, approval gates, rollback mechanisms, logging, provenance, or policy enforcement. The agent cannot declare these constraints obsolete.

### Adaptive Strategy Switching

If improvement stalls (several rounds with no meaningful improvement, candidate diversity collapses, evaluator stops discriminating), change: hypothesis, decomposition, research direction, tool, agent role, simplification, or evaluation criteria (only when justified by the real objective).

### Open-Ended Discovery

```
capability frontier → find weakness → generate challenge → attempt solution
→ evaluate → learn → update skill/model/strategy → generate harder challenge
```

Keep training and evaluation environments separated. Do not measure progress only on self-generated tasks.

---

## Learning

### Reflection

After meaningful work:

```
intent → actual outcome → evidence → deviation → root cause → lesson → action change → memory/skill update
```

A reflection is useful only if it changes future behavior, state, evaluation, or knowledge.

### Skill Acquisition

A candidate skill requires:

```
successful procedure → document procedure → test on independent case
→ compare outcome → validate → promote to trusted skill
```

A one-off success is not a trusted skill.

```yaml
skill:
  preconditions: []
  procedure: []
  expected_outcomes: []
  verification: []
  failure_modes: []
  confidence: 0.0
  tested_cases: []
  version: ""
```

### Meta-Learning

Learn not only what answer worked, but: which strategy worked, which environment signals mattered, when to switch strategies, which tools were reliable, which failures predict future failures, which model is best for which task, and how much verification was actually needed. Maintain a strategy-performance history.

### Model Routing

Route tasks by measured capability: `simple extraction → fast model, coding → coding-specialized model, deep reasoning → reasoning model, vision → vision model, classification → lightweight model, verification → independent model/tool`. Periodically evaluate routing decisions against actual outcomes.

---

## Checkpointing and Recovery

### Checkpointing

Long-running missions MUST checkpoint:

```yaml
checkpoint:
  mission_id: ""
  task_graph: {}
  current_state: {}
  completed_tasks: []
  active_tasks: []
  pending_tasks: []
  world_state: {}
  memory_refs: []
  evidence: []
  decisions: []
  permissions: []
  budgets: {}
  failures: []
  next_actions: []
  timestamp: ""
```

A process crash must not destroy mission state.

### Crash Recovery

On restart: `load checkpoint → validate state → reconcile external state → detect partial actions → identify uncertain transactions → recover → continue`. Never blindly replay an uncertain external action.

### Recovery Engine

| Mode | When to Use |
|------|-------------|
| RETRY | Transient failure, safe to retry |
| REPAIR | Logic or parameter error, fix and retry |
| ROLLBACK | Partial commit, revert and retry |
| ALTERNATIVE_TOOL | Current tool unreliable |
| ALTERNATIVE_PLAN | Current plan fundamentally flawed |
| ENVIRONMENT_RESET | Environment corrupted |
| STATE_RECONCILIATION | World model diverged from reality |
| SPECIALIST_ESCALATION | Need different expertise |
| HUMAN_ESCALATION | Needs authority or judgment only a human has |
| MISSION_ABORT | Continuing is irrational or unsafe |

Never repeat an identical failed action. Retries must change something: `diagnose → alter parameter → alter strategy → alternate tool → isolate cause → retry`.

---

*Next: `10-Implementation-Guide.md:1` — how to deploy and operate it.*
