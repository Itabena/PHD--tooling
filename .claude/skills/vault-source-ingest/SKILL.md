---
name: vault-source-ingest
description: "Scaffold a new source into a Sources/ folder in the Notes_phd vault. A paper becomes one note with a citation header; a book becomes a hub note plus empty per-chapter stubs plus an Exercises/ subfolder. Creates structure only — empty stubs, never summaries. Use when adding a paper or book to the vault."
---

# vault-source-ingest

Creates the scaffolding for a new source — a paper or a book — inside a `Sources/`
folder. The governing document is [[a - logistics/Source Note Types|Source Note Types]];
read it for the *why* behind every rule below. This file is the operational
contract, not a restatement — where it looks thin, the standard has the reasoning.

## The rule that governs everything

**Scaffolding is the skill's; understanding is mine.** The skill may create the
folder, the frontmatter, the citation header, the chapter stubs, and the
`Exercises/` subfolder. Everything that reads as understanding — takeaways,
objections, connections, chapter summaries — stays mine and is written later, by
me.

So **a stub with an empty body is the correct output of ingestion, not a failure
of it.** Do not fill a chapter stub with a paragraph summarizing the chapter to
make it look finished. If the skill *does* write prose that summarizes or reads
as understanding, it has crossed from scaffolding (allowed under the
[[aa- Dashboard|AI Use Policy]]) into first-pass notes (the review-required
tier), and that note **must be marked `#needs-review`** rather than filed
silently — an honesty flag for when the skill has overstepped.

## Frontmatter and tags

Every source note is a paper or a book, and the distinction lives in frontmatter
only: `type: paper` or `type: book` — never a tag, because it is a structural fact
the skill branches on, not something I browse by. **That rule is about `type`
alone; it is not a ban on tags.** Keyword and subject tags are exactly the
browsable thing the reasoning carves out — ingest proposes them (below).

## What ingest fills, and what it proposes

Implements the standard's section of the same name. Two tiers, and the boundary
is the point:

**Fills — mechanical metadata I skip when rushed and then can't find later:**

- the `type` frontmatter;
- the citation header standard across `Statistical Mechanics/Sources/` — author,
  year, venue, DOI;
- a **Zotero link**, `zotero://open-pdf/library/items/<item key>`, built from the
  item key (ask for it, or look it up in the Zotero library — the `zotero` tools
  can search it). The old archived template prompted for this key; the convention
  carries over unchanged.

**No prose section skeleton.** The old templates' fixed headings — abstract,
contributions, methods, results, strengths/weaknesses — are gone and not to be
reinstated in the note. Write prose the way the rest of the vault does: continuous,
headers only at real topic boundaries ([[a - logistics/Writing Style and Voice|Writing Style and Voice]]).

**Proposes — never writes silently:** keyword tags, and wikilinks to related notes
*already in the vault*. Both go at the **bottom** of the note in a clearly marked
block, as candidates for me to accept, edit, or delete — I commit them, not the
skill. Ground every proposal in something concrete: the source's own subject, its
reference list, a concept it names that already has a note. The AI Use Policy
allows suggesting links between existing notes but not inventing unjustified
connections, and the gap is thin — so a suggested link whose reason is not
immediately visible is one to leave out, not offer.

## Paper

One note, and it stays one note — a paper has no parts read on separate days. It
carries the citation header already standard across `Statistical Mechanics/Sources/`
(see [[Equivalence and Nonequivalence of Ensembles - Touchette 2015]] and
[[Statistical mechanics and dynamics of solvable models with long-range interactions - Campa Dauxois Ruffo 2009]]
as the model):

```
---
type: paper
---

# <Full title>

**Author(s):** …
**Year:** …
**Venue:** … (journal / arXiv id / DOI)
**Zotero:** [open](zotero://open-pdf/library/items/<item key>)

## Why this is on the reading list


---
*Ingest proposals — accept, edit, or delete; nothing here is filed until I keep it.*
**Tags:** #keyword-one #keyword-two
**Related:** [[An existing note]] · [[Another existing note]]
```

