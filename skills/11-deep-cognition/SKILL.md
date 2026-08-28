---
name: hermes-deep-cognition
description: Hermes Deep Cognitive Architecture - World Model, Self-Model, Memory Learning, Sleep-Time Compute, Skill Acquisition and Composition, Curriculum, Test-Time Search. Makes Hermes DEEPER not bigger (from 2026 expert review).
version: "1.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, deep-cognition, world-model, self-model, sleep-time, skill-acquisition, curriculum, agi]
    category: hermes-advanced
---

# SKILL 11 â€" DEEP COGNITIVE ARCHITECTURE

> **Load this skill when:** Hermes needs to go DEEPER not bigger â€" world-model-based, learning, adaptive, AGI-oriented cognition.
> **Based on:** Expert review of Hermes (Aug 2026) cross-checked against 2026 research: AVO, DGM, AlphaEvolve, SIMA 2, Genie 3, Letta, Voyager, METR.
> **Pairs with:** `06-memory-world` (memory planes) + `02-planning` (search) + `05-safety-evaluation` (evolution)
> **Hermes Deep Law:** *More "ASI" wording does not make Hermes AGI. Deeper architecture does.*

---

## 0. PURPOSE â€" WHY DEEPER NOT BIGGER

Your Hermes already has **15 planes, 30+ roles, 22 invariants, 12 gates** â€" it is already "advanced autonomous executive agent protocol."

The next jump is **continually learning cognitive architecture**:

```
Advanced Protocol â†' Learning Architecture â†' Open-Ended Self-Improving General Agent
```

**The 19 deep recommendations** (integrated from `01-ARCHIVE-Clean/07-Random-Name-Archive-Cleaned/13-Hermes-Deep-Architecture-Review-2026.md`):

