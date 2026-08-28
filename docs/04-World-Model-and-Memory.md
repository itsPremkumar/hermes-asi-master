# 04 — World Model and Memory

## The Core Distinction

The world model is the agent's **current best model of reality**. It is not reality itself. Every conclusion is tagged with epistemic status so the agent knows how much to trust it and what would change its mind.

---

## World Model

### Structure

```yaml
world:
  entities: []              # people, systems, files, resources
  relationships: []         # how entities relate
  resources: []             # compute, money, time, API quota
  capabilities: []          # what the agent can actually do (verified)
  environment: {}           # current environment snapshot
  tasks: []                 # active and pending work
  dependencies: []          # what blocks what
  observations: []          # raw tool/environment outputs
  events: []                # timestamped occurrences
  assumptions: []           # temporary premises
  hypotheses: []            # testable propositions
  risks: []                 # identified risks with severity
  commitments: []           # promises to the user or other agents
  external_state: {}        # state outside the agent's control
  temporal_state: {}        # deadlines, schedules, expected durations
  causal_models: []         # cause → mechanism → effect
  unknowns: []              # explicitly tracked unknowns
```

### Transitions

Every significant state change is recorded:

```yaml
transition:
  before: {}                # state before
  action: {}                # what was done
  observation: {}           # what was observed
  after: {}                 # state after
  timestamp: ""
  actor: ""                 # which agent or system
  source: ""                # tool or observation channel
  confidence: confirmed | supported | likely | plausible | uncertain
  evidence: []              # supporting evidence
  causal_hypothesis: ""     # optional explanation
  reversible: true | false | unknown
```

---

## Epistemic States

Every important claim carries epistemic metadata:

```yaml
claim:
  id: ""
  text: ""
  status: fact | observed | sourced | inferred | hypothesis | prediction | assumption | unknown | contradicted | obsolete
  sources: []
  confidence: 0.0-1.0
  verification_method: ""
  last_verified: ""
  expires_at: ""
  conflicting_claims: []
```

| Status | Meaning | Example |
|--------|---------|---------|
| **fact** | Directly supported by reliable evidence | "File X exists — observed via filesystem tool" |
| **observed** | Actually measured or returned | "API returned status 200" |
| **sourced** | Backed by an external authoritative source | "Docs say endpoint requires auth (2026-08-28)" |
| **inferred** | Derived from evidence through reasoning | "If X is true, Y probably follows" |
| **hypothesis** | Testable, not yet established | "If Z is true, Y should be observable after action A" |
| **prediction** | Forecast about future state | "Plan A will likely complete in 2 hours" |
| **assumption** | Temporary premise to continue | "Assuming credentials are valid" |
| **unknown** | Explicitly not established | "We do not know the rate limit" |
| **contradicted** | Evidence conflicts | "Source A says X, source B says not-X" |
| **obsolete** | Previously true, now stale | "API v1 endpoint (deprecated 2026-06)" |

**Never allow `assumption → fact` without evidence.** The agent must be able to say: "I know this. I infer this. I suspect this. I do not know this. Evidence contradicts this."

---

## Evidence Graph

Research produces a graph, not a pile of links:

```
Claim
 ├── Source (primary preferred)
 ├── Evidence (direct observation)
 ├── Counter-evidence (contradictory findings)
 ├── Method (how evidence was obtained)
 ├── Timestamp (when it was true)
 ├── Reliability (authority, freshness, independence)
 └── Dependency (what else it relies on)
```

For consequential claims:

```
claim → primary source → independent source → contradiction search → freshness check → confidence update
```

- Prefer primary evidence over secondary summaries.
- Never use search-result snippets as final evidence when the underlying source can be inspected.
- Record exact dates when timing matters.
- Preserve disagreements in the record.

---

## Source Reliability

Score each source by:

```
reliability = authority + primary_source_status + recency + methodological_transparency
            + corroboration + specificity + independence
            - conflict_of_interest - unverifiable_claims - stale_information
```

---

## Contradiction Engine

The agent actively searches for evidence that could prove its current belief wrong:

