"""
t_50623dec — Benchmark Runner + Evaluation Harness
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


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


class ARCAGI3Connector:
    def __init__(self) -> None:
        self.tasks: dict[str, BenchmarkTask] = {}

    def load_puzzle(self, puzzle_id: str, input_grid: list[list[int]], expected: list[list[int]] | None = None) -> BenchmarkTask:
        task = BenchmarkTask(
            id=puzzle_id, benchmark="arc_agi_3", task_type="puzzle",
            description=f"ARC-AGI-3 puzzle {puzzle_id}",
            input_data={"grid": input_grid}, expected_output=expected,
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

    def generate(self, size: int = 3) -> BenchmarkTask:
        import random
        grid = [[random.randint(0, 3) for _ in range(size)] for _ in range(size)]
        expected = [list(row) for row in zip(*grid[::-1])]
        task = BenchmarkTask(
            id=str(uuid.uuid4().hex[:8]), benchmark="arc_agi_3", task_type="rotation",
            description=f"Rotate {size}x{size} 90deg",
            input_data={"grid": grid}, expected_output=expected,
        )
        self.tasks[task.id] = task
        return task


class SWEBenchConnector:
    def __init__(self) -> None:
        self.tasks: dict[str, BenchmarkTask] = {}

    def load_task(self, task_id: str, repo: str, issue: str, base_commit: str) -> BenchmarkTask:
        task = BenchmarkTask(
            id=task_id, benchmark="swe_bench", task_type="bug_fix",
            description=issue, input_data={"repo": repo, "base_commit": base_commit},
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
            success=score >= 0.8, score=score, output={"patch": patch, "tests": test_results},
        )


class ResultLogger:
    def __init__(self, storage_path: str = "./state/results") -> None:
        self.storage_path = storage_path
        self.results: list[BenchmarkResult] = []
        os.makedirs(storage_path, exist_ok=True)

    def log(self, result: BenchmarkResult) -> None:
        self.results.append(result)
        self._save(result)

    def _save(self, result: BenchmarkResult) -> None:
        path = os.path.join(self.storage_path, f"{result.id}.json")
        atomic_file_write(path, result.to_dict())

    def get_results(self, benchmark: str | None = None, success: bool | None = None) -> list[BenchmarkResult]:
        results = self.results
        if benchmark:
            results = [r for r in results if r.benchmark == benchmark]
        if success is not None:
            results = [r for r in results if r.success == success]
        return results

    def get_summary(self) -> dict[str, Any]:
        if not self.results:
            return {"total": 0, "success_rate": 0.0, "avg_score": 0.0}
        return {
            "total": len(self.results),
            "success_rate": sum(1 for r in self.results if r.success) / len(self.results),
            "avg_score": sum(r.score for r in self.results) / len(self.results),
        }


class RegressionDetector:
    def __init__(self, threshold: float = 0.1) -> None:
        self.threshold = threshold
        self.history: dict[str, list[float]] = {}

    def record(self, task_id: str, score: float) -> None:
        if task_id not in self.history:
            self.history[task_id] = []
        self.history[task_id].append(score)

    def detect_regression(self, task_id: str) -> bool:
        scores = self.history.get(task_id, [])
        if len(scores) < 2:
            return False
        return (scores[-2] - scores[-1]) > self.threshold

    def get_trend(self, task_id: str) -> list[float]:
        return self.history.get(task_id, [])

    def get_all_regressions(self) -> list[str]:
        return [tid for tid in self.history if self.detect_regression(tid)]


class BenchmarkOrchestrator:
    def __init__(self, storage_path: str = "./state/bench") -> None:
        self.storage_path = storage_path
        self.arc_agi_3 = ARCAGI3Connector()
        self.swe_bench = SWEBenchConnector()
        self.logger = ResultLogger(storage_path=storage_path)
        self.regression = RegressionDetector()

    def run_arc_agi_3(self, task_id: str, agent_output: list[list[int]]) -> BenchmarkResult:
        result = self.arc_agi_3.evaluate(task_id, agent_output)
        self.logger.log(result)
        self.regression.record(task_id, result.score)
        return result

    def run_swe_bench(self, task_id: str, patch: str, test_results: dict[str, bool]) -> BenchmarkResult:
        result = self.swe_bench.evaluate(task_id, patch, test_results)
        self.logger.log(result)
        self.regression.record(task_id, result.score)
        return result

    def get_stats(self) -> dict[str, Any]:
        return self.logger.get_summary()

    def get_regressions(self) -> list[str]:
        return self.regression.get_all_regressions()
