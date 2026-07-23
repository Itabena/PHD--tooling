#!/usr/bin/env python3
"""Resolve poppler's non-injective glyph-fallback bytes using the PDF's own
declared glyph names, not a blind byte->character table.

Governed by `a - logistics/Source Note Types.md` -> extraction section, and
the same discipline `apply_glyph_map.py` already follows: never guess. The
finding this fixes (2026-07-23, Pathria Ch.2): pdftotext's ToUnicode
fallback emits a generic low-byte placeholder for any glyph its font's
ToUnicode CMap can't resolve, and the SAME placeholder byte is reused across
genuinely different glyphs -- so a flat byte->character map is the wrong
tool (it would be wrong in roughly half its own occurrences).

What this does instead: read each font's own `/Encoding /Differences` array
straight out of the PDF -- the font's own declared code -> glyph-name table,
which routinely survives even when `/ToUnicode` is missing or broken -- and
resolve each name to Unicode via the Adobe Glyph List (`fontTools.agl`),
falling back to a small curated supplement for MathType's own
operator-variant names (`Delta1`, `integraltext`, ...) that AGL doesn't
know. A glyph is substituted only when both steps succeed; anything else is
left exactly as flagged by `apply_glyph_map.py` -- refuse, don't guess.

Font-resource names (e.g. `/T1_2`) are PAGE-LOCAL PDF labels, not global
identifiers -- the same label can mean a different embedded font on a
different page of the same document. This resolves the mapping fresh, per
page, every time; treat any script that assumes a resource name is stable
across pages as buggy (an earlier draft of this exact tool was, until a
visual check on the Ch.2 "Delta1" glyph caught it).

Usage
-----
    python3 resolve_math_glyphs.py CHAPTER.raw.txt PDF.pdf --page-range 57 70 \\
        --map extraction/glyph-map.tsv -o CHAPTER.extract.txt

Runs `apply_glyph_map.py`'s existing literal substitution first (unchanged),
then this pass over whatever it left flagged, then reports what got resolved
vs. what's still flagged.
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

import pikepdf
from fontTools.agl import AGL2UV

sys.path.insert(0, str(Path(__file__).parent))
from apply_glyph_map import load_glyph_map, apply_map  # noqa: E402

# MathType operator-variant / non-standard glyph names the Adobe Glyph List
# doesn't know. Each entry confirmed by visual inspection against the real
# rendered PDF page where it was first hit -- not inferred from the name
# alone (a name like "Delta1" could plausibly mean several things; only the
# rendered glyph settles it). Extend this table the same way: add an entry
# only after looking at the actual page, and note where/how it was checked.
MATHTYPE_SUPPLEMENT = {
    "angbracketleft": "⟨",       # standard PostScript glyph name (not in AGL2UV), unambiguous
    "angbracketright": "⟩",      # same
    "Delta1": "Δ",               # Δ -- Pathria Ch.2 p.58, "(E - Delta, E]", visually confirmed
    "Gamma1": "Γ",               # Γ
    "Sigma1": "Σ",               # Σ
    "phi1": "ϕ",                 # alternate lowercase phi
    "integraltext": "∫",         # ∫ inline-size
    "integraldisplay": "∫",      # ∫ display-size
    "contintegraldisplay": "∮",  # contour integral
    "summationtext": "∑",
    "summationdisplay": "∑",
    "productdisplay": "∏",
    "planckover2pi1": "ℏ",       # ℏ
    "negationslash": "̸",        # combining not-slash
    "vextendsingle": "∣",
    "equivalence": "≡",
    "lessmuch": "≪",
    "greatermuch": "≫",
    "similarequal": "≃",
    "approxequal": "≈",
    "similar": "∼",
    "lessequal": "≤",
    "proportional": "∝",
    "negationslash1": "≠",
}

# Glyph names poppler's own text output expands to more than one character
# (ligatures) -- the content-stream side must expand them the same way, or
# character counts drift between the two sequences being aligned.
LIGATURE_EXPANSIONS = {"fi": "fi", "fl": "fl", "ffi": "ffi", "ffl": "ffl", "ff": "ff"}

# Confirmed literal overrides, applied as a final exact-string pass.
# Position-alignment (`_align_page`) only catches a control byte when it
# sits inside a *short, cleanly-isolated* diff block; a long run of
# otherwise-identical text on either side of it gets swept into one large
# "replace" opcode that the stricter equal-length check then skips
# entirely (confirmed while building this tool: Ch.2's "<byte> f <byte>"
# ensemble-average notation aligned cleanly at one occurrence but not the
# other ten, purely because of where each one happened to sit relative to
# nearby text). Each entry here was independently confirmed two ways
# before being added -- not a byte-value guess:
#   1. position-alignment resolved at least one real occurrence to this
#      exact literal string (see `_align_page`'s output for this chapter);
#   2. the font's own /Differences array names the bracketing glyphs
#      (MTSYN codes 3/4 = angbracketleft/angbracketright).
# Extending a position-confirmed literal string to its remaining identical
# repeats is safe in a way a bare byte substitution is not: the interior
# content (here, always "f") makes the match specific rather than generic.
CONFIRMED_LITERAL_OVERRIDES = {
    "\x03 f \x04": "⟨ f ⟩",  # ensemble average <f> -- Pathria Ch.2 SS2.1-2.3, 9 occurrences
    "\x03f\x04": "⟨f⟩",       # same, no interior spacing -- 2 occurrences
    "(E−\x03)": "(E−Δ)",      # energy-shell width Delta -- position-confirmed at 8+ other
    "(E − \x03)": "(E − Δ)",  # occurrences of this exact "(E [-] Delta [, E])" template
}


def resolve_name(name: str) -> str | None:
    if name in AGL2UV:
        return chr(AGL2UV[name])
    return MATHTYPE_SUPPLEMENT.get(name)


def font_differences_map(font_obj) -> dict[int, str]:
    """code -> glyph name, from this font's own /Encoding /Differences only."""
    mapping: dict[int, str] = {}
    enc = font_obj.get("/Encoding", None)
    if enc is None or isinstance(enc, pikepdf.Name):
        return mapping
    try:
        diffs = enc.get("/Differences", None)
    except Exception:
        return mapping
    if diffs is None:
        return mapping
    code = None
    for item in diffs:
        if isinstance(item, int):
            code = item
        elif code is not None:
            mapping[code] = str(item).lstrip("/")
            code += 1
    return mapping


