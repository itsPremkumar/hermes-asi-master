#!/usr/bin/env python3
"""
coder.py — DeerFlow 2.0 Code Synthesis & Tool Builder Subagent
Implements production code, handles edge cases, and provides modular outputs.
"""

from harness.state import AgentState
from harness.router import FreeModelRouter

class DeerFlowCoder:
    def __init__(self, router: FreeModelRouter):
        self.router = router

    def code(self, state: AgentState) -> AgentState:
        research = state.get_artifact("research_findings", {})
        sys_prompt = "You are the DeerFlow 2.0 Lead Coder. Synthesize clean, robust Python code satisfying all constraints."
        prompt = f"Goal: {state.goal}\nResearch Context: {research.get('summary', '')}\nWrite complete Python implementation:"

        resp = self.router.route(prompt, system_prompt=sys_prompt)
        raw_code = resp.content

        # Extract code block if wrapped in markdown
        if "```python" in raw_code:
            code = raw_code.split("```python")[1].split("```")[0].strip()
        elif "```" in raw_code:
            code = raw_code.split("```")[1].split("```")[0].strip()
        else:
            code = raw_code

        state.set_artifact("synthesized_code", code)
        state.log_step("coder", "synthesize_code", {"code_length": len(code)})
        return state