Fill the factual header (author, year, venue, DOI, Zotero link) — that is
metadata. Leave the body between the header and the proposals empty: the "why this
is on the reading list" reasoning and everything after it are mine. If the person
gives a one-line reason when asking for the ingest, place that line; otherwise
leave the heading for them. Do not draft a digested abstract — that is the
`#needs-review` trap above. The proposals block sits at the very bottom; the tags
and related links in it are candidates, not content.

## Book

A book is read and cited in pieces, so it becomes a **hub note + per-chapter
stubs + an `Exercises/` subfolder**, all inside the book's folder under
`Sources/`. It should come out looking roughly like the
`Phd courses/Information theory for natural scientists` course folder (chapter
notes + `Exercises/` per chapter) **minus the appendix**, which is
course-specific. If it comes out looking like something very different, the
convention is probably being applied wrong.

Layout:

```
<Subject>/Sources/<Book title — Authors Year>/
    <Book title>.md          ← hub note: citation header (type: book) + chapter list
    Chapter 1 — <title>.md   ← empty stub
    Chapter 2 — <title>.md   ← empty stub
    …
    Exercises/               ← per the ask below
    Extraction/              ← raw.txt/extract.txt per chapter, screenshot PNGs (PDF sources only)
```

- **Hub note**: the same citation header as a paper (with `type: book`, plus the
  Zotero link), followed by a chapter list where each entry links to that
  chapter's stub note. The chapter list is structure; do not annotate it with what
  each chapter is about. The ingest proposals block (tags, related notes) goes at
  the bottom of the hub note, same as a paper.
- **Chapter stubs**: one note per chapter, empty body, linked back to the hub — no
  proposals block. Reading the source to recover chapter *titles* and *numbers* is
  scaffolding and fine; writing chapter *summaries* is not (`#needs-review`).

### Exercises: stop and ask

The `Exercises/` subfolder is the one part the skill does **not** decide on its
own. After you have the chapter list, **stop and ask** which of three the person
wants:

1. **All now** — exercise stubs extracted for every chapter.
2. **Deferred** — just the empty `Exercises/` folder, nothing inside.
3. **Named chapters** — exercise stubs only for the chapters named at that moment.

Lean toward eager (an empty folder is cheap, a missing one interrupts later) but
the lean is not strong enough to assume — wait for the answer before creating
anything under `Exercises/`. The standard explains why this stays a question.

#### Shape of an exercise stub

When exercises are extracted (options 1 or 3), the shape is **one folder per
chapter, `Exercises/Chapter N/`, with one note per exercise inside it** — not a
flat folder of compound-named files, and *not one note per chapter* (the first
Pathria ingest's mistake: it read the paragraph above literally and produced
sixteen chapter stubs). A chapter's problems belong together and reachable on
their own; a flat list across every chapter is hundreds of files in one place.

Each exercise note carries two blocks: the **statement at the top**, and an
**empty attempt block** below it. The attempt block is empty for the same reason
every other stub body is — that part is the work.

#### Where the statement comes from — never a model

The statement is the one place a model must not write the content. A retyped
exercise drifts silently — a flipped sign, a dropped subscript, a lost condition
in a subclause — and a subtly wrong statement costs hours spent carefully solving
the wrong problem. So the statement is never transcribed by a model, full stop.

