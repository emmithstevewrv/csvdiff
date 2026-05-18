"""Annotate each row in a diff result with a change type label."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult

CHANGE_ADDED = "added"
CHANGE_REMOVED = "removed"
CHANGE_MODIFIED = "modified"
CHANGE_UNCHANGED = "unchanged"


@dataclass
class AnnotatedRow:
    key: Tuple
    change_type: str
    before: Dict[str, str]
    after: Dict[str, str]

    def __str__(self) -> str:
        return f"[{self.change_type.upper()}] key={self.key}"


@dataclass
class AnnotationResult:
    rows: List[AnnotatedRow] = field(default_factory=list)

    def by_type(self, change_type: str) -> List[AnnotatedRow]:
        return [r for r in self.rows if r.change_type == change_type]

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {
            CHANGE_ADDED: 0,
            CHANGE_REMOVED: 0,
            CHANGE_MODIFIED: 0,
        }
        for row in self.rows:
            if row.change_type in counts:
                counts[row.change_type] += 1
        return counts


class RowAnnotator:
    """Produce a flat, labelled list of all changed rows from a DiffResult."""

    def annotate(self, result: DiffResult) -> AnnotationResult:
        rows: List[AnnotatedRow] = []

        for key, row in result.added.items():
            rows.append(AnnotatedRow(
                key=key,
                change_type=CHANGE_ADDED,
                before={},
                after=row,
            ))

        for key, row in result.removed.items():
            rows.append(AnnotatedRow(
                key=key,
                change_type=CHANGE_REMOVED,
                before=row,
                after={},
            ))

        for key, (before, after) in result.modified.items():
            rows.append(AnnotatedRow(
                key=key,
                change_type=CHANGE_MODIFIED,
                before=before,
                after=after,
            ))

        return AnnotationResult(rows=rows)
