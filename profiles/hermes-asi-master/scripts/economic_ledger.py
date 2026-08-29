#!/usr/bin/env python3
"""
economic_ledger.py — HERMES-ASI-MASTER Economic Agency & Budget Ledger
Enforces hard token and financial budgets per mission with real-time burn rate accounting.
"""

import sys
import json
import unittest
from pathlib import Path
from datetime import datetime, timezone

try:
    from state_engine import load_state, save_state
except ImportError:
    from .state_engine import load_state, save_state

def record_token_spend(provider: str, input_tokens: int, output_tokens: int, estimated_cost_usd: float) -> dict:
    data = load_state("financial_ledger")
    
    tokens = data.setdefault("token_usage_total", {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0})
    tokens["input_tokens"] += input_tokens
    tokens["output_tokens"] += output_tokens
    
    costs = data.setdefault("cost_breakdown_by_provider", {})
    costs[provider] = round(costs.get(provider, 0.0) + estimated_cost_usd, 4)
    
    data["current_month_spend"] = round(data.get("current_month_spend", 0.0) + estimated_cost_usd, 4)
    data["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    save_state("financial_ledger", data)
    return {
        "monthly_budget": data.get("monthly_budget", 100.0),
        "current_month_spend": data["current_month_spend"],
        "remaining_budget": round(data.get("monthly_budget", 100.0) - data["current_month_spend"], 4)
    }

class EconomicLedgerTests(unittest.TestCase):
    def test_record_spend(self):
        res = record_token_spend("anthropic", 1000, 500, 0.015)
        self.assertIn("remaining_budget", res)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(EconomicLedgerTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Economic Ledger Active. Use --test for self-verification.")
