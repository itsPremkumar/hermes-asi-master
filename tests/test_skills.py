# tests/test_skills.py — Skill Registry Tests

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

SKILLS_DIR = Path(__file__).parent.parent / "skills"
EXPECTED_SKILLS = [
    "fleet-orchestration",
    "agent-lifecycle",
    "load-balancing",
    "memory-management",
    "context-compression",
    "episodic-recall",
    "task-decomposition",
    "pipeline-builder",
    "retry-orchestration",
    "inter-agent-messaging",
    "event-bus",
    "notification-dispatch",
    "safety-governor",
    "audit-logging",
    "access-control",
    "evolution-engine",
    "performance-profiling",
    "experiment-tracking",
    "deployment-automation",
    "monitoring-observability",
    "security-hardening",
]


class TestSkillRegistry:
    def test_all_skills_exist(self):
        for skill_name in EXPECTED_SKILLS:
            skill_dir = SKILLS_DIR / skill_name
            assert skill_dir.exists(), f"Missing skill: {skill_name}"
            assert (skill_dir / "SKILL.md").exists(), f"Missing SKILL.md: {skill_name}"

    def test_skill_count(self):
        actual = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        assert len(actual) >= 21, f"Expected 21+ skills, found {len(actual)}"
