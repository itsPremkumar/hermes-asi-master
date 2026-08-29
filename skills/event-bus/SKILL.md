# event-bus/SKILL.md

Centralized event streaming with subscription filtering and replay.

## Usage

```python
from hermes_asi_master.events import EventBus

bus = EventBus()
await bus.publish("task.completed", {"task_id": "123"})
bus.subscribe("task.*", handler=metrics_handler)
```
