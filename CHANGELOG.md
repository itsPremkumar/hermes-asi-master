# Changelog — HERMES Advanced

All notable changes to Hermes Advanced are documented here. Format based on Keep a Changelog.

---

## [2.0 Advanced] — 2026-08-28

### Added
- **15-Plane Architecture** (12 → 15): Added Strategic Superintelligence, Formal Verification, Self-Evolution planes
- **Hermes Search Superintelligence** (`skills/07-search-optimized`): 5 parallel `web_search` + `browser` extraction + evidence graph + contradiction search + second wave (flagship)
- **Hermes Swarm** (`skills/03-orchestration`): 30+ specialist roles, 3-5 parallel Hermes workers with isolated contexts, best-component synthesis, debate protocol
- **Project Synthesis Engine** (`skills/08-project-synthesis`): Any problem → search open + closed → evaluate (8 criteria) → reuse/modify/combine/inspire/scratch → deliver advanced synthesis with provenance
- **GitHub Highly Advanced** (`skills/09-github-advanced`): Worktree isolation, verified merge (5 strategies), subagent swarm on parallel worktrees, multi-project synthesis (submodule/subtree/refeature), MCP GitHub API
- **Hub Recommended** (`skills/10-hub-recommended`): Top 5 Skills Hub skills to augment Hermes (github-pr-workflow, merge-reconciler, codebase-inspection, git-worktree, delegate-to-hermes)
- **R0-R6 Risk Tiers** (added R6 Existential with multi-party approval) + **22 Invariants** (added ASI corrigibility + anti-power-seeking) + **12 Quality Gates** (added Formal Proof + Strategic Trajectory)
- **10 Docs** → Professional: `AGENTS.md` (official project context), `MEMORY.md`/`USER.md` at root, skill templates in `skills/<skill>/templates/`
- **Professional Files:** `.gitignore` (Hermes worktrees, secrets), `LICENSE` (MIT), `CHANGELOG.md`, `SECURITY.md`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `skills/*/scripts/` helper scripts

### Changed
- **Professional Refactor:** `AGENT.md` (singular, non-standard) → `AGENTS.md` (official Hermes project context)
- **Config:** `config/` + 3 profiles → single `config.yaml` at root (official: `~/.hermes/config.yaml`)
- **Memory:** `memory/MEMORY.md` → `MEMORY.md` at root (official: `~/.hermes/MEMORY.md`)
- **Evidence:** `evidence/template/` (top-level) → `skills/07-search-optimized/templates/` (per official skill structure)
- **Frontmatter:** All 10 skills upgraded to official `metadata.hermes.requires_tools` standard

### Removed
- `deployment/install.ps1` + `install.sh` (use official `hermes setup` + `hermes skills install`)
- `examples/` (merged into `SKILL.md` procedure via progressive disclosure)
- `docs/` 9 → 2 essential (Architecture + Search-Optimization); common workflows are in `SKILL.md`

---

## [1.0] — 2026-08-28 (Initial Hermes-Optimized)

- Initial Hermes-optimized skill from `HERMES-OPTIMIZED-SKILL.md` (v1.0)
- Basic Hermes toolset: `web_search`, `file_read`, `terminal_exec`
- Single `SKILL.md` without modular skills

---

## [Unreleased]

- Planned: Additional Hub skills from `hermesatlas.com/lists/top-skills` based on usage
- Planned: `skills/08-project-synthesis` auto-evolution with skill self-improvement during use
