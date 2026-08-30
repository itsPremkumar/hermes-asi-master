"""Tests for CI/CD, Debug, and Release modules."""
import pytest
import os
import tempfile
import time

from harness.ci_cd import CICDPipeline, PipelineRun, PipelineStep
from harness.debugger import Debugger, DebugSession, StackFrame
from harness.release import ReleaseManager, Release, ChangelogEntry


class TestPipelineStep:
    def test_create(self):
        step = PipelineStep(name="test", command="pytest")
        assert step.name == "test"
        assert step.status == "pending"

    def test_to_dict(self):
        step = PipelineStep(name="test", command="pytest")
        d = step.to_dict()
        assert d["name"] == "test"


class TestPipelineRun:
    def test_create(self):
        run = PipelineRun(id="r1", pipeline_id="p1", commit_sha="abc123")
        assert run.status == "running"

    def test_add_step(self):
        run = PipelineRun(id="r1", pipeline_id="p1")
        step = run.add_step("test", "pytest")
        assert len(run.steps) == 1
        assert step.name == "test"


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

    def test_run_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["echo hello"])
            run = pipe.run_pipeline(p.id, "abc123")
            assert run is not None
            assert run.status in ("success", "failed")

    def test_get_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("test", "main", ["echo hello"])
            pipe.run_pipeline(p.id, "abc123")
            runs = pipe.get_runs(p.id)
            assert len(runs) == 1

    def test_list_pipelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            pipe.register_pipeline("test1", "main", ["pytest"])
            pipe.register_pipeline("test2", "main", ["pytest"])
            assert len(pipe.list_pipelines()) == 2


class TestStackFrame:
    def test_create(self):
        frame = StackFrame(filename="test.py", lineno=10, function="main", locals={"x": 1})
        assert frame.filename == "test.py"
        assert frame.lineno == 10


class TestDebugSession:
    def test_create(self):
        session = DebugSession(id="d1", target="test.py")
        assert session.target == "test.py"
        assert session.status == "active"

    def test_add_frame(self):
        session = DebugSession(id="d1", target="test.py")
        frame = StackFrame(filename="test.py", lineno=10, function="main")
        session.add_frame(frame)
        assert len(session.frames) == 1


class TestDebugger:
    def test_create(self):
        dbg = Debugger()
        assert len(dbg.sessions) == 0

    def test_start_session(self):
        dbg = Debugger()
        session = dbg.start_session("test.py")
        assert session.id in dbg.sessions
        assert session.target == "test.py"

    def test_stop_session(self):
        dbg = Debugger()
        session = dbg.start_session("test.py")
        dbg.stop_session(session.id)
        assert dbg.sessions[session.id].status == "stopped"

    def test_get_session(self):
        dbg = Debugger()
        session = dbg.start_session("test.py")
        retrieved = dbg.get_session(session.id)
        assert retrieved is not None
        assert retrieved.id == session.id

    def test_list_sessions(self):
        dbg = Debugger()
        dbg.start_session("test1.py")
        dbg.start_session("test2.py")
        assert len(dbg.list_sessions()) == 2

    def test_evaluate_expression(self):
        dbg = Debugger()
        session = dbg.start_session("test.py")
        session.locals = {"x": 42, "name": "test"}
        result = dbg.evaluate(session.id, "x + 1")
        assert result is not None


class TestChangelogEntry:
    def test_create(self):
        entry = ChangelogEntry(type="feat", description="Add feature", pr_id="pr1")
        assert entry.type == "feat"
        assert entry.description == "Add feature"


class TestRelease:
    def test_create(self):
        release = Release(id="r1", version="1.0.0", branch="main")
        assert release.version == "1.0.0"
        assert release.status == "draft"

    def test_add_entry(self):
        release = Release(id="r1", version="1.0.0", branch="main")
        entry = ChangelogEntry(type="feat", description="Add feature")
        release.add_entry(entry)
        assert len(release.entries) == 1


class TestReleaseManager:
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            assert len(mgr.releases) == 0

    def test_create_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            release = mgr.create_release("1.0.0", "main")
            assert release.id in mgr.releases
            assert release.version == "1.0.0"

    def test_get_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            created = mgr.create_release("1.0.0", "main")
            retrieved = mgr.get_release(created.id)
            assert retrieved is not None
            assert retrieved.version == "1.0.0"

    def test_list_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            mgr.create_release("1.0.0", "main")
            mgr.create_release("1.1.0", "main")
            assert len(mgr.list_releases()) == 2

    def test_publish_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            release = mgr.create_release("1.0.0", "main")
            release.add_entry(ChangelogEntry(type="feat", description="Initial"))
            assert mgr.publish_release(release.id)
            assert mgr.releases[release.id].status == "published"

    def test_generate_changelog(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            release = mgr.create_release("1.0.0", "main")
            release.add_entry(ChangelogEntry(type="feat", description="Add feature"))
            release.add_entry(ChangelogEntry(type="fix", description="Fix bug"))
            changelog = mgr.generate_changelog(release.id)
            assert "feat" in changelog
            assert "Add feature" in changelog
