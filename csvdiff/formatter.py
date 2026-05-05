"""Output formatters for DiffResult."""

import json
from typing import Any
from csvdiff.differ import DiffResult


def format_text(result: DiffResult) -> str:
    """Render a DiffResult as human-readable text."""
    lines: list[str] = []

    for row in result.added:
        lines.append(f"+ {_row_str(row)}")

    for row in result.removed:
        lines.append(f"- {_row_str(row)}")

    for entry in result.modified:
        key_str = ", ".join(str(k) for k in entry["key"])
        lines.append(f"~ [{key_str}]")
        for col, change in entry["changes"].items():
            lines.append(f"    {col}: {change['old']!r} -> {change['new']!r}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def format_json(result: DiffResult) -> str:
    """Render a DiffResult as a JSON string."""
    payload: dict[str, Any] = {
        "added": result.added,
        "removed": result.removed,
        "modified": [
            {
                "key": list(entry["key"]),
                "changes": entry["changes"],
            }
            for entry in result.modified
        ],
        "summary": {
            "added": len(result.added),
            "removed": len(result.removed),
            "modified": len(result.modified),
        },
    }
    return json.dumps(payload, indent=2)


def _row_str(row: dict[str, Any]) -> str:
    return ", ".join(f"{k}={v}" for k, v in row.items())
