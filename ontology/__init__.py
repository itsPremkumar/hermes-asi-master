"""
Unified Cross-KG Ontology Schema.

Provides common entity types, relation types, and mapping rules for
interoperability across heterogeneous knowledge graphs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


# ──────────────────────────── Enums ──────────────────────────────────


class UnifiedEntityType(Enum):
    PERSON = "Person"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    EVENT = "Event"
    PRODUCT = "Product"
    FINANCIAL_INSTRUMENT = "FinancialInstrument"
    REGULATION = "Regulation"
    CONCEPT = "Concept"


class UnifiedRelationType(Enum):
    EMPLOYS = "employs"
    LOCATED_IN = "located_in"
    ACQUIRED = "acquired"
    MERGED_WITH = "merged_with"
    COMPETES_WITH = "competes_with"
    REGULATES = "regulates"
    SUPPLIES = "supplies"
    PARTNERS_WITH = "partners_with"
    PRODUCES = "produces"
    INFLUENCES = "influences"
    DERIVED_FROM = "derived_from"
    VERSION_OF = "version_of"


# ──────────────────────── Types ──────────────────────────────────────


@dataclass
class UnifiedEntity:
    """A unified entity across knowledge graphs."""
    id: str
    entity_type: UnifiedEntityType
    label: str
    properties: dict = field(default_factory=dict)
    source_kg: str = ""
    source_id: str = ""
    confidence: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    provenance: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.entity_type.value,
            "label": self.label,
            "properties": self.properties,
            "source_kg": self.source_kg,
            "source_id": self.source_id,
            "confidence": self.confidence,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "provenance": self.provenance,
        }


@dataclass
class UnifiedRelation:
    """A unified relation across knowledge graphs."""
    id: str
    relation_type: UnifiedRelationType
    source: str  # Entity ID
    target: str  # Entity ID
    properties: dict = field(default_factory=dict)
    source_kg: str = ""
    confidence: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    provenance: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.relation_type.value,
            "source": self.source,
            "target": self.target,
            "properties": self.properties,
            "source_kg": self.source_kg,
            "confidence": self.confidence,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "provenance": self.provenance,
        }


# ─────────────────────── Type Mapping ────────────────────────────────


class TypeMapping:
    """Maps domain-specific types to unified types."""

    def __init__(self):
        self._entity_mappings: dict[str, dict[str, UnifiedEntityType]] = {}
        self._relation_mappings: dict[str, dict[str, UnifiedRelationType]] = {}

    def map_entity(
        self,
        kg_name: str,
        domain_type: str,
        unified_type: UnifiedEntityType,
    ):
        """Map a domain-specific entity type to a unified type."""
        if kg_name not in self._entity_mappings:
            self._entity_mappings[kg_name] = {}
        self._entity_mappings[kg_name][domain_type] = unified_type

    def map_relation(
        self,
        kg_name: str,
        domain_type: str,
        unified_type: UnifiedRelationType,
    ):
        """Map a domain-specific relation type to a unified type."""
        if kg_name not in self._relation_mappings:
            self._relation_mappings[kg_name] = {}
        self._relation_mappings[kg_name][domain_type] = unified_type

    def get_entity_type(self, kg_name: str, domain_type: str) -> Optional[UnifiedEntityType]:
        """Get the unified type for a domain-specific type."""
        return self._entity_mappings.get(kg_name, {}).get(domain_type)

    def get_relation_type(self, kg_name: str, domain_type: str) -> Optional[UnifiedRelationType]:
        """Get the unified type for a domain-specific relation type."""
        return self._relation_mappings.get(kg_name, {}).get(domain_type)

    def list_mappings(self) -> dict:
        """List all type mappings."""
        return {
            "entity_mappings": {
                kg: {k: v.value for k, v in types.items()}
                for kg, types in self._entity_mappings.items()
            },
            "relation_mappings": {
                kg: {k: v.value for k, v in types.items()}
                for kg, types in self._relation_mappings.items()
            },
        }


# ──────────────────── Ontology Main Class ───────────────────────────


class UnifiedOntology:
    """Main class for unified cross-KG ontology."""

    def __init__(self):
        self._entities: dict[str, UnifiedEntity] = {}
        self._relations: dict[str, UnifiedRelation] = {}
        self._type_mapping = TypeMapping()
        self._kg_registry: dict[str, Any] = {}

    @property
    def type_mapping(self) -> TypeMapping:
        return self._type_mapping

    def register_kg(self, name: str, kg: Any):
        """Register a knowledge graph."""
        self._kg_registry[name] = kg

    def get_kg(self, name: str) -> Optional[Any]:
        """Get a registered knowledge graph."""
        return self._kg_registry.get(name)

    def list_kgs(self) -> list[str]:
        """List registered knowledge graphs."""
        return list(self._kg_registry.keys())

    def add_entity(self, entity: UnifiedEntity):
        """Add a unified entity."""
        self._entities[entity.id] = entity

    def add_relation(self, relation: UnifiedRelation):
        """Add a unified relation."""
        self._relations[relation.id] = relation

    def get_entity(self, entity_id: str) -> Optional[UnifiedEntity]:
        """Get a unified entity by ID."""
        return self._entities.get(entity_id)

    def get_relations(self, entity_id: str) -> list[UnifiedRelation]:
        """Get all relations for an entity."""
        return [
            r for r in self._relations.values()
            if r.source == entity_id or r.target == entity_id
        ]

    def find_entities(
        self,
        entity_type: Optional[UnifiedEntityType] = None,
        label: Optional[str] = None,
        source_kg: Optional[str] = None,
    ) -> list[UnifiedEntity]:
        """Find entities with optional filters."""
        results = []

        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            if label and label.lower() not in entity.label.lower():
                continue
            if source_kg and entity.source_kg != source_kg:
                continue
            results.append(entity)

        return results

    def find_relations(
        self,
        relation_type: Optional[UnifiedRelationType] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
    ) -> list[UnifiedRelation]:
        """Find relations with optional filters."""
        results = []

        for relation in self._relations.values():
            if relation_type and relation.relation_type != relation_type:
                continue
            if source and relation.source != source:
                continue
            if target and relation.target != target:
                continue
            results.append(relation)

        return results

    def map_domain_entity(
        self,
        kg_name: str,
        domain_type: str,
        label: str,
        properties: dict = None,
        source_id: str = "",
    ) -> UnifiedEntity:
        """Map a domain entity to unified entity."""
        unified_type = self._type_mapping.get_entity_type(kg_name, domain_type)
        if not unified_type:
            unified_type = UnifiedEntityType.CONCEPT  # Default fallback

        return UnifiedEntity(
            id=f"{kg_name}:{domain_type}:{source_id}",
            entity_type=unified_type,
            label=label,
            properties=properties or {},
            source_kg=kg_name,
            source_id=source_id,
        )

    def map_domain_relation(
        self,
        kg_name: str,
        domain_type: str,
        source: str,
        target: str,
        properties: dict = None,
    ) -> UnifiedRelation:
        """Map a domain relation to unified relation."""
        unified_type = self._type_mapping.get_relation_type(kg_name, domain_type)
        if not unified_type:
            unified_type = UnifiedRelationType.INFLUENCES  # Default fallback

        return UnifiedRelation(
            id=f"{kg_name}:{domain_type}:{source}:{target}",
            relation_type=unified_type,
            source=source,
            target=target,
            properties=properties or {},
            source_kg=kg_name,
        )

    def get_stats(self) -> dict[str, int]:
        """Get ontology statistics."""
        return {
            "entities": len(self._entities),
            "relations": len(self._relations),
            "registered_kgs": len(self._kg_registry),
        }

    def export_json(self, output_path: str):
        """Export ontology to JSON."""
        import json

        data = {
            "entities": [e.to_dict() for e in self._entities.values()],
            "relations": [r.to_dict() for r in self._relations.values()],
            "type_mappings": self._type_mapping.list_mappings(),
            "stats": self.get_stats(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def import_json(self, input_path: str):
        """Import ontology from JSON."""
        import json

        with open(input_path) as f:
            data = json.load(f)

        for entity_data in data.get("entities", []):
            entity = UnifiedEntity(
                id=entity_data["id"],
                entity_type=UnifiedEntityType(entity_data["type"]),
                label=entity_data["label"],
                properties=entity_data.get("properties", {}),
                source_kg=entity_data.get("source_kg", ""),
                source_id=entity_data.get("source_id", ""),
                confidence=entity_data.get("confidence", 1.0),
            )
            self.add_entity(entity)

        for relation_data in data.get("relations", []):
            relation = UnifiedRelation(
                id=relation_data["id"],
                relation_type=UnifiedRelationType(relation_data["type"]),
                source=relation_data["source"],
                target=relation_data["target"],
                properties=relation_data.get("properties", {}),
                source_kg=relation_data.get("source_kg", ""),
                confidence=relation_data.get("confidence", 1.0),
            )
            self.add_relation(relation)


# ─────────────────────── Cross-KG Query ──────────────────────────────


class CrossKGQuery:
    """Query engine for cross-KG queries."""

    def __init__(self, ontology: UnifiedOntology):
        self.ontology = ontology

    def find(
        self,
        source_type: str,
        relation_type: str,
        target_type: str,
        filters: Optional[dict] = None,
    ) -> list[dict]:
        """Find relations matching the pattern."""
        results = []

        # Get unified types
        unified_rel = UnifiedRelationType(relation_type)

        # Find matching relations
        for relation in self.ontology.find_relations(relation_type=unified_rel):
            source = self.ontology.get_entity(relation.source)
            target = self.ontology.get_entity(relation.target)

            if not source or not target:
                continue

            # Check types
            if source_type != "*" and source.entity_type.value != source_type:
                continue
            if target_type != "*" and target.entity_type.value != target_type:
                continue

            # Apply filters
            if filters:
                match = True
                for key, value in filters.items():
                    if source.properties.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            results.append({
                "source": source.to_dict(),
                "relation": relation.to_dict(),
                "target": target.to_dict(),
            })

        return results

    def find_by_label(self, label: str) -> list[UnifiedEntity]:
        """Find entities by label."""
        return self.ontology.find_entities(label=label)

    def find_by_type(self, entity_type: str) -> list[UnifiedEntity]:
        """Find entities by type."""
        unified_type = UnifiedEntityType(entity_type)
        return self.ontology.find_entities(entity_type=unified_type)

    def get_network(self, entity_id: str, depth: int = 2) -> dict:
        """Get relationship network for an entity."""
        visited = set()
        network = {"nodes": [], "edges": []}

        def _explore(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited:
                return

            visited.add(current_id)

            entity = self.ontology.get_entity(current_id)
            if entity:
                network["nodes"].append(entity.to_dict())

            relations = self.ontology.get_relations(current_id)
            for rel in relations:
                network["edges"].append(rel.to_dict())
                next_id = rel.target if rel.source == current_id else rel.source
                _explore(next_id, current_depth + 1)

        _explore(entity_id, 0)
        return network


# ──────────────────── Temporal Reasoning ─────────────────────────────


class TemporalReasoning:
    """Temporal reasoning over the ontology."""

    @staticmethod
    def is_valid_at(entity: UnifiedEntity, timestamp: str) -> bool:
        """Check if an entity is valid at a given timestamp."""
        if entity.valid_from and timestamp < entity.valid_from:
            return False
        if entity.valid_to and timestamp > entity.valid_to:
            return False
        return True

    @staticmethod
    def is_active_at(relation: UnifiedRelation, timestamp: str) -> bool:
        """Check if a relation is active at a given timestamp."""
        if relation.valid_from and timestamp < relation.valid_from:
            return False
        if relation.valid_to and timestamp > relation.valid_to:
            return False
        return True

    @staticmethod
    def find_at(
        ontology: UnifiedOntology,
        entity_type: UnifiedEntityType,
        timestamp: str,
    ) -> list[UnifiedEntity]:
        """Find entities valid at a timestamp."""
        results = []
        for entity in ontology.find_entities(entity_type=entity_type):
            if TemporalReasoning.is_valid_at(entity, timestamp):
                results.append(entity)
        return results

    @staticmethod
    def find_relations_at(
        ontology: UnifiedOntology,
        relation_type: UnifiedRelationType,
        timestamp: str,
    ) -> list[UnifiedRelation]:
        """Find relations active at a timestamp."""
        results = []
        for relation in ontology.find_relations(relation_type=relation_type):
            if TemporalReasoning.is_active_at(relation, timestamp):
                results.append(relation)
        return results


# ──────────────────── Confidence Scoring ─────────────────────────────


class ConfidenceScoring:
    """Confidence scoring and provenance tracking."""

    @staticmethod
    def calculate_aggregate(confidences: list[float]) -> float:
        """Calculate aggregate confidence from multiple sources."""
        if not confidences:
            return 0.0
        # Use harmonic mean for conservative estimate
        n = len(confidences)
        harmonic_mean = n / sum(1 / max(c, 0.001) for c in confidences)
        return min(1.0, harmonic_mean)

    @staticmethod
    def update_confidence(
        entity: UnifiedEntity,
        new_confidence: float,
        source: str,
    ):
        """Update entity confidence with new evidence."""
        # Weighted average favoring higher confidence
        old_weight = entity.confidence
        new_weight = new_confidence
        entity.confidence = (old_weight + new_weight) / 2
        entity.provenance += f";{source}"
