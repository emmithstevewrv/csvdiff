"""Tests for csvdiff.indexer.ColumnIndexer."""

import pytest

from csvdiff.indexer import ColumnIndexer


@pytest.fixture()
def row_index():
    return {
        ("1",): {"id": "1", "name": "Alice", "dept": "eng"},
        ("2",): {"id": "2", "name": "Bob", "dept": "eng"},
        ("3",): {"id": "3", "name": "Carol", "dept": "hr"},
        ("4",): {"id": "4", "name": "Dave", "dept": "hr"},
    }


def test_build_and_lookup_single_match(row_index):
    idx = ColumnIndexer(["dept"])
    idx.build(row_index)
    result = idx.lookup("dept", "hr")
    assert set(result) == {("3",), ("4",)}


def test_build_and_lookup_multiple_columns(row_index):
    idx = ColumnIndexer(["name", "dept"])
    idx.build(row_index)
    assert idx.lookup("name", "Alice") == [("1",)]
    assert set(idx.lookup("dept", "eng")) == {("1",), ("2",)}


def test_lookup_missing_value_returns_empty(row_index):
    idx = ColumnIndexer(["dept"])
    idx.build(row_index)
    assert idx.lookup("dept", "finance") == []


def test_lookup_unknown_column_raises(row_index):
    idx = ColumnIndexer(["name"])
    idx.build(row_index)
    with pytest.raises(KeyError, match="dept"):
        idx.lookup("dept", "eng")


def test_unique_values_sorted(row_index):
    idx = ColumnIndexer(["dept"])
    idx.build(row_index)
    assert idx.unique_values("dept") == ["eng", "hr"]


def test_value_counts(row_index):
    idx = ColumnIndexer(["dept"])
    idx.build(row_index)
    counts = idx.value_counts("dept")
    assert counts["eng"] == 2
    assert counts["hr"] == 2


def test_rebuild_clears_previous_data(row_index):
    idx = ColumnIndexer(["dept"])
    idx.build(row_index)
    # Rebuild with a smaller index
    idx.build({("1",): {"id": "1", "name": "Alice", "dept": "eng"}})
    assert idx.lookup("dept", "hr") == []
    assert idx.lookup("dept", "eng") == [("1",)]


def test_empty_columns_raises():
    with pytest.raises(ValueError):
        ColumnIndexer([])


def test_columns_property_returns_copy():
    idx = ColumnIndexer(["name", "dept"])
    cols = idx.columns
    cols.append("extra")
    assert "extra" not in idx.columns
