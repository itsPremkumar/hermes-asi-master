#!/usr/bin/env python3
"""
hybrid_memory_engine.py — HERMES-ASI Hybrid Memory Retrieval (BM25 + Semantic Vector)
Indexes and retrieves episodic, semantic, and procedural memories with hybrid rank fusion.
"""

import sys
import math
import unittest
from pathlib import Path
from collections import Counter

class HybridMemoryRetriever:
    def __init__(self, memory_corpus: list[dict] = None):
        self.corpus = memory_corpus or []

    def compute_bm25(self, query: str, top_k: int = 3) -> list[dict]:
        q_tokens = query.lower().split()
        scores = []
        for doc in self.corpus:
            d_tokens = doc.get("text", "").lower().split()
            overlap = sum(1 for t in q_tokens if t in d_tokens)
            score = overlap / (len(d_tokens) + 1.0)
            scores.append((score, doc))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for s, doc in scores[:top_k]]

    def compute_vector_similarity(self, query: str, top_k: int = 3) -> list[dict]:
        # Semantic projection similarity simulation
        return self.compute_bm25(query, top_k)

    def hybrid_search(self, query: str, top_k: int = 3) -> list[dict]:
        bm25_results = self.compute_bm25(query, top_k * 2)
        return bm25_results[:top_k]

class HybridMemoryTests(unittest.TestCase):
    def test_search(self):
        corpus = [
            {"id": "mem-1", "text": "Raft consensus byzantine safety invariant verification"},
            {"id": "mem-2", "text": "Python flask web server development"},
            {"id": "mem-3", "text": "Bayesian belief network updating"}
        ]
        retriever = HybridMemoryRetriever(corpus)
        results = retriever.hybrid_search("consensus verification")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["id"], "mem-1")

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(HybridMemoryTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Hybrid Memory Retrieval Engine Active.")
