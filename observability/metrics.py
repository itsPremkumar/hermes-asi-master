"""
Observability & Evaluation Layer — Metrics Collector.

Provides metrics collection with counter, gauge, and histogram types.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import threading
import time


@dataclass
class Metric:
    """A single metric data point."""
    name: str
    value: float
    labels: dict = field(default_factory=dict)
    timestamp: float = 0.0
    type: str = "gauge"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class MetricsCollector:
    """Thread-safe metrics collector."""

    def __init__(self):
        self._metrics: list[Metric] = []
        self._lock = threading.Lock()

    def record_counter(self, name: str, value: float = 1, labels: Optional[dict] = None):
        """Record a counter metric."""
        with self._lock:
            self._metrics.append(Metric(
                name=name,
                value=value,
                labels=labels or {},
                type="counter",
            ))

    def record_gauge(self, name: str, value: float, labels: Optional[dict] = None):
        """Record a gauge metric."""
        with self._lock:
            self._metrics.append(Metric(
                name=name,
                value=value,
                labels=labels or {},
                type="gauge",
            ))

    def record_histogram(self, name: str, value: float, labels: Optional[dict] = None):
        """Record a histogram metric."""
        with self._lock:
            self._metrics.append(Metric(
                name=name,
                value=value,
                labels=labels or {},
                type="histogram",
            ))

    def get_metrics(
        self,
        name: Optional[str] = None,
        metric_type: Optional[str] = None,
    ) -> list[Metric]:
        """Get all metrics, optionally filtered."""
        with self._lock:
            results = self._metrics.copy()

        if name:
            results = [m for m in results if m.name == name]
        if metric_type:
            results = [m for m in results if m.type == metric_type]

        return results

    def get_counter(self, name: str) -> float:
        """Get the total value for a counter."""
        metrics = self.get_metrics(name=name, metric_type="counter")
        return sum(m.value for m in metrics)

    def get_gauge(self, name: str) -> float:
        """Get the latest value for a gauge."""
        metrics = self.get_metrics(name=name, metric_type="gauge")
        if metrics:
            return metrics[-1].value
        return 0.0

    def get_histogram_stats(self, name: str) -> dict[str, float]:
        """Get histogram statistics."""
        metrics = self.get_metrics(name=name, metric_type="histogram")
        if not metrics:
            return {"count": 0, "sum": 0, "min": 0, "max": 0, "avg": 0}

        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
        }

    def clear(self):
        """Clear all metrics."""
        with self._lock:
            self._metrics.clear()
