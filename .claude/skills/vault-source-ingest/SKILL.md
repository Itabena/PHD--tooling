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
the wrong problem. So the statement is **extracted mechanically** — pulled from
the PDF with nothing in between that could paraphrase — then run through the
glyph map below, never through a model. Fallbacks, in order:

1. **Extracted + glyph-mapped text** by default (see below).
2. **A cropped screenshot** of the exercise embedded in the stub, when the
   extraction is unreadable — math-heavy exercises extract as noise. No model
   touches the content either way; the cost is the image is not searchable or
   quotable, so a quiz can never cite it (acceptable for a statement I read
   rather than search).
3. **A pointer** — chapter, problem number, page — when there is neither. An
   honest pointer beats a plausible transcription.

Never let a model fill the gap between these steps.

## The extraction artifact: what gets frozen

Implements `a - logistics/Source Note Types.md` -> "What exactly gets frozen"
(decided 23/07/2026) — read that section for the reasoning; this is the
mechanics. Extraction is two steps, and each freezes its own file, sitting
beside the note it serves, both frozen at ingest and never overwritten on
re-extraction (a new dated file instead):

1. **Tool extracts.** Run `pdftotext -layout` (poppler) over the PDF pages the
   note covers. This raw output is frozen unchanged as `<source name>.raw.txt`.
2. **Map repairs.** Run the raw text through `extraction/apply_glyph_map.py` in
   the tooling repo, against `extraction/glyph-map.tsv` — a plain, ordered,
   literal find/replace table (no regex, no inference, no LaTeX wrapping). The
   **result is the canonical artifact**, frozen as `<source name>.extract.txt`.
   Quote-matching (`vault-quizard`, once its PDF path exists) checks against
   this file, not the raw one — freezing the raw text but mapping downstream
   would make a quote containing a repaired glyph fail a check it should pass.

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

## See also

- [[a - logistics/Source Note Types|Source Note Types]] — the governing standard
- [[aa- Dashboard|AI Use Policy]] — scaffolding vs. review-required tiers
- [[a - logistics/Writing Style and Voice|Writing Style and Voice]] — governs how the body gets written (by me, later)
- `vault-quizard` — the downstream consumer of `<source name>.extract.txt`; its own PDF/quote-matching path is still deferred until that skill grows one
