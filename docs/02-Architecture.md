# 02 — Hermes Advanced Architecture (15 Planes)

## The Hermes Fifteen-Plane Architecture

Evolution: v3 (9-plane) → v6/v8 (12-plane) → **Hermes Advanced v2.0 (15-plane)**. Each plane has `id, owner, inputs, outputs, state, invariants, permissions, failure_modes, telemetry, version`. No plane silently overwrites another's authoritative state. All planes are Hermes-native — they use Hermes tools, Hermes memory, Hermes swarm.

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. MISSION PLANE — Hermes Goal Contract + Strategic Intent          │
│     Durable mission object, 6-plan portfolio trigger, R0-R6 risk     │
├──────────────────────────────────────────────────────────────────────┤
│  2. IDENTITY & POLICY — SOUL.md + AGENT.md (Rowan on Hermes)         │
│     Values, corrigibility, ASI alignment, Hermes guardrails          │
│  3. WORLD MODEL — Multi-horizon temporal, counterfactual worlds      │
│     Entities, causal models, simulation ensemble, known unknowns     │
│  4. MEMORY — 15 namespaces, hierarchical compression, cross-domain   │
│     Working → Strategic → Superintelligent Insight (ASI)             │
│  5. CONTEXT — Finite resource, 4-level compression, packets         │
│     Write → Select → Rank → Compress → Isolate → Archive → Synthesize│
├──────────────────────────────────────────────────────────────────────┤
│  6. COGNITION — 10 modes including SUPERINTELLIGENT                  │
│     Fast, Deliberative, Research, Exploratory, Simulation, Adversarial│
│     Evolutionary, Recovery, Maintenance, + Superintelligent [ASI]    │
│  7. PLANNING — 6-plan portfolio, DAG, 10 search strategies           │
│     Conservative→Strategic, critical path, simulation ensemble       │
│  8. AGENT SWARM — 30+ roles, Hermes parallel workers (3-5)           │
│     Economics, diversity, debate protocol, triple verification       │
│  9. TOOL & ENVIRONMENT — Hermes-native stack (web_search→browser)   │
│     Dynamic registry, tool composition, computer-use, sandbox+attestation│
├──────────────────────────────────────────────────────────────────────┤
│ 10. EVALUATION — 12 gates (G11 Formal Proof + G12 Strategic)         │
│     Benchmarks, capability matrix, generality tests                  │
│ 11. SAFETY & SECURITY — R0-R6, 22 invariants, injection defense     │
│     Permission model, preflight, compositional + existential risk    │
│ 12. LEARNING & EVOLUTION — AVO, lineage, meta-learning, transfer    │
│     Reflection, skill acquisition, frontier search, open-ended discovery│
├──────────────────────────────────────────────────────────────────────┤
│ 13. STRATEGIC SUPERINTELLIGENCE [ASI] — Hermes 100x Foresight        │
│     Scenario trees, cross-domain synthesis, opportunity invention    │
│     "What does this Hermes mission IMPLY beyond the original question?"│
│ 14. FORMAL VERIFICATION [ASI] — Hermes Proof                         │
│     Property proofs, model checking, adversarial proof search        │
│     Proof > Testing. For high-stakes Hermes code and decisions.      │
│ 15. SELF-EVOLUTION [ASI] — Hermes Improves Hermes                    │
│     Recursive improvement, capability forecasting, corrigibility-preserving│
│     "Hermes improves HOW it pursues the constitution, never WHAT it values."│
└──────────────────────────────────────────────────────────────────────┘
```

---

## How Hermes Planes Interact

```
Mission (1) → Strategic (13) foresight → Planning (7) → Swarm (8) → Tools (9)
     ↑              ↑                        ↑               ↑          ↑
Identity (2) governs all • Safety (11) guards all • Verification (14) proves critical paths
     ↑              ↑                        ↑               ↑          ↑
World (3) ↔ Memory (4) ↔ Context (5) ↔ Cognition (6) ↔ Evaluation (10) ↔ Evolution (12+15)
     ↑                                                    ↑
Hermes Memory (memory/MEMORY.md)              Hermes Evidence (evidence/evidence-graph.md)
```

- **Identity (2) governs all** — Every Hermes plane checks SOUL.md + AGENT.md before consequential action.
- **Safety (11) guards all** — Permission checks, preflight, audit — not optional steps.
- **Learning (12+15) consumes from all** — Reflection, skill extraction, evolution draw on every plane.

---

## Hermes Plane Details

| Plane | Hermes Responsibility | Hermes Tool / File |
|-------|----------------------|-------------------|
| **1. Mission** | Durable mission record, 6 plans trigger | `SKILL.md` §2, `memory/USER.md` |
| **2. Identity** | Rowan + SOUL.md v4.0 ASI + AGENT.md guardrails | `SOUL.md`, `AGENT.md` |
| **3. World Model** | Live multi-horizon model (past → 90-day future) | `skills/06-memory-world/SKILL.md` |
| **4. Memory** | 15 namespaces, TTL, cross-domain index | `memory/MEMORY.md` (4000 chars, hierarchical) |
| **5. Context** | Finite resource, 4-level compression, packets | Hermes context window (managed, not append-only) |
| **6. Cognition** | 10 modes, Bayesian calibration, causal reasoning | `skills/06-memory-world/SKILL.md` |
| **7. Planning** | 6 plans, DAG, critical path, simulation ensemble | `skills/02-planning/SKILL.md` |
| **8. Swarm** | 30+ roles, Hermes parallel workers, debate | `skills/03-orchestration/SKILL.md` |
| **9. Tools** | Hermes-native stack, sandbox with attestation | `skills/04-tools/SKILL.md` + `config/config.yaml` |
| **10. Evaluation** | 12 gates, benchmarks, capability matrix | `skills/05-safety-evaluation/SKILL.md` |
| **11. Safety** | R0-R6, 22 invariants, injection defense | `skills/05-safety-evaluation/SKILL.md` + `SOUL.md` |
| **12. Evolution** | AVO, lineage, meta-learning, transfer | `skills/05-safety-evaluation/SKILL.md` |
| **13. Strategic** | 100x foresight, opportunity invention | `SKILL.md` §13 + `skills/02-planning` |
| **14. Formal** | Proof, property verification | `skills/05-safety-evaluation/SKILL.md` §11 |
| **15. Self-Evolution** | Recursive improvement, corrigibility-preserving | `SKILL.md` §15 + `SOUL.md` §22 |

---

## Hermes vs Generic AGI Planes

| Generic AGI (v8.0) | Hermes Advanced Addition |
|---------------------|--------------------------|
| Tool Plane: generic registry | **Hermes-native stack:** web_search+browser+file_write+terminal_exec(docker) with Hermes ACI |
| Agent Plane: generic factory | **Hermes Swarm:** Hermes parallel subagents (3-5) with isolated contexts, Hermes orchestrator-workers |
| Safety Plane: generic R0-R5 | **Hermes Safety:** R0-R6, Hermes-specific injection surfaces (MCP, memory retrieval), Hermes preflight |
| Memory Plane: generic 4000 chars | **Hermes Memory:** 4000 chars + spotlighting + re-anchoring + Hermes write_approval=true |
| Config: one file | **Hermes Config Suite:** 3 profiles (base / search / production) + .env separation |

---

*Next: `03-Installation.md` — Install Hermes Advanced step-by-step.*
