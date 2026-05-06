"""Apply a DiffResult to a CSV index to produce a patched dataset."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult

# A row index maps a key-tuple to an ordered dict of {column: value}.
RowIndex = Dict[Tuple, Dict[str, str]]


class PatchError(Exception):
    """Raised when a patch cannot be applied cleanly."""


def apply(index: RowIndex, result: DiffResult) -> RowIndex:
    """Return a new index with *result* applied to *index*.

    Raises ``PatchError`` if the diff is inconsistent with the index
    (e.g. trying to add a row that already exists, or remove one that
    does not).
    """
    patched: RowIndex = deepcopy(index)

    for key, row in result.added.items():
        if key in patched:
            raise PatchError(
                f"Cannot add row {key!r}: key already exists in the base index."
            )
        patched[key] = dict(row)

    for key in result.removed:
        if key not in patched:
            raise PatchError(
                f"Cannot remove row {key!r}: key not found in the base index."
            )
        del patched[key]

    for key, (old_row, new_row) in result.modified.items():
        if key not in patched:
            raise PatchError(
                f"Cannot modify row {key!r}: key not found in the base index."
            )
        if patched[key] != dict(old_row):
            raise PatchError(
                f"Cannot modify row {key!r}: base data does not match expected old values."
            )
        patched[key] = dict(new_row)

    return patched


def to_rows(index: RowIndex, headers: List[str]) -> List[Dict[str, str]]:
    """Flatten a row index back into an ordered list of row dicts.

    Rows are returned in insertion order (Python 3.7+).
    Only columns present in *headers* are included.
    """
    return [
        {col: row.get(col, "") for col in headers}
        for row in index.values()
    ]
