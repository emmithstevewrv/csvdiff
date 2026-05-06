"""Tests for csvdiff.cache_cli."""

import os
import json
import pytest

from csvdiff.cache_cli import build_cache_parser, run_cache_command


@pytest.fixture
def cache_dir(tmp_path):
    d = tmp_path / ".csvdiff_cache"
    d.mkdir()
    return str(d)


def _add_entry(cache_dir, name="abc123"):
    path = os.path.join(cache_dir, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"added": {}, "removed": {}, "modified": {}}, fh)
    return path


def _parse(args_list):
    parser = build_cache_parser()
    return parser.parse_args(args_list)


def test_clear_removes_entries(cache_dir, capsys):
    _add_entry(cache_dir, "entry1")
    _add_entry(cache_dir, "entry2")
    args = _parse(["clear", "--cache-dir", cache_dir])
    code = run_cache_command(args)
    assert code == 0
    remaining = [f for f in os.listdir(cache_dir) if f.endswith(".json")]
    assert remaining == []
    out = capsys.readouterr().out
    assert "2" in out


def test_clear_empty_dir_reports_zero(cache_dir, capsys):
    args = _parse(["clear", "--cache-dir", cache_dir])
    code = run_cache_command(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "0" in out


def test_info_shows_entry_count(cache_dir, capsys):
    _add_entry(cache_dir, "x1")
    args = _parse(["info", "--cache-dir", cache_dir])
    code = run_cache_command(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "1" in out
    assert cache_dir in out


def test_info_missing_dir_reports_gracefully(tmp_path, capsys):
    missing = str(tmp_path / "no_cache")
    args = _parse(["info", "--cache-dir", missing])
    code = run_cache_command(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "does not exist" in out


def test_no_subcommand_returns_two(cache_dir, capsys):
    parser = build_cache_parser()
    args = parser.parse_args([])
    args.cache_dir = cache_dir
    code = run_cache_command(args)
    assert code == 2


def test_build_cache_parser_returns_parser():
    parser = build_cache_parser()
    assert parser is not None
