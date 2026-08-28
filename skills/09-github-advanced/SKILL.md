---
name: hermes-github-advanced
description: Hermes GitHub Highly Advanced — Worktree isolation, merge strategies, subagent swarm on parallel worktrees, multi-project synthesis, and MCP GitHub integration. The most advanced GitHub execution skill for Hermes.
version: "1.0 Advanced"
author: Hermes Advanced Team
license: MIT
metadata:
  hermes:
    tags: [hermes, github, worktree, merge, subagent, multi-project, mcp, advanced]
    category: hermes-advanced
    requires_tools: [terminal]
    requires_toolsets: [terminal]
---

# SKILL 09 — GITHUB HIGHLY ADVANCED

> **Load this skill when:** Task involves GitHub, git worktree, merging, parallel subagents on different branches, combining multiple projects, or MCP GitHub integration.
> **Pairs with:** `03-orchestration` (swarm) + `04-tools` (terminal) + `08-project-synthesis` (multi-project reuse)
> **Hermes GitHub Law:** *One task = One worktree = One subagent = Isolated, reversible, merge-ready.*

---

## 0. PURPOSE — WHY GITHUB IS THE MOST ADVANCED

GitHub is not just code hosting. For Hermes, GitHub is **the operating system for advanced work**:

- **Worktree** = Parallel universes — Hermes runs 3-5 tasks on the same repo without branch switching
- **Merge** = Verified integration — Hermes proves synthesis is more advanced than any source
- **Subagent** = Swarm on GitHub — Each Hermes worker gets its own worktree, isolated, no pollution
- **Multi-Project** = Synthesis — Hermes takes best features from Project A + B + C and composes one advanced project
- **MCP** = Hermes → GitHub as API — Hermes reads issues, PRs, reviews, and actions via Model Context Protocol

This skill makes Hermes **GitHub-superintelligent**.

---

## 1. GIT WORKTREE — HERMES PARALLEL UNIVERSES

### 1.1 Why Worktree (Not Branch Switching)

| Branch Switching (Basic) | Worktree (Advanced) |
|---|---|
| One working directory, switch branches = stash/pop, slow, error-prone | **Multiple working directories**, one per branch, simultaneous |
| Cannot run 2 tasks on same repo in parallel | **Hermes runs 3-5 parallel subagents**, each in its own worktree |
| Subagent pollutes main context | **Each worktree is isolated** — no pollution, no stash |
| Merge conflicts discovered late | **Conflicts detected early** per worktree |

### 1.2 Hermes Worktree Protocol

```bash
# Hermes creates isolated worktree per subagent task

# 1. Create worktree for a feature branch (Hermes subagent A)
git worktree add ../hermes-worktree-feature-a -b feature/a

# 2. Create worktree for another feature (Hermes subagent B, in parallel)
git worktree add ../hermes-worktree-feature-b -b feature/b

# 3. Create worktree for hotfix (Hermes subagent C, in parallel)
git worktree add ../hermes-worktree-hotfix -b hotfix/urgent

# Now Hermes has 3 parallel universes:
#   ./                  → main (Hermes master)
#   ../hermes-worktree-feature-a → feature/a (Worker A, isolated)
#   ../hermes-worktree-feature-b → feature/b (Worker B, isolated)
#   ../hermes-worktree-hotfix   → hotfix/urgent (Worker C, isolated)
```

**Hermes Worktree Commands:**

```bash
git worktree list                          # List all worktrees (Hermes checks)
git worktree add <path> -b <branch>        # Create new worktree + branch
git worktree add <path> <existing-branch>  # Create worktree for existing branch
git worktree remove <path>                 # Remove worktree (keep branch)
git worktree remove --force <path>         # Force remove (dirty worktree)
git worktree lock <path>                   # Lock worktree (prevent accidental removal)
git worktree unlock <path>                 # Unlock
git worktree prune                         # Clean stale worktree metadata
git worktree repair                        # Repair after manual move
```

**Hermes Worktree Naming (Professional):**

