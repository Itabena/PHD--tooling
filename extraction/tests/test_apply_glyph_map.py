#!/usr/bin/env python3
"""Tests for apply_glyph_map.py. Runs standalone: `python3 tests/test_apply_glyph_map.py`."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import apply_glyph_map as agm  # noqa: E402

REAL_MAP = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "glyph-map.tsv"


def _write(tmpdir: str, name: str, content: str) -> str:
    path = os.path.join(tmpdir, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def test_load_glyph_map_skips_comments_and_blanks():
    with tempfile.TemporaryDirectory() as d:
        path = _write(d, "map.tsv", "# comment\n\nfi\tFI\n\nfl\tFL\n")
        rows = agm.load_glyph_map(Path(path))
        assert rows == [("fi", "FI"), ("fl", "FL")]


def test_load_glyph_map_rejects_malformed_row():
    with tempfile.TemporaryDirectory() as d:
        path = _write(d, "map.tsv", "onlyonecolumn\n")
        try:
            agm.load_glyph_map(Path(path))
        except ValueError as exc:
            assert "expected 'from<TAB>to'" in str(exc)
        else:
            raise AssertionError("expected ValueError for malformed row")


def test_apply_map_is_literal_and_ordered():
    rows = [("ab", "X"), ("Xc", "Y")]  # second row's pattern only exists after the first fires
    assert agm.apply_map("abc", rows) == "Y"


def test_apply_map_does_not_touch_unmapped_text():
    rows = [("fi", "FI")]
    assert agm.apply_map("no ligatures here", rows) == "no ligatures here"


def test_real_glyph_map_decomposes_standard_ligatures():
    rows = agm.load_glyph_map(REAL_MAP)
    assert agm.apply_map("ﬁlled", rows) == "filled"
    assert agm.apply_map("ﬂow", rows) == "flow"
    assert agm.apply_map("stiﬀ", rows) == "stiff"


def test_flag_letter_spacing_detects_long_run():
    text = "Normal line.\nTw o s y s t e m s , A a n d B\nAnother normal line with n k T."
    flagged = agm.flag_letter_spacing(text)
    flagged_lines = {ln for ln, _ in flagged}
    assert 2 in flagged_lines
    assert 1 not in flagged_lines
    assert 3 not in flagged_lines  # "n k T" is only 3 single letters, below the run threshold


def test_flag_letter_spacing_never_rewrites():
    text = "Tw o s y s t e m s"
    flag_letter_spacing_result = agm.flag_letter_spacing(text)
    assert len(flag_letter_spacing_result) == 1
    # The detector is read-only: the same text passed through apply_map with an
    # empty table comes back byte-identical, proving no repair step exists.
    assert agm.apply_map(text, []) == text


def test_flag_unmapped_glyphs_detects_stray_control_byte():
    # \x04 here stands in for poppler's "no Unicode mapping" placeholder byte.
    text = "Normal line.\nThe number \x04(0) of Section 1.2.\nAnother clean line."
    flagged = agm.flag_unmapped_glyphs(text)
    assert [ln for ln, _, _ in flagged] == [2]
    assert flagged[0][1] == "0x4"


def test_flag_unmapped_glyphs_ignores_tabs_and_newlines():
    text = "clean\ttabbed line\nno stray bytes here"
    assert agm.flag_unmapped_glyphs(text) == []


def test_flag_unmapped_glyphs_never_rewrites():
    text = "hc \x06 2 \x071/2"
    before = text
    agm.flag_unmapped_glyphs(text)
    assert text == before  # detector took no action on its input


def test_glyph_map_does_not_contain_ambiguous_control_byte_entries():
    # Regression guard for the Pathria finding: 0x04 is Omega in prose but a
    # stacked-parenthesis piece elsewhere in the same document, so no entry
    # mapping a bare control byte to a math symbol may ever be added here.
    rows = agm.load_glyph_map(REAL_MAP)
    for from_, _ in rows:
        assert not any(ord(c) < 32 for c in from_), (
            f"glyph-map.tsv has a control-byte entry {from_!r} -- these are not "
            f"safely 1:1 (see Pathria ch.1 problems 1.9/1.16 vs Omega in prose)"
        )


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
