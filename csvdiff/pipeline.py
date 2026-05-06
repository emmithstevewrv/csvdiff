"""End-to-end diff pipeline wiring reader → filter → diff → reporter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csvdiff.differ import DiffResult, diff
from csvdiff.filter import ColumnFilter
from csvdiff.reader import CSVReader
from csvdiff.reporter import ReportStats, compute_stats
from csvdiff.validator import ValidationResult, validate


@dataclass
class PipelineConfig:
    left_path: str
    right_path: str
    key_columns: List[str]
    include_columns: Optional[List[str]] = None
    exclude_columns: Optional[List[str]] = None
    encoding: str = "utf-8"
    delimiter: str = ","


@dataclass
class PipelineResult:
    diff: DiffResult
    stats: ReportStats
    validation: ValidationResult
    headers: List[str] = field(default_factory=list)


class DiffPipeline:
    """Orchestrates the full diff workflow."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    def run(self) -> PipelineResult:
        cfg = self.config

        reader = CSVReader(
            key_columns=cfg.key_columns,
            encoding=cfg.encoding,
            delimiter=cfg.delimiter,
        )

        left_headers, left_index = reader.load(cfg.left_path)
        right_headers, right_index = reader.load(cfg.right_path)

        # Validate before filtering so we can report structural issues.
        validation = validate(
            left_headers=left_headers,
            right_headers=right_headers,
            key_columns=cfg.key_columns,
        )

        col_filter = ColumnFilter(
            include=cfg.include_columns,
            exclude=cfg.exclude_columns,
        )
        headers = col_filter.apply_headers(left_headers)

        left_index = {
            k: col_filter.apply_row(row) for k, row in left_index.items()
        }
        right_index = {
            k: col_filter.apply_row(row) for k, row in right_index.items()
        }

        diff_result = diff(left_index, right_index)
        stats = compute_stats(diff_result, total_rows=len(left_index))

        return PipelineResult(
            diff=diff_result,
            stats=stats,
            validation=validation,
            headers=headers,
        )

    # ------------------------------------------------------------------
    def run_with_stats(self) -> PipelineResult:
        """Alias kept for backward compatibility."""
        return self.run()
