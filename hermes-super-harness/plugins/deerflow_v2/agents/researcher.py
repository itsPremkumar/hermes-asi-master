#!/usr/bin/env python3
"""
researcher.py — DeerFlow 2.0 Research & Knowledge Subagent
Performs context gathering, evidence synthesis, and constraint mapping.
"""

from harness.state import AgentState
from harness.router import FreeModelRouter

class DeerFlowResearcher:
    def __init__(self, router: FreeModelRouter):
        self.router = router

    def research(self, state: AgentState) -> AgentState:
        sys_prompt = "You are the DeerFlow 2.0 Deep Researcher. Gather facts, trade-offs, and technical requirements."
        prompt = f"Goal: {state.goal}\nSynthesize requirements and key architectural facts:"

        resp = self.router.route(prompt, system_prompt=sys_prompt)
        findings = {
            "summary": resp.content,
            "constraints": ["Zero-cost local execution", "ACID state persistence", "AST safety invariant"],
            "key_technologies": ["Hermes Agent", "DeerFlow 2.0 StateGraph", "LangGraph Pattern"]
        }

        state.set_artifact("research_findings", findings)
        state.log_step("researcher", "gather_context", findings)
        return state
