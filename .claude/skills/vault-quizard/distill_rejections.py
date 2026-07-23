#!/usr/bin/env python3
"""Aggregate the rejection log into counted groups for distillation.

Governed by `a - logistics/Quiz Standards.md` -> "The feedback loop". The
standard is explicit that distillation is **aggregation, not summary**: "the
same complaint fifteen times is one pattern with a count of fifteen, not
fifteen entries, and the count is the useful part because it ranks what to fix
first." It also says distillation is the skill's job, done automatically at
generation time, not a manual someday-chore -- and that the raw log itself must
never be fed back into generation, only the short distilled list is.

This script does the part of that job which is genuinely mechanical: read
`logs/rejections.jsonl` (beside this script, in the tooling repo -- see
`reject.py`), group entries, and count them. It deliberately
stops there. Recognizing that "the equation lost a subscript but the question
still works" and "a sign is missing in the source equation" are the SAME
underlying pattern, worded two different ways, needs reading comprehension --
that step is `compress-to-read` territory per the standard ("re-deriving the
pattern list is pure comprehension with nothing quoted"), which means it is
something the generating agent does by reading this script's grouped output,
not something a fixed grouping key can get right in general.

So the division of labor is:
  - this script: mechanical grouping and counting (exact-match on `reason` and
    on the normalized `note` text), which already catches literal repeats
    verbatim -- run it first, every time, since it costs nothing.
  - the generating agent, reading this script's output: recognize when two
    differently-worded groups are actually the same complaint, merge them, and
    rewrite `rejection-patterns.md` with a named pattern and a combined count,
    ranked highest-count first. This is the step per the standard that makes
    distillation "automatic" rather than depending on a periodic manual pass:
    run this script and do the read-and-rewrite step at the start of every
    generation session, not "someday."

Usage
-----

    python3 distill_rejections.py [--log PATH] [--min-count 1]

Prints, per `kind` (integrity / quality / extraction), each distinct
(reason, normalized note) group with its count and the verbatim notes it
covers -- the raw material for the read-and-rewrite step above. Exits 0 even
with an empty log (nothing to distill yet is not an error).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vaultutil import normalize_ws  # noqa: E402
from reject import DEFAULT_LOG  # noqa: E402

# Kinds in the order the standard introduces them: two integrity reasons, then
# quality, then the newest, extraction. Not alphabetical on purpose -- this is
# also the priority order when triaging where to spend attention first.
KIND_ORDER = ["integrity", "quality", "extraction"]


def load_entries(log_path: str) -> list[dict]:
    """Read every line of the JSONL log. Missing file -> empty list, not an error."""
    if not os.path.exists(log_path):
        return []
    entries = []
    with open(log_path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"warning: {log_path}:{lineno}: skipping malformed entry ({exc})",
                      file=sys.stderr)
    return entries


def _group_key(entry: dict) -> tuple[str, str]:
    """Exact-match grouping key: (reason, normalized note).

    Deliberately naive -- this is the mechanical baseline described in the
    module docstring, not a claim that it catches every real duplicate.
    """
    reason = entry.get("reason", "?")
    note = normalize_ws(entry.get("note", "")).lower()
    return (reason, note)


def aggregate(entries: list[dict]) -> dict[str, list[tuple[tuple[str, str], int, list[dict]]]]:
    """Group entries by kind, then by (reason, normalized note), counted.

    Returns {kind: [((reason, note), count, [entries]), ...]}, each kind's list
    sorted by count descending -- highest-count group first, since the count is
    what ranks what to fix first.
    """
    by_kind: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_kind[e.get("kind", "?")].append(e)

    result: dict[str, list[tuple[tuple[str, str], int, list[dict]]]] = {}
    for kind, kind_entries in by_kind.items():
        groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for e in kind_entries:
            groups[_group_key(e)].append(e)
        ranked = sorted(
            ((key, len(members), members) for key, members in groups.items()),
            key=lambda item: item[1], reverse=True,
        )
        result[kind] = ranked
    return result


def format_report(aggregated: dict[str, list[tuple[tuple[str, str], int, list[dict]]]],
                   min_count: int = 1) -> str:
    out: list[str] = []
    surviving = sum(
        1 for groups in aggregated.values() for _, count, _ in groups if count >= min_count
    )
    if surviving == 0:
        return "No rejection groups found (log empty or all below --min-count).\n"

    for kind in KIND_ORDER:
        groups = aggregated.get(kind, [])
        groups = [g for g in groups if g[1] >= min_count]
        if not groups:
            continue
        out.append(f"## {kind} ({sum(c for _, c, _ in groups)} entries in {len(groups)} group(s))")
        for (reason, note), count, members in groups:
            out.append(f"\n- **{reason}** x{count}" + (f' -- "{note}"' if note else " (no note)"))
            distinct_stems = {m.get("stem", "") for m in members}
            for stem in list(distinct_stems)[:3]:
                if stem:
                    out.append(f"    e.g. stem: {stem[:100]}")
        out.append("")
    # Any kind not in KIND_ORDER (future-proofing against a new kind appearing
    # in the log before this script's ordering is updated) still gets reported.
    for kind, groups in aggregated.items():
        if kind in KIND_ORDER:
            continue
        groups = [g for g in groups if g[1] >= min_count]
        if not groups:
            continue
        out.append(f"## {kind} (unrecognized kind -- update KIND_ORDER)")
        for (reason, note), count, _ in groups:
            out.append(f"- **{reason}** x{count}" + (f' -- "{note}"' if note else ""))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--log", default=None,
                        help="override the log path (default: logs/rejections.jsonl beside reject.py)")
    parser.add_argument("--min-count", type=int, default=1,
                        help="omit groups with fewer than this many entries")
    args = parser.parse_args(argv)

    log_path = args.log or DEFAULT_LOG
    entries = load_entries(log_path)
    aggregated = aggregate(entries)
    print(format_report(aggregated, args.min_count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
