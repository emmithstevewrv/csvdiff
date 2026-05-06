"""Tests for csvdiff.validator module."""

import pytest
from csvdiff.validator import CSVValidator, ValidationResult, ValidationError


LEFT_HEADERS = ["id", "name", "age"]
RIGHT_HEADERS = ["id", "name", "age"]


def test_valid_headers_pass():
    v = CSVValidator(key_columns=["id"])
    result = v.validate_headers(LEFT_HEADERS, RIGHT_HEADERS)
    assert result.is_valid


def test_missing_key_in_left_raises_error():
    v = CSVValidator(key_columns=["missing_col"])
    result = v.validate_headers(LEFT_HEADERS, RIGHT_HEADERS)
    assert not result.is_valid
    messages = [e.message for e in result.errors]
    assert any("left" in m for m in messages)


def test_missing_key_in_right_raises_error():
    v = CSVValidator(key_columns=["id"])
    result = v.validate_headers(LEFT_HEADERS, ["id", "name"])
    assert not result.is_valid
    messages = [e.message for e in result.errors]
    assert any("right" in m for m in messages)


def test_column_only_in_left_reported():
    v = CSVValidator(key_columns=["id"])
    result = v.validate_headers(["id", "name", "extra"], ["id", "name"])
    assert not result.is_valid
    columns = [e.column for e in result.errors]
    assert "extra" in columns


def test_column_only_in_right_reported():
    v = CSVValidator(key_columns=["id"])
    result = v.validate_headers(["id", "name"], ["id", "name", "score"])
    assert not result.is_valid
    columns = [e.column for e in result.errors]
    assert "score" in columns


def test_composite_key_all_present():
    v = CSVValidator(key_columns=["id", "name"])
    result = v.validate_headers(LEFT_HEADERS, RIGHT_HEADERS)
    assert result.is_valid


def test_empty_key_columns_raises():
    with pytest.raises(ValueError, match="At least one key column"):
        CSVValidator(key_columns=[])


def test_validate_keys_unique_no_duplicates():
    v = CSVValidator(key_columns=["id"])
    index = {("1",): {"id": "1", "name": "Alice"}, ("2",): {"id": "2", "name": "Bob"}}
    result = v.validate_keys_unique(index, "left")
    assert result.is_valid


def test_validate_keys_unique_with_none_sentinel():
    v = CSVValidator(key_columns=["id"])
    index = {("1",): None, ("2",): {"id": "2", "name": "Bob"}}
    result = v.validate_keys_unique(index, "left")
    assert not result.is_valid
    assert any("Duplicate" in e.message for e in result.errors)


def test_validate_keys_unique_side_label_in_error():
    """Ensure the side label ('left' or 'right') appears in duplicate key error messages."""
    v = CSVValidator(key_columns=["id"])
    index = {("1",): None, ("2",): {"id": "2", "name": "Bob"}}
    for side in ("left", "right"):
        result = v.validate_keys_unique(index, side)
        assert not result.is_valid
        assert any(side in e.message for e in result.errors), (
            f"Expected side label '{side}' in error messages, got: "
            f"{[e.message for e in result.errors]}"
        )


def test_validation_result_str_on_failure():
    result = ValidationResult()
    result.add_error("Something went wrong", column="col1")
    text = str(result)
    assert "Validation failed" in text
    assert "Something went wrong" in text


def test_validation_result_str_on_success():
    result = ValidationResult()
    assert "passed" in str(result)
