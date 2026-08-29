"""mcp_pool.py — pooled MCP client connections (stdio + HTTP) with failover.

Design goals (per task spec):
  * Connect to multiple MCP servers (stdio or HTTP/streamable-http).
  * Pool / reuse a single ``ClientSession`` per server so we don't re-initialize
    on every tool call.
  * Fail over between servers when one is unhealthy: tries the next server in
    the pool for a given tool, returning the first successful result.
  * Timeouts + retries on every network call (no call may block forever).
  * Never crashes the session: every failure is returned as a structured
    ``MCPToolResult`` with ``success=False``.

The public entry point is :class:`MCPToolClientPool`.
"""
from __future__ import annotations

import asyncio
import logging
import sys
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from mcp import ClientSession, StdioServerParameters
from mcp import stdio_client
from mcp.types import CallToolResult, Tool

log = logging.getLogger("agentforge_x.tools.mcp_pool")

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Transport(str, Enum):
    """How an MCP server is connected."""

    STDIO = "stdio"
    HTTP = "http"


@dataclass
class MCPServerConfig:
    """Static configuration for an MCP server connection."""

    name: str
    transport: Transport
    # For stdio transport
    command: Optional[list[str]] = None
    env: Optional[dict[str, str]] = None
    # For HTTP transport
    url: Optional[str] = None
    # Runtime tuning
    timeout: float = 30.0
    max_retries: int = 3


@dataclass
class MCPToolResult:
    """Structured result of an MCP tool call. Never raises."""

    tool: str
    server: str
    success: bool
    content: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    duration_ms: float = 0.0
    tool_call_id: str = ""

    @property
    def text(self) -> str:
        """Concatenate all text content blocks for convenience."""
        chunks: list[str] = []
        for block in self.content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    chunks.append(block.get("text", ""))
                # Skip non-text blocks in the convenience accessor
        return "\n".join(chunks)


@dataclass
class MCPTool:
    """A tool discovered from an MCP server, with a back-reference to its server."""

    name: str
    description: str
    input_schema: dict[str, Any]
    server_name: str
    server_config: MCPServerConfig

    def to_mcp_tool(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
        )


# ---------------------------------------------------------------------------
# Single-server connection
# ---------------------------------------------------------------------------


class _ServerConnection:
    """A lazily-initialized, pooled MCP client session for one server."""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self._session: Optional[ClientSession] = None
        self._streams: tuple[Any, Any] | None = None
        self._init_lock: Optional[asyncio.Lock] = None
        self._last_used: float = 0.0
        self._healthy: bool = False
        self._tools: list[MCPTool] = []

    async def connect(self) -> None:
        """Initialize (or re-initialize) the MCP session."""
        if self._init_lock is None:
            self._init_lock = asyncio.Lock()
        async with self._init_lock:
            if self._session is not None and self._healthy:
                return  # already connected
            try:
                if self.config.transport == Transport.STDIO:
                    params = StdioServerParameters(
                        command=self.config.command or ["python", "-m", "mcp.server"],
                        env=self.config.env,
                    )
                    read_stream, write_stream = await stdio_client(params)
                else:  # HTTP / streamable-http
                    # MCP 2.x streamable-http uses connect_sse / http_client.
                    # We import lazily so the stdio path doesn't require it.
                    from mcp import http_client  # type: ignore

                    read_stream, write_stream = await http_client.connect(
                        self.config.url, read_timeout=self.config.timeout
                    )
                session = ClientSession(
                    read_stream=read_stream,
                    write_stream=write_stream,
                    read_timeout_seconds=self.config.timeout,
                )
                await session.initialize()
                self._session = session
                self._streams = (read_stream, write_stream)
                self._healthy = True
                self._tools = await self._discover_tools()
                log.debug("MCP pool: connected to %s (%d tools)",
                          self.config.name, len(self._tools))
            except Exception:
                self._healthy = False
                self._session = None
                self._streams = None
                log.debug("MCP pool: failed to connect to %s", self.config.name,
                          exc_info=True)
                raise

    async def _discover_tools(self) -> list[MCPTool]:
        assert self._session is not None
        result = await self._session.list_tools()
        tools: list[MCPTool] = []
        for t in result.tools:
            tools.append(
                MCPTool(
                    name=t.name,
                    description=getattr(t, "description", "") or "",
                    input_schema=t.inputSchema or {},
                    server_name=self.config.name,
                    server_config=self.config,
                )
            )
        return tools

    async def list_tools(self) -> list[MCPTool]:
        if self._session is None or not self._healthy:
            await self.connect()
        assert self._session is not None
        return list(self._tools)

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> MCPToolResult:
        call_id = str(uuid.uuid4())
        start = time.perf_counter()
        if self._session is None or not self._healthy:
            await self.connect()

        assert self._session is not None
        attempt = 0
        last_err: Optional[Exception] = None
        while attempt < self.config.max_retries:
            attempt += 1
            try:
                raw: CallToolResult = await self._session.call_tool(
                    tool_name, arguments
                )
                self._last_used = time.perf_counter()
                duration = (time.perf_counter() - start) * 1000
                # MCP CallToolResult has .content (list of content blocks) and
                # .is_error. Normalize to our structured result.
                content_blocks = []
                for block in raw.content:
                    if hasattr(block, "model_dump"):
                        content_blocks.append(block.model_dump())
                    elif isinstance(block, dict):
                        content_blocks.append(block)
                    else:
                        content_blocks.append({"type": "text", "text": str(block)})
                return MCPToolResult(
                    tool=tool_name,
                    server=self.config.name,
                    success=not getattr(raw, "is_error", False),
                    content=content_blocks,
                    error=getattr(raw, "is_error", False) and "tool returned error" or None,
                    duration_ms=duration,
                    tool_call_id=call_id,
                )
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                # On failure, mark unhealthy and try to reconnect on next attempt
                self._healthy = False
                await self._reconnect()
        # All retries exhausted
        duration = (time.perf_counter() - start) * 1000
        return MCPToolResult(
            tool=tool_name,
            server=self.config.name,
            success=False,
            content=[],
            error=f"{type(last_err).__name__}: {last_err}" if last_err else "unknown error",
            duration_ms=duration,
            tool_call_id=call_id,
        )

    async def _reconnect(self) -> None:
        """Drop the broken session and try to create a fresh one."""
        await self._close()
        try:
            await self.connect()
        except Exception:  # noqa: BLE101
            log.debug("MCP pool: reconnect failed for %s", self.config.name,
                      exc_info=True)

    async def _close(self) -> None:
        if self._session is not None:
            try:
                await self._session.close()
            except Exception:  # noqa: BLE101
                pass
        self._session = None
        self._streams = None
        self._healthy = False

    @property
    def healthy(self) -> bool:
        return self._healthy and self._session is not None