**One shape for every exercise (decided 23/07/2026, superseding the earlier
extract-then-screenshot waterfall): a screenshot, plus a plain-text pointer and
a Zotero deep link, always together.** Comparing both on the problems that did
extract cleanly, the screenshot won anyway — visually faithful, no PDF-artifact
noise, nothing to read carefully for a mangled subscript. Once the crop is
automatic there is no real cost to always taking it, so text extraction is no
longer attempted as an exercise-statement path at all (it remains exactly how a
*chapter's* `.extract.txt` gets built, which is a different job — see below).

1. **A cropped screenshot**, automated by
   `extraction/crop_exercise_screenshot.py` in the tooling repo: `pdftotext
   -bbox` locates the problem's region from its own label to the next one,
   `pdftoppm` renders the page, Pillow crops it. Purely mechanical, same
   discipline as the glyph map — it locates a *position*, never reads content
   for meaning. It refuses (rather than guesses) on three cases: the problem
   spans a page break, the page looks multi-column and the region straddles
   both sides, or there is no next label to bound the crop against (the last
   problem in a chapter). A refusal falls through to the floor below.
   **Not bit-for-bit reproducible run-to-run** (confirmed on Windows,
   2026-07-23): re-cropping the same page can differ by a pixel or two of
   antialiasing between separate `pdftoppm` renders. Content is always
   correct; don't expect an exact byte/hash match against a previous crop of
   the same problem as a correctness check — compare visually or by pixel
   diff, not by hash.
2. **A Zotero deep link plus a plain-text pointer** (chapter, problem number,
   page) — always both together, never either alone, and always present
   alongside the screenshot when one exists: the screenshot is not searchable
   or quotable, so the link/pointer is what lets me jump to the page rather
   than just read the image. The link is a dependency (needs Zotero installed
   and synced, which isn't true on mobile Obsidian or an unset-up machine), so
   the plain pointer is what's left when it doesn't resolve. Where a crop
   cannot be produced at all, this pair is the floor on its own.

Never let a model fill the gap between these steps.

## The extraction artifact: what gets frozen, and where it lives

Implements `a - logistics/Source Note Types.md` -> "What exactly gets frozen"
and "Scope of a frozen extract" (both decided 23/07/2026) — read those sections
for the reasoning; this is the mechanics. Extraction is two steps, and each
freezes its own file, both frozen at ingest and never overwritten on
re-extraction (a new dated file instead):

1. **Tool extracts.** Run `pdftotext -layout` (poppler) over the **whole
   chapter's** physical page range, not just a section of it — a
   Problems-only extract is enough for exercise stubs and useless for
   anything else, and `vault-quizard` fixes quiz generation at one chapter at
   a time, reading this same file. This raw output is frozen unchanged as
   `<chapter name>.raw.txt`.
2. **Map repairs.** Run the raw text through `extraction/apply_glyph_map.py` in
   the tooling repo, against `extraction/glyph-map.tsv` — a plain, ordered,
   literal find/replace table (no regex, no inference, no LaTeX wrapping). The
   **result is the canonical artifact**, frozen as `<chapter name>.extract.txt`.
   `vault-quizard`'s quote-matching checks against this file, not the raw one —
   freezing the raw text but mapping downstream would make a quote containing
   a repaired glyph fail a check it should pass.
3. **Math-glyph resolution (added 2026-07-23, optional, run after step 2).**
   `extraction/resolve_math_glyphs.py PDF.pdf CHAPTER.raw.txt --page-range N M
   --map extraction/glyph-map.tsv -o CHAPTER.extract.txt` resolves a real
   subset of the control-byte fallbacks `apply_glyph_map.py` can only flag —
   by reading each font's own `/Encoding /Differences` array straight out of
   the PDF (via `pikepdf`) and mapping the declared glyph name to Unicode via
   the Adobe Glyph List (`fontTools.agl`), substituting only at the exact
   position confirmed by aligning against the PDF's content stream. Needs
   `pikepdf` + `fontTools` in the `pdftools` env (conda-forge, same pinning
   discipline as poppler/Pillow). Cut Pathria Ch.2 from 95 to 60 flagged
   lines with zero incorrect substitutions, once a real bug was fixed along
   the way (see the tool's own docstring: a byte-value resolution applied as
   a blind global replace silently overwrote an unrelated glyph that
   happens to share the same fallback byte elsewhere — substitution must be
   positional, never by byte value alone). Genuinely can't reach isolated
   symbols inside stacked multi-line equations (integral bounds, big
   parens) — the content stream draws those out of reading order for
   layout, which defeats simple stream-order alignment. **No automated
   fallback exists for these** — unlike an exercise statement, a chapter
   passage has no clean label-to-next-label boundary to crop against, so
   `crop_exercise_screenshot.py`'s mechanism doesn't apply here. The lines
   stay correctly flagged (never guessed) and simply can't be used as a
   verbatim `source_quote` for a quiz question; the underlying content
   isn't lost from the vault or unreadable to a person, it's just
   unavailable to the automated quote-verification step specifically.

Both files, plus any exercise screenshot PNGs, go in an **`Extraction/`
subfolder inside the book's own folder** — not loose beside the chapter stub
notes, which stays just the hub note, the chapter stubs, and `Exercises/`.
Named to avoid colliding with the vault's own top-level `a - logistics/` folder
in search and links.

The map is a **versioned data file in the tooling repo**
(`phd-tooling/extraction/glyph-map.tsv`), not prose here, because it must be
byte-identical on every machine — a map that drifts between Mac and Windows
means the same PDF extracts to two different frozen files. It holds 1:1
substitutions only: standard ligature decompositions, and specific extractor
glyph-name artifacts confirmed against real output (never guessed in advance).

**Letter-spacing is not the map's job.** A word extracted as separated
characters (`T w o s y s t e m s`) has no lookup-table fix — single letters
separated by spaces are everywhere in physics notation (`n k T`, a loose index),
so a rejoin rule would corrupt legitimate notation as often as it fixes garbled
prose. `apply_glyph_map.py --flag-letter-spacing` detects a suspected run and
reports it; it never rewrites. A flagged line is a candidate for the screenshot
fallback above, decided by hand.

**Confirmed non-injective fallback bytes (why a blind add-to-the-map fix
doesn't work): the same byte can mean different glyphs in different places,
even within one chapter.** First seen in Pathria Ch.1 (byte `0x04` served
both Ω in running prose and one stroke of an oversized stacked parenthesis).
Confirmed recurring in Ch.2 (2026-07-23): byte `0x03` is Δ in `(E − Δ, E]`
but the ensemble-average brackets `⟨`/`⟩` a few lines later; byte `0x07` is
an integral sign in the Liouville flux equations but Γ (Pathria's own symbol
for multiplicity, not the more common Ω) in `S = k ln Γ = k ln(ω/ω0)`. A
single `glyph-map.tsv` row per byte would be wrong in roughly half its own
occurrences in a case like this.

**Don't trust "obvious" physics convention over what the font actually
declares — this was gotten wrong twice while resolving Ch.2** (2026-07-23):
the first pass assumed the energy-width symbol must be ε (textbook
convention) and the multiplicity symbol must be Ω (ditto) — both wrong.
The PDF's own `/Encoding /Differences` array said `Delta1` and `Gamma1`
respectively, and a direct crop of the rendered glyph confirmed it: Pathria's
own notation is Δ and Γ, not the more textbook-common ε and Ω. Trust the
font's declared glyph name (or a direct visual crop when the name itself is
ambiguous, like MathType's own operator-variant names) over what convention
says "should" be there — see `resolve_math_glyphs.py`, added the same day
this was caught.

## See also

- [[a - logistics/Source Note Types|Source Note Types]] — the governing standard
- [[aa- Dashboard|AI Use Policy]] — scaffolding vs. review-required tiers
- [[a - logistics/Writing Style and Voice|Writing Style and Voice]] — governs how the body gets written (by me, later)
- `vault-quizard` — the downstream consumer of `<chapter name>.extract.txt`; generates and verifies one chapter's quiz at a time against exactly this file
