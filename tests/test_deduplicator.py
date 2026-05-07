"""Tests for csvdiff.deduplicator."""
import pytest
from csvdiff.deduplicator import Deduplicator, DuplicateReport


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "score": "10"},
        {"id": "2", "name": "Bob",   "score": "20"},
        {"id": "1", "name": "Alice2", "score": "30"},  # duplicate id=1
        {"id": "3", "name": "Carol", "score": "40"},
        {"id": "2", "name": "Bob2",  "score": "50"},  # duplicate id=2
        {"id": "2", "name": "Bob3",  "score": "60"},  # third row for id=2
    ]


@pytest.fixture
def unique_rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


# ---------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------

def test_empty_key_columns_raises():
    with pytest.raises(ValueError, match="key_columns must not be empty"):
        Deduplicator([])


# ---------------------------------------------------------------------------
# find_duplicates
# ---------------------------------------------------------------------------

def test_no_duplicates_returns_empty_report(unique_rows):
    d = Deduplicator(["id"])
    report = d.find_duplicates(unique_rows)
    assert not report.has_duplicates
    assert report.duplicate_key_count == 0
    assert report.total_affected_rows == 0


def test_detects_single_key_duplicates(rows):
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    assert report.has_duplicates
    assert report.duplicate_key_count == 2  # id=1 and id=2


def test_affected_rows_count(rows):
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    # id=1 has 2 rows, id=2 has 3 rows → 5 total
    assert report.total_affected_rows == 5


def test_composite_key_deduplication():
    data = [
        {"a": "x", "b": "1", "val": "foo"},
        {"a": "x", "b": "1", "val": "bar"},  # duplicate (x,1)
        {"a": "x", "b": "2", "val": "baz"},
    ]
    d = Deduplicator(["a", "b"])
    report = d.find_duplicates(data)
    assert report.duplicate_key_count == 1
    assert ("x", "1") in report.duplicates


def test_missing_key_column_raises():
    data = [{"id": "1", "name": "Alice"}]
    d = Deduplicator(["id", "missing_col"])
    with pytest.raises(KeyError):
        d.find_duplicates(data)


def test_summary_no_duplicates(unique_rows):
    d = Deduplicator(["id"])
    report = d.find_duplicates(unique_rows)
    assert "No duplicate" in report.summary()


def test_summary_with_duplicates(rows):
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    summary = report.summary()
    assert "duplicate key" in summary.lower()
    assert "id=1" in summary or "1" in summary


def test_empty_row_list_returns_empty_report():
    d = Deduplicator(["id"])
    report = d.find_duplicates([])
    assert not report.has_duplicates
