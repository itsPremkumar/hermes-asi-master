#!/usr/bin/env python3
"""
cli.py — Master CLI Entrypoint for Hermes Super-Harness
Unified command line launcher for DeerFlow 2.0 workflows, plugin management, and benchmarks.

Usage:
    python cli.py list-plugins
    python cli.py run --goal "Build a high-performance Redis cache limiter"
    python cli.py evolve --prompt "Verify AST before emitting code"
    python cli.py benchmark
    python cli.py update
"""

import sys
import pathlib
import argparse

# Add repo root to path
ROOT_DIR = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR))

from harness.engine import SuperHarnessEngine
from plugins.deerflow_v2.plugin import DeerFlowV2Plugin

def print_banner():
    print(r"""
======================================================================
         HERMES SUPER-HARNESS — 100% FREE SUPERAGENT PLATFORM
======================================================================
  Built on: Hermes Agent Core (Nous Research) + DeerFlow 2.0 (ByteDance)
  Architecture: 100% Plugin-Native | Zero-Cost Model Routing | StateGraph
======================================================================
""")

def main():
    parser = argparse.ArgumentParser(description="Hermes Super-Harness CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 1. list-plugins
    subparsers.add_parser("list-plugins", help="List all discovered plugins and permission rings")

    # 2. run
    run_parser = subparsers.add_parser("run", help="Execute an autonomous goal using DeerFlow 2.0 workflow")
    run_parser.add_argument("--goal", type=str, required=True, help="High-level goal description")

    # 3. evolve
    evolve_parser = subparsers.add_parser("evolve", help="Evolve a prompt instruction via GEPA Pareto optimization")
    evolve_parser.add_argument("--prompt", type=str, required=True, help="Base prompt instruction")
    evolve_parser.add_argument("--iterations", type=int, default=2, help="Number of evolutionary generations")

    # 4. benchmark
    subparsers.add_parser("benchmark", help="Run the multi-domain SuperAgent benchmark suite")

    # 5. update
    subparsers.add_parser("update", help="Update Hermes Agent core from upstream")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    print_banner()
    engine = SuperHarnessEngine(plugins_dir=str(ROOT_DIR / "plugins"))
    engine.auto_discover_plugins()

    if args.command == "list-plugins":
        plugins = engine.list_plugins()
        print(f"[*] Discovered {len(plugins)} Super-Harness Plugins:\n")
        for p in plugins:
            status = "[ACTIVE]" if p["active"] else "[INACTIVE]"
            print(f"  {status} {p['name']} (v{p['version']}) — Ring: {p['permission']}")
            print(f"      Description:  {p['description']}")
            print(f"      Capabilities: {', '.join(p['capabilities'])}\n")

    elif args.command == "run":
        deerflow_plugin = engine.plugins.get("deerflow_v2")
        if not deerflow_plugin or not isinstance(deerflow_plugin, DeerFlowV2Plugin):
            print("[-] Error: DeerFlow 2.0 plugin is not loaded.")
            sys.exit(1)

        print(f"[*] Executing DeerFlow 2.0 SuperAgent Workflow on Goal:\n    \"{args.goal}\"\n")
        engine.trigger_on_goal_start({"goal": args.goal})
        state = deerflow_plugin.run_flow(args.goal)
        engine.trigger_on_goal_complete({"goal": args.goal}, {"status": state.status})

        print("================ DEERFLOW 2.0 EXECUTION TRACE ================")
        for step in state.history:
            print(f"  [{step['node'].upper()}] -> {step['action']} (Status: {step['status']})")
        print("==============================================================")
        print(f"Final Verdict: {state.status.upper()}")
        print(f"Total Steps:   {len(state.history)}")
        v_res = state.get_artifact("verification_result", {})
        print(f"AST Validated: {v_res.get('is_valid_ast', False)}")
        print("==============================================================\n")

    elif args.command == "evolve":
        gepa_plugin = engine.plugins.get("gepa_evolution")
        if not gepa_plugin:
            print("[-] Error: gepa_evolution plugin is not loaded.")
            sys.exit(1)

        print(f"[*] Running GEPA Pareto Genetic Mutation on prompt:\n    \"{args.prompt}\"\n")
        population = gepa_plugin.evolve_prompt(args.prompt, iterations=args.iterations)
        print(f"[+] Evolved {len(population)} Candidate Prompt Instructions:")
        for idx, item in enumerate(population[:4]):
            print(f"\n--- Variant #{idx+1} [Score: {item['score']}] (ID: {item['id']}) ---")
            print(item["prompt"])
        print("\n")

    elif args.command == "benchmark":
        import time
        print("[*] Running Super-Harness Multi-Domain Benchmark Suite...")
        tasks = [
            ("BM-DF-001", "Formal AST Synthesis", "Generate Python function computing Levenshtein distance"),
            ("BM-DF-002", "Multi-Agent Planning", "Decompose distributed token bucket into lock-free Ring Buffer"),
            ("BM-DF-003", "Security Audit", "Audit smart contract transfer logic for reentrancy bugs"),
            ("BM-DF-004", "Fault Tolerance", "Simulate network partition recovery under Raft consensus")
        ]

        deerflow_plugin = engine.plugins.get("deerflow_v2")
        passed = 0
        total_time = 0.0

        for t_id, domain, goal in tasks:
            t0 = time.time()
            st = deerflow_plugin.run_flow(goal)
            dt = (time.time() - t0) * 1000
            total_time += dt
            if st.status == "completed":
                passed += 1
                print(f"  [PASS] {t_id} ({domain}): Completed in {dt:.1f}ms ({len(st.history)} steps)")
            else:
                print(f"  [FAIL] {t_id} ({domain}): Failed")

        print(f"\nBenchmark Summary: {passed}/{len(tasks)} Passed ({passed/len(tasks)*100:.1f}%) | Avg Latency: {total_time/len(tasks):.1f}ms\n")

    elif args.command == "update":
        from updater import main as run_updater
        run_updater()

if __name__ == "__main__":
    main()
