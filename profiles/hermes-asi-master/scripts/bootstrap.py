#!/usr/bin/env python3
"""Bootstrap script — initializes state and verifies environment."""

import os
import sys
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml")
    sys.exit(1)


def bootstrap():
    base = os.path.dirname(os.path.abspath(__file__))
    state_path = os.path.join(base, "..", "state", "state.yaml")
    state_dir = os.path.dirname(state_path)
    os.makedirs(state_dir, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    if os.path.exists(state_path):
        with open(state_path) as f:
            state = yaml.safe_load(f)
    else:
        state = {"state": {}}

    state["state"]["initialized_at"] = now
    state["state"]["last_updated"] = now
    state["state"]["health"] = "healthy"
    state["state"]["current_phase"] = "operational"
    state["state"]["first_run"] = False

    with open(state_path, "w") as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)

    print(f"[BOOTSTRAP] Initialized at {now}")
    print(f"[BOOTSTRAP] State written to {state_path}")
    return 0


if __name__ == "__main__":
    sys.exit(bootstrap())
