#!/usr/bin/env python3
"""Tests for build_quiz.py. Runs standalone: `python3 tests/test_build_quiz.py`.

The verbatim-match mechanics are exercised against markdown fixtures here
(cheap, deterministic); the ITFNS regression additionally proves the parser on
real course content. `source_file` in production points at a chapter's frozen
`.extract.txt` -- the check works identically against either, which is what
these markdown fixtures stand in for.
"""
import json
import os
import random
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import build_quiz as bq  # noqa: E402
import vaultutil  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "kraft.quiz-draft.md")
VAULT = os.path.join(os.path.dirname(__file__), "fixtures", "vault")
SAMPLE_DRAFT = os.path.join(VAULT, "Notes", "sample.quiz-draft.md")


def _load_fixture():
    with open(FIXTURE, encoding="utf-8") as fh:
        return bq.parse_draft(fh.read())


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return bq.parse_draft(fh.read())


def _kinds(warnings, kind):
    return [w for w in warnings if w.kind == kind]


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def test_parse_frontmatter_and_questions():
    draft = _load_fixture()
    assert draft.source_file == "Information Theory/Derivations/Kraft's inequality.md"
    assert len(draft.questions) == 4
    q1 = draft.questions[0]
    assert q1.title == "what the inequality bounds"
    assert q1.kind == "mc"
    assert q1.correct[0].startswith("The sum of $2^{-\\ell_i}$ over all codewords is at most 1")
    assert len(q1.distractors) == 3
    assert q1.location == "Derivations, Kraft's inequality"
    assert "2^{-\\ell_i}" in q1.quote
    assert q1.stem.startswith("For a binary prefix code")


def test_parse_multi_requires_a_wrong_option():
    # Two [x] is now a valid multi-select -- but only if there is a distractor.
    text = "## Q1\nstem\n\n- [x] a\n- [x] b\n"
    try:
        bq.parse_draft(text)
    except ValueError as exc:
        assert "no wrong option" in str(exc)
    else:
        raise AssertionError("expected ValueError for multi-select with no distractor")


def test_parse_true_false_detected_and_marker_stripped():
    text = "## Q1 a claim *(True/False)*\nSome statement.\n- [ ] True\n- [x] False\n"
    q = bq.parse_draft(text).questions[0]
    assert q.kind == "tf"
    assert q.title == "a claim"  # marker stripped
    assert q.correct == ["False"]


def test_parse_multi_select_detected():
    text = "## Q1 pick some\ns\n- [x] a\n- [x] b\n- [ ] c\n"
    q = bq.parse_draft(text).questions[0]
    assert q.kind == "multi"
    assert set(q.correct) == {"a", "b"}
    assert q.distractors == ["c"]


def test_build_true_false_fixed_order_and_key():
    text = "## Q1\ns\n- [ ] True\n- [x] False\n\nlocation: x\n"
    draft = bq.parse_draft(text)
    bq.build(draft, seed=0)
    q = draft.questions[0]
    assert q.options == ["True", "False"]  # never permuted
    assert q.correct_indices == [1]
    assert bq._answer_label(q) == "False"


def test_build_multi_select_preserves_correct_set():
    text = "## Q1\ns\n- [x] a\n- [x] b\n- [ ] c\n- [ ] d\n\nlocation: x\n"
    draft = bq.parse_draft(text)
    bq.build(draft, seed=3)
    q = draft.questions[0]
    assert len(q.options) == 4
    assert set(q.options) == {"a", "b", "c", "d"}
    # correct_indices point at exactly the correct options, whatever the shuffle.
    assert {q.options[i] for i in q.correct_indices} == {"a", "b"}


def test_render_true_false_has_no_letter_labels():
    text = "## Q1\ns\n- [x] True\n- [ ] False\n\nlocation: x\n"
    draft = bq.parse_draft(text)
    md = bq.render_markdown(draft, bq.build(draft, seed=0))
    assert "- True" in md and "- False" in md
    assert "- A." not in md
    assert "> 1. **True**" in md


def test_render_multi_select_hint_and_key():
    text = "## Q1\ns\n- [x] a\n- [x] b\n- [ ] c\n\nlocation: x\n"
    draft = bq.parse_draft(text)
    md = bq.render_markdown(draft, bq.build(draft, seed=0))
    assert "*(select all that apply)*" in md
    assert "> 1. **A and B**" in md or "> 1. **A and C**" in md or "> 1. **B and C**" in md


