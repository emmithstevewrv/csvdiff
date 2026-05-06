"""Tests for csvdiff.reporter."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.reporter import ReportStats, compute_stats, format_summary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def full_result() -> DiffResult:
    return DiffResult(
        added=[("e",), ("f",)],
        removed=[("a",)],
        modified=[("b",)],
        unchanged=[("c",), ("d",)],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_compute_stats_counts(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    assert stats.added == 2
    assert stats.removed == 1
    assert stats.modified == 1
    assert stats.unchanged == 2


def test_compute_stats_totals(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    # left = removed + unchanged + modified = 1 + 2 + 1
    assert stats.total_left == 4
    # right = added + unchanged + modified = 2 + 2 + 1
    assert stats.total_right == 5


def test_total_changes(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    assert stats.total_changes == 4  # 2 added + 1 removed + 1 modified


def test_change_rate(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    # 4 changes / 4 left rows = 1.0
    assert stats.change_rate == pytest.approx(1.0)


def test_change_rate_zero_left(empty_result: DiffResult) -> None:
    stats = compute_stats(empty_result)
    assert stats.change_rate == 0.0


# ---------------------------------------------------------------------------
# format_summary
# ---------------------------------------------------------------------------

def test_format_summary_contains_counts(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    text = format_summary(stats)
    assert "2" in text   # added
    assert "1" in text   # removed / modified
    assert "Total changes: 4" in text


def test_format_summary_verbose_includes_extra(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    text = format_summary(stats, verbose=True)
    assert "Unchanged" in text
    assert "Change rate" in text
    assert "Left rows" in text


def test_format_summary_no_verbose_omits_extra(full_result: DiffResult) -> None:
    stats = compute_stats(full_result)
    text = format_summary(stats, verbose=False)
    assert "Change rate" not in text
    assert "Unchanged" not in text
