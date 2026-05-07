"""Tests for csvdiff.normalizer."""

import pytest
from csvdiff.normalizer import NormalizeConfig, RowNormalizer


@pytest.fixture
def default_normalizer():
    return RowNormalizer()


def test_strip_whitespace_by_default(default_normalizer):
    assert default_normalizer.normalize_value("  hello  ") == "hello"


def test_no_strip_when_disabled():
    cfg = NormalizeConfig(strip_whitespace=False)
    norm = RowNormalizer(cfg)
    assert norm.normalize_value("  hello  ") == "  hello  "


def test_lowercase_when_enabled():
    cfg = NormalizeConfig(lowercase=True)
    norm = RowNormalizer(cfg)
    assert norm.normalize_value("Hello World") == "hello world"


def test_null_values_replaced(default_normalizer):
    for null_str in ("NULL", "null", "None", "none", "NA", "N/A", ""):
        assert default_normalizer.normalize_value(null_str) == ""


def test_null_replacement_custom():
    cfg = NormalizeConfig(null_replacement="<NULL>")
    norm = RowNormalizer(cfg)
    assert norm.normalize_value("NULL") == "<NULL>"


def test_normalize_nulls_disabled():
    cfg = NormalizeConfig(normalize_nulls=False)
    norm = RowNormalizer(cfg)
    assert norm.normalize_value("NULL") == "NULL"


def test_normalize_row_applies_to_all_fields(default_normalizer):
    row = {"name": "  Alice  ", "age": "NULL", "city": "  NYC  "}
    result = default_normalizer.normalize_row(row)
    assert result == {"name": "Alice", "age": "", "city": "NYC"}


def test_column_override_applies_lowercase_to_specific_column():
    override = NormalizeConfig(lowercase=True)
    cfg = NormalizeConfig(lowercase=False, column_overrides={"email": override})
    norm = RowNormalizer(cfg)
    row = {"name": "Alice", "email": "Alice@Example.COM"}
    result = norm.normalize_row(row)
    assert result["name"] == "Alice"
    assert result["email"] == "alice@example.com"


def test_normalize_index_normalizes_all_rows(default_normalizer):
    index = {
        ("1",): {"id": "1", "val": "  foo  "},
        ("2",): {"id": "2", "val": "NULL"},
    }
    result = default_normalizer.normalize_index(index)
    assert result[("1",)]["val"] == "foo"
    assert result[("2",)]["val"] == ""


def test_normalize_index_preserves_keys(default_normalizer):
    index = {("abc",): {"id": "abc", "name": " Bob "}}
    result = default_normalizer.normalize_index(index)
    assert ("abc",) in result


def test_default_config_no_lowercase(default_normalizer):
    assert default_normalizer.normalize_value("UPPER") == "UPPER"
