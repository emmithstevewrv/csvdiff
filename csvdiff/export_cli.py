"""CLI sub-command: csvdiff export  — write diff results to a file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csvdiff.encoder import from_json
from csvdiff.exporter import EXPORT_FORMATS, export


def build_export_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="csvdiff export",
        description="Export a JSON diff to CSV, TSV, or JSONL.",
    )
    parser = (
        parent.add_parser("export", **kwargs)  # type: ignore[arg-type]
        if parent is not None
        else argparse.ArgumentParser(**kwargs)  # type: ignore[arg-type]
    )
    parser.add_argument("diff_file", help="Path to the JSON diff file produced by csvdiff.")
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=EXPORT_FORMATS,
        default="csv",
        help="Output format (default: csv).",
    )
    parser.add_argument(
        "--output", "-o",
        default="-",
        help="Output file path. Use '-' for stdout (default).",
    )
    return parser


def run_export_command(args: argparse.Namespace) -> int:
    diff_path = Path(args.diff_file)
    if not diff_path.exists():
        print(f"error: file not found: {diff_path}", file=sys.stderr)
        return 2

    try:
        raw = diff_path.read_text(encoding="utf-8")
        result = from_json(raw)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse diff file: {exc}", file=sys.stderr)
        return 2

    try:
        output = export(result, args.fmt)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.output == "-":
        print(output, end="")
    else:
        Path(args.output).write_text(output, encoding="utf-8")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_export_parser()
    args = parser.parse_args()
    sys.exit(run_export_command(args))
