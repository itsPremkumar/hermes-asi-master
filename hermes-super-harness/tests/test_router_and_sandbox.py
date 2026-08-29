#!/usr/bin/env python3
"""
test_router_and_sandbox.py — Validates Free Model Router, Local Sandbox, and GEPA
"""

import sys
import pathlib
import pytest

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from harness.router import FreeModelRouter
from harness.sandbox import ExecutionSandbox
from plugins.gepa_evolution.plugin import GEPAEvolutionPlugin
from harness.plugin_interface import PluginManifest

def test_zero_cost_model_router():
    router = FreeModelRouter(zero_cost_only=True)
    resp = router.route("Plan an autonomous trading agent")
    assert resp is not None
    assert resp.cost_usd == 0.0
    assert len(resp.content) > 0

def test_sandbox_python_execution():
    sandbox = ExecutionSandbox()
    res = sandbox.run_python_code("print('HERMES_SUPER_HARNESS_OK')")
    assert res.exit_code == 0
    assert "HERMES_SUPER_HARNESS_OK" in res.stdout
    assert res.timed_out is False

def test_gepa_evolution_plugin():
    manifest = PluginManifest(
        name="gepa_evolution",
        version="1.0.0",
        description="GEPA test"
    )
    plugin = GEPAEvolutionPlugin(manifest)
    population = plugin.evolve_prompt("Execute AST check before output", iterations=1)
    assert len(population) == 4
    assert population[0]["score"] >= 0.85
