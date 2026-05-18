"""Export DiffResult to various file formats (CSV, TSV, JSONL)."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from csvdiff.differ import DiffResult


EXPORT_FORMATS = ("csv", "tsv", "jsonl")


def _rows_with_tag(result: DiffResult) -> List[dict]:
    """Flatten all change rows into dicts with a '_change' tag column."""
    rows: List[dict] = []
    for key, row in result.added.items():
        rows.append({"_change": "added", **row})
    for key, row in result.removed.items():
        rows.append({"_change": "removed", **row})
    for key, (before, after) in result.modified.items():
        rows.append({"_change": "modified_before", **before})
        rows.append({"_change": "modified_after", **after})
    return rows


def export_csv(result: DiffResult, delimiter: str = ",") -> str:
    """Return all changed rows as a delimited string with a _change column."""
    rows = _rows_with_tag(result)
    if not rows:
        return ""
    fieldnames = ["_change"] + [c for c in rows[0] if c != "_change"]
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export_tsv(result: DiffResult) -> str:
    """Return all changed rows as a tab-separated string."""
    return export_csv(result, delimiter="\t")


def export_jsonl(result: DiffResult) -> str:
    """Return all changed rows as newline-delimited JSON."""
    rows = _rows_with_tag(result)
    return "\n".join(json.dumps(row) for row in rows)


def export(result: DiffResult, fmt: str) -> str:
    """Dispatch to the correct exporter by format name.

    Args:
        result: The DiffResult to export.
        fmt:    One of 'csv', 'tsv', 'jsonl'.

    Returns:
        Formatted string output.

    Raises:
        ValueError: If *fmt* is not a recognised format.
    """
    if fmt == "csv":
        return export_csv(result)
    if fmt == "tsv":
        return export_tsv(result)
    if fmt == "jsonl":
        return export_jsonl(result)
    raise ValueError(f"Unknown export format {fmt!r}. Choose from: {EXPORT_FORMATS}")
