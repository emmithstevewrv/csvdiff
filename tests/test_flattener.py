"""Tests for csvdiff.flattener."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.flattener import flatten, FlattenResult, CHANGE_TYPE_KEY


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        added={"3": {"id": "3", "name": "Carol", "score": "90"}},
        removed={"2": {"id": "2", "name": "Bob", "score": "70"}},
        modified={
            "1": (
                {"id": "1", "name": "Alice", "score": "80"},
                {"id": "1", "name": "Alice", "score": "85"},
            )
        },
    )


@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


def test_flatten_empty_diff_returns_empty_result(empty_diff):
    result = flatten(empty_diff)
    assert result.total == 0
    assert result.rows == []


def test_flatten_counts_added(diff_result):
    result = flatten(diff_result)
    added = result.by_type("added")
    assert len(added) == 1
    assert added[0].key == "3"
    assert added[0].data["name"] == "Carol"


def test_flatten_counts_removed(diff_result):
    result = flatten(diff_result)
    removed = result.by_type("removed")
    assert len(removed) == 1
    assert removed[0].key == "2"


def test_flatten_includes_modified_before_by_default(diff_result):
    result = flatten(diff_result)
    before = result.by_type("modified_before")
    assert len(before) == 1
    assert before[0].data["score"] == "80"


def test_flatten_includes_modified_after(diff_result):
    result = flatten(diff_result)
    after = result.by_type("modified_after")
    assert len(after) == 1
    assert after[0].data["score"] == "85"


def test_flatten_no_before_omits_modified_before(diff_result):
    result = flatten(diff_result, include_modified_before=False)
    assert result.by_type("modified_before") == []
    assert len(result.by_type("modified_after")) == 1


def test_flatten_total_with_before(diff_result):
    # 1 added + 1 removed + 1 before + 1 after = 4
    result = flatten(diff_result)
    assert result.total == 4


def test_flatten_total_without_before(diff_result):
    # 1 added + 1 removed + 1 after = 3
    result = flatten(diff_result, include_modified_before=False)
    assert result.total == 3


def test_to_dicts_contains_change_type_key(diff_result):
    result = flatten(diff_result)
    dicts = result.to_dicts()
    for d in dicts:
        assert CHANGE_TYPE_KEY in d


def test_to_dicts_include_key_adds_underscore_key(diff_result):
    result = flatten(diff_result)
    dicts = result.to_dicts(include_key=True)
    for d in dicts:
        assert "_key" in d


def test_to_dicts_no_key_omits_underscore_key(diff_result):
    result = flatten(diff_result)
    dicts = result.to_dicts(include_key=False)
    for d in dicts:
        assert "_key" not in d


def test_flat_row_str_contains_change_type(diff_result):
    result = flatten(diff_result)
    for row in result.rows:
        assert row.change_type in str(row)
