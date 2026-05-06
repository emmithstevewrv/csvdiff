"""Core diffing logic for CSV data indexed by key columns."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any


@dataclass
class DiffResult:
    added: Dict[Tuple, Dict[str, str]] = field(default_factory=dict)
    removed: Dict[Tuple, Dict[str, str]] = field(default_factory=dict)
    modified: Dict[Tuple, Tuple[Dict[str, str], Dict[str, str]]] = field(
        default_factory=dict
    )

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.modified:
            parts.append(f"~{len(self.modified)} modified")
        return ", ".join(parts) if parts else "no changes"


def has_changes(result: DiffResult) -> bool:
    return result.has_changes()


def summary(result: DiffResult) -> str:
    return result.summary()


def diff(
    left: Dict[Tuple, Dict[str, str]],
    right: Dict[Tuple, Dict[str, str]],
) -> DiffResult:
    """Compute the diff between two indexed CSV datasets."""
    left_keys = set(left.keys())
    right_keys = set(right.keys())

    added_keys = right_keys - left_keys
    removed_keys = left_keys - right_keys
    common_keys = left_keys & right_keys

    added = {k: right[k] for k in added_keys}
    removed = {k: left[k] for k in removed_keys}
    modified = {
        k: (left[k], right[k])
        for k in common_keys
        if left[k] != right[k]
    }

    return DiffResult(added=added, removed=removed, modified=modified)
