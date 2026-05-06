"""Tests for csvdiff.sampler.DiffSampler."""

import pytest

from csvdiff.differ import DiffResult
from csvdiff.sampler import DiffSampler


@pytest.fixture()
def big_result() -> DiffResult:
    headers = ["id", "name", "score"]
    added = {(str(i),): [str(i), f"add_{i}", str(i * 10)] for i in range(20)}
    removed = {(str(i),): [str(i), f"rem_{i}", str(i * 5)] for i in range(20)}
    modified = {
        (str(i),): (
            [str(i), f"old_{i}", "1"],
            [str(i), f"new_{i}", "2"],
        )
        for i in range(20)
    }
    return DiffResult(added=added, removed=removed, modified=modified, headers=headers)


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added={}, removed={}, modified={}, headers=["id", "name"])


def test_sample_limits_added_rows(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    result = sampler.sample(big_result, n=3)
    assert len(result.added) == 3


def test_sample_limits_removed_rows(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    result = sampler.sample(big_result, n=4)
    assert len(result.removed) == 4


def test_sample_limits_modified_rows(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    result = sampler.sample(big_result, n=5)
    assert len(result.modified) == 5


def test_sample_preserves_headers(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=1)
    result = sampler.sample(big_result, n=2)
    assert result.headers == big_result.headers


def test_sample_zero_returns_empty(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    result = sampler.sample(big_result, n=0)
    assert len(result.added) == 0
    assert len(result.removed) == 0
    assert len(result.modified) == 0


def test_sample_larger_than_population(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    result = sampler.sample(big_result, n=100)
    assert len(result.added) == len(big_result.added)


def test_sample_empty_result_stays_empty(empty_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    result = sampler.sample(empty_result, n=5)
    assert len(result.added) == 0
    assert len(result.removed) == 0
    assert len(result.modified) == 0


def test_negative_n_raises(big_result: DiffResult) -> None:
    sampler = DiffSampler(seed=0)
    with pytest.raises(ValueError, match="non-negative"):
        sampler.sample(big_result, n=-1)


def test_seed_produces_reproducible_results(big_result: DiffResult) -> None:
    s1 = DiffSampler(seed=42).sample(big_result, n=5)
    s2 = DiffSampler(seed=42).sample(big_result, n=5)
    assert set(s1.added.keys()) == set(s2.added.keys())
    assert set(s1.removed.keys()) == set(s2.removed.keys())
    assert set(s1.modified.keys()) == set(s2.modified.keys())
