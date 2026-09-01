"""
t_6a66fbd3 — MBPP Benchmark

MBPP: 974+ Python programming problems.
load_problems, run_problem, run_sample(n), get_accuracy.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class MBPPProblem:
    id: str
    description: str
    code: str
    test_cases: list[str]
    difficulty: str = "medium"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MBPPProblem":
        return cls(**d)


@dataclass
class MBPPResult:
    id: str
    problem_id: str
    success: bool
    output: Any = None
    error: str | None = None
    duration: float = 0.0
    test_results: dict[str, bool] = field(default_factory=dict)

    @property
    def accuracy(self) -> float:
        if not self.test_results:
            return 0.0
        passed = sum(1 for v in self.test_results.values() if v)
        return passed / len(self.test_results)


class MBPPLoader:
    """Load MBPP problems from JSON file."""

    def __init__(self, data_path: str | None = None) -> None:
        self.data_path = data_path
        self.problems: dict[str, MBPPProblem] = {}

    def load_problems(self, path: str | None = None) -> list[MBPPProblem]:
        target = path or self.data_path
        if not target or not os.path.exists(target):
            return []
        with open(target) as f:
            data = json.load(f)
        problems = []
        for item in data:
            p = MBPPProblem(
                id=str(item.get("id", uuid.uuid4().hex[:8])),
                description=item.get("description", ""),
                code=item.get("code", ""),
                test_cases=item.get("test_cases", []),
                difficulty=item.get("difficulty", "medium"),
                tags=item.get("tags", []),
            )
            self.problems[p.id] = p
            problems.append(p)
        return problems

    def get_problem(self, problem_id: str) -> MBPPProblem | None:
        return self.problems.get(problem_id)

    def get_all(self) -> list[MBPPProblem]:
        return list(self.problems.values())


class MBPPEvaluator:
    """Evaluate MBPP solutions."""

    def evaluate(self, problem: MBPPProblem, solution: str) -> MBPPResult:
        test_results: dict[str, bool] = {}
        error: str | None = None
        for test in problem.test_cases:
            try:
                namespace: dict[str, Any] = {}
                exec(solution, namespace)
                exec(test, namespace)
                test_results[test] = True
            except Exception as e:
                test_results[test] = False
                if error is None:
                    error = str(e)
        success = all(test_results.values()) if test_results else True
        return MBPPResult(
            id=str(uuid.uuid4().hex[:8]), problem_id=problem.id,
            success=success, error=error, test_results=test_results,
        )


class MBPPBenchmark:
    """MBPP benchmark runner."""

    def __init__(self, data_path: str | None = None) -> None:
        self.loader = MBPPLoader(data_path)
        self.evaluator = MBPPEvaluator()
        self.results: list[MBPPResult] = []

    def load_problems(self, path: str | None = None) -> list[MBPPProblem]:
        return self.loader.load_problems(path)

    def run_problem(self, problem_id: str, solution: str) -> MBPPResult:
        problem = self.loader.get_problem(problem_id)
        if not problem:
            return MBPPResult(id=str(uuid.uuid4().hex[:8]), problem_id=problem_id, success=False, error="Problem not found")
        result = self.evaluator.evaluate(problem, solution)
        self.results.append(result)
        return result

    def run_sample(self, n: int = 10) -> list[MBPPResult]:
        problems = self.loader.get_all()[:n]
        results = []
        for p in problems:
            result = self.evaluator.evaluate(p, p.code)
            results.append(result)
            self.results.append(result)
        return results

    def get_accuracy(self) -> dict[str, float]:
        if not self.results:
            return {"overall": 0.0, "total": 0}
        correct = sum(1 for r in self.results if r.success)
        return {"overall": correct / len(self.results), "total": len(self.results)}

    def get_results(self, success: bool | None = None) -> list[MBPPResult]:
        if success is None:
            return self.results
        return [r for r in self.results if r.success == success]
