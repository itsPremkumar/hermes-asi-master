---
name: hermes-project-synthesis
description: Hermes Project Synthesis Engine — Any problem → search open source & closed-source references → evaluate → reuse, modify, combine, or build from scratch → deliver advanced high-level synthesis.
version: "1.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, synthesis, open-source, reuse, build, evaluation, architecture]
    category: hermes-advanced
    requires_tools: [web_search]
    requires_toolsets: [web]
---

# SKILL 08 — PROJECT SYNTHESIS ENGINE

> **Load this skill when:** User has ANY problem and wants Hermes to find existing open-source projects, evaluate them, and decide: use as-is, modify, combine multiple, reference closed-source, or build from scratch — then build the advanced high-level synthesis.
> **Pairs with:** `01-research` (evidence) + `07-search-optimized` (live search) + `02-planning` (6-plan portfolio) — this skill is the synthesis brain on top of them.

---

## 0. PURPOSE — THE SYNTHESIS LAW

> **Never build from scratch what already exists. Never blindly reuse what doesn't fit. Always synthesize the most advanced result.**

For ANY problem Hermes receives, the default is NOT to code immediately. The default is:

```
PROBLEM → SEARCH OPEN SOURCE → SEARCH CLOSED-SOURCE REFERENCES → EVALUATE
→ DECIDE: Reuse / Modify / Combine / Inspire / Build → SYNTHESIZE → VERIFY → DELIVER
```

A Hermes synthesis task is complete only when the delivered artifact is **provably more advanced** than any single source project alone.

---

## 1. WHEN TO USE

| User Problem | Use This Skill? |
|---|---|
| "Build X — is there anything open source that already does this?" | **YES — primary use** |
| "Find a project like Y but more advanced" | **YES** |
| "I need feature A + feature B from different projects combined" | **YES — Combine mode** |
| "This closed-source product does Z — can we build something similar?" | **YES — Reference mode** |
| "Should we use existing tech or build from scratch?" | **YES — Decision mode** |
| Pure search with no build intent | Use `01-research` + `07-search-optimized` instead |

---

## 2. THE ADVANCED SYNTHESIS LOOP

```
1. DECOMPOSE PROBLEM
     ↓
2. SEARCH OPEN SOURCE (5 parallel searches + browser)
     ↓
3. SEARCH CLOSED-SOURCE REFERENCES (product pages, docs, reviews, comparisons)
     ↓
4. EVALUATE CANDIDATES (scoring matrix — see templates/evaluation-matrix.md)
     ↓
5. DECIDE STRATEGY (Reuse / Fork-Modify / Combine / Inspire / Scratch)
     ↓
6. SYNTHESIZE PLAN (6-plan portfolio including synthesis options)
     ↓
7. BUILD / MODIFY / COMPOSE
     ↓
8. VERIFY (12 gates + independent tester + compare to sources)
     ↓
9. DELIVER (with provenance: what was reused, modified, built, and why)
```

This loop is Hermes-native: every search uses `07-search-optimized` (5 parallel + browser + evidence graph), every build uses `03-orchestration` swarm if beneficial.

---

## 3. SEARCH — OPEN SOURCE & CLOSED-SOURCE

### 3.1 Open Source Search (Primary)

Hermes fires **5 parallel searches** via `07-search-optimized`:

| # | Query Pattern | Purpose |
|---|---------------|---------|
| 1 | `"{problem}" open source github` | Core discovery |
| 2 | `"{problem}" github stars >1000` | Most mature/popular |
| 3 | `"{problem}" alternative OR vs OR comparison 2025 2026` | Compare options |
| 4 | `"{problem}" framework OR library OR toolkit` | Different abstraction levels |
| 5 | `"{problem}" awesome list OR curated` | Curated collections |

**For each candidate:** Browser-load GitHub repo page + README + recent commits + issues + stars + license.

### 3.2 Closed-Source Reference Search (Secondary, Legal)

Hermes also searches **closed-source products** — NOT to copy code, but to understand features, UX, architecture, and benchmarks:

| # | Query Pattern | Purpose |
|---|---------------|---------|
| 1 | `"{problem}" best tools 2025 2026` | Commercial landscape |
| 2 | `"{problem}" "{closed product}" features` | Feature reference |
| 3 | `"{problem}" "{closed product}" vs open source alternative` | Gap analysis |
| 4 | `"{problem}" pricing OR comparison` | Build-vs-buy economics |

**Rule:** Closed-source is **reference only** — understand WHAT it does and HOW WELL, never copy proprietary code. Open source is where code comes from.

### 3.3 Technology Search

```
"{problem}" technology stack OR tech stack 2026
"{problem}" architecture pattern 2026
"{problem}" benchmark OR performance comparison
```

---

## 4. EVALUATION MATRIX

For each candidate project found, Hermes scores:

