# 03 — Operating Loop

## Canonical Mission Lifecycle

The universal operating loop is the single most important diagram in the system. Every mission, regardless of domain, flows through it.

```
                         ┌─────────────┐
                         │   MISSION   │  Raw human objective arrives
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │  INTERPRET  │  Intent, desired outcome, value
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │   COMPILE   │  Mission object, acceptance criteria, constraints
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │   OBSERVE   │  Read environment, files, state, tools
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │ MODEL WORLD │  Build or update world model
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │   RETRIEVE  │  Relevant memory, skills, failure lessons
                         │   MEMORY    │
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │  RESEARCH   │  Four-pass evidence synthesis
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │  GENERATE   │  Plan portfolio: Conservative / Balanced /
                         │   PLANS     │  Aggressive / Experimental
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │ SELECT PLAN │  Score by expected value, risk, evidence, cost
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │  DECOMPOSE  │  Task graph (DAG) with dependencies
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │  DELEGATE   │  Agent factory — only when benefit > cost
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │   EXECUTE   │  Isolated, reversible units: inspect → change → test
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │   OBSERVE   │  What actually happened?
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │   VERIFY    │  Independent checks against acceptance criteria
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │  EVALUATE   │  Score, compare to baseline, gate decisions
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │UPDATE WORLD │  Transitions, confidence, causal updates
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │    LEARN    │  Reflection → lesson → memory/skill update
                         └──────┬──────┘
                                ▼
                         ┌─────────────┐
                         │ CHECKPOINT  │  Durable snapshot — survives crashes
                         └──────┬──────┘
                                ▼
              ┌─────────────────────────────────┐
              │ CONTINUE / REPLAN / RECOVER /   │
              │      ESCALATE / COMPLETE        │
              └─────────────────────────────────┘
```

### What This Loop Is Not

```
think → act → answer    ←  NEVER for complex missions
```

That linear pattern has no memory, no verification, no recovery, and no learning. It optimizes for fluency, not outcomes. The canonical loop optimizes for **verified state change survived by evidence**.

## AGX Variant of the Same Loop

The AGX harness expresses the identical lifecycle with slightly different phase names:

```
OBJECTIVE → SPECIFICATION → RECON → RESEARCH → PLAN → HYPOTHESES
→ VERIFY → EXECUTE → TEST → CRITIQUE → REPAIR → EVOLVE → VALIDATE → DELIVER → LEARN
```

| Canonical | AGX | Emphasis |
|-----------|-----|----------|
| COMPILE | SPECIFICATION | Machine-readable contract |
| MODEL WORLD + RETRIEVE MEMORY | RECON | Context gathering before planning |
| GENERATE PLANS + SELECT PLAN | PLAN + HYPOTHESES | Competing approaches scored |
| DELEGATE + EXECUTE | EXECUTE | Parallel specialist work |
| VERIFY + EVALUATE | TEST + CRITIQUE | Layered checks and adversarial review |
| RECOVER / REPLAN | REPAIR | Structured failure taxonomy |
| LEARN + EVOLVE | EVOLVE + VALIDATE | Candidate lineage and promotion gates |

Both express the same closed loop. The canonical form is used in SKILL.md; the AGX form is preserved in `reference/AGX-Harness-Guide.md:1`.

## Master Executive Loop (Detailed Scheduler View)

For continuously operating deployments:

```
BOOT → LOAD IDENTITY / POLICY / CAPABILITIES → LOAD PERSISTENT STATE
→ RECONCILE WORLD STATE → READ MISSION QUEUE → SELECT HIGHEST-VALUE AUTHORIZED OBJECTIVE
→ COMPILE INTENT INTO SUCCESS CRITERIA → ASSESS NOVELTY / RISK / UNCERTAINTY
→ SELECT COGNITIVE MODE → RETRIEVE RELEVANT MEMORY → BUILD / UPDATE WORLD MODEL
→ GENERATE PLAN(S) → CHOOSE PLAN → BUILD TASK GRAPH → ALLOCATE RESOURCES
→ SPAWN SPECIALISTS WHEN JUSTIFIED → EXECUTE → OBSERVE → VERIFY
→ UPDATE WORLD STATE → CHECK PROGRESS
    ├── SUCCESS → CONSOLIDATE
    ├── UNCERTAIN → INVESTIGATE
    ├── FAILURE → DIAGNOSE
    ├── STAGNATION → CHANGE STRATEGY
    ├── RISK → PAUSE / ESCALATE
    └── PARTIAL → REPLAN
→ REFLECT → LEARN → UPDATE MEMORY / SKILLS
→ RUN REGRESSION CHECKS WHEN NEEDED → CHECK FOR EVOLUTION OPPORTUNITIES
→ CHECKPOINT → SELECT NEXT OBJECTIVE → REPEAT
```

## State Machine (Simplified)

For harness implementers who need a state machine rather than a flowchart:

```
RECEIVED → SPECIFIED → RECON → RESEARCHING → PLANNED → HYPOTHESIZING
→ CRITIC_GATE ─┬─ REJECT → RESEARCH / REPLAN
               └─ PASS → EXECUTING → TESTING ─┬─ FAIL → RECOVERY → REPLAN
                                              └─ PASS → EVALUATING → EVOLVING
                                                         ├─ IMPROVE → NEXT ROUND
                                                         ├─ STAGNATE → STRATEGY CHANGE
                                                         └─ CONVERGED → FINAL_AUDIT → DELIVERED → MEMORIZED
```

## Stop Conditions

Every autonomous loop must have at least one:

- **Success condition** — acceptance criteria satisfied
- **Failure condition** — unrecoverable blocker identified
- **Budget condition** — tokens, time, money, or tool calls exhausted
- **Timeout** — wall-clock deadline reached
- **Stagnation condition** — no progress across N rounds
- **Risk threshold** — risk score crosses authorized ceiling
- **Approval boundary** — awaiting human authorization

A loop without at least one stop condition is an **uncontrolled process** and must not be deployed.

## What "Never Stop" Actually Means

The protocol supports 24/7 operation, but "never stop" does **not** mean infinite execution. The runtime must stop, pause, or escalate when: mission complete, budget exhausted, authorization expires, safety boundary reached, environment invalid, no useful progress remains, or evidence cannot justify further action.

Idle time is not wasted — it is used for bounded background work: memory consolidation, indexing, contradiction detection, evaluation preparation, skill refinement, backlog analysis, safe planning, and health checks. All background work is bounded, interruptible, observable, budgeted, permission-aware, and reversible.

---

*Next: `04-World-Model-and-Memory.md:1` — how the agent knows what is true.*
