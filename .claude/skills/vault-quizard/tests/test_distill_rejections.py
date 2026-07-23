#!/usr/bin/env python3
"""Tests for distill_rejections.py. Runs standalone: `python3 tests/test_distill_rejections.py`."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import distill_rejections as dr  # noqa: E402
import reject  # noqa: E402


def _write_log(path, entries):
    with open(path, "w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def test_load_entries_missing_file_is_empty():
    assert dr.load_entries("/nonexistent/path/rejections.jsonl") == []


def test_load_entries_skips_malformed_lines():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "log.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write('{"reason": "trivia", "kind": "quality", "note": "ok"}\n')
            fh.write("not json at all\n")
            fh.write('{"reason": "trivia", "kind": "quality", "note": "ok2"}\n')
        entries = dr.load_entries(path)
        assert len(entries) == 2


def test_aggregate_groups_by_kind_then_exact_note():
    entries = [
        reject.make_entry("trivia", "a.md", "s1", note="asks for a number"),
        reject.make_entry("trivia", "b.md", "s2", note="asks for a number"),
        reject.make_entry("trivia", "c.md", "s3", note="asks for a number"),
        reject.make_entry("trivia", "d.md", "s4", note="different complaint"),
        reject.make_entry("fabricated-quote", "e.md", "s5", note="no quote found"),
    ]
    aggregated = dr.aggregate(entries)
    quality_groups = aggregated["quality"]
    assert quality_groups[0][1] == 3  # highest-count group first
    assert quality_groups[0][0] == ("trivia", "asks for a number")
    assert quality_groups[1][1] == 1
    assert aggregated["integrity"][0][1] == 1


def test_aggregate_normalizes_whitespace_and_case_in_notes():
    entries = [
        reject.make_entry("trivia", "a.md", "s1", note="Asks For A Number"),
        reject.make_entry("trivia", "b.md", "s2", note="asks   for a number"),
    ]
    aggregated = dr.aggregate(entries)
    assert len(aggregated["quality"]) == 1
    assert aggregated["quality"][0][1] == 2


def test_extraction_kind_is_distinct_from_integrity_and_quality():
    entries = [
        reject.make_entry("extraction-artifact", "a.extract.txt", "s1", note="mangled equation"),
        reject.make_entry("fabricated-quote", "b.md", "s2", note="invented"),
        reject.make_entry("trivia", "c.md", "s3", note="lookup value"),
    ]
    aggregated = dr.aggregate(entries)
    assert set(aggregated) == {"extraction", "integrity", "quality"}
    assert aggregated["extraction"][0][0][0] == "extraction-artifact"


def test_format_report_ranks_by_count_and_orders_kinds():
    entries = [
        reject.make_entry("trivia", "a.md", "s1", note="x"),
        reject.make_entry("trivia", "b.md", "s2", note="x"),
        reject.make_entry("fabricated-quote", "c.md", "s3", note="y"),
    ]
    report = dr.format_report(dr.aggregate(entries))
    # integrity section appears before quality (KIND_ORDER), regardless of count.
    assert report.index("## integrity") < report.index("## quality")
    assert "x2" in report


def test_format_report_empty_log():
    report = dr.format_report(dr.aggregate([]))
    assert "No rejection groups found" in report


def test_format_report_respects_min_count():
    entries = [
        reject.make_entry("trivia", "a.md", "s1", note="rare complaint"),
    ]
    report = dr.format_report(dr.aggregate(entries), min_count=2)
    assert "No rejection groups found" in report


def test_cli_reads_real_log_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "rejections.jsonl")
        _write_log(log, [
            reject.make_entry("extraction-artifact", "Chapter 1.extract.txt", "stem1",
                               note="missing sign in equation"),
            reject.make_entry("extraction-artifact", "Chapter 1.extract.txt", "stem2",
                               note="missing sign in equation"),
        ])
        rc = dr.main(["--log", log])
        assert rc == 0


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
