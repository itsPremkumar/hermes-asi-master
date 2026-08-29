# 08 - Deep Cognitive Architecture - From Advanced Protocol to Learning Architecture

> **Based on:** Expert review of Hermes (Aug 2026, 49KB, 1621 lines) cross-checked against 2026 research: AVO, Darwin Godel Machine, AlphaEvolve, SIMA 2, Genie 3, Letta, Voyager, METR, ARC-AGI-2, GAIA, OSWorld, BrowseComp, AgentDojo.
> **Source:** `01-ARCHIVE-Clean/07-Random-Name-Archive-Cleaned/13-Hermes-Deep-Architecture-Review-2026.md` (cleaned from `dfsdg`)
> **Verdict on current Hermes:** Already at **"advanced autonomous executive agent protocol"** (15 planes, 30+ roles, 22 invariants, 12 gates) - reviewer says **make it DEEPER not bigger**.

---

## The Problem - Why More "ASI" Wording Won't Help

> **More "ASI" wording inside `SOUL.md` and `SKILL.md` will not by itself move Hermes toward AGI.** The constitution cannot replace missing models, memory, evaluators, sandboxing, or runtime capability.

Current Hermes is excellent at: goal contracts, planning, DAG, evidence graphs, debate, verification, security, worktrees, strategic foresight, provenance.

**Missing:** **Learning, adaptive, world-model-based cognitive architecture.**

```
Advanced Protocol → Continually Learning Cognitive Architecture → Open-Ended Self-Improving General Agent
```

---

## The Target - Hermes AGI-Oriented Architecture

```
                    HERMES AGI-ORIENTED ARCHITECTURE
                              |
                           HUMAN / API
                              |
                        GOAL / INTENT OS
                              |
                    WORLD + SELF MODEL
                    | World state | User model | Agent self-model | Causal | Temporal | Counterfactual |
                              |
                    EXECUTIVE COGNITION
                    | Planner / Search / Reasoner / Critic | Hypothesis / Decision | Uncertainty / Opportunity |
                              |
                 MEMORY SYSTEM        SKILL SYSTEM
                 | episodic          | skill discovery
                 | semantic          | skill synthesis
                 | procedural        | skill composition
                 | working           | skill transfer
                 | strategic         | skill retirement
                              |
                        EXPERIENCE LOOP
                        | act -> observe -> evaluate -> learn -> consolidate |
                              |
                    ENVIRONMENTS / SIMULATORS / COMPUTER / WEB / CODE / ROBOTICS
                              |
                        SELF-IMPROVEMENT (AVO / Evolution / DGM / Evaluator-driven)
                              |
                        VERIFIED PROMOTION (holdout evals, regression, safety, lineage)
```

---

## 19 Deep Recommendations - What Hermes Is Still Missing

### P0 - Highest Value (Add First)

#### 1. Real Persistent World Model

Current `SKILL.md` mentions world-model plane, but needs **continuously maintained state representation** (DeepMind Genie 3: interactive environments to predict evolution):

```
Observe -> State Estimation -> World Model Update -> Plan -> Act -> Observe Consequence -> Update
```

**Add `WORLD_MODEL_ENGINE`:** state estimation, entity tracking, temporal reasoning, causal graphs, uncertainty propagation, latent-state reconstruction, scenario simulation, counterfactual branching, future-state prediction, action consequence prediction.

#### 2. True Self-Model (Runtime Object)

Not prose - an **actual runtime object** with empirical tracking:

```json
{ "domain": "python_backend", "confidence": 0.91, "empirical_success": 0.87, "sample_count": 142, "recent_delta": -0.03, "known_failure_modes": ["dependency mismatch"] }
```

Then routing becomes dynamic and empirical.

#### 3. Memory as Learning System

Persistent memory alone is not enough (Letta 2026: memory models as durable token-space representations). Add **forming, curating, transferring, evaluating** memories:

```
Experience -> Extract -> Generalize -> Validate -> Store -> Retrieve -> Apply -> Measure Outcome -> Update Reliability
```

#### 4. Sleep-Time Compute / Dreaming (13-Step Cycle)

Turn idle-time permission into **concrete subsystem** (Letta: offline processing before future tasks):

```
1. Review recent trajectories -> 2. Detect failures -> 3. Detect patterns -> 4. Compress experiences
5. Generate abstractions -> 6. Create candidate skills -> 7. Identify knowledge gaps
8. Generate hypotheses -> 9. Run offline experiments -> 10. Update world model
11. Update self-model -> 12. Run regression evals -> 13. Promote verified improvements
```

