"""Tests for csvdiff.profiler."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.profiler import DiffProfiler, ProfileResult, ColumnProfile


@pytest.fixture()
def result_with_modifications() -> DiffResult:
    return DiffResult(
        added={},
        removed={},
        modified={
            ("1",): ({"id": "1", "name": "Alice", "age": "30"}, {"id": "1", "name": "Alicia", "age": "30"}),
            ("2",): ({"id": "2", "name": "Bob",   "age": "25"}, {"id": "2", "name": "Bob",    "age": "26"}),
            ("3",): ({"id": "3", "name": "Carol",  "age": "40"}, {"id": "3", "name": "Caroline", "age": "41"}),
        },
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


def test_profile_counts_changed_columns(result_with_modifications):
    pr = DiffProfiler(result_with_modifications).profile()
    d = pr.as_dict()
    assert d["name"] == 2   # rows 1 and 3 changed name
    assert d["age"] == 2    # rows 2 and 3 changed age


def test_profile_total_modified(result_with_modifications):
    pr = DiffProfiler(result_with_modifications).profile()
    assert pr.total_modified == 3


def test_profile_change_rate(result_with_modifications):
    pr = DiffProfiler(result_with_modifications).profile()
    d = {c.name: c for c in pr.columns}
    assert abs(d["name"].change_rate - 2 / 3) < 1e-9


def test_most_changed_order(result_with_modifications):
    pr = DiffProfiler(result_with_modifications).profile()
    ranked = pr.most_changed()
    # both name and age have 2 changes; either may come first, but count must be descending
    for i in range(len(ranked) - 1):
        assert ranked[i].change_count >= ranked[i + 1].change_count


def test_profile_empty_result(empty_result):
    pr = DiffProfiler(empty_result).profile()
    assert pr.total_modified == 0
    assert pr.columns == []
    assert pr.as_dict() == {}


def test_profile_unchanged_column_not_included(result_with_modifications):
    pr = DiffProfiler(result_with_modifications).profile()
    # 'id' never changes
    assert "id" not in pr.as_dict()


def test_column_profile_str():
    cp = ColumnProfile(name="price", change_count=5, change_rate=0.5)
    assert "price" in str(cp)
    assert "5" in str(cp)


def test_profile_result_most_changed_empty():
    pr = ProfileResult(total_modified=0)
    assert pr.most_changed() == []
