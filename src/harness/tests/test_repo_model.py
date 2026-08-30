"""Tests for repo_model.py."""
import pytest
import os
import tempfile
import subprocess

from harness.repo_model import RepositoryModel, Repository, PullRequest


class TestRepository:
    def test_create(self):
        r = Repository(id="r1", name="test", path="/tmp")
        assert r.id == "r1"
        assert r.name == "test"
        assert r.default_branch == "main"

    def test_to_dict(self):
        r = Repository(id="r1", name="test", path="/tmp")
        d = r.to_dict()
        assert d["id"] == "r1"

    def test_from_dict(self):
        d = {"id": "r1", "name": "test", "path": "/tmp", "remote_url": "", "default_branch": "main", "branches": ["main"], "metadata": {}, "created_at": 0.0}
        r = Repository.from_dict(d)
        assert r.id == "r1"


class TestPullRequest:
    def test_create(self):
        pr = PullRequest(id="p1", repo_id="r1", title="PR", source_branch="feat", target_branch="main")
        assert pr.status == "open"

    def test_to_dict(self):
        pr = PullRequest(id="p1", repo_id="r1", title="PR", source_branch="feat", target_branch="main")
        d = pr.to_dict()
        assert d["id"] == "p1"


class TestRepositoryModel:
    def test_create_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            repo = model.create_repo("test", tmp)
            assert repo.id is not None
            assert repo.name == "test"

    def test_get_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            created = model.create_repo("test", tmp)
            retrieved = model.get_repo(created.id)
            assert retrieved is not None
            assert retrieved.id == created.id

    def test_list_repos(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            model.create_repo("test1", tmp)
            model.create_repo("test2", tmp)
            assert len(model.list_repos()) == 2

    def test_create_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            repo = model.create_repo("test", tmp)
            assert model.create_branch(repo.id, "feature-x")
            assert "feature-x" in model.get_repo(repo.id).branches

    def test_create_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            repo = model.create_repo("test", tmp)
            pr = model.create_pr(repo.id, "feat", "Add feature")
            assert pr is not None
            assert pr.status == "open"

    def test_merge_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            repo = model.create_repo("test", tmp)
            pr = model.create_pr(repo.id, "feat", "Add feature")
            assert model.merge_pr(pr.id)
            assert model.prs[pr.id].status == "merged"

    def test_get_prs_by_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            repo = model.create_repo("test", tmp)
            pr = model.create_pr(repo.id, "feat", "Add feature")
            open_prs = model.get_prs(status="open")
            assert len(open_prs) == 1
            model.merge_pr(pr.id)
            merged_prs = model.get_prs(status="merged")
            assert len(merged_prs) == 1

    def test_run_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = RepositoryModel(storage_path=tmp)
            # Init a real git repo
            subprocess.run(["git", "init", tmp], capture_output=True)
            subprocess.run(["git", "-C", tmp, "config", "user.email", "test@test.com"], capture_output=True)
            subprocess.run(["git", "-C", tmp, "config", "user.name", "Test"], capture_output=True)
            subprocess.run(["git", "-C", tmp, "commit", "--allow-empty", "-m", "init"], capture_output=True)
            repo = model.create_repo("test", tmp)
            rc, out, err = model.run_git(repo.id, "status")
            assert rc == 0
