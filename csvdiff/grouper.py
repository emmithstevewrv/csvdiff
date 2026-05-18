"""Group diff results by a specified column value."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult


@dataclass
class GroupBucket:
    key_value: str
    added: List[dict] = field(default_factory=list)
    removed: List[dict] = field(default_factory=list)
    modified: List[Tuple[dict, dict]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    def __str__(self) -> str:
        return (
            f"GroupBucket({self.key_value!r}: "
            f"+{len(self.added)} -{len(self.removed)} ~{len(self.modified)})"
        )


@dataclass
class GroupResult:
    column: str
    buckets: Dict[str, GroupBucket] = field(default_factory=dict)

    def sorted_buckets(self) -> List[GroupBucket]:
        return sorted(self.buckets.values(), key=lambda b: b.total, reverse=True)

    @property
    def group_count(self) -> int:
        return len(self.buckets)


class RowGrouper:
    def __init__(self, column: str):
        if not column:
            raise ValueError("column must be a non-empty string")
        self.column = column

    def _get_value(self, row: dict) -> str:
        return row.get(self.column, "<missing>")

    def _bucket(self, result: GroupResult, value: str) -> GroupBucket:
        if value not in result.buckets:
            result.buckets[value] = GroupBucket(key_value=value)
        return result.buckets[value]

    def group(self, diff: DiffResult) -> GroupResult:
        result = GroupResult(column=self.column)

        for row in diff.added:
            val = self._get_value(row)
            self._bucket(result, val).added.append(row)

        for row in diff.removed:
            val = self._get_value(row)
            self._bucket(result, val).removed.append(row)

        for before, after in diff.modified:
            val = self._get_value(after)
            self._bucket(result, val).modified.append((before, after))

        return result
