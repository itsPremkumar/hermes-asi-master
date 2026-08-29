#!/usr/bin/env python3
"""Model-vanish guard: verifies every pinned free model still exists in the
provider catalog. Zero API cost (catalog GET only). Silent when all healthy.
"""
import json, os, urllib.request

PINNED = [
    ("nvidia/nemotron-3-super-120b-a12b:free", "openrouter"),
    ("z-ai/glm-5.2:free", "openrouter"),
    ("nvidia/nemotron-nano-9b-v2:free", "openrouter"),
    ("poolside/laguna-s-2.1:free", "openrouter"),
]
CATALOG = "https://openrouter.ai/api/v1/models"

try:
    req = urllib.request.Request(CATALOG, headers={"User-Agent": "hermes-company-watchdog/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    ids = {m.get("id") for m in data.get("data", [])}
except Exception as e:
    print(f"MODEL CATALOG UNREACHABLE: {e}")  # network down is worth waking someone
    raise SystemExit(0)

missing = [mid for mid, _ in PINNED if mid not in ids]
if missing:
    print("MODELS VANISHED FROM CATALOG:", ", ".join(missing))
    print("ACTION: re-pin affected crons/bots to a live free model (see ops-dashboard notes)")
# else: silent - all pins healthy
