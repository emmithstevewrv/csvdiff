"""Sampling utilities for previewing diff results on large CSV files."""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from csvdiff.differ import DiffResult


class DiffSampler:
    """Randomly samples rows from each change category in a DiffResult."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def sample(
        self,
        result: DiffResult,
        n: int = 5,
    ) -> DiffResult:
        """Return a new DiffResult containing at most *n* rows per category."""
        if n < 0:
            raise ValueError(f"Sample size must be non-negative, got {n}")

        return DiffResult(
            added=self._sample_dict(result.added, n),
            removed=self._sample_dict(result.removed, n),
            modified=self._sample_pairs(result.modified, n),
            headers=result.headers,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sample_dict(
        self,
        mapping: Dict[Tuple, List[str]],
        n: int,
    ) -> Dict[Tuple, List[str]]:
        keys = list(mapping.keys())
        chosen = self._rng.sample(keys, min(n, len(keys)))
        return {k: mapping[k] for k in chosen}

    def _sample_pairs(
        self,
        mapping: Dict[Tuple, Tuple[List[str], List[str]]],
        n: int,
    ) -> Dict[Tuple, Tuple[List[str], List[str]]]:
        keys = list(mapping.keys())
        chosen = self._rng.sample(keys, min(n, len(keys)))
        return {k: mapping[k] for k in chosen}