def test_length_flag_skips_tf_and_multi():
    # A long correct option must not flag when there is no single-correct compare.
    tf = bq.parse_draft("## Q1\ns\n- [x] True\n- [ ] False\n\nlocation: x\n")
    assert _kinds(bq.build(tf, seed=0), "length") == []
    multi = bq.parse_draft(
        "## Q1\ns\n- [x] a very long correct option piling on qualifying clauses here\n"
        "- [x] also correct and lengthy in the same way for good measure indeed\n"
        "- [ ] short\n\nlocation: x\n"
    )
    assert _kinds(bq.build(multi, seed=0), "length") == []


def test_parse_rejects_no_correct():
    text = "## Q1\nstem\n\n- [ ] a\n- [ ] b\n"
    try:
        bq.parse_draft(text)
    except ValueError as exc:
        assert "no [x] correct" in str(exc)
    else:
        raise AssertionError("expected ValueError for no correct option")


def test_parse_rejects_no_distractors():
    text = "## Q1\nstem\n\n- [x] a\n"
    try:
        bq.parse_draft(text)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for no distractors")


# --------------------------------------------------------------------------- #
# Balanced key
# --------------------------------------------------------------------------- #

def test_balanced_positions_counts_are_even():
    rng = random.Random(0)
    for count in range(1, 40):
        for arity in (2, 3, 4, 5):
            positions = bq.balanced_positions(count, arity, rng)
            assert len(positions) == count
            counts = Counter(positions)
            assert all(0 <= p < arity for p in positions)
            # Every used position differs from every other by at most 1.
            hi = max(counts[p] for p in range(arity))
            lo = min(counts[p] for p in range(arity))
            assert hi - lo <= 1, (count, arity, counts)


def test_balanced_positions_not_trivially_ordered():
    # A shuffled balanced key should (almost always) not be plain A,B,C,D,A,...
    rng = random.Random(1)
    positions = bq.balanced_positions(20, 4, rng)
    assert positions != [i % 4 for i in range(20)]


def test_build_key_is_balanced_over_whole_quiz():
    draft = _load_fixture()  # 4 questions, all 4 options
    bq.build(draft, seed=7)
    key = [q.correct_indices[0] for q in draft.questions]
    counts = Counter(key)
    # 4 questions / 4 positions -> exactly one each.
    assert sorted(counts.keys()) == [0, 1, 2, 3]
    assert all(v == 1 for v in counts.values())


def test_build_preserves_all_options():
    draft = _load_fixture()
    bq.build(draft, seed=3)
    for q in draft.questions:
        assert len(q.options) == q.n_options
        assert q.options[q.correct_indices[0]] == q.correct[0]
        assert set(q.options) == set(q.correct + q.distractors)


def test_build_is_deterministic_under_seed():
    d1 = _load_fixture()
    d2 = _load_fixture()
    bq.build(d1, seed=42)
    bq.build(d2, seed=42)
    assert [q.correct_indices for q in d1.questions] == [q.correct_indices for q in d2.questions]
    assert [q.options for q in d1.questions] == [q.options for q in d2.questions]


def test_build_balances_mixed_arities_within_group():
    # Two 4-option and two 3-option questions: each arity group balances on its own.
    text = (
        "## Q1\ns\n- [x] a\n- [ ] b\n- [ ] c\n- [ ] d\n"
        "## Q2\ns\n- [x] a\n- [ ] b\n- [ ] c\n- [ ] d\n"
        "## Q3\ns\n- [x] a\n- [ ] b\n- [ ] c\n"
        "## Q4\ns\n- [x] a\n- [ ] b\n- [ ] c\n"
    )
    draft = bq.parse_draft(text)
    bq.build(draft, seed=5)
    four = [draft.questions[i].correct_indices[0] for i in (0, 1)]
    three = [draft.questions[i].correct_indices[0] for i in (2, 3)]
    assert all(0 <= p < 4 for p in four)
    assert all(0 <= p < 3 for p in three)
    assert four[0] != four[1]      # balanced -> distinct
    assert three[0] != three[1]


