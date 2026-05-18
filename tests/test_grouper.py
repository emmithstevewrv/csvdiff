"""Tests for csvdiff.grouper and csvdiff.group_cli."""

import json
import os
import pytest

from csvdiff.differ import DiffResult
from csvdiff.grouper import GroupBucket, GroupResult, RowGrouper


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def diff_result():
    return DiffResult(
        added=[
            {"region": "north", "id": "1", "val": "a"},
            {"region": "south", "id": "2", "val": "b"},
            {"region": "north", "id": "3", "val": "c"},
        ],
        removed=[
            {"region": "south", "id": "9", "val": "z"},
        ],
        modified=[
            ({"region": "east", "id": "5", "val": "old"}, {"region": "east", "id": "5", "val": "new"}),
            ({"region": "north", "id": "6", "val": "p"}, {"region": "north", "id": "6", "val": "q"}),
        ],
    )


@pytest.fixture()
def empty_diff():
    return DiffResult(added=[], removed=[], modified=[])


# ---------------------------------------------------------------------------
# RowGrouper unit tests
# ---------------------------------------------------------------------------

def test_empty_column_raises():
    with pytest.raises(ValueError):
        RowGrouper(column="")


def test_group_creates_correct_bucket_keys(diff_result):
    result = RowGrouper("region").group(diff_result)
    assert set(result.buckets.keys()) == {"north", "south", "east"}


def test_group_counts_added_per_bucket(diff_result):
    result = RowGrouper("region").group(diff_result)
    assert len(result.buckets["north"].added) == 2
    assert len(result.buckets["south"].added) == 1
    assert len(result.buckets["east"].added) == 0


def test_group_counts_removed_per_bucket(diff_result):
    result = RowGrouper("region").group(diff_result)
    assert len(result.buckets["south"].removed) == 1
    assert len(result.buckets["north"].removed) == 0


def test_group_counts_modified_per_bucket(diff_result):
    result = RowGrouper("region").group(diff_result)
    assert len(result.buckets["east"].modified) == 1
    assert len(result.buckets["north"].modified) == 1


def test_bucket_total(diff_result):
    result = RowGrouper("region").group(diff_result)
    # north: 2 added + 1 modified = 3
    assert result.buckets["north"].total == 3


def test_sorted_buckets_descending(diff_result):
    result = RowGrouper("region").group(diff_result)
    totals = [b.total for b in result.sorted_buckets()]
    assert totals == sorted(totals, reverse=True)


def test_group_empty_diff_returns_no_buckets(empty_diff):
    result = RowGrouper("region").group(empty_diff)
    assert result.group_count == 0


def test_missing_column_uses_placeholder(diff_result):
    result = RowGrouper("nonexistent").group(diff_result)
    assert "<missing>" in result.buckets


def test_group_result_column_attribute(diff_result):
    result = RowGrouper("region").group(diff_result)
    assert result.column == "region"


def test_bucket_str():
    b = GroupBucket(key_value="north", added=[{}], removed=[], modified=[])
    assert "north" in str(b)
    assert "+1" in str(b)


# ---------------------------------------------------------------------------
# group_cli tests
# ---------------------------------------------------------------------------

def test_group_cli_missing_file(tmp_path):
    from csvdiff.group_cli import build_group_parser, run_group_command
    parser = build_group_parser()
    args = parser.parse_args([str(tmp_path / "nope.json"), "--column", "region"])
    assert run_group_command(args) == 2


def test_group_cli_invalid_json(tmp_path):
    from csvdiff.group_cli import build_group_parser, run_group_command
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    parser = build_group_parser()
    args = parser.parse_args([str(bad), "--column", "region"])
    assert run_group_command(args) == 2


def test_group_cli_valid_diff(tmp_path, diff_result):
    from csvdiff.encoder import to_json
    from csvdiff.group_cli import build_group_parser, run_group_command
    diff_file = tmp_path / "diff.json"
    diff_file.write_text(json.dumps(to_json(diff_result)))
    parser = build_group_parser()
    args = parser.parse_args([str(diff_file), "--column", "region"])
    assert run_group_command(args) == 0


def test_group_cli_top_limits_output(tmp_path, diff_result, capsys):
    from csvdiff.encoder import to_json
    from csvdiff.group_cli import build_group_parser, run_group_command
    diff_file = tmp_path / "diff.json"
    diff_file.write_text(json.dumps(to_json(diff_result)))
    parser = build_group_parser()
    args = parser.parse_args([str(diff_file), "--column", "region", "--top", "1"])
    run_group_command(args)
    out = capsys.readouterr().out
    # only one bucket line printed (lines starting with two spaces)
    bucket_lines = [l for l in out.splitlines() if l.startswith("  ")]
    assert len(bucket_lines) == 1
