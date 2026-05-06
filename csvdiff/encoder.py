"""JSON and CSV encoding utilities for diff output serialization."""

import csv
import io
import json
from typing import Any, Dict, List, Optional

from csvdiff.differ import DiffResult


def to_json(result: DiffResult, indent: Optional[int] = 2) -> str:
    """Serialize a DiffResult to a JSON string."""
    payload = {
        "added": list(result.added.values()),
        "removed": list(result.removed.values()),
        "modified": [
            {"key": list(k) if isinstance(k, tuple) else k, "before": before, "after": after}
            for k, (before, after) in result.modified.items()
        ],
    }
    return json.dumps(payload, indent=indent, default=str)


def from_json(text: str) -> Dict[str, Any]:
    """Deserialize a JSON string back to a raw diff dict."""
    return json.loads(text)


def added_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Render the added rows of a DiffResult as a CSV string."""
    return _rows_to_csv(list(result.added.values()), headers)


def removed_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Render the removed rows of a DiffResult as a CSV string."""
    return _rows_to_csv(list(result.removed.values()), headers)


def modified_after_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Render the 'after' state of modified rows as a CSV string."""
    rows = [after for _before, after in result.modified.values()]
    return _rows_to_csv(rows, headers)


def _rows_to_csv(rows: List[Dict[str, str]], headers: List[str]) -> str:
    """Convert a list of row dicts to a CSV string with the given headers."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
