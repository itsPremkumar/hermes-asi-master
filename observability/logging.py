"""
Observability & Evaluation Layer — Log Collector.

Provides structured logging with JSON format and log levels.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import threading
import json


@dataclass
class LogEntry:
    """A single log entry."""
    timestamp: str
    level: str
    component: str
    message: str
    metadata: dict = field(default_factory=dict)
    task_id: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "component": self.component,
            "message": self.message,
            "metadata": self.metadata,
            "task_id": self.task_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class LogCollector:
    """Thread-safe structured log collector."""

    def __init__(self):
        self._logs: list[LogEntry] = []
        self._lock = threading.Lock()

    def log(
        self,
        level: str,
        message: str,
        component: str = "system",
        metadata: Optional[dict] = None,
        task_id: str = "",
    ):
        """Log a message."""
        with self._lock:
            self._logs.append(LogEntry(
                timestamp=datetime.utcnow().isoformat() + "Z",
                level=level.upper(),
                component=component,
                message=message,
                metadata=metadata or {},
                task_id=task_id,
            ))

    def debug(self, message: str, component: str = "system", **kwargs):
        """Log a debug message."""
        self.log("DEBUG", message, component, **kwargs)

    def info(self, message: str, component: str = "system", **kwargs):
        """Log an info message."""
        self.log("INFO", message, component, **kwargs)

    def warning(self, message: str, component: str = "system", **kwargs):
        """Log a warning message."""
        self.log("WARNING", message, component, **kwargs)

    def error(self, message: str, component: str = "system", **kwargs):
        """Log an error message."""
        self.log("ERROR", message, component, **kwargs)

    def critical(self, message: str, component: str = "system", **kwargs):
        """Log a critical message."""
        self.log("CRITICAL", message, component, **kwargs)

    def get_logs(
        self,
        level: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> list[LogEntry]:
        """Get logs with optional filters."""
        with self._lock:
            results = self._logs.copy()

        if level:
            results = [l for l in results if l.level == level.upper()]
        if component:
            results = [l for l in results if l.component == component]
        if start_time:
            results = [l for l in results if l.timestamp >= start_time]
        if end_time:
            results = [l for l in results if l.timestamp <= end_time]

        return results

    def search_logs(self, query: str) -> list[LogEntry]:
        """Search logs by message content."""
        with self._lock:
            return [l for l in self._logs if query.lower() in l.message.lower()]

    def clear(self):
        """Clear all logs."""
        with self._lock:
            self._logs.clear()
