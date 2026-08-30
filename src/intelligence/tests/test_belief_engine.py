"""Tests for belief_engine.py."""

import pytest
from intelligence.belief_engine import BeliefEngine, Belief, Evidence


class TestBeliefEngine:
    def test_add_belief(self, belief_engine):
        b = belief_engine.add_belief("The sky is blue", confidence=0.8)
        assert b.id is not None
        assert b.statement == "The sky is blue"
        assert b.confidence == 0.8

    def test_get_belief(self, belief_engine):
        added = belief_engine.add_belief("test statement")
        retrieved = belief_engine.get_belief(added.id)
        assert retrieved is not None
        assert retrieved.statement == "test statement"

    def test_add_supporting_evidence(self, belief_engine):
        b = belief_engine.add_belief("test", confidence=0.5)
        evidence = belief_engine.add_evidence(b.id, "observation 1", evidence_type="supporting")
        assert evidence is not None
        assert evidence.type == "supporting"

    def test_add_contradicting_evidence(self, belief_engine):
        b = belief_engine.add_belief("test", confidence=0.8)
        evidence = belief_engine.add_evidence(b.id, "observation 2", evidence_type="contradicting")
        updated = belief_engine.get_belief(b.id)
        # Confidence should decrease with contradicting evidence
        assert updated.confidence < 0.8

    def test_find_by_category(self, belief_engine):
        belief_engine.add_belief("fact", category="facts")
        belief_engine.add_belief("opinion", category="opinions")
        results = belief_engine.find_beliefs(category="facts")
        assert len(results) == 1

    def test_find_by_min_confidence(self, belief_engine):
        belief_engine.add_belief("high confidence", confidence=0.9)
        belief_engine.add_belief("low confidence", confidence=0.2)
        results = belief_engine.find_beliefs(min_confidence=0.5)
        assert len(results) == 1

    def test_revise_belief(self, belief_engine):
        b = belief_engine.add_belief("test", confidence=0.5)
        revised = belief_engine.revise_belief(b.id, 0.9)
        assert revised.confidence == 0.9

    def test_delete_belief(self, belief_engine):
        b = belief_engine.add_belief("to delete")
        assert belief_engine.delete_belief(b.id) is True
        assert belief_engine.get_belief(b.id) is None

    def test_list_all(self, belief_engine):
        belief_engine.add_belief("one")
        belief_engine.add_belief("two")
        assert len(belief_engine.list_all()) == 2

    def test_persistence(self, temp_storage):
        be1 = BeliefEngine(storage_path=temp_storage)
        be1.add_belief("persistent")
        be2 = BeliefEngine(storage_path=temp_storage)
        assert len(be2.list_all()) == 1
