"""Tests for csvdiff.merger."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.merger import MergeError, MergeResult, merge, to_rows


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_index():
    return {
        ("1",): {"id": "1", "name": "Alice", "score": "10"},
        ("2",): {"id": "2", "name": "Bob",   "score": "20"},
        ("3",): {"id": "3", "name": "Carol",  "score": "30"},
    }


@pytest.fixture()
def empty_diff():
    return DiffResult(added={}, removed={}, modified={})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_merge_empty_diff_returns_same_data(base_index, empty_diff):
    result = merge(base_index, empty_diff)
    assert result.index == base_index
    assert result.total_applied == 0


def test_merge_added_row(base_index, empty_diff):
    diff = DiffResult(
        added={("4",): {"id": "4", "name": "Dave", "score": "40"}},
        removed={},
        modified={},
    )
    result = merge(base_index, diff)
    assert ("4",) in result.index
    assert result.applied_added == 1
    assert result.applied_removed == 0
    assert result.applied_modified == 0


def test_merge_removed_row(base_index):
    diff = DiffResult(
        added={},
        removed={("2",): {"id": "2", "name": "Bob", "score": "20"}},
        modified={},
    )
    result = merge(base_index, diff)
    assert ("2",) not in result.index
    assert result.applied_removed == 1


def test_merge_modified_row(base_index):
    old = {"id": "1", "name": "Alice", "score": "10"}
    new = {"id": "1", "name": "Alice", "score": "99"}
    diff = DiffResult(added={}, removed={}, modified={("1",): (old, new)})
    result = merge(base_index, diff)
    assert result.index[("1",)]["score"] == "99"
    assert result.applied_modified == 1


def test_merge_raises_on_duplicate_add(base_index):
    diff = DiffResult(
        added={("1",): {"id": "1", "name": "Alice", "score": "10"}},
        removed={},
        modified={},
    )
    with pytest.raises(MergeError, match="already exists"):
        merge(base_index, diff)


def test_merge_raises_on_missing_remove(base_index):
    diff = DiffResult(
        added={},
        removed={("99",): {"id": "99", "name": "Ghost", "score": "0"}},
        modified={},
    )
    with pytest.raises(MergeError, match="not found in base"):
        merge(base_index, diff)


def test_merge_raises_on_missing_modify(base_index):
    old = {"id": "99", "name": "Ghost", "score": "0"}
    new = {"id": "99", "name": "Ghost", "score": "1"}
    diff = DiffResult(added={}, removed={}, modified={("99",): (old, new)})
    with pytest.raises(MergeError, match="not found in base"):
        merge(base_index, diff)


def test_to_rows_returns_correct_structure(base_index, empty_diff):
    headers = ["id", "name", "score"]
    result = merge(base_index, empty_diff)
    rows = to_rows(result, headers)
    assert len(rows) == 3
    assert all(set(r.keys()) == set(headers) for r in rows)


def test_total_applied_counts_all_changes(base_index):
    old = {"id": "3", "name": "Carol", "score": "30"}
    new = {"id": "3", "name": "Carol", "score": "31"}
    diff = DiffResult(
        added={("4",): {"id": "4", "name": "Dave", "score": "40"}},
        removed={("2",): {"id": "2", "name": "Bob", "score": "20"}},
        modified={("3",): (old, new)},
    )
    result = merge(base_index, diff)
    assert result.total_applied == 3
