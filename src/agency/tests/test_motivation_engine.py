"""Tests for motivation_engine.py."""
import time
import pytest
from agency.motivation_engine import MotivationEngine, Drive, ExplorationResult


class TestDrive:
    def test_create_drive(self):
        d = Drive(name="curiosity", intensity=0.7)
        assert d.name == "curiosity"
        assert d.intensity == 0.7
        assert d.is_active() is True

    def test_decay(self):
        d = Drive(name="test", intensity=0.5, decay_rate=0.1)
        d.tick()
        assert d.intensity == 0.4

    def test_boost(self):
        d = Drive(name="test", intensity=0.5, boost_rate=0.2)
        d.boost()
        assert d.intensity == 0.7

    def test_boost_custom(self):
        d = Drive(name="test", intensity=0.3)
        d.boost(0.5)
        assert d.intensity == 0.8

    def test_decay_below_threshold(self):
        d = Drive(name="test", intensity=0.1, threshold=0.3)
        assert d.is_active() is False

    def test_decay_to_zero(self):
        d = Drive(name="test", intensity=0.05, decay_rate=0.1)
        d.tick()
        assert d.intensity == 0.0


class TestMotivationEngine:
    def test_create(self):
        engine = MotivationEngine()
        assert "curiosity" in engine.drives
        assert "competence" in engine.drives
        assert "novelty" in engine.drives

    def test_select_drive(self):
        engine = MotivationEngine()
        drive = engine.select_drive()
        assert drive.name in ["curiosity", "competence", "novelty"]

    def test_propose_exploration(self):
        engine = MotivationEngine()
        actions = ["a", "b", "c"]
        choice = engine.propose_exploration(actions)
        assert choice in actions

    def test_update_boosts_novelty_drive(self):
        engine = MotivationEngine()
        result = ExplorationResult(action="x", novelty=0.9, success=True, reward=0.8)
        engine.update(result)
        assert engine.drives["novelty"].intensity > 0.6

    def test_update_boosts_competence_drive(self):
        engine = MotivationEngine()
        result = ExplorationResult(action="x", novelty=0.1, success=True, reward=0.9)
        engine.update(result)
        assert engine.drives["competence"].intensity > 0.5

    def test_exploration_count(self):
        engine = MotivationEngine()
        assert engine.exploration_count == 0
        engine.update(ExplorationResult("a", 0.5, True, 0.5))
        assert engine.exploration_count == 1

    def test_total_reward(self):
        engine = MotivationEngine()
        engine.update(ExplorationResult("a", 0.5, True, 0.7))
        engine.update(ExplorationResult("b", 0.5, True, 0.3))
        assert engine.total_reward == 1.0

    def test_get_state(self):
        engine = MotivationEngine()
        state = engine.get_state()
        assert "drives" in state
        assert "exploration_count" in state
        assert "active_drive" in state

    def test_tick_all(self):
        engine = MotivationEngine()
        engine.tick_all()
        assert engine.drives["curiosity"].intensity < 0.7

    def test_get_intrinsic_reward(self):
        engine = MotivationEngine()
        reward = engine.get_intrinsic_reward(novelty=0.9, success=True)
        assert reward > 0.3

    def test_intrinsic_reward_caps_at_one(self):
        engine = MotivationEngine()
        reward = engine.get_intrinsic_reward(novelty=1.0, success=True)
        assert reward <= 1.0


class TestExplorationResult:
    def test_create(self):
        r = ExplorationResult(action="a", novelty=0.5, success=True, reward=0.7)
        assert r.action == "a"
        assert r.novelty == 0.5
        assert r.success is True
        assert r.reward == 0.7
