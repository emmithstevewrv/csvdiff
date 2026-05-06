"""CLI helpers for cache management sub-commands."""

import argparse
import sys

from csvdiff.cacher import CacheConfig, DiffCache


def build_cache_parser(subparsers=None) -> argparse.ArgumentParser:
    desc = "Manage the csvdiff result cache"
    if subparsers is not None:
        parser = subparsers.add_parser("cache", help=desc)
    else:
        parser = argparse.ArgumentParser(prog="csvdiff cache", description=desc)

    sub = parser.add_subparsers(dest="cache_cmd")

    clear_p = sub.add_parser("clear", help="Remove all cached diff results")
    clear_p.add_argument(
        "--cache-dir",
        default=".csvdiff_cache",
        help="Directory where cache files are stored (default: .csvdiff_cache)",
    )

    info_p = sub.add_parser("info", help="Show cache statistics")
    info_p.add_argument(
        "--cache-dir",
        default=".csvdiff_cache",
        help="Directory where cache files are stored (default: .csvdiff_cache)",
    )

    return parser


def run_cache_command(args) -> int:
    """Dispatch cache sub-commands; return exit code."""
    cache_dir = getattr(args, "cache_dir", ".csvdiff_cache")
    cfg = CacheConfig(cache_dir=cache_dir)
    cache = DiffCache(cfg)

    if args.cache_cmd == "clear":
        removed = cache.clear()
        print(f"Removed {removed} cached entry/entries from '{cache_dir}'.")
        return 0

    if args.cache_cmd == "info":
        import os
        if not os.path.isdir(cache_dir):
            print(f"Cache directory '{cache_dir}' does not exist.")
            return 0
        entries = [f for f in os.listdir(cache_dir) if f.endswith(".json")]
        total_bytes = sum(
            os.path.getsize(os.path.join(cache_dir, f)) for f in entries
        )
        print(f"Cache directory : {cache_dir}")
        print(f"Cached entries  : {len(entries)}")
        print(f"Total size      : {total_bytes} bytes")
        return 0

    print("No cache sub-command specified. Use 'clear' or 'info'.", file=sys.stderr)
    return 2
