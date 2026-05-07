"""Normalize CSV field values before comparison (strip whitespace, case folding, etc.)."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class NormalizeConfig:
    strip_whitespace: bool = True
    lowercase: bool = False
    null_values: tuple = ("NULL", "null", "None", "none", "NA", "N/A", "")
    normalize_nulls: bool = True
    null_replacement: str = ""
    column_overrides: Dict[str, "NormalizeConfig"] = field(default_factory=dict)


class RowNormalizer:
    """Apply normalization rules to individual CSV rows."""

    def __init__(self, config: Optional[NormalizeConfig] = None) -> None:
        self.config = config or NormalizeConfig()

    def normalize_value(self, value: str, col: Optional[str] = None) -> str:
        """Normalize a single field value, optionally using column-specific config."""
        cfg = self.config
        if col and col in cfg.column_overrides:
            cfg = cfg.column_overrides[col]

        if cfg.strip_whitespace:
            value = value.strip()

        if cfg.normalize_nulls and value in cfg.null_values:
            value = cfg.null_replacement

        if cfg.lowercase:
            value = value.lower()

        return value

    def normalize_row(self, row: Dict[str, str]) -> Dict[str, str]:
        """Return a new row dict with all values normalized."""
        return {col: self.normalize_value(val, col) for col, val in row.items()}

    def normalize_index(
        self, index: Dict[tuple, Dict[str, str]]
    ) -> Dict[tuple, Dict[str, str]]:
        """Return a new index with every row normalized."""
        return {key: self.normalize_row(row) for key, row in index.items()}
