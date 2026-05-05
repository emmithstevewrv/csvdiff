"""Tests for csvdiff.formatter module."""

import json
import pytest
from csvdiff.differ import DiffResult
from csvdiff.formatter import format_text, format_json


@pytest.fixture
def populated_result():
    result = DiffResult()
    result.added = [{"id": "4", "name": "Dave", "score": "88"}]
    result.removed = [{"id": "3", "name": "Carol", "score": "78"}]
    result.modified = [
        {
            "key": ("1",),
            "changes": {"score": {"old": "90", "new": "95"}},
            "row": {"id": "1", "name": "Alice", "score": "95"},
        }
    ]
    return result


def test_format_text_shows_added(populated_result):
    output = format_text(populated_result)
    assert "+ id=4" in output


def test_format_text_shows_removed(populated_result):
    output = format_text(populated_result)
    assert "- id=3" in output


def test_format_text_shows_modified(populated_result):
    output = format_text(populated_result)
    assert "~ [1]" in output
    assert "score: '90' -> '95'" in output


def test_format_text_no_changes():
    output = format_text(DiffResult())
    assert "No differences found." in output


def test_format_json_structure(populated_result):
    output = format_json(populated_result)
    data = json.loads(output)
    assert "added" in data
    assert "removed" in data
    assert "modified" in data
    assert "summary" in data


def test_format_json_summary_counts(populated_result):
    data = json.loads(format_json(populated_result))
    assert data["summary"]["added"] == 1
    assert data["summary"]["removed"] == 1
    assert data["summary"]["modified"] == 1


def test_format_json_modified_key_is_list(populated_result):
    data = json.loads(format_json(populated_result))
    assert isinstance(data["modified"][0]["key"], list)


def test_format_json_empty_result():
    data = json.loads(format_json(DiffResult()))
    assert data["summary"] == {"added": 0, "removed": 0, "modified": 0}