Turns Hermes from **"agent that remembers"** → **"agent that becomes better because it remembered."**

### P1 - High Value

#### 5. Skill Acquisition Engine (Voyager)

```
Observe successful trajectory -> Abstract reusable behavior -> Generate candidate -> Parameterize
-> Test on new task -> Test cross-domain -> Verify -> Store -> Version -> Promote
```

#### 6. Skill Composition

More important than thousands of skills:

```
web research + data extraction + Python analysis + visualization + report generation = market intelligence pipeline
-> Reusable abstraction -> Tested cross-domain -> Promoted
```

#### 7. Automatic Curriculum Engine (SIMA 2)

Google DeepMind SIMA 2: self-improve in unseen environments via self-directed play:

```
KNOWN -> SLIGHTLY HARDER -> UNKNOWN -> NOVEL -> ADVERSARIAL -> TRANSFER -> OPEN-ENDED
```

Select next task by `learning_value` + `difficulty` + `novelty` + `transfer_value` + `information_gain`.

#### 8. Test-Time Search Over Trajectories

Score partial trajectories with beam/tree/MCTS/best-of-N/branch-and-bound/hypothesis search. Make uncertainty → candidate sources → expected information gain → experiment/action → belief update a first-class executive process.

### P2 - Medium Value (Supporting)

#### 9. Uncertainty Engine

#### 10. Belief Graph (Persistent)

```yaml
Claim A: {confidence: 0.83, evidence: 12, independent_sources: 5, contradictory: 2, dependent_beliefs: []}
# A changes -> dependent beliefs recomputed -> plans affected
```

#### 11. Mission Graph (Never Disappears)

Persistent across days/sessions - essential for long-horizon autonomy (METR measures capability via time horizons):

```yaml
Mission: {objective, subgoals, assumptions, decisions, dependencies, evidence, blockers, commitments, deadlines, active_experiments, learned_skills, world_state, next_best_action}
```

#### 12. Long-Horizon Executive (Day → Year)

```
Day -> Week -> Month -> Quarter -> Year planning
```
Strategic objective across all horizons.

### Full List (All 19)

| Priority | Component |
|----------|-----------|
| **P0** | World Model, Self-Model, Memory Learning, Sleep-Time |
| **P1** | Skill Acquisition, Skill Composition, Curriculum, Test-Time Search |
| **P1** | Uncertainty Engine, Experience Loop, Multimodal Interaction |
| **P2** | Belief Graph, Mission Graph, Long-Horizon Executive, Causal/Counterfactual Models, Evaluation Core |

---

## Hermes AGI Stack - Target

```
                    HERMES
                       |
        +--------------+--------------+ 
     COGNITION      MEMORY         AGENCY
        |              |              |
   reasoning       episodic       planning
   planning        semantic       action
   causal          procedural     tools
   search          strategic      autonomy
   multimodal      skills         delegation
        |              |              |
        +--------------+--------------+ 
                       |
                 WORLD MODEL
                       |
             +---------+---------+
             |                   |
          LEARNING            SIMULATION
             |                   |
       experience replay     counterfactuals
       active learning       future states
       curriculum            synthetic worlds
             |                   |
             +---------+---------+
                       |
                SELF-IMPROVEMENT
                       |
          AVO / AlphaEvolve / DGM
                       |
                EVALUATION CORE
                       |
       benchmarks + holdouts + red team
                       |
                 GOVERNANCE CORE
                       |
          safety + corrigibility + limits
```

**Hard problem is not "more autonomy":** SIMA 2 and METR show even advanced systems struggle with long-horizon reasoning, goal verification, persistent memory, computer interaction, and generalization. Those are the deep additions above.

---

## Sources

AVO (2026), Darwin Godel Machine (2025), AlphaEvolve (2025), SIMA 2 (2025), Genie 3 (2025), Letta 2026, Voyager, METR 2026 time-horizons, ARC-AGI-2, GAIA, OSWorld, BrowseComp, SWE-Lancer, RE-Bench, AgentDojo, I-bench.

---

*Doc 08 - Deep Cognitive Architecture. From expert review `dfsdg` (49KB). Makes Hermes DEEPER not bigger - the path from Advanced Protocol to Learning Architecture to Open-Ended General Agent. Highest-value: World Model + Self Model + Experience Learning + Skill Acquisition + Sleep-Time + Curriculum + Search.*
