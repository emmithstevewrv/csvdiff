"""Edge-case tests for DiffStreamer."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.streamer import DiffStreamer, StreamConfig


def _make_result(n_added=0, n_removed=0, n_modified=0):
    added = [{"id": str(i)} for i in range(n_added)]
    removed = [{"id": str(i)} for i in range(n_removed)]
    modified = [({"id": str(i), "v": "a"}, {"id": str(i), "v": "b"}) for i in range(n_modified)]
    return DiffResult(added=added, removed=removed, modified=modified)


def test_chunk_size_larger_than_total():
    result = _make_result(n_added=3)
    streamer = DiffStreamer(result, StreamConfig(chunk_size=100))
    chunks = list(streamer.stream())
    assert len(chunks) == 1
    assert chunks[0].size == 3


def test_chunk_size_of_one_yields_one_item_per_chunk():
    result = _make_result(n_added=3)
    streamer = DiffStreamer(result, StreamConfig(chunk_size=1))
    chunks = list(streamer.stream())
    assert len(chunks) == 3
    for c in chunks:
        assert c.size == 1


def test_only_modified_rows():
    result = _make_result(n_modified=4)
    streamer = DiffStreamer(result, StreamConfig(chunk_size=3))
    chunks = list(streamer.stream())
    assert len(chunks) == 2
    total_modified = sum(len(c.modified) for c in chunks)
    assert total_modified == 4


def test_chunk_count_empty_result():
    result = _make_result()
    streamer = DiffStreamer(result)
    assert streamer.chunk_count() == 0


def test_exclude_all_types_yields_no_chunks():
    result = _make_result(n_added=5, n_removed=5, n_modified=5)
    cfg = StreamConfig(
        chunk_size=10,
        include_added=False,
        include_removed=False,
        include_modified=False,
    )
    streamer = DiffStreamer(result, cfg)
    chunks = list(streamer.stream())
    assert chunks == []


def test_default_config_includes_all():
    result = _make_result(n_added=2, n_removed=2, n_modified=2)
    streamer = DiffStreamer(result)
    chunks = list(streamer.stream())
    total = sum(c.size for c in chunks)
    assert total == 6
