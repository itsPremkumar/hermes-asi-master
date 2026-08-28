---
name: hermes-hub-recommended
description: Hermes Hub Recommended — Top 5 Skills Hub skills to augment Hermes Advanced (GitHub PR workflow, merge reconciler, codebase inspection, worktree, delegate). Install via hermes skills install.
version: "1.0"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, hub, recommended, github, worktree, synthesis]
    category: hermes-advanced
---

# SKILL 10 — HUB RECOMMENDED

> **Load this skill when:** You want to augment Hermes Advanced with proven **Skills Hub** skills (90K skills across 11 registries) instead of building from scratch.
> **Pairs with:** `08-project-synthesis` (search open source before building) + `09-github-advanced` (your custom GitHub skill)
> **Hub Law:** *Never build what the Hub already has. Always search the Hub first (Phase 2 of synthesis).*

---

## 0. PURPOSE — WHY THE HUB

The **Skills Hub** (`hermes-agent.nousresearch.com/docs/skills` + `agentskills.io`) is the **live, built-in installer** for Hermes — **90,697 skills** as of Aug 2026 across 11 registries (ClawHub 69K, skills.sh 19K, LobeHub, etc.). All follow the open `agentskills.io` standard.

Your `08-project-synthesis` says: *Search open source before building.* The Hub IS that search — for skills. Before building any Hermes feature from scratch, **search the Hub first**:

```bash
hermes skills search "worktree"
hermes skills search "github"
hermes skills search "research"
```

This skill curates the **Top 5 Hub skills** that directly augment your Hermes Advanced 9 skills.

---

## 1. TOP 5 RECOMMENDED — FOR YOUR HERMES ADVANCED

### For Skill 09 (GitHub Highly Advanced) — Your GitHub skill's allies:

| # | Hub Skill | What It Does | Why It Augments Your Skill 09 | Install |
|---|-----------|--------------|-------------------------------|---------|
| **1** | **`github-pr-workflow`** (✓ Built-in) | Full PR lifecycle: branch, commit, open, CI, merge | Your Skill 09 does worktree+merge manually via `git`. This skill gives Hermes a **proven PR workflow** to complement it. | `hermes skills install official/github/github-pr-workflow` |
| **2** | **`merge-reconciler`** (✓ Built-in) | Neutral third-party resolution of agent merge conflicts | Your Skill 09 swarm does best-component synthesis. This skill is the **neutral judge** when workers conflict — prevents master bias. | `hermes skills install official/ai-agents/merge-reconciler` |
| **3** | **`codebase-inspection`** (✓ Built-in) | Inspect codebases w/ pygount: LOC, languages, ratios | Your Skill 04 does tool registry. This gives **quantitative repo insights** before synthesis. | `hermes skills install official/devops/codebase-inspection` |
| **4** | **`git-worktree`** (antjanus/skillbox) | Parallel dev: hotfixes while on feature, `git worktree` automation | Your Skill 09 does worktree via `git` commands. This skill **automates worktree setup** (branch → worktree → env). | `hermes skills install antjanus/skillbox --skill git-worktree` |
| **5** | **`delegate-to-hermes`** (bassemZohdy/delegate-skills) | Delegate tasks to Hermes in worktree isolation with self-healing | Your Skill 03 does orchestration. This skill **delegates to Hermes itself** in isolated worktree + monitors + self-heals. | `npx skills add bassemZohdy/delegate-skills --skill delegate-to-hermes` |

**Bonus for Skill 07 (Search):**

| **6** | **`arxiv`** (✓ Built-in) | Search arXiv papers by keyword/author/category | Your Skill 07 does web_search. This adds **domain-specific paper search**. | `hermes skills install official/research/arxiv` |

---

## 2. HOW INSTALLING WORKS (Official Hub Flow)

```bash
# 1. Search the live 90K Hub
hermes skills search "worktree"
hermes skills search "github"

# 2. Inspect before installing (security — read the SKILL.md)
hermes skills inspect official/github/github-pr-workflow
hermes skills inspect antjanus/skillbox --skill git-worktree

# 3. Install (copies to ~/.hermes/skills/, becomes slash command)
hermes skills install official/github/github-pr-workflow
hermes skills install official/ai-agents/merge-reconciler
hermes skills install antjanus/skillbox --skill git-worktree

# 4. Verify
hermes skills list                          # See installed
hermes skills list --source hub             # See hub-installed

# 5. Use in chat (progressive disclosure: only name+desc loaded at start)
# Full SKILL.md loads on demand when task matches description
/github-pr-workflow Create a PR for the auth refactor
/merge-reconciler Resolve conflicts between feature/a and feature/b
```

**Progressive Disclosure (Official):**
1.  `skills_list()` — compact list of all skills (~3K tokens) — loaded at session start
2.  `skill_view(name)` — full `SKILL.md` — loaded when agent decides it needs that skill
3.  `skill_view(name, file_path)` — specific reference file — only if needed

→ You can install **hundreds of Hub skills** with only ~3K token cost at startup. Full content loads on demand.

---

## 3. SECURITY — READ BEFORE INSTALL

