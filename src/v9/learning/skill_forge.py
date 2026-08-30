"""
skill_forge.py — Forge skills from successful trajectories.

Analyzes successful trajectories to extract reusable skills.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import re


@dataclass
class ForgedSkill:
    """A skill forged from trajectories."""
    name: str
    description: str
    steps: list[str]
    preconditions: list[str]
    postconditions: list[str]
    success_rate: float = 0.0
    source_trajectory_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "success_rate": self.success_rate,
            "source_trajectory_ids": self.source_trajectory_ids,
            "tags": self.tags,
        }


class SkillForge:
    """
    Forge skills from successful trajectories.

    Analyzes trajectories to extract reusable patterns.
    """

    def __init__(self):
        self.skills: dict[str, ForgedSkill] = {}

    def forge_from_trajectories(
        self,
        trajectories: list[Any],
        min_success_rate: float = 0.7,
    ) -> list[ForgedSkill]:
        """
        Forge skills from a list of trajectories.

        Args:
            trajectories: List of Trajectory objects
            min_success_rate: Minimum success rate to consider

        Returns:
            List of forged skills
        """
        skills = []
        for traj in trajectories:
            if traj.success_rate >= min_success_rate:
                skill = self._extract_skill(traj)
                if skill:
                    skills.append(skill)
                    self.skills[skill.name] = skill
        return skills

    def _extract_skill(self, trajectory: Any) -> Optional[ForgedSkill]:
        """Extract a skill from a single trajectory."""
        if not trajectory.steps:
            return None

        # Extract actions as steps
        steps = []
        for step in trajectory.steps:
            if step.success and step.action:
                steps.append(step.action)

        if not steps:
            return None

        # Extract tags from task
        tags = self._extract_tags(trajectory.task)

        # Generate skill name
        name = self._generate_skill_name(trajectory.task)

        # Extract preconditions and postconditions
        preconditions = self._extract_preconditions(trajectory)
        postconditions = self._extract_postconditions(trajectory)

        return ForgedSkill(
            name=name,
            description=f"Skill for: {trajectory.task}",
            steps=steps,
            preconditions=preconditions,
            postconditions=postconditions,
            success_rate=trajectory.success_rate,
            source_trajectory_ids=[trajectory.trajectory_id],
            tags=tags,
            metadata={"task": trajectory.task},
        )

    def _extract_tags(self, task: str) -> list[str]:
        """Extract tags from a task description."""
        tags = []
        task_lower = task.lower()
        tag_keywords = {
            "code": ["code", "implement", "function", "class", "algorithm", "program"],
            "debug": ["debug", "fix", "error", "bug", "issue", "problem"],
            "test": ["test", "verify", "validate", "check", "assert"],
            "deploy": ["deploy", "release", "ship", "publish", "distribute"],
            "data": ["data", "parse", "transform", "process", "extract", "load"],
            "api": ["api", "endpoint", "request", "response", "http", "rest"],
            "ui": ["ui", "interface", "design", "layout", "style", "css"],
            "db": ["database", "sql", "query", "schema", "table", "mongo"],
            "auth": ["auth", "login", "token", "permission", "security"],
            "research": ["research", "find", "search", "analyze", "investigate"],
            "write": ["write", "document", "create", "draft", "compose"],
            "optimize": ["optimize", "performance", "speed", "cache", "improve"],
        }
        for tag, keywords in tag_keywords.items():
            if any(kw in task_lower for kw in keywords):
                tags.append(tag)
        return tags or ["general"]

    def _generate_skill_name(self, task: str) -> str:
        """Generate a skill name from a task description."""
        words = task.lower().split()[:5]
        name = "-".join(re.findall(r'[a-z]+', " ".join(words)))
        return name or "unnamed-skill"

    def _extract_preconditions(self, trajectory: Any) -> list[str]:
        """Extract preconditions from a trajectory."""
        preconditions = []
        if trajectory.steps:
            first_step = trajectory.steps[0]
            if first_step.observation:
                preconditions.append(f"Initial state: {first_step.observation[:100]}")
        return preconditions or ["No specific preconditions"]

    def _extract_postconditions(self, trajectory: Any) -> list[str]:
        """Extract postconditions from a trajectory."""
        postconditions = []
        if trajectory.steps:
            last_step = trajectory.steps[-1]
            if last_step.result:
                postconditions.append(f"Final result: {last_step.result[:100]}")
        if trajectory.success:
            postconditions.append("Task completed successfully")
        return postconditions or ["No specific postconditions"]

    def get_skill(self, name: str) -> Optional[ForgedSkill]:
        """Get a skill by name."""
        return self.skills.get(name)

    def find_skills_by_tag(self, tag: str) -> list[ForgedSkill]:
        """Find skills by tag."""
        return [s for s in self.skills.values() if tag in s.tags]

    def list_skills(self) -> list[ForgedSkill]:
        """List all forged skills."""
        return list(self.skills.values())

    def merge_skills(self, skill1: ForgedSkill, skill2: ForgedSkill) -> ForgedSkill:
        """Merge two similar skills."""
        merged_steps = list(skill1.steps)
        for step in skill2.steps:
            if step not in merged_steps:
                merged_steps.append(step)

        return ForgedSkill(
            name=f"{skill1.name}-{skill2.name}",
            description=f"Merged: {skill1.description} + {skill2.description}",
            steps=merged_steps,
            preconditions=list(set(skill1.preconditions + skill2.preconditions)),
            postconditions=list(set(skill1.postconditions + skill2.postconditions)),
            success_rate=(skill1.success_rate + skill2.success_rate) / 2,
            source_trajectory_ids=skill1.source_trajectory_ids + skill2.source_trajectory_ids,
            tags=list(set(skill1.tags + skill2.tags)),
        )
