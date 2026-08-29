# MEMORY.md — HERMES-ASI-MASTER Memory Architecture

## Overview

The HERMES-ASI-MASTER memory system provides persistent, queryable state across all agents and execution episodes. It combines multiple memory types to enable both short-term task context and long-term organizational knowledge.

## Memory Types

### 1. Working Memory
- **Scope:** Current execution episode
- **Storage:** In-memory with Redis backing
- **Retention:** Duration of task + 24h
- **Capacity:** 10K tokens per agent

### 2. Episodic Memory
- **Scope:** Historical execution episodes
- **Storage:** PostgreSQL with JSONB
- **Retention:** 90 days (configurable)
- **Indexing:** Full-text search + vector embeddings

### 3. Semantic Memory
- **Scope:** Facts, concepts, relationships
- **Storage:** Vector database (pgvector)
- **Retention:** Indefinite with versioning
- **Indexing:** HNSW vector index

### 4. Procedural Memory
- **Scope:** Skills, routines, workflows
- **Storage:** File system + Git
- **Retention:** Indefinite with version history
- **Indexing:** Metadata tags + content hash

### 5. Prospective Memory
- **Scope:** Scheduled tasks, reminders, deadlines
- **Storage:** Cron + priority queue
- **Retention:** Until triggered + 30 days
- **Indexing:** Time-based + priority

## Memory Operations

### Store
```python
await memory.store(
    key="episode:12345",
    data={"outcome": "success", "metrics": {...}},
    memory_type="episodic",
    ttl=7776000  # 90 days
)
```

### Retrieve
```python
results = await memory.retrieve(
    query="deployment failures last week",
    memory_type="episodic",
    limit=10,
    min_relevance=0.7
)
```

### Prune
```python
deleted = await memory.prune(
    memory_type="episodic",
    older_than=timedelta(days=90),
    strategy="lru"
)
```

## Memory Governance

- **Privacy:** No PII stored without encryption
- **Retention:** Automatic pruning per policy
- **Access:** Role-based read/write permissions
- **Audit:** All access logged immutably
- **Backup:** Daily snapshots with 30-day retention

## Configuration

```yaml
# config/system.yaml
memory:
  working:
    backend: redis
    max_tokens: 10000
  episodic:
    backend: postgresql
    retention_days: 90
  semantic:
    backend: pgvector
    embedding_model: text-embedding-3-large
    dimensions: 3072
  procedural:
    backend: filesystem
    path: ./memory/procedural
  prospective:
    backend: cron
    store: redis
```
