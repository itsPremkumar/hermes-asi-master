"""
Observability & Evaluation Layer.

Provides comprehensive observability and evaluation for AI systems:
- Metrics collection (counter, gauge, histogram)
- Structured logging with JSON format
- Distributed tracing with span-based tracking
- Evaluation engine for quality, safety, and performance scoring
- Alert manager for threshold and anomaly detection
"""

from .metrics import MetricsCollector
from .logging import LogCollector
from .tracing import TraceCollector
from .evaluation import EvaluationEngine
from .alerting import AlertManager

__all__ = [
    "MetricsCollector",
    "LogCollector",
    "TraceCollector",
    "EvaluationEngine",
    "AlertManager",
]
