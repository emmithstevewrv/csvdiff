"""Column filtering and selection utilities for csvdiff."""

from typing import List, Dict, Optional


class ColumnFilter:
    """Filters and reorders columns in CSV row data."""

    def __init__(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ):
        """
        Initialize a ColumnFilter.

        Args:
            include: If provided, only these columns are kept (in given order).
            exclude: If provided, these columns are dropped. Ignored if include is set.
        """
        if include and exclude:
            raise ValueError("Specify either 'include' or 'exclude', not both.")
        self.include = include
        self.exclude = exclude

    def apply_headers(self, headers: List[str]) -> List[str]:
        """Return the filtered list of header names."""
        if self.include is not None:
            missing = [c for c in self.include if c not in headers]
            if missing:
                raise ValueError(
                    f"Columns not found in CSV headers: {missing}"
                )
            return list(self.include)
        if self.exclude is not None:
            return [h for h in headers if h not in self.exclude]
        return list(headers)

    def apply_row(self, row: Dict[str, str], filtered_headers: List[str]) -> Dict[str, str]:
        """Return a new row dict containing only the filtered columns."""
        return {col: row[col] for col in filtered_headers if col in row}

    def apply_index(
        self,
        index: Dict[tuple, Dict[str, str]],
        filtered_headers: List[str],
    ) -> Dict[tuple, Dict[str, str]]:
        """Apply column filtering to an entire row index."""
        return {
            key: self.apply_row(row, filtered_headers)
            for key, row in index.items()
        }
