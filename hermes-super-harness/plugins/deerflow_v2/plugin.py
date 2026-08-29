#!/usr/bin/env python3
"""
plugin.py — DeerFlow 2.0 Plugin for Hermes Super-Harness
Exposes DeerFlow 2.0 SuperAgent workflow, dynamic subagents, and memory stream to the harness engine.
"""

from typing import Dict, Any, Optional
from harness.plugin_interface import BasePlugin, PluginManifest
from harness.state import AgentState
from plugins.deerflow_v2.graph import DeerFlowWorkflowGraph

class DeerFlowV2Plugin(BasePlugin):
    def __init__(self, manifest: PluginManifest):
        super().__init__(manifest)
        self.workflow_graph: Optional[DeerFlowWorkflowGraph] = None
        self.engine_context: Dict[str, Any] = {}

    def on_load(self, harness_context: Dict[str, Any]) -> bool:
        self.engine_context = harness_context
        router = harness_context.get("router")
        sandbox = harness_context.get("sandbox")
        self.workflow_graph = DeerFlowWorkflowGraph(router, sandbox)
        self.is_active = True
        return True

    def run_flow(self, goal: str, initial_variables: Optional[Dict[str, Any]] = None) -> AgentState:
        """Runs the complete DeerFlow 2.0 SuperAgent workflow on a goal."""
        if not self.workflow_graph:
            raise RuntimeError("DeerFlowV2Plugin is not loaded.")

        sg = self.workflow_graph.build_graph()
        init_state = AgentState(
            goal=goal,
            variables=initial_variables or {}
        )
        final_state = sg.execute(init_state)
        return final_state
