"""Tests for ColumnComparator."""

import pytest
from csvdiff.comparator import ColumnComparator, CompareConfig


@pytest.fixture
def default_cmp():
    return ColumnComparator()


@pytest.fixture
def numeric_cmp():
    return ColumnComparator(CompareConfig(numeric_tolerance=0.01, numeric_columns=["price"]))


def test_equal_strings_are_equal(default_cmp):
    result = default_cmp.compare("name", "Alice", "Alice")
    assert result.equal is True


def test_different_strings_are_not_equal(default_cmp):
    result = default_cmp.compare("name", "Alice", "Bob")
    assert result.equal is False
    assert result.reason == "string mismatch"


def test_case_sensitive_by_default(default_cmp):
    result = default_cmp.compare("name", "alice", "Alice")
    assert result.equal is False


def test_case_insensitive_config():
    cmp = ColumnComparator(CompareConfig(case_sensitive=False))
    result = cmp.compare("name", "alice", "ALICE")
    assert result.equal is True


def test_ignore_whitespace_trims_values():
    cmp = ColumnComparator(CompareConfig(ignore_whitespace=True))
    result = cmp.compare("col", "  hello  ", "hello")
    assert result.equal is True


def test_numeric_within_tolerance_is_equal(numeric_cmp):
    result = numeric_cmp.compare("price", "1.000", "1.005")
    assert result.equal is True


def test_numeric_exceeds_tolerance_is_not_equal(numeric_cmp):
    result = numeric_cmp.compare("price", "1.000", "1.02")
    assert result.equal is False
    assert "numeric diff" in result.reason


def test_non_numeric_value_falls_back_to_string(numeric_cmp):
    result = numeric_cmp.compare("price", "N/A", "N/A")
    assert result.equal is True


def test_compare_result_str_equal():
    cmp = ColumnComparator()
    result = cmp.compare("col", "a", "a")
    assert "=" in str(result)


def test_compare_result_str_not_equal():
    cmp = ColumnComparator()
    result = cmp.compare("col", "a", "b")
    assert "≠" in str(result)


def test_compare_rows_skips_key_columns():
    cmp = ColumnComparator()
    left = {"id": "1", "name": "Alice", "age": "30"}
    right = {"id": "1", "name": "Alice", "age": "31"}
    results = cmp.compare_rows(left, right, key_columns=["id"])
    columns_compared = [r.column for r in results]
    assert "id" not in columns_compared
    assert "age" in columns_compared


def test_compare_rows_detects_change():
    cmp = ColumnComparator()
    left = {"id": "1", "val": "foo"}
    right = {"id": "1", "val": "bar"}
    results = cmp.compare_rows(left, right, key_columns=["id"])
    assert any(not r.equal for r in results)


def test_compare_rows_all_equal():
    cmp = ColumnComparator()
    left = {"id": "1", "val": "foo"}
    right = {"id": "1", "val": "foo"}
    results = cmp.compare_rows(left, right, key_columns=["id"])
    assert all(r.equal for r in results)
