"""Reporting pipeline — orchestrates collection, reporting, and output."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..dora.collector import DORAMetricsCollector
from ..dora.models import DORAConfig, DeploymentRecord
from ..flow.collector import FlowMetricsCollector
from ..flow.models import WorkItem
from ..team_health.collector import TeamHealthCollector
from ..team_health.models import HealthQuestion, HealthResponse
from .reporters import ReportBundle, ConsoleReporter, JSONReporter, MarkdownReporter


class ReportingPipeline:
    """Automated reporting pipeline — collects all metrics and publishes reports.

    Usage:
        pipeline = ReportingPipeline(config=...)
        bundle = pipeline.run(data_dir=Path("./data"))
        bundle.write_to(Path("./output"))
    """

    def __init__(
        self,
        dora_config: Optional[DORAConfig] = None,
        questions: Optional[list[HealthQuestion]] = None,
        reporters: Optional[list] = None,
    ) -> None:
        self.dora_collector = DORAMetricsCollector(dora_config)
        self.flow_collector = FlowMetricsCollector()
        self.health_collector = TeamHealthCollector(questions)
        self.reporters = reporters or [
            ConsoleReporter(),
            JSONReporter(),
            MarkdownReporter(),
        ]

    def run(
        self,
        deployments: Optional[list[DeploymentRecord]] = None,
        work_items: Optional[list[WorkItem]] = None,
        responses: Optional[list[HealthResponse]] = None,
        data_dir: Optional[Path] = None,
    ) -> ReportBundle:
        # Load data from files if dir provided
        if data_dir:
            deployments = deployments or self._load_deployments(data_dir)
            work_items = work_items or self._load_work_items(data_dir)
            responses = responses or self._load_responses(data_dir)

        # Collect metrics
        dora_result = (
            self.dora_collector.collect(deployments or [])
        )
        flow_result = (
            self.flow_collector.collect(work_items or [])
        )
        health_result = (
            self.health_collector.collect(responses or [])
        )

        # Build bundle
        bundle = ReportBundle(
            generated_at=datetime.utcnow(),
            dora=dora_result,
            flow=flow_result,
            health=health_result,
        )

        # Render with each reporter
        for reporter in self.reporters:
            reporter.write(bundle)

        return bundle

    def _load_deployments(self, data_dir: Path) -> list[DeploymentRecord]:
        path = data_dir / "deployments.json"
        if path.exists():
            return json.loads(path.read_text())
        return []

    def _load_work_items(self, data_dir: Path) -> list[WorkItem]:
        path = data_dir / "work_items.json"
        if path.exists():
            return json.loads(path.read_text())
        return []

    def _load_responses(self, data_dir: Path) -> list[HealthResponse]:
        path = data_dir / "survey_responses.json"
        if path.exists():
            return json.loads(path.read_text())
        return []