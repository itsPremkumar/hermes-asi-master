"""Async Configuration — non-blocking config loading and hot-reload."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ConfigChangeEvent:
    key: str
    old_value: Any
    new_value: Any
    timestamp: float


class AsyncConfig:
    """Asynchronous configuration with hot-reload and change callbacks."""

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._callbacks: list[Callable[[ConfigChangeEvent], None]] = []
        self._last_modified: float = 0.0
        self._watcher_task: asyncio.Task | None = None

    async def load(self) -> dict[str, Any]:
        """Load config from disk asynchronously."""
        async with self._lock:
            try:
                loop = asyncio.get_event_loop()
                content = await loop.run_in_executor(None, self.config_path.read_text)
                self._config = yaml.safe_load(content) or {}
                self._last_modified = self.config_path.stat().st_mtime
                logger.info(f"Config loaded from {self.config_path}")
                return self._config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return {}

    async def save(self) -> bool:
        """Save config to disk asynchronously."""
        async with self._lock:
            try:
                loop = asyncio.get_event_loop()
                content = yaml.dump(self._config, default_flow_style=False)
                await loop.run_in_executor(None, self.config_path.write_text, content)
                self._last_modified = self.config_path.stat().st_mtime
                logger.info(f"Config saved to {self.config_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save config: {e}")
                return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by key (dot-notation supported)."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    async def set(self, key: str, value: Any) -> None:
        """Set a config value and notify callbacks."""
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        old_value = config.get(keys[-1])
        config[keys[-1]] = value
        event = ConfigChangeEvent(
            key=key,
            old_value=old_value,
            new_value=value,
            timestamp=time.time(),
        )
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Config callback error: {e}")

    def on_change(self, callback: Callable[[ConfigChangeEvent], None]) -> None:
        """Register a callback for config changes."""
        self._callbacks.append(callback)

    async def start_watcher(self, interval: float = 5.0) -> None:
        """Start watching config file for changes."""
        if self._watcher_task:
            return
        self._watcher_task = asyncio.create_task(self._watch_loop(interval))
        logger.info(f"Config watcher started (interval={interval}s)")

    async def stop_watcher(self) -> None:
        """Stop the config watcher."""
        if self._watcher_task:
            self._watcher_task.cancel()
            self._watcher_task = None

    async def _watch_loop(self, interval: float) -> None:
        """Periodically check for config file changes."""
        while True:
            try:
                await asyncio.sleep(interval)
                if not self.config_path.exists():
                    continue
                mtime = self.config_path.stat().st_mtime
                if mtime > self._last_modified:
                    logger.info("Config file changed, reloading")
                    await self.load()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Config watcher error: {e}")