```markdown
| # | Criterion | Weight | Score (0-5) | Notes |
|---|-----------|--------|-------------|-------|
| 1 | **Functional Fit** — How much of the problem does it solve? | 25% | | % of requirements covered |
| 2 | **Maturity** — Stars, commits, contributors, last update | 15% | | >1K stars, active <3mo = high |
| 3 | **License** — Can we use/modify/commercialize? | 15% | | MIT/Apache = 5, GPL = 3, Proprietary = 0 |
| 4 | **Code Quality** — Tests, docs, architecture | 10% | | Tests + docs + clean arch = high |
| 5 | **Community** — Issues response, PRs, maintenance | 10% | | Active maintainer = high |
| 6 | **Tech Stack Fit** — Matches our stack? | 10% | | Same language/framework = high |
| 7 | **Extensibility** — How easy to modify/combine? | 10% | | Plugin system, modular = high |
| 8 | **Performance** — Benchmarks vs requirements | 5% | | Meets perf needs = high |

Weighted Score = Σ(Score × Weight) → Rank candidates.
```

**Template:** `templates/evaluation-matrix.md` (copy per candidate)

**License Quick Guide (Hermes must check):**

| License | Reuse As-Is | Modify | Combine | Commercial | Score |
|---------|------------|--------|---------|------------|-------|
| MIT, Apache 2.0, BSD | ✅ | ✅ | ✅ | ✅ | 5 |
| GPL v3 | ✅ | ✅ (must open source derivative) | ⚠️ Infects | ⚠️ Must open | 3 |
| Proprietary / Closed | ❌ | ❌ | ❌ | ❌ | 0 (reference only) |

Hermes MUST check license before recommending reuse. GPL derivative must be disclosed. Proprietary never reused as code.

---

## 5. DECISION FRAMEWORK — THE 5 STRATEGIES

After scoring, Hermes chooses ONE strategy per candidate (or a combination):

```
                    ┌─ Functional Fit ─┐
                    │   90-100%?       │
              ┌─────┤  AND License OK? ├─────┐
              │     │  AND Tech Fit?   │     │
              │     └──────────────────┘     │
              │              │               │
              │         YES  │          NO   │
              │              │               │
              ▼              ▼               ▼
        ┌──────────┐   ┌──────────┐    ┌──────────┐
        │  REUSE   │   │  MODIFY  │    │  COMBINE │
        │  As-Is   │   │  Fork &  │    │ Multiple │
        │          │   │  Extend  │    │ Projects │
        └──────────┘   └──────────┘    └──────────┘
              │              │               │
              └──────┬───────┘               │
                     │                       │
                     ▼                       ▼
              ┌──────────┐            ┌──────────┐
              │ INSPIRE  │            │  SCRATCH │
              │ Closed-  │            │  Build   │
              │ Source   │            │  New     │
              │ Reference│            │          │
              └──────────┘            └──────────┘
```

### Strategy Definitions

| Strategy | When | Hermes Action | Advanced Output |
|----------|------|---------------|-----------------|
| **REUSE** | Fit ≥90%, license OK, tech matches | Use project as-is, configure, deploy | Integrated + verified deployment with docs |
| **MODIFY** | Fit 60-90%, good base but needs changes | Fork repo, modify/extend, keep upstream attribution | Forked repo with delta documented, tests added |
| **COMBINE** | No single project covers all needs | Take **best features** from 2-4 projects, compose into new architecture | **Synthesis** — new project that is more advanced than any source alone (flagship) |
| **INSPIRE** | Closed-source reference is best | Study closed-source features/UX/benchmarks, design open equivalent inspired by it (no code copy) | Open alternative with closed-source UX + open-source extensibility |
| **SCRATCH** | No suitable open source, or license blocks, or existing projects are outdated/bloated | Build from scratch using best **technology** + **patterns** found, not code | Clean, modern, minimal implementation with lessons from all sources |

### COMBINE Mode — The Flagship (Refeature)

This is where Hermes is **most advanced**. Example:

```
Problem: "Build an AI agent dashboard"

Found:
  - Project A (React dashboard, great UI, no agent logic) — UI: 5/5, Logic: 1/5
  - Project B (Python agent harness, great logic, no UI) — UI: 1/5, Logic: 5/5
  - Project C (Closed-source product, great UX flow) — Reference for flow

Hermes COMBINE:
  - UI layer from Project A (MIT, reuse)
  - Agent logic from Project B (Apache, modify to add API)
  - UX flow inspired by Project C (reference, not copy)
  → New Project: Agent dashboard with best UI + best logic + best UX flow
  → More advanced than any single source
```

**Refeature:** Take Feature X from Project A + Feature Y from Project B → New feature XY that neither had alone.

---

## 6. SYNTHESIS PLAN — 6-PLAN PORTFOLIO FOR BUILD

For the chosen strategy, Hermes generates 6 competing plans (via `02-planning`):

