"""Tests for csvdiff.encoder serialization utilities."""

import json

import pytest

from csvdiff.differ import DiffResult
from csvdiff.encoder import (
    added_to_csv,
    from_json,
    modified_after_to_csv,
    removed_to_csv,
    to_json,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        added={"3": {"id": "3", "name": "Carol", "age": "28"}},
        removed={"2": {"id": "2", "name": "Bob", "age": "30"}},
        modified={
            "1": (
                {"id": "1", "name": "Alice", "age": "25"},
                {"id": "1", "name": "Alice", "age": "26"},
            )
        },
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


HEADERS = ["id", "name", "age"]


def test_to_json_contains_added(sample_result):
    data = json.loads(to_json(sample_result))
    assert len(data["added"]) == 1
    assert data["added"][0]["name"] == "Carol"


def test_to_json_contains_removed(sample_result):
    data = json.loads(to_json(sample_result))
    assert len(data["removed"]) == 1
    assert data["removed"][0]["name"] == "Bob"


def test_to_json_contains_modified(sample_result):
    data = json.loads(to_json(sample_result))
    assert len(data["modified"]) == 1
    entry = data["modified"][0]
    assert entry["before"]["age"] == "25"
    assert entry["after"]["age"] == "26"


def test_to_json_empty_result(empty_result):
    data = json.loads(to_json(empty_result))
    assert data == {"added": [], "removed": [], "modified": []}


def test_from_json_roundtrip(sample_result):
    serialized = to_json(sample_result)
    restored = from_json(serialized)
    assert len(restored["added"]) == 1
    assert len(restored["removed"]) == 1
    assert len(restored["modified"]) == 1


def test_added_to_csv_has_header(sample_result):
    csv_text = added_to_csv(sample_result, HEADERS)
    first_line = csv_text.splitlines()[0]
    assert first_line == "id,name,age"


def test_added_to_csv_has_row(sample_result):
    csv_text = added_to_csv(sample_result, HEADERS)
    assert "Carol" in csv_text


def test_removed_to_csv_has_row(sample_result):
    csv_text = removed_to_csv(sample_result, HEADERS)
    assert "Bob" in csv_text


def test_modified_after_to_csv_reflects_new_value(sample_result):
    csv_text = modified_after_to_csv(sample_result, HEADERS)
    assert "26" in csv_text
    assert "25" not in csv_text


def test_csv_empty_result_only_header(empty_result):
    csv_text = added_to_csv(empty_result, HEADERS)
    lines = [l for l in csv_text.splitlines() if l]
    assert lines == ["id,name,age"]
