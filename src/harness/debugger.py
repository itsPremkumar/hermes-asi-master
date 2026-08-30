"""
t_f0087914 — Debugger Module

Debug sessions, stack frames, expression evaluation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class StackFrame:
    """A stack frame."""
    filename: str
    lineno: int
    function: str
    locals: dict[str, Any] = field(default_factory=dict)


@dataclass
class DebugSession:
    """A debugging session."""
    id: str
    target: str
    status: str = "active"  # active, stopped, terminated
    frames: list[StackFrame] = field(default_factory=list)
    locals: dict[str, Any] = field(default_factory=dict)
    breakpoints: list[int] = field(default_factory=list)

    def add_frame(self, frame: StackFrame) -> None:
        self.frames.append(frame)

    def set_local(self, name: str, value: Any) -> None:
        self.locals[name] = value


class Debugger:
    """Manage debug sessions."""

    def __init__(self) -> None:
        self.sessions: dict[str, DebugSession] = {}

    def start_session(self, target: str) -> DebugSession:
        session = DebugSession(
            id=str(uuid.uuid4().hex[:8]),
            target=target,
        )
        self.sessions[session.id] = session
        return session

    def stop_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            self.sessions[session_id].status = "stopped"
            return True
        return False

    def get_session(self, session_id: str) -> Optional[DebugSession]:
        return self.sessions.get(session_id)

    def list_sessions(self) -> list[DebugSession]:
        return list(self.sessions.values())

    def evaluate(self, session_id: str, expression: str) -> Any:
        """Evaluate an expression in a session context."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        try:
            # Simple evaluation using session locals
            return eval(expression, {"__builtins__": {}}, session.locals)
        except Exception:
            return None
