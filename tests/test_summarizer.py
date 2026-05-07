"""Tests for csvdiff.summarizer."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.summarizer import DiffSummary, SummaryLine, summarize


@pytest.fixture
def result() -> DiffResult:
    return DiffResult(
        added={
            ("c",): {"id": "c", "val": "30"},
        },
        removed={
            ("b",): {"id": "b", "val": "20"},
        },
        modified={
            ("a",): (
                {"id": "a", "val": "10"},
                {"id": "a", "val": "99"},
            ),
        },
    )


@pytest.fixture
def empty_result() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


def test_summarize_counts_added(result):
    s = summarize(result, total_left=3, total_right=3)
    assert s.added == 1


def test_summarize_counts_removed(result):
    s = summarize(result, total_left=3, total_right=3)
    assert s.removed == 1


def test_summarize_counts_modified(result):
    s = summarize(result, total_left=3, total_right=3)
    assert s.modified == 1


def test_summarize_unchanged(result):
    # total_left=3, removed=1, modified=1 → unchanged=1
    s = summarize(result, total_left=3, total_right=3)
    assert s.unchanged == 1


def test_summarize_unchanged_never_negative():
    result = DiffResult(
        added={},
        removed={("x",): {"id": "x"}},
        modified={},
    )
    s = summarize(result, total_left=0, total_right=0)
    assert s.unchanged == 0


def test_total_changes(result):
    s = summarize(result, total_left=3, total_right=3)
    assert s.total_changes == 3


def test_change_rate(result):
    s = summarize(result, total_left=3, total_right=3)
    assert s.change_rate == round(3 / 3, 4)


def test_change_rate_zero_rows(empty_result):
    s = summarize(empty_result, total_left=0, total_right=0)
    assert s.change_rate == 0.0


def test_lines_returns_five_entries(result):
    s = summarize(result, total_left=3, total_right=3)
    assert len(s.lines()) == 5


def test_str_contains_added(result):
    s = summarize(result, total_left=3, total_right=3)
    assert "Added" in str(s)


def test_str_contains_rate(result):
    s = summarize(result, total_left=3, total_right=3)
    assert "Rate" in str(s)


def test_summary_line_str_with_detail():
    line = SummaryLine(label="Change rate", count=0, detail="50.00%")
    assert "50.00%" in str(line)


def test_summary_line_str_without_detail():
    line = SummaryLine(label="Added", count=5)
    assert str(line) == "Added: 5"
