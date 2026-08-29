# 07 — Project Synthesis Plan — Advanced High-Level

> **The Hermes Advanced Flagship Plan:** For ANY problem, search open + closed, evaluate, and synthesize the most advanced result. This is the complete advanced high-level plan you asked for.

---

## The Plan in One Diagram

```
ANY PROBLEM HERMES RECEIVES
        │
        ├──→ SEARCH: Open Source (GitHub, GitLab, awesome lists)
        ├──→ SEARCH: Closed-Source References (product pages, reviews, comparisons)
        └──→ SEARCH: Technology Stacks & Architecture Patterns
                │
                ▼
        EVALUATE EVERY CANDIDATE (8 criteria, weighted score, license check)
                │
                ▼
        DECIDE STRATEGY (5 options):
        ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
        │   REUSE     │   MODIFY    │   COMBINE   │   INSPIRE   │   SCRATCH   │
        │  As-Is      │  Fork &     │  Multiple   │  Closed-    │  Build New  │
        │  90-100% fit│  Extend     │  Projects   │  Source     │  No suitable│
        │             │  60-90% fit │  No single  │  Reference  │  open source│
        │             │             │  covers all │  is best    │  exists     │
        └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
                │             │             │             │             │
                └──────┬──────┘             │             │             │
                       │              ┌─────┴─────┐       │             │
                       ▼              ▼             ▼       ▼             ▼
                  SYNTHESIZE PLAN (6-plan portfolio: Reuse → Hybrid)
                       │
                       ▼
                  BUILD / MODIFY / COMPOSE (with swarm if beneficial)
                       │
                       ▼
                  VERIFY (12 gates + independent tester + feature matrix proves more advanced)
                       │
                       ▼
                  DELIVER WITH PROVENANCE (what was reused, modified, built, why)
```

---

## Phase 1: Decompose Problem

Before searching, Hermes decomposes the problem into searchable requirements:

```
Problem: "Build an AI agent dashboard like Product X but open source"

Decomposed:
  - Requirement 1: Dashboard UI (React, real-time)
  - Requirement 2: Agent orchestration (multi-agent, tools)
  - Requirement 3: Memory/persistence (across sessions)
  - Requirement 4: Search integration (live web)
  - Search each requirement independently (4 × 5 searches = 20 parallel searches via 07-search-optimized)
```

---

## Phase 2: Search — Open + Closed + Tech

Hermes fires **15-20 parallel searches** (3-5 per requirement):

| Type | Example Queries | Purpose |
|------|-----------------|---------|
| **Open Source** | `"agent dashboard" open source github`, `"agent dashboard" awesome list` | Find code to reuse |
| **Closed Reference** | `"Product X" features`, `"Product X vs open source"` | Understand WHAT to build, not HOW (no code copy) |
| **Technology** | `"agent dashboard" tech stack 2026`, `"agent dashboard" architecture` | Find best stack if building |

For each candidate found: **Browser-load** GitHub page + README + license + recent commits + stars + issues.

---

## Phase 3: Evaluate — Weighted Scoring

Per candidate, Hermes fills `skills/08-project-synthesis/templates/evaluation-matrix.md`:

| Criterion | Weight | Why It Matters |
|-----------|--------|----------------|
| Functional Fit | 25% | Does it solve the problem? |
| Maturity | 15% | Will it be maintained next year? |
| License | 15% | Can we legally reuse/modify? |
| Code Quality | 10% | Tests, docs, architecture? |
| Community | 10% | Will maintainers respond? |
| Tech Stack Fit | 10% | Matches our stack? |
| Extensibility | 10% | Easy to modify/combine? |
| Performance | 5% | Fast enough? |

**License is load-bearing:** MIT/Apache (5/5) → safe to reuse/modify/combine. GPL (3/5) → must open-source derivative. Proprietary (0/5) → reference only, never code.

---

## Phase 4: Decide — 5 Strategies

| Strategy | When to Choose | Hermes Does |
|----------|----------------|-------------|
| **REUSE** | One project fits 90-100% + license OK | Clone, configure, deploy — done |
| **MODIFY** | Best project fits 60-90% | Fork, branch, extend, document delta in `MODIFICATIONS.md` |
| **COMBINE** | No single project covers all | **Flagship:** Take Feature X from Project A (MIT) + Feature Y from Project B (Apache) → new architecture that is more advanced than either alone |
| **INSPIRE** | Closed-source product is best reference | Study closed features/UX/benchmarks → design open equivalent *inspired by* it (no code copied) |
| **SCRATCH** | No suitable open source exists | Build from scratch using best **technology + patterns** found (not code) |

**COMBINE (Refeature) is where Hermes is most advanced.** Example:

