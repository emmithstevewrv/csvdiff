"""Tests for csvdiff.aligner module."""

import pytest
from csvdiff.aligner import ColumnAligner, AlignmentResult


@pytest.fixture
def aligner():
    return ColumnAligner(key_columns=["id"])


def test_align_identical_headers_is_aligned(aligner):
    result = aligner.align(["id", "name", "age"], ["id", "name", "age"])
    assert result.aligned is True
    assert result.common == ["id", "name", "age"]
    assert result.left_only == []
    assert result.right_only == []
    assert result.reordered is False


def test_align_detects_left_only_columns(aligner):
    result = aligner.align(["id", "name", "score"], ["id", "name"])
    assert result.left_only == ["score"]
    assert result.right_only == []
    assert result.aligned is False


def test_align_detects_right_only_columns(aligner):
    result = aligner.align(["id", "name"], ["id", "name", "email"])
    assert result.right_only == ["email"]
    assert result.left_only == []
    assert result.aligned is False


def test_align_detects_reordered_columns(aligner):
    result = aligner.align(["id", "name", "age"], ["id", "age", "name"])
    assert result.reordered is True
    assert result.aligned is False
    assert result.left_only == []
    assert result.right_only == []


def test_align_common_excludes_right_only(aligner):
    result = aligner.align(["id", "name"], ["id", "name", "extra"])
    assert "extra" not in result.common


def test_summary_aligned(aligner):
    result = aligner.align(["id", "x"], ["id", "x"])
    assert result.summary() == "columns aligned"


def test_summary_with_differences(aligner):
    result = aligner.align(["id", "a"], ["id", "b"])
    s = result.summary()
    assert "left-only" in s
    assert "right-only" in s


def test_remap_row_keeps_target_columns(aligner):
    row = {"id": "1", "name": "Alice", "extra": "x"}
    remapped = aligner.remap_row(row, ["id", "name"])
    assert remapped == {"id": "1", "name": "Alice"}
    assert "extra" not in remapped


def test_remap_row_missing_column_skipped(aligner):
    row = {"id": "1"}
    remapped = aligner.remap_row(row, ["id", "name"])
    assert remapped == {"id": "1"}


def test_remap_index_applies_to_all_rows(aligner):
    index = {
        ("1",): {"id": "1", "name": "Alice", "score": "90"},
        ("2",): {"id": "2", "name": "Bob", "score": "80"},
    }
    remapped = aligner.remap_index(index, ["id", "name"])
    assert all("score" not in row for row in remapped.values())
    assert remapped[("1",)]["name"] == "Alice"
