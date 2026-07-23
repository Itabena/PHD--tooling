#!/usr/bin/env python3
"""Tests for reject.py. Runs standalone: `python3 tests/test_reject.py`."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reject  # noqa: E402


def test_reasons_are_the_four_kinds():
    assert set(reject.REASONS) == {
        "fabricated-quote", "quote-unsupported", "trivia", "extraction-artifact",
    }
    # Integrity vs quality vs extraction split kept, so distillation can triage
    # without dilution -- extraction-artifact must never fall into "integrity"
    # (it is not fabrication; the remedy is re-extraction, not careful generation).
    assert reject.REASONS["fabricated-quote"] == "integrity"
    assert reject.REASONS["quote-unsupported"] == "integrity"
    assert reject.REASONS["trivia"] == "quality"
    assert reject.REASONS["extraction-artifact"] == "extraction"


def test_make_entry_populates_fields():
    entry = reject.make_entry(
        "trivia", "Sources/foo.md", "What is the value of x?", note="lookup",
        timestamp="2026-07-21T10:00:00",
    )
    assert entry["reason"] == "trivia"
    assert entry["kind"] == "quality"
    assert entry["source_file"] == "Sources/foo.md"
    assert entry["stem"] == "What is the value of x?"
    assert entry["note"] == "lookup"
    assert entry["timestamp"] == "2026-07-21T10:00:00"


def test_extraction_artifact_is_not_integrity():
    entry = reject.make_entry(
        "extraction-artifact", "Sources/Chapter 1.extract.txt",
        "What does the entropy equal at the critical point?",
        note="quote is verbatim but the source equation is missing a sign",
    )
    assert entry["reason"] == "extraction-artifact"
    assert entry["kind"] == "extraction"
    assert entry["kind"] not in ("integrity", "quality")


def test_make_entry_rejects_unknown_reason():
    try:
        reject.make_entry("too-hard", "f.md", "stem")
    except ValueError as exc:
        assert "unknown reason" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown reason")


def test_append_entry_writes_jsonl():
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "rejections.jsonl")
        reject.append_entry(reject.make_entry("trivia", "a.md", "s1"), log)
        reject.append_entry(reject.make_entry("fabricated-quote", "b.md", "s2"), log)
        with open(log, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        assert len(lines) == 2
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["reason"] == "trivia" and first["kind"] == "quality"
        assert second["reason"] == "fabricated-quote" and second["kind"] == "integrity"


def test_cli_appends_and_validates():
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "log.jsonl")
        rc = reject.main([
            "--reason", "quote-unsupported",
            "--source-file", "Sources/x.md",
            "--stem", "Does the quote support this?",
            "--log", log,
        ])
        assert rc == 0
        with open(log, encoding="utf-8") as fh:
            entry = json.loads(fh.readline())
        assert entry["reason"] == "quote-unsupported"


def test_default_log_lands_beside_script_in_tooling_repo():
    # With no --log, the log goes to logs/rejections.jsonl beside reject.py --
    # versioned with the skill, not with any particular vault.
    here = os.path.dirname(os.path.abspath(reject.__file__))
    assert reject.DEFAULT_LOG == os.path.join(here, "logs", "rejections.jsonl")


def test_resolve_log_path_prefers_explicit():
    assert reject.resolve_log_path("/tmp/x.jsonl") == "/tmp/x.jsonl"
    assert reject.resolve_log_path(None) == reject.DEFAULT_LOG


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
