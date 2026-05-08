"""Tests for csvdiff.split_cli."""
import json
import os
import pytest

from csvdiff.differ import DiffResult
from csvdiff.encoder import to_json
from csvdiff.split_cli import build_split_parser, run_split_command


@pytest.fixture()
def diff_file(tmp_path):
    """Write a small diff JSON to a temp file and return its path."""
    r = DiffResult()
    r.modified["1"] = (
        {"id": "1", "name": "Alice", "score": "80"},
        {"id": "1", "name": "Alice", "score": "95"},
    )
    r.modified["2"] = (
        {"id": "2", "name": "Bob", "score": "70"},
        {"id": "2", "name": "Robert", "score": "70"},
    )
    path = tmp_path / "diff.json"
    path.write_text(json.dumps(to_json(r)))
    return str(path)


def _parse(args):
    parser = build_split_parser()
    return parser.parse_args(args)


def test_missing_diff_file_returns_two(tmp_path):
    ns = _parse([str(tmp_path / "nope.json"), "-k", "id"])
    assert run_split_command(ns) == 2


def test_invalid_json_returns_two(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    ns = _parse([str(bad), "-k", "id"])
    assert run_split_command(ns) == 2


def test_valid_diff_returns_zero(diff_file):
    ns = _parse([diff_file, "-k", "id"])
    assert run_split_command(ns) == 0


def test_text_output_shows_column(diff_file, capsys):
    ns = _parse([diff_file, "-k", "id"])
    run_split_command(ns)
    out = capsys.readouterr().out
    assert "score" in out
    assert "name" in out


def test_json_output_is_parseable(diff_file, capsys):
    ns = _parse([diff_file, "-k", "id", "--json"])
    run_split_command(ns)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "score" in data
    assert isinstance(data["score"], list)


def test_json_output_contains_before_after(diff_file, capsys):
    ns = _parse([diff_file, "-k", "id", "--json"])
    run_split_command(ns)
    data = json.loads(capsys.readouterr().out)
    entry = data["score"][0]
    assert "before" in entry and "after" in entry


def test_column_filter_limits_output(diff_file, capsys):
    ns = _parse([diff_file, "-k", "id", "-c", "score"])
    run_split_command(ns)
    out = capsys.readouterr().out
    assert "score" in out
    assert "name" not in out


def test_unknown_column_filter_produces_no_output(diff_file, capsys):
    ns = _parse([diff_file, "-k", "id", "-c", "nonexistent"])
    run_split_command(ns)
    out = capsys.readouterr().out
    assert out.strip() == ""
