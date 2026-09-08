"""
Tests for Observability & Evaluation Layer.
Test count: 18
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

from observability.metrics import MetricsCollector
from observability.logging import LogCollector
from observability.tracing import TraceCollector
from observability.evaluation import EvaluationEngine
from observability.alerting import AlertManager


# ──────────────────── Metrics Tests ───────────────────────────────────


class TestMetricsCollector:
    def test_create(self):
        collector = MetricsCollector()
        assert collector is not None

    def test_record_counter(self):
        collector = MetricsCollector()
        collector.record_counter("requests", 1)
        collector.record_counter("requests", 1)
        assert collector.get_counter("requests") == 2

    def test_record_gauge(self):
        collector = MetricsCollector()
        collector.record_gauge("cpu", 75.5)
        assert collector.get_gauge("cpu") == 75.5

    def test_record_histogram(self):
        collector = MetricsCollector()
        collector.record_histogram("latency", 100)
        collector.record_histogram("latency", 200)
        stats = collector.get_histogram_stats("latency")
        assert stats["count"] == 2
        assert stats["avg"] == 150

    def test_get_metrics(self):
        collector = MetricsCollector()
        collector.record_counter("a", 1)
        collector.record_gauge("b", 2.0)
        metrics = collector.get_metrics()
        assert len(metrics) == 2


# ──────────────────── Logging Tests ───────────────────────────────────


class TestLogCollector:
    def test_create(self):
        collector = LogCollector()
        assert collector is not None

    def test_log(self):
        collector = LogCollector()
        collector.info("Test message", component="test")
        logs = collector.get_logs()
        assert len(logs) == 1
        assert logs[0].level == "INFO"

    def test_get_logs(self):
        collector = LogCollector()
        collector.info("msg1", component="comp1")
        collector.error("msg2", component="comp2")
        logs = collector.get_logs(level="ERROR")
        assert len(logs) == 1

    def test_search_logs(self):
        collector = LogCollector()
        collector.info("Something happened")
        collector.info("Something else")
        results = collector.search_logs("happened")
        assert len(results) == 1


# ──────────────────── Tracing Tests ───────────────────────────────────


class TestTraceCollector:
    def test_create(self):
        collector = TraceCollector()
        assert collector is not None

    def test_start_end_span(self):
        collector = TraceCollector()
        span = collector.start_span("test_span")
        assert span.span_id != ""
        collector.end_span(span.span_id, span.trace_id)
        trace = collector.get_trace(span.trace_id)
        assert len(trace) == 1

    def test_get_trace(self):
        collector = TraceCollector()
        span = collector.start_span("op")
        trace = collector.get_trace(span.trace_id)
        assert len(trace) >= 1


# ──────────────────── Evaluation Tests ────────────────────────────────


class TestEvaluationEngine:
    def test_create(self):
        engine = EvaluationEngine()
        assert engine is not None

    def test_score_quality(self):
        engine = EvaluationEngine()
        scores = engine.score_quality("The answer is 42.", "42")
        assert "overall" in scores
        assert 0 <= scores["overall"] <= 1

    def test_score_safety(self):
        engine = EvaluationEngine()
        result = engine.score_safety({"safety_passed": True, "violations": []}, ["scope", "resource"])
        assert result["passed"] is True

    def test_score_performance(self):
        engine = EvaluationEngine()
        scores = engine.score_performance({"latency_ms": 50, "throughput": 500, "error_rate": 0.01})
        assert "overall" in scores

    def test_generate_report(self):
        engine = EvaluationEngine()
        report = engine.generate_report("2024-01-01", "2024-01-31")
        assert "summary" in report
        assert "scores" in report


# ──────────────────── Alerting Tests ──────────────────────────────────


class TestAlertManager:
    def test_create(self):
        manager = AlertManager()
        assert manager is not None

    def test_create_alert(self):
        manager = AlertManager()
        rule = manager.create_alert("high_error_rate", "error_rate > 5", "P2", ["slack"])
        assert rule.rule_id != ""

    def test_evaluate_alerts(self):
        manager = AlertManager()
        manager.create_alert("high_error_rate", "error_rate > 5", "P2", ["slack"])
        alerts = manager.evaluate_alerts({"error_rate": 10})
        assert len(alerts) >= 1

    def test_get_active_alerts(self):
        manager = AlertManager()
        manager.create_alert("high_error_rate", "error_rate > 5", "P2", ["slack"])
        manager.evaluate_alerts({"error_rate": 10})
        alerts = manager.get_active_alerts()
        assert len(alerts) >= 1
