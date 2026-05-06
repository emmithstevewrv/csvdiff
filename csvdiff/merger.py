"""Merge a diff result back into a base CSV index, producing an updated index."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult


Key = Tuple[str, ...]
Row = Dict[str, str]
Index = Dict[Key, Row]


@dataclass
class MergeResult:
    """Outcome of merging a diff into a base index."""

    index: Index = field(default_factory=dict)
    applied_added: int = 0
    applied_removed: int = 0
    applied_modified: int = 0

    @property
    def total_applied(self) -> int:
        return self.applied_added + self.applied_removed + self.applied_modified


class MergeError(Exception):
    """Raised when the merge cannot be applied cleanly."""


def merge(base: Index, diff: DiffResult) -> MergeResult:
    """Apply *diff* on top of *base* and return a :class:`MergeResult`.

    Raises
    ------
    MergeError
        If an added row already exists in *base*, or a removed / modified row
        is missing from *base*.
    """
    result_index: Index = dict(base)
    applied_added = 0
    applied_removed = 0
    applied_modified = 0

    for key, row in diff.added.items():
        if key in result_index:
            raise MergeError(
                f"Cannot add row {key!r}: key already exists in base."
            )
        result_index[key] = row
        applied_added += 1

    for key in diff.removed:
        if key not in result_index:
            raise MergeError(
                f"Cannot remove row {key!r}: key not found in base."
            )
        del result_index[key]
        applied_removed += 1

    for key, (_, new_row) in diff.modified.items():
        if key not in result_index:
            raise MergeError(
                f"Cannot modify row {key!r}: key not found in base."
            )
        result_index[key] = new_row
        applied_modified += 1

    return MergeResult(
        index=result_index,
        applied_added=applied_added,
        applied_removed=applied_removed,
        applied_modified=applied_modified,
    )


def to_rows(merge_result: MergeResult, headers: List[str]) -> List[Dict[str, str]]:
    """Return the merged index as an ordered list of row dicts."""
    return [
        {h: row.get(h, "") for h in headers}
        for row in merge_result.index.values()
    ]
