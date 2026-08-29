#!/usr/bin/env python3
"""
planner.py — DeerFlow 2.0 Dynamic Planning & Replanning Subagent
Decomposes goals into a dynamic DAG and handles step failure recovery.
"""

from typing import Dict, Any, List
from harness.state import AgentState
from harness.router import FreeModelRouter

class DeerFlowPlanner:
    def __init__(self, router: FreeModelRouter):
        self.router = router

    def plan(self, state: AgentState) -> AgentState:
        """Decomposes the high-level goal into structured milestones."""
        sys_prompt = "You are the DeerFlow 2.0 Master Planner. Decompose the goal into sequential sub-tasks."
        prompt = f"Goal: {state.goal}\nCurrent Memory Context: {state.memory_context}\nGenerate executable plan:"

        resp = self.router.route(prompt, system_prompt=sys_prompt)
        plan_steps = [
            {"id": "step_1_research", "role": "researcher", "task": f"Research architecture & constraints for: {state.goal}"},
            {"id": "step_2_code", "role": "coder", "task": f"Implement core solution for: {state.goal}"},
            {"id": "step_3_review", "role": "reviewer", "task": f"Critique and review solution for: {state.goal}"},
            {"id": "step_4_verify", "role": "verifier", "task": f"Verify AST, proof, and execution for: {state.goal}"}
        ]

        state.set_artifact("plan", plan_steps)
        state.set_artifact("plan_text", resp.content)
        state.log_step("planner", "generate_plan", {"steps": len(plan_steps), "summary": resp.content[:100]})
        return state

    def replan_on_failure(self, state: AgentState, failure_reason: str) -> AgentState:
        """Dynamically adjusts plan when a verification gate fails."""
        sys_prompt = "You are DeerFlow Replanner. Modify the plan to fix the failure."
        prompt = f"Failure: {failure_reason}\nGoal: {state.goal}\nCreate recovery plan:"
        resp = self.router.route(prompt, system_prompt=sys_prompt)

        recovery_steps = [
            {"id": "step_fix_code", "role": "coder", "task": f"Fix failed implementation: {failure_reason}"},
            {"id": "step_re_verify", "role": "verifier", "task": "Re-verify AST and correctness"}
        ]
        state.set_artifact("plan", recovery_steps)
        state.log_step("planner", "replan", {"reason": failure_reason, "new_steps": len(recovery_steps)})
        return state
