# 06 — Multi-Agent Orchestration

## Why Multi-Agent?

A single model call has limited context, limited specialization, and correlated failure modes. Multi-agent orchestration scales execution by:

- Reducing error through specialization and verification diversity
- Reducing context overload by partitioning work
- Reducing execution time through parallelization
- Reducing correlated blind spots through diverse perspectives

**The Executive must not spawn agents merely to appear sophisticated.** Every subagent has a cost (coordination, tokens, latency, failure correlation) and must justify it.

---

## Agent Factory

Agents are instantiated dynamically from a role library:

| Role | Purpose |
|------|---------|
| **Researcher** | Broad evidence gathering |
| **Deep Researcher** | Evidence graph and source auditing |
| **Web Researcher** | Current external claims, official docs, release notes |
| **Source Auditor / Fact Checker** | Source reliability and claim verification |
| **Contradiction Hunter** | Actively seeks disconfirming evidence |
| **Planner / Strategist** | Generates and scores competing plans |
| **Architect** | Designs best solution from evidence |
| **Engineer / Coder** | Implements the solution |
| **Debugger / Tester** | Finds and fixes defects; validates behavior |
| **Security / Privacy Auditor** | Secrets, permissions, attack surface |
| **Performance Engineer** | Latency, throughput, resource optimization |
| **Data Scientist / Statistician** | Analysis, modeling, causal inference |
| **Simulation / Experiment Designer** | Builds and runs controlled tests |
| **Browser / Computer / Operations Agent** | Interacts with environments |
| **Evaluator / Benchmark Agent** | Scores candidates against criteria |
| **Critic** | Tries to falsify the proposed solution |
| **Red Team Agent** | Finds security flaws, catastrophic modes, cheaper alternatives |
| **Verifier** | Independent validation of builder output |
| **Synthesizer / Writer / Editor** | Produces final artifacts |
| **Knowledge Curator / Memory Agent** | Maintains knowledge graph and memory |
| **Recovery Agent** | Diagnoses repeated failures |
| **Monitor / Observer** | Tracks health, progress, heartbeats |
| **Evolution / Optimization Agent** | Generates and evaluates variants |

---

## Agent Economics

For every proposed subagent, estimate:

```
expected_information_gain + expected_error_reduction + expected_time_saved
  vs.
coordination_cost + token_cost + latency + failure_correlation
```

Spawn only when `benefit > orchestration cost`.

---

## Agent Diversity

For important decisions, independence must be meaningful. Varying only the agent name while keeping identical prompts, context, and model is not diversity. Vary:

```
model, prompt, context, reasoning strategy, tools, search sources, specialization, assumptions
```

Useful diversity patterns:

- **Builder + Critic + Independent Solver + Verifier** — four independent perspectives
- **Epsilon-greedy exploration** — mostly exploit best strategy, occasionally explore alternatives
- **Pareto selection** — retain candidates that are best on different objectives

---

## Recursive Delegation

Children inherit **bounded** scope:

```
depth, fanout, budget, permissions, deadline, risk scope, workspace
```

Each child MUST have: `one objective, one parent, one budget, one termination condition`.

```
Executive
 ├── Researcher (depth 1, budget 30%)
 │    ├── Web Researcher (depth 2, budget 10%)
 │    └── Source Auditor (depth 2, budget 10%)
 ├── Planner (depth 1, budget 20%)
 └── Engineer (depth 1, budget 30%)
      ├── Coder A (depth 2)
      └── Coder B (depth 2, alternative approach)
```

Maximum depth, fan-out, budget, deadline, and risk scope are enforced. No child may exceed inherited authority.

---

## Delegation Contract

```yaml
delegation:
  id: ""
  parent_task: ""
  objective: ""              # exactly one objective
  non_goals: []              # explicitly out of scope
  context_refs: []           # minimal required context
  tools: []                  # scoped tool list
  source_requirements: []    # evidence quality expectations
  output_schema: {}          # required output format
  budget: {}                 # tokens, time, tool calls
  deadline: ""
  success_tests: []          # acceptance criteria
  authority_scope: {}        # what this delegation may do
  escalation_rule: ""        # when to escalate vs. recover locally
  termination_condition: ""  # when to stop
```

---

## Agent Result Contract

```yaml
result:
  task_id: ""
  status: success | partial | failed | blocked
  summary: ""
  artifacts: []              # files, outputs, data
  evidence: []               # what proves the claim
  assumptions: []            # what was assumed
  uncertainties: []          # what remains uncertain
  tests: []                  # tests run
  failures: []               # failures encountered
  metrics: {}                # measurable results
  confidence: 0.0
  recommended_next_action: ""
```

**Never merge results based on verbosity or confidence.** Evidence wins.

---

## Agent-to-Agent Protocol

Supported message types: `REQUEST, PROPOSAL, DELEGATION, RESULT, EVIDENCE, QUESTION, BLOCKER, WARNING, CRITIQUE, REVIEW, COMMIT, ROLLBACK, ESCALATION, HEARTBEAT, STATE_UPDATE, CAPABILITY_REQUEST, AUTHORIZATION_REQUEST`.

Each message includes: `{id, mission_id, task_id, sender, recipient, type, payload, evidence, confidence, timestamp, dependencies}`.

Support: `MCP, A2A, AG-UI-like event protocols, OpenAPI-compatible tools, REST, GraphQL, CLI, RPC, local process adapters`.

---

## Agent Debate Protocol

For consequential decisions:

```
PROPOSER → CRITIC → ALTERNATIVE SOLVER → RED TEAM → VERIFIER → EXECUTIVE
```

Debate is not a vote. Evidence wins. The Executive adjudicates based on strength of evidence and reasoning, not agent count.

### Adversarial Agent

The Red Team must attempt to:

- Falsify assumptions
- Find hidden dependencies
- Find security flaws
- Find contradictory evidence
- Break acceptance criteria
- Discover edge cases
- Find cheaper alternatives
- Find catastrophic failure modes

The Red Team must **not** optimize for negativity. Its job is to surface real risks, not to oppose for its own sake.

---

## Independent Verification

High-impact work requires separation between **builder** and **verifier**:

```
Builder produces → Verifier receives (objective + acceptance criteria + artifact + evidence)
                → Verifier checks without inheriting builder assumptions
                → Evidence → Adjudication
```

The verifier ideally receives only `objective + acceptance criteria + artifact + evidence` — not the builder's full context, which would propagate the same blind spots.

---

## Parallel Experimentation

When running independent candidates in parallel:

- Each worker has: isolated workspace, explicit hypothesis, identical acceptance criteria, comparable evaluation, independent trace.
- After execution: normalize results → deduplicate → detect contradictions → rank → retain best verified → feed lessons back.

Never combine incompatible changes without revalidation.

---

*Next: `07-Tools-and-Environment.md:1` — how the agent interacts with the world.*
