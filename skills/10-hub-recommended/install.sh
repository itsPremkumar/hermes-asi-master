#!/bin/bash
# install.sh — HERMES Hub Recommended — Install Top 5 Hub Skills
# Run: bash skills/10-hub-recommended/install.sh

echo "=== HERMES Hub Recommended — Installing Top 5 Skills ==="
echo "These augment your 9 Hermes Advanced skills with proven Hub implementations"
echo ""

skills=(
  "hermes skills install official/github/github-pr-workflow # builtin - always trusted"
  "hermes skills install official/ai-agents/merge-reconciler # builtin - always trusted"
  "hermes skills install official/devops/codebase-inspection # builtin - always trusted"
  "hermes skills install antjanus/skillbox --skill git-worktree # community - inspect first"
  "npx skills add bassemZohdy/delegate-skills --skill delegate-to-hermes # community - inspect first"
)

for cmd in "${skills[@]}"; do
  echo "Run: $cmd"
done

echo ""
echo "=== After installing, verify: ==="
echo "hermes skills list | grep -E 'github-pr-workflow|merge-reconciler|codebase-inspection|git-worktree|delegate-to-hermes'"
echo ""
echo "=== Security: Always inspect community skills first: ==="
echo "hermes skills inspect antjanus/skillbox --skill git-worktree"
