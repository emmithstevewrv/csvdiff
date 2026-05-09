"""Command-line interface for csvdiff."""

import sys
import argparse

from csvdiff.reader import CSVReader
from csvdiff.differ import diff
from csvdiff.formatter import format_text, format_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff",
        description="Fast column-aware diff tool for large CSV files.",
    )
    parser.add_argument("left", help="Original CSV file")
    parser.add_argument("right", help="Modified CSV file")
    parser.add_argument(
        "-k",
        "--key",
        dest="keys",
        metavar="COLUMN",
        action="append",
        default=[],
        help="Key column(s) used to match rows (repeatable). Defaults to first column.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color in text output",
    )
    return parser


def _load_csv(path: str, key_cols: list[str] | None) -> tuple:
    """Load a CSV file and return (headers, data), raising SystemExit on error."""
    reader = CSVReader(path, key_columns=key_cols)
    return reader.load()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    key_cols = args.keys or None  # None → reader defaults to first column

    try:
        left_headers, left_data = _load_csv(args.left, key_cols)
        right_headers, right_data = _load_csv(args.right, key_cols)
    except FileNotFoundError as exc:
        print(f"csvdiff: error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"csvdiff: error: {exc}", file=sys.stderr)
        return 2

    result = diff(left_headers, left_data, right_headers, right_data)

    if args.format == "json":
        print(format_json(result))
    else:
        output = format_text(result, color=not args.no_color)
        if output:
            print(output)

    return 1 if result.has_changes() else 0


if __name__ == "__main__":
    sys.exit(main())
