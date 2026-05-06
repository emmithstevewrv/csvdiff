"""Tests for csvdiff.highlighter."""

import pytest
from csvdiff.highlighter import FieldDiff, Highlighter, RowHighlight


HEADERS = ["id", "name", "score", "grade"]
KEYS = ["id"]


@pytest.fixture
def highlighter():
    return Highlighter(headers=HEADERS, key_columns=KEYS)


def test_highlight_row_detects_changed_fields(highlighter):
    before = {"id": "1", "name": "Alice", "score": "90", "grade": "A"}
    after  = {"id": "1", "name": "Alice", "score": "95", "grade": "A+"}
    result = highlighter.highlight_row(("1",), before, after)
    assert result.changed_columns == ["score", "grade"]


def test_highlight_row_no_changes(highlighter):
    row = {"id": "2", "name": "Bob", "score": "80", "grade": "B"}
    result = highlighter.highlight_row(("2",), row, row)
    assert len(result) == 0
    assert result.changes == []


def test_highlight_row_key_not_included_in_changes(highlighter):
    before = {"id": "3", "name": "Carol", "score": "70", "grade": "C"}
    after  = {"id": "99", "name": "Carol", "score": "70", "grade": "C"}
    # key column changes are not tracked as field diffs
    result = highlighter.highlight_row(("3",), before, after)
    assert "id" not in result.changed_columns


def test_highlight_all_returns_one_per_modified_row(highlighter):
    modified = {
        ("1",): (
            {"id": "1", "name": "Alice", "score": "90", "grade": "A"},
            {"id": "1", "name": "Alice", "score": "95", "grade": "A"},
        ),
        ("2",): (
            {"id": "2", "name": "Bob", "score": "80", "grade": "B"},
            {"id": "2", "name": "Bobby", "score": "80", "grade": "B"},
        ),
    }
    results = highlighter.highlight_all(modified)
    assert len(results) == 2


def test_field_diff_str():
    fd = FieldDiff(column="score", before="80", after="95")
    assert "score" in str(fd)
    assert "80" in str(fd)
    assert "95" in str(fd)


def test_row_highlight_changed_columns_order(highlighter):
    before = {"id": "5", "name": "Eve", "score": "60", "grade": "D"}
    after  = {"id": "5", "name": "Eva", "score": "65", "grade": "D"}
    result = highlighter.highlight_row(("5",), before, after)
    assert result.changed_columns == ["name", "score"]


def test_composite_key_highlighter():
    h = Highlighter(
        headers=["dept", "emp", "salary", "level"],
        key_columns=["dept", "emp"],
    )
    before = {"dept": "eng", "emp": "alice", "salary": "100", "level": "3"}
    after  = {"dept": "eng", "emp": "alice", "salary": "120", "level": "4"}
    result = h.highlight_row(("eng", "alice"), before, after)
    assert set(result.changed_columns) == {"salary", "level"}


def test_highlight_all_empty_modified(highlighter):
    results = highlighter.highlight_all({})
    assert results == []
