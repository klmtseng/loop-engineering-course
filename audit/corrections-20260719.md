# Pre-publish audit: merged verdicts and corrections (2026-07-19)

Two-stage audit of the English translation release candidate. Stage 1: internal mechanical
audit (`translation_audit.md`). Stage 2: independent cold review, fresh context, no access
to stage-1 output or the miss ledger. Verdicts merged and executed by the main session.

## Confirmed and fixed (commit 8194fd8)

| Finding | Caught by | Fix |
|---|---|---|
| lesson4 + ch04 kept the 40-char limit while exercise4 moved to 60 (translation-driven spec split) | stage 1 | unified at 60; lesson4 and all graders re-run green |
| README "seven single-file Python scripts"; course has ten lessons | stage 2 | "ten Python scripts"; "single-file" wording softened |
| ch07 "assemble all seven lessons" (stale count, present in the original Chinese too) | stage 2 | "all ten lessons" (zh-tw kept as historical record) |
| ch01 prose said 12-char limit; code and runtime use 20 | stage 2 | prose now says 20 |
| ch01 quoted an unnamed "original author" (attribution risk) | stage 2 | rewritten as plain prose, no quotation |
| em-dash in README title and docs template | stage 1 | replaced; docs rebuilt; repo-wide em-dash count now 0 |
| 12 unpushed commits authored with a personal email via local git config override | stage 2 | config fixed; all unpushed commits rebased with reset-author; single noreply author verified |

## Noted, not changed

- `docs/build.py` embeds a temp-dir path in one recorded playback (cosmetic, regenerated each build).
- Goodhart/Strathern 1997 attribution in ch07: flagged for external verification in the final
  pre-publish scan (citation re-check), not assumed correct.
- Spaced double-hyphen " -- " style in prose: consistent house style for now; optional polish item.

## Verified green after fixes

`progress.py --solutions` 11/11; `quiz.py --check` 32 questions OK; zero CJK outside `zh-tw/`;
zero em-dash outside `zh-tw/`; working tree clean; unpushed authors all noreply.
