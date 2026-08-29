"""Plugin Registry — hot-loadable, sandboxed plugin management."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PluginState(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADING = "unloading"
    ERROR = "error"


@dataclass
class Capability:
    name: str
    description: str
    permissions: list[str] = field(default_factory=list)


@dataclass
class PluginManifest:
    name: str
    version: str
    description: str
    author: str
    capabilities: list[Capability] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    entry_point: str = "__init__.py"
    state: PluginState = PluginState.UNLOADED
    health_check_interval: float = 30.0
    max_restart_attempts: int = 3
    sandbox_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    healthy: bool
    message: str
    last_check: float
    uptime_seconds: float
    memory_usage_mb: float
    error_count: int = 0


class PluginRegistry:
    """Manages plugin lifecycle: load, unload, hot-reload, health monitoring."""

    def __init__(self, plugin_dir: str | Path):
        self.plugin_dir = Path(plugin_dir)
        self._plugins: dict[str, PluginManifest] = {}
        self._health: dict[str, HealthStatus] = {}
        self._load_order: list[str] = []

    def discover(self) -> list[PluginManifest]:
        """Scan plugin directory and discover available plugins."""
        manifests = []
        if not self.plugin_dir.exists():
            return manifests
        for plugin_path in self.plugin_dir.iterdir():
            if not plugin_path.is_dir():
                continue
            manifest_file = plugin_path / "plugin.json"
            if manifest_file.exists():
                try:
                    data = json.loads(manifest_file.read_text())
                    manifest = PluginManifest(
                        name=data.get("name", plugin_path.name),
                        version=data.get("version", "0.1.0"),
                        description=data.get("description", ""),
                        author=data.get("author", "unknown"),
                        entry_point=data.get("entry_point", "__init__.py"),
                    )
                    manifests.append(manifest)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to load manifest from {manifest_file}: {e}")
        return manifests

    async def load(self, name: str) -> bool:
        """Load a plugin by name."""
        manifest = self._plugins.get(name)
        if not manifest:
            logger.error(f"Plugin '{name}' not found")
            return False
        if manifest.state == PluginState.LOADED:
            logger.warning(f"Plugin '{name}' already loaded")
            return True

        manifest.state = PluginState.LOADING
        try:
            # Resolve dependencies first
            for dep in manifest.dependencies:
                if dep not in self._plugins or self._plugins[dep].state != PluginState.LOADED:
                    await self.load(dep)
            # In production: import module, call load()
            await asyncio.sleep(0.05)
            manifest.state = PluginState.LOADED
            self._load_order.append(name)
            logger.info(f"Plugin '{name}' loaded successfully")
            return True
        except Exception as e:
            manifest.state = PluginState.ERROR
            logger.error(f"Failed to load plugin '{name}': {e}")
            return False

    async def unload(self, name: str) -> bool:
        """Unload a plugin by name."""
        manifest = self._plugins.get(name)
        if not manifest or manifest.state != PluginState.LOADED:
            return False
        manifest.state = PluginState.UNLOADING
        try:
            # In production: call unload(), release resources
            await asyncio.sleep(0.05)
            manifest.state = PluginState.UNLOADED
            if name in self._load_order:
                self._load_order.remove(name)
            logger.info(f"Plugin '{name}' unloaded")
            return True
        except Exception as e:
            manifest.state = PluginState.ERROR
            logger.error(f"Failed to unload plugin '{name}': {e}")
            return False

    async def hot_reload(self, name: str) -> bool:
        """Hot-reload a plugin without restarting the master."""
        logger.info(f"Hot-reloading plugin '{name}'")
        await self.unload(name)
        return await self.load(name)

    async def health_check(self, name: str) -> HealthStatus:
        """Check health of a loaded plugin."""
        manifest = self._plugins.get(name)
        if not manifest or manifest.state != PluginState.LOADED:
            return HealthStatus(
                healthy=False,
                message=f"Plugin '{name}' not loaded",
                last_check=time.time(),
                uptime_seconds=0.0,
                memory_usage_mb=0.0,
            )
        # In production: call plugin's health() method
        status = HealthStatus(
            healthy=True,
            message="OK",
            last_check=time.time(),
            uptime_seconds=0.0,
            memory_usage_mb=0.0,
        )
        self._health[name] = status
        return status

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all registered plugins with their state."""
        return [
            {
                "name": m.name,
                "version": m.version,
                "state": m.state.value,
                "capabilities": [c.name for c in m.capabilities],
            }
            for m in self._plugins.values()
        ]