```
../hermes-worktree-{task-id}-{slug}

Examples:
  ../hermes-worktree-01-research-hermes-docs
  ../hermes-worktree-02-feature-auth
  ../hermes-worktree-03-fix-memory-leak
```

### 1.3 Hermes Worktree + Subagent — The Power Combo

This is where Hermes is **highly advanced**:

```
Hermes Master (main worktree: ./ )
    │
    ├── Subagent A → Worktree: ../hermes-worktree-feature-a (branch: feature/a)
    │       └── Task: Implement feature A (isolated, no pollution)
    │
    ├── Subagent B → Worktree: ../hermes-worktree-feature-b (branch: feature/b)
    │       └── Task: Implement alternative approach B (isolated, parallel)
    │
    └── Subagent C → Worktree: ../hermes-worktree-hotfix (branch: hotfix/urgent)
            └── Task: Fix critical bug (isolated, urgent, no interference)

Each subagent:
  - Gets ONE worktree
  - Gets ONE branch
  - Gets ONE objective (from delegation contract)
  - Has isolated file system, isolated context, isolated git history
  - Reports via result contract (artifacts, evidence, confidence)
  - Hermes master collects → evaluates → best-component synthesis → merge
```

**Hermes Delegation → Worktree Mapping:**

```yaml
delegation:
  id: D-01
  objective: "Implement search feature"
  worktree: ../hermes-worktree-D01-search
  branch: feature/search
  base: main
  subagent: hermes-worker-D01
```

---

## 2. MERGE — HERMES VERIFIED INTEGRATION

### 2.1 Merge Strategies (Hermes Chooses)

| Strategy | Command | When Hermes Uses It | Advanced? |
|----------|---------|---------------------|-----------|
| **Merge Commit** | `git merge feature/a` | Preserve full history, feature branch visible | Standard |
| **Squash** | `git merge --squash feature/a` | Single clean commit, hide WIP history | Clean history |
| **Rebase** | `git rebase main` (on feature branch) | Linear history, no merge commits | Advanced, clean |
| **Cherry-Pick** | `git cherry-pick <commit>` | Take specific commits from another branch | Surgical |
| **Octopus** | `git merge feature/a feature/b feature/c` | Merge multiple branches at once | Highly advanced |

**Hermes Merge Decision:**

```
If feature is isolated and should be atomic → Squash
If feature history is valuable and should be preserved → Merge Commit
If linear history required (project convention) → Rebase
If taking best commits from multiple workers → Cherry-Pick (best-component synthesis)
If merging 3 parallel worker results at once → Octopus
```

### 2.2 Hermes Merge Protocol — Verified Integration

Hermes **never merges without verification**:

```bash
# Hermes verified merge (in main worktree)

# 1. Fetch first
git fetch origin

# 2. Create integration branch from main (isolated)
git worktree add ../hermes-worktree-integration -b integration/verify

# 3. Merge feature branch (or cherry-pick best commits)
cd ../hermes-worktree-integration
git merge --no-commit feature/a          # Try merge, don't commit yet
# OR for best-component synthesis:
git cherry-pick <commit-from-worker-A>   # Best feature from Worker A
git cherry-pick <commit-from-worker-B>   # Best feature from Worker B

# 4. Verify in integration worktree (BEFORE committing)
# Run tests, 12 gates, independent verifier
npm test                  # or pytest, cargo test, etc.
# If fails → abort merge, report, fix

# 5. Check conflicts
git status                # Any conflicts?
# If conflicts → resolve, test again, verify

# 6. Commit verified merge
git commit -m "Merge feature/a: <description> [Hermes verified, 12 gates pass]"

# 7. Push (only after verification)
git push origin integration/verify

# 8. Create PR (via gh or MCP)
gh pr create --title "Merge feature/a" --body "Verified: 12 gates pass, evidence in ./evidence/"
```

**Hermes Merge Rule:** *No merge without verification. No push without evidence.*

### 2.3 Conflict Resolution — Hermes Advanced

