"""Shared fixtures for intelligence module tests."""

import os
import sys

# Add src/ to Python path so modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture
def temp_storage(tmp_path):
    """Provide a temporary storage directory."""
    storage = str(tmp_path / "state")
    os.makedirs(storage, exist_ok=True)
    return storage


@pytest.fixture
def memory_engine(temp_storage):
    """Provide a MemoryEngine instance."""
    from intelligence.memory_engine import MemoryEngine
    return MemoryEngine(storage_path=temp_storage)


@pytest.fixture
def world_model(temp_storage):
    """Provide a WorldModel instance."""
    from intelligence.world_model import WorldModel
    return WorldModel(storage_path=temp_storage)


@pytest.fixture
def belief_engine(temp_storage):
    """Provide a BeliefEngine instance."""
    from intelligence.belief_engine import BeliefEngine
    return BeliefEngine(storage_path=temp_storage)


@pytest.fixture
def self_model(temp_storage):
    """Provide a SelfModel instance."""
    from intelligence.self_model import SelfModel
    return SelfModel(storage_path=temp_storage)
