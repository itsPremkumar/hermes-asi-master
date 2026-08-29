#!/usr/bin/env python3
"""
test_master_suite.py — Validation test suite for Hermes ASI Master repository
Tests skills frontmatters, core configs, 26 cognitive Python engines, and state files.
"""

import os
import sys
import ast
import json
import yaml
import pathlib
import subprocess
import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
SCRIPTS_DIR = REPO_ROOT / "profiles" / "hermes-asi-master" / "scripts"
STATE_DIR = REPO_ROOT / "profiles" / "hermes-asi-master" / "state"

def get_skill_files():
    assert SKILLS_DIR.exists(), f"Skills directory not found at {SKILLS_DIR}"
    return sorted(list(SKILLS_DIR.glob("*/SKILL.md")))

def get_script_files():
    assert SCRIPTS_DIR.exists(), f"Scripts directory not found at {SCRIPTS_DIR}"
    return sorted(list(SCRIPTS_DIR.glob("*.py")))

def parse_frontmatter(content: str):
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    return yaml.safe_load(parts[1])

def test_core_identity_files():
    """Verify that core identity and config files exist and are non-empty."""
    core_files = ["SOUL.md", "AGENTS.md", "MEMORY.md", "USER.md", "config.yaml", ".env.example", "requirements.txt", "install.py"]
    for filename in core_files:
        filepath = REPO_ROOT / filename
        assert filepath.exists(), f"Required core file missing: {filepath}"
        assert filepath.stat().st_size > 0, f"Core file is empty: {filepath}"

def test_skill_count():
    """Ensure all 21 modular skills are present."""
    skills = get_skill_files()
    assert len(skills) >= 21, f"Expected at least 21 skills, found {len(skills)}"

@pytest.mark.parametrize("skill_path", get_skill_files(), ids=lambda p: p.parent.name)
def test_skill_frontmatter(skill_path: pathlib.Path):
    """Verify that each SKILL.md has valid YAML frontmatter matching Hermes standards."""
    text = skill_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    assert fm is not None, f"Missing or malformed YAML frontmatter in {skill_path}"
    assert "name" in fm, f"Frontmatter missing 'name' in {skill_path}"
    assert "description" in fm, f"Frontmatter missing 'description' in {skill_path}"
    assert "version" in fm, f"Frontmatter missing 'version' in {skill_path}"

def test_state_files_json_validity():
    """Ensure all JSON state files in the master profile parse correctly."""
    assert STATE_DIR.exists(), f"State directory missing at {STATE_DIR}"
    for json_file in STATE_DIR.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data is not None, f"Empty JSON state in {json_file}"

def test_cron_jobs_validity():
    """Verify cron/jobs.json is valid JSON."""
    cron_file = REPO_ROOT / "cron" / "jobs.json"
    if cron_file.exists():
        with open(cron_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "jobs" in data or isinstance(data, list) or isinstance(data, dict)

def test_script_syntax():
    """Verify all Python scripts in the profile have valid syntax."""
    scripts = get_script_files()
    assert len(scripts) >= 20, f"Expected at least 20 scripts, found {len(scripts)}"
    for script_path in scripts:
        code = script_path.read_text(encoding="utf-8")
        try:
            ast.parse(code, filename=str(script_path))
        except SyntaxError as e:
            pytest.fail(f"Syntax error in {script_path}: {e}")

@pytest.mark.parametrize("script_path", get_script_files(), ids=lambda p: p.name)
def test_script_help_flag(script_path: pathlib.Path):
    """Verify each cognitive engine supports --help without throwing errors."""
    res = subprocess.run([sys.executable, str(script_path), "--help"], capture_output=True, text=True)
    assert res.returncode == 0, f"Script {script_path.name} failed --help test: {res.stderr}"
