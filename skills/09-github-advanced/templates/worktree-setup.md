# Worktree Setup — Template

> Copy-paste for Hermes per subagent. One worktree per task.

## Per Subagent

```bash
# Hermes creates isolated worktree for Delegation D-XX

# 1. Create worktree + branch from main
git worktree add ../hermes-worktree-DXX -b feature/DXX

# 2. Verify
git worktree list

# 3. Subagent works in its worktree
cd ../hermes-worktree-DXX
# ... do work, commit to feature/DXX ...

# 4. Master collects
cd ../main
git fetch origin
git log feature/DXX --oneline
git diff main..feature/DXX

# 5. After merge, cleanup
git worktree remove ../hermes-worktree-DXX
git branch -d feature/DXX
git worktree prune
```

## Naming

```
../hermes-worktree-{id}-{slug}
Examples: ../hermes-worktree-01-search, ../hermes-worktree-02-auth
```

## Rules

- One task = One worktree = One branch = One subagent
- Never share worktree between subagents
- Always verify in integration worktree before merging to main

---

*Template: skills/09-github-advanced/templates/worktree-setup.md*
