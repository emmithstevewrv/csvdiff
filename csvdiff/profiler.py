"""Profile a DiffResult to produce column-level change statistics."""

from dataclasses import dataclass, field
from typing import Dict, List
from csvdiff.differ import DiffResult


@dataclass
class ColumnProfile:
    """Change statistics for a single column."""
    name: str
    change_count: int = 0
    change_rate: float = 0.0

    def __str__(self) -> str:
        return f"{self.name}: {self.change_count} change(s) ({self.change_rate:.1%})"


@dataclass
class ProfileResult:
    """Aggregated column-level diff profile."""
    total_modified: int
    columns: List[ColumnProfile] = field(default_factory=list)

    def most_changed(self) -> List[ColumnProfile]:
        """Return columns sorted by change count descending."""
        return sorted(self.columns, key=lambda c: c.change_count, reverse=True)

    def as_dict(self) -> Dict[str, int]:
        return {c.name: c.change_count for c in self.columns}


class DiffProfiler:
    """Compute per-column change frequencies from a DiffResult."""

    def __init__(self, result: DiffResult) -> None:
        self._result = result

    def profile(self) -> ProfileResult:
        """Analyse modified rows and count per-column changes."""
        modified = self._result.modified
        total = len(modified)
        counts: Dict[str, int] = {}

        for key, (before, after) in modified.items():
            for col in after:
                if before.get(col) != after.get(col):
                    counts[col] = counts.get(col, 0) + 1

        columns = [
            ColumnProfile(
                name=col,
                change_count=cnt,
                change_rate=(cnt / total) if total > 0 else 0.0,
            )
            for col, cnt in counts.items()
        ]

        return ProfileResult(total_modified=total, columns=columns)
