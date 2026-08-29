"""Tests for the CurriculumEngine module."""

import pytest
from phase7.curriculum import CurriculumEngine, LearningPath, Lesson


class TestLesson:
    """Tests for the Lesson dataclass."""

    def test_lesson_fields(self):
        lesson = Lesson(
            name="Test Lesson",
            description="A test lesson",
            skill_name="test-skill",
            difficulty=0.5,
            prerequisites=[],
        )
        assert lesson.name == "Test Lesson"
        assert lesson.difficulty == 0.5
        assert lesson.completed is False
        assert lesson.score == 0.0

    def test_lesson_to_dict(self):
        lesson = Lesson(
            name="Test",
            description="Desc",
            skill_name="skill",
            difficulty=0.3,
            prerequisites=[],
        )
        d = lesson.to_dict()
        assert d["name"] == "Test"
        assert d["difficulty"] == 0.3


class TestLearningPath:
    """Tests for the LearningPath dataclass."""

    def test_learning_path_fields(self):
        path = LearningPath(
            name="Test Path",
            target_skill="python",
            lessons=[],
        )
        assert path.name == "Test Path"
        assert path.target_skill == "python"
        assert path.completed is False

    def test_learning_path_progress_empty(self):
        path = LearningPath(name="Test", target_skill="skill", lessons=[])
        assert path.progress == 0.0

    def test_learning_path_progress_partial(self):
        path = LearningPath(
            name="Test",
            target_skill="skill",
            lessons=[
                Lesson(name="L1", description="", skill_name="s", difficulty=0.1, prerequisites=[], completed=True),
                Lesson(name="L2", description="", skill_name="s", difficulty=0.2, prerequisites=[], completed=False),
            ],
        )
        assert path.progress == 0.5

    def test_learning_path_current_lesson(self):
        path = LearningPath(
            name="Test",
            target_skill="skill",
            lessons=[
                Lesson(name="L1", description="", skill_name="s", difficulty=0.1, prerequisites=[]),
                Lesson(name="L2", description="", skill_name="s", difficulty=0.2, prerequisites=[]),
            ],
        )
        assert path.current_lesson is not None
        assert path.current_lesson.name == "L1"

    def test_learning_path_next_lesson(self):
        path = LearningPath(
            name="Test",
            target_skill="skill",
            lessons=[
                Lesson(name="L1", description="", skill_name="s", difficulty=0.1, prerequisites=[]),
                Lesson(name="L2", description="", skill_name="s", difficulty=0.2, prerequisites=[]),
            ],
        )
        path.current_lesson_index = 0
        next_l = path.next_lesson
        assert next_l is not None
        assert next_l.name == "L2"

    def test_learning_path_complete_current_lesson(self):
        path = LearningPath(
            name="Test",
            target_skill="skill",
            lessons=[
                Lesson(name="L1", description="", skill_name="s", difficulty=0.1, prerequisites=[]),
                Lesson(name="L2", description="", skill_name="s", difficulty=0.2, prerequisites=[]),
            ],
        )
        path.complete_current_lesson(score=0.9)
        assert path.lessons[0].completed is True
        assert path.lessons[0].score == 0.9
        assert path.current_lesson_index == 1

    def test_learning_path_complete_all_lessons(self):
        path = LearningPath(
            name="Test",
            target_skill="skill",
            lessons=[
                Lesson(name="L1", description="", skill_name="s", difficulty=0.1, prerequisites=[]),
            ],
        )
        path.complete_current_lesson(score=1.0)
        assert path.completed is True

    def test_learning_path_to_dict(self):
        path = LearningPath(
            name="Test",
            target_skill="skill",
            lessons=[Lesson(name="L1", description="d", skill_name="s", difficulty=0.1, prerequisites=[])],
        )
        d = path.to_dict()
        assert d["name"] == "Test"
        assert len(d["lessons"]) == 1


class TestCurriculumEngine:
    """Tests for the CurriculumEngine class."""

    def test_generate_path_basic(self):
        engine = CurriculumEngine()
        path = engine.generate_path([], "python-basics")
        assert isinstance(path, LearningPath)
        assert path.target_skill == "python-basics"
        assert len(path.lessons) > 0

    def test_generate_path_with_current_skills(self):
        engine = CurriculumEngine()
        path = engine.generate_path(["python-basics"], "data-structures")
        assert path.target_skill == "data-structures"
        # Should not include python-basics lessons since already known
        lesson_names = [l.name for l in path.lessons]
        assert all("Variables" not in name for name in lesson_names)

    def test_generate_path_respects_max_lessons(self):
        engine = CurriculumEngine()
        path = engine.generate_path([], "system-design", max_lessons=5)
        assert len(path.lessons) <= 5

    def test_generate_path_includes_prerequisites(self):
        engine = CurriculumEngine()
        path = engine.generate_path([], "data-structures")
        # Should include python-basics prerequisites
        skill_names = set(l.skill_name for l in path.lessons)
        assert "python-basics" in skill_names

    def test_generate_path_sorted_by_difficulty(self):
        engine = CurriculumEngine()
        path = engine.generate_path([], "python-basics")
        difficulties = [l.difficulty for l in path.lessons]
        assert difficulties == sorted(difficulties)

    def test_get_skill_level_no_lessons(self):
        engine = CurriculumEngine()
        level = engine.get_skill_level("python-basics", [])
        assert level == 0.0

    def test_get_skill_level_partial(self):
        engine = CurriculumEngine()
        lessons = [
            Lesson(name="L1", description="", skill_name="python-basics", difficulty=0.1, prerequisites=[], completed=True),
            Lesson(name="L2", description="", skill_name="python-basics", difficulty=0.2, prerequisites=[], completed=False),
        ]
        level = engine.get_skill_level("python-basics", lessons)
        assert level == 0.5

    def test_get_skill_level_full_mastery(self):
        engine = CurriculumEngine()
        lessons = [
            Lesson(name=f"L{i}", description="", skill_name="python-basics", difficulty=0.1 * i, prerequisites=[], completed=True)
            for i in range(1, 5)
        ]
        level = engine.get_skill_level("python-basics", lessons)
        assert level == 1.0

    def test_get_skill_level_unknown_skill(self):
        engine = CurriculumEngine()
        level = engine.get_skill_level("unknown-skill", [])
        assert level == 0.0

    def test_skill_dependencies_exist(self):
        engine = CurriculumEngine()
        assert "python-basics" in engine.SKILL_DEPENDENCIES
        assert "system-design" in engine.SKILL_DEPENDENCIES

    def test_skill_lessons_exist(self):
        engine = CurriculumEngine()
        assert "python-basics" in engine.SKILL_LESSONS
        assert "data-structures" in engine.SKILL_LESSONS

    def test_find_needed_skills(self):
        engine = CurriculumEngine()
        needed = engine._find_needed_skills([], "data-structures")
        assert "python-basics" in needed
        assert "data-structures" in needed

    def test_find_needed_skills_with_current(self):
        engine = CurriculumEngine()
        needed = engine._find_needed_skills(["python-basics"], "data-structures")
        assert "python-basics" not in needed
        assert "data-structures" in needed
