"""
Base role module defining the abstract BaseRole class.
All agent roles (Proposer, Critic, Judge) inherit from this.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RoleConfig:
    """Configuration for an agent role."""
    name: str
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 512


@dataclass
class Message:
    """A single message in the debate."""
    role: str  # "proposer", "critic", "judge", "user"
    content: str
    round_num: int = 0
    timestamp: float = 0.0

    def __str__(self) -> str:
        return f"[{self.role} r{self.round_num}] {self.content[:80]}..."


@dataclass
class LLMResponse:
    """Response from an LLM call, including metadata."""
    content: str
    usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return self.content


class BaseRole(ABC):
    """Abstract base class for all debate roles."""

    def __init__(self, config: RoleConfig):
        self.config = config
        self.history: list[Message] = []

    @abstractmethod
    def act(self, context: list[Message], round_num: int) -> LLMResponse:
        """
        Produce a response given the current debate context.

        Args:
            context: All messages produced so far in the debate
            round_num: Current round number (0-indexed)

        Returns:
            LLMResponse with the role's contribution
        """
        pass

    def add_to_history(self, msg: Message) -> None:
        """Record a message in this role's local history."""
        self.history.append(msg)

    def reset_history(self) -> None:
        """Clear the role's local message history."""
        self.history.clear()

    @property
    def name(self) -> str:
        return self.config.name
