# 02 — Architecture Overview

## The Twelve-Plane Architecture

The AGI Executive Agent v8.0 Clean uses a **twelve-plane architecture**. Each plane is an independently controlled subsystem with its own `id, owner, inputs, outputs, state, invariants, permissions, failure_modes, telemetry, and version`. No plane may silently overwrite another plane's authoritative state.

```
┌──────────────────────────────────────────────────────────────┐
│                    1. Mission Plane                          │
│         Owns the mission object, priorities, authority       │
├──────────────────────────────────────────────────────────────┤
│  2. Identity &       │  3. World Model      │  4. Memory     │
│     Policy Plane     │     Plane            │     Plane      │
│  (SOUL.md)           │  Entities, relations │  Namespaces,   │
│  Values, boundaries, │  resources, causal   │  lifecycle,    │
│  authority model     │  models, transitions │  consolidation │
├──────────────────────────────────────────────────────────────┤
│  5. Context Plane    │  6. Cognition Plane  │  7. Planning   │
│  Managed resource:   │  Router, metacog,    │     Plane      │
│  select/rank/compress│  calibration, causal │  Portfolio,    │
│  isolate/archive     │  counterfactual      │  task graph,   │
│                      │                      │  search, path  │
├──────────────────────────────────────────────────────────────┤
│  8. Agent Plane      │  9. Tool &           │ 10. Evaluation │
│  Factory, economics, │     Environment Plane│     Plane      │
│  delegation, debate, │  Registry, discovery,│  Tests, scoring│
│  verification        │  computer-use, sandbox│  benchmarks   │
├──────────────────────────────────────────────────────────────┤
│  11. Safety &        │  12. Learning &      │                │
│      Security Plane  │      Evolution Plane │                │
│  Permissions, risk,  │  Reflection, skills, │                │
│  injection defense,  │  meta-learning, evo  │                │
│  audit               │  generalization       │                │
└──────────────────────────────────────────────────────────────┘
```

### Plane Details

| Plane | Responsibility | Key Mechanism |
|-------|---------------|---------------|
| **1. Mission** | Durable mission record, success criteria, budget, stakeholders | Mission contract, goal compiler |
| **2. Identity & Policy** | Who the agent is, what it will never do, authority hierarchy | SOUL.md constitution, autonomy ladder |
| **3. World Model** | Live model of entities, relationships, resources, state, transitions | World object, epistemic metadata, evidence graph |
| **4. Memory** | Persistent knowledge across sessions | 12 namespaces, importance scoring, conflict resolution |
| **5. Context** | Finite cognitive resource management | Context packets, selection/ranking/compression |
| **6. Cognition** | Reasoning modes, metacognition, calibration | Router (8 modes), contradiction engine |
| **7. Planning** | Strategies, decomposition, search, replanning | Plan portfolio, DAG, critical path, beam/tree/evolutionary search |
| **8. Agent** | Dynamic specialization and coordination | Factory, economics, debate, independent verification |
| **9. Tool & Environment** | World interaction | Dynamic registry, computer-use, sandbox, protocol adapters |
| **10. Evaluation** | Judging whether work is correct | Hierarchy (unit → real-world), benchmarks, quality gates |
| **11. Safety & Security** | Staying within bounds | Permission model, risk tiers R0–R5, injection defense, audit |
| **12. Learning & Evolution** | Getting better over time | Reflection, skill acquisition, candidate lineage, open-ended discovery |

### Evolution from v3 Nine-Plane to v8 Twelve-Plane

| v3 Nine-Plane | v8 Twelve-Plane | What Changed |
|---------------|-----------------|--------------|
| 1. Executive | 1. Mission | Narrowed to mission lifecycle; policy split out |
| — | 2. Identity & Policy | **New** — extracted from implicit SOUL.md coupling into explicit plane |
| 3. World Model | 3. World Model | Added causal models, temporal state, explicit transitions |
| 4. Memory | 4. Memory | Added failure, evaluation, causal, preference, identity namespaces |
| — | 5. Context | **New** — extracted from overloaded memory; finite-resource management |
| 2. Cognition | 6. Cognition | Added evolutionary, simulation, adversarial, maintenance modes |
| 5. Planning | 7. Planning | Added plan portfolio, critical path, search budgets |
| 6. Execution | 8. Agent + 9. Tool & Environment | **Split** — execution was overloaded; agents and tools are distinct concerns |
| 7. Evaluation | 10. Evaluation | Added benchmark portfolio and evolution gates |
| 9. Safety/Reliability | 11. Safety & Security | Expanded with injection defense, transaction model, compositional risk |
| 8. Adaptation | 12. Learning & Evolution | Expanded with lineage, protected invariants, generality evaluation |

## How the Planes Interact

```
Mission (1) defines → World Model (3) tracks → Context (5) assembles
        │                      │                      │
        ▼                      ▼                      ▼
   Planning (7) ←→ Cognition (6) ←→ Memory (4) ──────────→ Agent (8) ──→ Tool/Env (9)
        │                      │                      │           │              │
        ▼                      ▼                      ▼           ▼              ▼
   Evaluation (10) ←──────── Safety (11) ───────────── Learning (12) ← Identity (2) governs all
```

- **Identity (2) governs all** — every plane checks authority against SOUL.md before consequential action.
- **Safety (11) observes all** — permission checks, preflight, and audit are not optional steps but active guards.
- **Learning (12) consumes from all** — reflection, skill extraction, and evolution draw on evidence from every other plane.

## Technology Mapping

| Concept | v8 Plane | AGX Component | Hermes Equivalent | Research Source |
|---------|----------|---------------|-------------------|-----------------|
| Mission compilation | 1 | `agx/kernel.py` | planner | Anthropic workflows |
| Persistent state | 3, 4, 5 | `agx/memory.py` | `MEMORY.md` | MemGPT, Generative Agents |
| Planning | 7 | `agx/frontier.py` | plan portfolio | ReAct, Tree-of-Thought |
| Agents | 8 | `agx/supervisor.py` | agent factory | AutoGen, MetaGPT |
| Tools | 9 | `agx/sandbox.py` | terminal backend | ToolSandbox, AgentDojo |
| Evaluation | 10 | `agx/evaluator.py` | evaluator | SWE-bench, AgentDojo |
| Safety | 11 | `agx/secrets.py` | approval policy | AgentDojo, red-team literature |
| Evolution | 12 | `agx/knowledge.py` | lineage tracking | FunSearch, AlphaEvolve, AVO |

## Invariants That Cross All Planes

- No plane silently overwrites another plane's authoritative state.
- Every state transition is recorded with `before, action, observation, after, timestamp, actor, source, confidence, evidence`.
- External content entering any plane is treated as `DATA`, not `CONTROL`.
- Protected invariants (authorization, auditability, safety boundaries, isolation, approval gates, rollback, logging, provenance, policy enforcement) cannot be optimized away.

---

*Next: `03-Operating-Loop.md:1` — the mission lifecycle from receipt to delivery.*
