"""Column alignment utilities for comparing CSVs with differing column orders."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AlignmentResult:
    left_headers: List[str]
    right_headers: List[str]
    common: List[str]
    left_only: List[str]
    right_only: List[str]
    reordered: bool

    @property
    def aligned(self) -> bool:
        """True if both sides share all columns in the same order."""
        return not self.left_only and not self.right_only and not self.reordered

    def summary(self) -> str:
        parts = []
        if self.left_only:
            parts.append(f"left-only columns: {self.left_only}")
        if self.right_only:
            parts.append(f"right-only columns: {self.right_only}")
        if self.reordered:
            parts.append("column order differs")
        return "; ".join(parts) if parts else "columns aligned"


class ColumnAligner:
    """Aligns two sets of headers and remaps rows to a canonical column order."""

    def __init__(self, key_columns: List[str]):
        self.key_columns = key_columns

    def align(self, left_headers: List[str], right_headers: List[str]) -> AlignmentResult:
        left_set = set(left_headers)
        right_set = set(right_headers)
        common = [h for h in left_headers if h in right_set]
        left_only = [h for h in left_headers if h not in right_set]
        right_only = [h for h in right_headers if h not in left_set]
        right_common_order = [h for h in right_headers if h in left_set]
        reordered = common != right_common_order
        return AlignmentResult(
            left_headers=left_headers,
            right_headers=right_headers,
            common=common,
            left_only=left_only,
            right_only=right_only,
            reordered=reordered,
        )

    def remap_row(self, row: Dict[str, str], target_headers: List[str]) -> Dict[str, str]:
        """Return a new row dict containing only keys present in target_headers."""
        return {h: row[h] for h in target_headers if h in row}

    def remap_index(
        self, index: Dict[Tuple, Dict[str, str]], target_headers: List[str]
    ) -> Dict[Tuple, Dict[str, str]]:
        """Remap every row in an index to target_headers."""
        return {key: self.remap_row(row, target_headers) for key, row in index.items()}
