"""
Tests for Checkpoint System.
Test count: 14
"""
import sys
import os
import shutil
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from v9.horizon.checkpoint import (
    Checkpoint,
    CheckpointStore,
    CheckpointManager,
    CheckpointStrategy,
    AsyncCheckpointManager,
)


class TestCheckpoint:
    def test_create_checkpoint(self):
        cp = Checkpoint(
            id="cp1",
            workflow_id="wf1",
            step=1,
            state={"key": "value"},
            metadata={},
        )
        assert cp.id == "cp1"
        assert cp.workflow_id == "wf1"
        assert cp.step == 1

    def test_checksum_computed(self):
        cp = Checkpoint(
            id="cp1",
            workflow_id="wf1",
            step=1,
            state={"key": "value"},
            metadata={},
        )
        assert len(cp.checksum) > 0

    def test_verify_valid(self):
        cp = Checkpoint(
            id="cp1",
            workflow_id="wf1",
            step=1,
            state={"key": "value"},
            metadata={},
        )
        assert cp.verify() is True

    def test_verify_tampered(self):
        cp = Checkpoint(
            id="cp1",
            workflow_id="wf1",
            step=1,
            state={"key": "value"},
            metadata={},
        )
        cp.state = {"key": "tampered"}
        assert cp.verify() is False

    def test_to_dict(self):
        cp = Checkpoint(
            id="cp1",
            workflow_id="wf1",
            step=1,
            state={"a": 1},
            metadata={"note": "test"},
        )
        d = cp.to_dict()
        assert d["id"] == "cp1"
        assert d["workflow_id"] == "wf1"
        assert d["step"] == 1

    def test_from_dict(self):
        data = {
            "id": "cp1",
            "workflow_id": "wf1",
            "step": 1,
            "state": {"a": 1},
            "metadata": {},
            "parent_id": None,
            "created_at": 123.0,
            "checksum": "abc",
        }
        cp = Checkpoint.from_dict(data)
        assert cp.id == "cp1"
        assert cp.step == 1

    def test_checkpoint_manager_save(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store)
            cp = manager.save({"key": "value"})
            assert cp.step == 0
            assert len(manager._checkpoints) == 1
        finally:
            shutil.rmtree(tmpdir)

    def test_checkpoint_manager_restore(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store)
            manager.save({"key": "value"})
            restored = manager.restore()
            assert restored is not None
            assert restored["key"] == "value"
        finally:
            shutil.rmtree(tmpdir)

    def test_checkpoint_manager_history(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store, auto_checkpoint_interval=1)
            manager.save({"step": 1})
            manager.step()
            manager.save({"step": 2})
            history = manager.get_history()
            assert len(history) == 2
        finally:
            shutil.rmtree(tmpdir)

    def test_checkpoint_manager_incremental(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager(
                "wf1", store=store, strategy=CheckpointStrategy.INCREMENTAL
            )
            manager.save({"a": 1, "b": 2})
            manager.save({"a": 1, "b": 3})  # Only b changed
            history = manager.get_history()
            assert len(history) == 2
        finally:
            shutil.rmtree(tmpdir)

    def test_checkpoint_store_list(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store)
            manager.save({"a": 1})
            manager.step()
            manager.save({"a": 2})
            checkpoints = store.list_checkpoints("wf1")
            assert len(checkpoints) == 2
        finally:
            shutil.rmtree(tmpdir)

    def test_checkpoint_store_latest(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store)
            manager.save({"a": 1})
            manager.step()
            manager.save({"a": 999})
            latest = store.get_latest("wf1")
            assert latest is not None
            assert latest.state["a"] == 999
        finally:
            shutil.rmtree(tmpdir)

    def test_checkpoint_cleanup(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store, auto_checkpoint_interval=1)
            for i in range(10):
                manager.save({"step": i})
                manager.step()
            store.cleanup("wf1", keep_last=3)
            remaining = store.list_checkpoints("wf1")
            assert len(remaining) == 3
        finally:
            shutil.rmtree(tmpdir)

    def test_should_checkpoint(self):
        tmpdir = tempfile.mkdtemp()
        try:
            store = CheckpointStore(base_path=tmpdir)
            manager = CheckpointManager("wf1", store=store, auto_checkpoint_interval=5)
            manager.step()  # step 1
            assert manager.should_checkpoint() is True
            for _ in range(4):
                manager.step()
            assert manager.should_checkpoint() is True  # step 5
        finally:
            shutil.rmtree(tmpdir)