def page_font_resolution(page) -> dict[str, dict[int, str | None]]:
    """resource-name -> {code: resolved_char_or_None} for this page's fonts."""
    resources = page.get("/Resources", {})
    fonts = resources.get("/Font", {})
    result = {}
    for key, font in fonts.items():
        diffs = font_differences_map(font)
        result[str(key)] = {code: resolve_name(name) for code, name in diffs.items()}
    return result


def content_stream_sequence_one_page(page) -> list[str | None]:
    """One entry per character shown on this single page, in stream order.
    None = no confirmed resolution. Space codes are dropped (this PDF
    encodes word gaps as TJ-array kerning numbers, not literal space
    glyphs -- keeping them would desync the alignment against poppler's
    word-spaced text).
    """
    font_map = page_font_resolution(page)
    seq: list[str | None] = []
    current = None
    for operands, operator in pikepdf.parse_content_stream(page):
        op = str(operator)
        if op == "Tf":
            current = str(operands[0])
        elif op in ("Tj", "'", '"'):
            for b in bytes(operands[-1]):
                seq.append(font_map.get(current, {}).get(b))
        elif op == "TJ":
            for el in operands[0]:
                if isinstance(el, pikepdf.String):
                    for b in bytes(el):
                        seq.append(font_map.get(current, {}).get(b))
    return seq


def _align_page(raw_page_text: str, cs_seq: list) -> tuple[str, int]:
    """Position-specific substitution for one page's worth of text (see
    `resolve_positions` for why this must be positional, never a global
    byte->character replace).
    """
    nows_chars: list[str] = []
    nows_to_raw_idx: list[int] = []
    for idx, ch in enumerate(raw_page_text):
        if not ch.isspace():
            nows_chars.append(ch)
            nows_to_raw_idx.append(idx)
    pop_str = "".join(nows_chars)

    PUA_BASE = 0xE000
    def cs_token(i, ch):
        return ch if ch is not None else chr(PUA_BASE + (i % 0x1000))
    cs_str = "".join(cs_token(i, ch) for i, ch in enumerate(cs_seq))

    matcher = difflib.SequenceMatcher(None, pop_str, cs_str, autojunk=False)
    chars = list(raw_page_text)
    num_substituted = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "replace":
            continue
        pop_chunk = pop_str[i1:i2]
        cs_chunk_raw = cs_seq[j1:j2]
        # Equal-length blocks only -- e.g. "\x03f\x04" (3 chars) vs the
        # content stream's [angbracketleft, None, angbracketright] (3
        # entries): substitute position-by-position within the block,
        # since a control byte can sit right next to an ordinary letter
        # that doesn't itself need any resolution (it already matched
        # poppler's own correct decoding, which is exactly why it's not a
        # separate "equal" block of its own -- it only got swept into this
        # replace block because a real edit sits next to it). A block that
        # spans a long, otherwise-identical run of text between two real
        # edits will fail this check and be skipped entirely -- that gap
        # is what `CONFIRMED_LITERAL_OVERRIDES` exists to catch afterward.
        if len(pop_chunk) != len(cs_chunk_raw):
            continue
        for offset, pchar in enumerate(pop_chunk):
            if ord(pchar) >= 32:
                continue  # not a control-byte fallback, some other real edit
            resolved = cs_chunk_raw[offset]
            if resolved is None:
                continue
            raw_idx = nows_to_raw_idx[i1 + offset]
            chars[raw_idx] = resolved
            num_substituted += 1
    return "".join(chars), num_substituted


