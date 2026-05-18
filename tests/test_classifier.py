"""Tests for csvdiff.classifier."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.classifier import (
    classify,
    ClassifyResult,
    ClassifiedRow,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
)


@pytest.fixture
def diff_result():
    return DiffResult(
        added={},
        removed={},
        modified={
            ("1",): (
                {"id": "1", "name": "Alice", "age": "30", "city": "NY"},
                {"id": "1", "name": "Alice", "age": "31", "city": "NY"},
            ),
            ("2",): (
                {"id": "2", "name": "Bob", "age": "25", "city": "LA"},
                {"id": "2", "name": "Robert", "age": "26", "city": "SF"},
            ),
            ("3",): (
                {"id": "3", "name": "Carol", "age": "40", "city": "Chicago"},
                {"id": "3", "name": "Caroline", "age": "41", "city": "Houston"},
            ),
        },
    )


def test_classify_returns_classify_result(diff_result):
    result = classify(diff_result, key_columns=["id"])
    assert isinstance(result, ClassifyResult)


def test_classify_row_count_matches_modified(diff_result):
    result = classify(diff_result, key_columns=["id"])
    assert len(result.rows) == 3


def test_classify_single_field_change_is_low(diff_result):
    result = classify(diff_result, key_columns=["id"], low_max=1, medium_max=3)
    low_keys = {r.key for r in result.low}
    assert ("1",) in low_keys


def test_classify_two_field_change_is_medium(diff_result):
    result = classify(diff_result, key_columns=["id"], low_max=1, medium_max=3)
    medium_keys = {r.key for r in result.medium}
    assert ("2",) in medium_keys


def test_classify_three_field_change_is_high(diff_result):
    result = classify(diff_result, key_columns=["id"], low_max=1, medium_max=2)
    high_keys = {r.key for r in result.high}
    assert ("3",) in high_keys


def test_classify_changed_field_count_excludes_key(diff_result):
    result = classify(diff_result, key_columns=["id"])
    row = next(r for r in result.rows if r.key == ("1",))
    assert row.changed_field_count == 1


def test_classify_empty_modified_returns_empty_result():
    empty = DiffResult(added={}, removed={}, modified={})
    result = classify(empty, key_columns=["id"])
    assert result.rows == []


def test_classify_row_str_contains_severity(diff_result):
    result = classify(diff_result, key_columns=["id"])
    for row in result.rows:
        assert row.severity.upper() in str(row)


def test_classify_summary_shows_all_levels(diff_result):
    result = classify(diff_result, key_columns=["id"], low_max=1, medium_max=2)
    summary = result.summary()
    assert "low=" in summary
    assert "medium=" in summary
    assert "high=" in summary


def test_classify_custom_thresholds():
    dr = DiffResult(
        added={},
        removed={},
        modified={
            ("x",): (
                {"id": "x", "a": "1", "b": "2", "c": "3", "d": "4"},
                {"id": "x", "a": "9", "b": "9", "c": "9", "d": "9"},
            )
        },
    )
    result = classify(dr, key_columns=["id"], low_max=2, medium_max=3)
    assert result.rows[0].severity == SEVERITY_HIGH
    assert result.rows[0].changed_field_count == 4
