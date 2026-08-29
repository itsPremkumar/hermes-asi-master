---
name: hermes-search-optimized-agent
version: "1.0 Search-Optimized"
description: >
  Hermes AI Agent â€” Internet Search Super-Optimized Execution Protocol.
  Drop-in replacement for SKILL.md when your Hermes mission is SEARCH-HEAVY.
  Converts any research, investigation, or internet-dependent objective into
  verified, deep, parallel, evidence-backed web research through Hermes-native
  toolsets (web_search, browser, file_read/write, terminal_exec) with dynamic
  capability detection. Optimized for speed, depth, freshness, and source reliability.
  Pairs with SOUL.md v4.0 ASI (unchanged) for values and safety.
hermes:
  category: search-and-research
  tags: [hermes, internet-search, web-research, deep-research, verification, evidence-graph]
  requires: [web_search]
  recommends: [browser, file_read, file_write]
  toolsets_optimized: [web_search, browser, file_read, file_write, terminal_exec]
---

# HERMES â€” Internet Search Optimized Protocol v1.0

> **Use this file AS your `SKILL.md` when the task is search-heavy.**
> Keep `SOUL.md` v4.0 ASI as-is. Together: `SKILL-HERMES-SEARCH-OPTIMIZED.md` (how to search) + `SOUL.md` (who you are).
> For non-search tasks (pure coding, local ops), use `SKILL.md` v9.0 ASI instead.

---

## 0. PURPOSE â€” SEARCH AS SUPERPOWER

Hermes is not a chatbot that searches. Hermes is a **search-superintelligent research engine** that turns the entire internet into verified evidence.

**Principle:**

> **No important claim without a live source. No live source without verification. No verification without provenance.**

A Hermes search task is not complete because it returned links. It is complete when every important claim has a **live, fresh, independent, authoritative source with an evidence graph.**

---

## 1. HERMES SEARCH TOOLSET â€” OPTIMIZED CONFIG

### Required `config.yaml` for Search-Optimized Hermes

Copy this to `~/.hermes/config.yaml` (or your Hermes config path):

```yaml
# Model â€” needs >=64K context for deep research
provider: "anthropic"          # or "openrouter", "nous", "openai"
model: "anthropic/claude-sonnet-4"  # or your best research model

terminal:
  backend: "docker"            # most sandboxed you can use

memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 4000       # INCREASED for search (was 2200) â€” stores evidence graphs
  user_char_limit: 2000
  write_approval: true

# --- SEARCH-OPTIMIZED TOOLSETS ---
toolsets:
  enabled:
    - web_search               # REQUIRED â€” primary search
    - browser                  # REQUIRED for search-heavy â€” renders JS, bypasses snippet limits
    - file_read
    - file_write               # needed to save evidence graphs and reports
    - terminal_exec            # for curl, jq, data processing of search results
    # - messaging_send         # keep disabled unless task requires it

# Search tuning
search:
  default_results: 10
  max_parallel_searches: 5     # Hermes can run 3-5 searches in parallel
  timeout_seconds: 30
  freshness_preference: high   # prefer last 7-30 days for time-sensitive facts
  language: en
```

### How Hermes Discovers Tools at Runtime

Never hardcode tools. At task start, Hermes MUST:

```
1. List available toolsets from Hermes runtime
2. Confirm web_search is available â€” if not, STOP and report CAPABILITY_UNAVAILABLE
3. Prefer browser over web_search snippet when depth needed
4. Use file_write to persist every evidence graph (so it survives context truncation)
```

---

## 2. SEARCH-OPTIMIZED OPERATING LOOP

Standard loop is `RECEIVE â†’ RESEARCH â†’ PLAN â†’ EXECUTE â†’ VERIFY`. For search-heavy Hermes, it becomes:

```
USER QUESTION
  â†“
QUERY COMPILATION (decompose question into 3-7 searchable sub-queries)
  â†“
PARALLEL SEARCH (3-5 web_search + browser loads simultaneously)
  â†“
SOURCE TRIAGE (rank by authority, freshness, independence)
  â†“
DEEP EXTRACTION (browser load full pages, not snippets)
  â†“
EVIDENCE GRAPH (Claim â†’ Source â†’ Evidence â†’ Counter-evidence â†’ Confidence)
  â†“
CONTRADICTION SEARCH (actively seek disconfirming evidence)
  â†“
SYNTHESIS + GAP DETECTION (what is still unknown?)
  â†“
SECOND SEARCH WAVE (if gaps remain â€” new queries from synthesis)
  â†“
VERIFICATION (independent source per important claim)
  â†“
FINAL REPORT (with citations, limitations, freshness dates)
```

**Critical rule:** Never answer from memory when `web_search` is available and the fact is time-sensitive, external, or consequential. Memory is stale. Internet is live.

---

## 3. QUERY COMPILATION â€” HOW HERMES TURNS ONE QUESTION INTO 5 SEARCHES

