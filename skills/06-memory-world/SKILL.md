---
name: agi-memory-world
version: "9.0"
parent: hermes-advanced-executive
hermes: true
hermes_suite: HERMES-Advanced
scope: World Model, Epistemics, Evidence, Context, Memory, Temporal Reasoning
planes: [World Model, Memory, Context, Cognition]
---

# SKILL 06 â€” MEMORY, WORLD MODEL & CONTEXT

> **Load this skill when:** Task needs world state tracking, memory recall/storage, context management, or epistemic rigor.
> **Load FIRST in any full mission** â€” establishes the world model before research and planning.

---

## 1. World Model â€” Multi-Horizon Superintelligent

```yaml
world:
  entities: []
  relationships: []
  resources: []
  capabilities: []
  environment: {}
  tasks: []
  dependencies: []
  observations: []
  events: []
  assumptions: []
  hypotheses: []
  risks: []
  commitments: []
  external_state: {}
  temporal_state: {past: {}, present: {}, future_scenarios: []}  # ASI
  causal_models: []                     # cause â†’ mechanism â†’ effect
  counterfactual_worlds: []             # ASI what-if simulations
  simulation_ensemble: []               # ASI multiple futures
  unknowns: []
  known_unknowns: []
  unknown_unknowns_estimate: 0.0        # ASI humility metric
```

Every transition:

```yaml
transition: {before: {}, action: {}, observation: {}, after: {}, timestamp: "", actor: "", source: "", confidence: confirmed|supported|likely|plausible|uncertain, evidence: [], causal_hypothesis: "", reversible: true|false|unknown, strategic_implication: ""}
```

**Multi-Horizon Temporal Modeling [ASI]:**
- Past: causal reconstruction of what happened and why
- Present: what is true now with confidence intervals
- Near future: next 24h with scenarios
- Strategic future: next 90 days with branching trajectories

Distinguish: `completed | currently_true | in_progress | scheduled | expected | conditional | speculative | strategically_projected [ASI]`

## 2. Epistemic Superintelligence

```yaml
claim:
  id: ""
  text: ""
  status: fact | observed | sourced | inferred | hypothesis | prediction | assumption | unknown | contradicted | obsolete
  bayesian_prior: 0.0
  bayesian_posterior: 0.0
  sources: []
  confidence: 0.0-1.0
  calibration_score: 0.0
  verification_method: ""
  falsification_test: "what would prove this wrong"
  last_verified: ""
  expires_at: ""
  conflicting_claims: []
  cross_domain_support: []
```

| Status | Meaning | ASI Precision |
|--------|---------|---------------|
| fact | Directly supported | Bayesian posterior >0.95 + independent corroboration |
| observed | Actually measured | Sensor trace with provenance |
| hypothesis | Testable | Includes falsification criterion |
| unknown | Not established | Classified as known-unknown vs unknown-unknown |
| contradicted | Evidence conflicts | Both sides preserved with adjudication plan |

**Never allow `assumption â†’ fact` without evidence.** Even superhuman repetition doesn't make it true.

### Evidence Graph

```
Claim â†’ Source â†’ Evidence â†’ Counter-evidence â†’ Method â†’ Timestamp + Decay â†’ Reliability â†’ Dependency â†’ Bayesian Weight â†’ Cross-domain Corroboration
```

For consequential claims: `claim â†’ primary source â†’ independent source â†’ contradiction search â†’ freshness check â†’ adversarial challenge â†’ formal verification â†’ confidence update`

### Source Reliability

```
reliability = authority + primary_status + recency + transparency + corroboration + specificity + independence + reproducibility - conflict - unverifiable - stale - circular_citation
```

### Contradiction Engine

```
belief â†’ support search â†’ contradiction search â†’ â‰¥3 alternatives â†’ adversarial challenge â†’ independent verification â†’ Bayesian update â†’ posterior
```

## 3. Context Operating System â€” Hierarchical

Context is a FINITE managed resource:

```
WRITE â†’ SELECT â†’ RANK â†’ COMPRESS â†’ ISOLATE â†’ ARCHIVE â†’ RESTORE â†’ SYNTHESIZE [ASI]
```

Optimize for: relevance, decision impact, freshness, uncertainty, dependency, source quality, token cost, strategic value, cross-domain relevance.

**Hierarchical Compression [ASI]:**
- L1: Raw observations (full fidelity, short TTL)
- L2: Extracted facts (deduplicated, provenance-tagged)
- L3: Synthesized insights (compressed, high importance)
- L4: Strategic abstractions (cross-mission, permanent)

Before consequential reasoning, create:

```yaml
context_packet: {mission: {}, current_goal: {}, acceptance_tests: [], constraints: [], permissions: [], relevant_world_state: {}, relevant_memory: [], evidence: [], contradictory_evidence: [], hypotheses: [], active_plan: {}, failures: [], pending_commitments: [], available_tools: [], known_limitations: [], strategic_context: {}, cross_domain_analogies: []}
```

## 4. Memory OS â€” 15 Namespaces

```
working, episodic, semantic, procedural, organizational, failure, evaluation,
world-state, skill, research, decision, causal, preference, identity,
strategic [ASI], superintelligent_insight [ASI]
```

**Lifecycle:**
```
observe â†’ score â†’ normalize â†’ deduplicate â†’ validate â†’ resolve conflicts
â†’ synthesize â†’ assign provenance â†’ TTL â†’ hierarchical compress â†’ store
â†’ retrieve â†’ evaluate retrieval â†’ consolidate â†’ cross-domain index [ASI]
```

**Importance:**
```
importance = future_reuse Ã— consequence Ã— reconstruction_cost Ã— identity_relevance Ã— verification_strength Ã— cross_domain_transferability [ASI] Ã— strategic_value [ASI]
```

Conflict resolution evaluates: source authority, freshness, direct observation, corroboration, context, confidence, scope, expiration. Record `{memory_a, memory_b, resolution, evidence, confidence, strategic_implication}`. Never silently overwrite.

### Sleep-Time Superintelligence [ASI]

When idle, bounded background work: memory consolidation, hierarchical compression, research continuation, benchmarking, failure analysis, skill extraction, tool testing, index maintenance, plan preparation, multi-future simulation, candidate generation, evaluation, knowledge graph maintenance, **autonomous hypothesis generation**, **cross-mission pattern mining**, **self-model improvement**. All bounded, interruptible, observable, budgeted, permission-aware, reversible.

## 5. Hypothesis Ledger

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

## 6. Cognition Enhancements (Memory-Linked)

**Confidence Calibration:**
```yaml
confidence: {value: 0.0-1.0, basis: "", evidence_count: 0, independent_sources: 0, contradictory_sources: 0, uncertainty: "", calibration_history: [], bayesian_posterior: 0.0}
```
Track `predicted confidence vs actual success` â†’ Brier score â†’ calibration curve.

**Causal:** `hypothesis â†’ intervention â†’ observation â†’ causal update` with confounder modeling.

**Counterfactual:** For high-impact choices evaluate `A happens / B happens / nothing / assumption X false / resource Y disappears / environment changes / adversary responds / black swan`. Ask: *What evidence would make the current plan catastrophically wrong?*

---

*Memory & World Skill v9.0 â€” Multi-horizon world model, Bayesian epistemics, 15 namespaces, hierarchical context.*

