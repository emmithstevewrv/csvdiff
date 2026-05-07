"""Integration tests: summarizer wired through differ output."""

from csvdiff.differ import compute_diff
from csvdiff.summarizer import summarize


def _idx(rows, key="id"):
    return {(r[key],): r for r in rows}


def test_full_pipeline_no_changes():
    rows = [{"id": "1", "v": "a"}, {"id": "2", "v": "b"}]
    left = _idx(rows)
    right = _idx(rows)
    result = compute_diff(left, right, key_columns=["id"])
    s = summarize(result, total_left=2, total_right=2)
    assert s.total_changes == 0
    assert s.unchanged == 2
    assert s.change_rate == 0.0


def test_full_pipeline_only_additions():
    left = _idx([{"id": "1", "v": "a"}])
    right = _idx([{"id": "1", "v": "a"}, {"id": "2", "v": "b"}])
    result = compute_diff(left, right, key_columns=["id"])
    s = summarize(result, total_left=1, total_right=2)
    assert s.added == 1
    assert s.removed == 0
    assert s.modified == 0
    assert s.unchanged == 1


def test_full_pipeline_mixed_changes():
    left = _idx([
        {"id": "1", "v": "old"},
        {"id": "2", "v": "b"},
        {"id": "3", "v": "c"},
    ])
    right = _idx([
        {"id": "1", "v": "new"},
        {"id": "3", "v": "c"},
        {"id": "4", "v": "d"},
    ])
    result = compute_diff(left, right, key_columns=["id"])
    s = summarize(result, total_left=3, total_right=3)
    assert s.modified == 1
    assert s.removed == 1
    assert s.added == 1
    assert s.total_changes == 3


def test_summary_str_is_multiline():
    left = _idx([{"id": "1", "v": "a"}])
    right = _idx([{"id": "1", "v": "b"}])
    result = compute_diff(left, right, key_columns=["id"])
    s = summarize(result, total_left=1, total_right=1)
    text = str(s)
    assert len(text.splitlines()) >= 4
