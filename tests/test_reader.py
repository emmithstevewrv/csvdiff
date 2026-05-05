"""Tests for csvdiff.reader.CSVReader."""

import csv
import pytest
from pathlib import Path

from csvdiff.reader import CSVReader


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    """Create a simple CSV file for testing."""
    filepath = tmp_path / "sample.csv"
    rows = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "85"},
        {"id": "3", "name": "Carol", "score": "92"},
    ]
    with filepath.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["id", "name", "score"])
        writer.writeheader()
        writer.writerows(rows)
    return filepath


def test_load_returns_correct_headers(sample_csv: Path):
    reader = CSVReader(key_columns=["id"])
    headers, _ = reader.load(sample_csv)
    assert headers == ["id", "name", "score"]


def test_load_indexes_rows_by_single_key(sample_csv: Path):
    reader = CSVReader(key_columns=["id"])
    _, index = reader.load(sample_csv)
    assert ("1",) in index
    assert index[("2",)]["name"] == "Bob"
    assert len(index) == 3


def test_load_indexes_rows_by_composite_key(tmp_path: Path):
    filepath = tmp_path / "composite.csv"
    rows = [
        {"dept": "eng", "level": "1", "title": "Junior"},
        {"dept": "eng", "level": "2", "title": "Senior"},
        {"dept": "hr", "level": "1", "title": "Recruiter"},
    ]
    with filepath.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dept", "level", "title"])
        writer.writeheader()
        writer.writerows(rows)

    reader = CSVReader(key_columns=["dept", "level"])
    _, index = reader.load(filepath)
    assert ("eng", "2") in index
    assert index[("hr", "1")]["title"] == "Recruiter"


def test_load_raises_for_missing_file():
    reader = CSVReader(key_columns=["id"])
    with pytest.raises(FileNotFoundError):
        reader.load("/nonexistent/path/file.csv")


def test_load_raises_for_missing_key_column(sample_csv: Path):
    reader = CSVReader(key_columns=["nonexistent_col"])
    with pytest.raises(KeyError, match="nonexistent_col"):
        reader.load(sample_csv)


def test_constructor_raises_for_empty_key_columns():
    with pytest.raises(ValueError, match="At least one key column"):
        CSVReader(key_columns=[])
