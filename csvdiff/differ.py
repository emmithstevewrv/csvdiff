"""Core diff logic for comparing two CSV datasets."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiffResult:
    added: list[dict[str, Any]] = field(default_factory=list)
    removed: list[dict[str, Any]] = field(default_factory=list)
    modified: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        return (
            f"Added: {len(self.added)}, "
            f"Removed: {len(self.removed)}, "
            f"Modified: {len(self.modified)}"
        )


def diff(
    left: dict[tuple, dict[str, Any]],
    right: dict[tuple, dict[str, Any]],
    columns: list[str] | None = None,
) -> DiffResult:
    """Compare two indexed CSV datasets and return a DiffResult.

    Args:
        left: Row dict indexed by key tuples (from CSVReader.load).
        right: Row dict indexed by key tuples (from CSVReader.load).
        columns: Optional list of columns to restrict comparison to.

    Returns:
        DiffResult with added, removed, and modified rows.
    """
    result = DiffResult()

    left_keys = set(left.keys())
    right_keys = set(right.keys())

    for key in right_keys - left_keys:
        result.added.append(right[key])

    for key in left_keys - right_keys:
        result.removed.append(left[key])

    for key in left_keys & right_keys:
        left_row = left[key]
        right_row = right[key]
        compare_cols = columns if columns else list(left_row.keys())
        changes = {
            col: {"old": left_row.get(col), "new": right_row.get(col)}
            for col in compare_cols
            if left_row.get(col) != right_row.get(col)
        }
        if changes:
            result.modified.append(
                {"key": key, "changes": changes, "row": right_row}
            )

    return result
