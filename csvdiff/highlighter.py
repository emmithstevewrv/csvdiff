"""Field-level change highlighting for modified rows."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class FieldDiff:
    column: str
    before: str
    after: str

    def __str__(self) -> str:
        return f"{self.column}: {self.before!r} -> {self.after!r}"


@dataclass
class RowHighlight:
    key: Tuple[str, ...]
    changes: List[FieldDiff] = field(default_factory=list)

    @property
    def changed_columns(self) -> List[str]:
        return [c.column for c in self.changes]

    def __len__(self) -> int:
        return len(self.changes)


class Highlighter:
    """Computes field-level diffs for modified rows."""

    def __init__(self, headers: List[str], key_columns: List[str]):
        self.headers = headers
        self.key_columns = key_columns
        self._data_columns = [h for h in headers if h not in key_columns]

    def highlight_row(
        self,
        key: Tuple[str, ...],
        before: Dict[str, str],
        after: Dict[str, str],
    ) -> RowHighlight:
        """Return a RowHighlight describing which fields changed."""
        highlight = RowHighlight(key=key)
        for col in self._data_columns:
            b = before.get(col, "")
            a = after.get(col, "")
            if b != a:
                highlight.changes.append(FieldDiff(column=col, before=b, after=a))
        return highlight

    def highlight_all(
        self,
        modified: Dict[Tuple[str, ...], Tuple[Dict[str, str], Dict[str, str]]],
    ) -> List[RowHighlight]:
        """Return highlights for all modified rows."""
        return [
            self.highlight_row(key, before, after)
            for key, (before, after) in modified.items()
        ]
