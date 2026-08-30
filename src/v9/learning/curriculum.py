"""
curriculum.py — Generate learning curricula.

Generates personalized learning curricula based on current capabilities
and target goals.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class LearningModule:
    """A single learning module."""
    name: str
    description: str
    capability: str
    difficulty: float  # 0.0 to 1.0
    prerequisites: list[str]
    estimated_minutes: int = 30
    completed: bool = False
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "capability": self.capability,
            "difficulty": self.difficulty,
            "prerequisites": self.prerequisites,
            "estimated_minutes": self.estimated_minutes,
            "completed": self.completed,
            "score": self.score,
        }


@dataclass
class Curriculum:
    """A complete learning curriculum."""
    name: str
    target_capability: str
    modules: list[LearningModule]
    current_module_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def current_module(self) -> Optional[LearningModule]:
        if self.current_module_index < len(self.modules):
            return self.modules[self.current_module_index]
        return None

    @property
    def progress(self) -> float:
        if not self.modules:
            return 0.0
        completed = sum(1 for m in self.modules if m.completed)
        return completed / len(self.modules)

    @property
    def total_minutes(self) -> int:
        return sum(m.estimated_minutes for m in self.modules)

    def complete_current_module(self, score: float = 1.0) -> None:
        """Mark current module as completed."""
        if self.current_module:
            self.current_module.completed = True
            self.current_module.score = score
            self.current_module_index += 1

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "target_capability": self.target_capability,
            "modules": [m.to_dict() for m in self.modules],
            "progress": self.progress,
            "total_minutes": self.total_minutes,
        }


class CurriculumGenerator:
    """
    Generator for learning curricula.

    Generates curricula based on capability graphs and current skill levels.
    """

    # Module templates for common capabilities
    MODULE_TEMPLATES = {
        "python": [
            ("Variables & Types", "Basic Python types", 0.1, []),
            ("Control Flow", "if/else, loops", 0.2, ["Variables & Types"]),
            ("Functions", "Writing functions", 0.3, ["Control Flow"]),
            ("OOP", "Classes and objects", 0.4, ["Functions"]),
            ("Modules", "Imports and packages", 0.4, ["Functions"]),
            ("Error Handling", "Exceptions", 0.5, ["Control Flow"]),
        ],
        "algorithms": [
            ("Sorting", "Sort algorithms", 0.3, []),
            ("Searching", "Search algorithms", 0.4, ["Sorting"]),
            ("Dynamic Programming", "DP patterns", 0.6, ["Searching"]),
            ("Graph Algorithms", "Graph traversal", 0.7, ["Searching"]),
            ("Greedy Algorithms", "Greedy patterns", 0.5, ["Sorting"]),
        ],
        "web": [
            ("HTML Basics", "HTML structure", 0.1, []),
            ("CSS Styling", "CSS and layouts", 0.2, ["HTML Basics"]),
            ("JavaScript", "JS fundamentals", 0.3, ["HTML Basics"]),
            ("React", "React framework", 0.5, ["JavaScript"]),
            ("Node.js", "Server-side JS", 0.5, ["JavaScript"]),
            ("Databases", "SQL and NoSQL", 0.4, []),
        ],
        "devops": [
            ("Linux CLI", "Command line basics", 0.2, []),
            ("Git", "Version control", 0.3, []),
            ("Docker", "Containerization", 0.5, ["Linux CLI"]),
            ("CI/CD", "Continuous integration", 0.6, ["Git", "Docker"]),
            ("Kubernetes", "Container orchestration", 0.8, ["Docker"]),
            ("Monitoring", "Observability", 0.7, ["Linux CLI"]),
        ],
        "ml": [
            ("Statistics", "Statistical foundations", 0.3, []),
            ("Supervised Learning", "Regression, classification", 0.5, ["Statistics"]),
            ("Unsupervised Learning", "Clustering, PCA", 0.6, ["Statistics"]),
            ("Neural Networks", "Deep learning basics", 0.7, ["Supervised Learning"]),
            ("NLP", "Natural language processing", 0.8, ["Neural Networks"]),
            ("Computer Vision", "Image processing", 0.8, ["Neural Networks"]),
        ],
    }

    def generate_curriculum(
        self,
        current_levels: dict[str, float],
        target_capability: str,
        max_modules: int = 10,
    ) -> Curriculum:
        """
        Generate a learning curriculum.

        Args:
            current_levels: Dict of capability -> mastery level (0-1)
            target_capability: The capability to learn
            max_modules: Maximum number of modules

        Returns:
            A personalized Curriculum
        """
        # Find modules for the target capability
        modules = []
        for cap_name, level in current_levels.items():
            if cap_name in self.MODULE_TEMPLATES:
                for mod_name, desc, difficulty, prereqs in self.MODULE_TEMPLATES[cap_name]:
                    if level < 0.7:  # Not yet mastered
                        module = LearningModule(
                            name=mod_name,
                            description=desc,
                            capability=cap_name,
                            difficulty=difficulty,
                            prerequisites=prereqs,
                            estimated_minutes=int(difficulty * 60),
                        )
                        modules.append(module)

        # Sort by difficulty
        modules.sort(key=lambda m: m.difficulty)

        # Limit to max_modules
        modules = modules[:max_modules]

        return Curriculum(
            name=f"Curriculum for {target_capability}",
            target_capability=target_capability,
            modules=modules,
        )

    def generate_from_capability_graph(self, graph: Any, target: str) -> Curriculum:
        """
        Generate curriculum from a capability graph.

        Uses the graph to determine prerequisites and ordering.
        """
        modules = []
        visited = set()

        def add_modules(cap_name):
            if cap_name in visited:
                return
            visited.add(cap_name)
            node = graph.get_node(cap_name)
            if node and node.level < 0.7:
                for cap_templates in self.MODULE_TEMPLATES.values():
                    for mod_name, desc, difficulty, prereqs in cap_templates:
                        if cap_name.lower() in mod_name.lower() or mod_name.lower() in cap_name.lower():
                            modules.append(LearningModule(
                                name=mod_name,
                                description=desc,
                                capability=cap_name,
                                difficulty=difficulty,
                                prerequisites=prereqs,
                                estimated_minutes=int(difficulty * 60),
                            ))

        # Add target and its prerequisites
        prereqs = graph.get_prerequisites(target)
        for prereq in prereqs:
            add_modules(prereq)
        add_modules(target)

        modules.sort(key=lambda m: m.difficulty)

        return Curriculum(
            name=f"Curriculum for {target}",
            target_capability=target,
            modules=modules,
        )
