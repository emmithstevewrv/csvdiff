"""Summarizer: produce a human-readable summary of a DiffResult."""

from dataclasses import dataclass
from typing import List

from csvdiff.differ import DiffResult


@dataclass
class SummaryLine:
    label: str
    count: int
    detail: str = ""

    def __str__(self) -> str:
        base = f"{self.label}: {self.count}"
        return f"{base} ({self.detail})" if self.detail else base


@dataclass
class DiffSummary:
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
        base = max(self.total_left, self.total_right)
        return round(self.total_changes / base, 4) if base else 0.0

    def lines(self) -> List[SummaryLine]:
        return [
            SummaryLine("Added", self.added),
            SummaryLine("Removed", self.removed),
            SummaryLine("Modified", self.modified),
            SummaryLine("Unchanged", self.unchanged),
            SummaryLine(
                "Change rate",
                0,
                f"{self.change_rate * 100:.2f}%",
            ),
        ]

    def __str__(self) -> str:
        parts = [
            f"Added:    {self.added}",
            f"Removed:  {self.removed}",
            f"Modified: {self.modified}",
            f"Unchanged:{self.unchanged}",
            f"Rate:     {self.change_rate * 100:.2f}%",
        ]
        return "\n".join(parts)


def summarize(result: DiffResult, total_left: int, total_right: int) -> DiffSummary:
    """Build a DiffSummary from a DiffResult and row counts."""
    added = len(result.added)
    removed = len(result.removed)
    modified = len(result.modified)
    unchanged = total_left - removed - modified
    return DiffSummary(
        added=added,
        removed=removed,
        modified=modified,
        unchanged=max(unchanged, 0),
        total_left=total_left,
        total_right=total_right,
    )
