#!/usr/bin/env python3
"""Apply glyph-map.tsv to raw extractor output. Plain string substitution only.

Governed by `a - logistics/Source Note Types.md` -> "What exactly gets frozen".
Extraction is two steps: a tool pulls text out of a PDF (the raw output, frozen
as `<source name>.raw.txt`), and this script repairs the predictable, tool-level
corruptions in that output (frozen as `<source name>.extract.txt` — the
canonical artifact that quote-matching checks against). Both stay frozen; a
substitution here does not retroactively fix an already-written .extract.txt.

No regex, no inference, no LaTeX wrapping — each row in glyph-map.tsv is a
literal find/replace applied in file order. Comment lines (`#...`) and blank
lines in the map are skipped.

Deliberately NOT here: letter-spacing collapse ("T w o" -> "Two"). See
--flag-letter-spacing, which only reports suspected lines; it never rewrites
them. That failure mode is a readability problem the standard routes to the
screenshot fallback, not a character-encoding problem this script can fix by
substitution.

Also deliberately not repaired: a raw control byte (ASCII < 0x20, not
newline/tab) that pdftotext emits when a font glyph has no Unicode mapping it
knows. The tempting fix is a table entry (e.g. `\x04` -> `Omega`), and the
Pathria chapter-1 extraction is exactly why that is unsafe: pdftotext reused
byte 0x04 both for the symbol Omega in running prose and, elsewhere in the same
document, for one stroke of an oversized stacked parenthesis around a partial
derivative. Same byte, two unrelated meanings depending on where it sits --
telling them apart needs context, and a literal-substitution table has no
context to use. Guessing from context is the inference this file exists to
rule out. See --flag-unmapped-glyphs, detection only, never repaired: a
surviving stray byte is the extraction-is-noise signal the standard already
routes to the screenshot fallback.

Usage:
    python3 apply_glyph_map.py RAW.txt --map glyph-map.tsv -o OUT.extract.txt
    python3 apply_glyph_map.py RAW.txt --map glyph-map.tsv --flag-letter-spacing
    python3 apply_glyph_map.py RAW.txt --map glyph-map.tsv --flag-unmapped-glyphs
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
DEFAULT_MAP = HERE / "glyph-map.tsv"

# A run of this many or more consecutive single-alphabetic-character "words"
# is treated as suspected letter-spacing corruption rather than legitimate
# physics notation. Real notation strings together isolated single letters
# occasionally (n k T, a loose index) but rarely five or more in a row --
# that run length is what a spaced-out word ("T w o s y s t e m s") produces.
LETTER_SPACING_RUN = 5
_SINGLE_LETTER = re.compile(r"^[A-Za-z]$")


def load_glyph_map(path: Path) -> list[tuple[str, str]]:
    """Parse glyph-map.tsv into an ordered list of (from, to) pairs."""
    rows: list[tuple[str, str]] = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: expected 'from<TAB>to', got {line!r}")
            rows.append((parts[0], parts[1]))
    return rows


def apply_map(text: str, rows: list[tuple[str, str]]) -> str:
    """Literal, ordered string substitution -- no regex, no inference."""
    for from_, to in rows:
        text = text.replace(from_, to)
    return text


def flag_letter_spacing(text: str) -> list[tuple[int, str]]:
    """Return (1-based line number, line text) for lines with a suspected
    letter-spacing run. Detection only -- never repaired here."""
    flagged: list[tuple[int, str]] = []
    for i, line in enumerate(text.split("\n"), start=1):
        tokens = line.split(" ")
        run = 0
        best = 0
        for tok in tokens:
            if _SINGLE_LETTER.match(tok):
                run += 1
                best = max(best, run)
            else:
                run = 0
        if best >= LETTER_SPACING_RUN:
            flagged.append((i, line))
    return flagged


def flag_unmapped_glyphs(mapped_text: str) -> list[tuple[int, str, str]]:
    """Return (1-based line number, hex byte, line text) for every stray control
    character surviving in *already-mapped* text. Run this after apply_map, not
    before -- the point is to catch what the map's literal entries did not (and,
    per the module docstring, should not try to) resolve. Detection only."""
    flagged: list[tuple[int, str, str]] = []
    for i, line in enumerate(mapped_text.split("\n"), start=1):
        for ch in line:
            if ord(ch) < 32 and ch not in ("\t",):
                flagged.append((i, hex(ord(ch)), line))
                break
    return flagged


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("raw", help="path to the raw extractor output (.raw.txt)")
    parser.add_argument("--map", default=str(DEFAULT_MAP), help="path to glyph-map.tsv")
    parser.add_argument("-o", "--out", help="write mapped text here (default: stdout)")
    parser.add_argument("--flag-letter-spacing", action="store_true",
                        help="print suspected letter-spacing lines to stderr; detection only")
    parser.add_argument("--flag-unmapped-glyphs", action="store_true",
                        help="print lines with a stray control byte after mapping; detection only")
    args = parser.parse_args(argv)

    with open(args.raw, encoding="utf-8") as fh:
        raw_text = fh.read()

    rows = load_glyph_map(Path(args.map))
    mapped = apply_map(raw_text, rows)

    if args.flag_letter_spacing:
        flagged = flag_letter_spacing(raw_text)
        for lineno, line in flagged:
            print(f"letter-spacing? line {lineno}: {line.strip()!r}", file=sys.stderr)
        if flagged:
            print(f"{len(flagged)} line(s) flagged -- review for the screenshot "
                  f"fallback, not repaired here.", file=sys.stderr)

    if args.flag_unmapped_glyphs:
        glyph_flagged = flag_unmapped_glyphs(mapped)
        for lineno, byte, line in glyph_flagged:
            print(f"unmapped glyph {byte}? line {lineno}: {line.strip()!r}", file=sys.stderr)
        if glyph_flagged:
            print(f"{len(glyph_flagged)} line(s) flagged -- extraction produced an "
                  f"unrenderable glyph; do not guess its identity, route to the "
                  f"screenshot fallback.", file=sys.stderr)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(mapped)
    else:
        sys.stdout.write(mapped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
