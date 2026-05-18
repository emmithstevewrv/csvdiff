"""Tests for csvdiff.annotate_cli."""

import json
import pytest

from csvdiff.annotate_cli import build_annotate_parser, run_annotate_command
from csvdiff.annotator import CHANGE_ADDED, CHANGE_REMOVED, CHANGE_MODIFIED


@pytest.fixture
def diff_file(tmp_path):
    payload = {
        "added": [{"id": "3", "name": "Carol"}],
        "removed": [{"id": "2", "name": "Bob"}],
        "modified": [
            {
                "before": {"id": "1", "name": "Alice"},
                "after": {"id": "1", "name": "Alicia"},
            }
        ],
    }
    path = tmp_path / "diff.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _parse(diff_file, *extra):
    parser = build_annotate_parser()
    return parser.parse_args([diff_file, *extra])


def test_missing_file_returns_two(tmp_path):
    args = _parse(str(tmp_path / "nope.json"))
    assert run_annotate_command(args) == 2


def test_invalid_json_returns_two(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    args = _parse(str(bad))
    assert run_annotate_command(args) == 2


def test_valid_diff_returns_zero(diff_file):
    args = _parse(diff_file)
    assert run_annotate_command(args) == 0


def test_summary_flag_prints_counts(diff_file, capsys):
    args = _parse(diff_file, "--summary")
    rc = run_annotate_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "added: 1" in out
    assert "removed: 1" in out
    assert "modified: 1" in out


def test_filter_by_added(diff_file, capsys):
    args = _parse(diff_file, "--type", CHANGE_ADDED)
    rc = run_annotate_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "ADDED" in out
    assert "REMOVED" not in out
    assert "MODIFIED" not in out


def test_filter_by_removed(diff_file, capsys):
    args = _parse(diff_file, "--type", CHANGE_REMOVED)
    rc = run_annotate_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "REMOVED" in out
    assert "ADDED" not in out


def test_filter_by_modified(diff_file, capsys):
    args = _parse(diff_file, "--type", CHANGE_MODIFIED)
    rc = run_annotate_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "MODIFIED" in out
    assert "ADDED" not in out
