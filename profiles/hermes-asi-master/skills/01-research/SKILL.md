---
name: hermes-research
description: Hermes Research & Evidence Synthesis — 5-pass research protocol, evidence graph generation, primary source verification, and contradiction detection.
version: "2.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: ['hermes', 'research', 'evidence', 'verification', 'citations']
    category: hermes-advanced
    requires_tools: ['web_search', 'browser', 'file_read', 'file_write']
    requires_toolsets: ['web']
---
# SKILL 01 â€” RESEARCH & EVIDENCE SYNTHESIS

> **Load this skill when:** Task needs internet facts, source verification, contradiction checks, or evidence graphs.
> **Pairs with:** `07-hermes-search` for Hermes live web_search. Use this skill for RESEARCH LOGIC, use 07 for HERMES EXECUTION.

---

## 1. Research Engine â€” 5 Passes

```
PASS 1 â€” DISCOVERY
  Terminology, major entities, candidate solutions, source landscape, obvious contradictions, recent developments.
  â†’ Output: discovery_map.md

PASS 2 â€” EVIDENCE
  For each important claim: primary source, supporting evidence, source date, confidence, conflicting evidence.
  â†’ Output: evidence collected per claim

PASS 3 â€” ADVERSARIAL VERIFICATION
  Actively search for: counterexamples, contradictory docs, failure reports, version differences,
  discontinued features, hidden constraints, benchmark limits, misleading claims.
  â†’ Output: contradictions.md

PASS 4 â€” SYNTHESIS
  Build evidence matrix:

  | Claim | Evidence | Source Quality | Freshness | Contradiction | Confidence |
  |-------|----------|----------------|-----------|---------------|------------|

PASS 5 â€” STRATEGIC DISCOVERY [ASI]
  What does this research IMPLY? What opportunities, risks, cross-domain transfers does it reveal
  that the original question didn't ask?
  â†’ Output: strategic_implications.md
```

## 2. Evidence Graph

For every consequential claim:

```
claim â†’ primary source â†’ independent source â†’ contradiction search â†’ freshness check
      â†’ adversarial challenge â†’ formal verification attempt â†’ confidence update
```

```yaml
claim:
  id: C-001
  text: ""
  status: fact | observed | sourced | inferred | hypothesis | prediction | assumption | unknown | contradicted | obsolete
  bayesian_prior: 0.0
  bayesian_posterior: 0.0
  sources: [{url: "", type: primary|secondary, date: ""}]
  confidence: 0.0-1.0
  verification_method: ""
  falsification_test: "what would prove this wrong"
  last_verified: ""
  expires_at: ""
  conflicting_claims: []
```

Prefer primary evidence. Never use search snippets as final evidence when the underlying source can be inspected.

## 3. Source Reliability Scoring

```
reliability = authority + primary_status + recency + transparency + corroboration
            + specificity + independence + reproducibility
            - conflict_of_interest - unverifiable_claims - stale - circular_citation
```

| Signal | High (Use) | Low (Skip/Verify) |
|--------|------------|-------------------|
| Authority | Official docs, primary source, peer-reviewed | Random blog, SEO farm |
| Freshness | 2025-2026 for time-sensitive | Last updated 2022 |
| Independence | 3 separate domains agree | 3 sites copying one release |
| Primary | Source IS the creator | Source talks ABOUT creator |

## 4. Contradiction Engine

```
belief â†’ support search â†’ contradiction search â†’ â‰¥3 alternative explanations
       â†’ adversarial challenge â†’ independent verification â†’ Bayesian update
```

When conflicting: `detect â†’ preserve BOTH â†’ compare provenance â†’ check timestamps â†’ check scope â†’ discriminating test â†’ adjudicate â†’ record`. Never silently overwrite.

## 5. Stopping Rule

```
VOI = P(research changes decision) Ã— expected_benefit + strategic_discovery_value âˆ’ research_cost
Stop when VOI < threshold AND Pass 5 yields no high-value opportunities.
```

Never research forever. Never stop before Pass 5 has checked for non-obvious implications.

## 6. Query Compilation (for any search tool)

Decompose 1 user question into 3-7 parallel sub-queries:

- One per sub-question, with `site:` and date filters
- Vary phrasing (same fact, 2 phrasings)
- Include one counter-query: `"{topic} limitations OR issues"`
- Parallelize (3-5 simultaneous searches)

## 7. Output Contract â€” Research Deliverable

```markdown
# Research Report: {Question}
## Key Findings (with citations)
1. Finding â€” [Source](URL) (Primary, 2026, reliability 0.95)
## Evidence Quality
- Total sources: N (Primary: X), Freshness: N from 2026, Contradictions: N
## Contradictions Preserved
- X vs Y â†’ Stronger: X because...
## Limitations
- What was NOT found, what remains uncertain
```

---

*Research Skill v9.0 â€” Pairs with 07-hermes-search for live execution on Hermes.*

