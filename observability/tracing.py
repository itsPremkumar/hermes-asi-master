"""
Observability & Evaluation Layer — Trace Collector.

Provides distributed tracing with span-based tracking.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import threading
import uuid


@dataclass
class Span:
    """A trace span."""
    span_id: str
    trace_id: str
    name: str
    parent_span_id: str = ""
    start_time: str = ""
    end_time: str = ""
    status: str = "ok"
    tags: dict = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds."""
        if self.start_time and self.end_time:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
            return (end - start).total_seconds() * 1000
        return 0.0


class TraceCollector:
    """Thread-safe trace collector."""

    def __init__(self):
        self._traces: dict[str, list[Span]] = {}
        self._lock = threading.Lock()

    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: str = "",
        tags: Optional[dict] = None,
    ) -> Span:
        """Start a new span."""
        span = Span(
            span_id=str(uuid.uuid4())[:8],
            trace_id=trace_id or str(uuid.uuid4()),
            name=name,
            parent_span_id=parent_span_id,
            start_time=datetime.utcnow().isoformat() + "Z",
            tags=tags or {},
        )

        with self._lock:
            if span.trace_id not in self._traces:
                self._traces[span.trace_id] = []
            self._traces[span.trace_id].append(span)

        return span

    def end_span(self, span_id: str, trace_id: str, status: str = "ok"):
        """End a span."""
        with self._lock:
            if trace_id in self._traces:
                for span in self._traces[trace_id]:
                    if span.span_id == span_id:
                        span.end_time = datetime.utcnow().isoformat() + "Z"
                        span.status = status
                        break

    def get_trace(self, trace_id: str) -> list[Span]:
        """Get all spans for a trace."""
        with self._lock:
            return self._traces.get(trace_id, []).copy()

    def search_traces(self, name: str) -> list[str]:
        """Find trace IDs containing a span with the given name."""
        with self._lock:
            return [
                trace_id
                for trace_id, spans in self._traces.items()
                if any(s.name == name for s in spans)
            ]
