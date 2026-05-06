"""Tests for csvdiff.highlight_formatter."""

import pytest
from csvdiff.highlighter import FieldDiff, RowHighlight
from csvdiff.highlight_formatter import (
    format_highlight,
    format_highlight_summary,
)


def _make_highlight(key, changes):
    """Helper: build a RowHighlight from (col, before, after) tuples."""
    h = RowHighlight(key=key)
    for col, b, a in changes:
        h.changes.append(FieldDiff(column=col, before=b, after=a))
    return h


def test_format_highlight_empty_list():
    result = format_highlight([], color=False)
    assert "no modified rows" in result


def test_format_highlight_shows_key()
    hl = _make_highlight(("42",), [("score", "80", "90")])
    result = format_highlight([hl], color=False)
    assert "42" in result


def test_format_highlight_shows_column_name():
    hl = _make_highlight(("1",), [("grade", "B", "A")])
    result = format_highlight([hl], color=False)
    assert "grade" in result


def test_format_highlight_shows_before_and_after():
    hl = _make_highlight(("1",), [("salary", "100", "120")])
    result = format_highlight([hl], color=False)
    assert "100" in result
    assert "120" in result


def test_format_highlight_multiple_rows():
    h1 = _make_highlight(("1",), [("x", "a", "b")])
    h2 = _make_highlight(("2",), [("y", "c", "d")])
    result = format_highlight([h1, h2], color=False)
    assert "1" in result
    assert "2" in result


def test_format_highlight_field_count_in_header():
    hl = _make_highlight(("7",), [("a", "1", "2"), ("b", "3", "4")])
    result = format_highlight([hl], color=False)
    assert "2 field" in result


def test_format_highlight_summary_empty():
    assert format_highlight_summary([]) == "0 rows changed, 0 fields affected"


def test_format_highlight_summary_counts():
    h1 = _make_highlight(("1",), [("x", "a", "b"), ("y", "c", "d")])
    h2 = _make_highlight(("2",), [("z", "e", "f")])
    summary = format_highlight_summary([h1, h2])
    assert "2 row" in summary
    assert "3 field" in summary
