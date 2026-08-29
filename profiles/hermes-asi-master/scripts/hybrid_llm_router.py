#!/usr/bin/env python3
"""
hybrid_llm_router.py — HERMES-ASI-MASTER Speculative Hybrid LLM Router
Routes trivial tasks to fast local models (Ollama/vLLM) and strategic tasks to frontier reasoning cloud models.
"""

import sys
import unittest
from pathlib import Path

def route_request(task_prompt: str, risk_tier: str = "R1", reasoning_depth: str = "standard") -> dict:
    risk = risk_tier.upper()
    is_complex = len(task_prompt) > 500 or any(k in task_prompt.lower() for k in ["synthesize", "architect", "prove", "formal", "audit", "security"])
    
    if risk in ["R0", "R1"] and not is_complex and reasoning_depth == "standard":
        return {
            "tier": "LOCAL_FAST",
            "provider": "ollama",
            "model": "hermes-3-llama-3.1-8b",
            "cost_per_m_tokens": 0.0,
            "estimated_latency_ms": 150
        }
    else:
        return {
            "tier": "FRONTIER_CLOUD",
            "provider": "anthropic",
            "model": "claude-3-7-sonnet-20250219",
            "cost_per_m_tokens": 3.0,
            "estimated_latency_ms": 1200
        }

class HybridRouterTests(unittest.TestCase):
    def test_routing_local(self):
        res = route_request("Format this JSON string", risk_tier="R1")
        self.assertEqual(res["tier"], "LOCAL_FAST")

    def test_routing_frontier(self):
        res = route_request("Synthesize multi-agent security audit and formal proof", risk_tier="R4")
        self.assertEqual(res["tier"], "FRONTIER_CLOUD")

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(HybridRouterTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Hybrid LLM Router Active. Use --test for self-verification.")
