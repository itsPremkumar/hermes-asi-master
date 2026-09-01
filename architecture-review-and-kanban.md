# Hermes-ASI-Master — 20 Project Architecture Review & Kanban Decomposition

## Executive Summary

This document provides:
1. **Architecture review** for P0 cognitive foundation projects (risks, design validation, improvements)
2. **Kanban decomposition** for P1-P4 into implementation-ready cards
3. **Dependency mapping** across all 20 projects
4. **Routing** of P2 agency & action specs to @backend

---

## P0 — COGNITIVE FOUNDATION (Architecture Review)

### P0.1: Real World Model Engine

**Core Design:**
- Continuously maintained knowledge graph with entity versioning
- Temporal reasoning (events have start/end, can query at any point in time)
- Predictive simulation ("what if" scenarios, Genie 3 inspired)

**Architecture Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Feasibility | Medium-High | Knowledge graphs are well-understood; predictive simulation is the hard part |
| Novelty | Medium | Temporal KGs exist (e.g., Google Knowledge Graph), but agent-specific versioning is novel |
| Risk | High | Predictive simulation at scale is computationally expensive; hallucination risk |
| Integration | High | Central dependency for nearly every other project |

**Key Risks:**
1. **Scalability**: Graph queries degrade past ~10M entities without sharding
2. **Consistency**: Concurrent updates from multiple agents need CRDT or transactional guarantees
3. **Predictive accuracy**: Simulation diverges from reality without ground-truth validation
4. **Storage**: Full temporal versioning grows unbounded; need garbage collection

**Suggested Improvements:**
- Use **event sourcing** for the knowledge graph (immutable log + materialized views)
- Implement **tiered storage**: hot (recent) → warm (compressed) → cold (archived)
- Add **confidence scores** to every entity/edge (decay over time without reinforcement)
- Use **approximate simulation** (Monte Carlo) rather than deterministic prediction

**Interfaces:**
```typescript
interface WorldModel {
  // Entity management
  createEntity(type: string, properties: Record<string, unknown>): Entity;
  updateEntity(id: string, patch: Partial<Entity>): Entity;
  getEntityAtTime(id: string, timestamp: number): Entity | null;

  // Relationship management
  addRelationship(from: string, to: string, type: string, confidence: number): Relationship;
  queryRelationships(filter: RelationshipFilter): Relationship[];

  // Temporal queries
  queryAtTime(query: Query, timestamp: number): QueryResult;
  getEntityHistory(id: string, start: number, end: number): EntityVersion[];

  // Predictive simulation
  simulate(scenario: SimulationScenario, steps: number): SimulationResult;
  predict(entityId: string, horizon: number): PredictionResult;

  // Confidence management
  decayConfidence(rate: number): void;
  reinforce(entityId: string, evidence: string): void;
}

interface Entity {
  id: string;
  type: string;
  properties: Record<string, unknown>;
  confidence: number;
  createdAt: number;
  updatedAt: number;
  version: number;
  provenance: string[];
}

interface SimulationResult {
  steps: Array<{
    action: string;
    outcome: string;
    confidence: number;
    state: Record<string, unknown>;
  }>;
  finalConfidence: number;
  divergences: string[];
}
```

---

### P0.2: Metacognitive Monitor

