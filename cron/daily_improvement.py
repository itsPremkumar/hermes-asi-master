"""Daily Improvement Cron — schedules and runs daily self-improvement tasks."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

HERMES_HOME = Path.home() / ".hermes"
CRON_DIR = HERMES_HOME / "cron"


@dataclass
class CronJob:
    name: str
    schedule: str
    task: str
    enabled: bool = True
    last_run: float | None = None
    last_status: str | None = None


class DailyImprovementCron:
    """Manages daily self-improvement tasks for the flagship."""

    DAILY_JOBS = [
        CronJob(
            name="health-check",
            schedule="0 6 * * *",
            task="Run full system health check and report",
        ),
        CronJob(
            name="log-rotation",
            schedule="0 7 * * *",
            task="Rotate logs and clean up old entries",
        ),
        CronJob(
            name="dependency-audit",
            schedule="0 8 * * *",
            task="Audit dependencies for security vulnerabilities",
        ),
        CronJob(
            name="performance-benchmark",
            schedule="0 9 * * *",
            task="Run performance benchmarks and compare to baseline",
        ),
        CronJob(
            name="config-backup",
            schedule="0 10 * * *",
            task="Backup all config files to GitHub",
        ),
        CronJob(
            name="test-suite",
            schedule="0 11 * * *",
            task="Run full test suite and report results",
        ),
        CronJob(
            name="documentation-sync",
            schedule="0 12 * * *",
            task="Sync documentation with code changes",
        ),
        CronJob(
            name="model-health-check",
            schedule="0 13 * * *",
            task="Verify all model providers are responsive",
        ),
    ]

    def __init__(self):
        self.jobs: dict[str, CronJob] = {job.name: job for job in self.DAILY_JOBS}

    def list_jobs(self) -> list[dict[str, Any]]:
        """List all daily improvement jobs."""
        return [
            {
                "name": job.name,
                "schedule": job.schedule,
                "task": job.task,
                "enabled": job.enabled,
                "last_run": job.last_run,
                "last_status": job.last_status,
            }
            for job in self.jobs.values()
        ]

    async def run_job(self, name: str) -> dict[str, Any]:
        """Run a specific job by name."""
        job = self.jobs.get(name)
        if not job:
            return {"error": f"Job '{name}' not found"}
        if not job.enabled:
            return {"error": f"Job '{name}' is disabled"}

        logger.info(f"Running daily job: {name}")
        start = time.monotonic()
        try:
            # In production: dispatch to actual task handler
            await asyncio.sleep(0.1)
            duration = time.monotonic() - start
            job.last_run = time.time()
            job.last_status = "ok"
            return {
                "name": name,
                "status": "ok",
                "duration_seconds": duration,
            }
        except Exception as e:
            duration = time.monotonic() - start
            job.last_run = time.time()
            job.last_status = "error"
            return {
                "name": name,
                "status": "error",
                "duration_seconds": duration,
                "error": str(e),
            }

    async def run_all(self) -> list[dict[str, Any]]:
        """Run all enabled daily jobs."""
        results = []
        for name in self.jobs:
            result = await self.run_job(name)
            results.append(result)
        return results

    def to_json(self) -> str:
        """Serialize jobs to JSON for cron scheduler."""
        return json.dumps(self.list_jobs(), indent=2)
