"""Detect and report duplicate key rows within a CSV index."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DuplicateReport:
    """Holds duplicate key findings for one side of a diff."""

    duplicates: Dict[Tuple, List[dict]] = field(default_factory=dict)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    @property
    def total_affected_rows(self) -> int:
        """Total number of rows involved in any duplication."""
        return sum(len(rows) for rows in self.duplicates.values())

    @property
    def duplicate_key_count(self) -> int:
        return len(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = [f"Found {self.duplicate_key_count} duplicate key(s):"]
        for key, rows in self.duplicates.items():
            key_str = ", ".join(str(k) for k in key)
            lines.append(f"  key=({key_str}): {len(rows)} rows")
        return "\n".join(lines)


class Deduplicator:
    """Scans a row index for duplicate composite keys."""

    def __init__(self, key_columns: List[str]) -> None:
        if not key_columns:
            raise ValueError("key_columns must not be empty")
        self.key_columns = key_columns

    def _make_key(self, row: dict) -> Tuple:
        try:
            return tuple(row[col] for col in self.key_columns)
        except KeyError as exc:
            raise KeyError(f"Key column {exc} not found in row") from exc

    def find_duplicates(self, rows: List[dict]) -> DuplicateReport:
        """Return a DuplicateReport for the given list of row dicts."""
        seen: Dict[Tuple, List[dict]] = {}
        for row in rows:
            key = self._make_key(row)
            seen.setdefault(key, []).append(row)

        duplicates = {k: v for k, v in seen.items() if len(v) > 1}
        return DuplicateReport(duplicates=duplicates)
