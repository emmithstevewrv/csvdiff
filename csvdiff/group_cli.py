"""CLI command for grouping a diff result by a column value."""

import argparse
import json
import sys

from csvdiff.encoder import from_json
from csvdiff.grouper import RowGrouper


def build_group_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff-group",
        description="Group a JSON diff result by a column value.",
    )
    parser.add_argument("diff_file", help="Path to JSON diff file produced by csvdiff")
    parser.add_argument(
        "--column", "-c", required=True, help="Column name to group by"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Show only the top N groups by total changes (0 = all)",
    )
    return parser


def run_group_command(args: argparse.Namespace) -> int:
    try:
        with open(args.diff_file) as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {args.diff_file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON — {exc}", file=sys.stderr)
        return 2

    try:
        diff = from_json(raw)
    except (KeyError, TypeError) as exc:
        print(f"error: malformed diff object — {exc}", file=sys.stderr)
        return 2

    try:
        grouper = RowGrouper(column=args.column)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = grouper.group(diff)
    buckets = result.sorted_buckets()
    if args.top and args.top > 0:
        buckets = buckets[: args.top]

    if not buckets:
        print(f"No changes found when grouping by '{args.column}'.")
        return 0

    print(f"Groups by '{args.column}' ({result.group_count} total):")
    for bucket in buckets:
        print(
            f"  {bucket.key_value!r:30s}  "
            f"+{len(bucket.added):>4}  "
            f"-{len(bucket.removed):>4}  "
            f"~{len(bucket.modified):>4}  "
            f"total={bucket.total}"
        )
    return 0


def main() -> None:  # pragma: no cover
    parser = build_group_parser()
    args = parser.parse_args()
    sys.exit(run_group_command(args))
