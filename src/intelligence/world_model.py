"""
Phase 2 Persistent Intelligence — World Model

Structured representation of the agent's environment, entities, and their relationships.
Supports add, query, update, and persistence via atomic writes.
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
class Entity:
    """A thing in the world (object, person, concept, location, etc.)."""
    id: str
    name: str
    type: str = "object"
    properties: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Entity":
        return cls(**d)


@dataclass
class Relationship:
    """A directed relationship between two entities."""
    id: str
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Relationship":
        return cls(**d)


class WorldModel:
    """Thread-safe persistent world model with entities and relationships."""

    def __init__(self, storage_path: str = "./state/world") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[str, Relationship] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        """Lazily load state from disk."""
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "world.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for entity_data in data.get("entities", []):
                    entity = Entity.from_dict(entity_data)
                    self._entities[entity.id] = entity
                for rel_data in data.get("relationships", []):
                    rel = Relationship.from_dict(rel_data)
                    self._relationships[rel.id] = rel
            except (json.JSONDecodeError, KeyError):
                self._entities = {}
                self._relationships = {}
        self._loaded = True

    def _save(self) -> None:
        """Persist current state to disk atomically."""
        state_path = os.path.join(self.storage_path, "world.json")
        data = {
            "entities": [e.to_dict() for e in self._entities.values()],
            "relationships": [r.to_dict() for r in self._relationships.values()],
            "version": "1.0",
        }
        atomic_file_write(state_path, data)

    def add_entity(
        self,
        name: str,
        entity_type: str = "object",
        properties: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        entity_id: str | None = None,
    ) -> Entity:
        """Add a new entity to the world model."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if entity_id is None:
                entity_id = hashlib.md5(f"{name}:{entity_type}".encode()).hexdigest()[:12]
            entity = Entity(
                id=entity_id,
                name=name,
                type=entity_type,
                properties=properties or {},
                tags=tags or [],
            )
            self._entities[entity.id] = entity
            self._save()
            return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID."""
        with self._lock:
            self._ensure_loaded()
            return self._entities.get(entity_id)

    def find_entities(
        self,
        name: str | None = None,
        entity_type: str | None = None,
        tag: str | None = None,
    ) -> list[Entity]:
        """Find entities by name, type, or tag."""
        with self._lock:
            self._ensure_loaded()
            results = []
            for entity in self._entities.values():
                if name and name.lower() not in entity.name.lower():
                    continue
                if entity_type and entity.type != entity_type:
                    continue
                if tag and tag not in entity.tags:
                    continue
                results.append(entity)
            return results

    def update_entity(self, entity_id: str, **kwargs: Any) -> Optional[Entity]:
        """Update an entity's properties."""
        with self._lock:
            self._ensure_loaded()
            entity = self._entities.get(entity_id)
            if not entity:
                return None
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            entity.updated_at = time.time()
            self._save()
            return entity

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships."""
        with self._lock:
            self._ensure_loaded()
            if entity_id in self._entities:
                del self._entities[entity_id]
                # Remove related relationships
                to_delete = [
                    r.id for r in self._relationships.values()
                    if r.source_id == entity_id or r.target_id == entity_id
                ]
                for r_id in to_delete:
                    del self._relationships[r_id]
                self._save()
                return True
            return False

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> Optional[Relationship]:
        """Add a relationship between two entities."""
        import hashlib
        with self._lock:
            self._ensure_loaded()
            if source_id not in self._entities or target_id not in self._entities:
                return None
            rel_id = hashlib.md5(
                f"{source_id}:{target_id}:{relation_type}".encode()
            ).hexdigest()[:12]
            rel = Relationship(
                id=rel_id,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                metadata=metadata or {},
            )
            self._relationships[rel.id] = rel
            self._save()
            return rel

    def get_relationships(
        self,
        entity_id: str | None = None,
        relation_type: str | None = None,
    ) -> list[Relationship]:
        """Get relationships, optionally filtered by entity or type."""
        with self._lock:
            self._ensure_loaded()
            results = []
            for rel in self._relationships.values():
                if entity_id and rel.source_id != entity_id and rel.target_id != entity_id:
                    continue
                if relation_type and rel.relation_type != relation_type:
                    continue
                results.append(rel)
            return results

    def list_all(self) -> dict[str, list]:
        """Return all entities and relationships."""
        with self._lock:
            self._ensure_loaded()
            return {
                "entities": list(self._entities.values()),
                "relationships": list(self._relationships.values()),
            }

    def clear(self) -> None:
        """Clear all entities and relationships."""
        with self._lock:
            self._entities = {}
            self._relationships = {}
            self._save()
