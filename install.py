#!/usr/bin/env python3
"""HERMES-ASI-MASTER Installation Script."""

import os
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Verify Python 3.11+ is installed."""
    if sys.version_info < (3, 11):
        print(f"ERROR: Python 3.11+ required. Found {sys.version}")
        return False
    print(f"[OK] Python {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required packages."""
    print("\n[*] Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"[FAIL] pip install failed:\n{result.stderr}")
        return False
    print("[OK] Dependencies installed")
    return True


def create_directories():
    """Create required directory structure."""
    print("\n[*] Creating directories...")
    dirs = [
        "memory/procedural", "memory/episodic", "memory/semantic",
        "logs", "cache", "output",
        "profiles/hermes-asi-master/state",
        "profiles/hermes-asi-master/scripts",
        "profiles/hermes-asi-master/routines"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print(f"[OK] {len(dirs)} directories created")
    return True


def initialize_state():
    """Initialize system state."""
    print("\n[*] Initializing state...")
    state_file = Path("profiles/hermes-asi-master/state/state.yaml")
    if state_file.exists():
        print("[SKIP] State file already exists")
        return True
    return True


def run_health_check():
    """Run initial health check."""
    print("\n[*] Running health check...")
    script = Path("profiles/hermes-asi-master/scripts/health_check.py")
    if script.exists():
        result = subprocess.run([sys.executable, str(script)])
        return result.returncode == 0
    print("[SKIP] Health check script not found")
    return True


def main():
    print("=" * 60)
    print("  HERMES-ASI-MASTER v1.0.0 — Installation")
    print("=" * 60)

    base = Path(__file__).parent
    os.chdir(base)

    steps = [
        ("Python version check", check_python_version),
        ("Create directories", create_directories),
        ("Install dependencies", install_dependencies),
        ("Initialize state", initialize_state),
        ("Health check", run_health_check),
    ]

    for name, func in steps:
        if not func():
            print(f"\n[FAIL] Installation failed at: {name}")
            return 1

    print("\n" + "=" * 60)
    print("  Installation Complete!")
    print("  Run: python -m hermes_asi_master orchestrate")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
