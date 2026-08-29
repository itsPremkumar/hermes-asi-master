"""
Preset definitions and loader for agentforge-x.

presets.yaml demonstrates a full six-agent fleet configuration.
"""

from __future__ import annotations
import yaml
import os
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Preset:
    """A preset configuration for fleet operations."""
    name: str
    description: str
    agents: list[str]  # Agent type names to include
    topic: str
    max_iterations: int = 3
    judge_threshold: float = 0.7
    metadata: dict[str, Any] = field(default_factory=dict)


# Default presets — these mirror what's in presets.yaml
DEFAULT_PRESETS = [
    Preset(
        name="default",
        description="Standard six-agent fleet for general tasks",
        agents=["researcher", "coder", "critic", "tester", "writer", "ops"],
        topic="General problem solving",
        max_iterations=3,
        judge_threshold=0.7,
    ),
    Preset(
        name="code-review",
        description="Code review and quality assessment fleet",
        agents=["coder", "tester", "critic"],
        topic="Code review",
        max_iterations=2,
        judge_threshold=0.8,
    ),
    Preset(
        name="research-synthesis",
        description="Deep research and synthesis fleet",
        agents=["researcher", "writer", "critic"],
        topic="Research synthesis",
        max_iterations=3,
        judge_threshold=0.75,
    ),
    Preset(
        name="full-stack",
        description="End-to-end application development fleet",
        agents=["researcher", "coder", "tester", "ops"],
        topic="Full-stack development",
        max_iterations=3,
        judge_threshold=0.7,
    ),
    Preset(
        name="documentation",
        description="Documentation and content creation fleet",
        agents=["writer", "critic", "ops"],
        topic="Documentation",
        max_iterations=2,
        judge_threshold=0.65,
    ),
    Preset(
        name="ops-deploy",
        description="Infrastructure and deployment fleet",
        agents=["ops", "coder", "tester"],
        topic="Deployment",
        max_iterations=2,
        judge_threshold=0.8,
    ),
]


def load_presets(path: Optional[str] = None) -> list[Preset]:
    """
    Load presets from a YAML file or return defaults.

    Args:
        path: Path to presets YAML file. If None, looks for presets.yaml
              in the package directory. If not found, returns DEFAULT_PRESETS.

    Returns:
        List of Preset objects.
    """
    if path is None:
        # Look in package directory
        pkg_dir = os.path.dirname(__file__)
        path = os.path.join(pkg_dir, "presets.yaml")

    if not os.path.exists(path):
        return DEFAULT_PRESETS

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    presets = []
    for preset_data in data.get("presets", []):
        preset = Preset(
            name=preset_data["name"],
            description=preset_data["description"],
            agents=preset_data["agents"],
            topic=preset_data["topic"],
            max_iterations=preset_data.get("max_iterations", 3),
            judge_threshold=preset_data.get("judge_threshold", 0.7),
            metadata=preset_data.get("metadata", {}),
        )
        presets.append(preset)

    return presets


def get_preset(name: str, path: Optional[str] = None) -> Preset:
    """Get a single preset by name."""
    presets = load_presets(path)
    for p in presets:
        if p.name == name:
            return p
    raise KeyError(f"Preset '{name}' not found. Available: {[p.name for p in presets]}")
