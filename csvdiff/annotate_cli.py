"""CLI entry point for the annotate sub-command."""

import argparse
import json
import sys

from csvdiff.encoder import from_json
from csvdiff.annotator import RowAnnotator, CHANGE_ADDED, CHANGE_REMOVED, CHANGE_MODIFIED


def build_annotate_parser(parent: argparse.ArgumentParser = None) -> argparse.ArgumentParser:
    parser = parent or argparse.ArgumentParser(
        prog="csvdiff annotate",
        description="Annotate a diff JSON with per-row change type labels.",
    )
    parser.add_argument("diff_file", help="Path to a diff JSON produced by csvdiff.")
    parser.add_argument(
        "--type",
        dest="change_type",
        choices=[CHANGE_ADDED, CHANGE_REMOVED, CHANGE_MODIFIED],
        default=None,
        help="Filter output to a specific change type.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a count summary instead of individual rows.",
    )
    return parser


def run_annotate_command(args: argparse.Namespace) -> int:
    try:
        with open(args.diff_file, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {args.diff_file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2

    diff_result = from_json(raw)
    annotator = RowAnnotator()
    annotation = annotator.annotate(diff_result)

    if args.summary:
        for change_type, count in annotation.summary().items():
            print(f"{change_type}: {count}")
        return 0

    rows = annotation.by_type(args.change_type) if args.change_type else annotation.rows
    for row in rows:
        print(row)

    return 0


def main() -> None:  # pragma: no cover
    parser = build_annotate_parser()
    args = parser.parse_args()
    sys.exit(run_annotate_command(args))


if __name__ == "__main__":  # pragma: no cover
    main()
