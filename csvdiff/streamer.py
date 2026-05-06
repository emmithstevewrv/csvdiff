"""Stream large CSV diffs in chunks to avoid loading everything into memory."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List, Dict, Tuple, Any

from csvdiff.differ import DiffResult


@dataclass
class StreamConfig:
    chunk_size: int = 500
    include_added: bool = True
    include_removed: bool = True
    include_modified: bool = True


@dataclass
class DiffChunk:
    index: int
    added: List[Dict[str, str]] = field(default_factory=list)
    removed: List[Dict[str, str]] = field(default_factory=list)
    modified: List[Tuple[Dict[str, str], Dict[str, str]]] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    def is_empty(self) -> bool:
        return self.size == 0


class DiffStreamer:
    """Yields DiffChunk objects from a DiffResult in fixed-size batches."""

    def __init__(self, result: DiffResult, config: StreamConfig | None = None) -> None:
        self._result = result
        self._config = config or StreamConfig()

    def stream(self) -> Iterator[DiffChunk]:
        chunk_size = self._config.chunk_size
        cfg = self._config

        items: List[Tuple[str, Any]] = []
        if cfg.include_added:
            items += [("added", row) for row in self._result.added]
        if cfg.include_removed:
            items += [("removed", row) for row in self._result.removed]
        if cfg.include_modified:
            items += [("modified", pair) for pair in self._result.modified]

        for chunk_idx, start in enumerate(range(0, max(len(items), 1), chunk_size)):
            batch = items[start : start + chunk_size]
            if not batch:
                break
            chunk = DiffChunk(index=chunk_idx)
            for kind, payload in batch:
                if kind == "added":
                    chunk.added.append(payload)
                elif kind == "removed":
                    chunk.removed.append(payload)
                else:
                    chunk.modified.append(payload)
            yield chunk

    def chunk_count(self) -> int:
        cfg = self._config
        total = 0
        if cfg.include_added:
            total += len(self._result.added)
        if cfg.include_removed:
            total += len(self._result.removed)
        if cfg.include_modified:
            total += len(self._result.modified)
        if total == 0:
            return 0
        return (total + self._config.chunk_size - 1) // self._config.chunk_size
