#!/usr/bin/env python3
"""
sandbox.py — Local Process & Tool Execution Sandbox
Ensures safe, bounded execution of arbitrary code and tool scripts.
"""

import os
import sys
import time
import pathlib
import subprocess
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    timed_out: bool = False

class ExecutionSandbox:
    def __init__(self, workspace_dir: Optional[str] = None, timeout_sec: int = 30):
        if workspace_dir:
            self.workspace = pathlib.Path(workspace_dir).resolve()
        else:
            self.workspace = pathlib.Path("sandbox_workdir").resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.timeout_sec = timeout_sec

    def run_command(self, cmd: list[str], env: Optional[Dict[str, str]] = None) -> SandboxResult:
        """Executes a command inside the bounded sandbox."""
        start_time = time.time()
        custom_env = os.environ.copy()
        if env:
            custom_env.update(env)

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                env=custom_env
            )
            duration = (time.time() - start_time) * 1000
            return SandboxResult(
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_ms=duration,
                timed_out=False
            )
        except subprocess.TimeoutExpired:
            duration = (time.time() - start_time) * 1000
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr="Execution timed out.",
                duration_ms=duration,
                timed_out=True
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return SandboxResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration,
                timed_out=False
            )

    def run_python_code(self, code: str) -> SandboxResult:
        """Executes inline Python code inside sandbox."""
        temp_file = self.workspace / f"eval_{int(time.time() * 1000)}.py"
        temp_file.write_text(code, encoding="utf-8")
        try:
            res = self.run_command([sys.executable, str(temp_file)])
            return res
        finally:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass
