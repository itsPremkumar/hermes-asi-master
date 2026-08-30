"""Tests for world_model.py."""

import pytest
from intelligence.world_model import WorldModel, Entity, Relationship


class TestEntity:
    def test_create_entity(self):
        e = Entity(id="e1", name="Python", type="language")
        assert e.id == "e1"
        assert e.name == "Python"
        assert e.type == "language"

    def test_to_dict(self):
        e = Entity(id="e1", name="Test")
        d = e.to_dict()
        assert d["id"] == "e1"
        assert d["name"] == "Test"

    def test_from_dict(self):
        d = {"id": "e1", "name": "Test", "type": "object", "properties": {},
             "tags": [], "metadata": {}, "created_at": 0.0, "updated_at": 0.0}
        e = Entity.from_dict(d)
        assert e.id == "e1"


class TestWorldModel:
    def test_add_entity(self, world_model):
        e = world_model.add_entity("Python", entity_type="language")
        assert e.id is not None
        assert e.name == "Python"
        assert e.type == "language"

    def test_get_entity(self, world_model):
        added = world_model.add_entity("Test")
        retrieved = world_model.get_entity(added.id)
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_get_nonexistent(self, world_model):
        assert world_model.get_entity("nonexistent") is None

    def test_find_by_name(self, world_model):
        world_model.add_entity("Python")
        world_model.add_entity("JavaScript")
        results = world_model.find_entities(name="Python")
        assert len(results) == 1

    def test_find_by_type(self, world_model):
        world_model.add_entity("Python", entity_type="language")
        world_model.add_entity("Snake", entity_type="animal")
        results = world_model.find_entities(entity_type="language")
        assert len(results) == 1

    def test_find_by_tag(self, world_model):
        world_model.add_entity("Python", tags=["programming"])
        world_model.add_entity("Snake", tags=["animal"])
        results = world_model.find_entities(tag="programming")
        assert len(results) == 1

    def test_update_entity(self, world_model):
        e = world_model.add_entity("Python")
        updated = world_model.update_entity(e.id, name="Python 3")
        assert updated.name == "Python 3"

    def test_add_relationship(self, world_model):
        e1 = world_model.add_entity("Python")
        e2 = world_model.add_entity("Programming")
        rel = world_model.add_relationship(e1.id, e2.id, "used_for")
        assert rel is not None
        assert rel.source_id == e1.id
        assert rel.target_id == e2.id

    def test_add_relationship_invalid(self, world_model):
        result = world_model.add_relationship("bad", "also_bad", "test")
        assert result is None

    def test_get_relationships(self, world_model):
        e1 = world_model.add_entity("Python")
        e2 = world_model.add_entity("Programming")
        world_model.add_relationship(e1.id, e2.id, "used_for")
        rels = world_model.get_relationships(entity_id=e1.id)
        assert len(rels) >= 1

    def test_delete_entity(self, world_model):
        e = world_model.add_entity("Test")
        assert world_model.delete_entity(e.id) is True
        assert world_model.get_entity(e.id) is None

    def test_list_all(self, world_model):
        world_model.add_entity("one")
        world_model.add_entity("two")
        all_data = world_model.list_all()
        assert len(all_data["entities"]) == 2

    def test_persistence(self, temp_storage):
        wm1 = WorldModel(storage_path=temp_storage)
        wm1.add_entity("persistent")
        wm2 = WorldModel(storage_path=temp_storage)
        assert len(wm2.list_all()["entities"]) == 1

    def test_clear(self, world_model):
        world_model.add_entity("one")
        world_model.clear()
        assert len(world_model.list_all()["entities"]) == 0
