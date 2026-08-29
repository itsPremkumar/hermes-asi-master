#!/usr/bin/env python3
"""
graph.py — DeerFlow 2.0 StateGraph Execution Workflow
Implements the full Plan -> Research -> Code -> Review -> Verify -> (Replan if needed) -> Complete StateGraph.
"""

from typing import Dict, Any, Optional
from harness.state import AgentState, StateGraph
from harness.router import FreeModelRouter
from harness.sandbox import ExecutionSandbox
from plugins.deerflow_v2.agents.planner import DeerFlowPlanner
from plugins.deerflow_v2.agents.researcher import DeerFlowResearcher
from plugins.deerflow_v2.agents.coder import DeerFlowCoder
from plugins.deerflow_v2.agents.reviewer import DeerFlowReviewer
from plugins.deerflow_v2.agents.verifier import DeerFlowVerifier
from plugins.deerflow_v2.memory.memory_stream import DeerFlowMemoryStream

class DeerFlowWorkflowGraph:
    def __init__(self, router: FreeModelRouter, sandbox: ExecutionSandbox):
        self.router = router
        self.sandbox = sandbox
        self.memory = DeerFlowMemoryStream()
        
        self.planner = DeerFlowPlanner(router)
        self.researcher = DeerFlowResearcher(router)
        self.coder = DeerFlowCoder(router)
        self.reviewer = DeerFlowReviewer(router)
        self.verifier = DeerFlowVerifier(sandbox)

    def build_graph(self) -> StateGraph:
        """Constructs the DeerFlow 2.0 Plan-Execute StateGraph."""
        sg = StateGraph()

        # 1. Planner Node
        def plan_node(state: AgentState) -> AgentState:
            # Extract memory context first
            context = self.memory.get_relevant_context(state.goal)
            state.memory_context = context
            st = self.planner.plan(state)
            self.memory.extract_facts(st.get_artifact("plan_text", ""), "planner")
            return st

        # 2. Researcher Node
        def research_node(state: AgentState) -> AgentState:
            st = self.researcher.research(state)
            findings = st.get_artifact("research_findings", {})
            self.memory.extract_facts(findings.get("summary", ""), "researcher")
            return st

        # 3. Coder Node
        def code_node(state: AgentState) -> AgentState:
            return self.coder.code(state)

        # 4. Reviewer Node
        def review_node(state: AgentState) -> AgentState:
            return self.reviewer.review(state)

        # 5. Verifier Node
        def verify_node(state: AgentState) -> AgentState:
            return self.verifier.verify(state)

        # 6. Replan Node
        def replan_node(state: AgentState) -> AgentState:
            v_res = state.get_artifact("verification_result", {})
            err = "; ".join(v_res.get("errors", ["Verification failed"]))
            return self.planner.replan_on_failure(state, err)

        # Register nodes
        sg.add_node("plan", plan_node)
        sg.add_node("research", research_node)
        sg.add_node("code", code_node)
        sg.add_node("review", review_node)
        sg.add_node("verify", verify_node)
        sg.add_node("replan", replan_node)

        # Set entry point
        sg.set_entry_point("plan")

        # Standard pipeline edges
        sg.add_edge("plan", "research")
        sg.add_edge("research", "code")
        sg.add_edge("code", "review")
        sg.add_edge("review", "verify")

        # Conditional Edge after verify
        def route_after_verify(state: AgentState) -> str:
            v_res = state.get_artifact("verification_result", {})
            replan_count = state.variables.get("replan_count", 0)
            
            if v_res.get("passed", False):
                return "END"
            elif replan_count < 2:
                state.variables["replan_count"] = replan_count + 1
                return "replan"
            else:
                return "END"

        sg.add_conditional_edges("verify", route_after_verify)
        sg.add_edge("replan", "code")

        return sg
