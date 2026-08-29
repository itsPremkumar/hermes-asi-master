#!/usr/bin/env python3
"""
test_deerflow_v2.py — Validates DeerFlow 2.0 SuperAgent Workflow, Subagents & StateGraph
"""

import sys
import pathlib
import pytest

ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from harness.engine import SuperHarnessEngine
from harness.state import AgentState, StateGraph
from harness.router import FreeModelRouter
from harness.sandbox import ExecutionSandbox
from plugins.deerflow_v2.plugin import DeerFlowV2Plugin
from plugins.deerflow_v2.graph import DeerFlowWorkflowGraph
from plugins.deerflow_v2.memory.memory_stream import DeerFlowMemoryStream

def test_deerflow_memory_stream_fact_extraction():
    mem = DeerFlowMemoryStream()
    sample_text = """
    1. The system must maintain sub-millisecond lock-free token bucket throughput.
    2. Zero paid API keys are permitted in free-first mode.
    - [Rule] AST syntax must be verified prior to emitting final code.
    """
    facts = mem.extract_facts(sample_text, "planner")
    assert len(facts) >= 2
    
    ctx = mem.get_relevant_context("lock-free token bucket")
    assert len(ctx) >= 1
    assert "token bucket" in ctx[0].lower()

def test_deerflow_stategraph_execution():
    router = FreeModelRouter()
    sandbox = ExecutionSandbox()
    workflow = DeerFlowWorkflowGraph(router, sandbox)
    sg = workflow.build_graph()

    init_state = AgentState(goal="Implement a thread-safe sliding window rate limiter")
    final_state = sg.execute(init_state)

    assert final_state.status == "completed"
    assert len(final_state.history) >= 5
    
    # Verify artifacts
    assert "plan" in final_state.artifacts
    assert "research_findings" in final_state.artifacts
    assert "synthesized_code" in final_state.artifacts
    assert "code_review" in final_state.artifacts
    assert "verification_result" in final_state.artifacts

def test_deerflow_plugin_end_to_end():
    engine = SuperHarnessEngine(plugins_dir=str(ROOT_DIR / "plugins"))
    engine.auto_discover_plugins()

    plugin = engine.plugins.get("deerflow_v2")
    assert plugin is not None
    assert isinstance(plugin, DeerFlowV2Plugin)

    state = plugin.run_flow("Create an atomic Merkle tree leaf hasher")
    assert state.status == "completed"
    assert len(state.history) >= 5
    v_res = state.get_artifact("verification_result", {})
    assert v_res.get("is_valid_ast", False) is True
