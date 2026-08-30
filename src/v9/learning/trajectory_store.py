"""
trajectory_store.py — Store and query execution trajectories.

A trajectory is a sequence of steps an agent took to complete a task.
Trajectories can be stored, queried, and analyzed for patterns.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import time
import json
import hashlib


@dataclass
class TrajectoryStep:
    """A single step in a trajectory."""
    step_num: int
    action: str
    observation: str
    result: str
    success: bool
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> dict:
        return {
            "step_num": self.step_num,
            "action": self.action,
            "observation": self.observation,
            "result": self.result,
            "success": self.success,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class Trajectory:
    """A complete execution trajectory."""
    task: str
    steps: list[TrajectoryStep]
    success: bool
    total_reward: float = 0.0
    duration_ms: float = 0.0
    trajectory_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.trajectory_id:
            content = f"{self.task}:{len(self.steps)}:{time.time()}"
            self.trajectory_id = hashlib.md5(content.encode()).hexdigest()[:12]

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def success_rate(self) -> float:
        if not self.steps:
            return 0.0
        return sum(1 for s in self.steps if s.success) / len(self.steps)

    def to_dict(self) -> dict:
        return {
            "trajectory_id": self.trajectory_id,
            "task": self.task,
            "steps": [s.to_dict() for s in self.steps],
            "success": self.success,
            "total_reward": self.total_reward,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class TrajectoryStore:
    """
    Store for execution trajectories.

    Supports adding, querying, and analyzing trajectories.
    """

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.trajectories: dict[str, Trajectory] = {}
        self.task_index: dict[str, list[str]] = {}  # task -> trajectory_ids

    def add(self, trajectory: Trajectory) -> str:
        """
        Add a trajectory to the store.

        Returns:
            The trajectory ID
        """
        if len(self.trajectories) >= self.max_size:
            # Remove oldest trajectory
            oldest_id = next(iter(self.trajectories))
            self.remove(oldest_id)

        self.trajectories[trajectory.trajectory_id] = trajectory

        # Index by task
        task_key = trajectory.task.lower()
        if task_key not in self.task_index:
            self.task_index[task_key] = []
        self.task_index[task_key].append(trajectory.trajectory_id)

        return trajectory.trajectory_id

    def get(self, trajectory_id: str) -> Optional[Trajectory]:
        """Get a trajectory by ID."""
        return self.trajectories.get(trajectory_id)

    def remove(self, trajectory_id: str) -> bool:
        """Remove a trajectory."""
        trajectory = self.trajectories.pop(trajectory_id, None)
        if trajectory:
            task_key = trajectory.task.lower()
            if task_key in self.task_index:
                self.task_index[task_key] = [
                    tid for tid in self.task_index[task_key] if tid != trajectory_id
                ]
            return True
        return False

    def find_by_task(self, task: str) -> list[Trajectory]:
        """Find trajectories by task name."""
        task_key = task.lower()
        ids = self.task_index.get(task_key, [])
        return [self.trajectories[tid] for tid in ids if tid in self.trajectories]

    def find_successful(self) -> list[Trajectory]:
        """Find all successful trajectories."""
        return [t for t in self.trajectories.values() if t.success]

    def find_failed(self) -> list[Trajectory]:
        """Find all failed trajectories."""
        return [t for t in self.trajectories.values() if not t.success]

    def search(self, query: str) -> list[Trajectory]:
        """Search trajectories by content."""
        query_lower = query.lower()
        results = []
        for t in self.trajectories.values():
            if query_lower in t.task.lower():
                results.append(t)
                continue
            for step in t.steps:
                if (query_lower in step.action.lower() or
                    query_lower in step.result.lower()):
                    results.append(t)
                    break
        return results

    def get_all(self) -> list[Trajectory]:
        """Get all trajectories."""
        return list(self.trajectories.values())

    def get_statistics(self) -> dict[str, Any]:
        """Get store statistics."""
        if not self.trajectories:
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "avg_steps": 0,
                "avg_reward": 0,
            }

        total = len(self.trajectories)
        successful = sum(1 for t in self.trajectories.values() if t.success)
        failed = total - successful
        avg_steps = sum(t.step_count for t in self.trajectories.values()) / total
        avg_reward = sum(t.total_reward for t in self.trajectories.values()) / total

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total,
            "avg_steps": avg_steps,
            "avg_reward": avg_reward,
        }

    def clear(self) -> None:
        """Clear all trajectories."""
        self.trajectories.clear()
        self.task_index.clear()

    def __len__(self) -> int:
        return len(self.trajectories)
