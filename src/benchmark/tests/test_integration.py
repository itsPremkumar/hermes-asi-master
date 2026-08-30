"""Tests for t_d70c1de0 — ARC-AGI-3 + SWE-bench Integration Layer."""
import pytest
import os
import tempfile

from benchmark.integration import (
    ARCAGI3Adapter, SWEBenchAdapter, BenchmarkRunner,
    BenchmarkTask, BenchmarkResult
)


class TestBenchmarkTask:
    def test_create(self):
        t = BenchmarkTask(id="t1", benchmark="arc_agi_3", task_type="puzzle", description="test")
        assert t.id == "t1"
        assert t.benchmark == "arc_agi_3"
        assert t.difficulty == "medium"

    def test_to_dict(self):
        t = BenchmarkTask(id="t1", benchmark="arc_agi_3", task_type="puzzle", description="test")
        d = t.to_dict()
        assert d["id"] == "t1"

    def test_from_dict(self):
        d = {"id": "t1", "benchmark": "arc_agi_3", "task_type": "puzzle", "description": "test",
             "input_data": {}, "expected_output": None, "metadata": {}, "difficulty": "hard"}
        t = BenchmarkTask.from_dict(d)
        assert t.id == "t1"
        assert t.difficulty == "hard"


class TestBenchmarkResult:
    def test_create(self):
        r = BenchmarkResult(id="r1", task_id="t1", benchmark="arc_agi_3", success=True, score=1.0)
        assert r.success is True
        assert r.score == 1.0


class TestARCAGI3Adapter:
    def test_create(self):
        adapter = ARCAGI3Adapter()
        assert len(adapter.tasks) == 0

    def test_load_puzzle(self):
        adapter = ARCAGI3Adapter()
        task = adapter.load_puzzle("p1", [[1, 2], [3, 4]], [[2, 4], [1, 3]])
        assert task.id == "p1"
        assert "p1" in adapter.tasks

    def test_evaluate_correct(self):
        adapter = ARCAGI3Adapter()
        adapter.load_puzzle("p1", [[1, 2], [3, 4]], [[2, 4], [1, 3]])
        result = adapter.evaluate("p1", [[2, 4], [1, 3]])
        assert result.success is True
        assert result.score == 1.0

    def test_evaluate_incorrect(self):
        adapter = ARCAGI3Adapter()
        adapter.load_puzzle("p1", [[1, 2], [3, 4]], [[2, 4], [1, 3]])
        result = adapter.evaluate("p1", [[1, 2], [3, 4]])
        assert result.success is False
        assert result.score == 0.0

    def test_evaluate_no_task(self):
        adapter = ARCAGI3Adapter()
        result = adapter.evaluate("nonexistent", [])
        assert result.success is False

    def test_evaluate_no_expected(self):
        adapter = ARCAGI3Adapter()
        adapter.load_puzzle("p1", [[1, 2]], None)
        result = adapter.evaluate("p1", [[1, 2]])
        assert result.success is False

    def test_generate_puzzle(self):
        adapter = ARCAGI3Adapter()
        task = adapter.generate_puzzle(3)
        assert task.benchmark == "arc_agi_3"
        assert task.expected_output is not None
        assert task.id in adapter.tasks


class TestSWEBenchAdapter:
    def test_create(self):
        adapter = SWEBenchAdapter()
        assert len(adapter.tasks) == 0

    def test_load_task(self):
        adapter = SWEBenchAdapter()
        task = adapter.load_task("s1", "owner/repo", "Fix bug", "abc123")
        assert task.id == "s1"
        assert task.benchmark == "swe_bench"
        assert "s1" in adapter.tasks

    def test_evaluate_pass(self):
        adapter = SWEBenchAdapter()
        adapter.load_task("s1", "owner/repo", "Fix bug", "abc123")
        result = adapter.evaluate("s1", "patch content", {"test1": True, "test2": True})
        assert result.success is True
        assert result.score == 1.0

    def test_evaluate_partial(self):
        adapter = SWEBenchAdapter()
        adapter.load_task("s1", "owner/repo", "Fix bug", "abc123")
        result = adapter.evaluate("s1", "patch content", {"test1": True, "test2": False})
        assert result.success is False
        assert result.score == 0.5

    def test_evaluate_fail(self):
        adapter = SWEBenchAdapter()
        adapter.load_task("s1", "owner/repo", "Fix bug", "abc123")
        result = adapter.evaluate("s1", "patch content", {"test1": False, "test2": False})
        assert result.success is False
        assert result.score == 0.0

    def test_evaluate_no_results(self):
        adapter = SWEBenchAdapter()
        adapter.load_task("s1", "owner/repo", "Fix bug", "abc123")
        result = adapter.evaluate("s1", "", {})
        assert result.success is False


class TestBenchmarkRunner:
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = BenchmarkRunner(storage_path=tmp)
            assert len(runner.results) == 0

    def test_run_arc_agi_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = BenchmarkRunner(storage_path=tmp)
            runner.arc_agi_3.load_puzzle("p1", [[1, 0], [0, 1]], [[0, 1], [1, 0]])
            result = runner.run_arc_agi_3("p1", [[0, 1], [1, 0]])
            assert result.success is True

    def test_run_swe_bench(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = BenchmarkRunner(storage_path=tmp)
            runner.swe_bench.load_task("s1", "repo", "issue", "abc")
            result = runner.run_swe_bench("s1", "patch", {"t1": True, "t2": True})
            assert result.success is True

    def test_get_results_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = BenchmarkRunner(storage_path=tmp)
            runner.arc_agi_3.load_puzzle("p1", [[1]], [[1]])
            runner.swe_bench.load_task("s1", "repo", "issue", "abc")
            runner.run_arc_agi_3("p1", [[1]])
            runner.run_swe_bench("s1", "", {"t1": True})
            arc_results = runner.get_results(benchmark="arc_agi_3")
            assert len(arc_results) == 1
            swe_results = runner.get_results(benchmark="swe_bench")
            assert len(swe_results) == 1

    def test_get_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = BenchmarkRunner(storage_path=tmp)
            stats = runner.get_stats()
            assert stats["total"] == 0
            runner.arc_agi_3.load_puzzle("p1", [[1]], [[1]])
            runner.run_arc_agi_3("p1", [[1]])
            stats = runner.get_stats()
            assert stats["total"] == 1
            assert stats["success_rate"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
