"""Split a DiffResult into per-column change buckets for targeted analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult


@dataclass
class ColumnBucket:
    """Holds modified row pairs that changed a specific column."""
    column: str
    pairs: List[Tuple[dict, dict]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.pairs)

    def before_values(self) -> List[str]:
        return [before[self.column] for before, _ in self.pairs]

    def after_values(self) -> List[str]:
        return [after[self.column] for _, after in self.pairs]


@dataclass
class SplitResult:
    """Result of splitting a DiffResult by changed column."""
    buckets: Dict[str, ColumnBucket] = field(default_factory=dict)

    def columns(self) -> List[str]:
        return sorted(self.buckets.keys())

    def get(self, column: str) -> ColumnBucket:
        if column not in self.buckets:
            raise KeyError(f"No bucket for column '{column}'")
        return self.buckets[column]

    def total_pairs(self) -> int:
        return sum(b.count for b in self.buckets.values())


class DiffSplitter:
    """Splits a DiffResult's modified rows into per-column buckets."""

    def __init__(self, key_columns: List[str]) -> None:
        if not key_columns:
            raise ValueError("key_columns must not be empty")
        self._keys = set(key_columns)

    def split(self, result: DiffResult) -> SplitResult:
        """Return a SplitResult grouping modified pairs by changed column."""
        split = SplitResult()
        for key, (before, after) in result.modified.items():
            for col in after:
                if col in self._keys:
                    continue
                if before.get(col) != after.get(col):
                    if col not in split.buckets:
                        split.buckets[col] = ColumnBucket(column=col)
                    split.buckets[col].pairs.append((before, after))
        return split
