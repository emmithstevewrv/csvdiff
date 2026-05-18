"""Classify diff rows by change severity based on number of modified fields."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from csvdiff.differ import DiffResult


SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"


@dataclass
class ClassifiedRow:
    key: Tuple
    severity: str
    changed_field_count: int
    before: Dict[str, str]
    after: Dict[str, str]

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] key={self.key} fields_changed={self.changed_field_count}"


@dataclass
class ClassifyResult:
    rows: List[ClassifiedRow] = field(default_factory=list)

    def by_severity(self, severity: str) -> List[ClassifiedRow]:
        return [r for r in self.rows if r.severity == severity]

    @property
    def low(self) -> List[ClassifiedRow]:
        return self.by_severity(SEVERITY_LOW)

    @property
    def medium(self) -> List[ClassifiedRow]:
        return self.by_severity(SEVERITY_MEDIUM)

    @property
    def high(self) -> List[ClassifiedRow]:
        return self.by_severity(SEVERITY_HIGH)

    def summary(self) -> str:
        return (
            f"low={len(self.low)} "
            f"medium={len(self.medium)} "
            f"high={len(self.high)}"
        )


def _severity(changed: int, low_max: int, medium_max: int) -> str:
    if changed <= low_max:
        return SEVERITY_LOW
    if changed <= medium_max:
        return SEVERITY_MEDIUM
    return SEVERITY_HIGH


def classify(
    result: DiffResult,
    key_columns: List[str],
    low_max: int = 1,
    medium_max: int = 3,
) -> ClassifyResult:
    """Classify each modified row by how many fields changed."""
    classified: List[ClassifiedRow] = []
    for key, (before, after) in result.modified.items():
        changed = sum(
            1 for col in after
            if col not in key_columns and before.get(col) != after.get(col)
        )
        sev = _severity(changed, low_max, medium_max)
        classified.append(ClassifiedRow(
            key=key,
            severity=sev,
            changed_field_count=changed,
            before=before,
            after=after,
        ))
    return ClassifyResult(rows=classified)
