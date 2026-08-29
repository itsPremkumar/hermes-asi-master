#!/usr/bin/env python3
"""
curriculum_picker.py — HERMES-ASI-MASTER SIMA 2-Style Curriculum Engine
Evaluates task complexity, novelty, learning value, and schedules developmental tasks.
"""

import sys
import unittest
from pathlib import Path

CURRICULUM_LEVELS = [
    "KNOWN",
    "SLIGHTLY_HARDER",
    "UNKNOWN",
    "NOVEL",
    "ADVERSARIAL",
    "TRANSFER",
    "OPEN_ENDED"
]

def score_learning_value(difficulty: float, novelty: float, transfer_potential: float) -> float:
    # Value of Information & Learning metric
    score = (difficulty * 0.3) + (novelty * 0.4) + (transfer_potential * 0.3)
    return round(min(1.0, max(0.0, score)), 4)

def select_next_curriculum_task(current_domain_success: float) -> dict:
    if current_domain_success > 0.90:
        target_level = "NOVEL"
        diff_target = 0.85
    elif current_domain_success > 0.75:
        target_level = "SLIGHTLY_HARDER"
        diff_target = 0.70
    else:
        target_level = "KNOWN"
        diff_target = 0.50
        
    return {
        "target_level": target_level,
        "difficulty_target": diff_target,
        "curriculum_index": CURRICULUM_LEVELS.index(target_level),
        "learning_value": score_learning_value(diff_target, 0.8, 0.75)
    }

class CurriculumTests(unittest.TestCase):
    def test_score_learning(self):
        val = score_learning_value(0.7, 0.8, 0.9)
        self.assertGreater(val, 0.7)

    def test_task_selection(self):
        task = select_next_curriculum_task(0.95)
        self.assertEqual(task["target_level"], "NOVEL")

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(CurriculumTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print(select_next_curriculum_task(0.92))
