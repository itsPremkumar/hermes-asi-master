#!/usr/bin/env python3
"""
belief_engine.py — HERMES-ASI-MASTER Bayesian Belief & Epistemic Engine
Manages Bayesian belief updates, independent source corroboration, contradiction resolution,
and cascade notifications to dependent beliefs.
"""

import sys
import math
import unittest
from pathlib import Path
from datetime import datetime, timezone

try:
    from state_engine import load_state, save_state
except ImportError:
    from .state_engine import load_state, save_state

def calculate_posterior(prior: float, evidence_count: int, independent_sources: int, contradictions: int) -> float:
    # Bayesian evidence weight formula
    alpha = evidence_count + (independent_sources * 1.5)
    beta = max(1, contradictions * 3.0)
    
    likelihood_ratio = alpha / (alpha + beta)
    
    odds = (prior / (1.0 - prior + 1e-9)) * (likelihood_ratio / (1.0 - likelihood_ratio + 1e-9))
    posterior = odds / (1.0 + odds)
    return round(min(0.99, max(0.01, posterior)), 4)

def ingest_evidence(claim_id: str, claim_text: str, source: str, is_independent: bool = True, is_contradiction: bool = False) -> dict:
    data = load_state("belief_graph")
    beliefs = data.setdefault("beliefs", {})
    
    if claim_id not in beliefs:
        beliefs[claim_id] = {
            "claim": claim_text,
            "status": "hypothesis",
            "prior": 0.50,
            "posterior": 0.50,
            "evidence_count": 0,
            "independent_sources": 0,
            "contradiction_count": 0,
            "dependent_beliefs": [],
            "last_verified": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "provenance": []
        }
    
    b = beliefs[claim_id]
    b["evidence_count"] += 1
    if is_independent:
        b["independent_sources"] += 1
    if is_contradiction:
        b["contradiction_count"] += 1
    
    if source not in b["provenance"]:
        b["provenance"].append(source)
        
    b["posterior"] = calculate_posterior(
        b["prior"],
        b["evidence_count"],
        b["independent_sources"],
        b["contradiction_count"]
    )
    
    if b["posterior"] >= 0.95 and b["independent_sources"] >= 3 and b["contradiction_count"] == 0:
        b["status"] = "fact"
    elif b["posterior"] >= 0.80:
        b["status"] = "strongly_supported"
    elif b["contradiction_count"] > 0 and b["contradiction_count"] >= b["independent_sources"]:
        b["status"] = "contradicted"
    else:
        b["status"] = "inferred"
        
    b["last_verified"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    save_state("belief_graph", data)
    return b

def cascade_belief_update(claim_id: str) -> list:
    data = load_state("belief_graph")
    beliefs = data.get("beliefs", {})
    if claim_id not in beliefs:
        return []
    
    updated_dependents = []
    target = beliefs[claim_id]
    for dep_id in target.get("dependent_beliefs", []):
        if dep_id in beliefs:
            dep = beliefs[dep_id]
            dep["prior"] = round((dep["prior"] + target["posterior"]) / 2.0, 4)
            dep["posterior"] = calculate_posterior(
                dep["prior"],
                dep["evidence_count"],
                dep["independent_sources"],
                dep["contradiction_count"]
            )
            updated_dependents.append(dep_id)
            
    if updated_dependents:
        save_state("belief_graph", data)
    return updated_dependents

class BeliefEngineTests(unittest.TestCase):
    def test_posterior_calculation(self):
        p1 = calculate_posterior(0.5, 10, 4, 0)
        self.assertGreater(p1, 0.85)
        p2 = calculate_posterior(0.5, 2, 1, 5)
        self.assertLess(p2, 0.40)

    def test_ingest_and_cascade(self):
        b = ingest_evidence("TEST-CLAIM-01", "Testing Bayesian ingestion", "test_source", is_independent=True)
        self.assertIn("posterior", b)
        deps = cascade_belief_update("BELIEF-001")
        self.assertIsInstance(deps, list)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(BeliefEngineTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Belief Engine Active. Use --test for self-verification.")
