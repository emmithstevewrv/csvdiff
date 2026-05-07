"""Integration tests: ColumnAligner used alongside CSVReader and differ."""

import io
import csv
from typing import Dict, Tuple

import pytest

from csvdiff.aligner import ColumnAligner
from csvdiff.differ import diff


def _build_index(rows, key_columns):
    """Minimal helper: build a key -> row dict from a list of row dicts."""
    index = {}
    for row in rows:
        key = tuple(row[k] for k in key_columns)
        index[key] = row
    return index


def _parse(text):
    reader = csv.DictReader(io.StringIO(text.strip()))
    return list(reader.fieldnames or []), list(reader)


LEFT_CSV = """
id,name,age
1,Alice,30
2,Bob,25
"""

RIGHT_CSV = """
id,age,name
1,30,Alice
2,26,Bob
"""


def test_aligner_detects_reorder_between_files():
    left_headers, _ = _parse(LEFT_CSV)
    right_headers, _ = _parse(RIGHT_CSV)
    aligner = ColumnAligner(key_columns=["id"])
    result = aligner.align(left_headers, right_headers)
    assert result.reordered is True
    assert result.left_only == []
    assert result.right_only == []


def test_aligner_remap_enables_clean_diff():
    left_headers, left_rows = _parse(LEFT_CSV)
    right_headers, right_rows = _parse(RIGHT_CSV)
    aligner = ColumnAligner(key_columns=["id"])
    alignment = aligner.align(left_headers, right_headers)

    left_index = _build_index(left_rows, ["id"])
    right_index = _build_index(
        [aligner.remap_row(r, alignment.common) for r in right_rows], ["id"]
    )
    left_index_remapped = aligner.remap_index(left_index, alignment.common)

    result = diff(left_index_remapped, right_index)
    # Bob's age changed from 25 -> 26; Alice unchanged
    assert len(result.modified) == 1
    assert len(result.added) == 0
    assert len(result.removed) == 0


def test_aligner_with_extra_column_on_right():
    _, left_rows = _parse("id,name\n1,Alice\n")
    _, right_rows = _parse("id,name,score\n1,Alice\n")
    aligner = ColumnAligner(key_columns=["id"])
    alignment = aligner.align(["id", "name"], ["id", "name", "score"])
    assert alignment.right_only == ["score"]
    assert not alignment.aligned
