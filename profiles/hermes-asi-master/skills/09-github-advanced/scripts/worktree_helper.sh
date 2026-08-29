#!/bin/bash
# worktree_helper.sh — Hermes GitHub Advanced Helper Script
# Per official Hermes skill guideline: Include Helper Scripts
# Usage: bash worktree_helper.sh create <task-id> <branch> | list | cleanup <task-id>

set -e

cmd="$1"

case "$cmd" in
  create)
    task_id="$2"
    branch="$3"
    if [ -z "$task_id" ] || [ -z "$branch" ]; then
      echo "Usage: bash worktree_helper.sh create <task-id> <branch>"
      exit 1
    fi
    path="../hermes-worktree-$task_id"
    echo "Creating worktree $path for branch $branch..."
    git worktree add "$path" -b "$branch"
    echo "Created: $path → $branch"
    git worktree list
    ;;
  list)
    git worktree list
    ;;
  cleanup)
    task_id="$2"
    if [ -z "$task_id" ]; then
      echo "Usage: bash worktree_helper.sh cleanup <task-id>"
      exit 1
    fi
    path="../hermes-worktree-$task_id"
    branch=$(git worktree list | grep "$path" | awk '{print $2}' | tr -d '[]')
    echo "Removing worktree $path (branch $branch)..."
    git worktree remove "$path" --force 2>/dev/null || git worktree remove "$path"
    if [ -n "$branch" ] && [ "$branch" != "main" ]; then
      git branch -d "$branch" 2>/dev/null || echo "Branch $branch not deleted (has unmerged commits — delete manually if needed)"
    fi
    git worktree prune
    echo "Cleaned up $task_id"
    ;;
  *)
    echo "Usage:"
    echo "  bash worktree_helper.sh create <task-id> <branch>  # Create worktree + branch"
    echo "  bash worktree_helper.sh list                        # List worktrees"
    echo "  bash worktree_helper.sh cleanup <task-id>           # Remove worktree + branch"
    exit 1
    ;;
esac
