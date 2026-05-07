"""Integration tests: profiler wired to a real DiffResult produced by the differ."""

from csvdiff.differ import compute_diff
from csvdiff.profiler import DiffProfiler


def _index(rows, key="id"):
    return {(r[key],): r for r in rows}


def test_profiler_via_differ_detects_column():
    left = _index([
        {"id": "1", "city": "London", "pop": "9000000"},
        {"id": "2", "city": "Paris",  "pop": "2100000"},
    ])
    right = _index([
        {"id": "1", "city": "London", "pop": "9500000"},  # pop changed
        {"id": "2", "city": "Paris",  "pop": "2100000"},
    ])
    result = compute_diff(left, right)
    pr = DiffProfiler(result).profile()
    assert pr.total_modified == 1
    assert pr.as_dict().get("pop") == 1
    assert "city" not in pr.as_dict()


def test_profiler_via_differ_multiple_columns():
    left = _index([
        {"id": "1", "a": "x", "b": "y"},
        {"id": "2", "a": "p", "b": "q"},
    ])
    right = _index([
        {"id": "1", "a": "X", "b": "Y"},  # both columns changed
        {"id": "2", "a": "p", "b": "Q"},  # only b changed
    ])
    result = compute_diff(left, right)
    pr = DiffProfiler(result).profile()
    d = pr.as_dict()
    assert d["a"] == 1
    assert d["b"] == 2


def test_profiler_no_modifications_when_only_additions():
    left = _index([{"id": "1", "val": "a"}])
    right = _index([
        {"id": "1", "val": "a"},
        {"id": "2", "val": "b"},
    ])
    result = compute_diff(left, right)
    pr = DiffProfiler(result).profile()
    assert pr.total_modified == 0
    assert pr.columns == []
