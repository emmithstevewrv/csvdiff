"""Summary reporter for CSV diff results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult


@dataclass
class ReportStats:
    """Numeric summary of a diff result."""

    added: int
    removed: int
    modified: int
    unchanged: int
    total_left: int
    total_right: int

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.modified

    @property
    def change_rate(self) -> float:
        """Fraction of left-side rows that changed (0.0 – 1.0)."""
        if self.total_left == 0:
            return 0.0
        return self.total_changes / self.total_left


def compute_stats(result: DiffResult) -> ReportStats:
    """Derive :class:`ReportStats` from a :class:`DiffResult`."""
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)
    total_left = removed + len(result.unchanged) + modified
    total_right = added + len(result.unchanged) + modified
    unchanged = len(result.unchanged)
    return ReportStats(
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
        total_left=total_left,
        total_right=total_right,
    )


def format_summary(stats: ReportStats, *, verbose: bool = False) -> str:
    """Return a human-readable summary string."""
    lines = [
        f"Added:    {stats.added:>6}",
        f"Removed:  {stats.removed:>6}",
        f"Modified: {stats.modified:>6}",
    ]
    if verbose:
        lines += [
            f"Unchanged:{stats.unchanged:>6}",
            f"Left rows:{stats.total_left:>6}",
            f"Right rows:{stats.total_right:>5}",
            f"Change rate: {stats.change_rate:.1%}",
        ]
    lines.append(f"Total changes: {stats.total_changes}")
    return "\n".join(lines)
