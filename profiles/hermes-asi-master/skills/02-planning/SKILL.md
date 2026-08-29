---
name: hermes-planning
description: Hermes Planning & Search — Mission compilation, 6-plan portfolio, DAG task graph decomposition, search over strategies, and replanning.
version: "2.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: ['hermes', 'planning', 'dag', 'search', 'replanning']
    category: hermes-advanced
    requires_tools: ['file_read', 'file_write']
---
# SKILL 02 â€” PLANNING & SEARCH

> **Load this skill when:** Task needs goal decomposition, task graphs, plan selection, or search over strategies.
> **Requires:** Mission context + World Model from 06-memory-world (load 06 first if world state is stale).

---

## 1. Mission Compilation

Every mission becomes a durable object:

```yaml
mission:
  id: unique_id
  raw_request: original_text
  interpreted_intent: inferred_need
  superintelligent_intent: predicted_latent_need  # ASI
  desired_outcome: concrete_state_change
  strategic_value: long_term_optionality_created
  acceptance_criteria: [measurable_conditions]
  formal_properties: [provable_invariants]  # ASI
  constraints: {hard: [], soft: [], forbidden: [], physical: [], legal: [], ethical: []}
  risk: low | medium | high | critical | existential  # R6
  budget: {money: null, tokens: null, time: null, tool_calls: null, compute: null}
  evidence_requirements: []
  verification_standard: test | proof | independent_reproduction
  counterfactuals: [what_if_assumption_false]
  status: active | blocked | completed | aborted
```

**Strict separation:** `request â‰  intent â‰  goal â‰  objective â‰  outcome â‰  acceptance criterion â‰  task â‰  action`.

### Goal Compiler

```
natural-language mission â†’ Goal â†’ Subgoals â†’ Outcomes â†’ Constraints â†’ Acceptance Tests
â†’ Formal Properties â†’ Task Graph â†’ Execution Policy â†’ Verification Plan â†’ Proof Obligations
```

Detect: ambiguity, hidden requirements, conflicting goals, impossible constraints, missing permissions, dependencies, deadlines, strategic opportunities.

## 2. Plan Portfolio â€” 6 Competing Plans

```
PLAN A â€” Conservative    Lowest risk, proven path
PLAN B â€” Balanced        Best expected value (default)
PLAN C â€” Aggressive      Highest upside, managed risk
PLAN D â€” Experimental    Novel, high learning value
PLAN E â€” Antifragile     Gains from volatility, robust to unknowns
PLAN F â€” Strategic       Maximizes long-term optionality, 100x vision
```

Score each by: expected outcome, success probability, evidence, cost, latency, risk, reversibility, complexity, dependencies, maintenance, optionality, antifragility, strategic trajectory. **Evidence beats vote count.**

### Hypothesis Generation (AGX Pattern)

- **H1:** Safest conventional
- **H2:** High-upside alternative
- **H3:** Fundamentally different strategy

Score by: benefit, evidence, cost, reversibility, risk, compatibility, testability.

## 3. Task Graph (DAG)

```yaml
task:
  id: T1
  objective: ""
  inputs: []
  outputs: []
  dependencies: []
  owner: ""
  workspace: ""
  permissions: []
  budget: {}
  acceptance_tests: []
  formal_properties: []
  verification: {}
  rollback: {}
  status: pending | ready | running | blocked | failed | verified | proven
```

Rules:
- Parallelize only independent work. Serialize conflicting writes.
- Isolated workspaces for speculative branches.
- Critical path engine calculates: critical path, bottlenecks, single points of failure, resource contention, **strategic leverage points**.

## 4. Reasoning Portfolio

| Strategy | When |
|----------|------|
| ReAct `reasonâ†’actâ†’observeâ†’update` | General purpose |
| Plan-and-Execute | Structured decomposition |
| ReWOO `plan depsâ†’parallel executeâ†’synthesize` | Parallelizable work |
| Tree Search | Combinatorial decisions |
| Beam Search (keep best N) | Bounded exploration |
| Graph-of-Thought | Compositional merging |
| Monte-Carlo | Stochastic environments |
| Evolutionary `generateâ†’mutateâ†’evaluateâ†’select` | Optimization |
| **Abstract Synthesis [ASI]** | Cross-domain transfer |
| **Formal Reasoning [ASI]** | Provable correctness |

Every search has budget: `{max_branches, max_depth, max_rollouts, max_tokens, max_time, evaluation_budget, verification_budget}`

### Simulation Ensemble [ASI]

```
candidate actions â†’ simulation ensemble (N worlds) â†’ predicted distributions â†’ risk analysis â†’ decision
```
Never treat simulation success as real-world success.

## 5. Dynamic Replanning

Replan when: assumption fails, dependency breaks, environment changes, criteria change, risk crossed, evidence re-ranks plans, budget/deadline changes, tool unavailable, **strategic opportunity emerges**, **simulation reveals superior trajectory**. Do not replan on mere uncertainty.

## 6. Priority Heuristic

```
priority â‰ˆ value Ã— probability_of_success Ã— urgency Ã— information_gain Ã— strategic_optionality Ã— antifragility Ã· cost Ã· risk
```

## 7. Checklists

**Before Planning:**
- [ ] What is the actual + strategic outcome?
- [ ] What proves success? What would prove failure?
- [ ] What constraints (hard/soft/forbidden/legal/ethical)?
- [ ] What is the cheapest useful next action?

**During Execution:**
- [ ] Is plan still valid? Is world state still valid?
- [ ] Strategic trajectory still optimal?

---

*Planning Skill v9.0 â€” 6 plans, DAG, 10 reasoning strategies, simulation ensemble.*

