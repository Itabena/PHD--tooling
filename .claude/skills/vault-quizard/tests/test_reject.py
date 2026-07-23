#!/usr/bin/env python3
"""Tests for reject.py. Runs standalone: `python3 tests/test_reject.py`."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import reject  # noqa: E402


def test_reasons_are_the_three_kinds():
    assert set(reject.REASONS) == {"fabricated-quote", "quote-unsupported", "trivia"}
    # Integrity vs quality split kept, so distillation can triage without dilution.
    assert reject.REASONS["fabricated-quote"] == "integrity"
    assert reject.REASONS["quote-unsupported"] == "integrity"
    assert reject.REASONS["trivia"] == "quality"


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


def test_default_log_lands_in_vault_dotquiz():
    # With a vault root and no --log, the log goes to <vault>/.quiz/rejections.jsonl,
    # created on demand -- one shared file that syncs with the vault.
    with tempfile.TemporaryDirectory() as vault:
        rc = reject.main([
            "--reason", "trivia",
            "--source-file", "Notes/x.md",
            "--stem", "What is the value?",
            "--vault-root", vault,
        ])
        assert rc == 0
        expected = os.path.join(vault, ".quiz", "rejections.jsonl")
        assert os.path.exists(expected)
        with open(expected, encoding="utf-8") as fh:
            assert json.loads(fh.readline())["reason"] == "trivia"


def test_resolve_log_path_prefers_explicit():
    assert reject.resolve_log_path("/tmp/x.jsonl", "/vault") == "/tmp/x.jsonl"
    assert reject.resolve_log_path(None, "/vault").endswith(os.path.join(".quiz", "rejections.jsonl"))
    assert reject.resolve_log_path(None, None) is None


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
