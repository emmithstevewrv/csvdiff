"""Integration tests: Deduplicator used alongside CSVReader output."""
import io
import csv
import pytest
from csvdiff.deduplicator import Deduplicator


def _parse_csv(text: str) -> list[dict]:
    """Parse CSV text into a list of row dicts."""
    reader = csv.DictReader(io.StringIO(text.strip()))
    return list(reader)


LEFT_CSV = """\
id,name,value
1,Alice,10
2,Bob,20
3,Carol,30
"""

DUPLICATE_CSV = """\
id,name,value
1,Alice,10
2,Bob,20
1,AliceDup,99
3,Carol,30
2,BobDup,88
"""

COMPOSITE_CSV = """\
region,product,sales
US,widget,100
US,gadget,200
EU,widget,150
US,widget,300
"""


def test_clean_file_no_duplicates():
    rows = _parse_csv(LEFT_CSV)
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    assert not report.has_duplicates


def test_duplicate_file_detected():
    rows = _parse_csv(DUPLICATE_CSV)
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    assert report.has_duplicates
    assert report.duplicate_key_count == 2


def test_duplicate_rows_are_accessible():
    rows = _parse_csv(DUPLICATE_CSV)
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    dup_rows_for_1 = report.duplicates[("1",)]
    assert len(dup_rows_for_1) == 2
    names = {r["name"] for r in dup_rows_for_1}
    assert names == {"Alice", "AliceDup"}


def test_composite_key_integration():
    rows = _parse_csv(COMPOSITE_CSV)
    d = Deduplicator(["region", "product"])
    report = d.find_duplicates(rows)
    assert report.duplicate_key_count == 1
    assert ("US", "widget") in report.duplicates


def test_summary_string_integration():
    rows = _parse_csv(DUPLICATE_CSV)
    d = Deduplicator(["id"])
    report = d.find_duplicates(rows)
    summary = report.summary()
    assert isinstance(summary, str)
    assert len(summary) > 0
