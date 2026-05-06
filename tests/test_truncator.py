"""Tests for csvdiff.truncator."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.truncator import TruncateConfig, TruncateResult, truncate, _truncate_dict


@pytest.fixture
def big_result():
    added = {(f"a{i}",): {"id": f"a{i}", "val": "x"} for i in range(20)}
    removed = {(f"r{i}",): {"id": f"r{i}", "val": "y"} for i in range(15)}
    modified = {
        (f"m{i}",): ({"id": f"m{i}", "val": "old"}, {"id": f"m{i}", "val": "new"})
        for i in range(10)
    }
    return DiffResult(added=added, removed=removed, modified=modified)


@pytest.fixture
def small_result():
    added = {("a1",): {"id": "a1", "val": "x"}}
    removed = {("r1",): {"id": "r1", "val": "y"}}
    modified = {("m1",): ({"id": "m1", "val": "old"}, {"id": "m1", "val": "new"})}
    return DiffResult(added=added, removed=removed, modified=modified)


def test_truncate_limits_added(big_result):
    cfg = TruncateConfig(max_added=5, max_removed=100, max_modified=100)
    tr = truncate(big_result, cfg)
    assert len(tr.result.added) == 5
    assert tr.added_truncated == 15


def test_truncate_limits_removed(big_result):
    cfg = TruncateConfig(max_added=100, max_removed=6, max_modified=100)
    tr = truncate(big_result, cfg)
    assert len(tr.result.removed) == 6
    assert tr.removed_truncated == 9


def test_truncate_limits_modified(big_result):
    cfg = TruncateConfig(max_added=100, max_removed=100, max_modified=3)
    tr = truncate(big_result, cfg)
    assert len(tr.result.modified) == 3
    assert tr.modified_truncated == 7


def test_no_truncation_when_within_limits(small_result):
    cfg = TruncateConfig(max_added=10, max_removed=10, max_modified=10)
    tr = truncate(small_result, cfg)
    assert tr.added_truncated == 0
    assert tr.removed_truncated == 0
    assert tr.modified_truncated == 0
    assert not tr.any_truncated


def test_any_truncated_flag(big_result):
    cfg = TruncateConfig(max_added=1, max_removed=100, max_modified=100)
    tr = truncate(big_result, cfg)
    assert tr.any_truncated


def test_summary_no_truncation(small_result):
    cfg = TruncateConfig(max_added=10, max_removed=10, max_modified=10)
    tr = truncate(small_result, cfg)
    assert tr.summary() == "no truncation"


def test_summary_with_truncation(big_result):
    cfg = TruncateConfig(max_added=5, max_removed=5, max_modified=5)
    tr = truncate(big_result, cfg)
    summary = tr.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "modified" in summary


def test_truncate_dict_negative_limit_raises():
    with pytest.raises(ValueError, match="non-negative"):
        _truncate_dict({"a": 1}, -1)


def test_truncate_does_not_mutate_original(big_result):
    original_added_count = len(big_result.added)
    cfg = TruncateConfig(max_added=2, max_removed=2, max_modified=2)
    truncate(big_result, cfg)
    # original should be unchanged
    assert len(big_result.added) == original_added_count
