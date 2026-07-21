#!/usr/bin/env python3
"""Build a takeable quiz from a markdown draft.

Governed by `a - logistics/Quiz Standards.md` in the vault (the "Item quality"
section). This script does the two mechanical jobs that section assigns to the
build step, and nothing else:

  1. Position clustering. It does NOT randomize option order. It permutes each
     question's options onto a *balanced* answer key, so the correct answers
     land as close to equally across A/B/C/D as the arithmetic allows over the
     whole quiz. Randomization clumps often enough that a run of three B's
     teaches you to guess B; a balanced key cannot be gamed that way because no
     position is over-represented.

  2. Longest-answer bias. The real fix for that tell is a *generation* rule
     (every distractor a specific claim a half-understanding reader would
     believe), enforced when the questions are written, not here. This script
     only runs the cheap backstop the standard describes: flag any question
     whose correct option is much longer than the mean of the other options, so
     you can go rewrite the distractors. A flag is a warning, never a build
     failure -- consistent with the standard's rule that a check you disable is
     worth nothing.

Sources are markdown notes (the read -> exercises -> quiz workflow), so both the
input draft and the output quiz are markdown. It also runs the standard's core
check: a literal substring match of each `source_quote` against the contents of
its `source_file`, raising a per-question warning on a miss (never a build
failure -- the question still ships, flagged, carrying its location so it can be
adjudicated by hand at quiz time). The match is literal up to whitespace, so a
quote that wraps across a line in the source still matches. The PDF
`.extract.txt` path in the standard -- with its fuzzy near-miss vs total-miss
handling -- stays deferred until `vault-source-ingest` freezes an extraction
artifact to run it against; there is nothing to exercise that machinery on yet.

Draft format (`*.quiz-draft.md`)
--------------------------------

    ---
    source_file: Information Theory/Derivations/Kraft's inequality.md
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

    ## Q2 ...

`- [x]` marks the correct option; `- [ ]` marks a distractor (Obsidian's
checkbox syntax, so a draft still renders sanely in the vault). Everything after
the number on the `##` line is an optional human title. `quote:` and `location:`
are per the standard's traceability requirement; a missing one warns rather than
fails, so the build always runs.

Three question kinds, inferred from the options (no marker needed, though a
`*(True/False)*` / `*(select one or more)*` marker in the stem is tolerated and
stripped):

  - single-correct MC: one `[x]`, two or more options -- options are permuted
    onto the balanced key and the length backstop applies.
  - True/False: exactly two options, literally `True` and `False`, one `[x]`.
    Truth is fixed by the statement, so the options are never permuted or
    balanced and the length backstop is skipped; they render without letters.
  - multi-select: two or more `[x]` plus at least one distractor. Options are
    permuted (not balanced -- there is no single correct position) and the key
    lists every correct letter.

Usage
-----

    python3 build_quiz.py DRAFT.quiz-draft.md [-o OUT.quiz.md] [--vault-root DIR]
                          [--seed N] [--length-factor 1.5] [--length-min-gap 12]

The vault root (for resolving `source_file` during quote verification) is found
from `--vault-root`, else `$NOTES_PHD_VAULT`, else the `.obsidian` marker above
the draft. If none is found, quote verification is skipped with a note.

Exit status is 0 whenever a quiz was produced, even with length flags: flags are
review notes, not errors. A non-zero exit means the draft could not be parsed
into a quiz at all (e.g. a question with no correct option).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import random
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vaultutil import normalize_ws, resolve_vault_root  # noqa: E402

# Position labels. Five is already more options than any sane multiple-choice
# item; the balanced key generalises to any arity, this just names them.
LABELS = ["A", "B", "C", "D", "E", "F"]

# Question kinds. `mc` is single-correct multiple choice; `tf` is a True/False
# item (options are literally True and False); `multi` is select-one-or-more.
KIND_MC = "mc"
KIND_TF = "tf"
KIND_MULTI = "multi"

_OPTION_RE = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s?(.*)$")
_HEADING_RE = re.compile(r"^##\s+(.*)$")
_META_RE = re.compile(r"^(quote|location)\s*:\s*(.*)$", re.IGNORECASE)
# Cosmetic markers carried over from the ITFNS bank; stripped from the stem since
# the kind is inferred from the options, not the marker.
_TF_MARKER_RE = re.compile(r"\s*\*?\(?\s*true\s*/\s*false\s*\)?\*?", re.I)
_MULTI_MARKER_RE = re.compile(r"\s*\*?\(?\s*select (?:one or more|all that apply)\s*\)?\*?", re.I)


@dataclass
class Question:
    title: str
    stem: str
    correct: list[str]  # one entry for mc/tf, two or more for multi-select
    distractors: list[str]
    kind: str = KIND_MC
    quote: Optional[str] = None
    location: Optional[str] = None
    # Filled in by build(): the fully ordered option list, and the 0-based
    # positions of the correct option(s) within it.
    correct_indices: list[int] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    @property
    def n_options(self) -> int:
        return len(self.correct) + len(self.distractors)


@dataclass
class Draft:
    source_file: Optional[str]
    questions: list[Question]


@dataclass
class Warning:
    qnum: int
    kind: str  # "length" | "quote" | "traceability"
    message: str

    def __str__(self) -> str:
        return f"Q{self.qnum}: {self.message}"


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split a leading `--- ... ---` block off the top of the draft.

    Minimal on purpose: values here are plain strings (a vault path), so pulling
    in a YAML dependency would be more machinery than the job needs.
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    # lines[0] is the opening '---'; find the closing one.
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            meta: dict[str, str] = {}
            for raw in lines[1:i]:
                if ":" in raw:
                    key, val = raw.split(":", 1)
                    meta[key.strip()] = val.strip()
            return meta, "\n".join(lines[i + 1:])
    return {}, text


def parse_draft(text: str) -> Draft:
    meta, body = _parse_frontmatter(text)
    source_file = meta.get("source_file")

    questions: list[Question] = []
    # Each question runs from one `## ` heading to the next.
    blocks: list[list[str]] = []
    current: Optional[list[str]] = None
    for line in body.splitlines():
        if _HEADING_RE.match(line):
            if current is not None:
                blocks.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        blocks.append(current)

    for block in blocks:
        questions.append(_parse_block(block))
    return Draft(source_file=source_file, questions=questions)


def _strip_qnumber(title_line: str) -> str:
    # "Q1: foo" / "Q1 foo" / "1. foo" -> "foo"; a bare "Q1" -> "".
    return re.sub(r"^Q?\d+[\.:)]?\s*", "", title_line).strip()


def _strip_markers(text: str) -> str:
    text = _TF_MARKER_RE.sub("", text)
    text = _MULTI_MARKER_RE.sub("", text)
    return text.strip()


def _parse_block(block: list[str]) -> Question:
    heading = _HEADING_RE.match(block[0]).group(1).strip()
    title = _strip_markers(_strip_qnumber(heading))

    stem_lines: list[str] = []
    correct: list[str] = []
    distractors: list[str] = []
    quote: Optional[str] = None
    location: Optional[str] = None
    seen_option = False

    for line in block[1:]:
        opt = _OPTION_RE.match(line)
        if opt:
            seen_option = True
            marker, body_text = opt.group(1), opt.group(2).strip()
            if marker in ("x", "X"):
                correct.append(body_text)
            else:
                distractors.append(body_text)
            continue

        m = _META_RE.match(line.strip())
        if m:
            key, val = m.group(1).lower(), m.group(2).strip().strip('"“”')
            if key == "quote":
                quote = val or None
            else:
                location = val or None
            continue

        # Prose before the first option is the stem; blank lines and stray text
        # after options are ignored.
        if not seen_option:
            stem_lines.append(line)

    stem = _strip_markers("\n".join(stem_lines).strip())

    if not correct:
        raise ValueError(f"Question {heading!r} has no [x] correct option.")

    all_options = correct + distractors
    is_true_false = (
        len(all_options) == 2
        and {opt.strip().lower() for opt in all_options} == {"true", "false"}
    )

    if is_true_false:
        if len(correct) != 1:
            raise ValueError(f"Question {heading!r} is True/False but marks both correct.")
        kind = KIND_TF
    elif len(correct) >= 2:
        if not distractors:
            raise ValueError(
                f"Question {heading!r} is multi-select but has no wrong option."
            )
        kind = KIND_MULTI
    else:
        if not distractors:
            raise ValueError(f"Question {heading!r} has no distractors.")
        kind = KIND_MC

    return Question(
        title=title,
        stem=stem,
        correct=correct,
        distractors=distractors,
        kind=kind,
        quote=quote,
        location=location,
    )


# --------------------------------------------------------------------------- #
# Balanced answer key
# --------------------------------------------------------------------------- #

def balanced_positions(count: int, arity: int, rng: random.Random) -> list[int]:
    """Return `count` correct-answer positions in [0, arity), balanced by count.

    Each position appears floor(count/arity) or ceil(count/arity) times -- the
    most even split possible -- and the *order* is then shuffled so the sequence
    itself carries no A,B,C,D,... pattern. Balanced counts are what stop the
    "always guess B" tell; the shuffle just keeps the key from being predictable
    question to question.
    """
    base = [i % arity for i in range(count)]
    rng.shuffle(base)
    return base


def build(
    draft: Draft,
    seed: Optional[int] = None,
    length_factor: float = 1.5,
    length_min_gap: int = 12,
    vault_root: Optional[str] = None,
) -> list[Warning]:
    """Place every question's options onto a balanced key and collect warnings.

    Questions are grouped by option count so a 3-option item and a 4-option item
    are each balanced within their own group (mixing arities would bias the key).
    The questions are mutated in place with `correct_index` and `options` set.

    Warnings come in three kinds: `length` (longest-answer backstop), `quote`
    (the source_quote check -- only run when `vault_root` is given, since it must
    read the source file), and `traceability` (missing location). None of them
    fail the build.
    """
    rng = random.Random(seed)

    # Single-correct MC: group by arity and balance the correct position within
    # each group. Handled first and exactly as before, so a quiz with no tf/multi
    # items consumes the RNG identically to the single-kind builder.
    mc_by_arity: dict[int, list[int]] = {}
    for idx, q in enumerate(draft.questions):
        if q.kind == KIND_MC:
            mc_by_arity.setdefault(q.n_options, []).append(idx)

    for arity, idxs in mc_by_arity.items():
        positions = balanced_positions(len(idxs), arity, rng)
        for idx, pos in zip(idxs, positions):
            q = draft.questions[idx]
            distractors = list(q.distractors)
            rng.shuffle(distractors)
            options = list(distractors)
            options.insert(pos, q.correct[0])
            q.correct_indices = [pos]
            q.options = options

    for q in draft.questions:
        if q.kind == KIND_TF:
            # Truth is fixed by the statement, so there is nothing to permute or
            # balance: render True then False and record which is correct.
            q.options = ["True", "False"]
            q.correct_indices = [0 if q.correct[0].strip().lower() == "true" else 1]
        elif q.kind == KIND_MULTI:
            # No single correct position to balance; just permute all options so
            # the correct set is not always in the same slots.
            options = list(q.correct) + list(q.distractors)
            rng.shuffle(options)
            q.options = options
            q.correct_indices = sorted(options.index(c) for c in q.correct)

    warnings: list[Warning] = []
    for i, q in enumerate(draft.questions, start=1):
        # The longest-answer backstop only makes sense for a single correct
        # option compared against distractors -- skip tf (no distractors) and
        # multi (no single correct), matching the old builder.
        if q.kind == KIND_MC:
            flag = _length_flag(q, length_factor, length_min_gap)
            if flag is not None:
                warnings.append(Warning(i, "length", flag))

        if vault_root is not None:
            quote_miss = _verify_quote(q, vault_root, draft.source_file)
            if quote_miss is not None:
                warnings.append(Warning(i, "quote", quote_miss))

        if not q.location:
            warnings.append(Warning(i, "traceability", "no location — cannot trace back to the page."))
    return warnings


def _verify_quote(
    q: Question, vault_root: str, source_file: Optional[str]
) -> Optional[str]:
    """The standard's core check: does source_quote appear in source_file?

    Literal substring match, tolerant only of whitespace (line wrapping). A miss
    is returned as a warning message, never raised -- the question still ships,
    flagged, so it can be adjudicated by hand against the source at quiz time. A
    question that cannot be verified (no quote, unreadable source) is flagged
    too, rather than given the benefit of the doubt.
    """
    if not q.quote:
        return "no source_quote — the question cannot be verified against the source."
    if not source_file:
        return "no source_file — cannot locate the source to verify the quote."
    path = os.path.join(vault_root, source_file)
    try:
        with open(path, encoding="utf-8") as fh:
            contents = fh.read()
    except OSError:
        return f'could not read source_file "{source_file}" to verify the quote.'
    if normalize_ws(q.quote) in normalize_ws(contents):
        return None
    return (
        f'source_quote not found in "{source_file}" — treat as possible '
        f"fabrication and verify by hand before trusting this question."
    )


def _length_flag(
    q: Question, factor: float, min_gap: int
) -> Optional[str]:
    """Backstop for longest-answer bias.

    Flags when the correct option is both `factor`x longer than the mean of the
    distractors AND longer by at least `min_gap` characters. The absolute gap
    keeps short options (where a 1.5x ratio is a handful of characters and means
    nothing) from tripping the flag.
    """
    correct_len = len(q.correct[0].strip())
    others = [len(d.strip()) for d in q.distractors]
    mean_others = sum(others) / len(others)
    if mean_others <= 0:
        return None
    if correct_len >= factor * mean_others and (correct_len - mean_others) >= min_gap:
        ratio = correct_len / mean_others
        return (
            f"correct option is {ratio:.1f}x the mean distractor length "
            f"({correct_len} vs {mean_others:.0f} chars) -- rewrite the "
            f"distractors as fuller, specific claims rather than padding this one."
        )
    return None


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def _answer_label(q: Question) -> str:
    """The answer-key label(s): True/False text, one letter, or 'A and C'."""
    if q.kind == KIND_TF:
        return q.options[q.correct_indices[0]]
    labels = [LABELS[i] for i in q.correct_indices]
    return " and ".join(labels)


def render_markdown(draft: Draft, warnings: list["Warning"]) -> str:
    today = _dt.date.today().isoformat()
    out: list[str] = []

    out.append("---")
    if draft.source_file:
        out.append(f"source_file: {draft.source_file}")
    out.append(f"generated: {today}")
    out.append("---")
    out.append("")

    heading_src = draft.source_file or "source"
    out.append(f"# Quiz — {heading_src}")
    out.append("")

    for i, q in enumerate(draft.questions, start=1):
        title = f" {q.title}" if q.title else ""
        out.append(f"## Q{i}{title}")
        if q.stem:
            out.append(q.stem)
        if q.kind == KIND_MULTI:
            out.append("*(select all that apply)*")
        out.append("")
        if q.kind == KIND_TF:
            # No letter labels: the two options are their own labels.
            for opt in q.options:
                out.append(f"- {opt}")
        else:
            for label, opt in zip(LABELS, q.options):
                out.append(f"- {label}. {opt}")
        out.append("")

    # Answer key: collapsed callout so it is present for grading but hidden while
    # taking the quiz. Each line carries the source pointer so a flagged answer
    # can be adjudicated against the note without leaving the file.
    out.append("---")
    out.append("> [!answer]- Answer key")
    for i, q in enumerate(draft.questions, start=1):
        label = _answer_label(q)
        pointer_bits = []
        if q.location:
            pointer_bits.append(q.location)
        if q.quote:
            pointer_bits.append(f'"{q.quote}"')
        pointer = f" — {' · '.join(pointer_bits)}" if pointer_bits else ""
        out.append(f"> {i}. **{label}**{pointer}")
    out.append("")

    quote_w = [w for w in warnings if w.kind == "quote"]
    length_w = [w for w in warnings if w.kind == "length"]
    trace_w = [w for w in warnings if w.kind == "traceability"]

    def _loc(qnum: int) -> str:
        loc = draft.questions[qnum - 1].location
        return f" (location: {loc})" if loc else ""

    # Quote misses are the integrity signal, so this callout is expanded (no `-`)
    # and uses [!danger] to stay conspicuous, per the standard.
    if quote_w:
        out.append(f"> [!danger] Quote-match review ({len(quote_w)})")
        out.append(
            "> The source_quote could not be verified against the source file. "
            "Adjudicate against the page before trusting the question; if the "
            "quote is invented, reject it as `fabricated-quote`."
        )
        for w in quote_w:
            out.append(f"> - Q{w.qnum}: {w.message}{_loc(w.qnum)}")
        out.append("")

    if length_w:
        out.append(f"> [!warning]- Length-flag review ({len(length_w)})")
        out.append(
            "> Backstop only — the fix is better distractors, not a shorter "
            "correct option."
        )
        for w in length_w:
            out.append(f"> - Q{w.qnum}: {w.message}")
        out.append("")

    if trace_w:
        out.append(f"> [!missing]- Missing location ({len(trace_w)})")
        for w in trace_w:
            out.append(f"> - Q{w.qnum}: {w.message}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("draft", help="path to a *.quiz-draft.md file")
    parser.add_argument(
        "-o", "--out",
        help="output path (default: DRAFT with .quiz-draft.md -> .quiz.md)",
    )
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for a reproducible key")
    parser.add_argument("--length-factor", type=float, default=1.5,
                        help="flag when correct >= factor x mean distractor length")
    parser.add_argument("--length-min-gap", type=int, default=12,
                        help="also require this many extra characters before flagging")
    parser.add_argument("--vault-root", default=None,
                        help="vault root for resolving source_file (default: discover "
                             "the .obsidian marker above the draft, or $NOTES_PHD_VAULT)")
    args = parser.parse_args(argv)

    with open(args.draft, encoding="utf-8") as fh:
        text = fh.read()

    try:
        draft = parse_draft(text)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not draft.questions:
        print("error: no questions found in draft.", file=sys.stderr)
        return 1

    vault_root = resolve_vault_root(args.vault_root, os.path.dirname(os.path.abspath(args.draft)))
    if vault_root is None:
        print("note: no vault root found (.obsidian / $NOTES_PHD_VAULT / --vault-root); "
              "skipping quote verification.", file=sys.stderr)

    warnings = build(draft, seed=args.seed,
                     length_factor=args.length_factor,
                     length_min_gap=args.length_min_gap,
                     vault_root=vault_root)
    rendered = render_markdown(draft, warnings)

    out_path = args.out
    if out_path is None:
        if args.draft.endswith(".quiz-draft.md"):
            out_path = args.draft[: -len(".quiz-draft.md")] + ".quiz.md"
        else:
            out_path = args.draft.rsplit(".", 1)[0] + ".quiz.md"

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(rendered)

    print(f"wrote {out_path} ({len(draft.questions)} questions)", file=sys.stderr)
    for w in warnings:
        print(f"  [{w.kind}] {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
