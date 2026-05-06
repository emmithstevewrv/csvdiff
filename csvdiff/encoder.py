"""JSON and CSV encoding/decoding for DiffResult objects."""

import json
from typing import Any, Dict, List

from csvdiff.differ import DiffResult


def to_json(result: DiffResult) -> Dict[str, Any]:
    """Serialize a DiffResult to a plain dict suitable for JSON output."""
    modified_out = {}
    for key, (before, after) in result.modified.items():
        modified_out[key] = {"before": before, "after": after}
    return {
        "added": result.added,
        "removed": result.removed,
        "modified": modified_out,
    }


def from_json(data: Dict[str, Any]) -> DiffResult:
    """Deserialize a DiffResult from a plain dict (as produced by to_json)."""
    modified = {
        key: (entry["before"], entry["after"])
        for key, entry in data.get("modified", {}).items()
    }
    return DiffResult(
        added=data.get("added", {}),
        removed=data.get("removed", {}),
        modified=modified,
    )


def added_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Return added rows as a CSV string."""
    lines = [",".join(headers)]
    for row in result.added.values():
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    return "\n".join(lines) + "\n"


def removed_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Return removed rows as a CSV string."""
    lines = [",".join(headers)]
    for row in result.removed.values():
        lines.append(",".join(str(row.get(h, "")) for h in headers))
    return "\n".join(lines) + "\n"


def modified_after_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Return the 'after' state of modified rows as a CSV string."""
    lines = [",".join(headers)]
    for _before, after in result.modified.values():
        lines.append(",".join(str(after.get(h, "")) for h in headers))
    return "\n".join(lines) + "\n"


def modified_before_to_csv(result: DiffResult, headers: List[str]) -> str:
    """Return the 'before' state of modified rows as a CSV string."""
    lines = [",".join(headers)]
    for before, _after in result.modified.values():
        lines.append(",".join(str(before.get(h, "")) for h in headers))
    return "\n".join(lines) + "\n"
