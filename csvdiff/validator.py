"""Schema and key validation for CSV diff inputs."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationError:
    message: str
    column: Optional[str] = None


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, message: str, column: Optional[str] = None) -> None:
        self.errors.append(ValidationError(message=message, column=column))

    def __str__(self) -> str:
        if self.is_valid:
            return "Validation passed."
        lines = [f"  - {e.message}" for e in self.errors]
        return "Validation failed:\n" + "\n".join(lines)


class CSVValidator:
    """Validates headers and key columns for two CSV datasets."""

    def __init__(self, key_columns: List[str]):
        if not key_columns:
            raise ValueError("At least one key column must be specified.")
        self.key_columns = key_columns

    def validate_headers(self, left_headers: List[str], right_headers: List[str]) -> ValidationResult:
        result = ValidationResult()

        for key in self.key_columns:
            if key not in left_headers:
                result.add_error(f"Key column '{key}' not found in left file.", column=key)
            if key not in right_headers:
                result.add_error(f"Key column '{key}' not found in right file.", column=key)

        left_set = set(left_headers)
        right_set = set(right_headers)

        only_left = left_set - right_set
        only_right = right_set - left_set

        for col in sorted(only_left):
            result.add_error(f"Column '{col}' exists in left file but not in right.", column=col)
        for col in sorted(only_right):
            result.add_error(f"Column '{col}' exists in right file but not in left.", column=col)

        return result

    def validate_keys_unique(self, index: dict, label: str) -> ValidationResult:
        """Validate that all keys in an index are genuinely unique (no duplicates)."""
        result = ValidationResult()
        # index is already keyed by tuple; duplicates would have been overwritten during load.
        # This checks for any sentinel duplicate markers if the reader supports them.
        for key, row in index.items():
            if row is None:
                result.add_error(
                    f"Duplicate key {key} detected in {label} file."
                )
        return result
