"""Build and query an inverted index mapping column values to row keys."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple


RowIndex = Dict[Tuple, Dict[str, str]]
InvertedIndex = Dict[str, Dict[str, List[Tuple]]]


class ColumnIndexer:
    """Builds an inverted index from a row index for fast column-value lookups."""

    def __init__(self, columns: List[str]) -> None:
        if not columns:
            raise ValueError("columns must not be empty")
        self._columns = list(columns)
        self._index: InvertedIndex = {col: defaultdict(list) for col in columns}

    @property
    def columns(self) -> List[str]:
        return list(self._columns)

    def build(self, row_index: RowIndex) -> None:
        """Populate the inverted index from *row_index*."""
        # Reset before rebuilding
        self._index = {col: defaultdict(list) for col in self._columns}
        for key, row in row_index.items():
            for col in self._columns:
                value = row.get(col, "")
                self._index[col][value].append(key)

    def lookup(self, column: str, value: str) -> List[Tuple]:
        """Return all row keys where *column* equals *value*."""
        if column not in self._index:
            raise KeyError(f"Column {column!r} is not indexed")
        return list(self._index[column].get(value, []))

    def unique_values(self, column: str) -> List[str]:
        """Return sorted unique values present for *column*."""
        if column not in self._index:
            raise KeyError(f"Column {column!r} is not indexed")
        return sorted(self._index[column].keys())

    def value_counts(self, column: str) -> Dict[str, int]:
        """Return a mapping of value -> number of rows for *column*."""
        if column not in self._index:
            raise KeyError(f"Column {column!r} is not indexed")
        return {v: len(keys) for v, keys in self._index[column].items()}
