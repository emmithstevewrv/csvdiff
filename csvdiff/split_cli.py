"""CLI sub-command: split diff output into per-column change reports."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from csvdiff.encoder import from_json
from csvdiff.splitter import DiffSplitter


def build_split_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[name-defined]
    description = "Split a JSON diff into per-column change buckets."
    if parent is not None:
        parser = parent.add_parser("split", help=description)
    else:
        parser = argparse.ArgumentParser(prog="csvdiff-split", description=description)

    parser.add_argument("diff_file", help="JSON diff file produced by csvdiff")
    parser.add_argument(
        "-k", "--key",
        dest="keys",
        metavar="COLUMN",
        action="append",
        required=True,
        help="Key column (repeatable)",
    )
    parser.add_argument(
        "-c", "--column",
        dest="columns",
        metavar="COLUMN",
        action="append",
        default=None,
        help="Only report this column (repeatable; default: all)",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        default=False,
        help="Output as JSON instead of plain text",
    )
    return parser


def run_split_command(args: argparse.Namespace) -> int:
    try:
        with open(args.diff_file) as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {args.diff_file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON — {exc}", file=sys.stderr)
        return 2

    diff = from_json(raw)
    splitter = DiffSplitter(key_columns=args.keys)
    split = splitter.split(diff)

    target_cols: List[str] = args.columns if args.columns else split.columns()

    if args.as_json:
        out: dict = {}
        for col in target_cols:
            if col not in split.columns():
                continue
            bucket = split.get(col)
            out[col] = [
                {"before": b[col], "after": a[col]}
                for b, a in bucket.pairs
            ]
        print(json.dumps(out, indent=2))
    else:
        for col in target_cols:
            if col not in split.columns():
                continue
            bucket = split.get(col)
            print(f"[{col}]  {bucket.count} change(s)")
            for before, after in bucket.pairs:
                print(f"  {before[col]!r} -> {after[col]!r}")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_split_parser()
    sys.exit(run_split_command(parser.parse_args()))
