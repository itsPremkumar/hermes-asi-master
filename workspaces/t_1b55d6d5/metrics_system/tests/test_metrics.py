"""Tests for Engineering Metrics System."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Make metrics_system importable from workspace root
_WORKSPACE = Path(__file__).resolve().parent.parent
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from metrics_system.dora.models import DORAConfig, DORAResult, DeploymentRecord
from metrics_system.dora.collector import DORAMetricsCollector
from metrics_system.flow.models import WorkItem
from metrics_system.flow.collector import FlowMetricsCollector
from metrics_system.team_health.models import HealthQuestion, HealthResponse
from metrics_system.team_health.collector import TeamHealthCollector
from metrics_system.dashboard.renderer import DashboardRenderer
from metrics_system.dashboard.config import DashboardConfig
from metrics_system.pipeline.reporters import ReportBundle, JSONReporter, MarkdownReporter
from metrics_system.pipeline.engine import ReportingPipeline


# --- Helpers ---

def _deployments(n: int = 10, fail_rate: float = 0.1) -> list[DeploymentRecord]:
    now = datetime.utcnow()
    records = []
    for i in range(n):
        records.append(
            DeploymentRecord(
                id=f"deploy-{i}",
                timestamp=now - timedelta(days=i * 2),
                environment="production",
                status="success" if i / n > fail_rate else "failed",
                lead_time_hours=float(i * 4 + 2),
                change_failed=(i / n <= fail_rate),
                restore_time_hours=2.0 if (i / n <= fail_rate) else None,
            )
        )
    return records


def _work_items(n: int = 20) -> list[WorkItem]:
    now = datetime.utcnow()
    items = []
    for i in range(n):
        created = now - timedelta(days=i)
        done = created + timedelta(hours=i * 3)
        items.append(
            WorkItem(
                id=f"WI-{i}",
                title=f"Task {i}",
                created=created,
                started=created + timedelta(hours=1),
                done=done,
                status="done",
                story_points=3.0,
            )
        )
    return items


def _responses(n: int = 25) -> list[HealthResponse]:
    questions = [
        HealthQuestion(id="morale-1", text="q", category="morale", scale_max=5),
        HealthQuestion(id="clarity-1", text="q", category="clarity", scale_max=5),
        HealthQuestion(id="tools-1", text="q", category="tools", scale_max=5),
        HealthQuestion(id="process-1", text="q", category="process", scale_max=5),
        HealthQuestion(id="growth-1", text="q", category="growth", scale_max=5),
    ]
    responses = []
    for i in range(n):
        for q in questions:
            responses.append(
                HealthResponse(
                    question_id=q.id,
                    team_member=f"member-{i % 5}",
                    value=4.0,
                    timestamp=datetime.utcnow() - timedelta(days=i),
                )
            )
    return responses


# --- DORA tests ---

def test_dora_collector_computes_all_metrics():
    collector = DORAMetricsCollector(DORAConfig(window_days=60))
    result = collector.collect(_deployments(10, fail_rate=0.1))
    assert result.deployment_frequency.get("daily", 0) > 0
    assert result.median_lead_time_hours > 0
    assert 0 <= result.change_fail_rate <= 1
    print(f"DORA: {result.deployment_band} | {result.lead_time_band} | {result.failure_band}")


def test_dora_bands():
    result = DORAResult(
        deployment_frequency={"daily": 2.0},
        median_lead_time_hours=0.5,
        change_fail_rate=0.02,
        median_restore_hours=0.5,
    )
    assert "elite" in result.deployment_band
    assert "elite" in result.lead_time_band
    assert "elite" in result.failure_band
    assert "elite" in result.restore_band


# --- Flow tests ---

def test_flow_collector_computes_cycle_time():
    collector = FlowMetricsCollector(window_days=60)
    result = collector.collect(_work_items(20))
    assert result.cycle_time_hours > 0
    assert result.throughput > 0
    assert result.wip >= 0
    print(f"Flow: CT={result.cycle_time_hours:.1f}h | TP={result.throughput:.1f}/wk")


# --- Team Health tests ---

def test_health_collector_scores():
    collector = TeamHealthCollector(window_days=90)
    result = collector.collect(_responses(25))
    assert result.overall > 0
    assert result.responses_count > 0
    assert result.level in ("healthy", "at-risk", "critical")
    print(f"Health: {result.overall}/100 ({result.level}) | trend={result.trend}")


# --- Dashboard tests ---

def test_dashboard_renders_markdown():
    config = DashboardConfig(title="Test Dashboard")
    renderer = DashboardRenderer(config)
    dora = DORAMetricsCollector().collect(_deployments(5))
    flow = FlowMetricsCollector().collect(_work_items(10))
    health = TeamHealthCollector().collect(_responses(10))
    md = renderer.render_markdown(dora=dora, flow=flow, health=health)
    assert "# Test Dashboard" in md
    assert "## DORA Metrics" in md
    assert "## Flow Metrics" in md
    assert "## Team Health" in md
    print(f"Markdown dashboard: {len(md)} chars")


def test_dashboard_renders_console():
    renderer = DashboardRenderer()
    dora = DORAMetricsCollector().collect(_deployments(5))
    out = renderer.render_console(dora=dora)
    assert "[Engineering Metrics]" in out
    print(f"Console: {out}")


# --- Pipeline tests ---

def test_pipeline_runs_and_produces_bundle():
    pipeline = ReportingPipeline()
    bundle = pipeline.run(
        deployments=_deployments(8),
        work_items=_work_items(15),
        responses=_responses(20),
    )
    assert bundle.dora.deployment_frequency is not None
    assert bundle.flow.cycle_time_hours > 0
    assert bundle.health.overall > 0
    print(f"Pipeline bundle: dora={bundle.dora.deployment_band}, health={bundle.health.level}")


def test_json_reporter_writes():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        reporter = JSONReporter(output_dir=Path(tmp))
        pipeline = ReportingPipeline(reporters=[reporter])
        bundle = pipeline.run(
            deployments=_deployments(5),
            work_items=_work_items(10),
        )
        path = Path(tmp) / "report.json"
        assert path.exists()
        data = json.loads(path.read_text())
        assert "dora" in data
        assert "flow" in data
        assert "health" in data
        print(f"JSON report written to {path}")


def test_markdown_reporter_writes():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        reporter = MarkdownReporter(output_dir=Path(tmp))
        pipeline = ReportingPipeline(reporters=[reporter])
        bundle = pipeline.run(
            deployments=_deployments(5),
            work_items=_work_items(10),
        )
        path = Path(tmp) / "dashboard.md"
        assert path.exists()
        content = path.read_text()
        assert "# Engineering Metrics Dashboard" in content
        print(f"Markdown dashboard written to {path}")


if __name__ == "__main__":
    import traceback

    tests = [
        test_dora_collector_computes_all_metrics,
        test_dora_bands,
        test_flow_collector_computes_cycle_time,
        test_health_collector_scores,
        test_dashboard_renders_markdown,
        test_dashboard_renders_console,
        test_pipeline_runs_and_produces_bundle,
        test_json_reporter_writes,
        test_markdown_reporter_writes,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed}/{len(tests)} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)