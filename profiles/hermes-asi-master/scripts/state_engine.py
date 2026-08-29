#!/usr/bin/env python3
"""
state_engine.py — HERMES-ASI-MASTER State Engine
Manages atomic load, validate, backup, and save operations for all live JSON state files.
"""

import sys
import json
import shutil
import unittest
from pathlib import Path
from datetime import datetime, timezone

STATE_DIR = Path(__file__).resolve().parent.parent / "state"

VALID_STATES = ["world_state", "self_model", "belief_graph", "mission_graph", "financial_ledger", "evolution_benchmarks"]

def get_state_path(state_name: str) -> Path:
    name = state_name.replace(".json", "")
    if name not in VALID_STATES:
        raise ValueError(f"Unknown state '{name}'. Valid states: {VALID_STATES}")
    return STATE_DIR / f"{name}.json"

def load_state(state_name: str) -> dict:
    path = get_state_path(state_name)
    if not path.exists():
        raise FileNotFoundError(f"State file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state_name: str, data: dict, create_backup: bool = True) -> Path:
    path = get_state_path(state_name)
    if create_backup and path.exists():
        backup_path = path.with_suffix(".bak")
        shutil.copy2(path, backup_path)
    
    data["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Atomic write via temp file
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    temp_path.replace(path)
    return path

def validate_all_states() -> dict:
    results = {}
    for state_name in VALID_STATES:
        try:
            data = load_state(state_name)
            assert "version" in data, "Missing 'version'"
            assert "last_updated" in data, "Missing 'last_updated'"
            results[state_name] = {"valid": True, "keys": list(data.keys())}
        except Exception as e:
            results[state_name] = {"valid": False, "error": str(e)}
    return results

class StateEngineTests(unittest.TestCase):
    def test_load_all(self):
        for s in VALID_STATES:
            data = load_state(s)
            self.assertIsInstance(data, dict)
            self.assertIn("version", data)

    def test_save_and_backup(self):
        data = load_state("self_model")
        save_state("self_model", data, create_backup=True)
        reloaded = load_state("self_model")
        self.assertIsInstance(reloaded, dict)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(StateEngineTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        results = validate_all_states()
        print(json.dumps(results, indent=2))
