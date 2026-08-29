# task-decomposition/SKILL.md

Break complex goals into executable dependency graphs.

## Usage

```python
from hermes_asi_master.planner import TaskDecomposer

decomposer = TaskDecomposer()
graph = await decomposer.decompose(
    goal="Deploy microservice with monitoring",
    context={"environment": "production"}
)
```
