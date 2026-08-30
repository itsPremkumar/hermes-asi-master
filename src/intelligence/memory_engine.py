"""
Phase 2 Persistent Intelligence — Memory Engine

Persistent memory with atomic writes, deduplication, and thread safety.
All state stored in JSON files at storage_path.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def atomic_file_write(path: str, data: dict | list) -> None:
    """Write data to file atomically using write-temp-fsync-rename."""
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
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: float | None = None
    embedding: list[float] | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MemoryEntry":
        return cls(**d)

    def touch(self) -> None:
        """Record an access to this memory."""
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryEngine:
    """Thread-safe persistent memory engine with deduplication."""

    def __init__(self, storage_path: str = "./state/memory") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self._entries: dict[str, MemoryEntry] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        """Lazily load state from disk."""
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "memory.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for entry_data in data.get("entries", []):
                    entry = MemoryEntry.from_dict(entry_data)
                    self._entries[entry.id] = entry
            except (json.JSONDecodeError, KeyError):
                self._entries = {}
        self._loaded = True

    def _save(self) -> None:
        """Persist current state to disk atomically."""
        state_path = os.path.join(self.storage_path, "memory.json")
        data = {
            "entries": [e.to_dict() for e in self._entries.values()],
            "version": "1.0",
        }
        atomic_file_write(state_path, data)

    def add(
        self,
        content: str,
        category: str = "general",
        tags: list[str] | None = None,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
        entry_id: str | None = None,
    ) -> MemoryEntry:
        """Add a new memory entry."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if entry_id is None:
                entry_id = hashlib.md5(content.encode()).hexdigest()[:12]
            # Deduplication: skip if content hash matches existing
            content_hash = hashlib.md5(content.encode()).hexdigest()
            for existing in self._entries.values():
                existing_hash = hashlib.md5(existing.content.encode()).hexdigest()
                if existing_hash == content_hash:
                    existing.touch()
                    self._save()
                    return existing

            entry = MemoryEntry(
                id=entry_id,
                content=content,
                category=category,
                tags=tags or [],
                importance=importance,
                metadata=metadata or {},
            )
            self._entries[entry.id] = entry
            self._save()
            return entry

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID."""
        with self._lock:
            self._ensure_loaded()
            entry = self._entries.get(entry_id)
            if entry:
                entry.touch()
                self._save()
            return entry

    def search(
        self,
        query: str,
        category: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search memories by content substring."""
        with self._lock:
            self._ensure_loaded()
            results = []
            query_lower = query.lower()
            for entry in self._entries.values():
                if category and entry.category != category:
                    continue
                if query_lower in entry.content.lower():
                    results.append(entry)
            results.sort(key=lambda e: e.importance, reverse=True)
            return results[:limit]

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry by ID."""
        with self._lock:
            self._ensure_loaded()
            if entry_id in self._entries:
                del self._entries[entry_id]
                self._save()
                return True
            return False

    def list_all(self) -> list[MemoryEntry]:
        """List all memory entries."""
        with self._lock:
            self._ensure_loaded()
            return list(self._entries.values())

    def clear(self) -> None:
        """Clear all memory entries."""
        with self._lock:
            self._entries = {}
            self._save()

    def count(self) -> int:
        """Return total number of entries."""
        with self._lock:
            self._ensure_loaded()
            return len(self._entries)