**Koi Security Audit (Feb 2026):** Of 2,857 ClawHub skills audited, **341 were outright malicious** (later 824 of 10,700). ClawHub is 69K of your 90K — the Hub's largest source is also the riskiest.

**Trust Levels:**

| Level | Source | Trust | Action |
|-------|--------|-------|--------|
| `builtin` | Ships with Hermes (81 skills) | **Always trusted** | Install freely |
| `official` | `optional-skills/` in NousResearch/hermes-agent (115 skills) | **Built-in trust** | Install freely |
| `trusted` | openai/skills, anthropics/skills, huggingface/skills | **Trusted** | Install freely |
| `community` | Everything else (90K, including ClawHub) | **Verify first** | `inspect` → `install --force` can override `caution`, never `dangerous` |

**Rule:** For anything touching credentials/email/money, prefer `builtin`, `official`, `trusted`. Always `inspect` — it's just markdown, read it.

**The 5 recommended above:** `github-pr-workflow`, `merge-reconciler`, `codebase-inspection` are `builtin` (always trusted). `git-worktree` and `delegate-to-hermes` are community — `inspect` first.

---

## 4. HOW THESE 5 AUGMENT YOUR 9 SKILLS

| Your Hermes Skill | Hub Skill Augmentation | Combined Result |
|---|---|---|
| `09-github-advanced` (worktree + merge via `git`) | `merge-reconciler` (neutral conflict resolver) | Your skill = Hermes worktree protocol. Hub skill = **neutral judge** when workers conflict. Together = **bulletproof parallel merges without master bias.** |
| `09-github-advanced` (worktree) | `git-worktree` (automation) | Your skill = `git worktree add` commands. Hub skill = **automates worktree setup** (branch → worktree → env → port allocation). |
| `07-search-optimized` (5 parallel search) | `arxiv` (paper search) | Your skill = web_search superintelligence. Hub skill = **domain-specific search** (papers, models). |
| `03-orchestration` (swarm) | `delegate-to-hermes` (delegate to Hermes itself) | Your skill = swarm delegation. Hub skill = **delegate to Hermes in isolated worktree with self-healing** (process exits → retry, log not growing → kill + continue). |
| `04-tools` (tool registry) | `codebase-inspection` (pygount) | Your skill = tool discovery. Hub skill = **quantitative repo metrics** (LOC, languages, ratios) before synthesis. |

**You keep your 9 custom advanced skills.** Hub skills are **proven implementations** that make your skills stronger — not replacements.

---

## 5. INSTALL ALL 5 — ONE COMMAND PER SKILL

```bash
# Run these 5 commands (copy-paste):

hermes skills install official/github/github-pr-workflow
hermes skills install official/ai-agents/merge-reconciler
hermes skills install official/devops/codebase-inspection
hermes skills install antjanus/skillbox --skill git-worktree
npx skills add bassemZohdy/delegate-skills --skill delegate-to-hermes

# Or use the install scripts in this skill:
#   ./install.ps1  (Windows)
#   ./install.sh   (Linux/macOS)

# Verify:
hermes skills list | grep -E "github-pr-workflow|merge-reconciler|codebase-inspection|git-worktree|delegate-to-hermes"
```

**Alternative — Taps (Private Registry):**

```bash
# Point Hermes at any GitHub repo full of SKILL.md folders → private registry
hermes skills tap add obra/superpowers          # #1 skill pack ★278K
hermes skills tap add your-org/private-skills    # Your own private skills
# No server, no sign-up — just a GitHub repo
# Set GITHUB_TOKEN to avoid 60 req/hour anonymous limit → 5,000 with token
```

---

## 6. DO CLAUDE CODE / OPENCLAW SKILLS WORK IN HERMES?

**Mostly, yes.** The `SKILL.md` core (name, description, markdown body, bundled files) is portable by design across everything that speaks the `agentskills.io` standard — which is why ClawHub and skills.sh can sit inside the Hermes Hub at all.

ClawHub is OpenClaw's marketplace, skills.sh is Vercel's directory — both are in your Hermes Hub. A skill built for Claude Code (e.g., `obra/superpowers`) installs into Hermes via `hermes skills install` and works because the format is shared.

**One caveat:** Hermes-specific features (`requires_tools`, `requires_toolsets`, `fallback_for_*`, `metadata.hermes.blueprint`) are Hermes-only — other agents ignore them, but the core still works.

---

## 7. BLUEPRINTS — SKILLS THAT ARE ALSO AUTOMATIONS

A **blueprint** is an ordinary skill with a schedule in frontmatter:

```yaml
metadata:
  hermes:
    blueprint:
      schedule: "0 8 * * *"
      deliver: telegram
      prompt: "Summarize my unread email"
```

→ Becomes a **suggested cron job** via `/suggestions` (opt-in, never auto-schedules):

```bash
/suggestions              # List pending
/suggestions accept 1     # Schedule suggestion 1
/suggestions dismiss 1    # Never offer again
```

Blueprints flow through the entire skills pipeline — search, inspect, install, security scan — like any skill.

---

*SKILL 10 — Hermes Hub Recommended. 5 top Hub skills to augment your 9 Hermes Advanced skills. Search the Hub before building — never build what already exists. From 90,697 skills across 11 registries, these 5 make your Hermes more advanced.*
