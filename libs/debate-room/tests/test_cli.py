"""Tests for the CLI interface."""

import pytest
import json
import io
from contextlib import redirect_stdout
from debate_room.cli import parse_args, main, run_mock_debate, run_debate, show_info


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""

    def test_parse_run_command(self):
        args = parse_args(["run", "test topic", "-k", "2"])
        assert args.command == "run"
        assert args.topic == "test topic"
        assert args.rounds == 2

    def test_parse_run_default_rounds(self):
        args = parse_args(["run", "topic"])
        assert args.rounds == 3

    def test_parse_mock_command(self):
        args = parse_args(["mock", "topic", "-k", "2", "--verdict", "reject", "--score", "0.3"])
        assert args.command == "mock"
        assert args.topic == "topic"
        assert args.rounds == 2
        assert args.verdict == "reject"
        assert args.score == 0.3

    def test_parse_mock_default_verdict(self):
        args = parse_args(["mock", "topic"])
        assert args.verdict == "accept"

    def test_parse_mock_default_score(self):
        args = parse_args(["mock", "topic"])
        assert args.score == 0.8

    def test_parse_info_command(self):
        args = parse_args(["info"])
        assert args.command == "info"

    def test_parse_no_command(self):
        args = parse_args([])
        assert args.command is None

    def test_parse_json_flag(self):
        args = parse_args(["run", "topic", "--json"])
        assert args.as_json is True

    def test_parse_no_json_flag(self):
        args = parse_args(["run", "topic"])
        assert args.as_json is False

    def test_parse_unknown_verdict(self):
        with pytest.raises(SystemExit):
            parse_args(["mock", "topic", "--verdict", "maybe"])


class TestCLIMain:
    """Tests for the main() entry point."""

    def test_main_no_command(self):
        assert main([]) == 1

    def test_main_info_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main(["info"])
        assert rc == 0
        output = f.getvalue()
        assert "debate-room" in output
        assert "1.0.0" in output

    def test_main_info_json(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main(["info", "--json"])
        assert rc == 0
        data = json.loads(f.getvalue())
        assert data["name"] == "debate-room"
        assert "proposer" in data["roles"]

    def test_main_mock_command(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main(["mock", "test topic", "-k", "1"])
        assert rc == 0
        output = f.getvalue()
        assert "test topic" in output
        assert "VERDICT" in output

    def test_main_mock_json_output(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main(["mock", "json test", "-k", "1", "--json"])
        assert rc == 0
        data = json.loads(f.getvalue())
        assert data["topic"] == "json test"
        assert data["total_rounds"] == 1
        assert data["consensus"]["verdict"] == "accept"

    def test_main_mock_three_rounds(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main(["mock", "three round test", "-k", "3", "--json"])
        assert rc == 0
        data = json.loads(f.getvalue())
        assert data["total_rounds"] == 3
        roles = [h["role"] for h in data["history"]]
        assert len(roles) == 7  # 3 rounds * 2 + judge

    def test_main_mock_reject_verdict(self):
        f = io.StringIO()
        with redirect_stdout(f):
            rc = main(["mock", "reject test", "-k", "1", "--verdict", "reject", "--score", "0.3", "--json"])
        assert rc == 0
        data = json.loads(f.getvalue())
        assert data["consensus"]["verdict"] == "reject"
        assert data["consensus"]["score"] == 0.3
