"""registry.py — unified tool registry (MCP + local python), capability-tagged.

The registry is the single source of truth for which tools an agent can call.
It unifies:

  * **MCP tools** — discovered from one or more MCP servers (via
    :class:`~agentforge_x.tools.mcp_pool.MCPToolClientPool`) and invoked
    through the pooled, failover-capable client.
  * **Local Python tools** — plain callables registered at runtime
    (``sync`` or ``async``), optionally wrapped in a
    :class:`~agentforge_x.tools.sandbox.SandboxedToolWrapper`.

Every registered tool carries a set of *capability tags* (e.g.
``{"filesystem", "read"}`` or ``{"network", "search"}``) so the planner can
route requests to tools that have the right capability, and the sandbox can
enforce least privilege.
"""
from __future__ import annotations

import asyncio
import functools
import inspect
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Optional

from mcp.types import Tool as MCPTool

log = logging.getLogger("agentforge_x.tools.registry")


# ---------------------------------------------------------------------------
# Capability
# ---------------------------------------------------------------------------


class Capability(str, Enum):
    """Well-known capability tags.

    Free-form string tags are also allowed; these are the canonical ones used
    across agentforge-x for routing and sandbox policy.
    """

    # Filesystem
    FS_READ = "filesystem.read"
    FS_WRITE = "filesystem.write"
    FS_EXEC = "filesystem.exec"

    # Network
    NET_FETCH = "network.fetch"
    NET_SEARCH = "network.search"

    # Computation
    COMPUTE_MATH = "compute.math"
    COMPUTE_CODE = "compute.code"

    # MCP / tools
    MCP_TOOL = "mcp.tool"

    # Shell
    SHELL = "shell"

    # Destructive
    DESTRUCTIVE = "destructive"


# ---------------------------------------------------------------------------
# Tool kinds
# ---------------------------------------------------------------------------


class ToolKind(str, Enum):
    """Where a tool comes from and how it is invoked."""

    MCP = "mcp"
    LOCAL = "local"


@dataclass
class ToolEntry:
    """A registered tool, agnostic of its origin."""

    name: str
    kind: ToolKind
    description: str
    capabilities: set[str]
    # For MCP tools: reference to the MCP tool def + server name
    mcp_tool: Optional[MCPTool] = None
    server_name: str = ""
    # For local tools: the callable itself
    func: Optional[Callable[..., Any]] = None
    is_async: bool = False
    # Schema (JSON schema dict) describing arguments.
    input_schema: dict[str, Any] = field(default_factory=dict)
    # Safety / policy
    destructive: bool = False


# ---------------------------------------------------------------------------
# Local result type (mirrors MCPToolResult shape for unified handling)
# ---------------------------------------------------------------------------


