"""
Phase 2 Persistent Intelligence — Self Model

Tracks the agent's capabilities, limitations, and interaction history.
Supports self-assessment, capability discovery, and persistent learning
from interactions.
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
class Capability:
    """A capability the agent possesses."""
    id: str
    name: str
    description: str = ""
    proficiency: float = 0.5
    category: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    usage_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Capability":
        return cls(**d)


@dataclass
class Limitation:
    """A known limitation of the agent."""
    id: str
    name: str
    description: str = ""
    severity: float = 0.5
    category: str = "general"
    workaround: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Limitation":
        return cls(**d)


@dataclass
class InteractionRecord:
    """A record of an interaction or task execution."""
    id: str
    task_type: str
    description: str = ""
    success: bool = True
    duration_seconds: float = 0.0
    feedback: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "InteractionRecord":
        return cls(**d)


class SelfModel:
    """Thread-safe persistent self-model with capabilities, limitations, and history."""

    def __init__(self, storage_path: str = "./state/self") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self._capabilities: dict[str, Capability] = {}
        self._limitations: dict[str, Limitation] = {}
        self._interactions: list[InteractionRecord] = []
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        """Lazily load state from disk."""
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "self.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for cap_data in data.get("capabilities", []):
                    cap = Capability.from_dict(cap_data)
                    self._capabilities[cap.id] = cap
                for lim_data in data.get("limitations", []):
                    lim = Limitation.from_dict(lim_data)
                    self._limitations[lim.id] = lim
                for int_data in data.get("interactions", []):
                    interaction = InteractionRecord.from_dict(int_data)
                    self._interactions.append(interaction)
            except (json.JSONDecodeError, KeyError):
                self._capabilities = {}
                self._limitations = {}
                self._interactions = []
        self._loaded = True

    def _save(self) -> None:
        """Persist current state to disk atomically."""
        state_path = os.path.join(self.storage_path, "self.json")
        data = {
            "capabilities": [c.to_dict() for c in self._capabilities.values()],
            "limitations": [l.to_dict() for l in self._limitations.values()],
            "interactions": [i.to_dict() for i in self._interactions[-1000:]],  # Keep last 1000
            "version": "1.0",
        }
        atomic_file_write(state_path, data)

    def add_capability(
        self,
        name: str,
        description: str = "",
        proficiency: float = 0.5,
        category: str = "general",
        metadata: dict[str, Any] | None = None,
        capability_id: str | None = None,
    ) -> Capability:
        """Register a new capability."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if capability_id is None:
                capability_id = hashlib.md5(f"{name}:{category}".encode()).hexdigest()[:12]
            cap = Capability(
                id=capability_id,
                name=name,
                description=description,
                proficiency=proficiency,
                category=category,
                metadata=metadata or {},
            )
            self._capabilities[cap.id] = cap
            self._save()
            return cap

    def get_capability(self, capability_id: str) -> Optional[Capability]:
        """Retrieve a capability by ID."""
        with self._lock:
            self._ensure_loaded()
            return self._capabilities.get(capability_id)

    def find_capabilities(
        self,
        category: str | None = None,
        min_proficiency: float = 0.0,
    ) -> list[Capability]:
        """Find capabilities by category or proficiency threshold."""
        with self._lock:
            self._ensure_loaded()
            results = []
            for cap in self._capabilities.values():
                if category and cap.category != category:
                    continue
                if cap.proficiency < min_proficiency:
                    continue
                results.append(cap)
            results.sort(key=lambda c: c.proficiency, reverse=True)
            return results

    def update_proficiency(self, capability_id: str, new_proficiency: float) -> Optional[Capability]:
        """Update a capability's proficiency."""
        with self._lock:
            self._ensure_loaded()
            cap = self._capabilities.get(capability_id)
            if not cap:
                return None
            cap.proficiency = min(1.0, max(0.0, new_proficiency))
            cap.usage_count += 1
            cap.updated_at = time.time()
            self._save()
            return cap

    def add_limitation(
        self,
        name: str,
        description: str = "",
        severity: float = 0.5,
        category: str = "general",
        workaround: str = "",
        metadata: dict[str, Any] | None = None,
        limitation_id: str | None = None,
    ) -> Limitation:
        """Register a known limitation."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if limitation_id is None:
                limitation_id = hashlib.md5(f"{name}:{category}".encode()).hexdigest()[:12]
            lim = Limitation(
                id=limitation_id,
                name=name,
                description=description,
                severity=severity,
                category=category,
                workaround=workaround,
                metadata=metadata or {},
            )
            self._limitations[lim.id] = lim
            self._save()
            return lim

    def get_limitation(self, limitation_id: str) -> Optional[Limitation]:
        """Retrieve a limitation by ID."""
        with self._lock:
            self._ensure_loaded()
            return self._limitations.get(limitation_id)

    def find_limitations(
        self,
        category: str | None = None,
        min_severity: float = 0.0,
    ) -> list[Limitation]:
        """Find limitations by category or severity threshold."""
        with self._lock:
            self._ensure_loaded()
            results = []
            for lim in self._limitations.values():
                if category and lim.category != category:
                    continue
                if lim.severity < min_severity:
                    continue
                results.append(lim)
            results.sort(key=lambda l: l.severity, reverse=True)
            return results

    def record_interaction(
        self,
        task_type: str,
        description: str = "",
        success: bool = True,
        duration_seconds: float = 0.0,
        feedback: str = "",
        metadata: dict[str, Any] | None = None,
        interaction_id: str | None = None,
    ) -> InteractionRecord:
        """Record an interaction or task execution."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if interaction_id is None:
                interaction_id = hashlib.md5(
                    f"{task_type}:{time.time()}".encode()
                ).hexdigest()[:12]
            record = InteractionRecord(
                id=interaction_id,
                task_type=task_type,
                description=description,
                success=success,
                duration_seconds=duration_seconds,
                feedback=feedback,
                metadata=metadata or {},
            )
            self._interactions.append(record)
            self._save()
            return record

    def get_interactions(
        self,
        task_type: str | None = None,
        success: bool | None = None,
        limit: int = 100,
    ) -> list[InteractionRecord]:
        """Get interaction history, optionally filtered."""
        with self._lock:
            self._ensure_loaded()
            results = []
            for interaction in reversed(self._interactions):
                if task_type and interaction.task_type != task_type:
                    continue
                if success is not None and interaction.success != success:
                    continue
                results.append(interaction)
                if len(results) >= limit:
                    break
            return results

    def get_self_assessment(self) -> dict[str, Any]:
        """Generate a self-assessment summary."""
        with self._lock:
            self._ensure_loaded()
            total_interactions = len(self._interactions)
            successful = sum(1 for i in self._interactions if i.success)
            success_rate = successful / total_interactions if total_interactions > 0 else 0.0
            return {
                "total_capabilities": len(self._capabilities),
                "total_limitations": len(self._limitations),
                "total_interactions": total_interactions,
                "success_rate": success_rate,
                "avg_proficiency": (
                    sum(c.proficiency for c in self._capabilities.values()) / len(self._capabilities)
                    if self._capabilities else 0.0
                ),
                "avg_severity": (
                    sum(l.severity for l in self._limitations.values()) / len(self._limitations)
                    if self._limitations else 0.0
                ),
            }

    def list_all(self) -> dict[str, list]:
        """Return all self-model data."""
        with self._lock:
            self._ensure_loaded()
            return {
                "capabilities": list(self._capabilities.values()),
                "limitations": list(self._limitations.values()),
                "interactions": list(self._interactions),
            }

    def clear(self) -> None:
        """Clear all self-model data."""
        with self._lock:
            self._capabilities = {}
            self._limitations = {}
            self._interactions = []
            self._save()
