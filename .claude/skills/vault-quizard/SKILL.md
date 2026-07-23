---
name: vault-quizard
description: "Generate a self-quiz for one chapter of a source in the Notes_phd vault, verified against that chapter's frozen extraction artifact, following Quiz Standards.md: verbatim quote-matching, balanced-key permutation, four rejection reasons, and a feedback loop captured while taking the quiz."
---

# vault-quizard

Generates a self-quiz from a source so I can test whether a chapter actually
absorbed. The governing document is `a - logistics/Quiz Standards.md` in the
vault — read it in full before generating anything; it was substantially
revised and this file implements it, not restates it.

## Scope: one chapter, from its frozen extract

A quiz is generated **per chapter, never per book** — a whole book's extract is
too large to read at once, and more importantly a question from chapter 3 tells
me nothing about whether chapter 9 landed, which is the only thing a quiz is
for. `source_file` in the draft should point at that chapter's frozen
`<chapter>.extract.txt` (see `a - logistics/Source Note Types.md`), sitting
beside the chapter's stub note.

**Questions come from sources, not from my own notes.** The verbatim check works
identically against a markdown note as against an extract — architecturally
either is a valid `source_file` — but the *trust* is not the same. My notes
carry `#verified`, `#proofread`, `#needs-review` precisely because reliability
varies; generating off a `#needs-review` note tests me against my own unchecked
draft while every automated check passes. Prefer the frozen extract wherever one
exists. If generating off a note, check its status tag first and refuse a
`#needs-review` one — say so rather than generate anyway.

**Never generate a question from compressed text.** If a chapter's extract is
large enough that I read a compressed rendering of it to decide what's worth
asking about, that's fine — surveying is exactly what compression is for. But
the moment I write a `source_quote`, pull the exact span from the *uncompressed*
extract first. A quote lifted from a compressed rendering is a quote of the
compression, not of the source: it either fails the verbatim check or gets
silently reconstructed into something plausible, which is the model-transcription
failure this whole standard exists to prevent, reintroduced one layer up.

A quiz spanning several chapters is **assembled, not generated**: each chapter's
questions are generated and verified independently against that chapter's own
extract, producing a `*.quiz-bank.json` per chapter (see below). Combining
chapters into one quiz is concatenating question banks — no chapter's source is
ever reloaded to do it. The question bank is the durable artifact; any one quiz
is just a view over it.

## Generating questions

Before writing anything, refresh and read `rejection-patterns.md` — run
`python3 distill_rejections.py` first (see "Distillation" below), then read the
file, since it is only ever as current as the last time someone did that.

The two failure modes the standard names are prevented **here, in how the
questions are written** — the build script is only a backstop:

- **Every distractor is a specific claim a half-understanding reader would
  genuinely believe** — ideally a real misconception the source itself warns
  against. This is the actual fix for longest-answer bias: written this way, a
  distractor ends up about as long as the correct answer for honest reasons. Do
  **not** pad distractors to match length — padded wrong answers read as padded
  and just teach a new tell.
- **No absolutes in distractors** — no *always*, *never*, *every*, *impossible*.
  They are near-automatic eliminations for anyone who has taken a test.
- **Every option must parse grammatically after the stem.** If only the correct
  option reads correctly, grammatical agreement gives it away — rewrite the stem
  so agreement is not a signal, or fix the options.
- **No general knowledge.** If the source does not say it, there is no question
  about it, even when the missing statement is true and standard. A quiz mixing
  sourced and unsourced questions cannot separate gaps in my reading from gaps in
  the model, which is the only reason to run it.
- **Don't lean on "this chapter states" / "according to the text" as stem
  filler.** `source_file` and `location` already carry that; the stem should
  just ask the question directly (flagged on the first real calibration run —
  every stem had it, and it added nothing).

### Draft format (`*.quiz-draft.md`)