```
belief → support search → contradiction search → alternative explanation
       → independent verification → posterior update
```

When evidence conflicts:

```
detect → preserve both claims → compare provenance → check timestamps
→ check scope → run discriminating test → adjudicate → record resolution
```

Never silently overwrite contradictory information. Preserve both claims until evidence resolves them.

---

## Research Engine

Research is an executable subsystem with stopping rules based on Value of Information:

```
VOI = P(research changes decision) × expected benefit − research cost
```

Stop when the decision is sufficiently supported AND additional research has low expected VOI.

### Four Passes

| Pass | Name | Purpose |
|------|------|---------|
| **1** | Discovery | Terminology, major entities, candidate solutions, source landscape, obvious contradictions, recent developments |
| **2** | Evidence | Primary sources, supporting evidence, source dates, confidence, conflicts for each important claim |
| **3** | Adversarial | Counterexamples, contradictory docs, failure reports, version differences, discontinued features, hidden constraints, misleading claims |
| **4** | Synthesis | Evidence matrix: \| Claim \| Evidence \| Source quality \| Freshness \| Contradiction \| Confidence \| |

---

## Context Operating System

Context is a **finite managed resource**, not an append-only log.

**Operations:** `WRITE → SELECT → RANK → COMPRESS → ISOLATE → ARCHIVE → RESTORE`

Optimize for: relevance, decision impact, freshness, uncertainty, dependency, source quality, token cost.

### Context Packets

Before consequential reasoning, create:

```yaml
context_packet:
  mission: {}
  current_goal: {}
  acceptance_tests: []
  constraints: []
  permissions: []
  relevant_world_state: {}
  relevant_memory: []
  evidence: []
  contradictory_evidence: []
  hypotheses: []
  active_plan: {}
  failures: []
  pending_commitments: []
  available_tools: []
  known_limitations: []
```

---

## Memory OS

### Namespaces

```
working        — current task working memory
episodic       — what happened, when, with evidence
semantic       — durable facts about the world
procedural     — how to do things (validated procedures)
organizational — architecture decisions, conventions
failure        — what failed, why, and the fix
evaluation     — benchmark results, scores, regressions
world-state    — snapshots of world model over time
skill          — promoted, validated skills
research       — evidence graphs and source assessments
decision       — decision records with rationale
causal         — cause → mechanism → effect models
preference     — user preferences (not world facts)
identity       — stable commitments (SOUL.md)
```

### Lifecycle

```
observe → score → normalize → deduplicate → validate → resolve conflicts
→ summarize → assign provenance → assign TTL → store → retrieve
→ evaluate retrieval → consolidate
```

### Importance

```
importance = future_reuse × consequence × reconstruction_cost × identity_relevance × verification_strength
```

Do not persist everything. Persist information because it is reusable, consequential, difficult to reconstruct, identity-relevant, a validated skill, a failure lesson, a durable fact, or an important decision rationale.

### Conflict Resolution

When memories conflict (`new evidence vs. old memory`), evaluate: source authority, freshness, direct observation, corroboration, context, confidence, scope, expiration.

```yaml
conflict: {memory_a: {}, memory_b: {}, resolution: "", evidence: [], confidence: 0.0}
```

Never silently overwrite. Expire obsolete information.

### Sleep-Time Intelligence

When idle, the agent may perform bounded background computation: memory consolidation, research continuation, benchmarking, failure analysis, skill extraction, tool testing, index maintenance, plan preparation, simulation, candidate generation, evaluation, knowledge graph maintenance. Background workers must not silently perform high-impact external actions.

---

## Hypothesis Ledger

Maintain an explicit hypothesis ledger:

```yaml
hypothesis:
  id: H-123
  claim: ""
  confidence: 0.0
  supporting_evidence: []
  opposing_evidence: []
  predictions: []
  tests: []
  status: active | supported | rejected | unknown
```

Never allow an old assumption to silently become a fact. Periodically revalidate active hypotheses against new evidence.

---

*Next: `05-Planning-and-Search.md:1` — how the agent decides what to do.*
