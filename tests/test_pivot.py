"""Tests for csvdiff.pivot."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.pivot import PivotBucket, PivotResult, pivot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        added={
            ("1",): {"id": "1", "region": "north", "val": "10"},
            ("2",): {"id": "2", "region": "south", "val": "20"},
        },
        removed={
            ("3",): {"id": "3", "region": "north", "val": "30"},
        },
        modified={
            ("4",): (
                {"id": "4", "region": "east", "val": "40"},
                {"id": "4", "region": "east", "val": "99"},
            ),
            ("5",): (
                {"id": "5", "region": "south", "val": "50"},
                {"id": "5", "region": "south", "val": "51"},
            ),
        },
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_pivot_returns_pivot_result(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    assert isinstance(result, PivotResult)
    assert result.column == "region"


def test_pivot_counts_added(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    assert result.buckets["north"].added == 1
    assert result.buckets["south"].added == 1


def test_pivot_counts_removed(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    assert result.buckets["north"].removed == 1


def test_pivot_counts_modified(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    assert result.buckets["east"].modified == 1
    assert result.buckets["south"].modified == 1


def test_pivot_total_per_bucket(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    # north: 1 added + 1 removed = 2
    assert result.buckets["north"].total == 2


def test_pivot_grand_total(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    # 2 added + 1 removed + 2 modified = 5
    assert result.grand_total() == 5


def test_pivot_sorted_buckets_descending(diff_result):
    result = pivot(diff_result, column="region", key_columns=["id"])
    buckets = result.sorted_buckets(by="total")
    totals = [b.total for b in buckets]
    assert totals == sorted(totals, reverse=True)


def test_pivot_skips_rows_missing_column(diff_result):
    # Add a row without the pivot column
    diff_result.added[("9",)] = {"id": "9", "val": "0"}  # no 'region'
    result = pivot(diff_result, column="region", key_columns=["id"])
    # Should not raise and '9' should not create a bucket
    assert all(b.value != "" for b in result.buckets.values())


def test_pivot_empty_diff():
    empty = DiffResult(added={}, removed={}, modified={})
    result = pivot(empty, column="region", key_columns=["id"])
    assert result.buckets == {}
    assert result.grand_total() == 0
