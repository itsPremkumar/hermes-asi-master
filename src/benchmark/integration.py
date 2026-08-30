"""
t_d70c1de0 — ARC-AGI-3 + SWE-bench Integration Layer
"""

from __future__ import annotations

import json
import os
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
class BenchmarkTask:
    id: str
    benchmark: str
    task_type: str
    description: str
    input_data: dict[str, Any] = field(default_factory=dict)
    expected_output: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    difficulty: str = "medium"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "BenchmarkTask":
        return cls(**d)


@dataclass
class BenchmarkResult:
    id: str
    task_id: str
    benchmark: str
    success: bool
    score: float
    output: Any = None
    duration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)


class ARCAGI3Adapter:
    def __init__(self) -> None:
        self.tasks: dict[str, BenchmarkTask] = {}

    def load_puzzle(self, puzzle_id: str, input_grid: list[list[int]], expected_output: list[list[int]] | None = None) -> BenchmarkTask:
        task = BenchmarkTask(
            id=puzzle_id, benchmark="arc_agi_3", task_type="puzzle_solving",
            description=f"ARC-AGI-3 puzzle {puzzle_id}",
            input_data={"grid": input_grid}, expected_output=expected_output,
        )
        self.tasks[puzzle_id] = task
        return task

    def evaluate(self, task_id: str, agent_output: list[list[int]]) -> BenchmarkResult:
        task = self.tasks.get(task_id)
        if not task or task.expected_output is None:
            return BenchmarkResult(id=str(uuid.uuid4().hex[:8]), task_id=task_id, benchmark="arc_agi_3", success=False, score=0.0)
        success = agent_output == task.expected_output
        return BenchmarkResult(
            id=str(uuid.uuid4().hex[:8]), task_id=task_id, benchmark="arc_agi_3",
            success=success, score=1.0 if success else 0.0, output=agent_output,
        )

    def generate_puzzle(self, size: int = 3) -> BenchmarkTask:
        import random
        grid = [[random.randint(0, 3) for _ in range(size)] for _ in range(size)]
        expected = [list(row) for row in zip(*grid[::-1])]
        task = BenchmarkTask(
            id=str(uuid.uuid4().hex[:8]), benchmark="arc_agi_3", task_type="pattern_recognition",
            description=f"Rotate {size}x{size} grid 90 degrees",
            input_data={"grid": grid}, expected_output=expected,
        )
        self.tasks[task.id] = task
        return task


class SWEBenchAdapter:
    def __init__(self) -> None:
        self.tasks: dict[str, BenchmarkTask] = {}

    def load_task(self, task_id: str, repo: str, issue_description: str, base_commit: str) -> BenchmarkTask:
        task = BenchmarkTask(
            id=task_id, benchmark="swe_bench", task_type="bug_fix",
            description=issue_description,
            input_data={"repo": repo, "base_commit": base_commit}, difficulty="hard",
        )
        self.tasks[task_id] = task
        return task

    def evaluate(self, task_id: str, patch: str, test_results: dict[str, bool]) -> BenchmarkResult:
        task = self.tasks.get(task_id)
        if not task or not test_results:
            return BenchmarkResult(id=str(uuid.uuid4().hex[:8]), task_id=task_id, benchmark="swe_bench", success=False, score=0.0)
        passed = sum(1 for v in test_results.values() if v)
        total = len(test_results)
        score = passed / total if total > 0 else 0.0
        return BenchmarkResult(
            id=str(uuid.uuid4().hex[:8]), task_id=task_id, benchmark="swe_bench",
            success=score >= 0.8, score=score, output={"patch": patch, "test_results": test_results},
        )


class BenchmarkRunner:
    def __init__(self, storage_path: str = "./state/benchmarks") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self.arc_agi_3 = ARCAGI3Adapter()
        self.swe_bench = SWEBenchAdapter()
        self.results: list[BenchmarkResult] = []
        os.makedirs(storage_path, exist_ok=True)

    def run_arc_agi_3(self, task_id: str, agent_output: list[list[int]]) -> BenchmarkResult:
        result = self.arc_agi_3.evaluate(task_id, agent_output)
        self.results.append(result)
        return result

    def run_swe_bench(self, task_id: str, patch: str, test_results: dict[str, bool]) -> BenchmarkResult:
        result = self.swe_bench.evaluate(task_id, patch, test_results)
        self.results.append(result)
        return result

    def get_results(self, benchmark: str | None = None, success: bool | None = None) -> list[BenchmarkResult]:
        results = self.results
        if benchmark:
            results = [r for r in results if r.benchmark == benchmark]
        if success is not None:
            results = [r for r in results if r.success == success]
        return results

    def get_stats(self) -> dict[str, Any]:
        if not self.results:
            return {"total": 0, "success_rate": 0.0, "avg_score": 0.0}
        return {
            "total": len(self.results),
            "success_rate": sum(1 for r in self.results if r.success) / len(self.results),
            "avg_score": sum(r.score for r in self.results) / len(self.results),
        }