```
---
source_file: Statistical Mechanics/Sources/.../Chapter 1.extract.txt
---

## Q1  (optional title after the number)
Stem text, which may span
several lines until the first option.

- [x] The correct option (exactly one per question).
- [ ] A specific claim a half-understanding reader would believe.
- [ ] Another believable misconception.
- [ ] A third.

quote: a verbatim span copied from source_file
location: p. 12, ch. 3
```

`- [x]` marks the correct option; `- [ ]` marks a distractor (Obsidian's
checkbox syntax, so a draft still renders sanely in the vault). `quote:` and
`location:` are the standard's traceability fields; a missing one warns rather
than fails, so the build always runs.

Three question kinds, inferred from the options (no marker needed, though a
`*(True/False)*` / `*(select one or more)*` marker in the stem is tolerated and
stripped):

- **single-correct MC**: one `[x]`, two or more options — permuted onto the
  balanced key, length backstop applies.
- **True/False**: exactly two options, literally `True` and `False`, one `[x]`.
  Truth is fixed by the statement, so never permuted or balanced — write a mix
  of true and false statements yourself.
- **multi-select**: two or more `[x]` plus at least one distractor. Permuted (no
  single position to balance); the key lists every correct letter.

## Building the quiz

```
python3 build_quiz.py path/to/chapter.quiz-draft.md
```

The vault root is found automatically from the `.obsidian` marker above the
draft (override with `--vault-root`, or set `$NOTES_PHD_VAULT`). The build:

- **Verifies every quote.** Literal substring match (tolerant of line-wrap
  whitespace) of `source_quote` against `source_file`. A miss raises a
  conspicuous `[!danger]` callout, never a build failure — flagged for
  adjudication at quiz time. **Read a mismatch as "check the extraction" before
  "the model lied."** Poppler's glyph-repair fallback byte is not one-to-one
  (`a - logistics/Source Note Types.md`), so a garbled quote near a math symbol
  is now the *likely* explanation, not the exception — reject as
  `extraction-artifact`, not `fabricated-quote`, unless there's a specific
  reason to think otherwise.
- **Balances the answer key, never randomizes.** Single-correct MC options are
  permuted onto a balanced key so correct answers land as close to equally
  across A/B/C/D as the arithmetic allows over the whole quiz.
- **Flags longest-answer bias** as a backstop (MC only) — a warning, not a
  failure; the fix is better distractors.
- **Writes two durable outputs**: a human-readable `*.quiz.md` and a
  `*.quiz-bank.json` question bank. The bank is what an HTML quiz builder or a
  future multi-chapter assembler reads; the Markdown is for eyeballing the
  chapter's set at a glance.

**Both land in the source's own `Quizzes/` subfolder by default** — derived from
`source_file`, not from wherever the draft happens to sit. For
`.../Pathria/Extraction/Chapter 1.extract.txt` that's `.../Pathria/Quizzes/`;
for `.../ITFNS/Lecture notes/Chapter 1 (ITFNS).md` that's `.../ITFNS/Quizzes/`
— the existing ITFNS `Quizzes/` folder is exactly this convention, generalized.
Override with `-o`/`--bank-out` when the guess is wrong (a paper has no natural
per-paper folder of its own, so it falls back to a shared `Quizzes/` next to it).

## Rejecting a question

A rejection is logged, not just discarded — saying "this question is bad" is
meant to mean something beyond the current quiz:

```
python3 reject.py --reason REASON \
    --source-file "<vault path>" --stem "<the question>" [--note "..."]
```

`REASON` is exactly one of **four** kinds, kept distinct because the remedy
differs by kind and filing them together dilutes the signal:

| reason | kind | remedy |
| --- | --- | --- |
| `fabricated-quote` | integrity | no quote, or a quote not in the source — generate more carefully |
| `quote-unsupported` | integrity | quote is real but doesn't support the question — generate more carefully |
| `trivia` | quality | real and supported, but a lookup value, not understanding — generate a better question |
| `extraction-artifact` | extraction | quote is verbatim but the **source text itself** is corrupt — re-extract, screenshot, or mark the region off-limits, **not** "generate more carefully" |