# --------------------------------------------------------------------------- #
# Length flag
# --------------------------------------------------------------------------- #

def test_length_flag_triggers_on_long_correct():
    text = (
        "## Q1\nstem\n"
        "- [x] This is a deliberately long correct option that piles on qualifying clauses.\n"
        "- [ ] short one\n"
        "- [ ] short two\n"
        "- [ ] short three\n"
    )
    draft = bq.parse_draft(text)
    warnings = _kinds(bq.build(draft, seed=0), "length")
    assert len(warnings) == 1
    assert warnings[0].qnum == 1


def test_length_flag_quiet_on_even_options():
    # The realistic fixture (with locations, built without a vault) is fully
    # clean, and an even-length draft raises no length flag either.
    draft = _load_fixture()
    assert bq.build(draft, seed=0) == []
    text = (
        "## Q1\nstem\n"
        "- [x] alpha beta gamma delta\n"
        "- [ ] gamma delta alpha beta\n"
        "- [ ] delta alpha beta gamma\n"
        "- [ ] beta gamma delta alpha\n"
    )
    even = bq.parse_draft(text)
    assert _kinds(bq.build(even, seed=0), "length") == []


def test_length_flag_respects_min_gap():
    # 1.5x ratio but tiny absolute gap -> no flag.
    text = "## Q1\ns\n- [x] abcdef\n- [ ] abcd\n- [ ] abc\n"
    draft = bq.parse_draft(text)
    assert _kinds(bq.build(draft, seed=0, length_min_gap=12), "length") == []


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def test_render_has_labels_key_and_hides_correct_marker():
    draft = _load_fixture()
    warnings = bq.build(draft, seed=7)
    md = bq.render_markdown(draft, warnings)
    assert "# Quiz — Information Theory/Derivations/Kraft's inequality.md" in md
    assert "- A." in md and "- B." in md
    assert "[!answer]- Answer key" in md
    assert "[x]" not in md  # the correct marker must not leak into the takeable quiz
    # Answer key labels match the assigned positions.
    for i, q in enumerate(draft.questions, start=1):
        label = bq.LABELS[q.correct_indices[0]]
        assert f"> {i}. **{label}**" in md


def test_render_flags_missing_traceability():
    text = "## Q1\nstem\n- [x] a\n- [ ] b\n- [ ] c\n"  # no location
    draft = bq.parse_draft(text)
    warnings = bq.build(draft, seed=0)
    md = bq.render_markdown(draft, warnings)
    assert "Missing location" in md
    assert "Q1" in md


# --------------------------------------------------------------------------- #
# Quote verification (the standard's core check)
# --------------------------------------------------------------------------- #

def test_find_vault_root_from_draft():
    assert vaultutil.find_vault_root(SAMPLE_DRAFT) == os.path.abspath(VAULT)


def test_quote_match_flags_only_the_absent_quote():
    draft = _load(SAMPLE_DRAFT)
    quote_w = _kinds(bq.build(draft, seed=0, vault_root=VAULT), "quote")
    # Q1's quote wraps a line in the source, Q2's is verbatim -> both match.
    # Only Q3's quote does not appear in the file.
    assert [w.qnum for w in quote_w] == [3]
    assert "not found" in quote_w[0].message


def test_quote_match_tolerates_line_wrap():
    # Q1's quote spans a newline in sample.md; normalized match must accept it.
    draft = _load(SAMPLE_DRAFT)
    q1 = draft.questions[0]
    with open(os.path.join(VAULT, "Notes", "sample.md"), encoding="utf-8") as fh:
        contents = fh.read()
    assert q1.quote not in contents  # literal match would fail (has a newline)
    assert vaultutil.normalize_ws(q1.quote) in vaultutil.normalize_ws(contents)


def test_quote_check_skipped_without_vault():
    draft = _load(SAMPLE_DRAFT)
    assert _kinds(bq.build(draft, seed=0, vault_root=None), "quote") == []


def test_quote_flags_unreadable_source():
    text = (
        "---\nsource_file: Notes/does-not-exist.md\n---\n"
        "## Q1\ns\n- [x] a\n- [ ] b\n- [ ] c\n\nquote: whatever\nlocation: x\n"
    )
    draft = bq.parse_draft(text)
    quote_w = _kinds(bq.build(draft, seed=0, vault_root=VAULT), "quote")
    assert len(quote_w) == 1
    assert "could not read" in quote_w[0].message


