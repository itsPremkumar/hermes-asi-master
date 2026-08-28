# MCP GitHub — Hermes Reference

> How Hermes talks to GitHub as API via Model Context Protocol.

## MCP Server Config

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

**.env:**
```
GITHUB_TOKEN=ghp_...
```

## MCP Tools

| MCP Tool | Purpose |
|----------|---------|
| `mcp_github_search_repos` | Search repos (alternative to web_search) |
| `mcp_github_get_file` | Read file without cloning |
| `mcp_github_list_issues` | List issues |
| `mcp_github_get_issue` | Read issue + comments |
| `mcp_github_create_issue` | Create issue |
| `mcp_github_list_prs` | List PRs |
| `mcp_github_get_pr` | Read PR diff + reviews |
| `mcp_github_create_pr` | Create PR |
| `mcp_github_merge_pr` | Merge PR |
| `mcp_github_list_commits` | Audit history |

## Workflows

**Create Verified PR:**
```
mcp_github_create_pr(repo: "org/repo", title: "Hermes: feature", body: "Verified: 12 gates pass", head: "feature/x", base: "main")
```

**Multi-Project Discovery:**
```
mcp_github_search_repos(query: "dashboard stars:>1000 language:typescript")
→ mcp_github_get_file(path: "README.md", repo: "org/repo") → score via 08-project-synthesis
```

## Terminal vs MCP

| Task | Terminal | MCP |
|------|----------|-----|
| Worktree, merge, rebase | ✅ Only way | ❌ No worktree |
| List/search issues, PRs | ✅ gh | ✅ MCP (cleaner JSON) |
| Search repos | ✅ gh search | ✅ MCP (structured) |

**Use terminal for git, MCP for GitHub API.**

---

*Reference: skills/09-github-advanced/references/mcp-github.md*
