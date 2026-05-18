"""Tests for csvdiff.exporter and csvdiff.export_cli."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from csvdiff.differ import DiffResult
from csvdiff.exporter import export, export_csv, export_jsonl, export_tsv


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        added={"3": {"id": "3", "name": "Carol"}},
        removed={"2": {"id": "2", "name": "Bob"}},
        modified={
            "1": (
                {"id": "1", "name": "Alice"},
                {"id": "1", "name": "Alicia"},
            )
        },
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


# ---------------------------------------------------------------------------
# export_csv
# ---------------------------------------------------------------------------

def test_export_csv_contains_added_row(diff_result: DiffResult) -> None:
    out = export_csv(diff_result)
    assert "added" in out
    assert "Carol" in out


def test_export_csv_contains_removed_row(diff_result: DiffResult) -> None:
    out = export_csv(diff_result)
    assert "removed" in out
    assert "Bob" in out


def test_export_csv_contains_modified_rows(diff_result: DiffResult) -> None:
    out = export_csv(diff_result)
    assert "modified_before" in out
    assert "modified_after" in out
    assert "Alicia" in out


def test_export_csv_first_column_is_change_tag(diff_result: DiffResult) -> None:
    first_line = export_csv(diff_result).splitlines()[0]
    assert first_line.startswith("_change")


def test_export_csv_empty_result_returns_empty_string(empty_result: DiffResult) -> None:
    assert export_csv(empty_result) == ""


# ---------------------------------------------------------------------------
# export_tsv
# ---------------------------------------------------------------------------

def test_export_tsv_uses_tab_delimiter(diff_result: DiffResult) -> None:
    out = export_tsv(diff_result)
    first_line = out.splitlines()[0]
    assert "\t" in first_line


# ---------------------------------------------------------------------------
# export_jsonl
# ---------------------------------------------------------------------------

def test_export_jsonl_each_line_is_valid_json(diff_result: DiffResult) -> None:
    out = export_jsonl(diff_result)
    for line in out.splitlines():
        obj = json.loads(line)
        assert "_change" in obj


def test_export_jsonl_empty_result_returns_empty_string(empty_result: DiffResult) -> None:
    assert export_jsonl(empty_result) == ""


# ---------------------------------------------------------------------------
# export dispatcher
# ---------------------------------------------------------------------------

def test_export_unknown_format_raises(diff_result: DiffResult) -> None:
    with pytest.raises(ValueError, match="Unknown export format"):
        export(diff_result, "xml")


def test_export_dispatches_csv(diff_result: DiffResult) -> None:
    assert export(diff_result, "csv") == export_csv(diff_result)


def test_export_dispatches_tsv(diff_result: DiffResult) -> None:
    assert export(diff_result, "tsv") == export_tsv(diff_result)


def test_export_dispatches_jsonl(diff_result: DiffResult) -> None:
    assert export(diff_result, "jsonl") == export_jsonl(diff_result)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def diff_file(tmp_path: Path, diff_result: DiffResult) -> Path:
    from csvdiff.encoder import to_json
    p = tmp_path / "diff.json"
    p.write_text(to_json(diff_result), encoding="utf-8")
    return p


def _parse(args: list[str]):
    from csvdiff.export_cli import build_export_parser, run_export_command
    parser = build_export_parser()
    return run_export_command(parser.parse_args(args))


def test_cli_missing_file_returns_two(tmp_path: Path) -> None:
    assert _parse([str(tmp_path / "no.json")]) == 2


def test_cli_valid_diff_returns_zero(diff_file: Path) -> None:
    assert _parse([str(diff_file)]) == 0


def test_cli_writes_output_file(diff_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    _parse([str(diff_file), "--format", "csv", "--output", str(out)])
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "_change" in content


def test_cli_jsonl_format(diff_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.jsonl"
    code = _parse([str(diff_file), "--format", "jsonl", "--output", str(out)])
    assert code == 0
    lines = out.read_text(encoding="utf-8").splitlines()
    assert all(json.loads(ln) for ln in lines)
