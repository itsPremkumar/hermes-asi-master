"""v9 · Engineering Control Plane — Controller Base.

All controllers inherit from ControllerBase and must implement:
- run(state: dict) -> dict: Execute the controller logic and return new state.
- validate(state: tuple[bool, list[str]]: Validate preconditions.

Each controller defines METADATA describing its name, version, level, and tags.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass
class ControllerMetadata:
    """Metadata for a controller plugin."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    level: int = 1  # 1-10, where 10 requires human approval
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "level": self.level,
            "tags": list(self.tags),
            "dependencies": list(self.dependencies),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ControllerMetadata":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @property
    def requires_approval(self) -> bool:
        return self.level >= 10


class ControllerBase(ABC):
    """Abstract base class for all engineering controllers.

    Subclass this to create a new controller. Override the
    `run` method to implement the controller logic.

    Usage:
        class MyController(ControllerBase):
            METADATA = ControllerMetadata(name="my_controller", description="...")

            def run(self, state: dict[str, Any]) -> dict[str, Any]:
                return new_state
    """

    METADATA: ControllerMetadata | None = None

    def __init__(self) -> None:
        if self.METADATA is None:
            raise ValueError(f"{self.__class__.__name__} must define METADATA")

    @abstractmethod
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Run the controller on the given state. Returns new state."""
        ...

    def validate(self, state: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate that the controller can run on the given state."""
        return True, []

    def cleanup(self) -> None:
        """Clean up resources after the controller finishes."""
        pass

    @property
    def name(self) -> str:
        return self.METADATA.name

    @property
    def level(self) -> int:
        return self.METADATA.level

    @property
    def requires_approval(self) -> bool:
        return self.METADATA.requires_approval

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.METADATA.to_dict(),
            "class": self.__class__.__name__,
        }


def controller(
    name: str,
    version: str = "1.0.0",
    description: str = "",
    author: str = "",
    level: int = 1,
    tags: Sequence[str] | None = None,
    dependencies: Sequence[str] | None = None,
):
    """Decorator to register a class as a controller.

    Usage:
        @controller(name="my_controller", description="...")
        class MyController(ControllerBase):
            def run(self, state):
                return state
    """

    def decorator(cls):
        cls.METADATA = ControllerMetadata(
            name=name,
            version=version,
            description=description,
            author=author,
            level=level,
            tags=list(tags) if tags else [],
            dependencies=list(dependencies) if dependencies else [],
        )
        return cls

    return decorator