# ---------------------------------------------------------------------------
# Pool
# ---------------------------------------------------------------------------


class MCPToolClientPool:
    """Pool of MCP server connections with failover.

    Servers are tried in registration order when invoking a tool, so the first
    server that advertises the requested tool *and* returns success wins.
    """

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self._servers: list[MCPServerConfig] = []
        self._connections: dict[str, _ServerConnection] = {}
        self.default_timeout = timeout
        self.default_retries = max_retries
        self._ready = asyncio.Event()

    # -- configuration ----------------------------------------------------

    def add_server(self, config: MCPServerConfig) -> "MCPToolClientPool":
        """Register a server config (fluent builder pattern)."""
        self._servers.append(config)
        # Force re-evaluation of readiness on next list_tools / call
        return self

    def add_stdio(
        self,
        name: str,
        command: list[str],
        env: Optional[dict[str, str]] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> "MCPToolClientPool":
        return self.add_server(
            MCPServerConfig(
                name=name,
                transport=Transport.STDIO,
                command=command,
                env=env,
                timeout=timeout or self.default_timeout,
                max_retries=max_retries or self.default_retries,
            )
        )

    def add_http(
        self,
        name: str,
        url: str,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> "MCPToolClientPool":
        return self.add_server(
            MCPServerConfig(
                name=name,
                transport=Transport.HTTP,
                url=url,
                timeout=timeout or self.default_timeout,
                max_retries=max_retries or self.default_retries,
            )
        )

    @property
    def servers(self) -> list[MCPServerConfig]:
        return list(self._servers)

    # -- lifecycle --------------------------------------------------------

    async def initialize(self, parallel: bool = True) -> None:
        """Connect to all configured servers. Failures are logged, not fatal."""
        if not self._servers:
            self._ready.set()
            return

        async def _init_one(cfg: MCPServerConfig) -> None:
            conn = self._connections.setdefault(cfg.name, _ServerConnection(cfg))
            if not conn.healthy:
                await conn.connect()

        if parallel:
            await asyncio.gather(*(_init_one(c) for c in self._servers),
                                 return_exceptions=True)
        else:
            for cfg in self._servers:
                await _init_one(cfg)
        self._ready.set()

    async def close(self) -> None:
        """Close all pooled connections."""
        for conn in self._connections.values():
            await conn._close()
        self._connections.clear()

    async def __aenter__(self) -> "MCPToolClientPool":
        await self.initialize()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # -- introspection ----------------------------------------------------

    async def list_tools(self) -> list[MCPTool]:
        """List all tools from all healthy servers."""
        await self.initialize()
        all_tools: list[MCPTool] = []
        for cfg in self._servers:
            conn = self._connections.get(cfg.name)
            if conn is None or not conn.healthy:
                continue
            try:
                all_tools.extend(await conn.list_tools())
            except Exception:  # noqa: BLE101
                log.debug("list_tools failed for %s", cfg.name, exc_info=True)
        return all_tools

    async def has_tool(self, tool_name: str) -> bool:
        """True if any healthy server advertises ``tool_name``."""
        for t in await self.list_tools():
            if t.name == tool_name:
                return True
        return False

    # -- invocation (with failover) --------------------------------------

    async def call_tool(
        self, tool_name: str, arguments: Optional[dict[str, Any]] = None
    ) -> MCPToolResult:
        """Call a tool, failing over across servers that advertise it.

        Tries each healthy server that lists the tool. Returns the first
        successful result. If all fail, returns a failure result describing
        the last error.
        """
        await self.initialize()
        arguments = arguments or {}

        # Find candidate servers (preserve registration order).
        candidates: list[_ServerConnection] = []
        for cfg in self._servers:
            conn = self._connections.get(cfg.name)
            if conn is None or not conn.healthy:
                continue
            if any(t.name == tool_name for t in conn._tools):
                candidates.append(conn)

        if not candidates:
            return MCPToolResult(
                tool=tool_name,
                server="",
                success=False,
                error=f"Tool '{tool_name}' is not available on any healthy server",
            )

        last_result: Optional[MCPToolResult] = None
        for conn in candidates:
            result = await conn.call_tool(tool_name, arguments)
            if result.success:
                return result
            last_result = result

        # All candidates failed — return the last failure (failover exhausted).
        if last_result is not None:
            return last_result
        return MCPToolResult(
            tool=tool_name,
            server="",
            success=False,
            error=f"Tool '{tool_name}' failed on all servers",
        )

    # -- bulk -------------------------------------------------------------

    async def call_many(
        self, calls: list[tuple[str, dict[str, Any]]]
    ) -> list[MCPToolResult]:
        """Call multiple tools concurrently."""
        return await asyncio.gather(*(self.call_tool(n, a) for n, a in calls))
