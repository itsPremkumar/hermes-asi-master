"""
P2.9.3 — Motivation Arbiter

Combines curiosity, competence, and extrinsic goals into motivation signal.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MotivationSignal:
    """A motivation signal for decision making."""
    source: str  # curiosity, competence, extrinsic
    intensity: float  # 0.0 to 1.0
    description: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class MotivationArbiter:
    """Arbitrates between different motivation sources."""

    def __init__(self) -> None:
        self.signals: list[MotivationSignal] = []
        self.weights: dict[str, float] = {
            "curiosity": 0.4,
            "competence": 0.3,
            "extrinsic": 0.3,
        }

    def add_signal(self, source: str, intensity: float, description: str = "", metadata: dict[str, Any] | None = None) -> MotivationSignal:
        """Add a motivation signal."""
        signal = MotivationSignal(
            source=source,
            intensity=min(1.0, max(0.0, intensity)),
            description=description,
            metadata=metadata or {},
        )
        self.signals.append(signal)
        return signal

    def arbitrate(self) -> MotivationSignal | None:
        """Select the most intense motivation signal."""
        if not self.signals:
            return None
        # Weight signals by source and intensity
        weighted = []
        for signal in self.signals[-10:]:  # recent signals only
            weight = self.weights.get(signal.source, 0.5)
            weighted.append((signal, signal.intensity * weight))
        weighted.sort(key=lambda x: x[1], reverse=True)
        return weighted[0][0] if weighted else None

    def get_composite_signal(self) -> float:
        """Get a composite motivation value (0.0 to 1.0)."""
        if not self.signals:
            return 0.0
        recent = self.signals[-10:]
        total = sum(s.intensity * self.weights.get(s.source, 0.5) for s in recent)
        return min(1.0, total / len(recent))
