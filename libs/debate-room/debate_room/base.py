"""Re-export base classes for convenience."""

from .roles.base import BaseRole, Message, LLMResponse, RoleConfig

__all__ = ["BaseRole", "Message", "LLMResponse", "RoleConfig"]
