#!/usr/bin/env python3
"""
plugin_interface.py — Standard Plugin Contract for Hermes Super-Harness
Defines the universal manifest, lifecycle hooks, and 3-Ring permission security model.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field

class PermissionRing(str, Enum):
    R0_CORE_KERNEL = "R0_CORE_KERNEL"
    R1_SANDBOX_LOCAL = "R1_SANDBOX_LOCAL"
    R2_NETWORK_EXTERNAL = "R2_NETWORK_EXTERNAL"
    R3_UNRESTRICTED = "R3_UNRESTRICTED"

class ToolContract(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    permission: PermissionRing = PermissionRing.R1_SANDBOX_LOCAL

class PluginManifest(BaseModel):
    name: str
    version: str
    description: str
    author: str = "Hermes Open Source Swarm"
    permission_ring: PermissionRing = PermissionRing.R1_SANDBOX_LOCAL
    capabilities: List[str] = Field(default_factory=list)
    tools: List[ToolContract] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class BasePlugin:
    """Base class for all Super-Harness plugins."""
    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.is_active = False

    def on_load(self, harness_context: Dict[str, Any]) -> bool:
        """Called when plugin is loaded and registered into harness."""
        self.is_active = True
        return True

    def on_goal_start(self, goal: Dict[str, Any]) -> None:
        """Lifecycle hook fired when an autonomous mission commences."""
        pass

    def pre_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Lifecycle hook fired before any tool executes. May inspect or transform args."""
        return args

    def post_tool_call(self, tool_name: str, result: Any) -> Any:
        """Lifecycle hook fired after tool execution. May inspect or transform result."""
        return result

    def on_step(self, agent_role: str, step_data: Dict[str, Any]) -> None:
        """Lifecycle hook fired on each step of the multi-agent graph."""
        pass

    def on_goal_complete(self, goal: Dict[str, Any], verdict: Dict[str, Any]) -> None:
        """Lifecycle hook fired upon completion of goal."""
        pass

    def on_unload(self) -> None:
        """Called when plugin is deactivated."""
        self.is_active = False
