"""Command-line interface for the debate-room framework."""

from __future__ import annotations
import argparse
import json
import sys

from .debate import Debate, build_mock_debate, build_judge_mock_debate
from .roles import Proposer, Critic, Judge, ProposerConfig, CriticConfig, JudgeConfig


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="debate",
        description="Multi-agent debate & consensus framework",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'run' command — actual debate (placeholder LLM)
    run_parser = subparsers.add_parser("run", help="Run a debate on a topic")
    run_parser.add_argument("topic", type=str, help="The topic to debate")
    run_parser.add_argument(
        "-k", "--rounds", type=int, default=3,
        help="Number of debate rounds (default: 3)",
    )
    run_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output result as JSON",
    )

    # 'mock' command — run with mock LLMs for demonstration/testing
    mock_parser = subparsers.add_parser("mock", help="Run a mock debate (deterministic)")
    mock_parser.add_argument("topic", type=str, help="The topic to debate")
    mock_parser.add_argument(
        "-k", "--rounds", type=int, default=3,
        help="Number of debate rounds (default: 3)",
    )
    mock_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output result as JSON",
    )
    mock_parser.add_argument(
        "--verdict", type=str, default="accept",
        choices=["accept", "reject"],
        help="Mock judge verdict (default: accept)",
    )
    mock_parser.add_argument(
        "--score", type=float, default=0.8,
        help="Mock judge consensus score (default: 0.8)",
    )

    # 'info' command — show framework info
    info_parser = subparsers.add_parser("info", help="Show framework information")
    info_parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Output as JSON",
    )

    return parser.parse_args(argv)


def run_debate(args: argparse.Namespace) -> int:
    """Execute a 'run' command."""
    debate = Debate(topic=args.topic, k_rounds=args.rounds)
    result = debate.run()
    _print_result(result, args.as_json)
    return 0


def run_mock_debate(args: argparse.Namespace) -> int:
    """Execute a 'mock' command."""
    debate = build_judge_mock_debate(
        topic=args.topic,
        k_rounds=args.rounds,
        verdict=args.verdict,
        score=args.score,
        explanation=f"Mock judgment for: {args.topic}",
    )
    result = debate.run()
    _print_result(result, args.as_json)
    return 0


def show_info(args: argparse.Namespace) -> int:
    """Execute the 'info' command."""
    info = {
        "name": "debate-room",
        "version": "1.0.0",
        "description": "Multi-agent debate & consensus framework",
        "roles": ["proposer", "critic", "judge"],
        "commands": ["run", "mock", "info"],
    }
    if args.as_json:
        print(json.dumps(info, indent=2))
    else:
        print(f"debate-room v{info['version']}")
        print(f"Description: {info['description']}")
        print(f"Roles: {', '.join(info['roles'])}")
        print(f"Commands: {', '.join(info['commands'])}")
    return 0


def _print_result(result, as_json: bool) -> None:
    """Format and print debate results."""
    if as_json:
        output = {
            "topic": result.topic,
            "total_rounds": result.total_rounds,
            "history": [
                {
                    "role": msg.role,
                    "round": msg.round_num,
                    "content": msg.content,
                }
                for msg in result.final_history
            ],
            "consensus": {
                "verdict": result.consensus.verdict if result.consensus else None,
                "score": result.consensus.score if result.consensus else None,
                "explanation": result.consensus.explanation if result.consensus else None,
            } if result.consensus else None,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"=== Debate: {result.topic} ===")
        print(f"Rounds: {result.total_rounds}")
        print()
        for msg in result.final_history:
            print(f"[{msg.role.upper()} Round {msg.round_num}]")
            print(f"  {msg.content}")
            print()
        if result.consensus:
            print("=== VERDICT ===")
            print(f"  Verdict: {result.consensus.verdict}")
            print(f"  Score:   {result.consensus.score}")
            print(f"  Reason:  {result.consensus.explanation}")


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    args = parse_args(argv)

    if args.command is None:
        print("Usage: debate [--help] {run,mock,info} ...")
        return 1

    if args.command == "run":
        return run_debate(args)
    elif args.command == "mock":
        return run_mock_debate(args)
    elif args.command == "info":
        return show_info(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
