"""End-to-end diff pipeline orchestrating reader, filter, sorter, differ, and validator."""

from typing import List, Optional

from csvdiff.reader import CSVReader
from csvdiff.filter import ColumnFilter
from csvdiff.sorter import RowSorter
from csvdiff.differ import diff, DiffResult
from csvdiff.validator import CSVValidator
from csvdiff.reporter import compute_stats, ReportStats


class DiffPipeline:
    """Orchestrates the full CSV diff workflow."""

    def __init__(
        self,
        left_path: str,
        right_path: str,
        key_columns: List[str],
        include_columns: Optional[List[str]] = None,
        exclude_columns: Optional[List[str]] = None,
        sort_keys: Optional[List[str]] = None,
        sort_reverse: bool = False,
        validate: bool = True,
    ):
        self.left_path = left_path
        self.right_path = right_path
        self.key_columns = key_columns
        self.include_columns = include_columns
        self.exclude_columns = exclude_columns
        self.sort_keys = sort_keys
        self.sort_reverse = sort_reverse
        self.validate = validate

    def run(self) -> DiffResult:
        reader = CSVReader(key_columns=self.key_columns)
        left_headers, left_index = reader.load(self.left_path)
        right_headers, right_index = reader.load(self.right_path)

        if self.validate:
            validator = CSVValidator(key_columns=self.key_columns)
            header_result = validator.validate_headers(left_headers, right_headers)
            if not header_result.is_valid:
                raise ValueError(str(header_result))

            for label, index in (("left", left_index), ("right", right_index)):
                key_result = validator.validate_keys_unique(index, label)
                if not key_result.is_valid:
                    raise ValueError(str(key_result))

        col_filter = ColumnFilter(
            headers=left_headers,
            include=self.include_columns,
            exclude=self.exclude_columns,
        )
        active_headers = col_filter.apply_headers()

        left_index = {k: col_filter.apply_row(row) for k, row in left_index.items()}
        right_index = {k: col_filter.apply_row(row) for k, row in right_index.items()}

        if self.sort_keys:
            sorter = RowSorter(sort_keys=self.sort_keys, reverse=self.sort_reverse)
            left_index = sorter.sort_index(left_index)
            right_index = sorter.sort_index(right_index)

        result = diff(
            left_index=left_index,
            right_index=right_index,
            headers=active_headers,
        )
        return result

    def run_with_stats(self) -> tuple:
        """Run the pipeline and return (DiffResult, ReportStats)."""
        result = self.run()
        stats = compute_stats(result)
        return result, stats
