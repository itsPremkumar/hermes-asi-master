#!/usr/bin/env python3
"""
self_tracker.py — HERMES-ASI-MASTER Empirical Self-Model Tracker
Records task performance outcomes, computes Brier calibration curves, tracks failure modes,
and updates runtime self-model capabilities.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone

try:
    from state_engine import load_state, save_state
except ImportError:
    from .state_engine import load_state, save_state

def record_task_outcome(domain: str, predicted_confidence: float, success: bool, failure_mode: str = None) -> dict:
    data = load_state("self_model")
    domains = data.setdefault("domains", {})
    
    d = domains.setdefault(domain, {
        "confidence": 0.50,
        "empirical_success": 0.50,
        "sample_count": 0,
        "recent_delta": 0.0,
        "known_failure_modes": []
    })
    
    n = d["sample_count"]
    old_success = d["empirical_success"]
    outcome_val = 1.0 if success else 0.0
    new_success = round(((old_success * n) + outcome_val) / (n + 1), 4)
    
    d["sample_count"] = n + 1
    d["recent_delta"] = round(new_success - old_success, 4)
    d["empirical_success"] = new_success
    d["confidence"] = round(predicted_confidence, 4)
    
    if not success and failure_mode and failure_mode not in d["known_failure_modes"]:
        d["known_failure_modes"].append(failure_mode)
        
    # Calculate Brier score entry: (predicted - actual)^2
    brier_entry = (predicted_confidence - outcome_val) ** 2
    history = data.setdefault("calibration_history", [])
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "predicted": predicted_confidence,
        "actual": outcome_val,
        "brier": round(brier_entry, 4)
    })
    
    if len(history) > 50:
        history.pop(0)
        
    avg_brier = round(sum(h["brier"] for h in history) / len(history), 4)
    data["overall_calibration_brier"] = avg_brier
    
    save_state("self_model", data)
    return d

def get_calibration_summary() -> dict:
    data = load_state("self_model")
    return {
        "overall_brier": data.get("overall_calibration_brier", 0.0),
        "domains": {k: v["empirical_success"] for k, v in data.get("domains", {}).items()},
        "total_samples": sum(v["sample_count"] for v in data.get("domains", {}).values())
    }

class SelfTrackerTests(unittest.TestCase):
    def test_record_outcome(self):
        d = record_task_outcome("test_domain", 0.90, True)
        self.assertIn("empirical_success", d)
        self.assertGreater(d["sample_count"], 0)

    def test_calibration_summary(self):
        summary = get_calibration_summary()
        self.assertIn("overall_brier", summary)
        self.assertIn("domains", summary)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(SelfTrackerTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print(get_calibration_summary())
