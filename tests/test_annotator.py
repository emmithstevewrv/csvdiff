"""Tests for csvdiff.annotator."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.annotator import (
    RowAnnotator,
    AnnotationResult,
    AnnotatedRow,
    CHANGE_ADDED,
    CHANGE_REMOVED,
    CHANGE_MODIFIED,
)


@pytest.fixture
def diff_result():
    return DiffResult(
        added={("3",): {"id": "3", "name": "Carol"}},
        removed={("2",): {"id": "2", "name": "Bob"}},
        modified={
            ("1",): (
                {"id": "1", "name": "Alice"},
                {"id": "1", "name": "Alicia"},
            )
        },
    )


@pytest.fixture
def annotator():
    return RowAnnotator()


def test_annotate_returns_annotation_result(annotator, diff_result):
    result = annotator.annotate(diff_result)
    assert isinstance(result, AnnotationResult)


def test_annotate_total_row_count(annotator, diff_result):
    result = annotator.annotate(diff_result)
    assert len(result.rows) == 3


def test_annotate_added_rows(annotator, diff_result):
    result = annotator.annotate(diff_result)
    added = result.by_type(CHANGE_ADDED)
    assert len(added) == 1
    assert added[0].key == ("3",)
    assert added[0].after == {"id": "3", "name": "Carol"}
    assert added[0].before == {}


def test_annotate_removed_rows(annotator, diff_result):
    result = annotator.annotate(diff_result)
    removed = result.by_type(CHANGE_REMOVED)
    assert len(removed) == 1
    assert removed[0].key == ("2",)
    assert removed[0].before == {"id": "2", "name": "Bob"}
    assert removed[0].after == {}


def test_annotate_modified_rows(annotator, diff_result):
    result = annotator.annotate(diff_result)
    modified = result.by_type(CHANGE_MODIFIED)
    assert len(modified) == 1
    assert modified[0].key == ("1",)
    assert modified[0].before["name"] == "Alice"
    assert modified[0].after["name"] == "Alicia"


def test_summary_counts(annotator, diff_result):
    result = annotator.annotate(diff_result)
    summary = result.summary()
    assert summary[CHANGE_ADDED] == 1
    assert summary[CHANGE_REMOVED] == 1
    assert summary[CHANGE_MODIFIED] == 1


def test_annotated_row_str(annotator, diff_result):
    result = annotator.annotate(diff_result)
    added = result.by_type(CHANGE_ADDED)[0]
    assert "ADDED" in str(added)
    assert "3" in str(added)


def test_empty_diff_produces_empty_result(annotator):
    empty = DiffResult(added={}, removed={}, modified={})
    result = annotator.annotate(empty)
    assert result.rows == []
    summary = result.summary()
    assert all(v == 0 for v in summary.values())
