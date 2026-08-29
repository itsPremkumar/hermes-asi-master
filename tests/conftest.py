# tests/conftest.py — Pytest Configuration and Fixtures

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config_dir():
    """Return the config directory path."""
    return Path(__file__).parent.parent / "config"


@pytest.fixture
def sample_agent_config():
    """Return a sample agent configuration."""
    return {
        "name": "test-agent",
        "role": "test",
        "priority": "medium",
        "capabilities": ["test_capability"],
        "resources": {"cpu": "0.5", "memory": "512Mi"},
    }


@pytest.fixture
def sample_task():
    """Return a sample task definition."""
    return {
        "id": "test-task-001",
        "type": "test",
        "action": "noop",
        "params": {},
        "priority": "low",
    }
