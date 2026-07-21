---
name: vault-quiz
description: "Generate a multiple-choice quiz from a markdown source note in the Notes_phd vault, following the item-quality and rejection rules in Quiz Standards.md. Sources are markdown notes only; PDF quote-matching is deferred until the extraction artifact exists."
---

# vault-quiz

Generates a self-quiz from a source note so I can test whether I actually
absorbed it. The governing document is `a - logistics/Quiz Standards.md` in the
vault — read it if anything here is ambiguous; this file implements two of its
sections and defers the rest.

**Scope right now.** The workflow is read → exercises → quiz, so sources are my
own markdown notes, not PDFs. Build against markdown only. Quote verification —
the core of the standard — **is** implemented for markdown: `build_quiz.py` does
a literal substring match (tolerant of line-wrapping whitespace) of each
`source_quote` against its `source_file`, and a miss raises a conspicuous
per-question warning rather than failing the build. The `.extract.txt` path in
the standard, with its fuzzy near-miss vs total-miss handling, stays deferred
until `vault-source-ingest` freezes an extraction artifact to run it against —
that machinery has nothing to exercise it yet.

## Generating questions

Read the source note. Write questions to a `*.quiz-draft.md` file (format below).
The two failure modes the standard names are prevented **here, in how the
questions are written** — the build script is only a backstop.

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

Before generating, **read `rejection-patterns.md`** (the distilled list, not the
raw log) and avoid the failure modes it records.

### Draft format (`*.quiz-draft.md`)

```
---
source_file: Information Theory/Derivations/Kraft's inequality.md
---

## Q1  (optional title)
Stem text, up to the first option line.

- [x] The correct option (exactly one per question).
- [ ] A believable misconception.
- [ ] Another believable misconception.
- [ ] A third.

quote: a verbatim span from source_file
location: p. 12, ch. 3
```

`- [x]` marks the correct option, `- [ ]` a distractor. Author them in natural
reading order; do not try to place the answer — that is the build's job.

The kind is inferred from the options — no marker needed:

- **True/False**: exactly two options, literally `True` and `False`, one `[x]`.
  A `*(True/False)*` marker in the stem is tolerated and stripped. Truth is fixed
  by the statement, so the build never permutes or balances these — write a mix
  of true and false statements yourself.
- **Multi-select**: two or more `[x]` plus at least one distractor. A
  `*(select one or more)*` marker is tolerated and stripped; the quiz renders a
  "select all that apply" hint.

## Building the quiz

```
python3 build_quiz.py path/to/note.quiz-draft.md
```

Because the draft lives in the vault, the vault root is found automatically from
the `.obsidian` marker above it (override with `--vault-root`, or set
`$NOTES_PHD_VAULT`). The build does three things:

- **Balanced answer key, not randomization.** Single-correct MC options are
  permuted onto a balanced key so correct answers land as close to equally across
  A/B/C/D as the arithmetic allows over the whole quiz — killing position
  clustering without the "run of three B's" that pure randomization produces.
  (True/False can't be balanced since truth is fixed; multi-select is permuted
  but has no single position to balance.)
- **Quote verification.** Each `source_quote` is literal-substring matched
  (tolerant of line wrapping) against its `source_file`. A miss — including a
  missing quote or an unreadable source — raises a conspicuous `[!danger]`
  callout carrying the question's `location`, so it can be adjudicated against
  the page at quiz time. It never fails the build; a quote you cannot verify is
  flagged, not trusted, and gets rejected as `fabricated-quote` if it turns out
  invented.
- **Longest-answer backstop.** For single-correct MC, it flags any question whose
  correct option is much longer than the mean of the others (skipped for
  True/False and multi-select, which have no single correct-vs-distractor
  compare). A flag is a warning, never a failure — the fix is better distractors,
  not a shorter answer.

Output is a takeable `*.quiz.md` with a collapsed answer key (carrying each
question's `location`/`quote` for adjudication) and the callouts above. Use
`--seed` for a reproducible key; `--length-factor` / `--length-min-gap` tune the
length flag.

## Rejecting a question

When a question is bad, record it — a rejection is meant to mean something beyond
the current quiz:

```
python3 reject.py --reason REASON \
    --source-file "<vault path>" --stem "<the question>" \
    --vault-root "<absolute vault path>" [--note "..."]
```

`REASON` is exactly one of three kinds, kept distinct on purpose:

| reason | kind | meaning |
| --- | --- | --- |
| `fabricated-quote` | integrity | no quote, or a quote not in the source file |
| `quote-unsupported` | integrity | quote is real but does not support the question |
| `trivia` | quality | real and supported, but asks for a lookup value, not understanding |

Rejections append to `<vault>/.quiz/rejections.jsonl` — inside the vault, not
beside the skill, so it is one shared log that syncs across machines with the
vault rather than a separate file per machine. Do **not** feed that log into
generation — it grows without bound. Instead the recurring patterns are distilled
into `rejection-patterns.md`, and *that* short list is what generation reads.
Distilling is a manual pass for now (the standard leaves its cadence open until
the log has ~20 entries).

## Files

- `build_quiz.py` — draft → takeable quiz (balanced key + quote check + length flag)
- `reject.py` — append a validated rejection to the vault log
- `vaultutil.py` — shared helpers (vault-root discovery, whitespace normalization)
- `rejection-patterns.md` — distilled failure modes; read this before generating
- `<vault>/.quiz/rejections.jsonl` — raw append-only evidence log (created on first rejection; never read wholesale)
