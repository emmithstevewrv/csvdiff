"""Flatten a DiffResult into a list of uniform row dicts with a change-type tag."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from csvdiff.differ import DiffResult

CHANGE_TYPE_KEY = "_change_type"


@dataclass
class FlatRow:
    """A single row from the diff with an attached change-type label."""

    change_type: str  # 'added' | 'removed' | 'modified_before' | 'modified_after'
    key: str
    data: Dict[str, str]

    def __str__(self) -> str:
        return f"[{self.change_type}] {self.key}: {self.data}"


@dataclass
class FlattenResult:
    rows: List[FlatRow] = field(default_factory=list)

    def by_type(self, change_type: str) -> List[FlatRow]:
        return [r for r in self.rows if r.change_type == change_type]

    @property
    def total(self) -> int:
        return len(self.rows)

    def to_dicts(self, include_key: bool = True) -> List[Dict[str, str]]:
        """Return each row as a plain dict, optionally including the key and tag."""
        result = []
        for row in self.rows:
            entry = {CHANGE_TYPE_KEY: row.change_type}
            if include_key:
                entry["_key"] = row.key
            entry.update(row.data)
            result.append(entry)
        return result


def flatten(diff: DiffResult, include_modified_before: bool = True) -> FlattenResult:
    """Convert a DiffResult into a flat list of FlatRow objects.

    Args:
        diff: The DiffResult to flatten.
        include_modified_before: When True, emit a 'modified_before' row in
            addition to the 'modified_after' row for every modified entry.
    """
    rows: List[FlatRow] = []

    for key, row in diff.added.items():
        rows.append(FlatRow(change_type="added", key=key, data=dict(row)))

    for key, row in diff.removed.items():
        rows.append(FlatRow(change_type="removed", key=key, data=dict(row)))

    for key, (before, after) in diff.modified.items():
        if include_modified_before:
            rows.append(FlatRow(change_type="modified_before", key=key, data=dict(before)))
        rows.append(FlatRow(change_type="modified_after", key=key, data=dict(after)))

    return FlattenResult(rows=rows)
