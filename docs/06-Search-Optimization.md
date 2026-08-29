# 06 — Hermes Search Optimization (Flagship)

> This is the **flagship capability** of Hermes Advanced. If Hermes is only superhuman at one thing, it is this.

---

## The Hermes Search Law

> **No important claim without a live source. No live source without verification. No verification without provenance.**
> **No snippet as final evidence when browser is available.**

---

## The 5-Parallel-Search Protocol

### Before Hermes Searches

Hermes **compiles** one user question into 5 parallel searches:

**User asks:** `"What is the latest Hermes Agent deployment best practice for 2026?"`

| # | Query | Purpose | Required |
|---|-------|---------|----------|
| 1 | `hermes agent deployment guide site:nousresearch.com` | Authoritative primary source | ✅ |
| 2 | `hermes agent config.yaml best practice 2026` | Freshness (2026) | ✅ |
| 3 | `hermes agent sandbox security 2025 2026` | Security best practice | ✅ |
| 4 | `hermes agent vs openclaw comparison 2026` | Alternative view | Optional |
| 5 | `hermes agent limitations OR issues` | **Contradiction / counter-evidence** | ✅ |

**Rules:**
1.  One search per sub-question, with `site:` and date filters
2.  Vary phrasing (same fact, 2 phrasings = 2x coverage)
3.  Include one **counter-query** (`limitations OR issues`)
4.  Fire **3-5 searches in parallel** (Hermes parallel tool calling)

### Hermes Executes

```
5 web_search calls IN PARALLEL (not sequentially)
  ↓
For each: get top 5 URLs → rank by authority + freshness + independence
  ↓
Browser load TOP 3 URLs IN PARALLEL (full pages, not snippets)
  ↓
Extract {title, publish_date, author, content, code_blocks, tables}
  ↓
Follow links to PRIMARY source if this is a summary
  ↓
Save to ./evidence/raw/source-*.md with full provenance
```

### Hermes Triage

```
Score each result: authority(0-3) + freshness(0-2) + independence(0-2) + specificity(0-2)
  ≥6: browser load full page (high value)
  3-5: snippet + flag as needs corroboration
  <3: skip unless desperate
```

---

## Evidence Graph — Hermes File-Based

Hermes context truncates at ~200K tokens. **Hermes MUST persist evidence to files:**

```
./evidence/
├── evidence-graph.md       # Master: Claim → Source → Confidence (THIS IS THE DELIVERABLE)
├── sources.md              # All sources with reliability scores
├── contradictions.md       # Conflicting claims preserved (both sides)
└── raw/
    ├── source-01-hermes-docs-2026.md
    ├── source-02-github-hermes-2026.md
    └── source-03-paper-2026.md
```

**Master Evidence Graph Template:**

```markdown
| # | Claim | Source | Type | Freshness | Reliability | Confidence | Contradiction |
|---|-------|--------|------|-----------|-------------|------------|---------------|
| 1 | Hermes requires >=64K context | nousresearch.com/docs (Primary) | Primary | 2026 | 0.95 | confirmed | None |
| 2 | Hermes default write_approval is false | config.yaml docs (Primary) | Primary | 2026 | 0.90 | strongly_supported | — |
| 3 | Hermes heartbeat acts without prompting | OpenClaw docs (Secondary) | Secondary | 2026 | 0.80 | supported | SOUL §6 limits apply |
```

---

## Contradiction Search + Second Wave

**Contradiction Search (Mandatory):**

```
Search: "{original query} limitations OR issues OR problems OR deprecated"
Action: Browser load contradictory source → compare side-by-side
Output: contradictions.md with BOTH sides preserved

Never silently pick the convenient answer. Report which side has stronger evidence and why.
```

**Second Search Wave (Gap Closure):**

```
After first synthesis, Hermes asks:
  What claims still lack independent corroboration?
  What claims rely on a single source?
  What 2026 claims lack freshness verification?
→ Generate NEW targeted searches for gaps
→ Fire SECOND parallel wave (2-3 searches)
→ Merge into evidence graph

Two waves is the Hermes Advanced MINIMUM. One wave is never enough for complex questions.
```

---

## Hermes Search Prompts — Copy-Paste

**Official docs:**
```
"{topic}" site:github.com/nousresearch OR site:nousresearch.com after:2025-01-01
```

**Fresh information:**
```
"{topic}" 2026 -2023 -2024
```

**Security / best practice:**
```
"{topic}" security OR sandbox OR approval OR best practice 2026
```

**Troubleshooting:**
```
"{topic}" error OR issue OR fix site:github.com
```

**Contradiction:**
```
"{topic}" limitations OR deprecated OR alternative OR vs
```

---

## Final Report — Hermes Search Deliverable

Every search-heavy Hermes task ends with this structure:

```markdown
# Research Report: {User Question}

## Summary (3 sentences)

## Key Findings (with citations)
1. Finding — [Source](URL) (Primary, 2026, reliability 0.95)
2. Finding — [Source](URL) + Corroborated by [Source2](URL)

## Evidence Quality
- Total sources: N (Primary: X, Secondary: Y)
- Freshness: N from 2026, M from 2025
- Contradictions found: N (see below)

## Contradictions Preserved
- Claim A says X [Source1] vs Claim B says Y [Source2] → Stronger: Source1 because...

## Limitations
- What was NOT found
- What remains uncertain
- What would require deeper search

## Files
- Evidence graph: ./evidence/evidence-graph.md
- Sources: ./evidence/sources.md
```

**Evidence files are the REAL deliverable** — the report is the summary of them.

---

## Performance Tips

| Optimization | Why | How |
|---|---|---|
| **Parallel 3-5** | 15x token cost but huge quality on broad questions | Fire sub-queries at once |
| **Browser over snippet** | Snippets miss 80% of content | Always browser-load top 3 after web_search |
| **File persistence** | Survives 200K truncation | Save every source to ./evidence/ immediately |
| **Site-filter first** | Official docs > SEO blogs | First query always with site:official-domain |
| **Date-filter** | Avoids stale 2023 answers | Add 2026 or after:2025-01-01 |
| **Contradiction query** | Prevents confirmation bias | Always run one counter-evidence search |

---

*Next: `07-Multi-Agent.md` — Hermes Swarm.*
