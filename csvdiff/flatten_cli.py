"""CLI command: csvdiff flatten — export a diff as a flat annotated CSV."""

import argparse
import csv
import sys
from typing import List, Optional

from csvdiff.encoder import from_json
from csvdiff.flattener import flatten, CHANGE_TYPE_KEY


def build_flatten_parser(parent: Optional[argparse.ArgumentParser] = None) -> argparse.ArgumentParser:
    parser = parent or argparse.ArgumentParser(
        prog="csvdiff flatten",
        description="Export a diff JSON as a flat annotated CSV.",
    )
    parser.add_argument("diff_file", help="Path to the diff JSON file produced by csvdiff.")
    parser.add_argument(
        "--no-before",
        action="store_true",
        default=False,
        help="Omit 'modified_before' rows; only emit 'modified_after'.",
    )
    parser.add_argument(
        "--output", "-o",
        default="-",
        help="Output file path. Defaults to stdout (-).",
    )
    return parser


def run_flatten_command(args: argparse.Namespace) -> int:
    try:
        with open(args.diff_file, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except FileNotFoundError:
        print(f"error: file not found: {args.diff_file}", file=sys.stderr)
        return 2

    try:
        diff = from_json(raw)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse diff JSON: {exc}", file=sys.stderr)
        return 2

    flat = flatten(diff, include_modified_before=not args.no_before)
    dicts = flat.to_dicts(include_key=False)

    if not dicts:
        return 0

    # Preserve column order: tag first, then data columns
    first_data_keys = [k for k in dicts[0].keys() if k != CHANGE_TYPE_KEY]
    fieldnames = [CHANGE_TYPE_KEY] + first_data_keys

    if args.output == "-":
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dicts)
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dicts)

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_flatten_parser()
    args = parser.parse_args(argv)
    sys.exit(run_flatten_command(args))


if __name__ == "__main__":
    main()
