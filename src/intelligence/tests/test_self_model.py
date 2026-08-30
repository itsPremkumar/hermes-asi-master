"""Tests for self_model.py."""

import pytest
from intelligence.self_model import SelfModel, Capability, Limitation, InteractionRecord


class TestSelfModel:
    def test_add_capability(self, self_model):
        cap = self_model.add_capability("coding", proficiency=0.8)
        assert cap.id is not None
        assert cap.name == "coding"
        assert cap.proficiency == 0.8

    def test_get_capability(self, self_model):
        added = self_model.add_capability("analysis")
        retrieved = self_model.get_capability(added.id)
        assert retrieved is not None
        assert retrieved.name == "analysis"

    def test_find_by_category(self, self_model):
        self_model.add_capability("coding", category="technical")
        self_model.add_capability("writing", category="creative")
        results = self_model.find_capabilities(category="technical")
        assert len(results) == 1

    def test_update_proficiency(self, self_model):
        cap = self_model.add_capability("test", proficiency=0.3)
        updated = self_model.update_proficiency(cap.id, 0.9)
        assert updated.proficiency == 0.9
        assert updated.usage_count == 1

    def test_add_limitation(self, self_model):
        lim = self_model.add_limitation("no_internet", severity=0.7)
        assert lim.id is not None
        assert lim.name == "no_internet"

    def test_add_interaction(self, self_model):
        record = self_model.record_interaction("task", description="test task", success=True)
        assert record.id is not None
        assert record.task_type == "task"
        assert record.success is True

    def test_get_interactions(self, self_model):
        self_model.record_interaction("type_a")
        self_model.record_interaction("type_b")
        interactions = self_model.get_interactions()
        assert len(interactions) >= 2

    def test_get_self_assessment(self, self_model):
        self_model.add_capability("coding", proficiency=0.8)
        self_model.add_capability("analysis", proficiency=0.6)
        self_model.record_interaction("task", success=True)
        assessment = self_model.get_self_assessment()
        assert assessment["total_capabilities"] == 2
        assert assessment["total_interactions"] == 1

    def test_persistence(self, temp_storage):
        sm1 = SelfModel(storage_path=temp_storage)
        sm1.add_capability("test_cap")
        sm2 = SelfModel(storage_path=temp_storage)
        assert len(sm2.find_capabilities()) == 1

    def test_clear(self, self_model):
        self_model.add_capability("test")
        self_model.clear()
        assert len(self_model.list_all()["capabilities"]) == 0
