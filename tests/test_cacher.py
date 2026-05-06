"""Tests for csvdiff.cacher."""

import os
import pytest

from csvdiff.cacher import CacheConfig, DiffCache
from csvdiff.differ import DiffResult


@pytest.fixture
def diff_result():
    return DiffResult(
        added={"("A",)": {"id": "A", "val": "1"}},
        removed={},
        modified={},
    )


@pytest.fixture
def tmp_cache(tmp_path):
    cfg = CacheConfig(cache_dir=str(tmp_path / "cache"), max_entries=4)
    return DiffCache(cfg)


def _fake_files(tmp_path):
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    left.write_text("id,val\nA,1\n")
    right.write_text("id,val\nA,2\n")
    return str(left), str(right)


def test_get_returns_none_on_miss(tmp_path, tmp_cache):
    left, right = _fake_files(tmp_path)
    assert tmp_cache.get(left, right, ["id"]) is None


def test_put_and_get_roundtrip(tmp_path, tmp_cache, diff_result):
    left, right = _fake_files(tmp_path)
    tmp_cache.put(left, right, ["id"], diff_result)
    cached = tmp_cache.get(left, right, ["id"])
    assert cached is not None
    assert list(cached.added.keys()) == list(diff_result.added.keys())


def test_different_keys_produce_different_entries(tmp_path, tmp_cache, diff_result):
    left, right = _fake_files(tmp_path)
    tmp_cache.put(left, right, ["id"], diff_result)
    assert tmp_cache.get(left, right, ["name"]) is None


def test_clear_removes_all_entries(tmp_path, tmp_cache, diff_result):
    left, right = _fake_files(tmp_path)
    tmp_cache.put(left, right, ["id"], diff_result)
    removed = tmp_cache.clear()
    assert removed == 1
    assert tmp_cache.get(left, right, ["id"]) is None


def test_eviction_respects_max_entries(tmp_path, diff_result):
    cfg = CacheConfig(cache_dir=str(tmp_path / "cache"), max_entries=2)
    cache = DiffCache(cfg)
    # Create 3 different file pairs to generate 3 cache entries
    for i in range(3):
        left = tmp_path / f"left{i}.csv"
        right = tmp_path / f"right{i}.csv"
        left.write_text(f"id,val\n{i},x\n")
        right.write_text(f"id,val\n{i},y\n")
        cache.put(str(left), str(right), ["id"], diff_result)
    files = [f for f in os.listdir(cfg.cache_dir) if f.endswith(".json")]
    assert len(files) <= 2


def test_disabled_cache_never_stores(tmp_path, diff_result):
    cfg = CacheConfig(cache_dir=str(tmp_path / "cache"), enabled=False)
    cache = DiffCache(cfg)
    left = tmp_path / "l.csv"
    right = tmp_path / "r.csv"
    left.write_text("id\n1\n")
    right.write_text("id\n2\n")
    cache.put(str(left), str(right), ["id"], diff_result)
    assert not os.path.isdir(cfg.cache_dir)
    assert cache.get(str(left), str(right), ["id"]) is None


def test_clear_on_empty_dir_returns_zero(tmp_path):
    cfg = CacheConfig(cache_dir=str(tmp_path / "no_such_dir"))
    cache = DiffCache(cfg)
    # Don't enable / create dir
    cache.config.enabled = False
    assert cache.clear() == 0
