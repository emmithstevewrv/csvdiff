"""Tests for csvdiff.renamer."""

import pytest
from csvdiff.renamer import ColumnRenamer, RenameConfig


@pytest.fixture
def renamer():
    return ColumnRenamer(RenameConfig(mapping={"old_name": "new_name", "qty": "quantity"}))


def test_rename_headers_substitutes_mapped_columns(renamer):
    result = renamer.rename_headers(["id", "old_name", "qty"])
    assert result == ["id", "new_name", "quantity"]


def test_rename_headers_leaves_unmapped_columns_unchanged(renamer):
    result = renamer.rename_headers(["id", "price"])
    assert result == ["id", "price"]


def test_rename_row_substitutes_keys(renamer):
    row = {"id": "1", "old_name": "Alice", "qty": "5"}
    result = renamer.rename_row(row)
    assert result == {"id": "1", "new_name": "Alice", "quantity": "5"}


def test_rename_row_leaves_unmapped_keys_unchanged(renamer):
    row = {"id": "1", "price": "9.99"}
    result = renamer.rename_row(row)
    assert result == {"id": "1", "price": "9.99"}


def test_rename_index_applies_to_all_rows(renamer):
    index = {
        ("1",): {"id": "1", "old_name": "Alice", "qty": "3"},
        ("2",): {"id": "2", "old_name": "Bob", "qty": "7"},
    }
    result = renamer.rename_index(index)
    assert result[("1",)] == {"id": "1", "new_name": "Alice", "quantity": "3"}
    assert result[("2",)] == {"id": "2", "new_name": "Bob", "quantity": "7"}


def test_apply_returns_renamed_headers_and_index(renamer):
    headers = ["id", "old_name", "qty"]
    index = {("1",): {"id": "1", "old_name": "Alice", "qty": "2"}}
    result = renamer.apply(headers, index)
    assert result.headers == ["id", "new_name", "quantity"]
    assert result.rows[("1",)]["new_name"] == "Alice"


def test_apply_reports_renamed_columns(renamer):
    headers = ["id", "old_name"]
    index = {}
    result = renamer.apply(headers, index)
    assert "new_name" in result.renamed_columns


def test_apply_empty_mapping_leaves_everything_unchanged():
    r = ColumnRenamer(RenameConfig())
    headers = ["id", "score"]
    index = {("1",): {"id": "1", "score": "99"}}
    result = r.apply(headers, index)
    assert result.headers == headers
    assert result.rows == index
    assert result.renamed_columns == []


def test_from_pairs_parses_valid_pairs():
    r = ColumnRenamer.from_pairs(["old=new", "a=b"])
    assert r.config.mapping == {"old": "new", "a": "b"}


def test_from_pairs_raises_on_invalid_pair():
    with pytest.raises(ValueError, match="Invalid rename pair"):
        ColumnRenamer.from_pairs(["badpair"])


def test_inverse_mapping():
    config = RenameConfig(mapping={"a": "b", "c": "d"})
    inv = config.inverse()
    assert inv.mapping == {"b": "a", "d": "c"}


def test_is_empty_true_for_no_mapping():
    assert RenameConfig().is_empty() is True


def test_is_empty_false_when_mapping_present():
    assert RenameConfig(mapping={"x": "y"}).is_empty() is False