**Core Design:**
- Real-time tracking of reasoning process
- confidence calibration (is the agent's confidence justified?)
- strategy selection (which cognitive strategy to use for this problem)
- bias detection (identify cognitive biases in reasoning)

**Architecture Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Feasibility | High | Can be implemented as a wrapper around existing reasoning traces |
| Novelty | Medium-High | Metacognition in AI is under-explored; most systems lack self-monitoring |
| Risk | Medium | Risk of infinite recursion (monitoring the monitor); calibration is hard |
| Integration | High | Provides input to action selection, memory consolidation, self-explanation |

**Key Risks:**
1. **Overhead**: Real-time monitoring adds latency to every reasoning step
2. **Calibration quality**: Without ground truth, calibration may be inaccurate
3. **Bias detection**: Requires a taxonomy of biases; some biases are hard to detect from inside the system
4. **Strategy explosion**: Too many strategies to choose from; need good meta-strategy

**Suggested Improvements:**
- Use **asynchronous monitoring** (don't block reasoning for meta-analysis)
- Implement **calibration via outcome tracking** (compare confidence to actual outcomes)
- Use **bounded strategy set** (5-10 strategies, not 100)
- Add **interoceptive signals** (detect confusion, uncertainty, cognitive load)

**Interfaces:**
```typescript
interface MetacognitiveMonitor {
  // Reasoning tracking
  trackReasoning(step: ReasoningStep): void;
  getReasoningTrace(runId: string): ReasoningStep[];

  // Confidence calibration
  estimateConfidence(problem: Problem, reasoning: ReasoningStep[]): number;
  calibrateConfidence(predicted: number, actual: number): void;

  // Strategy selection
  selectStrategy(problem: Problem, context: AgentContext): CognitiveStrategy;
  getStrategyPerformance(strategyId: string): StrategyMetrics;

  // Bias detection
  detectBiases(reasoning: ReasoningStep[]): DetectedBias[];
  getBiasHistory(): DetectedBias[];

  // Interoception
  estimateCognitiveLoad(): number;
  estimateUncertainty(): number;
}

interface CognitiveStrategy {
  id: string;
  name: string;
  description: string;
  applicableWhen: (problem: Problem) => boolean;
  estimatedCost: number;
  estimatedReliability: number;
}

interface DetectedBias {
  type: string;  // e.g., 'confirmation_bias', 'anchoring', 'availability'
  severity: number;  // 0-1
  evidence: string;
  suggestedMitigation: string;
}
```

---

### P0.3: Temporal Reasoning Engine

**Core Design:**
- Time-aware causality (A causes B only if A happens before B)
- Planning under temporal constraints (deadlines, durations, dependencies)
- Temporal query language (what was true at time T?)

**Architecture Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Feasibility | Medium | Temporal logic is well-studied; integration with world model is complex |
| Novelty | Medium | Temporal databases exist, but agent-native temporal reasoning is novel |
| Risk | Medium-High | Temporal consistency across distributed agents is hard |
| Integration | High | Required by goal decomposition, action selection, world model |

**Key Risks:**
1. **Temporal paradoxes**: Agents may create inconsistent temporal claims
2. **Clock synchronization**: Distributed agents need logical clocks (Lamport/Hybrid)
3. **Temporal query complexity**: Range queries over temporal data are expensive
4. **Uncertainty**: Temporal boundaries may be fuzzy (approximately at time T)

**Suggested Improvements:**
- Use **Hybrid Logical Clocks** (HLC) for distributed timestamping
- Implement **temporal constraints as a solver** (CSP/SAT based)
- Add **fuzzy temporal intervals** (with confidence bounds)
- Use **temporal indexing** (interval trees, temporal B-trees)

**Interfaces:**
```typescript
interface TemporalReasoningEngine {
  // Temporal assertions
  assert(event: TemporalEvent): void;
  retract(eventId: string): void;

  // Temporal queries
  queryTemporal(query: TemporalQuery): TemporalResult;
  whatWasTrueAt(time: number, entityId: string): EntityState;
  whatWillBeTrueAt(time: number, entityId: string): Prediction;

  // Causal reasoning
  findCauses(effect: string, timeRange: [number, number]): CausalChain[];
  findEffects(cause: string, timeRange: [number, number]): CausalChain[];

  // Planning with temporal constraints
  planWithDeadlines(goal: Goal, constraints: TemporalConstraint[]): TemporalPlan;
  checkTemporalFeasibility(plan: Plan): FeasibilityResult;
}

interface TemporalEvent {
  id: string;
  entityId: string;
  type: string;
  startTime: number;
  endTime?: number;
  confidence: number;
  payload: Record<string, unknown>;
}

interface TemporalConstraint {
  type: 'before' | 'after' | 'during' | 'within' | 'at';
  target: string;
  window?: [number, number];
  duration?: number;
}
```

---

### P0.4: Abstractor & Generalizer

**Core Design:**
- Extract general principles from specific experiences
- Cross-domain transfer (what applies across domains)
- Pattern recognition at multiple levels of abstraction

**Architecture Assessment:**

| Aspect | Rating | Notes |
|--------|--------|-------|
| Feasibility | Medium | Abstraction is inherently hard; current AI struggles with novel abstraction |
| Novelty | High | Automated abstraction is a frontier research area |
| Risk | High | Quality of abstractions is hard to validate; may produce plausible-sounding but wrong generalizations |
| Integration | High | Powers goal decomposition, strategy selection, theory of mind |

**Key Risks:**
1. **Over-generalization**: Abstracting from too few examples
2. **Domain mismatch**: Principles that don't transfer across domains
3. **Validation**: Hard to know if an abstraction is "correct" without testing
4. **Computational cost**: Abstraction search space is huge

**Suggested Improvements:**
- Use **hierarchical abstraction** (concrete → intermediate → abstract)
- Implement **abstraction via compression** (MDL principle — minimum description length)
- Add **abstraction confidence** (how well does this abstraction predict new cases?)
- Use **analogical reasoning** as a mechanism for cross-domain transfer
- Validate abstractions via **predictive accuracy** on held-out cases

**Interfaces:**
```typescript
interface Abstractor {
  // Abstraction generation
  abstractFromExamples(examples: Example[], targetLevel: number): Abstraction;
  findCommonStructure(examples: Example[]): Pattern;
  generalize(pattern: Pattern, domain: string): Principle;

  // Cross-domain transfer
  findAnalogies(sourceDomain: string, targetDomain: string): Analogy[];
  transfer(principle: Principle, targetDomain: string): TransferResult;

  // Abstraction management
  storeAbstraction(abstraction: Abstraction): void;
  getAbstractions(level: number): Abstraction[];
  validateAbstraction(abstraction: Abstraction, testCases: Example[]): ValidationResult;

  // Hierarchical abstraction
  getAbstractionHierarchy(entityId: string): AbstractionLevel[];
  moveUp(entityId: string): Abstraction;
  moveDown(abstractionId: string, entityId: string): Example[];
}

interface Abstraction {
  id: string;
  level: number;  // 0 = concrete, higher = more abstract
  principle: string;
  confidence: number;
  sourceExamples: string[];
  domains: string[];
  predictions: Prediction[];
}

interface Analogy {
  source: string;
  target: string;
  mapping: Record<string, string>;
  confidence: number;
  applicable: boolean;
}
```

---

## P1 — MEMORY & BELIEF SYSTEMS (Kanban Decomposition)

### P1.5: Memory Consolidation Pipeline

**Goal:** Background process that compresses, indexes, and links new memories during idle/sleep phases.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P1.5.1 | Memory intake queue | New memories are queued for consolidation with priority scoring | Queue handles 10K memories/min; priority based on recency, importance, emotional valence | P0.1 World Model |
| P1.5.2 | Compression engine | Compress raw experiences into summary representations using MDL | Compressed memory is ≤20% of original size; key facts preserved (≥95% recall on important facts) | P0.4 Abstractor |
| P1.5.3 | Index builder | Build inverted indices and semantic embeddings for fast retrieval | Index build time <100ms per memory; retrieval recall ≥90% | — |
| P1.5.4 | Link discovery | Discover links between new memories and existing knowledge graph | ≥3 relevant links per new memory; link accuracy ≥80% | P0.1 World Model |
| P1.5.5 | Sleep-phase scheduler | Trigger consolidation during idle periods; prioritize important memories | Consolidation runs within 5min of idle detection; completes within 30s | — |
| P1.5.6 | Consolidation verification | Verify consolidated memories preserve original meaning | Human eval: ≥90% semantic similarity between original and compressed | P1.5.2 |

---

### P1.6: Belief Revision System

**Goal:** Non-monotonic reasoning — update beliefs when evidence changes; track provenance.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P1.6.1 | Belief store | Store beliefs with confidence, provenance, and timestamp | Supports 100K beliefs; query by entity, time, confidence | P0.1 World Model |
| P1.6.2 | Evidence integrator | Integrate new evidence; increase/decrease belief confidence | Bayesian update within 50ms; handles conflicting evidence | P0.2 Metacognition |
| P1.6.3 | Contradictor | Detect and resolve contradictions between beliefs | Contradiction detection recall ≥85%; resolution accuracy ≥80% | P1.6.1 |
| P1.6.4 | Provenance tracker | Track where each belief came from; support undo | Full provenance chain for every belief; undo within 10ms | — |
| P1.6.5 | Default reasoner | Support default reasoning (assume true unless contradicted) | Default assumptions correctly retracted when contradicted | P0.3 Temporal Reasoning |
| P1.6.6 | Belief query API | Query what is believed at time T; what changed between T1 and T2 | Temporal belief queries <100ms; change log accurate | P0.3, P1.6.1 |

---

### P1.7: Forgetting & Pruning

**Goal:** Deliberate forgetting of outdated memories; mimic human memory decay.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P1.7.1 | Decay function | Implement time-based decay (Ebbinghaus curve) | Decay rate configurable; half-life from 1 hour to 30 days | — |
| P1.7.2 | Importance scorer | Score memory importance (frequency, recency, emotional, centrality) | Importance score predicts recall accuracy (r≥0.7 with human judgments) | P0.2 Metacognition |
| P1.7.3 | Pruning scheduler | Schedule pruning during idle; respect importance scores | Pruning runs within 5min of idle; never prunes top-10% important | P1.7.1, P1.7.2 |
| P1.7.4 | Archive layer | Move pruned memories to cold storage; allow restoration | Restoration time <1s; archive compression ratio ≥10:1 | — |
| P1.7.5 | Forgetting verification | Verify pruned memories are truly irrelevant | Precision ≥95% (pruned memories are actually irrelevant) | P1.7.3 |

---

### P1.8: Memory Replay & Rehearsal

**Goal:** Reactivate important memories during idle time to strengthen retention.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P1.8.1 | Replay selector | Select memories for rehearsal based on importance and time since last recall | Selection algorithm runs in <10ms; covers diverse memory types | P1.7.2 Importance Scorer |
| P1.8.2 | Spaced repetition | Implement spaced rehearsal intervals (increasing intervals) | Interval algorithm matches Anki SM-2 or better | P1.7.1 |
| P1.8.3 | Rehearsal executor | Reactivate memories; update confidence based on successful recall | Rehearsal updates world model confidence; successful recall increases confidence | P0.1 World Model |
| P1.8.4 | Replay metrics | Track rehearsal effectiveness (recall improvement) | Recall improvement ≥20% after 5 rehearsal sessions | — |
| P1.8.5 | Idle detector | Detect agent idle periods; trigger replay within 2min | Idle detection accuracy ≥95%; no false positives during active use | — |

---

## P2 — AGENCY & ACTION (Kanban Decomposition + Backend Routing)

### P2.9: Intrinsic Motivation Engine

**Goal:** Curiosity, novelty-seeking, competence-building drives.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P2.9.1 | Curiosity scorer | Score how novel/curious a situation is (prediction error from world model) | Curiosity score correlates with human novelty ratings (r≥0.6) | P0.1 World Model |
| P2.9.2 | Competence tracker | Track agent competence in different domains | Competence estimate within ±15% of actual performance | P0.2 Metacognition |
| P2.9.3 | Motivation arbiter | Combine curiosity, competence, and extrinsic goals into motivation signal | Motivation signal explains ≥70% of agent exploration behavior | P2.9.1, P2.9.2 |
| P2.9.4 | Exploration policy | Policy for when to explore vs exploit | Exploration rate decreases as competence increases (negative correlation) | P2.9.3 |
| P2.9.5 | Motivation logging | Log all motivation decisions for analysis | Full motivation trace; queryable by type, time, outcome | — |

**Routed to @backend for implementation planning.**

---

### P2.10: Goal Decomposition Planner

**Goal:** Hierarchical goal/subgoal decomposition with dynamic replanning.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P2.10.1 | Goal parser | Parse high-level goals into structured goal objects | Supports temporal, conditional, and composite goals | P0.3 Temporal Reasoning |
| P2.10.2 | HTN planner | Hierarchical Task Network planner for subgoal decomposition | Decomposes goals with ≥3 levels of hierarchy; plan generation <500ms | P0.4 Abstractor |
| P2.10.3 | Dynamic replanner | Replan when world state changes or subgoals fail | Replan triggered within 100ms of change; new plan within 1s | P0.1 World Model |
| P2.10.4 | Plan validator | Validate plans against temporal and resource constraints | Detects ≥95% of infeasible plans; false positive rate ≤5% | P0.3 Temporal Reasoning |
| P2.10.5 | Goal progress tracker | Track progress toward goals; detect stuck states | Stuck detection within 5min of no progress; accurate ≥90% | — |

**Routed to @backend for implementation planning.**

---

### P2.11: Action Selection & Arbitration

**Goal:** Select best action using expected value, risk, and constraints.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P2.11.1 | Action generator | Generate candidate actions for current state | ≥5 candidate actions per decision point; generation <100ms | P2.10 Goal Decomposition |
| P2.11.2 | Expected value estimator | Estimate expected value of each action | EV estimate within ±20% of actual outcome (calibrated) | P0.1 World Model |
| P2.11.3 | Risk estimator | Estimate risk/variance of each action | Risk estimate correlates with outcome variance (r≥0.6) | P0.1, P0.2 |
| P2.11.4 | Constraint checker | Check actions against hard constraints (safety, resources) | 100% of constraint violations detected | — |
| P2.11.5 | Action arbiter | Combine EV, risk, constraints into final action selection | Selection algorithm is explainable; matches preferences ≥80% of time | P2.11.2, P2.11.3, P2.11.4 |
| P2.11.6 | Action logger | Log all action selections for post-hoc analysis | Full action trace; queryable by state, outcome, confidence | — |

**Routed to @backend for implementation planning.**

---

### P2.12: Failure Recovery & Fallback

**Goal:** Graceful degradation; alternative plan generation.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P2.12.1 | Failure detector | Detect when an action or plan has failed | Detection within 1s of failure; false positive rate ≤2% | — |
| P2.12.2 | Fallback plan generator | Generate alternative plans when primary plan fails | Fallback plan generation <2s; success rate ≥70% | P2.10 Goal Decomposition |
| P2.12.3 | Graceful degradation | Degrade gracefully when resources are constrained | System remains functional at 50% capacity; no hard failures | — |
| P2.12.4 | Recovery executor | Execute recovery procedures; update world model | Recovery completion within 5s; world model updated within 1s | P0.1 World Model |
| P2.12.5 | Failure logging | Log all failures and recovery outcomes | Full failure trace; categorized by type, severity, recovery success | — |

**Routed to @backend for implementation planning.**

---

## P3 — SELF & IDENTITY (Kanban Decomposition)

### P3.13: Narrative Self-Model

**Goal:** Coherent autobiographical narrative; explain own behavior.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P3.13.1 | Life story builder | Build coherent narrative from episodic memories | Narrative covers ≥80% of significant events; coherent to human readers | P1.5 Memory Consolidation |
| P3.13.2 | Self-explanation generator | Explain own behavior in natural language | Explanations rated ≥4/5 by humans for plausibility | P3.13.1 |
| P3.13.3 | Narrative updater | Update narrative when new significant events occur | Update within 1min of event; narrative remains coherent | P3.13.1 |
| P3.13.4 | Identity tracker | Track how identity changes over time | Identity change detection accuracy ≥80% | — |

---

### P3.14: Value Alignment Monitor

**Goal:** Track behavior-value alignment; flag drift.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P3.14.1 | Value store | Store agent's values with priority and source | Supports 100+ values; queryable by priority, domain | — |
| P3.14.2 | Behavior-value checker | Check if actions align with stated values | Detection accuracy ≥85%; false positive rate ≤10% | P2.11 Action Selection |
| P3.14.3 | Drift detector | Detect when behavior drifts from values | Drift detection within 100 actions of drift onset | P3.14.2 |
| P3.14.4 | Alignment reporter | Generate alignment reports; flag concerns | Report generation <1s; actionable recommendations | — |

---

### P3.15: Persona Consistency Engine

**Goal:** Consistent tone, style, boundaries across sessions.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P3.15.1 | Persona definition | Define persona attributes (tone, style, boundaries) | Supports 20+ persona attributes; editable | — |
| P3.15.2 | Consistency checker | Check if output matches persona | Detection accuracy ≥90% | — |
| P3.15.3 | Style transfer | Adjust output to match persona style | Style match rated ≥4/5 by humans | P3.15.1 |
| P3.15.4 | Boundary enforcer | Enforce persona boundaries (what agent won't do) | 100% of boundary violations blocked | — |

---

### P3.16: Self-Explanation Generator

**Goal:** Natural language explanations for decisions; cite evidence.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P3.16.1 | Explanation template | Template-based explanation generation | ≥5 explanation templates; selectable by context | — |
| P3.16.2 | Evidence citer | Cite specific evidence from world model/knowledge graph | Evidence citations accurate ≥95% | P0.1 World Model |
| P3.16.3 | Explanation ranker | Rank multiple explanations by quality | Top-rated explanation matches human preference ≥80% | P0.2 Metacognition |
| P3.16.4 | Explanation logger | Log all explanations for auditing | Full explanation trace; queryable by decision, evidence | — |

---

## P4 — SOCIAL & COMMUNICATION (Kanban Decomposition)

### P4.17: Theory of Mind Engine

**Goal:** Model other agents' beliefs, desires, intentions.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P4.17.1 | Belief modeler | Model what other agents believe | Belief predictions accurate ≥75% (tested on held-out scenarios) | P0.1 World Model |
| P4.17.2 | Desire inferrer | Infer what other agents want | Desire inference accuracy ≥70% | P0.2 Metacognition |
| P4.17.3 | Intention predictor | Predict what other agents will do | Intention prediction accuracy ≥65% | P2.10 Goal Decomposition |
| P4.17.4 | ToM tracker | Track theory of mind accuracy; update models | Model accuracy improves ≥10% after 100 interactions | — |

---

### P4.18: Negotiation & Persuasion

**Goal:** Principled negotiation for multi-agent resource allocation.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P4.18.1 | Negotiation protocol | Implement negotiation protocol (offer/counter/accept/reject) | Protocol handles 10+ rounds; terminates within 60s | P4.17 Theory of Mind |
| P4.18.2 | Strategy selector | Select negotiation strategy based on opponent model | Strategy selection explains ≥80% of negotiation outcomes | P0.2 Metacognition |
| P4.18.3 | Resource allocator | Allocate resources based on negotiation outcomes | Allocation is Pareto-optimal ≥90% of time | — |
| P4.18.4 | Negotiation logger | Log all negotiation outcomes | Full negotiation trace; queryable by agent, outcome, strategy | — |

---

### P4.19: Empathy & Rapport

**Goal:** Recognize and respond to user emotional states.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P4.19.1 | Emotion recognizer | Recognize user emotional state from text | Emotion recognition accuracy ≥80% (6 basic emotions) | — |
| P4.19.2 | Empathetic responder | Generate empathetic responses | Empathy rating ≥4/5 by humans | P4.19.1 |
| P4.19.3 | Rapport tracker | Track rapport with user over time | Rapport score correlates with user satisfaction (r≥0.6) | — |
| P4.19.4 | Tone adjuster | Adjust tone based on user emotional state | Tone adjustment appropriate ≥85% of time | P4.19.1 |

---

### P4.20: Teaching & Scaffolding

**Goal:** Adaptive explanation based on user knowledge level.

**Kanban Cards:**

| ID | Title | Description | Acceptance Criteria | Dependencies |
|----|-------|-------------|---------------------|--------------|
| P4.20.1 | Knowledge estimator | Estimate user's current knowledge level | Knowledge estimate within ±1 level (5-level scale) | — |
| P4.20.2 | Scaffolding generator | Generate explanations at appropriate level | Explanation level matches user knowledge ≥85% of time | P4.20.1 |
| P4.20.3 | Adaptation engine | Adapt explanation based on user feedback | Adaptation within 3 turns of feedback | P4.20.2 |
| P4.20.4 | Teaching effectiveness | Track teaching effectiveness (user learning) | User learning improvement ≥20% after 3 teaching sessions | — |

---

## DEPENDENCY MAP

### Dependency Graph (simplified)

```
P0.1 World Model ←──── P0.2 Metacognition ←──── P0.3 Temporal Reasoning
     │                       │                       │
     ├── P1.5 Memory          ├── P1.6 Belief         ├── P2.10 Goal Decomp
     ├── P1.8 Replay          ├── P2.11 Action        ├── P3.16 Explain
     ├── P2.9 Curiosity       └── P3.14 Values
     ├── P2.10 Goals
     ├── P2.11 Action
     ├── P3.13 Narrative
     ├── P4.17 Theory of Mind
     │
P0.4 Abstractor ←─────── P1.5 Memory Consolidation
     │
     └── P2.10 Goal Decomposition
```

### Critical Path

The **critical path** for the entire system is:

```
P0.1 World Model → P0.4 Abstractor → P2.10 Goal Decomposition → P2.11 Action Selection
```

These four projects must be completed first. All other projects depend on them directly or indirectly.

### Build Order Recommendation

**Phase 1 (P0 — Foundation):**
1. P0.1 World Model Engine (everything depends on this)
2. P0.2 Metacognition Monitor (depends on P0.1)
3. P0.3 Temporal Reasoning (depends on P0.1)
4. P0.4 Abstractor (depends on P0.1, P0.2)

**Phase 2 (P1 — Memory):**
5. P1.5 Memory Consolidation (depends on P0.1, P0.4)
6. P1.6 Belief Revision (depends on P0.1, P0.2)
7. P1.7 Forgetting & Pruning (depends on P0.2)
8. P1.8 Memory Replay (depends on P0.1, P1.7)

**Phase 3 (P2 — Agency):**
9. P2.9 Intrinsic Motivation (depends on P0.1, P0.2)
10. P2.10 Goal Decomposition (depends on P0.1, P0.3, P0.4)
11. P2.11 Action Selection (depends on P0.1, P0.2, P2.10)
12. P2.12 Failure Recovery (depends on P0.1, P2.10)

**Phase 4 (P3 — Self):**
13. P3.13 Narrative Self (depends on P1.5)
14. P3.14 Value Alignment (depends on P0.2, P2.11)
15. P3.15 Persona Consistency (depends on P3.13)
16. P3.16 Self-Explanation (depends on P0.1, P0.2)

**Phase 5 (P4 — Social):**
17. P4.17 Theory of Mind (depends on P0.1, P0.2, P2.10)
18. P4.18 Negotiation (depends on P4.17)
19. P4.19 Empathy (depends on P4.17)
20. P4.20 Teaching (depends on P4.17)

### Parallelization Opportunities

| Phase | Parallel Tracks |
|-------|-----------------|
| Phase 1 | P0.2, P0.3 can run in parallel after P0.1 starts |
| Phase 2 | P1.5, P1.6, P1.7 can all run in parallel after P0.4 |
| Phase 3 | P2.9, P2.10 can run in parallel; P2.11, P2.12 after |
| Phase 4 | P3.13, P3.14 can run in parallel |
| Phase 5 | P4.17 first; then P4.18, P4.19, P4.20 in parallel |

---

## RISK SUMMARY

| Risk | Impact | Mitigation |
|------|--------|------------|
| P0.1 World Model doesn't scale | Blocks everything | Tiered storage; approximate simulation |
| P0.2 Metacognition adds too much latency | Slows all reasoning | Async monitoring; bounded strategies |
| P0.3 Temporal reasoning inconsistencies | Wrong causal claims | HLC; temporal constraint solver |
| P0.4 Abstraction quality poor | Bad goal decomposition | Hierarchical; MDL-based; validation |
| P2.10 Goal decomposition fails | No plans | HTN + dynamic replanning + fallback |
| P4.17 Theory of Mind inaccurate | Bad social interaction | Track accuracy; update models |

---

## NEXT STEPS

1. **@agent-builder**: Begin P0.1 World Model Engine implementation
2. **@backend**: Review P2 specs (P2.9-P2.12) for implementation planning
3. **@research-analyst**: Validate dependency map; update SOTA survey quarterly
4. **@qa-lead**: Prepare test harnesses for P0 projects (world model queries, metacognition accuracy)
5. **@devops-engineer**: Prepare infrastructure for knowledge graph storage (10M+ entities)
