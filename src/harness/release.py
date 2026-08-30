"""
t_f0087914 — Release Management Module

Manage releases, changelogs, versioning.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
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
class ChangelogEntry:
    """A changelog entry."""
    type: str  # feat, fix, docs, refactor, test, chore
    description: str
    pr_id: str = ""
    author: str = ""


@dataclass
class Release:
    """A release."""
    id: str
    version: str
    branch: str
    status: str = "draft"  # draft, published, rolled_back
    entries: list[ChangelogEntry] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    published_at: float | None = None

    def add_entry(self, entry: ChangelogEntry) -> None:
        self.entries.append(entry)


class ReleaseManager:
    """Manage releases."""

    def __init__(self, storage_path: str = "./state/releases") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self.releases: dict[str, Release] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "releases.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for rel_data in data.get("releases", []):
                    entries = [ChangelogEntry(**e) for e in rel_data.get("entries", [])]
                    release = Release(
                        id=rel_data["id"],
                        version=rel_data["version"],
                        branch=rel_data["branch"],
                        status=rel_data.get("status", "draft"),
                        entries=entries,
                    )
                    self.releases[release.id] = release
            except (json.JSONDecodeError, KeyError):
                pass
        self._loaded = True

    def _save(self) -> None:
        state_path = os.path.join(self.storage_path, "releases.json")
        data = {
            "releases": [
                {
                    "id": r.id,
                    "version": r.version,
                    "branch": r.branch,
                    "status": r.status,
                    "entries": [
                        {"type": e.type, "description": e.description, "pr_id": e.pr_id, "author": e.author}
                        for e in r.entries
                    ],
                }
                for r in self.releases.values()
            ],
        }
        atomic_file_write(state_path, data)

    def create_release(self, version: str, branch: str = "main") -> Release:
        release = Release(
            id=str(uuid.uuid4().hex[:8]),
            version=version,
            branch=branch,
        )
        self.releases[release.id] = release
        self._save()
        return release

    def get_release(self, release_id: str) -> Optional[Release]:
        return self.releases.get(release_id)

    def list_releases(self) -> list[Release]:
        return list(self.releases.values())

    def publish_release(self, release_id: str) -> bool:
        release = self.releases.get(release_id)
        if not release or release.status != "draft":
            return False
        release.status = "published"
        release.published_at = time.time()
        self._save()
        return True

    def generate_changelog(self, release_id: str) -> str:
        release = self.releases.get(release_id)
        if not release:
            return ""
        lines = [f"# Release {release.version}", ""]
        by_type: dict[str, list[str]] = {}
        for entry in release.entries:
            by_type.setdefault(entry.type, []).append(entry.description)
        for type_name, descriptions in sorted(by_type.items()):
            lines.append(f"## {type_name}")
            for desc in descriptions:
                lines.append(f"- {desc}")
            lines.append("")
        return "\n".join(lines)
