"""Tests for csvdiff.streamer."""

import pytest
from csvdiff.differ import DiffResult
from csvdiff.streamer import DiffStreamer, DiffChunk, StreamConfig


@pytest.fixture
def big_result():
    added = [{"id": str(i), "val": "a"} for i in range(12)]
    removed = [{"id": str(i), "val": "r"} for i in range(5)]
    modified = [
        ({"id": str(i), "val": "old"}, {"id": str(i), "val": "new"})
        for i in range(8)
    ]
    return DiffResult(added=added, removed=removed, modified=modified)


@pytest.fixture
def empty_result():
    return DiffResult(added=[], removed=[], modified=[])


def test_stream_yields_chunks(big_result):
    streamer = DiffStreamer(big_result, StreamConfig(chunk_size=10))
    chunks = list(streamer.stream())
    assert len(chunks) == 3  # 25 items / 10 = 3 chunks


def test_chunk_size_respected(big_result):
    streamer = DiffStreamer(big_result, StreamConfig(chunk_size=10))
    chunks = list(streamer.stream())
    assert chunks[0].size == 10
    assert chunks[1].size == 10
    assert chunks[2].size == 5


def test_chunk_indices_are_sequential(big_result):
    streamer = DiffStreamer(big_result, StreamConfig(chunk_size=10))
    indices = [c.index for c in streamer.stream()]
    assert indices == [0, 1, 2]


def test_empty_result_yields_no_chunks(empty_result):
    streamer = DiffStreamer(empty_result)
    chunks = list(streamer.stream())
    assert chunks == []


def test_chunk_count_matches_yielded(big_result):
    cfg = StreamConfig(chunk_size=10)
    streamer = DiffStreamer(big_result, cfg)
    assert streamer.chunk_count() == len(list(streamer.stream()))


def test_exclude_added_omits_added_rows(big_result):
    cfg = StreamConfig(chunk_size=100, include_added=False)
    streamer = DiffStreamer(big_result, cfg)
    chunks = list(streamer.stream())
    total_added = sum(len(c.added) for c in chunks)
    assert total_added == 0


def test_exclude_removed_omits_removed_rows(big_result):
    cfg = StreamConfig(chunk_size=100, include_removed=False)
    streamer = DiffStreamer(big_result, cfg)
    chunks = list(streamer.stream())
    total_removed = sum(len(c.removed) for c in chunks)
    assert total_removed == 0


def test_exclude_modified_omits_modified_rows(big_result):
    cfg = StreamConfig(chunk_size=100, include_modified=False)
    streamer = DiffStreamer(big_result, cfg)
    chunks = list(streamer.stream())
    total_modified = sum(len(c.modified) for c in chunks)
    assert total_modified == 0


def test_chunk_is_empty_false_when_has_items(big_result):
    streamer = DiffStreamer(big_result, StreamConfig(chunk_size=100))
    chunk = next(streamer.stream())
    assert not chunk.is_empty()


def test_all_items_present_across_chunks(big_result):
    streamer = DiffStreamer(big_result, StreamConfig(chunk_size=7))
    chunks = list(streamer.stream())
    total = sum(c.size for c in chunks)
    assert total == 25
