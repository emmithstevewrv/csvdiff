"""High-level pipeline that wires reader, filter, sorter, and differ together."""

from typing import List, Optional

from csvdiff.reader import CSVReader
from csvdiff.filter import ColumnFilter
from csvdiff.sorter import RowSorter
from csvdiff.differ import DiffResult, diff


class DiffPipeline:
    """Orchestrates loading, filtering, sorting, and diffing two CSV files."""

    def __init__(
        self,
        key_cols: List[str],
        include_cols: Optional[List[str]] = None,
        exclude_cols: Optional[List[str]] = None,
        sort_keys: Optional[List[str]] = None,
        sort_reverse: bool = False,
    ):
        """
        Args:
            key_cols: Columns that uniquely identify a row.
            include_cols: If set, only these columns are compared.
            exclude_cols: Columns to drop before comparing.
            sort_keys: Columns to sort output rows by.
            sort_reverse: Sort in descending order when True.
        """
        self.key_cols = key_cols
        self.col_filter = ColumnFilter(
            include=include_cols, exclude=exclude_cols
        )
        self.sorter = RowSorter(sort_keys=sort_keys, reverse=sort_reverse)

    def run(self, left_path: str, right_path: str) -> DiffResult:
        """Execute the full diff pipeline.

        Args:
            left_path: Path to the original CSV file.
            right_path: Path to the updated CSV file.

        Returns:
            DiffResult containing added, removed, and modified rows.

        Raises:
            FileNotFoundError: If either file cannot be opened.
            KeyError: If key or sort columns are absent from headers.
        """
        left_reader = CSVReader(left_path, key_cols=self.key_cols)
        right_reader = CSVReader(right_path, key_cols=self.key_cols)

        left_headers, left_index = left_reader.load()
        right_headers, right_index = right_reader.load()

        left_headers = self.col_filter.apply_headers(left_headers)
        right_headers = self.col_filter.apply_headers(right_headers)

        left_index = {
            k: self.col_filter.apply_row(row, left_headers)
            for k, row in left_index.items()
        }
        right_index = {
            k: self.col_filter.apply_row(row, right_headers)
            for k, row in right_index.items()
        }

        result = diff(left_index, right_index, right_headers)

        if self.sorter.sort_keys:
            result = DiffResult(
                headers=result.headers,
                added=self.sorter.sort_rows(result.added, result.headers),
                removed=self.sorter.sort_rows(result.removed, result.headers),
                modified=result.modified,
            )

        return result
