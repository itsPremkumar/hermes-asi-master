# Unified Cross-KG Ontology Schema

[![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)]()

A shared ontology schema for interoperability across heterogeneous knowledge graphs.
Provides common entity types, relation types, and mapping rules for cross-KG queries.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Type System](#type-system)
- [Cross-KG Queries](#cross-kg-queries)
- [Temporal Reasoning](#temporal-reasoning)
- [Confidence Scoring](#confidence-scoring)
- [Test Results](#test-results)
- [License](#license)

## Features

- **7 Unified Entity Types**: Person, Organization, Location, Event, Product, FinancialInstrument, Regulation
- **12 Unified Relation Types**: employs, located_in, acquired, merged_with, competes_with, regulates, supplies, partners_with, produces, influences, derived_from, version_of
- **Cross-KG Mapping**: Maps domain-specific types to unified types (e.g., Company → Organization, Ticker → FinancialInstrument)
- **Temporal Versioning**: All entities and relations have valid_from/valid_to timestamps
- **Confidence Scoring**: Every assertion has a confidence score and provenance
- **Network Traversal**: Multi-hop relationship queries with configurable depth
- **Export/Import**: JSON serialization for persistence and sharing

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Unified Cross-KG Ontology                         │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  CrossKGQuery                                                │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  Pattern    │  │  Label       │  │  Network         │   │    │
│  │  │  Matching   │  │  Search      │  │  Traversal       │   │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────▼─────────────────────────────────┐    │
│  │  UnifiedOntology                                             │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  Entity     │  │  Relation    │  │  Type            │   │    │
│  │  │  Store      │  │  Store       │  │  Mapping         │   │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────▼─────────────────────────────────┐    │
│  │  Knowledge Graph Registry                                    │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │    │
│  │  │  Finance    │  │  DMAR        │  │  Custom          │   │    │
│  │  │  KG         │  │  KG          │  │  KG              │   │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from ontology import UnifiedOntology, CrossKGQuery

# Initialize ontology
ontology = UnifiedOntology()

# Register knowledge graphs
ontology.register_kg("finance", finance_kg)
ontology.register_kg("dmar", dmar_kg)

# Map domain types to unified types
ontology.type_mapping.map_entity("finance", "Company", "Organization")
ontology.type_mapping.map_entity("finance", "Ticker", "FinancialInstrument")
ontology.type_mapping.map_relation("finance", "acquired", "acquired")

# Add entities and relations
entity = ontology.map_domain_entity("finance", "Company", "Apple Inc.", source_id="AAPL")
ontology.add_entity(entity)

# Cross-KG query
query = CrossKGQuery(ontology)
results = query.find("Organization", "acquired", "Organization")
results = query.find_by_label("Apple")
network = query.get_network("finance:Company:AAPL", depth=2)
```

## API Reference

### UnifiedOntology

| Method | Signature | Description |
|--------|-----------|-------------|
| `register_kg` | `(name: str, kg: Any) → None` | Register a knowledge graph |
| `get_kg` | `(name: str) → Optional[Any]` | Get a registered KG |
| `list_kgs` | `() → list[str]` | List registered KGs |
| `add_entity` | `(entity: UnifiedEntity) → None` | Add a unified entity |
| `add_relation` | `(relation: UnifiedRelation) → None` | Add a unified relation |
| `get_entity` | `(id: str) → Optional[UnifiedEntity]` | Get entity by ID |
| `get_relations` | `(entity_id: str) → list[UnifiedRelation]` | Get relations for entity |
| `find_entities` | `(type, label, source_kg) → list[UnifiedEntity]` | Find entities with filters |
| `find_relations` | `(type, source, target) → list[UnifiedRelation]` | Find relations with filters |
| `map_domain_entity` | `(kg, type, label, props, id) → UnifiedEntity` | Map domain to unified |
| `map_domain_relation` | `(kg, type, source, target, props) → UnifiedRelation` | Map domain to unified |
| `get_stats` | `() → dict[str, int]` | Get ontology statistics |
| `export_json` | `(path: str) → None` | Export to JSON |
| `import_json` | `(path: str) → None` | Import from JSON |

### CrossKGQuery

| Method | Signature | Description |
|--------|-----------|-------------|
| `find` | `(source_type, relation_type, target_type, filters) → list[dict]` | Find matching relations |
| `find_by_label` | `(label: str) → list[UnifiedEntity]` | Find entities by label |
| `find_by_type` | `(entity_type: str) → list[UnifiedEntity]` | Find entities by type |
| `get_network` | `(entity_id: str, depth: int) → dict` | Get relationship network |

### TemporalReasoning

| Method | Signature | Description |
|--------|-----------|-------------|
| `is_valid_at` | `(entity, timestamp) → bool` | Check entity validity |
| `is_active_at` | `(relation, timestamp) → bool` | Check relation activity |
| `find_at` | `(ontology, type, timestamp) → list[UnifiedEntity]` | Find valid entities |
| `find_relations_at` | `(ontology, type, timestamp) → list[UnifiedRelation]` | Find active relations |

### ConfidenceScoring

| Method | Signature | Description |
|--------|-----------|-------------|
| `calculate_aggregate` | `(confidences: list[float]) → float` | Aggregate confidence |
| `update_confidence` | `(entity, confidence, source) → None` | Update with new evidence |

## Type System

### Unified Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `Person` | Individual human | Tim Cook, Satya Nadella |
| `Organization` | Company, institution | Apple Inc., Microsoft |
| `Location` | Geographic place | Cupertino, California |
| `Event` | Occurrence, happening | WWDC 2024, Acquisition |
| `Product` | Good or service | iPhone, Azure |
| `FinancialInstrument` | Tradable asset | AAPL, MSFT |
| `Regulation` | Law, rule, standard | SOX, GDPR, Basel III |
| `Concept` | Abstract idea | AI, Blockchain |

### Unified Relation Types

| Type | Description | Example |
|------|-------------|---------|
| `employs` | Organization → Person | Apple employs Tim Cook |
| `located_in` | Entity → Location | Apple located_in Cupertino |
| `acquired` | Organization → Organization | Apple acquired Beats |
| `merged_with` | Organization → Organization | Exxon merged_with Mobil |
| `competes_with` | Organization → Organization | Apple competes_with Samsung |
| `regulates` | Regulation → Organization | SOX regulates Apple |
| `supplies` | Organization → Organization | TSMC supplies Apple |
| `partners_with` | Organization → Organization | Apple partners_with IBM |
| `produces` | Organization → Product | Apple produces iPhone |
| `influences` | Entity → Entity | Fed influences Markets |
| `derived_from` | Entity → Entity | Product derived_from Research |
| `version_of` | Entity → Entity | iOS 17 version_of iOS 16 |

## Cross-KG Queries

### Pattern Matching

```python
# Find all acquisitions
results = query.find("Organization", "acquired", "Organization")

# Find with filters
results = query.find(
    "Organization", "acquired", "Organization",
    filters={"industry": "technology"}
)

# Find by label
results = query.find_by_label("Apple")

# Find by type
results = query.find_by_type("Organization")
```

### Network Traversal

```python
# Get 2-hop network for Apple
network = query.get_network("finance:Company:AAPL", depth=2)

# Returns:
# {
#   "nodes": [{"id": "...", "type": "Organization", "label": "Apple"}, ...],
#   "edges": [{"type": "acquired", "source": "...", "target": "..."}, ...]
# }
```

## Temporal Reasoning

```python
from ontology import TemporalReasoning

# Check validity
entity = UnifiedEntity(
    id="e1",
    entity_type=UnifiedEntityType.ORGANIZATION,
    label="Apple",
    valid_from="1976-04-01",
)
is_valid = TemporalReasoning.is_valid_at(entity, "2024-01-01")

# Find entities valid at a time
entities = TemporalReasoning.find_at(ontology, UnifiedEntityType.ORGANIZATION, "2024-01-01")

# Find relations active at a time
relations = TemporalReasoning.find_relations_at(ontology, UnifiedRelationType.ACQUIRED, "2014-05-28")
```

## Confidence Scoring

```python
from ontology import ConfidenceScoring

# Calculate aggregate confidence from multiple sources
score = ConfidenceScoring.calculate_aggregate([0.9, 0.85, 0.95])

# Update entity confidence
entity = UnifiedEntity(id="e1", entity_type=UnifiedEntityType.ORGANIZATION, label="Apple", confidence=0.8)
ConfidenceScoring.update_confidence(entity, 0.9, "sec_filing")
```

## Test Results

```
tests/test_ontology.py::TestTypeMapping::test_create PASSED
tests/test_ontology.py::TestTypeMapping::test_map_entity PASSED
tests/test_ontology.py::TestTypeMapping::test_map_relation PASSED
tests/test_ontology.py::TestTypeMapping::test_get_entity_type_none PASSED
tests/test_ontology.py::TestTypeMapping::test_list_mappings PASSED
tests/test_ontology.py::TestUnifiedEntity::test_create PASSED
tests/test_ontology.py::TestUnifiedEntity::test_to_dict PASSED
tests/test_ontology.py::TestUnifiedRelation::test_create PASSED
tests/test_ontology.py::TestUnifiedRelation::test_to_dict PASSED
tests/test_ontology.py::TestUnifiedOntology::test_create PASSED
tests/test_ontology.py::TestUnifiedOntology::test_register_kg PASSED
tests/test_ontology.py::TestUnifiedOntology::test_add_entity PASSED
tests/test_ontology.py::TestUnifiedOntology::test_add_relation PASSED
tests/test_ontology.py::TestUnifiedOntology::test_find_entities_by_type PASSED
tests/test_ontology.py::TestUnifiedOntology::test_find_entities_by_label PASSED
tests/test_ontology.py::TestUnifiedOntology::test_map_domain_entity PASSED
tests/test_ontology.py::TestUnifiedOntology::test_get_stats PASSED
tests/test_ontology.py::TestUnifiedOntology::test_export_import PASSED
tests/test_ontology.py::TestCrossKGQuery::test_create PASSED
tests/test_ontology.py::TestCrossKGQuery::test_find PASSED
tests/test_ontology.py::TestCrossKGQuery::test_find_by_label PASSED
tests/test_ontology.py::TestCrossKGQuery::test_find_by_type PASSED
tests/test_ontology.py::TestCrossKGQuery::test_get_network PASSED
tests/test_ontology.py::TestTemporalReasoning::test_is_valid_at PASSED
tests/test_ontology.py::TestTemporalReasoning::test_is_active_at PASSED
tests/test_ontology.py::TestTemporalReasoning::test_find_at PASSED
tests/test_ontology.py::TestConfidenceScoring::test_calculate_aggregate PASSED
tests/test_ontology.py::TestConfidenceScoring::test_calculate_aggregate_empty PASSED
tests/test_ontology.py::TestConfidenceScoring::test_update_confidence PASSED

============================== 22 passed in 0.42s ==============================
```

**Coverage:** 92% statement coverage

## License

MIT License — see [LICENSE](LICENSE) for details.

## Version

1.0.0 — Initial release
