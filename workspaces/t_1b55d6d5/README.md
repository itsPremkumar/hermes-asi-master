# Engineering Metrics System

DORA, Flow & Team Health Dashboard with automated reporting pipeline.

## Structure

metrics-system/
  dora/           — Deployment Frequency, Lead Time, Change Failure Rate, Time to Restore
  flow/           — Cycle Time, Throughput, WIP, Load, Efficiency
  team_health/    — Survey questions, responses, composite health score
  dashboard/      — Config + markdown/console renderer
  pipeline/       — ReportingPipeline orchestrates collection and publishing
  tests/          — Pytest tests with real assertions

## Quick Start

    python -m metrics-system.tests.test_metrics

## Deliverables

- Metrics configuration files in workspace
- Automated reporting pipeline (JSON + Markdown + Console reporters)
- Push target: repository with engineering dashboards