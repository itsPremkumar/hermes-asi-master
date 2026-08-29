#!/usr/bin/env python3
"""
engine.py — Core Super-Harness Engine
Manages dynamic plugin discovery, lifecycle hooks, tool registration, and multi-agent coordination.
"""

import os
import json
import importlib.util
import pathlib
from typing import Dict, Any, List, Optional
from harness.plugin_interface import BasePlugin, PluginManifest
from harness.router import FreeModelRouter
from harness.state import AgentState, StateGraph
from harness.sandbox import ExecutionSandbox

class SuperHarnessEngine:
    def __init__(self, plugins_dir: Optional[str] = None):
        self.plugins_dir = pathlib.Path(plugins_dir or "plugins").resolve()
        self.plugins: Dict[str, BasePlugin] = {}
        self.router = FreeModelRouter()
        self.sandbox = ExecutionSandbox()
        self.context: Dict[str, Any] = {
            "engine": self,
            "router": self.router,
            "sandbox": self.sandbox
        }

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Registers a plugin and fires on_load."""
        name = plugin.manifest.name
        if name in self.plugins:
            return False
        success = plugin.on_load(self.context)
        if success:
            self.plugins[name] = plugin
            return True
        return False

    def unregister_plugin(self, name: str) -> bool:
        if name in self.plugins:
            self.plugins[name].on_unload()
            del self.plugins[name]
            return True
        return False

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": p.manifest.name,
                "version": p.manifest.version,
                "description": p.manifest.description,
                "permission": p.manifest.permission_ring.value,
                "capabilities": p.manifest.capabilities,
                "active": p.is_active
            }
            for p in self.plugins.values()
        ]

    def auto_discover_plugins(self):
        """Scans plugins_dir for directories with manifest.json and plugin.py."""
        if not self.plugins_dir.exists():
            return

        for p_dir in self.plugins_dir.iterdir():
            if p_dir.is_dir():
                manifest_file = p_dir / "manifest.json"
                plugin_file = p_dir / "plugin.py"
                if manifest_file.exists() and plugin_file.exists():
                    try:
                        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
                        manifest = PluginManifest(**manifest_data)
                        
                        # Dynamically import plugin module cleanly
                        mod = importlib.import_module(f"plugins.{p_dir.name}.plugin")
                        
                        # Find plugin class
                        for attr_name in dir(mod):
                            attr = getattr(mod, attr_name)
                            if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                                plugin_instance = attr(manifest)
                                self.register_plugin(plugin_instance)
                                break
                    except Exception as e:
                        print(f"[!] Warning: Failed to load plugin from {p_dir.name}: {e}")

    # --- Lifecycle Interceptors ---
    def trigger_on_goal_start(self, goal: Dict[str, Any]):
        for p in self.plugins.values():
            if p.is_active:
                p.on_goal_start(goal)

    def trigger_pre_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        curr_args = args
        for p in self.plugins.values():
            if p.is_active:
                curr_args = p.pre_tool_call(tool_name, curr_args)
        return curr_args

    def trigger_post_tool_call(self, tool_name: str, result: Any) -> Any:
        curr_result = result
        for p in self.plugins.values():
            if p.is_active:
                curr_result = p.post_tool_call(tool_name, curr_result)
        return curr_result

    def trigger_on_step(self, agent_role: str, step_data: Dict[str, Any]):
        for p in self.plugins.values():
            if p.is_active:
                p.on_step(agent_role, step_data)

    def trigger_on_goal_complete(self, goal: Dict[str, Any], verdict: Dict[str, Any]):
        for p in self.plugins.values():
            if p.is_active:
                p.on_goal_complete(goal, verdict)
