"""Edge-case tests for csvdiff.truncator."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.truncator import TruncateConfig, truncate


@pytest.fixture
def empty_result():
    return DiffResult(added={}, removed={}, modified={})


def test_truncate_empty_result_no_change(empty_result):
    cfg = TruncateConfig(max_added=5, max_removed=5, max_modified=5)
    tr = truncate(empty_result, cfg)
    assert len(tr.result.added) == 0
    assert len(tr.result.removed) == 0
    assert len(tr.result.modified) == 0
    assert not tr.any_truncated


def test_truncate_zero_limit_removes_all():
    added = {(f"k{i}",): {"id": f"k{i}"} for i in range(5)}
    result = DiffResult(added=added, removed={}, modified={})
    cfg = TruncateConfig(max_added=0, max_removed=0, max_modified=0)
    tr = truncate(result, cfg)
    assert len(tr.result.added) == 0
    assert tr.added_truncated == 5


def test_truncate_exact_limit_no_truncation():
    added = {(f"k{i}",): {"id": f"k{i}"} for i in range(5)}
    result = DiffResult(added=added, removed={}, modified={})
    cfg = TruncateConfig(max_added=5, max_removed=5, max_modified=5)
    tr = truncate(result, cfg)
    assert len(tr.result.added) == 5
    assert tr.added_truncated == 0


def test_truncate_returns_new_diff_result(empty_result):
    cfg = TruncateConfig()
    tr = truncate(empty_result, cfg)
    assert isinstance(tr.result, DiffResult)


def test_truncate_config_defaults():
    cfg = TruncateConfig()
    assert cfg.max_added == 100
    assert cfg.max_removed == 100
    assert cfg.max_modified == 100


def test_summary_partial_truncation():
    added = {(f"a{i}",): {"id": f"a{i}"} for i in range(10)}
    result = DiffResult(added=added, removed={}, modified={})
    cfg = TruncateConfig(max_added=3, max_removed=100, max_modified=100)
    tr = truncate(result, cfg)
    summary = tr.summary()
    assert "added" in summary
    assert "removed" not in summary
    assert "modified" not in summary