```bash
# When merge conflicts occur in integration worktree

# 1. Detect
git merge feature/a
# → CONFLICT in file.js

# 2. Isolate conflict per file
git status                          # See conflicted files
git diff --check                    # See conflict markers

# 3. Resolve (Hermes chooses: take master, take feature, or synthesize)
# Option A: Take feature version
git checkout --theirs file.js
# Option B: Take main version
git checkout --ours file.js
# Option C: Manual synthesis (most advanced — combine both)
#   Edit file.js to combine best of both

# 4. Mark resolved + verify
git add file.js
npm test                            # Verify merge still works

# 5. Complete merge
git commit -m "Merge feature/a with conflict resolution in file.js"
```

---

## 3. SUBAGENT SWARM ON GITHUB — PARALLEL WORKTREES

### 3.1 Hermes Swarm + Worktree Architecture

```
Hermes Master (main: ./ on branch main)
    │
    ├── Delegation D-01 → Subagent 1 → Worktree ../hermes-worktree-D01 (branch: feature/D01)
    │       └── Task: Research + implement approach A
    │
    ├── Delegation D-02 → Subagent 2 → Worktree ../hermes-worktree-D02 (branch: feature/D02)
    │       └── Task: Research + implement alternative approach B
    │
    └── Delegation D-03 → Subagent 3 → Worktree ../hermes-worktree-D03 (branch: feature/D03)
            └── Task: Security + performance review

All 3 worktrees run IN PARALLEL, isolated, no branch switching, no stash.

Hermes Master:
  Collects results via result contract
  → Evaluates: which approach is best?
  → Best-component synthesis: Take best code from D-01 + best tests from D-02
  → Verifies in integration worktree
  → Creates PR with provenance
```

### 3.2 Hermes Worktree Lifecycle (Managed)

```bash
# Hermes manages full lifecycle per subagent

# SPAWN
git worktree add ../hermes-worktree-D01 -b feature/D01
# Delegate to subagent with worktree path in context

# EXECUTE (subagent works in its worktree, isolated)
cd ../hermes-worktree-D01
# ... subagent does work, commits to feature/D01 ...

# COLLECT (master collects result + branch)
git fetch origin
git log feature/D01 --oneline          # See worker's commits
git diff main..feature/D01             # See worker's changes

# EVALUATE (master evaluates in parallel for each worker)
# Score: functional fit, code quality, tests, coverage

# SYNTHESIZE (cherry-pick best commits)
git worktree add ../hermes-worktree-integration -b integration/synthesis
cd ../hermes-worktree-integration
git cherry-pick <best-commit-from-D01>
git cherry-pick <best-commit-from-D02>

# VERIFY (in integration worktree)
npm test && npm run lint

# MERGE (if verified)
git checkout main
git merge integration/synthesis

# CLEANUP (after merge)
git worktree remove ../hermes-worktree-D01
git worktree remove ../hermes-worktree-D02
git worktree remove ../hermes-worktree-integration
git branch -d feature/D01 feature/D02
git worktree prune
```

---

## 4. MULTI-PROJECT SYNTHESIS — MERGE THE IMPORTANT WORK

This is the **most advanced Hermes GitHub skill** — taking best work from **multiple separate GitHub projects/repos** and merging into one advanced synthesis.

### 4.1 When to Use Multi-Project

```
Problem: "Build an AI dashboard like Product X but open source"

Hermes finds:
  Project A (github.com/orgA/dashboard) — Best UI (MIT)
  Project B (github.com/orgB/agent-harness) — Best agent logic (Apache)
  Project C (github.com/orgC/memory-system) — Best memory (MIT)

Hermes must MERGE the important work from A + B + C into ONE new advanced project.
```

### 4.2 Hermes Multi-Project Strategies

| Strategy | Git Command | When |
|----------|-------------|------|
| **Submodule** | `git submodule add <url> <path>` | Keep projects as dependencies, not merged (track upstream) |
| **Subtree** | `git subtree add --prefix=<path> <url> <branch> --squash` | Merge project history into subdirectory |
| **Cherry-Pick Cross-Repo** | `git fetch <remote> && git cherry-pick <commit>` | Take specific commits from another repo |
| **Patch** | `git format-patch` + `git apply` | Take diff as patch, apply |
| **Manual Refeature** | Copy + adapt specific files/modules | Take best features, rewrite glue (most advanced, most control) |

