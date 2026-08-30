"""Tests for Debugger and Release modules."""
import pytest
import os
import tempfile

from harness.debugger import Debugger, DebugSession, StackFrame
from harness.release import ReleaseManager, Release, ChangelogEntry


class TestStackFrame:
    def test_create(self):
        frame = StackFrame(filename="test.py", lineno=10, function="main", locals={"x": 1})
        assert frame.filename == "test.py"
        assert frame.lineno == 10
        assert frame.locals["x"] == 1


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

    def test_set_local(self):
        session = DebugSession(id="d1", target="test.py")
        session.set_local("x", 42)
        assert session.locals["x"] == 42


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
        assert dbg.stop_session(session.id)
        assert dbg.sessions[session.id].status == "stopped"

    def test_stop_nonexistent(self):
        dbg = Debugger()
        assert not dbg.stop_session("nonexistent")

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
        assert result == 43

    def test_evaluate_no_session(self):
        dbg = Debugger()
        assert dbg.evaluate("nonexistent", "x") is None


class TestChangelogEntry:
    def test_create(self):
        entry = ChangelogEntry(type="feat", description="Add feature", pr_id="pr1")
        assert entry.type == "feat"
        assert entry.description == "Add feature"
        assert entry.pr_id == "pr1"


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

    def test_publish_no_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            release = mgr.create_release("1.0.0", "main")
            # Should still publish (empty changelog)
            assert mgr.publish_release(release.id)

    def test_generate_changelog(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            release = mgr.create_release("1.0.0", "main")
            release.add_entry(ChangelogEntry(type="feat", description="Add feature"))
            release.add_entry(ChangelogEntry(type="fix", description="Fix bug"))
            changelog = mgr.generate_changelog(release.id)
            assert "feat" in changelog
            assert "Add feature" in changelog

    def test_generate_changelog_no_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            assert mgr.generate_changelog("nonexistent") == ""
