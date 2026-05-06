"""Truncate diff output to a maximum number of rows per change category."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

from csvdiff.differ import DiffResult


@dataclass
class TruncateConfig:
    max_added: int = 100
    max_removed: int = 100
    max_modified: int = 100


@dataclass
class TruncateResult:
    result: DiffResult
    added_truncated: int = 0
    removed_truncated: int = 0
    modified_truncated: int = 0

    @property
    def any_truncated(self) -> bool:
        return (
            self.added_truncated > 0
            or self.removed_truncated > 0
            or self.modified_truncated > 0
        )

    def summary(self) -> str:
        parts = []
        if self.added_truncated:
            parts.append(f"{self.added_truncated} added row(s) omitted")
        if self.removed_truncated:
            parts.append(f"{self.removed_truncated} removed row(s) omitted")
        if self.modified_truncated:
            parts.append(f"{self.modified_truncated} modified row(s) omitted")
        return "; ".join(parts) if parts else "no truncation"


def truncate(result: DiffResult, config: TruncateConfig) -> TruncateResult:
    """Return a new DiffResult with each category capped to configured limits."""
    added = dict(result.added)
    removed = dict(result.removed)
    modified = dict(result.modified)

    added_truncated = _truncate_dict(added, config.max_added)
    removed_truncated = _truncate_dict(removed, config.max_removed)
    modified_truncated = _truncate_dict(modified, config.max_modified)

    truncated_result = DiffResult(
        added=added,
        removed=removed,
        modified=modified,
    )

    return TruncateResult(
        result=truncated_result,
        added_truncated=added_truncated,
        removed_truncated=removed_truncated,
        modified_truncated=modified_truncated,
    )


def _truncate_dict(d: dict, limit: int) -> int:
    """Truncate dict in-place to at most `limit` entries. Returns number removed."""
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")
    excess = len(d) - limit
    if excess <= 0:
        return 0
    keys_to_remove = list(d.keys())[limit:]
    for k in keys_to_remove:
        del d[k]
    return excess
