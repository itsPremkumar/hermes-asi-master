"""Shared fixtures for v9 controllers tests."""

import os
import sys

# Add src/ to Python path so modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pytest
from v9.controllers import ControllerBase, ControllerMetadata, controller
from v9.controllers.registry import ControllerRegistry
from v9.controllers.controllers import (
    LoopController,
    ResourceController,
    BudgetController,
    ErrorController,
    FlowController,
    EventController,
    RetryController,
    ConcurrencyController,
    TimeoutController,
    ValidationController,
    CircuitBreakerController,
    RateLimiterController,
    StateController,
    PipelineController,
    FallbackController,
    ApprovalController,
)


@pytest.fixture
def registry():
    """Provide a pre-populated ControllerRegistry."""
    reg = ControllerRegistry()
    reg.register(LoopController)
    reg.register(ResourceController)
    reg.register(BudgetController)
    reg.register(ErrorController)
    reg.register(FlowController)
    reg.register(EventController)
    reg.register(RetryController)
    reg.register(ConcurrencyController)
    reg.register(TimeoutController)
    reg.register(ValidationController)
    reg.register(CircuitBreakerController)
    reg.register(RateLimiterController)
    reg.register(StateController)
    reg.register(PipelineController)
    reg.register(FallbackController)
    reg.register(ApprovalController)
    return reg
