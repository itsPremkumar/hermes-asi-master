# memory-management/SKILL.md

Long-term storage, retrieval, and pruning of agent memory.

## Usage

```python
from hermes_asi_master.memory import MemoryManager

mm = MemoryManager()
await mm.store(key="episode:123", data={...}, memory_type="episodic")
results = await mm.retrieve(query="recent failures", limit=10)
await mm.prune(older_than=timedelta(days=90))
```
