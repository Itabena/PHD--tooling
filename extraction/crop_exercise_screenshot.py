#!/usr/bin/env python3
"""Crop a single exercise statement out of a PDF page as a PNG screenshot.

Governed by `a - logistics/Source Note Types.md` -> "The screenshot tier is
automatable." Same discipline as glyph-map.tsv: this locates and crops a
*position* in the PDF, it never reads or infers what the content means. The
only judgment a human makes is looking at the resulting image afterward and
deciding whether the crop is right -- "a bad crop is visibly bad."

Pipeline
--------
1. `pdftotext -bbox` on the target page gives word-level bounding boxes in PDF
   points (72 per inch), independent of any render resolution.
2. The target problem's region is located mechanically: find the word token
   matching its label (e.g. "1.7."), find the word token matching the next
   problem's label (e.g. "1.8."), and take the bounding-box union of every
   word from the first (inclusive) to the second (exclusive). No text is read
   for meaning -- only word identity (exact label match) and position.
3. `pdftoppm -r <dpi> -png` renders the same page as a bitmap.
4. The point-space bbox is converted to pixel space by multiplying by
   dpi/72 (bbox coordinates are always in points at 72 dpi regardless of the
   resolution the page is rendered at), a small padding margin is added, and
   Pillow crops the rendered page to that pixel box.

What this refuses to do
------------------------
Three situations have no mechanically safe way to bound the crop region, so
each raises CropRefused instead of guessing:

  - **Page break.** The label is found on the target page but the next
    label isn't -- the problem's true extent might run onto the following
    page, and silently cropping to the bottom of the current page would cut
    it off without saying so.
  - **Multi-column bleed.** The collected words' x-range straddles what looks
    like two separate column bands on the page (a wide horizontal gap with no
    word crossing it). A single crop across two columns is not one region.
  - **No next label.** The caller has nothing to bound the crop against (the
    last problem in a chapter, or the last one being processed in a batch).
    Guessing a bottom margin is exactly the content inference this tool must
    not do.

Usage
-----
    python3 crop_exercise_screenshot.py PDF.pdf --page 54 \\
        --label "1.7." --next-label "1.8." \\
        --render-dpi 200 -o out/pathria-beale-1-7-statement.png

Omit --next-label to explicitly signal there is none (forces a refusal for
that reason rather than a silent guess).
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

try:
    from PIL import Image
except ImportError:  # pragma: no cover - environment guard, not a code path
    Image = None

PDFTOTEXT = "pdftotext"
PDFTOPPM = "pdftoppm"
POINTS_PER_INCH = 72.0
# Small margin so a crop doesn't shave the edge of a word that sits exactly on
# the computed boundary. Purely cosmetic; does not affect region selection.
# Tuned down from 4.0 after the first real batch (Pathria ch.1): at 4pt the
# bottom margin was wide enough to nick a sliver of the *next* problem's first
# line on tightly-spaced pages (6 of 7 crops). 1.5pt still keeps full glyphs
# but stops crossing into an adjacent line's row.
PAD_POINTS = 1.5


class CropRefused(Exception):
    """Raised for any of the three cases with no safe mechanical answer."""


@dataclass
class Word:
    text: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class BBoxUnion:
    x_min: float
    y_min: float
    x_max: float
    y_max: float


# XML 1.0 forbids raw control bytes below 0x20 other than tab/CR/LF. The same
# unmapped-glyph fallback bytes documented in glyph-map.tsv (a font glyph
# poppler can't map to Unicode) show up inside <word> text here too, and break
# ElementTree's parser outright. Stripping them is a parsing-robustness fix
# only -- it touches a <word>'s text content, never its xMin/yMin/xMax/yMax
# attributes, so no position data is altered. A label token is plain ASCII by
# construction, so this can never change which word matches a label search.
_ILLEGAL_XML_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def run_pdftotext_bbox(pdf_path: str, page: int) -> tuple[float, float, list[Word]]:
    """Run `pdftotext -bbox` on a single page and parse the word list.

    Returns (page_width_pt, page_height_pt, words_in_reading_order).
    """
    result = subprocess.run(
        [PDFTOTEXT, "-bbox", "-f", str(page), "-l", str(page), pdf_path, "-"],
        capture_output=True, text=True, check=True,
    )
    sanitized = _ILLEGAL_XML_CONTROL.sub("", result.stdout)
    root = ET.fromstring(sanitized)
    # pdftotext -bbox wraps the output in an xhtml-namespaced <html>, so a
    # bare ".//page" search silently matches nothing -- match by local name
    # instead of hardcoding (or fighting version drift in) the namespace URI.
    def local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    page_el = next((el for el in root.iter() if local_name(el.tag) == "page"), None)
    if page_el is None:
        raise CropRefused(f"pdftotext -bbox produced no <page> element for page {page}")
    width = float(page_el.get("width"))
    height = float(page_el.get("height"))
    words = [
        Word(
            text=w.text or "",
            x_min=float(w.get("xMin")), y_min=float(w.get("yMin")),
            x_max=float(w.get("xMax")), y_max=float(w.get("yMax")),
        )
        for w in page_el if local_name(w.tag) == "word"
    ]
    return width, height, words


def find_label_index(words: list[Word], label: str) -> Optional[int]:
    """Find the position of the word token exactly matching `label`.

    Exact string match only -- this is a position lookup, not a text search
    that could match a similarly-shaped cross-reference elsewhere on the page.
    """
    for i, w in enumerate(words):
        if w.text == label:
            return i
    return None


# A page is flagged as (at least) two-column if sorting all word x-positions
# reveals a horizontal gap wider than this fraction of the page width with no
# word crossing it -- i.e. a vertical gutter rather than ordinary word/column
# spacing. Not validated against a real multi-column PDF yet (Pathria is
# single-column); revisit the threshold when one is ingested.
COLUMN_GUTTER_FRACTION = 0.12


def detect_column_gutter(all_page_words: list[Word], page_width: float) -> Optional[tuple[float, float]]:
    """Return (gutter_start, gutter_end) in points if the page looks
    multi-column, else None. Operates on every word on the page, not just the
    region being cropped, since the gutter is a property of the page layout.
    """
    if not all_page_words:
        return None
    intervals = sorted((w.x_min, w.x_max) for w in all_page_words)
    merged: list[list[float]] = []
    for x0, x1 in intervals:
        if merged and x0 <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], x1)
        else:
            merged.append([x0, x1])
    threshold = page_width * COLUMN_GUTTER_FRACTION
    for (a0, a1), (b0, b1) in zip(merged, merged[1:]):
        if (b0 - a1) >= threshold:
            return (a1, b0)
    return None


def locate_region(
    pdf_path: str, page: int, label: str, next_label: Optional[str],
) -> BBoxUnion:
    """Locate the bounding-box union for `label`'s statement on `page`.

    Raises CropRefused for any of the three unsafe cases.
    """
    if next_label is None:
        raise CropRefused(
            f"no next label given for {label!r} -- nothing to bound the crop "
            f"against (last problem in the batch/chapter); guessing a bottom "
            f"margin would be content inference, not position lookup."
        )

    width, height, words = run_pdftotext_bbox(pdf_path, page)

    start_idx = find_label_index(words, label)
    if start_idx is None:
        raise CropRefused(f"label {label!r} not found on page {page}")

    end_idx = find_label_index(words, next_label)
    if end_idx is None:
        raise CropRefused(
            f"next label {next_label!r} not found on page {page} -- "
            f"{label!r}'s statement may spill onto the following page "
            f"(page break); refusing rather than guess where it ends."
        )
    if end_idx <= start_idx:
        raise CropRefused(
            f"next label {next_label!r} appears before {label!r} on page "
            f"{page} in reading order -- label ordering assumption violated, "
            f"refusing rather than guess."
        )

    region_words = words[start_idx:end_idx]

    gutter = detect_column_gutter(words, width)
    if gutter is not None:
        g0, g1 = gutter
        straddles = any(w.x_min < g0 and w.x_max > g0 for w in region_words) or (
            any(w.x_max <= g0 for w in region_words) and any(w.x_min >= g1 for w in region_words)
        )
        if straddles:
            raise CropRefused(
                f"page {page} looks multi-column (a gutter at x∈[{g0:.1f},{g1:.1f}] pt "
                f"with no word crossing it) and {label!r}'s region spans both "
                f"sides of it -- refusing rather than crop across two columns."
            )

    x_min = min(w.x_min for w in region_words)
    y_min = min(w.y_min for w in region_words)
    x_max = max(w.x_max for w in region_words)
    y_max = max(w.y_max for w in region_words)
    return BBoxUnion(x_min, y_min, x_max, y_max)


def render_page_png(pdf_path: str, page: int, dpi: float, out_png_prefix: str) -> Path:
    """Render a single page to PNG via pdftoppm. Returns the produced file path."""
    subprocess.run(
        [PDFTOPPM, "-r", str(dpi), "-png", "-f", str(page), "-l", str(page),
         "-singlefile", pdf_path, out_png_prefix],
        check=True,
    )
    produced = Path(f"{out_png_prefix}.png")
    if not produced.exists():
        raise RuntimeError(f"pdftoppm did not produce {produced}")
    return produced


def crop_region(page_png: Path, region: BBoxUnion, dpi: float, out_path: Path) -> None:
    """Crop the rendered page image to `region`, converting points -> pixels."""
    if Image is None:
        raise RuntimeError("Pillow is not installed in this environment")
    scale = dpi / POINTS_PER_INCH
    pad = PAD_POINTS
    box = (
        max(0, (region.x_min - pad) * scale),
        max(0, (region.y_min - pad) * scale),
        (region.x_max + pad) * scale,
        (region.y_max + pad) * scale,
    )
    with Image.open(page_png) as im:
        box = (
            box[0], box[1],
            min(box[2], im.width), min(box[3], im.height),
        )
        cropped = im.crop(tuple(int(round(v)) for v in box))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(out_path)


def crop_exercise(
    pdf_path: str, page: int, label: str, next_label: Optional[str],
    render_dpi: float, out_path: Path, tmp_dir: Path,
) -> Path:
    """End-to-end: locate, render, crop. Returns the written PNG path."""
    region = locate_region(pdf_path, page, label, next_label)
    prefix = str(tmp_dir / f"page-{page}-render")
    page_png = render_page_png(pdf_path, page, render_dpi, prefix)
    crop_region(page_png, region, render_dpi, out_path)
    return out_path


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("pdf", help="path to the source PDF")
    parser.add_argument("--page", type=int, required=True, help="physical PDF page (1-based)")
    parser.add_argument("--label", required=True, help='exact label token, e.g. "1.7."')
    parser.add_argument("--next-label", default=None,
                        help='exact next label token, e.g. "1.8."; omit if none exists')
    parser.add_argument("--render-dpi", type=float, default=200.0)
    parser.add_argument("-o", "--out", required=True, help="output PNG path")
    parser.add_argument("--tmp-dir", default="/tmp", help="scratch dir for the rendered page PNG")
    args = parser.parse_args(argv)

    if shutil.which(PDFTOTEXT) is None or shutil.which(PDFTOPPM) is None:
        print(
            "poppler not found -- run via `micromamba run -n pdftools`",
            file=sys.stderr,
        )
        return 2

    try:
        out_path = crop_exercise(
            args.pdf, args.page, args.label, args.next_label,
            args.render_dpi, Path(args.out), Path(args.tmp_dir),
        )
    except CropRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
