# pipeline-builder/SKILL.md

Construct multi-stage execution pipelines with branching and conditions.

## Usage

```python
from hermes_asi_master.pipeline import Pipeline

pipe = Pipeline("deploy")
pipe.add_stage("test", action=run_tests)
pipe.add_stage("build", action=build_image, depends_on=["test"])
pipe.add_stage("deploy", action=deploy_prod, depends_on=["build"])
result = await pipe.execute()
```
