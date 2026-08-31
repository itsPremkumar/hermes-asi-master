"""Tests for runner.py — Benchmark Runner + Evaluation Harness."""
import pytest
import os
import tempfile

from benchmark.runner import (
    ARCAGI3Connector, SWEBenchConnector, BenchmarkOrchestrator,
    ResultLogger, RegressionDetector, BenchmarkResult
)


class TestARCAGI3Connector:
    def test_create(self):
        c = ARCAGI3Connector()
        assert len(c.tasks) == 0

    def test_load_puzzle(self):
        c = ARCAGI3Connector()
        t = c.load_puzzle("p1", [[1, 2], [3, 4]], [[2, 4], [1, 3]])
        assert t.id == "p1"

    def test_evaluate_correct(self):
        c = ARCAGI3Connector()
        c.load_puzzle("p1", [[1, 0], [0, 1]], [[0, 1], [1, 0]])
        r = c.evaluate("p1", [[0, 1], [1, 0]])
        assert r.success is True
        assert r.score == 1.0

    def test_evaluate_incorrect(self):
        c = ARCAGI3Connector()
        c.load_puzzle("p1", [[1, 0], [0, 1]], [[0, 1], [1, 0]])
        r = c.evaluate("p1", [[1, 0], [0, 1]])
        assert r.success is False

    def test_evaluate_no_expected(self):
        c = ARCAGI3Connector()
        c.load_puzzle("p1", [[1]], None)
        r = c.evaluate("p1", [[1]])
        assert r.success is False

    def test_evaluate_no_task(self):
        c = ARCAGI3Connector()
        r = c.evaluate("nonexistent", [])
        assert r.success is False

    def test_generate(self):
        c = ARCAGI3Connector()
        t = c.generate(3)
        assert t.benchmark == "arc_agi_3"
        assert t.expected_output is not None


class TestSWEBenchConnector:
    def test_create(self):
        c = SWEBenchConnector()
        assert len(c.tasks) == 0

    def test_load_task(self):
        c = SWEBenchConnector()
        t = c.load_task("s1", "repo", "Fix bug", "abc")
        assert t.id == "s1"

    def test_evaluate_all_pass(self):
        c = SWEBenchConnector()
        c.load_task("s1", "repo", "Fix", "abc")
        r = c.evaluate("s1", "patch", {"t1": True, "t2": True})
        assert r.success is True
        assert r.score == 1.0

    def test_evaluate_partial(self):
        c = SWEBenchConnector()
        c.load_task("s1", "repo", "Fix", "abc")
        r = c.evaluate("s1", "patch", {"t1": True, "t2": False})
        assert r.score == 0.5

    def test_evaluate_fail(self):
        c = SWEBenchConnector()
        c.load_task("s1", "repo", "Fix", "abc")
        r = c.evaluate("s1", "patch", {"t1": False})
        assert r.success is False

    def test_evaluate_no_results(self):
        c = SWEBenchConnector()
        c.load_task("s1", "repo", "Fix", "abc")
        r = c.evaluate("s1", "", {})
        assert r.success is False


class TestResultLogger:
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = ResultLogger(storage_path=tmp)
            assert len(logger.results) == 0

    def test_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = ResultLogger(storage_path=tmp)
            r = BenchmarkResult(id="r1", task_id="t1", benchmark="arc", success=True, score=1.0)
            logger.log(r)
            assert len(logger.results) == 1

    def test_log_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = ResultLogger(storage_path=tmp)
            r = BenchmarkResult(id="r1", task_id="t1", benchmark="arc", success=True, score=1.0)
            logger.log(r)
            assert os.path.exists(os.path.join(tmp, "r1.json"))

    def test_get_results_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = ResultLogger(storage_path=tmp)
            logger.log(BenchmarkResult(id="r1", task_id="t1", benchmark="arc", success=True, score=1.0))
            logger.log(BenchmarkResult(id="r2", task_id="t2", benchmark="swe", success=False, score=0.0))
            assert len(logger.get_results(benchmark="arc")) == 1
            assert len(logger.get_results(success=True)) == 1

    def test_get_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = ResultLogger(storage_path=tmp)
            logger.log(BenchmarkResult(id="r1", task_id="t1", benchmark="arc", success=True, score=1.0))
            logger.log(BenchmarkResult(id="r2", task_id="t2", benchmark="arc", success=False, score=0.0))
            s = logger.get_summary()
            assert s["total"] == 2
            assert s["success_rate"] == 0.5

    def test_get_summary_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = ResultLogger(storage_path=tmp)
            s = logger.get_summary()
            assert s["total"] == 0


class TestRegressionDetector:
    def test_create(self):
        rd = RegressionDetector()
        assert rd.threshold == 0.1

    def test_record(self):
        rd = RegressionDetector()
        rd.record("t1", 0.9)
        rd.record("t1", 0.8)
        assert len(rd.history["t1"]) == 2

    def test_detect_regression(self):
        rd = RegressionDetector(threshold=0.1)
        rd.record("t1", 0.9)
        rd.record("t1", 0.7)
        assert rd.detect_regression("t1") is True

    def test_no_regression(self):
        rd = RegressionDetector(threshold=0.1)
        rd.record("t1", 0.8)
        rd.record("t1", 0.75)
        assert rd.detect_regression("t1") is False

    def test_insufficient_data(self):
        rd = RegressionDetector()
        rd.record("t1", 0.9)
        assert rd.detect_regression("t1") is False

    def test_get_trend(self):
        rd = RegressionDetector()
        rd.record("t1", 0.9)
        rd.record("t1", 0.8)
        trend = rd.get_trend("t1")
        assert len(trend) == 2

    def test_get_all_regressions(self):
        rd = RegressionDetector(threshold=0.1)
        rd.record("t1", 0.9)
        rd.record("t1", 0.7)
        rd.record("t2", 0.8)
        rd.record("t2", 0.75)
        regressions = rd.get_all_regressions()
        assert "t1" in regressions
        assert "t2" not in regressions


class TestBenchmarkOrchestrator:
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            orch = BenchmarkOrchestrator(storage_path=tmp)
            assert orch.arc_agi_3 is not None
            assert orch.swe_bench is not None

    def test_run_arc_agi_3(self):
        with tempfile.TemporaryDirectory() as tmp:
            orch = BenchmarkOrchestrator(storage_path=tmp)
            orch.arc_agi_3.load_puzzle("p1", [[1]], [[1]])
            r = orch.run_arc_agi_3("p1", [[1]])
            assert r.success is True

    def test_run_swe_bench(self):
        with tempfile.TemporaryDirectory() as tmp:
            orch = BenchmarkOrchestrator(storage_path=tmp)
            orch.swe_bench.load_task("s1", "repo", "Fix", "abc")
            r = orch.run_swe_bench("s1", "patch", {"t1": True})
            assert r.success is True

    def test_get_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            orch = BenchmarkOrchestrator(storage_path=tmp)
            orch.arc_agi_3.load_puzzle("p1", [[1]], [[1]])
            orch.run_arc_agi_3("p1", [[1]])
            stats = orch.get_stats()
            assert stats["total"] == 1

    def test_get_regressions(self):
        with tempfile.TemporaryDirectory() as tmp:
            orch = BenchmarkOrchestrator(storage_path=tmp)
            orch.arc_agi_3.load_puzzle("p1", [[1]], [[1]])
            orch.run_arc_agi_3("p1", [[1]])
            regressions = orch.get_regressions()
            assert isinstance(regressions, list)
