#!/usr/bin/env python3
"""
trajectory_rl_exporter.py — HERMES-ASI-MASTER Reinforcement Learning Trajectory Exporter
Exports multi-step execution traces into ShareGPT & DPO fine-tuning datasets for Atropos RL.
"""

import sys
import json
import unittest
from pathlib import Path

def convert_trace_to_sharegpt(system_prompt: str, user_prompt: str, tool_calls: list[dict], final_response: str) -> dict:
    conversations = [
        {"from": "system", "value": system_prompt},
        {"from": "human", "value": user_prompt}
    ]
    for tc in tool_calls:
        conversations.append({"from": "gpt", "value": f"<tool_call>{json.dumps(tc)}</tool_call>"})
        conversations.append({"from": "tool", "value": tc.get("result", "success")})
    conversations.append({"from": "gpt", "value": final_response})
    return {"conversations": conversations}

class RlExporterTests(unittest.TestCase):
    def test_export(self):
        sg = convert_trace_to_sharegpt(
            "You are Hermes ASI",
            "Search for AGI",
            [{"name": "web_search", "args": {"q": "AGI"}, "result": "Found 10 results"}],
            "Here is the verified AGI summary."
        )
        self.assertEqual(len(sg["conversations"]), 5)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(RlExporterTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Trajectory RL Exporter Active. Use --test for self-verification.")
