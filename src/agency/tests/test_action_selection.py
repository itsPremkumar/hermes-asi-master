"""Tests for action_selection.py."""
import pytest
from agency.action_selection import ActionSelectionEngine, ActionOption


class TestActionOption:
    def test_create(self):
        opt = ActionOption(id="a1", name="test", expected_value=0.7)
        assert opt.id == "a1"
        assert opt.name == "test"
        assert opt.expected_value == 0.7

    def test_to_dict(self):
        opt = ActionOption(id="a1", name="test", expected_value=0.7, risk=0.3)
        d = opt.to_dict()
        assert d["id"] == "a1"
        assert d["expected_value"] == 0.7


class TestActionSelectionEngine:
    def test_create(self):
        engine = ActionSelectionEngine()
        assert engine.risk_tolerance == 0.5
        assert engine.exploration_rate == 0.1

    def test_evaluate_action(self):
        engine = ActionSelectionEngine()
        opt = ActionOption(id="a1", name="test", expected_value=0.8, risk=0.1, cost=0.1)
        score = engine.evaluate_action(opt)
        assert score > 0.5

    def test_evaluate_high_risk(self):
        engine = ActionSelectionEngine(risk_tolerance=0.2)
        opt = ActionOption(id="a1", name="test", expected_value=0.8, risk=0.9)
        score = engine.evaluate_action(opt)
        assert score < 0.5

    def test_select_action(self):
        engine = ActionSelectionEngine()
        options = [
            ActionOption(id="a1", name="good", expected_value=0.9, risk=0.1),
            ActionOption(id="a2", name="bad", expected_value=0.2, risk=0.8),
        ]
        selected = engine.select_action(options)
        assert selected is not None
        assert selected.name == "good"

    def test_select_action_empty(self):
        engine = ActionSelectionEngine()
        assert engine.select_action([]) is None

    def test_select_precondition_check(self):
        engine = ActionSelectionEngine()
        options = [
            ActionOption(id="a1", name="needs_cap", preconditions=["file_read"]),
        ]
        selected = engine.select_action(options, context={"capabilities": ["file_read"]})
        assert selected is not None

    def test_select_precondition_fail(self):
        engine = ActionSelectionEngine()
        options = [
            ActionOption(id="a1", name="needs_cap", preconditions=["admin"]),
        ]
        selected = engine.select_action(options, context={"capabilities": ["file_read"]})
        assert selected is None

    def test_record_outcome(self):
        engine = ActionSelectionEngine()
        engine.record_outcome("a1", 0.9)
        engine.record_outcome("a1", 0.8)
        assert engine.get_success_rate("a1") == 1.0

    def test_record_outcome_mixed(self):
        engine = ActionSelectionEngine()
        engine.record_outcome("a1", 0.9)
        engine.record_outcome("a1", 0.2)
        assert engine.get_success_rate("a1") == 0.5

    def test_get_stats(self):
        engine = ActionSelectionEngine()
        engine.record_outcome("a1", 0.9)
        stats = engine.get_stats()
        assert stats["actions_tracked"] == 1

    def test_context_bonus(self):
        engine = ActionSelectionEngine()
        opt = ActionOption(id="a1", name="tagged", expected_value=0.5,
                          metadata=["programming"])
        score = engine.evaluate_action(opt, context={"tags": ["programming"]})
        assert score > 0.3
