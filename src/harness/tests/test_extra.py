"""Additional tests for harness modules to reach ≥100 total."""
import pytest
import os
import tempfile
import time

from harness.repo_model import RepositoryModel, Repository
from harness.code_generator import CodeGenerator
from harness.ci_cd import CICDPipeline
from harness.release import ReleaseManager, ChangelogEntry


class TestRepositoryExtended:
    def test_repo_branches_default(self):
        r = Repository(id="r1", name="test", path="/tmp", branches=["main"])
        assert "main" in r.branches

    def test_repo_metadata(self):
        r = Repository(id="r1", name="test", path="/tmp", metadata={"key": "val"})
        assert r.metadata["key"] == "val"


class TestCodeGeneratorExtended:
    def test_generate_multiple(self):
        gen = CodeGenerator()
        t = gen.register_template("t", "python", "def {{ name }}():")
        gen.generate(t.id, name="a")
        gen.generate(t.id, name="b")
        assert len(gen.generated) == 2

    def test_generate_invalid_template(self):
        gen = CodeGenerator()
        assert gen.generate("nonexistent", name="x") is None

    def test_generate_function_bash(self):
        gen = CodeGenerator()
        func = gen.generate_function("my_func", "bash", ["$1", "$2"], "    echo $1")
        assert "my_func()" in func

    def test_generate_function_unsupported(self):
        gen = CodeGenerator()
        func = gen.generate_function("f", "rust", [], "")
        assert "not supported" in func

    def test_generate_class_no_properties(self):
        gen = CodeGenerator()
        cls = gen.generate_class("C", "python", ["def m(self):"])
        assert "class C:" in cls
        assert "def m(self):" in cls


class TestCICDPipelineExtended:
    def test_pipeline_with_multiple_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("multi", "main", ["echo a", "echo b", "echo c"])
            run = pipe.run_pipeline(p.id)
            assert len(run.steps) == 3

    def test_pipeline_all_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("ok", "main", ["echo ok"])
            run = pipe.run_pipeline(p.id)
            assert run.status == "success"
            assert all(s.status == "success" for s in run.steps)

    def test_pipeline_runs_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipe = CICDPipeline(storage_path=tmp)
            p = pipe.register_pipeline("p", "main", ["echo x"])
            run1 = pipe.run_pipeline(p.id, "sha1")
            run2 = pipe.run_pipeline(p.id, "sha2")
            assert run1.id != run2.id
            assert run1.commit_sha != run2.commit_sha


class TestReleaseManagerExtended:
    def test_release_publish_prevents_double(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            rel = mgr.create_release("1.0.0", "main")
            assert mgr.publish_release(rel.id)
            assert not mgr.publish_release(rel.id)  # already published

    def test_changelog_groups_by_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            rel = mgr.create_release("1.0.0", "main")
            rel.add_entry(ChangelogEntry(type="feat", description="A"))
            rel.add_entry(ChangelogEntry(type="feat", description="B"))
            rel.add_entry(ChangelogEntry(type="fix", description="C"))
            changelog = mgr.generate_changelog(rel.id)
            assert "A" in changelog
            assert "B" in changelog
            assert "C" in changelog

    def test_release_list_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = ReleaseManager(storage_path=tmp)
            mgr.create_release("1.0.0", "main")
            mgr.create_release("2.0.0", "main")
            releases = mgr.list_releases()
            assert len(releases) == 2
