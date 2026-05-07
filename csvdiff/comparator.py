"""Column-level value comparator with configurable tolerance for numeric fields."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CompareConfig:
    numeric_tolerance: float = 0.0
    case_sensitive: bool = True
    ignore_whitespace: bool = False
    numeric_columns: list = field(default_factory=list)


@dataclass
class CompareResult:
    column: str
    left: str
    right: str
    equal: bool
    reason: Optional[str] = None

    def __str__(self) -> str:
        status = "=" if self.equal else "≠"
        return f"{self.column}: {self.left!r} {status} {self.right!r}"


class ColumnComparator:
    def __init__(self, config: Optional[CompareConfig] = None):
        self._cfg = config or CompareConfig()

    def compare(self, column: str, left: str, right: str) -> CompareResult:
        lv, rv = left, right

        if self._cfg.ignore_whitespace:
            lv, rv = lv.strip(), rv.strip()

        if not self._cfg.case_sensitive:
            lv, rv = lv.lower(), rv.lower()

        if column in self._cfg.numeric_columns or self._cfg.numeric_tolerance > 0:
            result = self._numeric_compare(column, lv, rv)
            if result is not None:
                return result

        equal = lv == rv
        reason = None if equal else "string mismatch"
        return CompareResult(column=column, left=left, right=right, equal=equal, reason=reason)

    def _numeric_compare(self, column: str, left: str, right: str) -> Optional[CompareResult]:
        try:
            lf, rf = float(left), float(right)
        except ValueError:
            return None

        diff = abs(lf - rf)
        equal = diff <= self._cfg.numeric_tolerance
        reason = None if equal else f"numeric diff {diff} exceeds tolerance {self._cfg.numeric_tolerance}"
        return CompareResult(column=column, left=left, right=right, equal=equal, reason=reason)

    def compare_rows(
        self,
        left_row: dict,
        right_row: dict,
        columns: Optional[list] = None,
        key_columns: Optional[list] = None,
    ) -> list:
        cols = columns or list(left_row.keys())
        skip = set(key_columns or [])
        return [
            self.compare(col, left_row.get(col, ""), right_row.get(col, ""))
            for col in cols
            if col not in skip
        ]
