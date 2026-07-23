# Rejection patterns

**This is the file the skill reads before generating questions — not the raw log.**
It is the short standing list of recurring failure modes distilled from
`logs/rejections.jsonl` (beside `reject.py` in this repo), the same move as the
AI-notes review checklist on the dashboard: a set of failure modes, not a list
of every bad question. The raw log is evidence to go back to; it never enters a
generation prompt.

Refresh this file at the **start of every generation session**, not periodically
by hand — per `a - logistics/Quiz Standards.md` -> "The feedback loop," nothing
learns between sessions, and this file is the only thing carrying failure modes
forward, so a stale copy means the loop silently stops working while appearing
to run. The refresh has two steps, mechanical then judgment:

1. Run `python3 distill_rejections.py` — mechanical grouping and counting by
   `(kind, reason, normalized note)`. This is aggregation, not summary: the same
   complaint fifteen times becomes one line with a count of fifteen, and the
   count is what ranks what to fix first.
2. Read the grouped output. The script only catches exact-text repeats; a real
   pattern usually shows up worded differently each time ("the equation lost a
   subscript" vs. "a sign is missing" are the same underlying complaint), and
   recognizing that takes reading, not string matching — that's the model
   judgment step. Merge what's really the same pattern, write it below as one
   concrete rule with its combined count, and drop anything that stopped
   recurring.

Three sections below, matching the standard's three *kinds* (not its four
*reasons* — the two integrity reasons share a section, since both call for the
same remedy: generate more carefully).

## Integrity failures to avoid

*(`fabricated-quote` and `quote-unsupported` rejections distill here — both mean
"generate more carefully," which is why they share a section despite being two
reasons.)*

- _None yet — the log is empty. Add patterns as they recur._

## Quality failures to avoid

*(`trivia` rejections distill here.)*

- _None yet — the log is empty. Add patterns as they recur._

## Extraction artifacts to watch for

*(`extraction-artifact` rejections distill here. Kept separate from Integrity on
purpose — nothing here means "generate more carefully"; it means "this passage
of the source is not quotable," and the remedy is re-extraction, a screenshot,
or marking the region off-limits. Filing these as integrity failures would send
the wrong instruction. Given poppler's non-injective fallback byte, a recurring
pattern here is likely to look like "this equation/symbol keeps landing wrong,"
which is a signal about a specific source file or page range, not about how a
question was written.)*

- _None yet — the log is empty. Add patterns as they recur._
