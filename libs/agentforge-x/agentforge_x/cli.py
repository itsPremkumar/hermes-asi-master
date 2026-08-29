"""Command-line interface for agentforge-x."""

from __future__ import annotations
import argparse
import json
import sys

from .presets import load_presets, get_preset, DEFAULT_PRESETS
from .agents import AGENT_REGISTRY
from .judge import Judge, Verdict
from .agent import AgentType


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentforge",
        description="Multi-agent fleet framework with six specialized agents",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'list' command — list available agents and presets
    list_parser = subparsers.add_parser("list", help="List agents and presets")
    list_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output as JSON",
    )

    # 'run' command — run a preset
    run_parser = subparsers.add_parser("run", help="Run a preset fleet")
    run_parser.add_argument("preset", type=str, nargs="?", default="default",
                            help="Preset name (default: 'default')")
    run_parser.add_argument("topic", type=str, nargs="?", default="",
                            help="Topic for the agents")
    run_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output result as JSON",
    )

    # 'agent' command — run a single agent
    agent_parser = subparsers.add_parser("agent", help="Run a single agent")
    agent_parser.add_argument("agent_type", type=str,
                              choices=list(AGENT_REGISTRY.keys()),
                              help="Agent type to run")
    agent_parser.add_argument("task", type=str, help="Task for the agent")
    agent_parser.add_argument(
        "-k", "--iterations", type=int, default=3,
        help="Max iterations (default: 3)",
    )
    agent_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output result as JSON",
    )

    # 'presets' command — list available presets
    presets_parser = subparsers.add_parser("presets", help="List available presets")
    presets_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output as JSON",
    )

    return parser.parse_args(argv)


def cmd_list(args: argparse.Namespace) -> int:
    """Execute 'list' command."""
    agents = list(AGENT_REGISTRY.keys())
    presets = [p.name for p in load_presets()]

    if args.as_json:
        print(json.dumps({"agents": agents, "presets": presets}, indent=2))
    else:
        print("=== Available Agents ===")
        for a in agents:
            print(f"  {a}")
        print()
        print("=== Available Presets ===")
        for p in presets:
            print(f"  {p}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Execute 'run' command."""
    try:
        preset = get_preset(args.preset)
    except KeyError as e:
        print(f"Error: {e}")
        return 1

    topic = args.topic or preset.topic
    print(f"=== Running preset: {preset.name} ===")
    print(f"Topic: {topic}")
    print(f"Agents: {', '.join(preset.agents)}")
    print(f"Rounds: {preset.max_iterations}")
    print()

    # In real mode, this would instantiate agents and run them.
    # For now, simulate the fleet run with placeholder output.
    from .agents import get_agent_class

    results = {}
    for agent_name in preset.agents:
        agent_cls = get_agent_class(agent_name)
        agent = agent_cls(max_iterations=preset.max_iterations)
        result = agent.run(topic)
        results[agent_name] = result
        if not args.as_json:
            print(f"[{agent_name}] completed ({len(agent.history)} steps)")

    # Judge evaluation
    judge = Judge()
    all_work = "\n\n".join(results.values())
    verdict = judge.evaluate(all_work, context=topic)

    if not args.as_json:
        print()
        print("=== VERDICT ===")
        print(f"  Verdict: {verdict.verdict}")
        print(f"  Score:   {verdict.score}")
        print(f"  Reason:  {verdict.explanation[:100]}...")

    if args.as_json:
        output = {
            "preset": args.preset,
            "topic": topic,
            "agents": preset.agents,
            "results": results,
            "verdict": {
                "verdict": verdict.verdict,
                "score": verdict.score,
                "explanation": verdict.explanation,
                "evidence": verdict.evidence,
            },
        }
        print(json.dumps(output, indent=2))

    return 0


def cmd_agent(args: argparse.Namespace) -> int:
    """Execute 'agent' command."""
    from .agents import get_agent_class

    agent_cls = get_agent_class(args.agent_type)
    agent = agent_cls(max_iterations=args.iterations)
    result = agent.run(args.task)

    if args.as_json:
        output = {
            "agent": args.agent_type,
            "task": args.task,
            "iterations": args.iterations,
            "result": result,
            "history_steps": len(agent.history),
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"=== {args.agent_type.upper()} Agent ===")
        print(f"Task: {args.task}")
        print(f"Iterations: {args.iterations}")
        print(f"Result: {result}")
        print(f"History steps: {len(agent.history)}")
    return 0


def cmd_presets(args: argparse.Namespace) -> int:
    """Execute 'presets' command."""
    presets = load_presets()
    if args.as_json:
        output = [{"name": p.name, "description": p.description, "agents": p.agents}
                  for p in presets]
        print(json.dumps(output, indent=2))
    else:
        print("=== Available Presets ===")
        for p in presets:
            print(f"\n  {p.name}:")
            print(f"    Description: {p.description}")
            print(f"    Agents: {', '.join(p.agents)}")
            print(f"    Topic: {p.topic}")
            print(f"    Rounds: {p.max_iterations}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    args = parse_args(argv)

    if args.command is None:
        print("Usage: agentforge [--help] {list,run,agent,presets} ...")
        return 1

    if args.command == "list":
        return cmd_list(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "agent":
        return cmd_agent(args)
    elif args.command == "presets":
        return cmd_presets(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
