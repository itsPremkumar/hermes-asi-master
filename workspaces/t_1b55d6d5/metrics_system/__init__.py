from dataclasses import dataclass

from metrics_system.pipeline.reporters import ReportBundle, ConsoleReporter, JSONReporter, MarkdownReporter
from metrics_system.dora.models import DORAResult, DeploymentRecord
from metrics_system.flow.models import FlowResult, WorkItem
from metrics_system.team_health.models import HealthScore, HealthQuestion, HealthResponse
from metrics_system.dashboard.config import DashboardConfig, PanelConfig
from metrics_system.pipeline.engine import ReportingPipeline
from metrics_system.dora.collector import DORAMetricsCollector
from metrics_system.flow.collector import FlowMetricsCollector
from metrics_system.team_health.collector import TeamHealthCollector
from metrics_system.dashboard.renderer import DashboardRenderer