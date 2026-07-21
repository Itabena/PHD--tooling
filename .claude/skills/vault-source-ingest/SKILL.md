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

## Deferred: the `.extract.txt` extraction artifact

Source Note Types describes freezing the PDF's extracted text into a
`<source name>.extract.txt` at ingest. **Do not create it yet.** Nothing consumes
it until PDF quizzing exists — `vault-quiz` is markdown-only today and its
PDF/`.extract.txt` quote-matching is deferred for the same reason. Build it when
`vault-quiz` grows the PDF path, so the format is exercised the day it is written
rather than guessed at now. Reading a PDF to recover citation metadata and
chapter titles for the scaffolding is fine — that is different from persisting the
frozen artifact.

## See also

- [[a - logistics/Source Note Types|Source Note Types]] — the governing standard
- [[aa- Dashboard|AI Use Policy]] — scaffolding vs. review-required tiers
- [[a - logistics/Writing Style and Voice|Writing Style and Voice]] — governs how the body gets written (by me, later)
- `vault-quiz` — the downstream consumer whose PDF path gates the `.extract.txt` deferral