@dataclass
class ToolResult:
    """Unified result returned by ``ToolRegistry.call``.

    Always carries ``success``; never raises to the caller.
    """

    tool: str
    success: bool
    content: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: float = 0.0
    tool_call_id: str = ""
    # Which backend executed it (server name for MCP, or "local")
    source: str = "local"

    @property
    def text(self) -> str:
        chunks = [b.get("text", "") for b in self.content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(chunks)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class ToolRegistry:
    """Unified, capability-tagged registry of MCP + local tools.

    Example
    -------
    >>> async def setup():
    ...     reg = ToolRegistry()
    ...     await reg.connect_mcp_pool(pool)
    ...     reg.register_local(echo, name="echo", capabilities={"shell"})
    ...     result = await reg.call("echo", {"text": "hi"})
    """

    def __init__(self) -> None:
        self._mcp_tools: dict[str, ToolEntry] = {}
        self._local_tools: dict[str, ToolEntry] = {}
        self._pool: Optional[Any] = None  # MCPToolClientPool (lazy import)

    # -- MCP integration --------------------------------------------------

    def set_mcp_pool(self, pool: Any) -> None:
        """Attach a pooled MCP client. Tools are discovered lazily."""
        self._pool = pool

    async def discover_mcp_tools(self) -> list[ToolEntry]:
        """Query all healthy MCP servers and register their tools.

        Returns the list of newly-registered MCP tools. Re-discovering
        refreshes the set (servers can come and go).
        """
        if self._pool is None:
            return []

        tools = await self._pool.list_tools()
        # Wipe stale MCP entries so we don't accumulate dead tools.
        self._mcp_tools.clear()
        for mcp_tool in tools:
            entry = ToolEntry(
                name=mcp_tool.name,
                kind=ToolKind.MCP,
                description=mcp_tool.description,
                capabilities=Capability.MCP_TOOL.value and {Capability.MCP_TOOL.value},
                mcp_tool=mcp_tool,
                server_name=mcp_tool.server_name,
                input_schema=mcp_tool.input_schema,
                func=None,
                is_async=True,
            )
            self._mcp_tools[mcp_tool.name] = entry
        log.debug("registry: discovered %d MCP tools (total MCP=%d, local=%d)",
                  len(tools), len(self._mcp_tools), len(self._local_tools))
        return list(self._mcp_tools.values())

    # -- local tools ------------------------------------------------------

    def register_local(
        self,
        func: Callable[..., Any],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[set[str]] = None,
        destructive: bool = False,
        input_schema: Optional[dict[str, Any]] = None,
    ) -> ToolEntry:
        """Register a local Python tool (sync or async callable)."""
        tool_name = name or getattr(func, "__name__", "anonymous")
        sig = inspect.signature(func)
        if input_schema is None:
            input_schema = _schema_from_signature(sig)
        desc = description or (func.__doc__ or "").strip().split("\n")[0]

        entry = ToolEntry(
            name=tool_name,
            kind=ToolKind.LOCAL,
            description=desc,
            capabilities=capabilities or set(),
            func=func,
            is_async=inspect.iscoroutinefunction(func),
            input_schema=input_schema,
            destructive=destructive,
        )
        self._local_tools[tool_name] = entry
        log.debug("registry: registered local tool '%s' (async=%s)",
                  tool_name, entry.is_async)
        return entry

    def register_local_batch(
        self, items: list[tuple[Callable[..., Any], dict[str, Any]]]
    ) -> list[ToolEntry]:
        """Register several local tools at once (convenience for adapters)."""
        results = []
        for func, kwargs in items:
            results.append(self.register_local(func, **kwargs))
        return results

    # -- queries ----------------------------------------------------------

    def has(self, name: str) -> bool:
        return name in self._local_tools or name in self._mcp_tools

    def get(self, name: str) -> Optional[ToolEntry]:
        return self._local_tools.get(name) or self._mcp_tools.get(name)

    def all_tools(self) -> list[ToolEntry]:
        return list(self._local_tools.values()) + list(self._mcp_tools.values())

    def local_tools(self) -> list[ToolEntry]:
        return list(self._local_tools.values())

    def mcp_tools(self) -> list[ToolEntry]:
        return list(self._mcp_tools.values())

    def tools_by_capability(self, capability: str) -> list[ToolEntry]:
        """Return all tools tagged with the given capability."""
        return [t for t in self.all_tools() if capability in t.capabilities]

    def tool_names(self) -> list[str]:
        return [t.name for t in self.all_tools()]

    # -- invocation -------------------------------------------------------

    def _resolve_schema(self, entry: ToolEntry) -> Optional[type]:
        """Build a pydantic model class from the JSON schema, if feasible."""
        try:
            from pydantic import BaseModel, create_model

            schema = entry.input_schema or {}
            if not schema.get("properties"):
                return None
            fields: dict[str, Any] = {}
            for pname, pinfo in schema.get("properties", {}).items():
                ptype = _python_type(pinfo.get("type", "string"))
                required = pname in schema.get("required", [])
                if required:
                    fields[pname] = (ptype, ...)
                else:
                    fields[pname] = (Optional[ptype], None)
            return create_model(f"{entry.name}_Input", **fields)  # type: ignore[arg-type]
        except Exception:  # noqa: BLE101
            return None

    async def call(
        self, tool_name: str, arguments: Optional[dict[str, Any]] = None
    ) -> ToolResult:
        """Invoke a tool by name.

        Dispatches to the local callable or the MCP pooled client. Never
        raises — failures are returned as ``ToolResult(success=False)``.
        """
        arguments = arguments or {}
        call_id = str(uuid.uuid4())
        start = time.perf_counter()

        entry = self.get(tool_name)
        if entry is None:
            return ToolResult(
                tool=tool_name,
                success=False,
                error=f"Tool not found: {tool_name}",
                source="none",
                tool_call_id=call_id,
            )

        try:
            if entry.kind == ToolKind.LOCAL:
                entry = self._local_tools[tool_name]
                result = await self._call_local(entry, arguments)
            else:
                result = await self._call_mcp(tool_name, arguments)
        except Exception as exc:  # noqa: BLE101
            duration = (time.perf_counter() - start) * 1000
            return ToolResult(
                tool=tool_name,
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=duration,
                source=entry.kind.value,
                tool_call_id=call_id,
            )

        duration = (time.perf_counter() - start) * 1000
        return ToolResult(
            tool=tool_name,
            success=result.success,
            content=result.content,
            error=result.error,
            duration_ms=duration,
            source=result.source or entry.kind.value,
            tool_call_id=call_id,
        )

    async def _call_local(self, entry: ToolEntry, arguments: dict[str, Any]) -> ToolResult:
        """Invoke a local registered callable."""
        call_id = str(uuid.uuid4())
        # Bind arguments, filling defaults for missing ones.
        sig = inspect.signature(entry.func)  # type: ignore[arg-type]
        kwargs: dict[str, Any] = {}
        for pname, param in sig.parameters.items():
            if pname in arguments:
                kwargs[pname] = arguments[pname]
            elif param.default is not inspect.Parameter.empty:
                kwargs[pname] = param.default
            elif param.kind in (inspect.Parameter.VAR_POSITIONAL,
                                inspect.Parameter.VAR_KEYWORD):
                continue
            else:
                kwargs[pname] = None  # will likely error in the call
        output = entry.func(**kwargs)  # type: ignore[operator]
        if inspect.isawaitable(output):
            output = await output
        text = output if isinstance(output, str) else str(output)
        return ToolResult(
            tool=entry.name,
            success=True,
            content=[{"type": "text", "text": text}],
            source="local",
            tool_call_id=call_id,
        )

    async def _call_mcp(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Invoke a tool through the MCP pool (with failover)."""
        if self._pool is None:
            return ToolResult(
                tool=tool_name,
                success=False,
                error="No MCP pool configured for tool: " + tool_name,
                source="mcp",
            )
        result = await self._pool.call_tool(tool_name, arguments)
        return ToolResult(
            tool=tool_name,
            success=result.success,
            content=result.content,
            error=result.error,
            duration_ms=result.duration_ms,
            source=result.server or "mcp",
            tool_call_id=result.tool_call_id,
        )

    # -- management -------------------------------------------------------

    def unregister(self, name: str) -> bool:
        """Remove a tool from either local or MCP registry."""
        for store in (self._local_tools, self._mcp_tools):
            if name in store:
                del store[name]
                return True
        return False

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _schema_from_signature(sig: inspect.Signature) -> dict[str, Any]:
    """Infer a minimal JSON schema from a callable signature."""
    properties: dict[str, Any] = {}
    required: list[str] = []
    for pname, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL,
                          inspect.Parameter.VAR_KEYWORD):
            continue
        ptype = _python_type_to_schema(param.annotation)
        properties[pname] = {**ptype} if ptype else {"type": "string"}
        if param.default is inspect.Parameter.empty:
            required.append(pname)
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema


def _python_type_to_schema(annotation: Any) -> dict[str, Any]:
    """Map a Python type annotation to a JSON-schema fragment."""
    if annotation is inspect.Parameter.empty:
        return {"type": "string"}
    name = getattr(annotation, "__name__", str(annotation))
    mapping = {
        "str": {"type": "string"},
        "int": {"type": "integer"},
        "float": {"type": "number"},
        "bool": {"type": "boolean"},
        "list": {"type": "array"},
        "dict": {"type": "object"},
    }
    return mapping.get(name, {"type": "string"})


def _python_type(json_type: str) -> type:
    return {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }.get(json_type, str)


# Convenience: decorator for registering local tools
def tool(
    name: Optional[str] = None,
    *,
    description: Optional[str] = None,
    capabilities: Optional[set[str]] = None,
    destructive: bool = False,
):
    """Decorator: register a function as a local tool.

    Usage::

        @tool(capabilities={"shell"})
        def echo(text: str) -> str:
            return text
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Stash metadata; the registry picks it up via ``register_local``.
        func._agentforge_tool = True  # type: ignore[attr-defined]
        func._agentforge_tool_meta = {  # type: ignore[attr-defined]
            "name": name,
            "description": description,
            "capabilities": capabilities,
            "destructive": destructive,
        }

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
