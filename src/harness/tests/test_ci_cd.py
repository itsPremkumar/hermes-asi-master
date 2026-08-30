"""Tests for CI/CD module."""
import pytest
import os
import tempfile

from harness.ci_cd import CICDPipeline, PipelineRun, PipelineStep


class TestPipelineStep:
    def test_create(self):
        step = PipelineStep(name="test", command="pytest")
        assert step.name == "test"
        assert step.status == "pending"

    def test_to_dict(self):
        step = PipelineStep(name="test", command="pytest")
        d = step.to_dict()
        assert d["name"] == "test"

    def test_from_dict(self):
        d = {"name": "test", "command": "pytest", "status": "success", "output": "", "duration": 0.0}
        step = PipelineStep.from_dict(d)
        assert step.name == "test"
        assert step.status == "success"


class TestPipelineRun:
    def test_create(self):
        run = PipelineRun(id="r1", pipeline_id="p1", commit_sha="abc123")
        assert run.status == "running"
        assert run.commit_sha == "abc123"

    def test_add_step(self):
        run = PipelineRun(id="r1", pipeline_id="p1")
        step = run.add_step("test", "pytest")
        assert len(run.steps) == 1
        assert step.name == "test"

    def test_to_dict(self):
        run = PipelineRun(id="r1", pipeline_id="p1")
        d = run.to_dict()
        assert d["id"] == "r1"
        assert d["pipeline_id"] == "p1"


class TestCICDPipeline:
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            assert len(pipe.pipelines) == 0

    def test_register_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["pytest"])
            assert p.id in pipe.pipelines
            assert p.name == "test"
            assert p.branch == "main"
            assert len(p.steps) == 1

    def test_run_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["echo hello"])
            run = pipe.run_pipeline(p.id, "abc123")
            assert run is not None
            assert run.status in ("success", "failed")
            assert run.commit_sha == "abc123"

    def test_run_pipeline_not_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            assert pipe.run_pipeline("nonexistent") is None

    def test_get_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["echo hello"])
            pipe.run_pipeline(p.id, "abc123")
            pipe.run_pipeline(p.id, "def456")
            runs = pipe.get_runs(p.id)
            assert len(runs) == 2

    def test_list_pipelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            pipe.register_pipeline("test1", "main", ["pytest"])
            pipe.register_pipeline("test2", "develop", ["pytest"])
            assert len(pipe.list_pipelines()) == 2

    def test_pipeline_steps_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["echo step1", "echo step2"])
            run = pipe.run_pipeline(p.id)
            assert len(run.steps) == 2
            assert all(s.status in ("success", "failed") for s in run.steps)

    def test_pipeline_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["false"])  # false exits with 1
            run = pipe.run_pipeline(p.id)
            assert run.status == "failed"

    def test_multiple_pipelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p1 = pipe.register_pipeline("p1", "main", ["echo a"])
            p2 = pipe.register_pipeline("p2", "main", ["echo b"])
            assert len(pipe.get_runs(p1.id)) == 0
            assert len(pipe.get_runs(p2.id)) == 0
