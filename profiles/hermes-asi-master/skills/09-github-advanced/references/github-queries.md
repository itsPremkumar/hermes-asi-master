# GitHub Queries Reference — Hermes

> Copy-paste for Hermes via terminal (gh) or MCP.

## Worktree

```bash
git worktree list
git worktree add ../hermes-worktree-feature -b feature/my-feature
git worktree add ../hermes-worktree-hotfix hotfix/urgent  # existing branch
git worktree remove ../hermes-worktree-feature
git worktree remove --force ../hermes-worktree-feature
git worktree lock ../hermes-worktree-feature
git worktree prune
```

## Merge

```bash
git merge feature/a                          # merge commit
git merge --squash feature/a                 # squash
git rebase main                              # rebase (on feature branch)
git cherry-pick <commit>                     # surgical
git merge feature/a feature/b feature/c      # octopus
git checkout --theirs <file>                 # resolve: take feature
git checkout --ours <file>                   # resolve: take main
```

## GitHub CLI (gh)

```bash
gh auth login
gh pr create --title "Hermes: feature" --body "Verified: 12 gates pass"
gh pr view 123 --json title,body,state
gh pr merge 123 --squash --delete-branch
gh issue list --limit 10 --search "bug"
gh issue view 42 --json title,body,comments
gh issue create --title "Hermes: fix" --body "Found via search"
gh search repos "agent dashboard language:typescript stars:>1000" --limit 10
gh repo clone org/projectA ../projectA
gh repo fork org/projectA --clone=false
```

## Multi-Project

```bash
git submodule add https://github.com/org/project.git path/to/submodule
git subtree add --prefix=path/to/merge https://github.com/org/project.git main --squash
git remote add projectA https://github.com/orgA/project.git && git fetch projectA
git checkout projectA/main -- path/to/file
git fetch projectA && git cherry-pick <commit-from-projectA>
```

## MCP GitHub (Hermes → GitHub as API)

```
mcp_github_search_repos(query: "agent dashboard language:typescript stars:>1000")
mcp_github_get_file(path: "README.md", repo: "org/repo")
mcp_github_list_issues(repo: "org/repo", state: "open")
mcp_github_get_issue(repo: "org/repo", issue_number: 42)
mcp_github_create_issue(repo: "org/repo", title: "...", body: "...")
mcp_github_list_prs(repo: "org/repo")
mcp_github_get_pr(repo: "org/repo", pr_number: 123)
mcp_github_create_pr(repo: "org/repo", title: "...", body: "...", head: "feature/x", base: "main")
mcp_github_merge_pr(repo: "org/repo", pr_number: 123)
```

**Rule:** Terminal for git worktree/merge (only terminal can), MCP for GitHub API (cleaner JSON).

---

*Reference: skills/09-github-advanced/references/github-queries.md*
