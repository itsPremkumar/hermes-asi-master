"""
Tests for Unified Cross-KG Ontology Schema.
Test count: 22
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'src'))

from ontology import (
    UnifiedOntology,
    CrossKGQuery,
    UnifiedEntity,
    UnifiedRelation,
    UnifiedEntityType,
    UnifiedRelationType,
    TypeMapping,
    TemporalReasoning,
    ConfidenceScoring,
)


# ──────────────────── Type Mapping Tests ──────────────────────────────


class TestTypeMapping:
    def test_create(self):
        mapping = TypeMapping()
        assert mapping is not None

    def test_map_entity(self):
        mapping = TypeMapping()
        mapping.map_entity("finance", "Company", UnifiedEntityType.ORGANIZATION)
        result = mapping.get_entity_type("finance", "Company")
        assert result == UnifiedEntityType.ORGANIZATION

    def test_map_relation(self):
        mapping = TypeMapping()
        mapping.map_relation("finance", "acquired", UnifiedRelationType.ACQUIRED)
        result = mapping.get_relation_type("finance", "acquired")
        assert result == UnifiedRelationType.ACQUIRED

    def test_get_entity_type_none(self):
        mapping = TypeMapping()
        result = mapping.get_entity_type("nonexistent", "Type")
        assert result is None

    def test_list_mappings(self):
        mapping = TypeMapping()
        mapping.map_entity("finance", "Company", UnifiedEntityType.ORGANIZATION)
        mappings = mapping.list_mappings()
        assert "entity_mappings" in mappings


# ──────────────────── Entity Tests ────────────────────────────────────


class TestUnifiedEntity:
    def test_create(self):
        entity = UnifiedEntity(
            id="e1",
            entity_type=UnifiedEntityType.ORGANIZATION,
            label="Apple Inc.",
        )
        assert entity.id == "e1"
        assert entity.entity_type == UnifiedEntityType.ORGANIZATION
        assert entity.confidence == 1.0

    def test_to_dict(self):
        entity = UnifiedEntity(
            id="e1",
            entity_type=UnifiedEntityType.PERSON,
            label="Tim Cook",
            properties={"role": "CEO"},
        )
        d = entity.to_dict()
        assert d["id"] == "e1"
        assert d["type"] == "Person"
        assert d["properties"]["role"] == "CEO"


# ──────────────────── Relation Tests ─────────────────────────────────


class TestUnifiedRelation:
    def test_create(self):
        relation = UnifiedRelation(
            id="r1",
            relation_type=UnifiedRelationType.ACQUIRED,
            source="e1",
            target="e2",
        )
        assert relation.id == "r1"
        assert relation.relation_type == UnifiedRelationType.ACQUIRED

    def test_to_dict(self):
        relation = UnifiedRelation(
            id="r1",
            relation_type=UnifiedRelationType.EMPLOYS,
            source="e1",
            target="e2",
            properties={"since": "2011"},
        )
        d = relation.to_dict()
        assert d["type"] == "employs"
        assert d["properties"]["since"] == "2011"


# ──────────────────── Ontology Tests ─────────────────────────────────


class TestUnifiedOntology:
    def test_create(self):
        ontology = UnifiedOntology()
        assert ontology is not None

    def test_register_kg(self):
        ontology = UnifiedOntology()
        ontology.register_kg("finance", {"name": "Finance KG"})
        assert "finance" in ontology.list_kgs()

    def test_add_entity(self):
        ontology = UnifiedOntology()
        entity = UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple")
        ontology.add_entity(entity)
        result = ontology.get_entity("e1")
        assert result is not None
        assert result.label == "Apple"

    def test_add_relation(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))
        ontology.add_entity(UnifiedEntity(id="e2", entity_type=UnifiedEntityType.ORGANIZATION, label="Beats"))
        relation = UnifiedRelation(id="r1", relation_type=UnifiedRelationType.ACQUIRED, source="e1", target="e2")
        ontology.add_relation(relation)
        relations = ontology.get_relations("e1")
        assert len(relations) == 1

    def test_find_entities_by_type(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))
        ontology.add_entity(UnifiedEntity(id="e2", entity_type=UnifiedEntityType.PERSON, label="Tim Cook"))
        results = ontology.find_entities(entity_type=UnifiedEntityType.ORGANIZATION)
        assert len(results) == 1

    def test_find_entities_by_label(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple Inc."))
        results = ontology.find_entities(label="Apple")
        assert len(results) == 1

    def test_map_domain_entity(self):
        ontology = UnifiedOntology()
        ontology.type_mapping.map_entity("finance", "Company", UnifiedEntityType.ORGANIZATION)
        entity = ontology.map_domain_entity("finance", "Company", "Apple", source_id="AAPL")
        assert entity.entity_type == UnifiedEntityType.ORGANIZATION
        assert entity.source_kg == "finance"

    def test_get_stats(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))
        stats = ontology.get_stats()
        assert stats["entities"] == 1

    def test_export_import(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name

        try:
            ontology.export_json(path)
            ontology2 = UnifiedOntology()
            ontology2.import_json(path)
            stats = ontology2.get_stats()
            assert stats["entities"] == 1
        finally:
            os.unlink(path)


# ──────────────────── Cross-KG Query Tests ────────────────────────────


class TestCrossKGQuery:
    def test_create(self):
        ontology = UnifiedOntology()
        query = CrossKGQuery(ontology)
        assert query is not None

    def test_find(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))
        ontology.add_entity(UnifiedEntity(id="e2", entity_type=UnifiedEntityType.ORGANIZATION, label="Beats"))
        ontology.add_relation(UnifiedRelation(id="r1", relation_type=UnifiedRelationType.ACQUIRED, source="e1", target="e2"))

        query = CrossKGQuery(ontology)
        results = query.find("Organization", "acquired", "Organization")
        assert len(results) == 1

    def test_find_by_label(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))

        query = CrossKGQuery(ontology)
        results = query.find_by_label("Apple")
        assert len(results) == 1

    def test_find_by_type(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))
        ontology.add_entity(UnifiedEntity(id="e2", entity_type=UnifiedEntityType.PERSON, label="Tim Cook"))

        query = CrossKGQuery(ontology)
        results = query.find_by_type("Organization")
        assert len(results) == 1

    def test_get_network(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple"))
        ontology.add_entity(UnifiedEntity(id="e2", entity_type=UnifiedEntityType.ORGANIZATION, label="Beats"))
        ontology.add_relation(UnifiedRelation(id="r1", relation_type=UnifiedRelationType.ACQUIRED, source="e1", target="e2"))

        query = CrossKGQuery(ontology)
        network = query.get_network("e1")
        assert len(network["nodes"]) >= 1


# ──────────────────── Temporal Reasoning Tests ────────────────────────


class TestTemporalReasoning:
    def test_is_valid_at(self):
        entity = UnifiedEntity(
            id="e1",
            entity_type=UnifiedEntityType.ORGANIZATION,
            label="Apple",
            valid_from="2020-01-01",
            valid_to="2025-12-31",
        )
        assert TemporalReasoning.is_valid_at(entity, "2024-06-15") is True
        assert TemporalReasoning.is_valid_at(entity, "2026-01-01") is False

    def test_is_active_at(self):
        relation = UnifiedRelation(
            id="r1",
            relation_type=UnifiedRelationType.ACQUIRED,
            source="e1",
            target="e2",
            valid_from="2014-05-28",
        )
        assert TemporalReasoning.is_active_at(relation, "2024-01-01") is True
        assert TemporalReasoning.is_active_at(relation, "2014-01-01") is False

    def test_find_at(self):
        ontology = UnifiedOntology()
        ontology.add_entity(UnifiedEntity(
            id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple",
            valid_from="2020-01-01",
        ))
        results = TemporalReasoning.find_at(ontology, UnifiedEntityType.ORGANIZATION, "2024-01-01")
        assert len(results) == 1


# ──────────────────── Confidence Scoring Tests ────────────────────────


class TestConfidenceScoring:
    def test_calculate_aggregate(self):
        score = ConfidenceScoring.calculate_aggregate([0.9, 0.8, 0.95])
        assert 0 < score <= 1.0

    def test_calculate_aggregate_empty(self):
        score = ConfidenceScoring.calculate_aggregate([])
        assert score == 0.0

    def test_update_confidence(self):
        entity = UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple", confidence=0.8)
        ConfidenceScoring.update_confidence(entity, 0.9, "source2")
        assert entity.confidence > 0.8
