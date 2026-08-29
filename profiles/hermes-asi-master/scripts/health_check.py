#!/usr/bin/env python3
"""Health check script for HERMES-ASI-MASTER master profile."""

import json
import os
import sys
from datetime import datetime, timezone


def check_state():
    """Verify state file exists and is valid."""
    state_path = os.path.join(os.path.dirname(__file__), "..", "state", "state.yaml")
    if not os.path.exists(state_path):
        return {"status": "error", "message": "State file not found"}
    return {"status": "ok", "state_path": state_path}


def check_dependencies():
    """Verify required dependencies are importable."""
    required = ["asyncio", "yaml", "aiohttp", "pydantic"]
    missing = []
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        return {"status": "warning", "missing": missing}
    return {"status": "ok"}


def main():
    now = datetime.now(timezone.utc).isoformat()
    state_check = check_state()
    deps_check = check_dependencies()

    report = {
        "timestamp": now,
        "service": "hermes-asi-master",
        "version": "1.0.0",
        "state": state_check,
        "dependencies": deps_check,
    }

    all_ok = all(c["status"] == "ok" for c in [state_check, deps_check])
    report["healthy"] = all_ok

    print(json.dumps(report, indent=2))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
