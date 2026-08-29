# agent-lifecycle/SKILL.md

Spawn, suspend, resume, and retire agents with full state management.

## Usage

```python
from hermes_asi_master.lifecycle import AgentLifecycle

lifecycle = AgentLifecycle()
agent = await lifecycle.spawn(role="researcher", config={})
await lifecycle.suspend(agent.id)
await lifecycle.resume(agent.id)
await lifecycle.retire(agent.id, persist_state=True)
```
