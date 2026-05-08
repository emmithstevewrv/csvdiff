"""Tests for csvdiff.splitter."""
import pytest

from csvdiff.differ import DiffResult
from csvdiff.splitter import ColumnBucket, DiffSplitter, SplitResult


@pytest.fixture()
def result_with_mods() -> DiffResult:
    r = DiffResult()
    r.modified["1"] = (
        {"id": "1", "name": "Alice", "score": "80"},
        {"id": "1", "name": "Alice", "score": "95"},
    )
    r.modified["2"] = (
        {"id": "2", "name": "Bob", "score": "70"},
        {"id": "2", "name": "Robert", "score": "70"},
    )
    r.modified["3"] = (
        {"id": "3", "name": "Carol", "score": "60"},
        {"id": "3", "name": "Caroline", "score": "90"},
    )
    return r


def test_split_creates_bucket_per_changed_column(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    assert "score" in sr.columns()
    assert "name" in sr.columns()


def test_split_score_bucket_has_correct_count(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    # rows 1 and 3 changed score
    assert sr.get("score").count == 2


def test_split_name_bucket_has_correct_count(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    # rows 2 and 3 changed name
    assert sr.get("name").count == 2


def test_split_key_column_not_in_buckets(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    assert "id" not in sr.columns()


def test_split_empty_modified_returns_empty_split():
    r = DiffResult()
    r.added["x"] = {"id": "x", "val": "1"}
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(r)
    assert sr.columns() == []
    assert sr.total_pairs() == 0


def test_before_and_after_values(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    bucket = sr.get("score")
    assert "80" in bucket.before_values() or "60" in bucket.before_values()
    assert "95" in bucket.after_values() or "90" in bucket.after_values()


def test_get_unknown_column_raises(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    with pytest.raises(KeyError):
        sr.get("nonexistent")


def test_empty_key_columns_raises():
    with pytest.raises(ValueError):
        DiffSplitter(key_columns=[])


def test_total_pairs_sums_all_buckets(result_with_mods):
    splitter = DiffSplitter(key_columns=["id"])
    sr = splitter.split(result_with_mods)
    # score: 2 pairs, name: 2 pairs
    assert sr.total_pairs() == 4


def test_composite_key_excluded_from_buckets():
    r = DiffResult()
    r.modified["A|1"] = (
        {"grp": "A", "seq": "1", "val": "old"},
        {"grp": "A", "seq": "1", "val": "new"},
    )
    splitter = DiffSplitter(key_columns=["grp", "seq"])
    sr = splitter.split(r)
    assert "grp" not in sr.columns()
    assert "seq" not in sr.columns()
    assert "val" in sr.columns()
