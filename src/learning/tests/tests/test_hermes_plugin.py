"""Tests for the HermesPlugin module."""

import pytest
from phase7.hermes_plugin import (
    HermesSkillPlugin, SkillMetadata, SelfEvalPlugin, SkillForgePlugin,
    CurriculumPlugin, ExperienceReplayPlugin, PLUGIN_REGISTRY,
    register_skill, get_plugin, create_plugin, list_plugins,
)


class TestSkillMetadata:
    """Tests for SkillMetadata."""

    def test_metadata_fields(self):
        meta = SkillMetadata(
            name="test",
            description="Test",
            version="1.0.0",
            author="Test",
            tags=["test"],
            dependencies=[],
            entry_point="module:Class",
        )
        assert meta.name == "test"
        assert meta.version == "1.0.0"

    def test_metadata_to_dict(self):
        meta = SkillMetadata(
            name="test",
            description="Test",
            version="1.0.0",
            author="Test",
            tags=["test"],
            dependencies=[],
            entry_point="module:Class",
        )
        d = meta.to_dict()
        assert d["name"] == "test"
        assert d["tags"] == ["test"]


class TestHermesSkillPlugin:
    """Tests for the HermesSkillPlugin base class."""

    def test_plugin_initialization(self):
        meta = SkillMetadata(
            name="test",
            description="Test",
            version="1.0.0",
            author="Test",
            tags=[],
            dependencies=[],
            entry_point="module:Class",
        )
        plugin = HermesSkillPlugin(meta)
        assert plugin.metadata.name == "test"
        assert plugin.enabled is True

    def test_plugin_enable_disable(self):
        meta = SkillMetadata(
            name="test",
            description="Test",
            version="1.0.0",
            author="Test",
            tags=[],
            dependencies=[],
            entry_point="module:Class",
        )
        plugin = HermesSkillPlugin(meta)
        plugin.shutdown()
        assert plugin.enabled is False
        plugin.initialize()
        assert plugin.enabled is True

    def test_plugin_to_skill_md(self):
        meta = SkillMetadata(
            name="test-skill",
            description="A test skill",
            version="1.0.0",
            author="Test",
            tags=["test"],
            dependencies=[],
            entry_point="module:Class",
        )
        plugin = HermesSkillPlugin(meta)
        md = plugin.to_skill_md()
        assert "test-skill" in md
        assert "A test skill" in md


class TestPluginRegistry:
    """Tests for the plugin registry."""

    def test_registry_has_four_plugins(self):
        assert len(PLUGIN_REGISTRY) == 4

    def test_registry_contains_self_eval(self):
        assert "self-evaluation" in PLUGIN_REGISTRY

    def test_registry_contains_skill_forge(self):
        assert "skill-forge" in PLUGIN_REGISTRY

    def test_registry_contains_curriculum(self):
        assert "curriculum-engine" in PLUGIN_REGISTRY

    def test_registry_contains_experience_replay(self):
        assert "experience-replay" in PLUGIN_REGISTRY

    def test_get_plugin(self):
        plugin_class = get_plugin("self-evaluation")
        assert plugin_class is SelfEvalPlugin

    def test_get_plugin_invalid(self):
        assert get_plugin("nonexistent") is None

    def test_create_plugin(self):
        plugin = create_plugin("self-evaluation")
        assert isinstance(plugin, SelfEvalPlugin)

    def test_create_plugin_invalid(self):
        assert create_plugin("nonexistent") is None

    def test_list_plugins(self):
        plugins = list_plugins()
        assert len(plugins) == 4
        assert "self-evaluation" in plugins

    def test_register_skill(self):
        class CustomPlugin(HermesSkillPlugin):
            def __init__(self):
                super().__init__(SkillMetadata(
                    name="custom",
                    description="Custom",
                    version="1.0.0",
                    author="Test",
                    tags=[],
                    dependencies=[],
                    entry_point="module:Class",
                ))
            def execute(self, *args, **kwargs):
                return "custom"

        register_skill("custom", CustomPlugin)
        assert "custom" in PLUGIN_REGISTRY
        plugin = create_plugin("custom")
        assert isinstance(plugin, CustomPlugin)


class TestSelfEvalPlugin:
    """Tests for the SelfEvalPlugin."""

    def test_plugin_creation(self):
        plugin = SelfEvalPlugin()
        assert plugin.metadata.name == "self-evaluation"
        assert plugin.enabled is True

    def test_plugin_execute(self):
        plugin = SelfEvalPlugin()
        result = plugin.execute("output", "task")
        assert result is not None
        assert hasattr(result, "score")
        assert hasattr(result, "verdict")


class TestSkillForgePlugin:
    """Tests for the SkillForgePlugin."""

    def test_plugin_creation(self):
        plugin = SkillForgePlugin()
        assert plugin.metadata.name == "skill-forge"

    def test_plugin_execute(self):
        from phase7.skill_forge import SkillTrace
        plugin = SkillForgePlugin()
        trace = SkillTrace(
            task="Test",
            steps=[{"action": "a", "result": "r", "success": True}],
            final_result="r",
            success=True,
        )
        skill = plugin.execute(trace)
        assert skill is not None
        assert hasattr(skill, "name")


class TestCurriculumPlugin:
    """Tests for the CurriculumPlugin."""

    def test_plugin_creation(self):
        plugin = CurriculumPlugin()
        assert plugin.metadata.name == "curriculum-engine"

    def test_plugin_execute(self):
        plugin = CurriculumPlugin()
        path = plugin.execute([], "python-basics")
        assert path is not None
        assert hasattr(path, "lessons")


class TestExperienceReplayPlugin:
    """Tests for the ExperienceReplayPlugin."""

    def test_plugin_creation(self):
        plugin = ExperienceReplayPlugin()
        assert plugin.metadata.name == "experience-replay"

    def test_plugin_execute(self):
        from phase7.experience_replay import Experience
        plugin = ExperienceReplayPlugin()
        exp = Experience(state="s", action="a", result="r", reward=0.5)
        plugin.execute(exp)
        assert len(plugin.replay.buffer) == 1
