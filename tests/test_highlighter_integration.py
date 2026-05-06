"""Integration tests: Highlighter + highlight_formatter together."""

from csvdiff.highlighter import Highlighter
from csvdiff.highlight_formatter import format_highlight, format_highlight_summary


HEADERS = ["id", "name", "dept", "salary"]
KEYS = ["id"]


def _hl(headers=HEADERS, keys=KEYS):
    return Highlighter(headers=headers, key_columns=keys)


def test_full_pipeline_single_change():
    modified = {
        ("10",): (
            {"id": "10", "name": "Alice", "dept": "eng", "salary": "90000"},
            {"id": "10", "name": "Alice", "dept": "eng", "salary": "95000"},
        )
    }
    highlights = _hl().highlight_all(modified)
    text = format_highlight(highlights, color=False)
    assert "10" in text
    assert "salary" in text
    assert "90000" in text
    assert "95000" in text


def test_full_pipeline_no_changes():
    row = {"id": "1", "name": "Bob", "dept": "hr", "salary": "50000"}
    modified = {("1",): (row, row)}
    highlights = _hl().highlight_all(modified)
    # highlight exists but has 0 field changes
    assert len(highlights) == 1
    assert len(highlights[0]) == 0
    summary = format_highlight_summary(highlights)
    # 1 row returned but 0 fields changed
    assert "0 fields" in summary


def test_full_pipeline_multiple_rows_summary():
    modified = {
        ("1",): (
            {"id": "1", "name": "A", "dept": "x", "salary": "1"},
            {"id": "1", "name": "B", "dept": "x", "salary": "2"},
        ),
        ("2",): (
            {"id": "2", "name": "C", "dept": "y", "salary": "3"},
            {"id": "2", "name": "C", "dept": "z", "salary": "3"},
        ),
    }
    highlights = _hl().highlight_all(modified)
    summary = format_highlight_summary(highlights)
    assert "2 row" in summary
    assert "3 field" in summary
