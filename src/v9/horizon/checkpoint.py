"""
v9 Long-Horizon Engineering — Checkpoint System

State checkpoint system for long-running workflows.
Supports incremental checkpoints, state versioning, and restoration.
"""

from __future__ import annotations
import asyncio
import copy
import hashlib
import json
import logging
import os
import pickle
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CheckpointStrategy(Enum):
    FULL = "full"           # Full state snapshot
    INCREMENTAL = "incremental"  # Only changes since last
    DELTA = "delta"         # Delta encoding


@dataclass
class Checkpoint:
    id: str
    workflow_id: str
    step: int
    state: dict
    metadata: dict
    parent_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    checksum: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:12]
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute SHA256 checksum of state."""
        state_bytes = json.dumps(self.state, sort_keys=True, default=str).encode()
        return hashlib.sha256(state_bytes).hexdigest()[:16]

    def verify(self) -> bool:
        """Verify checkpoint integrity."""
        return self.checksum == self._compute_checksum()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "step": self.step,
            "state": self.state,
            "metadata": self.metadata,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Checkpoint":
        return cls(
            id=data.get("id", ""),
            workflow_id=data["workflow_id"],
            step=data["step"],
            state=data["state"],
            metadata=data.get("metadata", {}),
            parent_id=data.get("parent_id"),
            created_at=data.get("created_at", time.time()),
            checksum=data.get("checksum", ""),
        )


class CheckpointStore:
    """Backend storage for checkpoints."""

    def __init__(self, base_path: str = ".checkpoints"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, checkpoint: Checkpoint) -> str:
        """Save checkpoint to storage."""
        workflow_dir = self.base_path / checkpoint.workflow_id
        workflow_dir.mkdir(parents=True, exist_ok=True)

        path = workflow_dir / f"checkpoint_{checkpoint.step:04d}_{checkpoint.id}.json"
        with open(path, "w") as f:
            json.dump(checkpoint.to_dict(), f, indent=2, default=str)

        logger.info(f"Checkpoint saved: {path}")
        return str(path)

    def load(self, workflow_id: str, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint by ID."""
        workflow_dir = self.base_path / workflow_id
        if not workflow_dir.exists():
            return None

        for path in workflow_dir.glob(f"*_{checkpoint_id}.json"):
            with open(path) as f:
                data = json.load(f)
                return Checkpoint.from_dict(data)

        return None

    def get_latest(self, workflow_id: str) -> Optional[Checkpoint]:
        """Get the latest checkpoint for a workflow."""
        workflow_dir = self.base_path / workflow_id
        if not workflow_dir.exists():
            return None

        checkpoints = list(workflow_dir.glob("checkpoint_*.json"))
        if not checkpoints:
            return None

        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        with open(latest) as f:
            data = json.load(f)
            return Checkpoint.from_dict(data)

    def list_checkpoints(self, workflow_id: str) -> list[Checkpoint]:
        """List all checkpoints for a workflow."""
        workflow_dir = self.base_path / workflow_id
        if not workflow_dir.exists():
            return []

        result = []
        for path in sorted(workflow_dir.glob("checkpoint_*.json")):
            with open(path) as f:
                data = json.load(f)
                result.append(Checkpoint.from_dict(data))

        return result

    def delete(self, workflow_id: str, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        workflow_dir = self.base_path / workflow_id
        if not workflow_dir.exists():
            return False

        for path in workflow_dir.glob(f"*_{checkpoint_id}.json"):
            path.unlink()
            return True

        return False

    def cleanup(self, workflow_id: str, keep_last: int = 5):
        """Keep only the last N checkpoints."""
        checkpoints = self.list_checkpoints(workflow_id)
        if len(checkpoints) <= keep_last:
            return

        to_delete = checkpoints[:-keep_last]
        for cp in to_delete:
            self.delete(workflow_id, cp.id)


class CheckpointManager:
    """Manage checkpoint lifecycle."""

    def __init__(
        self,
        workflow_id: str,
        store: Optional[CheckpointStore] = None,
        strategy: CheckpointStrategy = CheckpointStrategy.FULL,
        auto_checkpoint_interval: int = 10,
    ):
        self.workflow_id = workflow_id
        self.store = store or CheckpointStore()
        self.strategy = strategy
        self.auto_checkpoint_interval = auto_checkpoint_interval
        self._step = 0
        self._last_state: Optional[dict] = None
        self._checkpoints: list[Checkpoint] = []

    @property
    def current_step(self) -> int:
        return self._step

    def step(self):
        """Advance step counter."""
        self._step += 1

    def should_checkpoint(self) -> bool:
        """Determine if we should checkpoint at this step."""
        if self._step == 1:
            return True
        return self._step % self.auto_checkpoint_interval == 0

    def save(self, state: dict, metadata: Optional[dict] = None) -> Checkpoint:
        """Save a checkpoint."""
        if self.strategy == CheckpointStrategy.INCREMENTAL and self._last_state:
            checkpoint_state = self._compute_delta(self._last_state, state)
        else:
            checkpoint_state = copy.deepcopy(state)

        checkpoint = Checkpoint(
            id="",
            workflow_id=self.workflow_id,
            step=self._step,
            state=checkpoint_state,
            metadata=metadata or {},
            parent_id=self._checkpoints[-1].id if self._checkpoints else None,
        )

        self.store.save(checkpoint)
        self._checkpoints.append(checkpoint)
        self._last_state = copy.deepcopy(state)

        return checkpoint

    def restore(self, checkpoint_id: Optional[str] = None) -> Optional[dict]:
        """Restore from a checkpoint."""
        if checkpoint_id:
            checkpoint = self.store.load(self.workflow_id, checkpoint_id)
        else:
            checkpoint = self.store.get_latest(self.workflow_id)

        if not checkpoint:
            return None

        if not checkpoint.verify():
            raise ValueError(f"Checkpoint {checkpoint.id} failed integrity check")

        state = checkpoint.state
        if self.strategy == CheckpointStrategy.INCREMENTAL and checkpoint.parent_id:
            parent = self.store.load(self.workflow_id, checkpoint.parent_id)
            if parent:
                state = self._apply_delta(parent.state, state)

        self._step = checkpoint.step
        return state

    def get_history(self) -> list[Checkpoint]:
        """Get checkpoint history."""
        return self.store.list_checkpoints(self.workflow_id)

    def _compute_delta(self, old: dict, new: dict) -> dict:
        """Compute delta between states."""
        delta = {}
        for key in new:
            if key not in old or old[key] != new[key]:
                delta[key] = new[key]
        return delta

    def _apply_delta(self, base: dict, delta: dict) -> dict:
        """Apply delta to base state."""
        result = copy.deepcopy(base)
        result.update(delta)
        return result


class AsyncCheckpointManager(CheckpointManager):
    """Async-aware checkpoint manager."""

    async def save_async(self, state: dict, metadata: Optional[dict] = None) -> Checkpoint:
        """Save checkpoint asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.save, state, metadata)

    async def restore_async(self, checkpoint_id: Optional[str] = None) -> Optional[dict]:
        """Restore checkpoint asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.restore, checkpoint_id)
