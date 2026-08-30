"""Tests for skill_forge.py."""

import pytest
from v9.learning.skill_forge import SkillForge, ForgedSkill
from v9.learning.trajectory_store import Trajectory, TrajectoryStep


class TestForgedSkill:
    """Tests for ForgedSkill."""

    def test_skill_fields(self):
        skill = ForgedSkill(
            name="test-skill",
            description="A test skill",
            steps=["step1", "step2"],
            preconditions=["pre1"],
            postconditions=["post1"],
            success_rate=0.8,
        )
        assert skill.name == "test-skill"
        assert skill.success_rate == 0.8

    def test_skill_to_dict(self):
        skill = ForgedSkill(
            name="test",
            description="Test",
            steps=["s1"],
            preconditions=[],
            postconditions=[],
        )
        d = skill.to_dict()
        assert d["name"] == "test"


class TestSkillForge:
    """Tests for SkillForge."""

    def test_forge_from_trajectories(self):
        forge = SkillForge()
        traj = Trajectory(
            task="Write code",
            steps=[
                TrajectoryStep(step_num=0, action="implement", observation="", result="code", success=True),
                TrajectoryStep(step_num=1, action="test", observation="", result="pass", success=True),
            ],
            success=True,
        )
        skills = forge.forge_from_trajectories([traj])
        assert len(skills) > 0

    def test_forge_stores_skill(self):
        forge = SkillForge()
        traj = Trajectory(
            task="Write code",
            steps=[TrajectoryStep(step_num=0, action="a", observation="", result="r", success=True)],
            success=True,
        )
        skills = forge.forge_from_trajectories([traj])
        if skills:
            assert skills[0].name in forge.skills

    def test_forge_filters_low_success(self):
        forge = SkillForge()
        traj = Trajectory(
            task="test",
            steps=[
                TrajectoryStep(step_num=0, action="a", observation="", result="r", success=False),
                TrajectoryStep(step_num=1, action="b", observation="", result="r", success=False),
            ],
            success=False,
        )
        skills = forge.forge_from_trajectories([traj], min_success_rate=0.7)
        assert len(skills) == 0

    def test_get_skill(self):
        forge = SkillForge()
        traj = Trajectory(
            task="Write code",
            steps=[TrajectoryStep(step_num=0, action="a", observation="", result="r", success=True)],
            success=True,
        )
        skills = forge.forge_from_trajectories([traj])
        if skills:
            retrieved = forge.get_skill(skills[0].name)
            assert retrieved is not None

    def test_find_skills_by_tag(self):
        forge = SkillForge()
        traj = Trajectory(
            task="Write code",
            steps=[TrajectoryStep(step_num=0, action="a", observation="", result="r", success=True)],
            success=True,
        )
        forge.forge_from_trajectories([traj])
        code_skills = forge.find_skills_by_tag("code")
        assert len(code_skills) > 0

    def test_list_skills(self):
        forge = SkillForge()
        traj = Trajectory(
            task="Test",
            steps=[TrajectoryStep(step_num=0, action="a", observation="", result="r", success=True)],
            success=True,
        )
        forge.forge_from_trajectories([traj])
        assert len(forge.list_skills()) > 0

    def test_merge_skills(self):
        forge = SkillForge()
        skill1 = ForgedSkill(
            name="s1", description="d1", steps=["a"], preconditions=[], postconditions=[]
        )
        skill2 = ForgedSkill(
            name="s2", description="d2", steps=["b"], preconditions=[], postconditions=[]
        )
        merged = forge.merge_skills(skill1, skill2)
        assert "a" in merged.steps
        assert "b" in merged.steps

    def test_extract_tags_code(self):
        forge = SkillForge()
        tags = forge._extract_tags("Write code for a function")
        assert "code" in tags

    def test_extract_tags_debug(self):
        forge = SkillForge()
        tags = forge._extract_tags("Debug the error in production")
        assert "debug" in tags
