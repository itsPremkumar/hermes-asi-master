"""
t_f0087914 — Harness Engineering Loop

Complete engineering harness for repository model, code generation,
CI/CD, debugging, and release management.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def atomic_file_write(path: str, data: dict | list) -> None:
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


@dataclass
class Repository:
    """A git repository."""
    id: str
    name: str
    path: str
    remote_url: str = ""
    default_branch: str = "main"
    branches: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Repository":
        return cls(**d)


@dataclass
class PullRequest:
    """A pull request."""
    id: str
    repo_id: str
    title: str
    source_branch: str
    target_branch: str
    description: str = ""
    status: str = "open"  # open, merged, closed
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PullRequest":
        return cls(**d)


class RepositoryModel:
    """Git repository abstraction with branch and PR management."""

    def __init__(self, storage_path: str = "./state/repos") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self.repos: dict[str, Repository] = {}
        self.prs: dict[str, PullRequest] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "repos.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for repo_data in data.get("repos", []):
                    repo = Repository.from_dict(repo_data)
                    self.repos[repo.id] = repo
                for pr_data in data.get("prs", []):
                    pr = PullRequest.from_dict(pr_data)
                    self.prs[pr.id] = pr
            except (json.JSONDecodeError, KeyError):
                pass
        self._loaded = True

    def _save(self) -> None:
        state_path = os.path.join(self.storage_path, "repos.json")
        data = {
            "repos": [r.to_dict() for r in self.repos.values()],
            "prs": [p.to_dict() for p in self.prs.values()],
        }
        atomic_file_write(state_path, data)

    def create_repo(self, name: str, path: str, remote_url: str = "") -> Repository:
        """Register a repository."""
        repo = Repository(
            id=str(uuid.uuid4().hex[:8]),
            name=name,
            path=path,
            remote_url=remote_url,
            branches=["main"],
        )
        self.repos[repo.id] = repo
        self._save()
        return repo

    def get_repo(self, repo_id: str) -> Optional[Repository]:
        return self.repos.get(repo_id)

    def list_repos(self) -> list[Repository]:
        return list(self.repos.values())

    def create_branch(self, repo_id: str, branch_name: str, base: str = "main") -> bool:
        """Create a new branch in a repo."""
        repo = self.repos.get(repo_id)
        if not repo:
            return False
        if branch_name not in repo.branches:
            repo.branches.append(branch_name)
            self._save()
        return True

    def create_pr(
        self,
        repo_id: str,
        title: str,
        source_branch: str,
        target_branch: str = "main",
        description: str = "",
    ) -> Optional[PullRequest]:
        """Create a pull request."""
        repo = self.repos.get(repo_id)
        if not repo:
            return None
        pr = PullRequest(
            id=str(uuid.uuid4().hex[:8]),
            repo_id=repo_id,
            title=title,
            source_branch=source_branch,
            target_branch=target_branch,
            description=description,
        )
        self.prs[pr.id] = pr
        self._save()
        return pr

    def merge_pr(self, pr_id: str) -> bool:
        """Merge a pull request."""
        pr = self.prs.get(pr_id)
        if not pr or pr.status != "open":
            return False
        pr.status = "merged"
        self._save()
        return True

    def get_prs(self, repo_id: str | None = None, status: str | None = None) -> list[PullRequest]:
        """Get PRs, optionally filtered."""
        results = []
        for pr in self.prs.values():
            if repo_id and pr.repo_id != repo_id:
                continue
            if status and pr.status != status:
                continue
            results.append(pr)
        return results

    def run_git(self, repo_id: str, *args: str) -> tuple[int, str, str]:
        """Run a git command in a repo."""
        repo = self.repos.get(repo_id)
        if not repo:
            return 1, "", "Repo not found"
        try:
            result = subprocess.run(
                ["git", "-C", repo.path] + list(args),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Timeout"
        except Exception as e:
            return 1, "", str(e)