| Plan | Strategy | Risk | When Best |
|------|----------|------|-----------|
| **A — Reuse** | Use best single project as-is | Lowest | High fit + OK license |
| **B — Modify** | Fork + extend best project | Low-Med | 60-90% fit |
| **C — Combine** | Compose 2-3 projects (refeature) | Medium | No single project covers all |
| **D — Inspire** | Build open alternative inspired by closed-source | Medium | Closed-source is best reference |
| **E — Scratch** | Build from scratch with best tech | Higher | No suitable open source |
| **F — Hybrid** | Combine open reuse + closed inspiration + scratch for gaps | Medium-High | Complex problem needing all |

Score each by: functional coverage, license safety, tech fit, community health, extensibility, performance, cost (build time), risk, maintenance burden. **Evidence beats vote count.**

---

## 7. BUILD / MODIFY / COMPOSE

### If REUSE:
```bash
git clone <repo> && configure && deploy
# Hermes verifies: tests pass, deployment works, docs complete
```

### If MODIFY (Fork & Extend):
```bash
git clone <repo> → fork → branch → modify → add tests → document delta
# Hermes tracks: What was changed, why, and how to merge upstream updates
# File: MODIFICATIONS.md — "Forked from X at commit Y, changed Z because..."
```

### If COMBINE (Synthesis — Flagship):
```
1. Scaffold new project architecture
2. Import/reuse modules from each source (with attribution + license compliance)
3. Write glue code + new features that connect them
4. Add integration tests
5. Document provenance: "Feature X from Project A (MIT), Feature Y from Project B (Apache)..."

Hermes uses swarm (skills/03-orchestration) if beneficial:
  Worker 1: Integrates Project A components
  Worker 2: Integrates Project B components
  Worker 3: Builds glue + new synthesis features
  → Best-component synthesis
```

### If SCRATCH:
```
Build from scratch BUT using:
  - Best technology stack found in search
  - Best architecture patterns found
  - Lessons from why existing projects were insufficient (documented)
```

---

## 8. VERIFICATION — PROVE IT'S MORE ADVANCED

Hermes does NOT deliver without proving the synthesis is advanced:

```
1. Functional: Does it solve the original problem? (vs requirements)
2. Comparative: Is it more advanced than each source alone? (feature matrix)
3. Independent: Tester worker verifies without builder context
4. License: All reuse/modify/combine respects licenses (attribution, GPL disclosure)
5. Quality Gates: 12 gates (G1-G12) — see skills/05-safety-evaluation

Feature Comparison Matrix (proves synthesis is advanced):
| Feature | Source A | Source B | Closed Ref C | Hermes Synthesis |
|---------|----------|----------|--------------|------------------|
| Feature X | ✅ | ❌ | ✅ | ✅ (from A + C UX) |
| Feature Y | ❌ | ✅ | ❌ | ✅ (from B) |
| Feature Z (new) | ❌ | ❌ | ❌ | ✅ (Hermes invented) |
→ Synthesis has MORE than any single source = proof it is more advanced
```

---

## 9. DELIVERY — PROVENANCE

Every Hermes synthesis delivery includes:

```markdown
# Delivery: {Problem} — Hermes Synthesis

## What Was Done
- **Strategy:** Combine (Project A + Project B + Closed-source C inspiration)
- **Result:** New project at ./synthesis-output/ — more advanced than any source alone

## Provenance (What Came From Where)
- **Reused as-is:** Project A UI components (MIT, https://github.com/.../A, commit abc123)
- **Modified:** Project B agent logic (Apache 2.0, forked, extended with feature Y)
- **Inspired by:** Product C UX flow (reference: https://.../product-c, no code copied)
- **Built from scratch:** Feature Z (novel synthesis, not in any source)

## Why This Strategy?
- Project A alone: 60% fit, missing logic
- Project B alone: 55% fit, missing UI
- Scratch alone: 3 weeks vs 1 week with reuse
- Combine: 95% fit + novel Z = most advanced result

## Verification
- 12 gates: G1-G10 pass, G11/G12 N/A
- Independent tester: verified
- License compliance: MIT + Apache attribution in LICENSE, no GPL

## Files
- ./synthesis-output/ — New project
- ./evidence/evidence-graph.md — All sources with scores
- ./MODIFICATIONS.md — What was changed from each source
```

---

## 10. HERMES SEARCH QUERIES FOR SYNTHESIS

Hermes fires these searches via `07-search-optimized` (5 parallel + browser):

**Open source discovery:**
```
"{problem}" open source github
"{problem}" github stars:>1000
"{problem}" alternative vs comparison 2026
"{problem}" awesome list
"{problem}" framework library toolkit
```

**Closed-source reference:**
```
"{problem}" best tools 2026
"{problem}" "{closed product}" features vs open source
```

**Technology:**
```
"{problem}" tech stack 2026
"{problem}" architecture pattern benchmark
```

---

*SKILL 08 — Hermes Project Synthesis Engine. Any problem → search open + closed → evaluate → reuse/modify/combine/inspire/scratch → deliver advanced synthesis with provenance.*
*The flagship of Hermes Advanced: never build what exists, never blindly reuse what doesn't fit, always synthesize the most advanced result.*
