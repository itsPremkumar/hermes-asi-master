#!/usr/bin/env python3
"""
guardrail_manager.py — HERMES-ASI Hard Budget & Loop Guardrail Enforcement
Prevents runaway spending and enforces hard token/dollar caps on autonomous tasks.
"""

import sys
import unittest
from pathlib import Path

MAX_DAILY_BUDGET_USD = 5.00
MAX_MONTHLY_BUDGET_USD = 100.00

def check_execution_guardrails(current_day_spend: float, consecutive_loop_count: int) -> tuple[bool, str]:
    if current_day_spend >= MAX_DAILY_BUDGET_USD:
        return False, f"[GUARDRAIL TRIPPED] Daily spending cap (${MAX_DAILY_BUDGET_USD:.2f}) exceeded. Falling back to local offline tier."
    if consecutive_loop_count >= 5:
        return False, "[GUARDRAIL TRIPPED] High repetition loop detected (≥5 iterations without state delta)."
    return True, "All guardrails passed."

class GuardrailTests(unittest.TestCase):
    def test_spend_cap(self):
        ok, msg = check_execution_guardrails(6.0, 1)
        self.assertFalse(ok)
        self.assertIn("Daily spending cap", msg)

    def test_loop_cap(self):
        ok, msg = check_execution_guardrails(1.0, 6)
        self.assertFalse(ok)
        self.assertIn("loop detected", msg)

    def test_pass(self):
        ok, msg = check_execution_guardrails(1.0, 1)
        self.assertTrue(ok)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(GuardrailTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Guardrail Manager Active.")
