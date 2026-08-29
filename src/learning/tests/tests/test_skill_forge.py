"""Tests for the SkillForge module."""

import pytest
from phase7.skill_forge import SkillForge, Skill, SkillTrace


class TestSkill:
    """Tests for the Skill dataclass."""

    def test_skill_fields(self):
        skill = Skill(
            name="test-skill",
            description="A test skill",
            steps=["step1", "step2"],
            tags=["test"],
            success_rate=0.8,
            usage_count=5,
        )
        assert skill.name == "test-skill"
        assert skill.description == "A test skill"
        assert skill.steps == ["step1", "step2"]
        assert skill.tags == ["test"]
        assert skill.success_rate == 0.8
        assert skill.usage_count == 5

    def test_skill_to_dict(self):
        skill = Skill(
            name="test-skill",
            description="Test",
            steps=["s1"],
            tags=["t1"],
        )
        d = skill.to_dict()
        assert d["name"] == "test-skill"
        assert d["steps"] == ["s1"]

    def test_skill_from_dict(self):
        data = {
            "name": "from-dict",
            "description": "Created from dict",
            "steps": ["step1"],
            "tags": ["tag1"],
            "success_rate": 0.9,
            "usage_count": 10,
        }
        skill = Skill.from_dict(data)
        assert skill.name == "from-dict"
        assert skill.success_rate == 0.9
        assert skill.usage_count == 10


class TestSkillTrace:
    """Tests for the SkillTrace dataclass."""

    def test_skill_trace_fields(self):
        trace = SkillTrace(
            task="test task",
            steps=[{"action": "act1", "result": "res1", "success": True}],
            final_result="done",
            success=True,
        )
        assert trace.task == "test task"
        assert len(trace.steps) == 1
        assert trace.success is True

    def test_skill_trace_success_rate(self):
        trace = SkillTrace(
            task="test",
            steps=[
                {"action": "a1", "result": "r1", "success": True},
                {"action": "a2", "result": "r2", "success": False},
                {"action": "a3", "result": "r3", "success": True},
            ],
            final_result="",
            success=True,
        )
        assert trace.success_rate == 2 / 3

    def test_skill_trace_success_rate_empty(self):
        trace = SkillTrace(task="test", steps=[], final_result="", success=True)
        assert trace.success_rate == 0.0


class TestSkillForge:
    """Tests for the SkillForge class."""

    def test_forge_from_trace(self):
        forge = SkillForge()
        trace = SkillTrace(
            task="Write a sorting function",
            steps=[
                {"action": "implement", "result": "code written", "success": True},
                {"action": "test", "result": "tests pass", "success": True},
            ],
            final_result="def sort(arr): return sorted(arr)",
            success=True,
        )
        skill = forge.forge_from_trace(trace)
        assert isinstance(skill, Skill)
        assert skill.name != ""
        assert len(skill.steps) > 0

    def test_forge_stores_skill(self):
        forge = SkillForge()
        trace = SkillTrace(
            task="Test task",
            steps=[{"action": "a", "result": "r", "success": True}],
            final_result="result",
            success=True,
        )
        skill = forge.forge_from_trace(trace)
        assert skill.name in forge.skills

    def test_forge_get_skill(self):
        forge = SkillForge()
        trace = SkillTrace(
            task="Deploy app",
            steps=[{"action": "deploy", "result": "done", "success": True}],
            final_result="deployed",
            success=True,
        )
        skill = forge.forge_from_trace(trace)
        retrieved = forge.get_skill(skill.name)
        assert retrieved is not None
        assert retrieved.name == skill.name

    def test_forge_find_skills_by_tag(self):
        forge = SkillForge()
        trace = SkillTrace(
            task="Write code for sorting",
            steps=[{"action": "code", "result": "done", "success": True}],
            final_result="code",
            success=True,
        )
        forge.forge_from_trace(trace)
        code_skills = forge.find_skills_by_tag("code")
        assert len(code_skills) > 0

    def test_forge_list_skills(self):
        forge = SkillForge()
        trace = SkillTrace(
            task="Test",
            steps=[{"action": "a", "result": "r", "success": True}],
            final_result="r",
            success=True,
        )
        forge.forge_from_trace(trace)
        skills = forge.list_skills()
        assert len(skills) > 0

    def test_forge_update_skill_success(self):
        forge = SkillForge()
        trace = SkillTrace(
            task="Test",
            steps=[{"action": "a", "result": "r", "success": True}],
            final_result="r",
            success=True,
        )
        skill = forge.forge_from_trace(trace)
        old_rate = skill.success_rate
        forge.update_skill_success(skill.name, True)
        assert skill.usage_count == 1

    def test_forge_with_llm(self):
        """Test forging with a mock LLM."""
        import json
        llm = lambda p: json.dumps({
            "name": "llm-skill",
            "description": "Forged by LLM",
            "steps": ["step1", "step2"],
            "tags": ["llm", "test"],
        })
        forge = SkillForge(llm=llm)
        trace = SkillTrace(
            task="Test LLM forge",
            steps=[{"action": "a", "result": "r", "success": True}],
            final_result="r",
            success=True,
        )
        skill = forge.forge_from_trace(trace)
        assert skill.name == "llm-skill"
        assert "llm" in skill.tags

    def test_forge_extract_tags_code(self):
        forge = SkillForge()
        tags = forge._extract_tags("Write code for a function")
        assert "code" in tags

    def test_forge_extract_tags_research(self):
        forge = SkillForge()
        tags = forge._extract_tags("Research the latest AI trends")
        assert "research" in tags

    def test_forge_extract_tags_write(self):
        forge = SkillForge()
        tags = forge._extract_tags("Write documentation for the API")
        assert "write" in tags

    def test_forge_generate_skill_name(self):
        forge = SkillForge()
        name = forge._extract_tags("Write a function to sort a list")
        assert isinstance(name, list)

    def test_forge_multiple_traces(self):
        forge = SkillForge()
        for i in range(3):
            trace = SkillTrace(
                task=f"Task {i}",
                steps=[{"action": f"a{i}", "result": f"r{i}", "success": True}],
                final_result=f"r{i}",
                success=True,
            )
            forge.forge_from_trace(trace)
        assert len(forge.traces) == 3
