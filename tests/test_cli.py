"""Tests for the csvdiff CLI entry point."""

import json
import textwrap
from pathlib import Path

import pytest

from csvdiff.cli import main


@pytest.fixture()
def tmp_csv(tmp_path: Path):
    """Factory that writes a CSV string to a temp file and returns its path."""

    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return str(p)

    return _write


def test_no_changes_returns_zero(tmp_csv):
    data = """\
        id,name
        1,Alice
        2,Bob
    """
    left = tmp_csv("left.csv", data)
    right = tmp_csv("right.csv", data)
    assert main([left, right, "-k", "id"]) == 0


def test_changes_return_one(tmp_csv):
    left = tmp_csv("left.csv", "id,name\n1,Alice\n")
    right = tmp_csv("right.csv", "id,name\n1,Alice\n2,Bob\n")
    assert main([left, right, "-k", "id"]) == 1


def test_missing_file_returns_two(tmp_csv, capsys):
    left = tmp_csv("left.csv", "id,name\n1,Alice\n")
    rc = main([left, "nonexistent.csv", "-k", "id"])
    assert rc == 2
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_json_format_output(tmp_csv, capsys):
    left = tmp_csv("left.csv", "id,name\n1,Alice\n")
    right = tmp_csv("right.csv", "id,name\n1,Alice\n2,Bob\n")
    main([left, right, "-k", "id", "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "added" in data
    assert len(data["added"]) == 1


def test_text_format_contains_plus(tmp_csv, capsys):
    left = tmp_csv("left.csv", "id,name\n1,Alice\n")
    right = tmp_csv("right.csv", "id,name\n1,Alice\n2,Bob\n")
    main([left, right, "-k", "id", "--format", "text", "--no-color"])
    captured = capsys.readouterr()
    assert "+" in captured.out


def test_default_key_uses_first_column(tmp_csv):
    left = tmp_csv("left.csv", "id,name\n1,Alice\n")
    right = tmp_csv("right.csv", "id,name\n1,Alice\n")
    # No -k flag — should not raise
    assert main([left, right]) == 0
