"""MCP tool layer — package root.

Exposes:
    mcp_pool.MCPToolClientPool  — pooled MCP client connections (stdio + HTTP) with failover
    registry.ToolRegistry        — unified registry of MCP + local python tools
    sandbox.SandboxedToolWrapper — allowlist / fs-jail wrapper for local tool execution
    adapters.to_langgraph_tools  — LangGraph ToolNode-compatible bindings
"""
from __future__ import annotations

from agentforge_x.tools.mcp_pool import (
    MCPToolClientPool,
    MCPServerConfig,
    MCPToolResult,
)
from agentforge_x.tools.registry import ToolRegistry, ToolEntry, ToolKind, Capability
from agentforge_x.tools.sandbox import (
    SandboxedToolWrapper,
    FS_JAIL_ROOT,
    DEFAULT_ALLOWLIST,
)
from agentforge_x.tools.adapters import (
    to_langgraph_tools,
    ToolNodeCompatibleTool,
)

__all__ = [
    "MCPToolClientPool",
    "MCPServerConfig",
    "MCPToolResult",
    "ToolRegistry",
    "ToolEntry",
    "ToolKind",
    "Capability",
    "SandboxedToolWrapper",
    "FS_JAIL_ROOT",
    "DEFAULT_ALLOWLIST",
    "to_langgraph_tools",
    "ToolNodeCompatibleTool",
]
