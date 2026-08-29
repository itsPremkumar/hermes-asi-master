#!/usr/bin/env python3
"""
install.py — Universal 1-Click Installer for Hermes ASI Master
Deploys configurations, constitutions (SOUL.md), memory files, master profiles,
Kanban production line, cron jobs, and all 21 skills to the official Hermes Agent path (~/.hermes/).

Cross-platform support: Windows, macOS, and Linux.
Usage:
    python install.py                   # Standard deployment
    python install.py --all-skills      # Automatically deploy all 21 skills
    python install.py --dry-run         # Simulate installation without copying
    python install.py --target custom   # Custom destination directory
"""

import os
import sys
import shutil
import pathlib
import argparse

VERSION = "4.0.0 ASI"
REPO_ROOT = pathlib.Path(__file__).parent

def print_banner():
    print(r"""
======================================================================
           HERMES ASI MASTER — 1-CLICK SYSTEM INSTALLER
======================================================================
  Version: 4.0 ASI Universal Master (Nous Hermes Native)
  Cognitive Planes: 15 | Active Skills: 21 | Cognitive Engines: 26
======================================================================
""")

def get_default_hermes_dir() -> pathlib.Path:
    """Returns the default ~/.hermes directory across OS platforms."""
    return pathlib.Path.home() / ".hermes"

def check_prerequisites() -> dict:
    """Checks for Python, Git, and Docker availability."""
    checks = {
        "python": sys.version.split()[0],
        "git": shutil.which("git") is not None,
        "docker": shutil.which("docker") is not None,
    }
    return checks

def deploy_file(src: pathlib.Path, dst: pathlib.Path, dry_run: bool = False, overwrite: bool = False):
    """Safely copies a single file, preserving existing files unless specified."""
    if not src.exists():
        print(f"  [MISSING] Source file not found: {src}")
        return False

    if dst.exists() and not overwrite:
        print(f"  [EXISTS] {dst.name} already exists. Skipping (use --force to overwrite).")
        return True

    if dry_run:
        print(f"  [DRY RUN] Would copy {src.name} -> {dst}")
        return True

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  [INSTALLED] {dst.name} -> {dst}")
    return True

def deploy_tree(src: pathlib.Path, dst: pathlib.Path, dry_run: bool = False, force: bool = False, label: str = "Folder"):
    """Deploys a directory tree with overwrite/merge support."""
    if not src.exists():
        return 0

    if dry_run:
        print(f"  [DRY RUN] Would deploy {label}: {src.name} -> {dst}")
        return len(list(src.iterdir()))

    if dst.exists() and force:
        shutil.rmtree(dst)

    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"  [{label} +] Deployed: {src.name} -> {dst}")
    return len(list(src.iterdir()))

def deploy_skills(src_skills: pathlib.Path, dst_skills: pathlib.Path, dry_run: bool = False, force: bool = False):
    """Deploys all skill directories into the destination skills folder."""
    if not src_skills.exists():
        print(f"  [ERROR] Skills source directory not found: {src_skills}")
        return 0

    installed_count = 0
    for skill_dir in sorted(src_skills.iterdir()):
        if skill_dir.is_dir():
            target_skill = dst_skills / skill_dir.name
            if dry_run:
                print(f"  [DRY RUN] Would install skill: {skill_dir.name} -> {target_skill}")
                installed_count += 1
                continue

            if target_skill.exists() and force:
                shutil.rmtree(target_skill)

            shutil.copytree(skill_dir, target_skill, dirs_exist_ok=True)
            print(f"  [SKILL +] Installed skill: {skill_dir.name}")
            installed_count += 1

    return installed_count

def main():
    parser = argparse.ArgumentParser(description="Hermes ASI Master Installer")
    parser.add_argument("--all-skills", action="store_true", help="Install all 21 skills automatically")
    parser.add_argument("--dry-run", action="store_true", help="Simulate installation without modifying disk")
    parser.add_argument("--force", action="store_true", help="Overwrite existing configuration files")
    parser.add_argument("--target", type=str, default=None, help="Custom destination directory (default: ~/.hermes)")
    args = parser.parse_args()

    print_banner()

    target_dir = pathlib.Path(args.target).expanduser().resolve() if args.target else get_default_hermes_dir()
    print(f"Target Directory: {target_dir}")
    print(f"Mode: {'DRY RUN (Simulation)' if args.dry_run else 'LIVE DEPLOYMENT'}\n")

    # 1. Check prerequisites
    checks = check_prerequisites()
    print("System Check:")
    print(f"  - Python: {checks['python']} (OK)")
    print(f"  - Git:    {'Available' if checks['git'] else 'Not Found (Recommended for worktrees)'}")
    print(f"  - Docker: {'Available (Docker backend ready)' if checks['docker'] else 'Not Found (Local backend will be used)'}\n")

    # 2. Deploy core files
    print("1. Deploying Core Hermes Identity, Memory, and Config:")
    core_files = [
        ("SOUL.md", "SOUL.md"),
        ("AGENTS.md", "AGENTS.md"),
        ("MEMORY.md", "MEMORY.md"),
        ("USER.md", "USER.md"),
        ("config.yaml", "config.yaml"),
        (".env.example", ".env.example"),
    ]

    for src_name, dst_name in core_files:
        src = REPO_ROOT / src_name
        dst = target_dir / dst_name
        deploy_file(src, dst, dry_run=args.dry_run, overwrite=args.force)

    # 3. Deploy Master Profile
    print("\n2. Deploying Master Profile (hermes-asi-master):")
    profile_src = REPO_ROOT / "profiles" / "hermes-asi-master"
    profile_dst = target_dir / "profiles" / "hermes-asi-master"
    deploy_tree(profile_src, profile_dst, dry_run=args.dry_run, force=args.force, label="Profile")

    # 4. Deploy Cron Jobs
    cron_src = REPO_ROOT / "cron"
    cron_dst = target_dir / "cron"
    if cron_src.exists():
        print("\n3. Deploying Scheduled Cron Routines:")
        deploy_tree(cron_src, cron_dst, dry_run=args.dry_run, force=args.force, label="Cron")

    # 5. Deploy Production Line
    prod_src = REPO_ROOT / "production-line"
    prod_dst = target_dir / "production-line"
    if prod_src.exists():
        print("\n4. Deploying Kanban Production Line:")
        deploy_tree(prod_src, prod_dst, dry_run=args.dry_run, force=args.force, label="Production-Line")

    # 6. Deploy Skills
    print("\n5. Deploying Hermes Skills:")
    src_skills = REPO_ROOT / "skills"
    dst_skills = target_dir / "skills"
    count = deploy_skills(src_skills, dst_skills, dry_run=args.dry_run, force=args.force)
    print(f"\nTotal Skills Processed: {count}")

    # 7. Summary & Next steps
    print("\n" + "="*70)
    if args.dry_run:
        print("DRY RUN COMPLETED. No changes were made to your filesystem.")
    else:
        print("INSTALLATION COMPLETE!")
        print("\nNext Steps:")
        print(f"  1. Review your config:        {target_dir / 'config.yaml'}")
        print(f"  2. Setup your API keys:       cp {target_dir / '.env.example'} {target_dir / '.env'}")
        print(f"  3. Launch Master Profile:     hermes -p hermes-asi-master chat")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
