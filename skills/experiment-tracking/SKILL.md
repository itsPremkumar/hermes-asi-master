# experiment-tracking/SKILL.md

A/B testing and variant analysis for agent behaviors.

## Usage

```python
from hermes_asi_master.experiments import Experiment

exp = Experiment("prompt_v2_vs_v1")
exp.add_control(prompt_template="v1")
exp.add_variant(prompt_template="v2", weight=0.5)
result = await exp.run(sample_size=200)
```
