"""Tests for csvdiff.sorter module."""

import pytest
from csvdiff.sorter import RowSorter


HEADERS = ["id", "name", "score"]

ROWS = [
    {"id": "3", "name": "Charlie", "score": "90"},
    {"id": "1", "name": "Alice",   "score": "70"},
    {"id": "2", "name": "Bob",     "score": "85"},
]


def test_sort_by_single_key():
    sorter = RowSorter(sort_keys=["id"])
    result = sorter.sort_rows(ROWS, HEADERS)
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_sort_by_single_key_reverse():
    sorter = RowSorter(sort_keys=["id"], reverse=True)
    result = sorter.sort_rows(ROWS, HEADERS)
    assert [r["id"] for r in result] == ["3", "2", "1"]


def test_sort_by_multiple_keys():
    rows = [
        {"id": "1", "name": "Zara",  "score": "80"},
        {"id": "1", "name": "Alice", "score": "70"},
        {"id": "2", "name": "Bob",   "score": "85"},
    ]
    sorter = RowSorter(sort_keys=["id", "name"])
    result = sorter.sort_rows(rows, HEADERS)
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Zara"
    assert result[2]["name"] == "Bob"


def test_no_sort_keys_preserves_order():
    sorter = RowSorter()
    result = sorter.sort_rows(ROWS, HEADERS)
    assert result == ROWS


def test_sort_missing_key_raises():
    sorter = RowSorter(sort_keys=["nonexistent"])
    with pytest.raises(KeyError, match="nonexistent"):
        sorter.sort_rows(ROWS, HEADERS)


def test_sort_index_ascending():
    index = {
        ("3",): {"id": "3", "name": "Charlie"},
        ("1",): {"id": "1", "name": "Alice"},
        ("2",): {"id": "2", "name": "Bob"},
    }
    sorter = RowSorter()
    result = sorter.sort_index(index)
    keys = [k for k, _ in result]
    assert keys == [("1",), ("2",), ("3",)]


def test_sort_index_descending():
    index = {
        ("a",): {"id": "a"},
        ("c",): {"id": "c"},
        ("b",): {"id": "b"},
    }
    sorter = RowSorter(reverse=True)
    result = sorter.sort_index(index)
    keys = [k for k, _ in result]
    assert keys == [("c",), ("b",), ("a",)]


def test_sort_rows_does_not_mutate_original():
    import copy
    original = copy.deepcopy(ROWS)
    sorter = RowSorter(sort_keys=["name"])
    sorter.sort_rows(ROWS, HEADERS)
    assert ROWS == original


def test_sort_empty_rows_returns_empty():
    """Sorting an empty list of rows should return an empty list without error."""
    sorter = RowSorter(sort_keys=["id"])
    result = sorter.sort_rows([], HEADERS)
    assert result == []


def test_sort_empty_index_returns_empty():
    """Sorting an empty index should return an empty list without error."""
    sorter = RowSorter()
    result = sorter.sort_index({})
    assert result == []
