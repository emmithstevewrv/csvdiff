"""Caching layer for CSV diff results to avoid redundant computation."""

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Optional

from csvdiff.differ import DiffResult
from csvdiff.encoder import to_json, from_json


@dataclass
class CacheConfig:
    cache_dir: str = ".csvdiff_cache"
    max_entries: int = 64
    enabled: bool = True


class DiffCache:
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        if self.config.enabled:
            os.makedirs(self.config.cache_dir, exist_ok=True)

    def _cache_key(self, left_path: str, right_path: str, keys: list) -> str:
        left_stat = self._file_sig(left_path)
        right_stat = self._file_sig(right_path)
        raw = f"{left_stat}|{right_stat}|{','.join(keys)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _file_sig(self, path: str) -> str:
        try:
            stat = os.stat(path)
            return f"{path}:{stat.st_size}:{stat.st_mtime}"
        except FileNotFoundError:
            return f"{path}:missing"

    def _cache_path(self, key: str) -> str:
        return os.path.join(self.config.cache_dir, f"{key}.json")

    def get(self, left_path: str, right_path: str, keys: list) -> Optional[DiffResult]:
        if not self.config.enabled:
            return None
        key = self._cache_key(left_path, right_path, keys)
        path = self._cache_path(key)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return from_json(data)

    def put(self, left_path: str, right_path: str, keys: list, result: DiffResult) -> None:
        if not self.config.enabled:
            return
        key = self._cache_key(left_path, right_path, keys)
        path = self._cache_path(key)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(to_json(result), fh, indent=2)
        self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        entries = sorted(
            (os.path.getmtime(os.path.join(self.config.cache_dir, f)),
             os.path.join(self.config.cache_dir, f))
            for f in os.listdir(self.config.cache_dir)
            if f.endswith(".json")
        )
        while len(entries) > self.config.max_entries:
            _, oldest = entries.pop(0)
            os.remove(oldest)

    def clear(self) -> int:
        removed = 0
        if not os.path.isdir(self.config.cache_dir):
            return removed
        for f in os.listdir(self.config.cache_dir):
            if f.endswith(".json"):
                os.remove(os.path.join(self.config.cache_dir, f))
                removed += 1
        return removed
