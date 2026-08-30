"""
Phase 2 Persistent Intelligence — Belief Engine

Bayesian belief tracking with evidence accumulation, confidence scoring,
and revision. Supports adding evidence, updating beliefs, and querying
the belief state.
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
class Evidence:
    """A piece of evidence supporting or contradicting a belief."""
    id: str
    description: str
    source: str = "observation"
    type: str = "supporting"  # "supporting" or "contradicting"
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Evidence":
        return cls(**d)


@dataclass
class Belief:
    """A belief held by the agent, with associated evidence."""
    id: str
    statement: str
    confidence: float = 0.5
    category: str = "general"
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "statement": self.statement,
            "confidence": self.confidence,
            "category": self.category,
            "evidence": [e.to_dict() for e in self.evidence],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Belief":
        evidence = [Evidence.from_dict(e) for e in d.get("evidence", [])]
        return cls(
            id=d["id"],
            statement=d["statement"],
            confidence=d.get("confidence", 0.5),
            category=d.get("category", "general"),
            evidence=evidence,
            metadata=d.get("metadata", {}),
            created_at=d.get("created_at", time.time()),
            updated_at=d.get("updated_at", time.time()),
        )


class BeliefEngine:
    """Thread-safe persistent belief engine with Bayesian revision."""

    def __init__(self, storage_path: str = "./state/beliefs") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self._beliefs: dict[str, Belief] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        """Lazily load state from disk."""
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "beliefs.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for belief_data in data.get("beliefs", []):
                    belief = Belief.from_dict(belief_data)
                    self._beliefs[belief.id] = belief
            except (json.JSONDecodeError, KeyError):
                self._beliefs = {}
        self._loaded = True

    def _save(self) -> None:
        """Persist current state to disk atomically."""
        state_path = os.path.join(self.storage_path, "beliefs.json")
        data = {
            "beliefs": [b.to_dict() for b in self._beliefs.values()],
            "version": "1.0",
        }
        atomic_file_write(state_path, data)

    def add_belief(
        self,
        statement: str,
        confidence: float = 0.5,
        category: str = "general",
        metadata: dict[str, Any] | None = None,
        belief_id: str | None = None,
    ) -> Belief:
        """Add a new belief."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if belief_id is None:
                belief_id = hashlib.md5(statement.encode()).hexdigest()[:12]
            belief = Belief(
                id=belief_id,
                statement=statement,
                confidence=confidence,
                category=category,
                evidence=[],
                metadata=metadata or {},
            )
            self._beliefs[belief.id] = belief
            self._save()
            return belief

    def add_evidence(
        self,
        belief_id: str,
        description: str,
        evidence_type: str = "supporting",
        weight: float = 1.0,
        source: str = "observation",
        metadata: dict[str, Any] | None = None,
    ) -> Optional[Evidence]:
        """Add evidence to a belief."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            belief = self._beliefs.get(belief_id)
            if not belief:
                return None
            ev_id = hashlib.md5(f"{belief_id}:{description}".encode()).hexdigest()[:12]
            evidence = Evidence(
                id=ev_id,
                description=description,
                source=source,
                type=evidence_type,
                weight=weight,
                metadata=metadata or {},
            )
            belief.evidence.append(evidence)
            belief.updated_at = time.time()
            # Update confidence using simple Bayesian-like update
            self._update_confidence(belief)
            self._save()
            return evidence

    def _update_confidence(self, belief: Belief) -> None:
        """Update belief confidence based on accumulated evidence."""
        supporting = sum(
            e.weight for e in belief.evidence if e.type == "supporting"
        )
        contradicting = sum(
            e.weight for e in belief.evidence if e.type == "contradicting"
        )
        total = supporting + contradicting
        if total > 0:
            # Simple update: start at 0.5, move toward evidence ratio
            ratio = supporting / total
            # Bayesian update approximation
            belief.confidence = min(0.99, max(0.01, 0.5 + (ratio - 0.5) * total / (total + 1)))

    def get_belief(self, belief_id: str) -> Optional[Belief]:
        """Retrieve a belief by ID."""
        with self._lock:
            self._ensure_loaded()
            return self._beliefs.get(belief_id)

    def find_beliefs(
        self,
        category: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[Belief]:
        """Find beliefs by category or confidence threshold."""
        with self._lock:
            self._ensure_loaded()
            results = []
            for belief in self._beliefs.values():
                if category and belief.category != category:
                    continue
                if belief.confidence < min_confidence:
                    continue
                results.append(belief)
            results.sort(key=lambda b: b.confidence, reverse=True)
            return results

    def revise_belief(self, belief_id: str, new_confidence: float) -> Optional[Belief]:
        """Manually revise a belief's confidence."""
        with self._lock:
            self._ensure_loaded()
            belief = self._beliefs.get(belief_id)
            if not belief:
                return None
            belief.confidence = min(1.0, max(0.0, new_confidence))
            belief.updated_at = time.time()
            self._save()
            return belief

    def delete_belief(self, belief_id: str) -> bool:
        """Delete a belief."""
        with self._lock:
            self._ensure_loaded()
            if belief_id in self._beliefs:
                del self._beliefs[belief_id]
                self._save()
                return True
            return False

    def list_all(self) -> list[Belief]:
        """Return all beliefs."""
        with self._lock:
            self._ensure_loaded()
            return list(self._beliefs.values())

    def clear(self) -> None:
        """Clear all beliefs."""
        with self._lock:
            self._beliefs = {}
            self._save()