**Hermes Decision:**

```
If projects are independent dependencies → Submodule
If projects should be merged with history → Subtree
If taking specific commits → Cherry-Pick Cross-Repo
If taking best features to compose new architecture → Manual Refeature (flagship, most advanced)
```

### 4.3 Hermes Manual Refeature — Flagship Multi-Project

```bash
# Hermes flagship: Manual Refeature (most advanced)

# 1. Scaffold new synthesis project
mkdir hermes-synthesis-dashboard && cd hermes-synthesis-dashboard
git init

# 2. Take UI from Project A (MIT — reuse)
git remote add projectA https://github.com/orgA/dashboard.git
git fetch projectA
git checkout projectA/main -- src/ui/          # Take UI module
cp -r /tmp/projectA/src/ui ./src/ui            # With attribution

# 3. Take agent logic from Project B (Apache — modify)
git remote add projectB https://github.com/orgB/agent-harness.git
git fetch projectB
git checkout projectB/main -- src/agent/       # Take agent module
# Modify to add Hermes integration
# ... Hermes modifies src/agent/ ...

# 4. Build glue + new synthesis features (Hermes invents)
# Write src/glue/ that connects UI + agent logic
# Add Feature Z that neither project had

# 5. Document provenance
cat > PROVENANCE.md << 'EOF'
## Provenance
- UI: Project A (MIT, github.com/orgA/dashboard, commit abc123) — reused as-is
- Agent: Project B (Apache 2.0, github.com/orgB/agent-harness, commit def456) — modified
- Glue + Feature Z: Hermes built from scratch (novel synthesis)
EOF

# 6. Verify (12 gates, feature matrix proves more advanced)
# Feature Matrix:
#   Feature X: A✅ B❌ → Synthesis ✅ (from A)
#   Feature Y: A❌ B✅ → Synthesis ✅ (from B)
#   Feature Z: A❌ B❌ → Synthesis ✅ (Hermes invented) → Proof synthesis > any source

# 7. Commit with provenance
git add .
git commit -m "Hermes synthesis: UI from Project A + agent from Project B + novel Z

Provenance:
- Project A (MIT): src/ui/
- Project B (Apache): src/agent/ (modified)
- Hermes: src/glue/ + Feature Z

More advanced than any single source: 95% vs 60% max"
```

### 4.4 Hermes Worktree + Multi-Project Combo

**Most advanced of all:**

```
Hermes master (main worktree: ./hermes-synthesis-dashboard)

  Worktree 1: ../hermes-worktree-projectA-integration
    → Integrates Project A components (isolated)

  Worktree 2: ../hermes-worktree-projectB-integration
    → Integrates Project B components (isolated)

  Worktree 3: ../hermes-worktree-synthesis
    → Composes A + B + novel glue (isolated, flagship)

All 3 IN PARALLEL, isolated, no pollution.
Master collects → best-component synthesis → verified merge → deliver.
```

---

## 5. MCP — HERMES → GITHUB AS API

**MCP (Model Context Protocol)** lets Hermes talk to GitHub as an API — read issues, PRs, reviews, actions, without shell.

### 5.1 MCP GitHub Server

```yaml
# In Hermes MCP config (gateway or config.yaml)

mcp:
  servers:
    github:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}  # From ~/.hermes/.env
```

**Tools MCP Gives Hermes:**

| MCP GitHub Tool | Hermes Uses It For |
|---|---|
| `mcp_github_list_issues` | Search GitHub issues for problem context |
| `mcp_github_get_issue` | Read specific issue + comments |
| `mcp_github_create_issue` | Create issue for tracked work |
| `mcp_github_list_prs` | Find PRs to review or merge |
| `mcp_github_get_pr` | Read PR diff + reviews |
| `mcp_github_create_pr` | Create PR with Hermes verification evidence |
| `mcp_github_merge_pr` | Merge verified PR |
| `mcp_github_list_commits` | Audit history |
| `mcp_github_search_repos` | Open source discovery (alternative to web_search) |
| `mcp_github_get_file` | Read repo files without cloning |

