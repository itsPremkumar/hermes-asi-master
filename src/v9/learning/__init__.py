"""
v9 STAGE 5: Engineering Learning System.

Modules:
- trajectory_store.py: Store and query execution trajectories
- skill_forge.py: Forge skills from successful trajectories
- capability_graph.py: Map agent capabilities and dependencies
- curriculum.py: Generate learning curricula
- failure_model.py: Model and predict failures
"""

from .trajectory_store import TrajectoryStore, Trajectory, TrajectoryStep
from .skill_forge import SkillForge, ForgedSkill
from .capability_graph import CapabilityGraph, CapabilityNode, Edge
from .curriculum import CurriculumGenerator, LearningModule
from .failure_model import FailureModel, FailurePrediction

__version__ = "1.0.0"
__all__ = [
    "TrajectoryStore",
    "Trajectory",
    "TrajectoryStep",
    "SkillForge",
    "ForgedSkill",
    "CapabilityGraph",
    "CapabilityNode",
    "Edge",
    "Curriculum",
    "LearningModule",
    "FailureModel",
    "FailurePrediction",
]
