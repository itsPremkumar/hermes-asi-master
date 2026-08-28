# Merge Verification — Template

> Hermes verified merge checklist — no merge without verification.

## Verified Merge Steps

```bash
# In integration worktree (NOT main)
git worktree add ../hermes-worktree-integration -b integration/verify
cd ../hermes-worktree-integration

# Try merge (no commit)
git merge --no-commit feature/my-feature
# OR cherry-pick best commits:
git cherry-pick <commit-from-worker-A>
git cherry-pick <commit-from-worker-B>

# Verify
npm test                    # or pytest, cargo test
npm run lint
git status                  # conflicts?

# If conflicts:
#   git checkout --theirs <file>  # or --ours, or manual synthesis
#   git add <file>
#   npm test                    # verify again

# Commit only if verified
git commit -m "Merge feature/my-feature: <desc> [Hermes verified, 12 gates pass]"

# Push only after verification
git push origin integration/verify

# Create PR
gh pr create --title "Hermes: feature" --body "Verified: 12 gates pass, evidence in ./evidence/"
```

## Checklist

- [ ] Merge tried in integration worktree (not main)
- [ ] Tests pass
- [ ] Lint passes
- [ ] Conflicts resolved (if any) and re-verified
- [ ] Commit has Hermes verification note
- [ ] PR body has evidence

---

*Template: skills/09-github-advanced/templates/merge-verification.md*
