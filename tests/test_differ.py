"""Tests for csvdiff.differ module."""

import pytest
from csvdiff.differ import diff, DiffResult


@pytest.fixture
def left_data():
    return {
        ("1",): {"id": "1", "name": "Alice", "score": "90"},
        ("2",): {"id": "2", "name": "Bob", "score": "85"},
        ("3",): {"id": "3", "name": "Carol", "score": "78"},
    }


@pytest.fixture
def right_data():
    return {
        ("1",): {"id": "1", "name": "Alice", "score": "95"},  # modified
        ("2",): {"id": "2", "name": "Bob", "score": "85"},   # unchanged
        ("4",): {"id": "4", "name": "Dave", "score": "88"},  # added
        # "3" removed
    }


def test_diff_detects_added_rows(left_data, right_data):
    result = diff(left_data, right_data)
    assert len(result.added) == 1
    assert result.added[0]["id"] == "4"


def test_diff_detects_removed_rows(left_data, right_data):
    result = diff(left_data, right_data)
    assert len(result.removed) == 1
    assert result.removed[0]["id"] == "3"


def test_diff_detects_modified_rows(left_data, right_data):
    result = diff(left_data, right_data)
    assert len(result.modified) == 1
    mod = result.modified[0]
    assert mod["key"] == ("1",)
    assert mod["changes"]["score"] == {"old": "90", "new": "95"}


def test_diff_no_changes_when_identical(left_data):
    result = diff(left_data, left_data)
    assert not result.has_changes


def test_diff_respects_column_filter(left_data, right_data):
    # Only compare 'name'; score change should be ignored
    result = diff(left_data, right_data, columns=["name"])
    assert len(result.modified) == 0


def test_diff_result_summary(left_data, right_data):
    result = diff(left_data, right_data)
    summary = result.summary()
    assert "Added: 1" in summary
    assert "Removed: 1" in summary
    assert "Modified: 1" in summary


def test_diff_empty_left():
    right = {("1",): {"id": "1", "val": "a"}}
    result = diff({}, right)
    assert len(result.added) == 1
    assert not result.removed
    assert not result.modified


def test_diff_empty_right():
    left = {("1",): {"id": "1", "val": "a"}}
    result = diff(left, {})
    assert len(result.removed) == 1
    assert not result.added
    assert not result.modified