```
Found:
  - Project A: React dashboard (UI: 5/5, agent logic: 1/5) — MIT
  - Project B: Python agent harness (UI: 1/5, logic: 5/5) — Apache
  - Product C: Closed dashboard (great UX flow) — Reference

Hermes COMBINE:
  UI from A + Logic from B + UX flow inspired by C
  = New project more advanced than any single source
```

---

## Phase 5: Synthesize Plan — 6-Plan Portfolio

For the chosen strategy, Hermes generates 6 competing plans via `02-planning`:

| Plan | Strategy | Risk |
|------|----------|------|
| A — Reuse | Use best single project as-is | Lowest |
| B — Modify | Fork & extend best project | Low-Med |
| C — Combine | Compose 2-3 projects (refeature) | Medium |
| D — Inspire | Build open alternative inspired by closed | Medium |
| E — Scratch | Build from scratch with best tech | Higher |
| F — Hybrid | Combine open reuse + closed inspiration + scratch for gaps | Medium-High |

Score each by coverage, license safety, tech fit, community, extensibility, performance, **build time**, risk, maintenance. Pick best by evidence.

---

## Phase 6: Build / Modify / Compose

| Strategy | Hermes Build Steps |
|----------|-------------------|
| **REUSE** | `git clone && configure && deploy` → verify tests pass |
| **MODIFY** | `clone → fork → branch → modify → add tests → MODIFICATIONS.md` (what changed, why, upstream commit) |
| **COMBINE** | Scaffold new project → import modules from each source (with attribution) → glue code + new synthesis features → integration tests. Use **swarm** (`03-orchestration`) if beneficial: Worker 1 integrates A, Worker 2 integrates B, Worker 3 builds glue |
| **SCRATCH** | Build clean, minimal, modern implementation using best stack/patterns from search — document why existing projects were insufficient |

All builds respect licenses: MIT/Apache attribution in `LICENSE`, GPL disclosure if needed, no proprietary code copied.

---

## Phase 7: Verify — Prove It's More Advanced

Hermes does NOT deliver without proof:

| Check | How |
|-------|-----|
| **Functional** | Does it solve original problem? (vs requirements) |
| **Comparative** | Feature matrix proves synthesis has MORE than any single source (see `templates/comparison-matrix.md`) |
| **Independent** | Tester worker verifies without builder context |
| **License** | Attribution correct, GPL disclosed, no proprietary copy |
| **Quality Gates** | 12 gates (G1-G12) via `05-safety-evaluation` |

**Feature Comparison Matrix (proves advanced):**

| Feature | Source A | Source B | Closed C | Hermes Synthesis |
|---------|----------|----------|----------|------------------|
| Feature X | ✅ | ❌ | ✅ | ✅ (from A + C UX) |
| Feature Y | ❌ | ✅ | ❌ | ✅ (from B) |
| Feature Z (novel) | ❌ | ❌ | ❌ | ✅ (Hermes invented) |
| **Coverage** | 60% | 55% | 70% | **95%** |

Synthesis 95% > any single source 70% = **proof it is more advanced**.

---

## Phase 8: Deliver with Provenance

Every delivery includes `templates/provenance.md` filled:

```markdown
## What Came From Where
- Reused: Project A UI (MIT, github.com/.../A, commit abc)
- Modified: Project B logic (Apache, forked, feature Y added)
- Inspired by: Product C UX (reference, no code copied)
- Built from scratch: Feature Z (novel)

## Why This Strategy?
- A alone: 60% fit, missing logic
- B alone: 55% fit, missing UI
- Scratch: 3 weeks vs 1 week with reuse
- Combine: 95% + novel Z = most advanced
```

---

## When to Use This Plan

| User Says | Hermes Does |
|-----------|-------------|
| "Build X — is there open source for this?" | Full synthesis loop (Phases 1-8) |
| "Find project like Y but better" | Search → Evaluate → Modify/Combine |
| "Combine feature A + B from different projects" | Direct to COMBINE |
| "Closed product Z does this — can we build similar?" | INSPIRE mode (reference, not copy) |
| "Should we use existing or build from scratch?" | Search → Evaluate → 6-plan portfolio → Recommend |

---

## For Hermes: Search Queries to Fire

Hermes uses `07-search-optimized` (5 parallel + browser) with these query sets:

**Open source:**
```
"{problem}" open source github
"{problem}" github stars:>1000
"{problem}" alternative vs comparison 2026
"{problem}" awesome list
```

**Closed reference:**
```
"{problem}" best tools 2026
"{problem}" "{product}" vs open source
```

**Technology:**
```
"{problem}" tech stack 2026
"{problem}" architecture benchmark
```

---

*Plan by Hermes Advanced Project Synthesis Engine (Skill 08). Any problem → search open + closed → evaluate → reuse/modify/combine/inspire/scratch → deliver advanced synthesis with provenance. Never build what exists, never blindly reuse what doesn't fit, always synthesize the most advanced result.*
