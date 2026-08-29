#!/usr/bin/env python3
"""
test_plugin_framework.py — Validates Plugin Lifecycle, Manifests, and Discovery
"""

import sys
import pathlib
import pytest

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from harness.plugin_interface import BasePlugin, PluginManifest, PermissionRing, ToolContract
from harness.engine import SuperHarnessEngine

def test_manifest_validation():
    manifest = PluginManifest(
        name="test_plugin",
        version="1.0.0",
        description="A test plugin",
        permission_ring=PermissionRing.R1_SANDBOX_LOCAL,
        capabilities=["test_cap_1", "test_cap_2"],
        tools=[
            ToolContract(name="test_tool", description="A test tool")
        ]
    )
    assert manifest.name == "test_plugin"
    assert manifest.permission_ring == PermissionRing.R1_SANDBOX_LOCAL
    assert len(manifest.tools) == 1

def test_plugin_registration_and_lifecycle():
    engine = SuperHarnessEngine()
    manifest = PluginManifest(
        name="dummy_plugin",
        version="1.0.0",
        description="Dummy test plugin"
    )
    plugin = BasePlugin(manifest)
    
    # Register
    ok = engine.register_plugin(plugin)
    assert ok is True
    assert plugin.is_active is True
    assert len(engine.list_plugins()) == 1

    # Unregister
    ok_unreg = engine.unregister_plugin("dummy_plugin")
    assert ok_unreg is True
    assert plugin.is_active is False
    assert len(engine.list_plugins()) == 0

def test_auto_discovery_of_plugins():
    engine = SuperHarnessEngine(plugins_dir=str(ROOT_DIR / "plugins"))
    engine.auto_discover_plugins()
    
    plugin_names = [p["name"] for p in engine.list_plugins()]
    assert "deerflow_v2" in plugin_names
    assert "hermes_asi_core" in plugin_names
    assert "gepa_evolution" in plugin_names
