#!/usr/bin/env python3
"""Record a rejected quiz question.

Governed by the "Rejecting questions" section of `a - logistics/Quiz
Standards.md`. Saying "this question is bad" is meant to mean something beyond
the current quiz, so a rejection is *logged*, not just discarded, and it carries
one of exactly three reasons. The three are not the same kind of problem, and
keeping them distinct is the whole point -- filing a trivia complaint next to a
fabricated quote dilutes the one signal that matters:

  fabricated-quote   No quote at all, or a quote that does not appear in the
                     source file. This is fabrication -- an INTEGRITY failure.

  quote-unsupported  The quote is real but does not support the question.
                     Subtler and in some ways worse, because every automated
                     check passes while the question is still unfounded. Also an
                     integrity failure; only a human can catch it.

  trivia             The quote is real and supports the question, but the
                     question asks for a number you would look up rather than
                     something you should understand. A QUALITY judgement, not an
                     integrity one -- deliberately kept out of the first two's
                     pile.

The log is append-only JSONL and grows without bound; that is fine, it is
evidence to go back to. What must NOT happen is the whole log being fed back into
generation. The skill carries forward a short distilled list of recurring
failure modes (`rejection-patterns.md`) instead, refreshed from the log
periodically. This script only appends to the log; distillation is a separate,
deliberately-not-yet-automated step (see the standard: "Ask me again after the
log has twenty entries").

The log lives inside the vault (`<vault>/.quiz/rejections.jsonl`), not beside the
skill, so it is one shared file that syncs across machines with the vault rather
than a separate log per machine.

Usage
-----

    python3 reject.py --reason trivia \\
        --source-file "Information Theory/Derivations/Kraft's inequality.md" \\
        --stem "What is the depth of the tree in the proof?" \\
        --vault-root "/path/to/Notes_phd" \\
        [--note "asks for a value, not the argument"] \\
        [--log PATH]

The vault root is found from `--vault-root`, else `$NOTES_PHD_VAULT`, else by
discovering the `.obsidian` marker above the current directory. `--log`
overrides the location entirely.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vaultutil import resolve_vault_root  # noqa: E402

REASONS = {
    "fabricated-quote": "integrity",
    "quote-unsupported": "integrity",
    "trivia": "quality",
}

# Path within the vault where the shared rejection log lives. A dotfolder so
# Obsidian ignores it; tracked by the vault's git, so it syncs across machines.
VAULT_LOG_RELPATH = os.path.join(".quiz", "rejections.jsonl")


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


def resolve_log_path(explicit_log: Optional[str], vault_root: Optional[str]) -> Optional[str]:
    """An explicit --log wins; otherwise the shared log inside the vault."""
    if explicit_log:
        return explicit_log
    if vault_root:
        return os.path.join(vault_root, VAULT_LOG_RELPATH)
    return None


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--reason", required=True, choices=sorted(REASONS),
                        help="one of the three rejection kinds")
    parser.add_argument("--source-file", required=True,
                        help="vault path of the source the question came from")
    parser.add_argument("--stem", required=True, help="the question stem being rejected")
    parser.add_argument("--note", default=None, help="optional free-text detail")
    parser.add_argument("--vault-root", default=None,
                        help="vault root (default: $NOTES_PHD_VAULT or .obsidian above CWD)")
    parser.add_argument("--log", default=None,
                        help="override the log path (default: <vault>/.quiz/rejections.jsonl)")
    args = parser.parse_args(argv)

    vault_root = resolve_vault_root(args.vault_root, os.getcwd())
    log_path = resolve_log_path(args.log, vault_root)
    if log_path is None:
        print("error: could not locate the vault to place the log. Pass --vault-root "
              "or --log, or set $NOTES_PHD_VAULT.", file=sys.stderr)
        return 1

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