`extraction-artifact` is the newest and easiest to get wrong: every automated
check *passes* on it, because the quote genuinely is in the file — a mangled
equation was read faithfully and believed. It is not fabrication and must never
be filed as one; conflating the two sends the wrong instruction. When in doubt
between `fabricated-quote` and `extraction-artifact`, ask whether the quote
really does appear verbatim in `source_file` — if yes, it's `extraction-artifact`
or `quote-unsupported`, never `fabricated-quote`.

Rejections append to `logs/rejections.jsonl`, beside this script in the tooling
repo (decided 23/07/2026, moved off the vault) — this log is feedback about
*generation quality*, a property of the skill, not of any particular vault
content, so it doesn't care which quiz or which machine produced an entry; it
syncs like every other change to the skill, by committing and pushing this
repo. Do **not** feed the raw log into generation.

## Distillation

Refresh `rejection-patterns.md` at the **start of every generation session** —
this is now automatic, not a manual someday-pass:

```
python3 distill_rejections.py
```

This does the mechanical half: groups rejections by `(kind, reason, normalized
note)` and counts them — aggregation, not summary, so the same complaint
fifteen times is one line with a count of fifteen. Read its output and do the
judgment half: recognize when two differently-worded groups are the same
underlying pattern (extraction noise gets described differently each time),
merge them, and rewrite `rejection-patterns.md` with a named rule per pattern,
ranked by combined count. That file — never the raw log — is what generation
reads. **Nothing learns between sessions except through this file**: if it goes
stale, the whole feedback loop silently stops working while appearing to run.

## The feedback loop

The automated checks cannot catch the failure that matters most: a garbled
equation read faithfully, misunderstood, and turned into a confident wrong
question with a verbatim quote attached — every check passes. The only backstop
is noticing while taking the quiz, so response capture is not a nice-to-have
layered on later; it is the primary safeguard and belongs in the first working
version.

The HTML quiz builder (see the sibling `quiz-builder/` tooling) captures, per
question, one of three responses — **accept**, **slight notice**, **reject** —
plus a free-text note, recorded when I advance to the next question rather than
at the end. Three levels because most feedback is neither "fine" nor "broken":
it's "the equation lost a subscript but the question still works," worth
recording without discarding the question.

A `reject` response requires one of the four reasons above and is written to
`logs/rejections.jsonl` — the same file `reject.py` writes, same schema, so
`distill_rejections.py` sees both without extra plumbing. `accept` and `notice`
responses are not integrity/quality/extraction judgments on their own, so they
are not forced into the four-reason taxonomy; they still get captured (see the
builder's export format) in `logs/responses.jsonl` as the fuller raw session
trail, kept as evidence rather than fed to generation.

## Files

- `build_quiz.py` — draft → `*.quiz.md` (human-readable) + `*.quiz-bank.json`
  (durable, assemblable question bank), defaulting into the source's own
  `Quizzes/` subfolder; balanced key, quote verification, length backstop
- `reject.py` — append a validated rejection (one of four reasons) to `logs/rejections.jsonl`
- `distill_rejections.py` — mechanical aggregation pass over the rejection log;
  run at the start of every generation session, before reading `rejection-patterns.md`
- `vaultutil.py` — shared helpers (vault-root discovery, whitespace normalization)
- `rejection-patterns.md` — distilled failure modes, three sections (integrity /
  quality / extraction); read this before generating, after refreshing it
- `logs/rejections.jsonl` — raw append-only evidence log, versioned with the skill (not the vault); never read wholesale, only via `distill_rejections.py`
- `logs/responses.jsonl` — the fuller per-question feedback trail from the HTML builder (accept/notice/reject + notes), kept as evidence, never fed to generation
- `quiz-builder/index.html` — static, no-server HTML tool: loads one or more `*.quiz-bank.json` files, captures per-question feedback, exports the two log blocks above to copy-paste
