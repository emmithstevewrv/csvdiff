"""Format highlighted row diffs for human-readable output."""

from typing import List, Optional

from csvdiff.highlighter import RowHighlight

_RESET  = "\033[0m"
_RED    = "\033[31m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_BOLD   = "\033[1m"


def format_highlight(
    highlights: List[RowHighlight],
    *,
    color: bool = True,
    indent: int = 2,
) -> str:
    """Return a multi-line string describing all highlighted row changes."""
    if not highlights:
        return "(no modified rows)"

    pad = " " * indent
    lines: List[str] = []

    for row in highlights:
        key_str = ", ".join(row.key)
        header = f"~ row ({key_str})  [{len(row)} field(s) changed]"
        if color:
            header = f"{_BOLD}{_YELLOW}{header}{_RESET}"
        lines.append(header)

        for fd in row.changes:
            before_part = _colorize(f"-{fd.before!r}", _RED, color)
            after_part  = _colorize(f"+{fd.after!r}", _GREEN, color)
            col_part    = _colorize(fd.column, _BOLD, color)
            lines.append(f"{pad}{col_part}: {before_part}  {after_part}")

    return "\n".join(lines)


def format_highlight_summary(highlights: List[RowHighlight]) -> str:
    """Return a one-line summary of highlighted changes."""
    if not highlights:
        return "0 rows changed, 0 fields affected"
    total_fields = sum(len(h) for h in highlights)
    return f"{len(highlights)} row(s) changed, {total_fields} field(s) affected"


def _colorize(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{code}{text}{_RESET}"