def test_quote_flags_missing_quote_field():
    text = "---\nsource_file: Notes/sample.md\n---\n## Q1\ns\n- [x] a\n- [ ] b\n- [ ] c\nlocation: x\n"
    draft = bq.parse_draft(text)
    quote_w = _kinds(bq.build(draft, seed=0, vault_root=VAULT), "quote")
    assert len(quote_w) == 1
    assert "no source_quote" in quote_w[0].message


def test_render_quote_review_is_conspicuous():
    draft = _load(SAMPLE_DRAFT)
    warnings = bq.build(draft, seed=0, vault_root=VAULT)
    md = bq.render_markdown(draft, warnings)
    # Expanded danger callout (no collapse dash), and carries the location.
    assert "> [!danger] Quote-match review" in md
    assert "location: Notes/sample.md" in md


# --------------------------------------------------------------------------- #
# ITFNS regression: regenerate a real quiz and diff against a committed golden.
# Toy fixtures are too clean to catch anything; this one exercises the parser on
# real course content (unicode math, multi-line stems, length-matched options)
# and locks the balanced-key + render output so a refactor cannot silently drift.
# --------------------------------------------------------------------------- #

ITFNS_DRAFT = os.path.join(os.path.dirname(__file__), "fixtures", "itfns-regression.quiz-draft.md")
ITFNS_GOLDEN = os.path.join(os.path.dirname(__file__), "fixtures", "itfns-regression.quiz.golden.md")
ITFNS_SEED = 1729


def _strip_generated_date(md: str) -> str:
    # The `generated:` line is today's date; normalize it so the diff is stable.
    return re.sub(r"^generated: \d{4}-\d{2}-\d{2}$", "generated: <date>", md, flags=re.M)


def test_itfns_regression_matches_golden():
    draft = _load(ITFNS_DRAFT)
    warnings = bq.build(draft, seed=ITFNS_SEED, vault_root=None)
    actual = bq.render_markdown(draft, warnings)
    with open(ITFNS_GOLDEN, encoding="utf-8") as fh:
        golden = fh.read()
    if _strip_generated_date(actual) != _strip_generated_date(golden):
        raise AssertionError(
            "ITFNS regression output drifted from the golden. Review the change; "
            "if it is intended, regenerate with:\n"
            f"  python3 build_quiz.py {ITFNS_DRAFT} --seed {ITFNS_SEED} -o {ITFNS_GOLDEN}"
        )


def test_itfns_regression_parses_all_kinds():
    # Guards the parser on the real quiz's full mix: 10 single-correct MC, 4
    # True/False, 1 multi-select -- exactly the kinds the old parser handled.
    draft = _load(ITFNS_DRAFT)
    assert len(draft.questions) == 15
    kinds = Counter(q.kind for q in draft.questions)
    assert kinds == {"mc": 10, "tf": 4, "multi": 1}
    for q in draft.questions:
        assert q.correct and q.location


def test_itfns_regression_mc_key_is_balanced():
    draft = _load(ITFNS_DRAFT)
    bq.build(draft, seed=ITFNS_SEED, vault_root=None)
    # Only single-correct MC gets a balanced position key.
    counts = Counter(q.correct_indices[0] for q in draft.questions if q.kind == "mc")
    assert max(counts.values()) - min(counts.values()) <= 1


# --------------------------------------------------------------------------- #
# Question bank (the durable JSON artifact)
# --------------------------------------------------------------------------- #

def test_generate_bank_is_json_serializable_and_shaped():
    draft = _load_fixture()
    warnings = bq.build(draft, seed=1)
    bank = bq.generate_bank(draft, warnings, generated_date="2026-07-23")
    serialized = json.dumps(bank)  # must not raise
    reloaded = json.loads(serialized)
    assert reloaded["source_file"] == draft.source_file
    assert reloaded["generated"] == "2026-07-23"
    assert reloaded["question_count"] == len(draft.questions)
    assert len(reloaded["questions"]) == len(draft.questions)
    q0 = reloaded["questions"][0]
    for key in ("number", "title", "stem", "kind", "options", "correct_indices",
                "source_file", "location", "quote", "warnings"):
        assert key in q0