A user asks one question. Hermes must compile it into **multiple parallel searches**:

**Example:** User: `"What is the latest Hermes Agent deployment best practice for 2026?"`

| Bad (1 vague search) | Good (5 parallel searches) |
|---|---|
| `hermes agent best practice` | `hermes agent deployment guide site:nousresearch.com` |
| | `hermes agent config.yaml best practice 2026` |
| | `hermes agent sandbox security 2025 2026` |
| | `hermes agent vs openclaw comparison 2026` |
| | `hermes agent memory tool approval 2026` |

**Hermes Query Compilation Rules:**

1.  **One search per sub-question** â€” Decompose complex question into atomic searchable facts
2.  **Add site: and date filters** â€” `site:official-docs`, `after:2025-01-01`, `2026`
3.  **Vary query phrasing** â€” Same fact with 2 different phrasings catches different sources
4.  **Include counter-query** â€” One search should seek disconfirming evidence: `"hermes agent limitations"`, `"hermes agent security issues"`
5.  **Parallelize** â€” Fire 3-5 searches simultaneously via Hermes parallel tool calling (not sequentially)

```yaml
query_plan:
  original: "user's raw question"
  sub_queries:
    - query: "primary fact search with site filter"
      purpose: "get authoritative source"
      required: true
    - query: "freshness check with 2026 date filter"
      purpose: "ensure not stale"
      required: true
    - query: "contradiction search"
      purpose: "find counter-evidence"
      required: true
  parallel_width: 5
  timeout: 30s
```

---

## 4. SOURCE TRIAGE â€” RANKING WHAT HERMES FOUND

Hermes may get 50 results. It must **triage** before deep reading:

| Signal | High Score (Use) | Low Score (Skip or Verify) |
|---|---|---|
| **Authority** | Official docs, primary source, .edu/.gov, peer-reviewed, maintainer repo | Random blog, SEO farm, unverified forum |
| **Freshness** | Updated 2025-2026 for time-sensitive facts | Last updated 2022 for a 2026 question |
| **Independence** | 3 separate domains saying same thing | 3 sites copying same press release |
| **Specificity** | Exact version, exact config, exact error | Vague "it works" |
| **Primary** | Source IS the creator (Nous docs for Hermes) | Source talks ABOUT the creator |

**Hermes Triage Action:**

```
For each search result:
  score = authority(0-3) + freshness(0-2) + independence(0-2) + specificity(0-2)
  if score >=6: browser load full page
  if score 3-5: snippet + flag as needs corroboration
  if score <3: skip unless nothing better exists
```

---

## 5. DEEP EXTRACTION â€” BEYOND SNIPPETS

**NEVER rely on web_search snippets as final evidence** when `browser` is available. Snippets are truncated, often stale, and miss key context.

**Hermes Extraction Protocol:**

```
web_search â†’ get top 5 URLs â†’ browser load each full page in parallel
  â†’ extract: {title, publish_date, author, main_content, code_blocks, tables}
  â†’ check: is this the primary source or a summary of another source?
  â†’ if summary: follow link to primary and load that too
  â†’ save evidence to file: ./evidence/{claim_id}.md with full provenance
```

**For each extracted page, Hermes records:**

```yaml
source:
  url: "https://..."
  title: ""
  author: ""
  publish_date: "2026-08-15"
  access_date: "2026-08-28"
  type: primary | secondary | tertiary
  reliability: 0.0-1.0
  extracted_facts:
    - claim: ""
      quote: "exact quote from page"
      location: "section heading"
```

---

## 6. EVIDENCE GRAPH â€” HERMES FILE-BASED

Because Hermes context can truncate at 200K tokens, **Hermes MUST persist evidence to files**, not just hold it in context.

**File structure Hermes creates per research task:**

```
./evidence/
â”œâ”€â”€ evidence-graph.md          # Master: Claim â†’ Source â†’ Confidence table
â”œâ”€â”€ sources.md                 # All sources with reliability scores
â”œâ”€â”€ contradictions.md          # Conflicting claims preserved
â””â”€â”€ raw/
    â”œâ”€â”€ source-01-hermes-docs.md
    â”œâ”€â”€ source-02-github.md
    â””â”€â”€ source-03-paper.md
```

**Master Evidence Graph Template (`evidence-graph.md`):**

```markdown
| # | Claim | Source | Type | Freshness | Reliability | Confidence | Contradiction |
|---|-------|--------|------|-----------|-------------|------------|---------------|
| 1 | Hermes requires >=64K context | nousresearch.com/docs | Primary | 2026 | 0.95 | confirmed | None |
| 2 | Hermes default write_approval is false | config.yaml docs | Primary | 2026 | 0.90 | strongly_supported | â€” |
```

---

## 7. CONTRADICTION SEARCH â€” HERMES RED-TEAM

