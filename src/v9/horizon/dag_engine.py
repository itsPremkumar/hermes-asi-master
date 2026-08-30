"""
v9 Long-Horizon Engineering — DAG Engine

Directed Acyclic Graph task execution engine for long-horizon workflows.
Supports parallel execution, dependency resolution, and dynamic task injection.
"""

from __future__ import annotations
import asyncio
import enum
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    started_at: float = 0.0
    completed_at: float = 0.0
    attempts: int = 0

    @property
    def duration(self) -> float:
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return 0.0

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "attempts": self.attempts,
        }


@dataclass
class Task:
    id: str
    name: str
    func: Callable[..., Awaitable[Any]]
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 300.0
    priority: int = 0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


class DAG:
    """Directed Acyclic Graph for task dependency management."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self._adjacency: dict[str, list[str]] = {}  # task -> dependents
        self._reverse_adj: dict[str, list[str]] = {}  # task -> dependencies

    def add_task(self, task: Task) -> Task:
        """Add a task to the DAG."""
        if task.id in self.tasks:
            raise ValueError(f"Task {task.id} already exists")
        self.tasks[task.id] = task
        self._adjacency.setdefault(task.id, [])
        self._reverse_adj.setdefault(task.id, [])

        for dep_id in task.dependencies:
            self._adjacency.setdefault(dep_id, []).append(task.id)
            self._reverse_adj[task.id].append(dep_id)

        self._validate()
        return task

    def remove_task(self, task_id: str) -> Optional[Task]:
        """Remove a task and its edges."""
        if task_id not in self.tasks:
            return None

        task = self.tasks.pop(task_id)
        del self._adjacency[task_id]
        del self._reverse_adj[task_id]

        for dep_id in task.dependencies:
            if dep_id in self._adjacency:
                self._adjacency[dep_id] = [t for t in self._adjacency[dep_id] if t != task_id]

        return task

    def get_dependencies(self, task_id: str) -> list[str]:
        """Get direct dependencies of a task."""
        return self._reverse_adj.get(task_id, [])

    def get_dependents(self, task_id: str) -> list[str]:
        """Get tasks that depend on this task."""
        return self._adjacency.get(task_id, [])

    def get_ready_tasks(self, completed: set[str]) -> list[Task]:
        """Get tasks whose dependencies are all satisfied."""
        ready = []
        for task_id, task in self.tasks.items():
            if task_id in completed:
                continue
            deps = self._reverse_adj.get(task_id, [])
            if all(d in completed for d in deps):
                ready.append(task)
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready

    def topological_sort(self) -> list[str]:
        """Return tasks in topological order (Kahn's algorithm)."""
        in_degree = {tid: len(deps) for tid, deps in self._reverse_adj.items()}
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            queue.sort(key=lambda t: self.tasks[t].priority, reverse=True)
            current = queue.pop(0)
            result.append(current)

            for dependent in self._adjacency.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self.tasks):
            raise ValueError("Cycle detected in DAG")

        return result

    def _validate(self):
        """Validate the DAG has no cycles."""
        self.topological_sort()

    def to_dict(self) -> dict:
        return {
            "tasks": {
                tid: {
                    "id": t.id,
                    "name": t.name,
                    "dependencies": t.dependencies,
                    "max_retries": t.max_retries,
                    "priority": t.priority,
                }
                for tid, t in self.tasks.items()
            }
        }


class DAGEngine:
    """Execute DAG tasks with parallel execution and retry logic."""

    def __init__(self, max_parallel: int = 4):
        self.dag = DAG()
        self.max_parallel = max_parallel
        self.results: dict[str, TaskResult] = {}
        self._semaphore = asyncio.Semaphore(max_parallel)
        self._listeners: list[Callable[[str, TaskResult], None]] = []

    def add_task(self, task: Task) -> Task:
        """Add a task to the engine."""
        return self.dag.add_task(task)

    def on_task_complete(self, callback: Callable[[str, TaskResult], None]):
        """Register a callback for task completion."""
        self._listeners.append(callback)

    async def execute(self, context: Optional[dict] = None) -> dict[str, TaskResult]:
        """Execute all tasks in the DAG."""
        self.results = {}
        completed = set()
        failed = set()

        # Get execution order
        try:
            order = self.dag.topological_sort()
        except ValueError as e:
            raise ValueError(f"Invalid DAG: {e}")

        # Execute in waves (parallel where possible)
        while len(completed) + len(failed) < len(self.dag.tasks):
            ready = self.dag.get_ready_tasks(completed)
            # Filter out tasks whose dependencies failed
            ready = [
                t for t in ready
                if not any(d in failed for d in self.dag.get_dependencies(t.id))
            ]

            if not ready:
                break

            # Execute ready tasks in parallel
            tasks = [self._execute_task(t, context) for t in ready]
            await asyncio.gather(*tasks, return_exceptions=True)

            # Update completed/failed sets
            for task in ready:
                result = self.results.get(task.id)
                if result and result.status == TaskStatus.COMPLETED:
                    completed.add(task.id)
                elif result and result.status == TaskStatus.FAILED:
                    failed.add(task.id)
                    # Mark dependents as skipped
                    for dep_id in self.dag.get_dependents(task.id):
                        if dep_id not in completed and dep_id not in failed:
                            self.results[dep_id] = TaskResult(
                                task_id=dep_id,
                                status=TaskStatus.SKIPPED,
                                error=f"Dependency {task.id} failed",
                            )
                            failed.add(dep_id)

        return self.results

    async def _execute_task(self, task: Task, context: Optional[dict]):
        """Execute a single task with retry logic."""
        async with self._semaphore:
            result = TaskResult(task_id=task.id, status=TaskStatus.PENDING)
            self.results[task.id] = result

            for attempt in range(task.max_retries + 1):
                result.attempts = attempt + 1
                result.status = TaskStatus.RUNNING
                result.started_at = time.time()

                try:
                    # Inject context if function accepts it
                    if context is not None and self._accepts_context(task.func):
                        output = await asyncio.wait_for(
                            task.func(*task.args, **task.kwargs, context=context),
                            timeout=task.timeout,
                        )
                    else:
                        output = await asyncio.wait_for(
                            task.func(*task.args, **task.kwargs),
                            timeout=task.timeout,
                        )

                    result.status = TaskStatus.COMPLETED
                    result.output = output
                    result.completed_at = time.time()
                    break

                except asyncio.TimeoutError:
                    result.error = f"Task timed out after {task.timeout}s"
                    logger.warning(f"Task {task.id} timed out (attempt {attempt + 1})")
                except Exception as e:
                    result.error = str(e)
                    logger.warning(f"Task {task.id} failed (attempt {attempt + 1}): {e}")

                if attempt < task.max_retries:
                    await asyncio.sleep(task.retry_delay * (2 ** attempt))

            if result.status == TaskStatus.RUNNING:
                result.status = TaskStatus.FAILED
                result.completed_at = time.time()

            # Notify listeners
            for listener in self._listeners:
                try:
                    listener(task.id, result)
                except Exception:
                    pass

    @staticmethod
    def _accepts_context(func: Callable) -> bool:
        """Check if function accepts a 'context' parameter."""
        import inspect
        sig = inspect.signature(func)
        return "context" in sig.parameters

    def get_execution_order(self) -> list[str]:
        """Get the topological execution order."""
        return self.dag.topological_sort()

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result for a specific task."""
        return self.results.get(task_id)

    def to_dict(self) -> dict:
        return {
            "dag": self.dag.to_dict(),
            "results": {tid: r.to_dict() for tid, r in self.results.items()},
        }
