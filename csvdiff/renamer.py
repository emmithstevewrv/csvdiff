"""Column renamer: maps column names from one CSV to another before diffing."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameConfig:
    """Mapping of old column names to new column names."""
    mapping: Dict[str, str] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return len(self.mapping) == 0

    def inverse(self) -> "RenameConfig":
        """Return a RenameConfig with the mapping reversed."""
        return RenameConfig(mapping={v: k for k, v in self.mapping.items()})


@dataclass
class RenameResult:
    headers: List[str]
    rows: Dict[tuple, Dict[str, str]]
    renamed_columns: List[str]


class ColumnRenamer:
    """Applies a column rename mapping to headers and row data."""

    def __init__(self, config: RenameConfig) -> None:
        self.config = config

    def rename_headers(self, headers: List[str]) -> List[str]:
        """Return headers with renamed columns substituted in place."""
        return [self.config.mapping.get(h, h) for h in headers]

    def rename_row(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a new row dict with keys renamed according to the mapping."""
        return {self.config.mapping.get(k, k): v for k, v in row.items()}

    def rename_index(
        self,
        index: Dict[tuple, Dict[str, str]],
    ) -> Dict[tuple, Dict[str, str]]:
        """Return a new index with all row dicts renamed."""
        return {key: self.rename_row(row) for key, row in index.items()}

    def apply(
        self,
        headers: List[str],
        index: Dict[tuple, Dict[str, str]],
    ) -> RenameResult:
        """Apply the rename mapping to headers and all rows in the index."""
        new_headers = self.rename_headers(headers)
        new_index = self.rename_index(index)
        renamed = [
            self.config.mapping[h]
            for h in headers
            if h in self.config.mapping
        ]
        return RenameResult(
            headers=new_headers,
            rows=new_index,
            renamed_columns=renamed,
        )

    @staticmethod
    def from_pairs(pairs: List[str]) -> "ColumnRenamer":
        """Build a ColumnRenamer from a list of 'old=new' strings."""
        mapping: Dict[str, str] = {}
        for pair in pairs:
            if "=" not in pair:
                raise ValueError(f"Invalid rename pair (expected 'old=new'): {pair!r}")
            old, new = pair.split("=", 1)
            mapping[old.strip()] = new.strip()
        return ColumnRenamer(RenameConfig(mapping=mapping))