After first synthesis, Hermes MUST run a **dedicated contradiction pass**:

```
Search query: "{original query} limitations OR issues OR problems OR deprecated"
Search query: "{original query} alternative OR vs OR comparison"
Action: Browser load contradictory source â†’ compare claims side-by-side
Output: contradictions.md with BOTH sides preserved
```

Never silently pick the more convenient answer. Preserve the conflict and report it to the user with which side has stronger evidence and why.

---

## 8. SECOND SEARCH WAVE â€” GAP CLOSURE

After first synthesis, Hermes asks:

```
What claims still lack independent corroboration?
What claims rely on a single source?
What fresh claims (2026) lack freshness verification?
â†’ Generate NEW targeted searches for those gaps
â†’ Fire second parallel wave (2-3 searches)
â†’ Merge results into evidence graph
```

A single search wave is never enough for complex questions. **Two waves is the Hermes minimum.**

---

## 9. HERMES SEARCH-OPTIMIZED PROMPTS

Use these exact query patterns for best Hermes web_search performance:

**For official docs:**
```
"{topic}" site:github.com/nousresearch OR site:nousresearch.com OR site:docs.hermes-agent.io after:2025-01-01
```

**For fresh information:**
```
"{topic}" 2026 -2023 -2024  (forces recent results, excludes stale)
```

**For security/best practice:**
```
"{topic}" security OR sandbox OR approval OR best practice 2026
```

**For troubleshooting:**
```
"{topic}" error OR issue OR fix site:github.com
```

---

## 10. FINAL REPORT â€” HERMES SEARCH DELIVERABLE

Every search-heavy Hermes task ends with this structure (saved as `report.md` + printed):

```markdown
# Research Report: {User Question}

## Summary (3 sentences, no citations needed)

## Key Findings (with citations)
1. Finding â€” [Source](URL) (Primary, 2026, reliability 0.95)
2. Finding â€” [Source](URL) + Corroborated by [Source2](URL)

## Evidence Quality
- Total sources: N (Primary: X, Secondary: Y)
- Freshness: N sources from 2026, M from 2025
- Contradictions found: N (see below)

## Contradictions Preserved
- Claim A says X [Source1] vs Claim B says Y [Source2] â†’ Stronger: Source1 because...

## Limitations
- What was NOT found
- What remains uncertain
- What would require deeper search

## Files
- Evidence graph: ./evidence/evidence-graph.md
- Sources: ./evidence/sources.md
```

---

## 11. HERMES SEARCH TUNING â€” PERFORMANCE TIPS

| Optimization | Why | How |
|---|---|---|
| **Parallel searches (3-5)** | 15x token cost but huge quality gain on broad questions | Fire all sub-queries at once, not sequentially |
| **Browser over snippets** | Snippets miss 80% of content | Always browser-load top 3 results after web_search |
| **File-based persistence** | Hermes context truncates at ~200K | Save every source to `./evidence/` immediately |
| **Site-filter first** | Official docs beat SEO blogs | First query always with `site:official-domain` |
| **Date-filter for freshness** | Avoids stale 2023 answers for 2026 question | Add `2026` or `after:2025-01-01` to time-sensitive queries |
| **Contradiction query** | Prevents confirmation bias | Always run one search for counter-evidence |

---

## 12. WHAT THIS OPTIMIZED SKILL DOES NOT DO

*   This skill optimizes **SEARCH**. It does NOT replace `SOUL.md` (values, safety) â€” keep SOUL.md loaded.
*   This skill does NOT give Hermes new capabilities â€” it organizes existing `web_search` + `browser` + `file_*` tools into a superior workflow.
*   For pure coding or local tasks with no internet need, use `SKILL.md` v9.0 ASI instead (faster, no unnecessary searches).

---

## Deployment (30 seconds)

```bash
# Option A: Search-heavy deployment (RECOMMENDED for your request)
cp SKILL-HERMES-SEARCH-OPTIMIZED.md ~/.hermes/skills/hermes-search/SKILL.md
cp AG-ASI-Ultimate/SOUL.md ~/.hermes/skills/hermes-search/SOUL.md
cp AG-ASI-Ultimate/deployment/config.yaml ~/.hermes/config.yaml
# Edit provider, model, and ensure toolsets.enabled includes web_search + browser

# Option B: Keep both skills and switch per task
# - Search tasks -> load SKILL-HERMES-SEARCH-OPTIMIZED.md
# - Build tasks  -> load SKILL.md v9.0 ASI
```

**Verify search is live:**
Give Hermes: *"Search the live web for 'Hermes Agent Nous Research latest release 2026' and report the publish date and URL of the primary source."* If it cites a live URL with a 2026 date, search optimization is active.

---

*Hermes Search-Optimized v1.0 â€” Pairs with SOUL.md v4.0 ASI. All search concepts from AGX, Hermes, and Deep Harness consolidated and super-optimized for internet search on Hermes.*