### 5.2 Hermes MCP Workflows

**Workflow 1: Hermes Creates Verified PR via MCP**

```
Hermes (via MCP, no shell):
  1. mcp_github_create_pr(
       repo: "org/repo",
       title: "Hermes: Add search superintelligence",
       body: "Verified: 12 gates pass\nEvidence: ./evidence/evidence-graph.md\nProvenance: ...",
       head: "feature/search",
       base: "main"
     )
  → PR created with Hermes verification evidence in body
```

**Workflow 2: Hermes Reviews PR via MCP**

```
Hermes:
  1. mcp_github_get_pr(repo: "org/repo", pr_number: 123)
  → Gets diff + reviews
  2. Hermes analyzes diff (via 05-safety-evaluation + formal verification)
  3. Posts review via MCP or terminal
```

**Workflow 3: Hermes Multi-Project Discovery via MCP**

```
Hermes:
  1. mcp_github_search_repos(query: "agent dashboard language:typescript stars:>1000")
  → Finds candidate projects to evaluate (alternative to web_search)
  2. For each candidate: mcp_github_get_file(path: "README.md", repo: "org/repo")
  → Reads README without cloning
  3. Scores via evaluation matrix (08-project-synthesis)
```

### 5.3 Hermes Terminal vs MCP — When to Use Which

| Task | Use Terminal (`gh`, `git`) | Use MCP (`mcp_github_*`) |
|------|---------------------------|--------------------------|
| Worktree, merge, rebase, cherry-pick | ✅ Terminal is only way | ❌ MCP has no worktree |
| `git` history, branching, submodules | ✅ Terminal | ❌ |
| List/search issues, PRs | ✅ `gh issue list` | ✅ MCP (cleaner, no parsing) |
| Create PR with body | ✅ `gh pr create` | ✅ MCP (structured) |
| Review PR diff | ✅ `gh pr diff` | ✅ MCP (no clone needed) |
| Search repos | ✅ `gh search repos` | ✅ MCP (structured JSON) |

**Hermes Advanced Rule:** Use **terminal for git worktree/merge** (only terminal can do it), use **MCP for GitHub API** (issues, PRs, search — cleaner than parsing `gh` output).

---

## 6. HERMES GITHUB CLI (gh) — QUICK REFERENCE

```bash
# Auth (once)
gh auth login

# Worktree + Branch
git worktree add ../hermes-worktree-feature -b feature/my-feature
gh pr create --title "Hermes: feature" --body "Verified: 12 gates pass"
gh pr view 123 --json title,body,state
gh pr merge 123 --squash --delete-branch

# Issues
gh issue list --limit 10 --search "bug"
gh issue view 42 --json title,body,comments
gh issue create --title "Hermes: fix" --body "Found via search"

# Search
gh search repos "agent dashboard language:typescript stars:>1000" --limit 10
gh search issues "memory leak" --repo org/repo

# Multi-Project
gh repo clone org/projectA ../projectA
gh repo fork org/projectA --clone=false
```

---

## 7. TEMPLATES & REFERENCES

- **Templates:** `templates/worktree-setup.md` — Hermes worktree creation checklist
- **References:** `references/github-queries.md` — Copy-paste `gh` + MCP queries

---

## 8. VERIFICATION — GITHUB ADVANCED

Hermes never delivers GitHub work without:

```
1. Worktree isolation verified (each subagent in its own worktree)
2. Merge verified (tests pass in integration worktree before push)
3. License compliance (MIT/Apache attribution, GPL disclosure)
4. Provenance documented (what came from which worktree/project, which commit)
5. PR body has evidence (12 gates, feature matrix, evidence graph link)
```

---

*SKILL 09 — Hermes GitHub Highly Advanced. Worktree + Merge + Subagent swarm on parallel worktrees + Multi-project synthesis + MCP GitHub API. The most advanced GitHub execution skill for Hermes.*
*GitHub is the highly advanced thing — Hermes makes it superintelligent.*
