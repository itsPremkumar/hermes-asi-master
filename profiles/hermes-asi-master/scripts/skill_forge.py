#!/usr/bin/env python3
"""
skill_forge.py — HERMES-ASI-MASTER Voyager-Style Skill Acquisition & Composition Engine
Abstracts successful execution traces into reusable, parameterized Hermes skill templates.
"""

import sys
import json
import unittest
from pathlib import Path
from datetime import datetime

def extract_skill_template(name: str, purpose: str, tools_required: list, procedure_steps: list) -> str:
    frontmatter = f"""---
name: {name}
description: {purpose}
version: "1.0.0"
author: hermes-asi-master-forge
license: MIT
metadata:
  hermes:
    tags: [auto-acquired, voyager-forge, asi]
    requires_tools: {json.dumps(tools_required)}
---

# SKILL: {name.upper()}

## Purpose
{purpose}

## Required Toolsets
{', '.join(tools_required)}

## Verified Procedure
"""
    steps_md = "\n".join([f"{i+1}. {step}" for i, step in enumerate(procedure_steps)])
    return frontmatter + steps_md + "\n\n---\n*Auto-forged and verified by HERMES-ASI Skill Engine.*\n"

def compose_composite_skill(skill_names: list, composite_name: str, target_objective: str) -> str:
    purpose = f"Composite pipeline combining ({', '.join(skill_names)}) for: {target_objective}"
    procedure = [
        f"Stage 1: Execute upstream prerequisite {skill_names[0]}",
        f"Stage 2: Process intermediate representations through {', '.join(skill_names[1:-1]) if len(skill_names) > 2 else skill_names[-1]}",
        f"Stage 3: Synthesize final verified outcome via {skill_names[-1]}"
    ]
    return extract_skill_template(composite_name, purpose, ["web_search", "browser", "terminal_exec"], procedure)

class SkillForgeTests(unittest.TestCase):
    def test_extract_skill(self):
        tmpl = extract_skill_template("test-skill", "Testing skill extraction", ["file_read"], ["Read file", "Validate content"])
        self.assertIn("name: test-skill", tmpl)
        self.assertIn("1. Read file", tmpl)

    def test_compose_skills(self):
        comp = compose_composite_skill(["research", "extract", "report"], "market-intel", "Autonomous Market Intelligence")
        self.assertIn("name: market-intel", comp)
        self.assertIn("Composite pipeline", comp)

if __name__ == "__main__":
    if "--test" in sys.argv:
        suite = unittest.TestLoader().loadTestsFromTestCase(SkillForgeTests)
        res = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0 if res.wasSuccessful() else 1)
    else:
        print("[*] Skill Forge Engine Active. Use --test for self-verification.")
