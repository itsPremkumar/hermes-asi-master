# episodic-recall/SKILL.md

Query past execution episodes with natural language.

## Usage

```python
from hermes_asi_master.memory import EpisodicStore

store = EpisodicStore()
episodes = await store.search("deployment that failed last Tuesday")
recent = await store.get_recent(n=5, agent="operator")
```
