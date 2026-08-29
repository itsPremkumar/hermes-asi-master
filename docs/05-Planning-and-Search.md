# 05 — Planning and Search

## Goal Compilation

Every natural-language mission is compiled into a structured execution contract:

```
natural-language mission
  → Goal → Subgoals → Outcomes → Constraints → Acceptance Tests
  → Task Graph → Execution Policy → Verification Plan
```

The compiler must detect: ambiguity, hidden requirements, conflicting goals, impossible constraints, missing permissions, unavailable resources, dependencies, deadlines, risk, and required evidence.

**Material ambiguity is surfaced. Low-risk ambiguity may be resolved with conservative defaults.** Never silently invent a material requirement.

### What the Compiler Produces

| Artifact | Purpose |
|----------|---------|
| **Goal** | Single desired state change, outcome-oriented |
| **Subgoals** | Decomposed outcomes, each with owner and acceptance tests |
| **Constraints** | Hard (must hold), soft (prefer), forbidden (must not occur) |
| **Acceptance Tests** | Measurable conditions that prove completion |
| **Task Graph** | Dependency-aware DAG of work units |
| **Execution Policy** | Cognitive mode, parallelism, budget, risk ceiling |
| **Verification Plan** | What evidence proves each subgoal |

---

## Plan Portfolio

For any high-impact objective, generate **four competing plans**:

```
PLAN A — Conservative    Lowest risk, most reliable path
PLAN B — Balanced        Best expected value (usually recommended)
PLAN C — Aggressive      Highest upside, higher risk
PLAN D — Experimental    Novel approach, learning-oriented
```

Score each by:

```
expected outcome, success probability, evidence strength, cost, time,
risk, reversibility, complexity, dependency exposure, future optionality, maintenance burden
```

Choose based on evidence and mission utility. Evidence beats vote count.

### Hypothesis Generation (AGX Pattern)

Before expensive execution, generate at least:

- **H1:** Safest conventional approach
- **H2:** High-upside alternative
- **H3:** Fundamentally different strategy (when search space is broad)

Score by: expected benefit, evidence strength, implementation cost, reversibility, risk, compatibility, testability.

---

## Task Graph

Represent work as a DAG (or controlled state graph):

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
  verification: {}
  rollback: {}
  status: pending | ready | running | blocked | failed | verified
```

Rules:

- Parallelize only independent work.
- Serialize conflicting writes.
- Use isolated workspaces for speculative branches.
- Continuously calculate: critical path, bottlenecks, single points of failure, resource contention, gating evidence, high fan-out dependencies.
- **Optimize the bottleneck, not random tasks.**

---

## Search Strategies

For difficult problems, search over **strategies**, not just answers:

```
state → candidate strategies → cheap evaluation → prune weak branches
      → expand promising branches → test → retain best evidence-backed branch
```

| Strategy | When to Use |
|----------|-------------|
| **ReAct** | `reason → act → observe → update` — general purpose |
| **Plan-and-Execute** | `plan → execute subtasks → verify` — structured decomposition |
| **ReWOO-style** | `plan tool dependencies → execute parallel operations → synthesize` — parallelizable work |
| **Tree Search** | Branch on candidate plans, evaluate, prune — combinatorial decisions |
| **Beam Search** | Keep only the best N strategies — bounded exploration |
| **Graph-of-Thought** | Reusable partial solutions merge — compositional tasks |
| **Monte-Carlo Search** | When simulation is possible — stochastic environments |
| **Evolutionary Search** | `generate → mutate → evaluate → select → archive → repeat` — optimization |

Every search requires a budget:

```yaml
search_budget: {max_branches: 0, max_depth: 0, max_rollouts: 0, max_tokens: 0, max_time: "", evaluation_budget: 0, stop_rule: ""}
```

Never explode the search tree without a budget.

---

## Simulation Layer

Before risky real-world actions, simulate where possible:

```
candidate action → simulation model → real environment
```

Simulation can test: code, workflows, plans, financial assumptions, scheduling, infrastructure, robotics, browser workflows, deployment, optimization candidates.

**Never treat simulation success as real-world success.**

---

## Dynamic Replanning

Replan when:

- Critical assumption fails
- Dependency breaks
- Environment changes
- Acceptance criteria change
- Risk crosses threshold
- New evidence changes plan ranking
- Budget or deadline changes
- Tool becomes unavailable
- Better strategy appears

**Do not replan merely because uncertainty exists.** Uncertainty is normal and expected. Replan when uncertainty materially changes the decision.

---

## Decision Engine

```yaml
decision:
  question: ""
  options: []
  assumptions: []
  evidence: []
  probabilities: []
  expected_values: []
  risks: []
  reversibility: ""
  dependencies: []
  second_order_effects: []
  recommendation: ""
  confidence: 0.0
```

For consequential decisions compare: expected value, worst case, best case, variance, reversibility, option value, downside risk.

### Counterfactual Engine

For high-impact choices evaluate:

```
A happens / B happens / nothing happens / assumption X is false
/ resource Y disappears / environment changes / adversary responds
```

Ask: **What evidence would make the current preferred plan wrong?**

---

## Priority and Utility

Practical heuristic:

```
priority ≈ value × probability_of_success × urgency × information_gain × strategic_optionality ÷ cost ÷ risk
```

This is a decision aid, not a universal law. Use it to rank tasks when multiple are ready.

---

*Next: `06-Multi-Agent-Orchestration.md:1` — how the agent scales beyond one model call.*
