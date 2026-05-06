"""Tests for csvdiff.patcher."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.patcher import PatchError, apply, to_rows


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
# apply()
# ---------------------------------------------------------------------------

def test_apply_empty_diff_returns_same_data(base_index, empty_diff):
    result = apply(base_index, empty_diff)
    assert result == base_index


def test_apply_added_row(base_index):
    diff = DiffResult(
        added={("4",): {"id": "4", "name": "Dave", "score": "40"}},
        removed={},
        modified={},
    )
    result = apply(base_index, diff)
    assert ("4",) in result
    assert result[("4",)]["name"] == "Dave"


def test_apply_removed_row(base_index):
    diff = DiffResult(added={}, removed={("2",): base_index[("2",)], }, modified={})
    result = apply(base_index, diff)
    assert ("2",) not in result
    assert len(result) == 2


def test_apply_modified_row(base_index):
    old = base_index[("1",)]
    new = {"id": "1", "name": "Alice", "score": "99"}
    diff = DiffResult(added={}, removed={}, modified={("1",): (old, new)})
    result = apply(base_index, diff)
    assert result[("1",)]["score"] == "99"


def test_apply_does_not_mutate_original(base_index):
    import copy
    original = copy.deepcopy(base_index)
    diff = DiffResult(added={("9",): {"id": "9", "name": "X", "score": "0"}}, removed={}, modified={})
    apply(base_index, diff)
    assert base_index == original


def test_apply_raises_on_duplicate_add(base_index):
    diff = DiffResult(
        added={("1",): {"id": "1", "name": "Dup", "score": "0"}},
        removed={},
        modified={},
    )
    with pytest.raises(PatchError, match="already exists"):
        apply(base_index, diff)


def test_apply_raises_on_missing_remove(base_index):
    diff = DiffResult(added={}, removed={("99",): {"id": "99"}}, modified={})
    with pytest.raises(PatchError, match="not found"):
        apply(base_index, diff)


def test_apply_raises_on_stale_modify(base_index):
    stale_old = {"id": "1", "name": "Wrong", "score": "0"}
    new = {"id": "1", "name": "Alice", "score": "55"}
    diff = DiffResult(added={}, removed={}, modified={("1",): (stale_old, new)})
    with pytest.raises(PatchError, match="does not match"):
        apply(base_index, diff)


# ---------------------------------------------------------------------------
# to_rows()
# ---------------------------------------------------------------------------

def test_to_rows_returns_correct_count(base_index):
    rows = to_rows(base_index, ["id", "name", "score"])
    assert len(rows) == 3


def test_to_rows_respects_header_order(base_index):
    headers = ["score", "id"]
    rows = to_rows(base_index, headers)
    assert list(rows[0].keys()) == ["score", "id"]


def test_to_rows_fills_missing_column_with_empty_string():
    index = {("1",): {"id": "1", "name": "Alice"}}
    rows = to_rows(index, ["id", "name", "score"])
    assert rows[0]["score"] == ""
