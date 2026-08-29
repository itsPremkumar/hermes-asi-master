# tests/test_config.py — Configuration Tests

import os
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


class TestSystemConfig:
    def test_system_yaml_exists(self):
        assert (CONFIG_DIR / "system.yaml").exists()

    def test_system_has_required_keys(self):
        config = load_yaml(CONFIG_DIR / "system.yaml")
        assert "system" in config
        assert "orchestrator" in config
        assert "memory" in config
        assert "fleet" in config

    def test_memory_backends_configured(self):
        config = load_yaml(CONFIG_DIR / "system.yaml")
        memory = config.get("memory", {})
        assert "working" in memory
        assert "episodic" in memory
        assert "semantic" in memory


class TestModelsConfig:
    def test_models_yaml_exists(self):
        assert (CONFIG_DIR / "models.yaml").exists()

    def test_has_primary_model(self):
        config = load_yaml(CONFIG_DIR / "models.yaml")
        assert "primary" in config.get("models", {})


class TestAgentsConfig:
    def test_agents_yaml_exists(self):
        assert (CONFIG_DIR / "agents.yaml").exists()

    def test_all_agents_have_scaling(self):
        config = load_yaml(CONFIG_DIR / "agents.yaml")
        agents = config.get("agents", {})
        for name, agent in agents.items():
            assert "scaling" in agent, f"{name} missing scaling"
            assert "min" in agent["scaling"]
            assert "max" in agent["scaling"]


class TestSafetyConfig:
    def test_safety_yaml_exists(self):
        assert (CONFIG_DIR / "safety.yaml").exists()

    def test_has_policies(self):
        config = load_yaml(CONFIG_DIR / "safety.yaml")
        assert len(config.get("policies", [])) > 0
