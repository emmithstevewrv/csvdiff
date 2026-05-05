"""Tests for csvdiff.filter.ColumnFilter."""

import pytest
from csvdiff.filter import ColumnFilter


HEADERS = ["id", "name", "age", "city"]

ROW = {"id": "1", "name": "Alice", "age": "30", "city": "Berlin"}

INDEX = {
    ("1",): {"id": "1", "name": "Alice", "age": "30", "city": "Berlin"},
    ("2",): {"id": "2", "name": "Bob", "age": "25", "city": "Paris"},
}


# --- apply_headers ---

def test_include_returns_selected_columns():
    f = ColumnFilter(include=["id", "name"])
    assert f.apply_headers(HEADERS) == ["id", "name"]


def test_exclude_removes_columns():
    f = ColumnFilter(exclude=["age", "city"])
    assert f.apply_headers(HEADERS) == ["id", "name"]


def test_no_filter_returns_all_headers():
    f = ColumnFilter()
    assert f.apply_headers(HEADERS) == HEADERS


def test_include_preserves_given_order():
    f = ColumnFilter(include=["city", "id"])
    assert f.apply_headers(HEADERS) == ["city", "id"]


def test_include_missing_column_raises():
    f = ColumnFilter(include=["id", "nonexistent"])
    with pytest.raises(ValueError, match="nonexistent"):
        f.apply_headers(HEADERS)


def test_both_include_and_exclude_raises():
    with pytest.raises(ValueError):
        ColumnFilter(include=["id"], exclude=["age"])


# --- apply_row ---

def test_apply_row_keeps_selected_columns():
    f = ColumnFilter(include=["id", "name"])
    filtered_headers = f.apply_headers(HEADERS)
    result = f.apply_row(ROW, filtered_headers)
    assert result == {"id": "1", "name": "Alice"}


def test_apply_row_excludes_columns():
    f = ColumnFilter(exclude=["city"])
    filtered_headers = f.apply_headers(HEADERS)
    result = f.apply_row(ROW, filtered_headers)
    assert "city" not in result
    assert result["name"] == "Alice"


# --- apply_index ---

def test_apply_index_filters_all_rows():
    f = ColumnFilter(include=["id", "name"])
    filtered_headers = f.apply_headers(HEADERS)
    result = f.apply_index(INDEX, filtered_headers)
    assert result == {
        ("1",): {"id": "1", "name": "Alice"},
        ("2",): {"id": "2", "name": "Bob"},
    }


def test_apply_index_empty_index():
    f = ColumnFilter(exclude=["age"])
    filtered_headers = f.apply_headers(HEADERS)
    result = f.apply_index({}, filtered_headers)
    assert result == {}
