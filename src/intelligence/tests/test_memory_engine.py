"""Tests for memory_engine.py."""

import os
import pytest
from intelligence.memory_engine import MemoryEngine, MemoryEntry, atomic_file_write


class TestMemoryEntry:
    def test_create_entry(self):
        entry = MemoryEntry(id="e1", content="test content")
        assert entry.id == "e1"
        assert entry.content == "test content"
        assert entry.category == "general"
        assert entry.importance == 0.5
        assert entry.access_count == 0

    def test_to_dict(self):
        entry = MemoryEntry(id="e1", content="test", category="facts")
        d = entry.to_dict()
        assert d["id"] == "e1"
        assert d["content"] == "test"
        assert d["category"] == "facts"

    def test_from_dict(self):
        d = {"id": "e1", "content": "test", "category": "general", "tags": [],
             "metadata": {}, "created_at": 0.0, "updated_at": 0.0,
             "importance": 0.5, "access_count": 0, "last_accessed": None,
             "embedding": None}
        entry = MemoryEntry.from_dict(d)
        assert entry.id == "e1"
        assert entry.content == "test"

    def test_touch(self):
        entry = MemoryEntry(id="e1", content="test")
        entry.touch()
        assert entry.access_count == 1
        assert entry.last_accessed is not None


class TestMemoryEngine:
    def test_add_memory(self, memory_engine):
        entry = memory_engine.add("The sky is blue", category="facts")
        assert entry.id is not None
        assert entry.content == "The sky is blue"
        assert entry.category == "facts"

    def test_add_duplicate(self, memory_engine):
        memory_engine.add("unique content")
        memory_engine.add("unique content")
        assert memory_engine.count() == 1

    def test_get_memory(self, memory_engine):
        added = memory_engine.add("retrievable content")
        retrieved = memory_engine.get(added.id)
        assert retrieved is not None
        assert retrieved.content == "retrievable content"

    def test_get_nonexistent(self, memory_engine):
        assert memory_engine.get("nonexistent") is None

    def test_search(self, memory_engine):
        memory_engine.add("Python is a programming language")
        memory_engine.add("JavaScript is also a language")
        results = memory_engine.search("Python")
        assert len(results) >= 1

    def test_search_by_category(self, memory_engine):
        memory_engine.add("fact content", category="facts")
        memory_engine.add("opinion content", category="opinions")
        results = memory_engine.search("content", category="facts")
        assert len(results) == 1

    def test_delete(self, memory_engine):
        entry = memory_engine.add("to be deleted")
        assert memory_engine.delete(entry.id) is True
        assert memory_engine.get(entry.id) is None

    def test_delete_nonexistent(self, memory_engine):
        assert memory_engine.delete("nonexistent") is False

    def test_list_all(self, memory_engine):
        memory_engine.add("one")
        memory_engine.add("two")
        all_entries = memory_engine.list_all()
        assert len(all_entries) == 2

    def test_clear(self, memory_engine):
        memory_engine.add("one")
        memory_engine.add("two")
        memory_engine.clear()
        assert memory_engine.count() == 0

    def test_persistence(self, temp_storage):
        engine1 = MemoryEngine(storage_path=temp_storage)
        engine1.add("persistent content")
        engine2 = MemoryEngine(storage_path=temp_storage)
        assert engine2.count() == 1

    def test_count(self, memory_engine):
        assert memory_engine.count() == 0
        memory_engine.add("one")
        assert memory_engine.count() == 1


class TestAtomicFileWrite:
    def test_write_and_read(self, tmp_path):
        path = str(tmp_path / "test.json")
        atomic_file_write(path, {"key": "value"})
        assert os.path.exists(path)
        import json
        with open(path) as f:
            data = json.load(f)
        assert data["key"] == "value"

    def test_atomic_replacement(self, tmp_path):
        path = str(tmp_path / "test.json")
        atomic_file_write(path, {"v": 1})
        atomic_file_write(path, {"v": 2})
        import json
        with open(path) as f:
            data = json.load(f)
        assert data["v"] == 2
