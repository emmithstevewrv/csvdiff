"""Sorting utilities for CSV diff output and row ordering."""

from typing import List, Dict, Any, Optional, Tuple


SortKey = List[str]


class RowSorter:
    """Sorts rows or diff results by one or more column keys."""

    def __init__(self, sort_keys: Optional[SortKey] = None, reverse: bool = False):
        """
        Args:
            sort_keys: List of column names to sort by. If None, original order is preserved.
            reverse: If True, sort in descending order.
        """
        self.sort_keys = sort_keys or []
        self.reverse = reverse

    def sort_rows(
        self, rows: List[Dict[str, Any]], headers: List[str]
    ) -> List[Dict[str, Any]]:
        """Return rows sorted by the configured sort keys.

        Args:
            rows: List of row dicts to sort.
            headers: Available column headers (used for validation).

        Returns:
            Sorted list of row dicts.

        Raises:
            KeyError: If a sort key is not found in headers.
        """
        if not self.sort_keys:
            return list(rows)

        missing = [k for k in self.sort_keys if k not in headers]
        if missing:
            raise KeyError(
                f"Sort key(s) not found in headers: {missing}"
            )

        return sorted(
            rows,
            key=lambda row: tuple(row.get(k, "") for k in self.sort_keys),
            reverse=self.reverse,
        )

    def sort_index(
        self, index: Dict[Tuple, Dict[str, Any]]
    ) -> List[Tuple[Tuple, Dict[str, Any]]]:
        """Return index entries as a sorted list of (key, row) pairs.

        Args:
            index: Dict mapping composite key tuples to row dicts.

        Returns:
            List of (key_tuple, row_dict) sorted by key tuple.
        """
        return sorted(index.items(), key=lambda item: item[0], reverse=self.reverse)