def resolve_positions(raw_text: str, pdf_path: str, first_page: int, last_page: int) -> tuple[str, int]:
    """Align `raw_text` (the frozen .raw.txt content, exactly as pdftotext
    produced it) against the content-stream reconstruction, and substitute
    CONFIRMED characters at their exact aligned positions only.

    This is the crux of the whole fix: the same control byte legitimately
    means different glyphs at different positions (that's the non-injective
    fallback this tool exists to work around), so resolving "byte 0x03 means
    Delta" and then blindly find/replacing every 0x03 in the file would
    silently corrupt every *other* glyph that also happens to fall back to
    0x03 elsewhere -- exactly the bug this docstring is warning the next
    reader away from (it happened once already, while building this tool:
    the ensemble-average brackets got overwritten with Delta on the first
    pass). Substitute by position, never by byte value alone.

    Runs the alignment **per page**, splitting `raw_text` on the form-feed
    (`\\f`) pdftotext -layout inserts between pages -- a whole-chapter
    alignment drifts badly over 10+ pages (SequenceMatcher loses the plot
    over long, repetitive mathematical text) and silently misses most
    occurrences; per-page windows are short enough to align cleanly.

    Returns (new_text, num_substituted).
    """
    pdf = pikepdf.open(pdf_path)
    raw_pages = raw_text.split("\f")
    n_pages = last_page - first_page + 1
    if len(raw_pages) not in (n_pages, n_pages + 1):
        print(f"WARNING: raw.txt has {len(raw_pages)} form-feed-delimited "
              f"segments, expected {n_pages} (or {n_pages + 1} with a "
              f"trailing one) for pages {first_page}-{last_page}. Page "
              f"alignment may be off.", file=sys.stderr)

    out_pages = []
    total_substituted = 0
    for i, raw_page_text in enumerate(raw_pages):
        pnum = first_page + i
        if pnum > last_page:
            out_pages.append(raw_page_text)  # trailing empty segment, if any
            continue
        cs_seq = content_stream_sequence_one_page(pdf.pages[pnum - 1])
        new_text, n = _align_page(raw_page_text, cs_seq)
        out_pages.append(new_text)
        total_substituted += n

    result = "\f".join(out_pages)

    # Confirmed literal overrides (see the table's own docstring) -- catches
    # the repeats position-alignment missed because they sat in a diff
    # block too large for the strict equal-length check to touch.
    for literal, resolved in CONFIRMED_LITERAL_OVERRIDES.items():
        count = result.count(literal)
        if count:
            result = result.replace(literal, resolved)
            total_substituted += count

    return result, total_substituted


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("raw", help="path to the chapter's .raw.txt")
    parser.add_argument("pdf", help="path to the source PDF")
    parser.add_argument("--page-range", nargs=2, type=int, required=True, metavar=("FIRST", "LAST"))
    parser.add_argument("--map", required=True, help="path to glyph-map.tsv")
    parser.add_argument("-o", "--out", required=True, help="output .extract.txt path")
    args = parser.parse_args(argv)

    raw_text = Path(args.raw).read_text(encoding="utf-8")

    resolved_text, num_substituted = resolve_positions(
        raw_text, args.pdf, args.page_range[0], args.page_range[1])
    print(f"Substituted {num_substituted} individual glyph occurrence(s) "
          f"at their exact positions (by PDF-declared glyph name).", file=sys.stderr)

    glyph_map = load_glyph_map(args.map)
    final_text = apply_map(resolved_text, glyph_map)

    Path(args.out).write_text(final_text, encoding="utf-8")
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