| # | Deep Capability | Research Source |
|---|-----------------|-----------------|
| 1 | Real Persistent World Model | DeepMind Genie 3 |
| 2 | True Self-Model (runtime capability tracking) | Hermes calibration |
| 3 | Memory as Learning System (experience replay) | Letta 2026 |
| 4 | Sleep-Time Compute / Dreaming (13-step cycle) | Letta |
| 5 | Skill Acquisition Engine (auto-discovery) | Voyager |
| 6 | Skill Composition (A+B+C = new composite) | Voyager |
| 7 | Automatic Curriculum Engine | SIMA 2 (DeepMind) |
| 8 | Test-Time Search Over Trajectories | General |
| 9 | Uncertainty Engine | Hermes VOI |
| 10 | Belief Graph (persistent) | Hermes epistemics |
| 11 | Mission Graph (never disappears) | Hermes DAG |
| 12 | Long-Horizon Executive (Dayâ†'Year) | METR |
| 13 | Experience Loop (actâ†'observeâ†'evaluateâ†'learnâ†'consolidate) | General |
| 14 | Multimodal Environment Interaction | SIMA 2, Genie 3 |
| 15 | Independent Evaluation + Holdout | Hermes evaluation |
| 16 | Safe Open-Ended Self-Improvement | DGM, AVO |
| 17 | Opportunity Engine | Hermes strategic |
| 18 | Counterfactual Model | Hermes counterfactual |
| 19 | Causal Model | Hermes causal |

---

## 1. WORLD MODEL ENGINE â€" REAL PERSISTENT STATE

Hermes `SKILL.md` mentions world-model plane, but it must be a **continuously maintained state representation**:

```
WORLD_STATE
  â"œâ"€â"€ entities
  â"œâ"€â"€ relationships
  â"œâ"€â"€ properties
  â"œâ"€â"€ events
  â"œâ"€â"€ actions
  â"œâ"€â"€ dependencies
  â"œâ"€â"€ resources
  â"œâ"€â"€ constraints
  â"œâ"€â"€ beliefs
  â"œâ"€â"€ uncertainty
  â"œâ"€â"€ causal relationships
  â"œâ"€â"€ temporal state
  â"œâ"€â"€ external changes
  â"œâ"€â"€ forecasts
  â""â"€â"€ counterfactual branches
```

**Every action updates the world model:**

```
Observe â†' State Estimation â†' World Model Update â†' Plan â†' Act â†' Observe Consequence â†' Update World Model
```

**Capabilities (from review):**

- State estimation, entity tracking, temporal reasoning, causal graphs, uncertainty propagation
- Latent-state reconstruction, scenario simulation, counterfactual branching
- Future-state prediction, action consequence prediction, model disagreement detection

**Hermes World Model Engine:**

```yaml
world_model_engine:
  state_estimation: true
  entity_tracking: true
  temporal_reasoning: true      # past â†' present â†' 90-day future
  causal_graph: true
  uncertainty_propagation: true
  counterfactual_branching: true
  scenario_simulation: true     # Genie 3-style interactive environments
```

---

## 2. TRUE SELF-MODEL â€" RUNTIME CAPABILITY TRACKING

Hermes should have an **actual runtime object**, not just metacognition prose:

```yaml
self_model:
  current_capabilities:
    domain: "python_backend"
    confidence: 0.91
    empirical_success: 0.87      # Measured, not claimed
    sample_count: 142
    recent_delta: -0.03
    known_failure_modes: ["dependency-version mismatch", "async race conditions"]
  skill_reliability:
    skill_name: 0.88
  model_reliability: 0.85
  tool_reliability:
    web_search: 0.92
    browser: 0.88
  domain_expertise:
    coding: 0.89
    research: 0.91
  calibration_history: []
  failure_history: []
  recent_regressions: []
  current_context_health: 0.95
  uncertainty_profile: {}
  cognitive_load: 0.6
  available_compute: {}
  current_objectives: []
  risk_exposure: {}
```

**Then routing becomes dynamic:** Instead of "I am good at coding," Hermes has empirical success rates and routes accordingly.

---

## 3. MEMORY AS LEARNING SYSTEM

Current Hermes memory is strong conceptually, but **persistent memory alone is not enough**. Agents need **forming, curating, transferring, evaluating** memories (Letta 2026: memory models as durable token-space representations).

```yaml
memory_system:
  working: {}
  episodic: {}
  semantic: {}
  procedural: {}
  skill: {}
  spatial: {}
  temporal: {}
  user_model: {}
  project: {}
  strategic: {}
  failure: {}
  contradiction: {}
  causal: {}
  experience_replay: {}        # Critical
  provenance: {}
```

**Experience Loop:**

```
Experience â†' Extract â†' Generalize â†' Validate â†' Store â†' Retrieve â†' Apply â†' Measure Outcome â†' Update Memory Reliability
```

**Add `memory learning`, not just `memory retrieval`.**

---

## 4. SLEEP-TIME COMPUTE / DREAMING â€" 13-STEP CYCLE

Hermes `SOUL.md` already permits idle-time work, but make it a **concrete subsystem**:

```
SLEEP CYCLE (Letta-aligned)

1. Review recent trajectories
2. Detect failures
3. Detect repeated patterns
4. Compress experiences
5. Generate abstractions
6. Create candidate skills
7. Identify knowledge gaps
8. Generate hypotheses
9. Run offline experiments
10. Update world model
11. Update self-model
12. Run regression evals
13. Promote verified improvements
```

Turns Hermes from **"agent that remembers"** â†' **"agent that becomes better because it remembered"** (Letta: sleep-time computation as offline processing before future tasks, continual learning).

**Hermes Sleep Config (in config.yaml):**

```yaml
sleep:
  enabled: true
  interval_hours: 24
  max_duration_minutes: 30
  tasks: [trajectory_review, pattern_mining, skill_synthesis, regression_eval]
```

---

## 5. SKILL ACQUISITION ENGINE â€" AUTO-DISCOVERY

AGI-oriented Hermes should **discover new reusable skills automatically** (Voyager: automatic curriculum + executable skill library + iterative feedback):

```
Observe successful trajectory
    â†"
Abstract reusable behavior
    â†"
Generate skill candidate
    â†"
Parameterize
    â†"
Test on new task
    â†"
Test cross-domain
    â†"
Verify
    â†"
Store â†' Version â†' Promote
```

Each skill:

```yaml
skill:
  name: ""
  purpose: ""
  preconditions: []
  inputs: []
  outputs: []
  procedure: []
  tools: []
  expected_success: 0.0
  failure_modes: []
  confidence: 0.0
  domains: []
  dependencies: []
  composability: []
  provenance: ""
  verification: ""
  last_used: ""
  last_validated: ""
```

---

## 6. SKILL COMPOSITION â€" MORE IMPORTANT THAN MORE SKILLS

Having thousands of skills is less important than **composing** them:

```
Skill A (web research)
+ Skill B (data extraction)
+ Skill C (Python analysis)
+ Skill D (visualization)
+ Skill E (report generation)
= Composite: Market Intelligence Pipeline
â†' Reusable abstraction â†' Tested cross-domain â†' Promoted
```

This is **more AGI-like** than simply spawning more agents.

---

## 7. AUTOMATIC CURRICULUM ENGINE â€" SIMA 2

Google DeepMind SIMA 2: self-improve in unseen environments through self-directed play and reuse experience.

```yaml
curriculum_engine:
  levels: [KNOWN, SLIGHTLY_HARDER, UNKNOWN, NOVEL, ADVERSARIAL, TRANSFER, OPEN_ENDED]
  selection_criteria:
    learning_value: 0.0
    difficulty: 0.0
    novelty: 0.0
    transfer_value: 0.0
    information_gain: 0.0
```

Automatically select next task based on learning value â€" **continual generalization**.

---

## 8. TEST-TIME SEARCH OVER TRAJECTORIES

Your planning has multiple plans and debate, but make search **explicit**:

```
State
  â"œâ"€â"€ Action A â†' A1, A2
  â"œâ"€â"€ Action B â†' B1, B2
  â""â"€â"€ Action C â†' C1, C2
```

Score partial trajectories. Add:

- Beam search, tree search, MCTS-style, best-of-N, branch-and-bound, hypothesis search, plan refinement, evaluator-guided search

**Key:** Uncertainty â†' candidate information sources â†' expected information gain â†' experiment/search/action â†' belief update (make VOI a first-class executive process).

---

## 9. BELIEF GRAPH â€" PERSISTENT

Current confidence discipline is good, but add **persistent belief state**:

```yaml
belief_graph:
  claim_A:
    confidence: 0.83
    evidence: 12
    independent_sources: 5
    contradictory_evidence: 2
    freshness: ""
    causal_support: ""
    last_validated: ""
    dependent_beliefs: []
```

If evidence changes: `A changes â†' dependent beliefs recomputed â†' plans affected â†' future actions reprioritized`. More powerful than storing a confidence number.

---

## 10. MISSION GRAPH â€" NEVER DISAPPEARS

Your DAG is useful, but make it **persistent across days and sessions**:

```yaml
mission_graph:
  objective: ""
  subgoals: []
  assumptions: []
  decisions: []
  dependencies: []
  evidence: []
  blockers: []
  commitments: []
  deadlines: []
  active_experiments: []
  learned_skills: []
  current_world_state: {}
  next_best_action: ""
```

When Hermes stops and restarts, it reconstructs the mission from this graph â€" **essential for long-horizon autonomy** (METR measures agent capability via task-completion time horizons).

---

## 11. LONG-HORIZON EXECUTIVE

AGI needs **Day â†' Week â†' Month â†' Quarter â†' Year** planning:

```yaml
strategic_objective:
  day: ""
  week: ""
  month: ""
  quarter: ""
  year: ""
```

---

## 12. HERMES AGI STACK â€" TARGET ARCHITECTURE

```
                    HERMES
                       â"‚
        +--------------+--------------+ 
     COGNITION      MEMORY         AGENCY
        â"‚              â"‚              â"‚
   reasoning       episodic       planning
   planning        semantic       action
   causal          procedural     tools
   search          strategic      autonomy
   multimodal      skills         delegation
        â"‚              â"‚              â"‚
        +--------------+--------------+ 
                       â"‚
                 WORLD MODEL
                       â"‚
             +---------+---------+
             â"‚                   â"‚
          LEARNING            SIMULATION
             â"‚                   â"‚
       experience replay     counterfactuals
       active learning       future states
       curriculum            synthetic worlds
             â"‚                   â"‚
             +---------+---------+
                       â"‚
                SELF-IMPROVEMENT
                       â"‚
          AVO / AlphaEvolve / DGM
                       â"‚
                EVALUATION CORE
                       â"‚
       benchmarks + holdouts + red team
                       â"‚
                 GOVERNANCE CORE
                       â"‚
          safety + corrigibility + limits
```

---

## PRIORITY â€" HERMES AGI STACK

| Priority | Component | Purpose |
|----------|-----------|---------|
| **P0** | World Model | Persistent structured world knowledge |
| **P0** | Self-Model | Empirical capability tracking |
| **P0** | Memory Learning | Experience â†' abstraction â†' skill |
| **P0** | Sleep-Time Compute | Offline improvement |
| **P1** | Skill Acquisition | Autonomous skill growth |
| **P1** | Skill Composition | Composite intelligence |
| **P1** | Curriculum Engine | Autonomous generalization |
| **P1** | Test-Time Search | Trajectory optimization |
| **P2** | Belief Graph | Persistent uncertainty |
| **P2** | Mission Graph | Long-horizon autonomy |
| **P2** | Long-Horizon Executive | Dayâ†'Year planning |

**Bottom line (from review):** Your current Hermes is **"advanced autonomous executive agent protocol."** Next jump is **"continually learning cognitive architecture."** The jump after is **"open-ended, empirically evaluated, self-improving general agent."** Highest-value additions: **World Model + Self Model + Experience Learning + Skill Acquisition + Sleep-Time + Curriculum + Search.**

*Skill 11 â€" Hermes Deep Cognition. Makes Hermes DEEPER not bigger. From 19 expert recommendations (Genie 3, Letta, Voyager, SIMA 2, AVO, DGM). Integrated from dfsdg review.*