def test_generate_bank_options_and_correct_indices_match_built_draft():
    draft = _load_fixture()
    bq.build(draft, seed=2)
    bank = bq.generate_bank(draft, [])
    for i, q in enumerate(draft.questions):
        bq_json = bank["questions"][i]
        assert bq_json["options"] == q.options
        assert bq_json["correct_indices"] == q.correct_indices


def test_generate_bank_attaches_warnings_to_the_right_question():
    text = (
        "## Q1\ns\n- [x] a\n- [ ] b\n- [ ] c\n"  # no location -> traceability warning
        "## Q2\ns\n- [x] a\n- [ ] b\n- [ ] c\n\nlocation: x\n"  # clean
    )
    draft = bq.parse_draft(text)
    warnings = bq.build(draft, seed=0)
    bank = bq.generate_bank(draft, warnings)
    assert len(bank["questions"][0]["warnings"]) == 1
    assert bank["questions"][0]["warnings"][0]["kind"] == "traceability"
    assert bank["questions"][1]["warnings"] == []


def test_cli_writes_bank_json_alongside_quiz_md(tmp_path=None):
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        draft_path = os.path.join(d, "note.quiz-draft.md")
        with open(FIXTURE, encoding="utf-8") as fh:
            fixture_text = fh.read()
        with open(draft_path, "w", encoding="utf-8") as fh:
            fh.write(fixture_text)
        script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build_quiz.py")
        result = subprocess.run(
            [sys.executable, script, draft_path, "--seed", "0"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        bank_path = os.path.join(d, "note.quiz-bank.json")
        assert os.path.exists(bank_path)
        with open(bank_path, encoding="utf-8") as fh:
            bank = json.load(fh)
        assert bank["question_count"] == 4


# --------------------------------------------------------------------------- #
# Default output location: <book/course folder>/Quizzes/
# --------------------------------------------------------------------------- #

def test_default_quiz_dir_unwraps_extraction_container():
    src = "Statistical Mechanics/Sources/Pathria/Extraction/Chapter 1.extract.txt"
    assert bq.default_quiz_dir(src) == "Statistical Mechanics/Sources/Pathria/Quizzes"


def test_default_quiz_dir_unwraps_lecture_notes_container():
    src = "Phd courses/ITFNS/Lecture notes/Chapter 1 (ITFNS).md"
    assert bq.default_quiz_dir(src) == "Phd courses/ITFNS/Quizzes"


def test_default_quiz_dir_uses_immediate_parent_otherwise():
    src = "Statistical Mechanics/Sources/Some Paper.md"
    assert bq.default_quiz_dir(src) == "Statistical Mechanics/Sources/Quizzes"


def test_cli_defaults_output_into_book_quizzes_folder_when_vault_known():
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as vault:
        os.makedirs(os.path.join(vault, ".obsidian"))
        book_dir = os.path.join(vault, "Statistical Mechanics", "Sources", "Pathria")
        extraction_dir = os.path.join(book_dir, "Extraction")
        os.makedirs(extraction_dir)
        with open(os.path.join(extraction_dir, "Chapter 1.extract.txt"), "w", encoding="utf-8") as fh:
            fh.write("free energy is the part of the internal energy that is free to become work")

        draft_path = os.path.join(vault, "scratch.quiz-draft.md")
        with open(draft_path, "w", encoding="utf-8") as fh:
            fh.write(
                "---\nsource_file: Statistical Mechanics/Sources/Pathria/Extraction/Chapter 1.extract.txt\n---\n\n"
                "## Q1\ns\n- [x] free energy is the part of the internal energy that is free to become work\n"
                "- [ ] b\n- [ ] c\n\n"
                "quote: free energy is the part of the internal energy that is free to become work\nlocation: x\n"
            )
        script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build_quiz.py")
        result = subprocess.run(
            [sys.executable, script, draft_path, "--vault-root", vault, "--seed", "0"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        expected_dir = os.path.join(book_dir, "Quizzes")
        assert os.path.exists(os.path.join(expected_dir, "scratch.quiz.md"))
        assert os.path.exists(os.path.join(expected_dir, "scratch.quiz-bank.json"))


# --------------------------------------------------------------------------- #
# runner
# --------------------------------------------------------------------------- #

def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
