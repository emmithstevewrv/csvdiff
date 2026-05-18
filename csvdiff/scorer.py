"""Row similarity scorer for ranking diff results by change magnitude."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult


@dataclass
class RowScore:
    key: str
    before: Dict[str, str]
    after: Dict[str, str]
    changed_count: int
    total_count: int

    @property
    def score(self) -> float:
        """Fraction of columns that changed (0.0 – 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.changed_count / self.total_count

    def __str__(self) -> str:
        return f"{self.key}: {self.changed_count}/{self.total_count} columns changed ({self.score:.0%})"


@dataclass
class ScorerResult:
    scores: List[RowScore] = field(default_factory=list)

    def top(self, n: int = 10) -> List[RowScore]:
        """Return the *n* rows with the highest change scores."""
        return sorted(self.scores, key=lambda r: r.score, reverse=True)[:n]

    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(r.score for r in self.scores) / len(self.scores)


def score_diff(result: DiffResult, key_columns: List[str]) -> ScorerResult:
    """Score every modified row in *result* by the fraction of changed columns."""
    scored: List[RowScore] = []

    for key, (before, after) in result.modified.items():
        all_cols = [c for c in before if c not in key_columns]
        if not all_cols:
            continue
        changed = sum(1 for c in all_cols if before.get(c) != after.get(c))
        scored.append(
            RowScore(
                key=key,
                before=before,
                after=after,
                changed_count=changed,
                total_count=len(all_cols),
            )
        )

    return ScorerResult(scores=scored)
