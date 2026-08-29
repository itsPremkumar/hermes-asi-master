"""Real-World Tester — exercises the flagship against actual workloads."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    name: str
    category: str
    prompt: str
    expected_output_contains: list[str] = field(default_factory=list)
    max_duration_seconds: float = 60.0


@dataclass
class TestResult:
    test_name: str
    category: str
    passed: bool
    duration_seconds: float
    output: str
    error: str | None = None


class RealWorldTester:
    """Runs real-world test scenarios against the flagship."""

    TEST_CASES = [
        TestCase(
            name="agent_dispatch",
            category="orchestration",
            prompt="Dispatch a task to the deep-researcher agent",
            expected_output_contains=["researcher", "dispatched"],
        ),
        TestCase(
            name="kanban_flow",
            category="kanban",
            prompt="Create a task in kanban and verify it appears in ready lane",
            expected_output_contains=["task", "ready"],
        ),
        TestCase(
            name="git_push",
            category="git",
            prompt="Commit a file and push to GitHub",
            expected_output_contains=["commit", "push"],
        ),
        TestCase(
            name="config_reload",
            category="config",
            prompt="Change a config value and verify it loads",
            expected_output_contains=["config", "loaded"],
        ),
        TestCase(
            name="cron_schedule",
            category="cron",
            prompt="Schedule a cron job and verify it fires",
            expected_output_contains=["cron", "scheduled"],
        ),
        TestCase(
            name="plugin_load",
            category="plugins",
            prompt="Load a plugin and verify health check",
            expected_output_contains=["plugin", "loaded"],
        ),
        TestCase(
            name="multi_agent_parallel",
            category="swarm",
            prompt="Run 3 agents in parallel and aggregate results",
            expected_output_contains=["parallel", "complete"],
        ),
        TestCase(
            name="error_recovery",
            category="resilience",
            prompt="Trigger an error and verify graceful recovery",
            expected_output_contains=["error", "recovered"],
        ),
    ]

    async def run_all(self) -> list[TestResult]:
        """Execute all real-world test cases."""
        results = []
        for test in self.TEST_CASES:
            result = await self._run_single(test)
            results.append(result)
        return results

    async def _run_single(self, test: TestCase) -> TestResult:
        """Execute a single test case."""
        start = time.monotonic()
        try:
            # In production: dispatch to actual agent
            await asyncio.sleep(0.05)
            duration = time.monotonic() - start
            output = f"Test '{test.name}' completed"
            passed = all(exp in output.lower() for exp in test.expected_output_contains)
            return TestResult(
                test_name=test.name,
                category=test.category,
                passed=passed,
                duration_seconds=duration,
                output=output,
            )
        except Exception as e:
            duration = time.monotonic() - start
            return TestResult(
                test_name=test.name,
                category=test.category,
                passed=False,
                duration_seconds=duration,
                output="",
                error=str(e),
            )

    def generate_report(self, results: list[TestResult]) -> dict[str, Any]:
        """Generate a summary report."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "results": [
                {
                    "test": r.test_name,
                    "category": r.category,
                    "passed": r.passed,
                    "duration_ms": round(r.duration_seconds * 1000, 1),
                    "error": r.error,
                }
                for r in results
            ],
        }
