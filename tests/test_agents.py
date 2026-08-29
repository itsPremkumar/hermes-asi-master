# tests/test_agents.py — Agent Configuration Tests

import os
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

AGENTS_DIR = Path(__file__).parent.parent / "agents"
EXPECTED_AGENTS = [
    "orchestrator",
    "researcher",
    "engineer",
    "operator",
    "quality",
    "curator",
    "guardian",
    "evolver",
]


class TestAgentConfigs:
    def test_all_agents_exist(self):
        for agent_name in EXPECTED_AGENTS:
            agent_file = AGENTS_DIR / agent_name / "agent.yaml"
            assert agent_file.exists(), f"Missing agent config: {agent_name}"

    def test_all_agents_have_required_fields(self):
        for agent_name in EXPECTED_AGENTS:
            with open(AGENTS_DIR / agent_name / "agent.yaml") as f:
                config = yaml.safe_load(f)
            assert "name" in config
            assert "role" in config
            assert "capabilities" in config
            assert "resources" in config

    def test_orchestrator_is_critical(self):
        with open(AGENTS_DIR / "orchestrator" / "agent.yaml") as f:
            config = yaml.safe_load(f)
        assert config["priority"] == "critical"

    def test_guardian_is_critical(self):
        with open(AGENTS_DIR / "guardian" / "agent.yaml") as f:
            config = yaml.safe_load(f)
        assert config["priority"] == "critical"
