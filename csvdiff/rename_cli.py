"""CLI sub-command: apply column renames to a CSV file and print the result."""

import argparse
import csv
import sys
from typing import List, Optional

from csvdiff.renamer import ColumnRenamer


def build_rename_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    description = "Rename columns in a CSV file and write the result to stdout."
    if parent is not None:
        parser = parent.add_parser("rename", help=description)
    else:
        parser = argparse.ArgumentParser(prog="csvdiff-rename", description=description)

    parser.add_argument("file", help="Input CSV file path")
    parser.add_argument(
        "-r",
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        dest="renames",
        help="Column rename in OLD=NEW format. May be repeated.",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter (default: ',')",
    )
    return parser


def run_rename_command(args: argparse.Namespace) -> int:
    if not args.renames:
        print("Error: at least one --rename OLD=NEW mapping is required.", file=sys.stderr)
        return 2

    try:
        renamer = ColumnRenamer.from_pairs(args.renames)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        with open(args.file, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter=args.delimiter)
            if reader.fieldnames is None:
                print("Error: CSV file has no headers.", file=sys.stderr)
                return 2

            original_headers: List[str] = list(reader.fieldnames)
            new_headers = renamer.rename_headers(original_headers)

            writer = csv.DictWriter(
                sys.stdout,
                fieldnames=new_headers,
                lineterminator="\n",
                delimiter=args.delimiter,
            )
            writer.writeheader()
            for row in reader:
                writer.writerow(renamer.rename_row(dict(row)))

    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_rename_parser()
    args = parser.parse_args(argv)
    sys.exit(run_rename_command(args))


if __name__ == "__main__":
    main()
