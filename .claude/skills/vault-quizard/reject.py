#!/usr/bin/env python3
"""Record a rejected quiz question.

Governed by the "Rejecting questions" section of `a - logistics/Quiz
Standards.md`. Saying "this question is bad" is meant to mean something beyond
the current quiz, so a rejection is *logged*, not just discarded, and it carries
one of exactly four reasons. They are not the same kind of problem, and keeping
them distinct is the whole point -- filing a trivia complaint next to a
fabricated quote dilutes the one signal that matters, and conflating the fourth
reason with the first two sends the wrong remedy in both directions:

  fabricated-quote   No quote at all, or a quote that does not appear in the
                     source file. This is fabrication -- an INTEGRITY failure.
                     Remedy: generate more carefully.

  quote-unsupported  The quote is real but does not support the question.
                     Subtler and in some ways worse, because every automated
                     check passes while the question is still unfounded. Also an
                     integrity failure; only a human can catch it. Remedy:
                     generate more carefully.

  trivia             The quote is real and supports the question, but the
                     question asks for a number you would look up rather than
                     something you should understand. A QUALITY judgement, not an
                     integrity one -- deliberately kept out of the first two's
                     pile. Remedy: generate a better question.

  extraction-artifact  The quote is faithful -- genuinely, verbatim in the
                     source -- and the SOURCE TEXT ITSELF is corrupt: a mangled
                     equation, a dropped sign, garbage from a bad extraction.
                     The question states wrong physics but nothing in it was
                     invented; it read broken material and believed it. Every
                     automated check passes for exactly this reason, which is
                     why only a human catches it. This is NOT fabrication and
                     must never be filed as one -- the remedy is different in
                     kind: re-extraction, a screenshot, or marking the region
                     off-limits, not "try generating again." Added once the
                     first real PDF extraction landed and made this failure
                     mode unavoidable (poppler's non-injective fallback byte
                     means a mismatch increasingly often means "check the
                     extraction" rather than "the model lied" -- see
                     a - logistics/Source Note Types.md).

The log is append-only JSONL and grows without bound; that is fine, it is
evidence to go back to. What must NOT happen is the whole log being fed back into
generation. The skill carries forward a short distilled list of recurring
failure modes (`rejection-patterns.md`) instead, refreshed from the log via
`distill_rejections.py` plus a model judgment pass -- see that script and
`a - logistics/Quiz Standards.md` -> "The feedback loop" for why distillation is
aggregation (count how often the same complaint recurs) rather than a summary,
and why it is now the skill's job at generation time rather than a manual
someday-chore.

The log lives in this tooling repo (`logs/rejections.jsonl`, beside this
script), not in the vault (decided 23/07/2026, moved from the earlier
`<vault>/.quiz/rejections.jsonl`). The log is feedback about *generation
quality* -- a property of the skill, not of any particular vault content -- so
it does not care which quiz or which machine produced an entry, and it syncs
by committing and pushing this repo the same way every other change to the
skill does.

Usage
-----

    python3 reject.py --reason trivia \\
        --source-file "Information Theory/Derivations/Kraft's inequality.md" \\
        --stem "What is the depth of the tree in the proof?" \\
        [--note "asks for a value, not the argument"] \\
        [--log PATH]

`--log` overrides the default location (`logs/rejections.jsonl` beside this
script) entirely.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from typing import Optional

REASONS = {
    "fabricated-quote": "integrity",
    "quote-unsupported": "integrity",
    "trivia": "quality",
    "extraction-artifact": "extraction",
}

# The shared rejection log, versioned with the skill in the tooling repo.
DEFAULT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "rejections.jsonl")


def make_entry(
    reason: str,
    source_file: str,
    stem: str,
    note: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> dict:
    if reason not in REASONS:
        raise ValueError(
            f"unknown reason {reason!r}; must be one of {', '.join(sorted(REASONS))}"
        )
    return {
        "timestamp": timestamp or _dt.datetime.now().isoformat(timespec="seconds"),
        "reason": reason,
        "kind": REASONS[reason],  # integrity | quality -- lets distillation triage
        "source_file": source_file,
        "stem": stem,
        "note": note or "",
    }


def append_entry(entry: dict, log_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def resolve_log_path(explicit_log: Optional[str]) -> str:
    """An explicit --log wins; otherwise the shared log beside this script."""
    return explicit_log or DEFAULT_LOG


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reason", required=True, choices=sorted(REASONS),
                        help="one of the four rejection kinds")
    parser.add_argument("--source-file", required=True,
                        help="vault path of the source the question came from")
    parser.add_argument("--stem", required=True, help="the question stem being rejected")
    parser.add_argument("--note", default=None, help="optional free-text detail")
    parser.add_argument("--log", default=None,
                        help="override the log path (default: logs/rejections.jsonl beside this script)")
    args = parser.parse_args(argv)

    log_path = resolve_log_path(args.log)

    try:
        entry = make_entry(args.reason, args.source_file, args.stem, args.note)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    append_entry(entry, log_path)
    print(f"logged {args.reason} ({entry['kind']}) -> {log_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
