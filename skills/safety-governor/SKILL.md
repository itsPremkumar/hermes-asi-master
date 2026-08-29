# safety-governor/SKILL.md

Enforce policy constraints on all agent actions with audit trails.

## Usage

```python
from hermes_asi_master.safety import SafetyGovernor

gov = SafetyGovernor(policy_file="config/safety.yaml")
result = await gov.evaluate(action={"tool": "shell", "command": "ls"})
if result.approved:
    execute(action)
```
