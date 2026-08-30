"""Tests for curriculum.py."""

import pytest
from v9.learning.curriculum import CurriculumGenerator, LearningModule, Curriculum


class TestLearningModule:
    """Tests for LearningModule."""

    def test_module_fields(self):
        module = LearningModule(
            name="Test",
            description="Test module",
            capability="python",
            difficulty=0.5,
            prerequisites=[],
        )
        assert module.name == "Test"
        assert module.difficulty == 0.5
        assert module.completed is False

    def test_module_to_dict(self):
        module = LearningModule(
            name="Test",
            description="Test",
            capability="python",
            difficulty=0.5,
            prerequisites=[],
        )
        d = module.to_dict()
        assert d["name"] == "Test"


class TestCurriculum:
    """Tests for Curriculum dataclass."""

    def test_curriculum_fields(self):
        curr = Curriculum(
            name="Test",
            target_capability="python",
            modules=[],
        )
        assert curr.name == "Test"
        assert curr.target_capability == "python"

    def test_progress_empty(self):
        curr = Curriculum(name="T", target_capability="p", modules=[])
        assert curr.progress == 0.0

    def test_progress_partial(self):
        curr = Curriculum(
            name="T",
            target_capability="p",
            modules=[
                LearningModule(name="L1", description="", capability="p", difficulty=0.1, prerequisites=[], completed=True),
                LearningModule(name="L2", description="", capability="p", difficulty=0.2, prerequisites=[], completed=False),
            ],
        )
        assert curr.progress == 0.5

    def test_current_module(self):
        curr = Curriculum(
            name="T",
            target_capability="p",
            modules=[
                LearningModule(name="L1", description="", capability="p", difficulty=0.1, prerequisites=[]),
                LearningModule(name="L2", description="", capability="p", difficulty=0.2, prerequisites=[]),
            ],
        )
        assert curr.current_module is not None
        assert curr.current_module.name == "L1"

    def test_complete_current_module(self):
        curr = Curriculum(
            name="T",
            target_capability="p",
            modules=[
                LearningModule(name="L1", description="", capability="p", difficulty=0.1, prerequisites=[]),
                LearningModule(name="L2", description="", capability="p", difficulty=0.2, prerequisites=[]),
            ],
        )
        curr.complete_current_module(score=0.9)
        assert curr.modules[0].completed is True
        assert curr.modules[0].score == 0.9
        assert curr.current_module_index == 1


class TestCurriculumGenerator:
    """Tests for CurriculumGenerator."""

    def test_generate_curriculum(self):
        gen = CurriculumGenerator()
        levels = {"python": 0.5, "algorithms": 0.3}
        curr = gen.generate_curriculum(levels, "algorithms")
        assert isinstance(curr, Curriculum)
        assert curr.target_capability == "algorithms"

    def test_generate_respects_max_modules(self):
        gen = CurriculumGenerator()
        levels = {"python": 0.1, "web": 0.1, "devops": 0.1, "ml": 0.1}
        curr = gen.generate_curriculum(levels, "ml", max_modules=5)
        assert len(curr.modules) <= 5

    def test_generate_sorts_by_difficulty(self):
        gen = CurriculumGenerator()
        levels = {"python": 0.3}
        curr = gen.generate_curriculum(levels, "python")
        difficulties = [m.difficulty for m in curr.modules]
        assert difficulties == sorted(difficulties)

    def test_generate_from_capability_graph(self):
        from v9.learning.capability_graph import CapabilityGraph, CapabilityNode
        gen = CurriculumGenerator()
        graph = CapabilityGraph()
        graph.add_node(CapabilityNode(name="python", description="", level=0.3))
        curr = gen.generate_from_capability_graph(graph, "python")
        assert isinstance(curr, Curriculum)
        assert curr.target_capability == "python"

    def test_module_templates_exist(self):
        gen = CurriculumGenerator()
        assert "python" in gen.MODULE_TEMPLATES
        assert "algorithms" in gen.MODULE_TEMPLATES
