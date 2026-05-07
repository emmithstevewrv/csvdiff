"""CLI helpers for reporting column alignment issues between two CSV files."""

import argparse
import csv
import sys
from typing import List

from csvdiff.aligner import ColumnAligner


def _read_headers(path: str) -> List[str]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            return next(reader, [])
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def build_align_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:
    description = "Report column alignment differences between two CSV files."
    if parent is not None:
        p = parent.add_parser("align", description=description, help=description)
    else:
        p = argparse.ArgumentParser(prog="csvdiff-align", description=description)
    p.add_argument("left", help="Left CSV file")
    p.add_argument("right", help="Right CSV file")
    p.add_argument(
        "-k", "--key", dest="keys", action="append", default=[],
        metavar="COL", help="Key column (repeatable)",
    )
    p.add_argument(
        "--strict", action="store_true",
        help="Exit with code 1 if columns are not fully aligned",
    )
    return p


def run_align_command(args: argparse.Namespace) -> int:
    left_headers = _read_headers(args.left)
    right_headers = _read_headers(args.right)
    key_columns = args.keys or []

    aligner = ColumnAligner(key_columns=key_columns)
    result = aligner.align(left_headers, right_headers)

    print(f"Left columns  : {result.left_headers}")
    print(f"Right columns : {result.right_headers}")
    print(f"Common        : {result.common}")
    if result.left_only:
        print(f"Left-only     : {result.left_only}")
    if result.right_only:
        print(f"Right-only    : {result.right_only}")
    if result.reordered:
        print("Column order  : differs")
    print(f"Status        : {result.summary()}")

    if args.strict and not result.aligned:
        return 1
    return 0


def main(argv=None) -> None:
    parser = build_align_parser()
    args = parser.parse_args(argv)
    sys.exit(run_align_command(args))


if __name__ == "__main__":
    main()
