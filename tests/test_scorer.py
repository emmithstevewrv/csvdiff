"""Tests for csvdiff.scorer."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.scorer import RowScore, ScorerResult, score_diff


@pytest.fixture()
def diff_result() -> DiffResult:
    return DiffResult(
        added={},
        removed={},
        modified={
            "1": (
                {"id": "1", "name": "Alice", "city": "NY",  "age": "30"},
                {"id": "1", "name": "Alice", "city": "LA",  "age": "31"},
            ),
            "2": (
                {"id": "2", "name": "Bob",   "city": "NY",  "age": "25"},
                {"id": "2", "name": "Robert","city": "NY",  "age": "25"},
            ),
            "3": (
                {"id": "3", "name": "Carol", "city": "SF",  "age": "40"},
                {"id": "3", "name": "Carol", "city": "SF",  "age": "40"},
            ),
        },
    )


@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={})


def test_score_diff_returns_scorer_result(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    assert isinstance(result, ScorerResult)


def test_score_diff_counts_modified_rows(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    assert len(result.scores) == 3


def test_score_diff_correct_changed_count(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    scores_by_key = {r.key: r for r in result.scores}

    assert scores_by_key["1"].changed_count == 2   # city + age
    assert scores_by_key["2"].changed_count == 1   # name only
    assert scores_by_key["3"].changed_count == 0   # no change


def test_score_values_between_zero_and_one(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    for row in result.scores:
        assert 0.0 <= row.score <= 1.0


def test_top_returns_highest_scores_first(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    top = result.top(2)
    assert len(top) == 2
    assert top[0].score >= top[1].score


def test_top_respects_n_limit(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    assert len(result.top(1)) == 1


def test_average_score_empty_result(empty_diff):
    result = score_diff(empty_diff, key_columns=["id"])
    assert result.average_score() == 0.0


def test_average_score_non_empty(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    avg = result.average_score()
    assert 0.0 < avg <= 1.0


def test_row_score_str_contains_key(diff_result):
    result = score_diff(diff_result, key_columns=["id"])
    scores_by_key = {r.key: r for r in result.scores}
    assert "1" in str(scores_by_key["1"])


def test_key_columns_excluded_from_total(diff_result):
    """Key columns must not count toward total_count."""
    result = score_diff(diff_result, key_columns=["id"])
    for row in result.scores:
        assert row.total_count == 3  # name, city, age
