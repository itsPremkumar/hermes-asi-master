"""
t_f0087914 — CI/CD Pipeline Module

Run pipelines, track execution, manage steps.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def atomic_file_write(path: str, data: dict | list) -> None:
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


@dataclass
class PipelineStep:
    """A step in a pipeline."""
    name: str
    command: str
    status: str = "pending"  # pending, running, success, failed
    output: str = ""
    duration: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PipelineStep":
        return cls(**d)


@dataclass
class PipelineRun:
    """A run of a pipeline."""
    id: str
    pipeline_id: str
    commit_sha: str = ""
    status: str = "running"  # running, success, failed
    steps: list[PipelineStep] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    def add_step(self, name: str, command: str) -> PipelineStep:
        step = PipelineStep(name=name, command=command)
        self.steps.append(step)
        return step

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "commit_sha": self.commit_sha,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@dataclass
class Pipeline:
    """A CI/CD pipeline."""
    id: str
    name: str
    branch: str
    steps: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


class CICDPipeline:
    """Manage CI/CD pipelines."""

    def __init__(self, storage_path: str = "./state/ci") -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self.pipelines: dict[str, Pipeline] = {}
        self.runs: dict[str, PipelineRun] = {}
        self._loaded = False
        os.makedirs(storage_path, exist_ok=True)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        state_path = os.path.join(self.storage_path, "ci.json")
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    data = json.load(f)
                for p_data in data.get("pipelines", []):
                    p = Pipeline(**p_data)
                    self.pipelines[p.id] = p
            except (json.JSONDecodeError, KeyError):
                pass
        self._loaded = True

    def _save(self) -> None:
        state_path = os.path.join(self.storage_path, "ci.json")
        data = {
            "pipelines": [p.to_dict() for p in self.pipelines.values()],
        }
        atomic_file_write(state_path, data)

    def register_pipeline(self, name: str, branch: str, steps: list[str]) -> Pipeline:
        """Register a pipeline."""
        pipeline = Pipeline(
            id=str(uuid.uuid4().hex[:8]),
            name=name,
            branch=branch,
            steps=[{"name": f"step-{i}", "command": cmd} for i, cmd in enumerate(steps)],
        )
        self.pipelines[pipeline.id] = pipeline
        self._save()
        return pipeline

    def run_pipeline(self, pipeline_id: str, commit_sha: str = "") -> Optional[PipelineRun]:
        """Run a pipeline."""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
        run = PipelineRun(
            id=str(uuid.uuid4().hex[:8]),
            pipeline_id=pipeline_id,
            commit_sha=commit_sha,
        )
        for step_data in pipeline.steps:
            run.add_step(step_data["name"], step_data["command"])
        # Execute steps
        for step in run.steps:
            step.status = "running"
            try:
                result = subprocess.run(
                    step.command, shell=True, capture_output=True, text=True, timeout=60
                )
                step.output = result.stdout + result.stderr
                step.status = "success" if result.returncode == 0 else "failed"
            except subprocess.TimeoutExpired:
                step.status = "failed"
                step.output = "Timeout"
            except Exception as e:
                step.status = "failed"
                step.output = str(e)
            step.duration = 0.1
        # Determine overall status
        if any(s.status == "failed" for s in run.steps):
            run.status = "failed"
        else:
            run.status = "success"
        run.finished_at = time.time()
        self.runs[run.id] = run
        return run

    def get_runs(self, pipeline_id: str) -> list[PipelineRun]:
        return [r for r in self.runs.values() if r.pipeline_id == pipeline_id]

    def list_pipelines(self) -> list[Pipeline]:
        return list(self.pipelines.values())
