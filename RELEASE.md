# Release gates — English edition (2026-07-19)

This release translated the course from Traditional Chinese to English and shipped essay 01.
Every gate below was run before push. Evidence is quoted from actual runs; nothing here is
"confirmed" without output. The original Chinese textbook is preserved unchanged in `zh-tw/`.

## Gate 1 — Translation completeness

Check: zero CJK characters outside `zh-tw/`.

```
grep -rlP '[\x{4e00}-\x{9fff}]' . --exclude-dir=zh-tw --exclude-dir=.git --exclude-dir=__pycache__
→ (empty)
```

## Gate 2 — Behavioral regression

Check: every lesson, exercise autograder, quiz, and the capstone grader pass against reference solutions.

```
python3 progress.py --solutions   → Progress [ooooooooooo] 11/11, All passed!
python3 quiz/quiz.py --check      → 32 questions, format OK
capstone grader                   → 17/17
```

Translation-driven string couplings (assertions that test output text) were changed together
with their graders and are listed in `audit/translation_audit.md`. One deliberate parameter
change shipped with the translation: the lesson 4 / exercise 4 reply-length limit moved from
40 to 60 characters because idiomatic English replies are longer; lesson, textbook, exercise,
and grader were unified at 60 (initially they were not; gate 3 caught the split).

## Gate 3 — Two-stage validity audit

Stage 1: internal mechanical audit (`audit/translation_audit.md`).
Stage 2: independent cold review by a fresh-context reviewer with no access to stage-1 output.
Merged verdicts and the seven confirmed fixes (stale lesson counts, a prose/code spec mismatch,
an unattributed quote, the 40/60 split above, and more): `audit/corrections-20260719.md`,
fixed in commit `8194fd8`.

The same two-stage audit ran on essay 01 before publishing; those receipts, including the
finding that caught a personal email about to enter this repo's history, are in
`audit/essay-01/` (working language: Chinese; summary in the essay itself).

## Gate 4 — De-identification and secrets

Checks: secret-pattern grep (keys, tokens) over all tracked files; personal-path and email
grep; commit author scan on every unpushed commit.

```
secret patterns  → 0 real hits (template placeholders only)
personal paths   → 0
git log --format='%ae' origin/main..HEAD | sort -u
→ klmtseng@users.noreply.github.com
```

The author scan exists because the audit caught 12 commits authored with a personal email via
a local git config override. All were rewritten before push. That miss is now a permanent
entry in the audit framework's challenge ledger.

## Gate 5 — Citation and link check

- Goodhart's law attribution in ch07 (the pithy wording is Strathern 1997, not Goodhart 1975):
  verified against external sources before publish.
- All README external references and essay links: resolve with HTTP 200.

---

Process note: gates are frozen once run. A failed gate is never redefined by the builder that
failed it; that rule (and the incident behind it) is what lesson 7 and essay 01 are about.
