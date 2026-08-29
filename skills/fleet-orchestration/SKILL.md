# fleet-orchestration/SKILL.md

Deploy, scale, and manage agent fleets across distributed environments.

## Usage

```python
from hermes_asi_master.fleet import FleetManager

manager = FleetManager(config="config/agents.yaml")
await manager.scale("researcher", instances=5)
```

## Capabilities

- Horizontal auto-scaling based on queue depth
- Rolling deployments with zero downtime
- Agent health monitoring and self-healing
- Load balancing across regions
