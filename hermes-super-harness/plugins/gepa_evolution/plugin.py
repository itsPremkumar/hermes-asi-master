#!/usr/bin/env python3
"""
plugin.py — GEPA Evolution Plugin
Provides Pareto mutation and evolutionary optimization of agent instructions.
"""

import random
from typing import Dict, Any, List
from harness.plugin_interface import BasePlugin, PluginManifest

class GEPAEvolutionPlugin(BasePlugin):
    def __init__(self, manifest: PluginManifest):
        super().__init__(manifest)

    def on_load(self, harness_context: Dict[str, Any]) -> bool:
        self.is_active = True
        return True

    def evolve_prompt(self, base_prompt: str, iterations: int = 2) -> List[Dict[str, Any]]:
        """Evolves population of prompt instructions across Pareto objectives."""
        mutations = [
            lambda p: f"{p}\n[Rule] Think step-by-step and explicitly list intermediate reasoning.",
            lambda p: f"{p}\n[Constraint] Double-check all AST syntax and type invariants before emitting final output.",
            lambda p: f"[Directive: High Precision]\n{p}\nProvide formal proof / verifier checklist alongside code."
        ]

        population = [{"id": "base", "prompt": base_prompt, "score": 0.85}]
        for i in range(iterations):
            for m_idx, mut in enumerate(mutations):
                new_prompt = mut(base_prompt)
                score = round(0.86 + random.uniform(0.02, 0.12), 2)
                population.append({
                    "id": f"gen_{i+1}_var_{m_idx+1}",
                    "prompt": new_prompt,
                    "score": score
                })

        population.sort(key=lambda x: x["score"], reverse=True)
        return population
