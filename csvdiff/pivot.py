"""Pivot diff results by a column to summarise changes per unique value."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult


@dataclass
class PivotBucket:
    """Aggregated change counts for a single pivot value."""

    value: str
    added: int = 0
    removed: int = 0
    modified: int = 0

    @property
    def total(self) -> int:
        return self.added + self.removed + self.modified

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"{self.value}: +{self.added} -{self.removed} ~{self.modified}"
        )


@dataclass
class PivotResult:
    """Collection of pivot buckets keyed by pivot column value."""

    column: str
    buckets: Dict[str, PivotBucket] = field(default_factory=dict)

    def sorted_buckets(self, by: str = "total") -> List[PivotBucket]:
        """Return buckets sorted descending by *by* attribute."""
        return sorted(
            self.buckets.values(), key=lambda b: getattr(b, by), reverse=True
        )

    def grand_total(self) -> int:
        return sum(b.total for b in self.buckets.values())


def pivot(
    result: DiffResult,
    column: str,
    key_columns: List[str],
) -> PivotResult:
    """Pivot *result* by *column*, counting changes per unique column value.

    Rows that do not contain *column* are skipped silently.
    """
    pr = PivotResult(column=column)

    def _bucket(value: str) -> PivotBucket:
        if value not in pr.buckets:
            pr.buckets[value] = PivotBucket(value=value)
        return pr.buckets[value]

    for key, row in result.added.items():
        if column in row:
            _bucket(row[column]).added += 1

    for key, row in result.removed.items():
        if column in row:
            _bucket(row[column]).removed += 1

    for key, (before, after) in result.modified.items():
        # Prefer the *after* value for the pivot column
        row = after if column in after else before
        if column in row:
            _bucket(row[column]).modified += 1

    return pr
