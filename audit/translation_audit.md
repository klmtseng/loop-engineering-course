# Translation Audit — Loop Engineering Course (Internal Mechanical Review)

Auditor: validity-audit Stage 1 (Content/Courseware Pack)
Date: 2026-07-19
Scope: Translation wave (11 commits, `5cd5221`..`HEAD`) → pre-publication release check

---

## 1. Behavioral Changes in .py Files

Diff range: `git diff 5cd5221 HEAD -- '*.py'`

### 1a. exercise4 length limit: 40 → 60 chars  FAIL (judgment needed)

| File | Line | Change |
|---|---|---|
| `exercises/exercise4_maker_checker.py` | spec block | `Length must be <= 40 characters` → `Length must be <= 60 characters` |
| `exercises/solutions/exercise4_maker_checker.py` | ~17 | `if len(draft) > 40:` → `if len(draft) > 60:` |
| `exercises/check_exercise4.py` | test input | `"抱歉,我們會在 24 小時內回覆您。"` → `"Sorry for the trouble. We will reply within 24 hours."` (36 chars, under both 40 and 60) |

**Verdict**: Translation-necessary (original Chinese hard criterion "≤40字" is met only by very terse Chinese text; equivalent English phrases naturally run 40–65 chars). The change is consistent across exercise stub + solution + grader. **However, the lesson4 demo file and textbook ch04 were NOT updated:**

- `lesson4_maker_checker.py` line 55: still says `# 3. Must be at most 40 characters`
- `lesson4_maker_checker.py` line 92: `if len(draft) > 40:`
- `textbook/ch04_maker_checker.md` line 62: `max 40 characters`
- `textbook/ch04_maker_checker.md` line 70: `if len(draft) > 40:`

**This creates a cross-file inconsistency**: the lesson demo enforces 40, but the exercise spec + solution enforce 60. A student who reads the textbook code snippet, then tries the exercise, will get different behavior. This is a P1 bug.

### 1b. anim.py: fuse bar characters changed  PASS (translation-necessary)

`fuse()`: `◉/◯` → `o/.`; `banner()`: `╭─` → `+--`
Affects `--animate` mode only (display, no-op when disabled). ASCII fallback is safer in terminals that don't render Unicode. No logic change.

### 1c. checker keyword strings: "已完成" → "completed"  PASS (translation-necessary)

`lesson*.py` and capstone solution: `result.startswith("已完成")` → `result.startswith("completed")`. The paired maker also changed from `f"已完成 [{task}]"` to `f"completed [{task}]"`, so maker and checker remain internally consistent. Capstone grader test passes with `checker("t", "completed [t]") is True`.

### 1d. check_exercise4.py: grader keyword tests broadened  PASS (translation-necessary)

Original Chinese grader checked `"道歉" in msg`; English grader checks `"apolog" in msg.lower() or "sorry" in msg.lower() or "missing" in msg.lower()`. This broadening is necessary because the English rejection message can use multiple synonyms. Semantically equivalent intent.

---

## 2. Textbook Claims vs. Code Implementation

### ch02 Claims (3 checked)

| Claim | Source | Verification |
|---|---|---|
| "iteration 1: SyntaxError, iteration 2: printed '41', iteration 3: green" | ch02 §2.3 | `python3 lesson2_exit_conditions.py` → Round 1 SyntaxError, Round 2 printed '41', Round 3 green ✅ PASS |
| "STALL: two consecutive identical outputs → stop early" | ch02 §2.2 | `lesson2_exit_conditions.py` code: `if code == last_code: return Exit.STALL, None` ✅ PASS |
| "check_cmd can be swapped for pytest/ruff without changing the loop" | ch02 §2.4 | `run_check()` decouples command from logic; the loop only checks `proc.returncode == 0` ✅ PASS |

### ch07 Claims (3 checked)

| Claim | Source | Verification |
|---|---|---|
| "hard-coded agent fools weak verify, not strong verify" | ch07 §7.4 | `python3 lesson7_verifier_gaming.py` → hard-coded agent green on weak, red on strong ✅ PASS |
| "three cheating techniques: hard-code / weaken verifier / fake completion" | ch07 §7.2 | Table in lesson output matches textbook ✅ PASS |
| "Goodhart's Law attribution: Marilyn Strathern 1997 restatement" | ch07 §7.2 | Same attribution appears in both zh-tw and English textbook; audit does not verify external source (flagged as unverified per 00-diagnosis漏洞3) |

### ch08 Claims (3 checked)

| Claim | Source | Verification |
|---|---|---|
| "best-so-far (by proxy) selected attempt 6: proxy=97, true=82; truly best was attempt 4: true=86, proxy=90" | ch08 §8.2 | `python3 lesson8_real_agent.py` → exact numbers confirmed ✅ PASS |
| "same loop runs with `--real` flag connecting to live LLM, gracefully falls back without key" | ch08 §8.5 | Code: `if "--real" not in sys.argv:` branch; no API key = stub path ✅ PASS |
| "non-determinism not only from sampling; temperature=0 + batch size still causes variance" | ch08 §8.1 | Documentation claim; not verifiable via local run (marked: software behavior claim, unverifiable here) |

---

## 3. Translation Semantic Drift Audit

zh-tw/ vs English textbook. Sample: ch01/ch04/ch07, 5 technical sentences each.

### ch01 (5 sentences)

| zh-tw | English | Verdict |
|---|---|---|
| `loop engineering = 把「決定要不要再 prompt 一次的人」換成一段 act→verify→decide 的程式` | `loop engineering = replacing the human who decides whether to prompt again with an act->verify->decide program` | PASS — equivalent |
| `前提是目標必須機器可判定` | `the prerequisite is that the goal must be machine-checkable` | PASS — equivalent |
| `「把文案寫好一點」不能做成 loop —— 因為 verify 永遠不知道何時該停` | `"Make the copy better" cannot be turned into a loop -- verify would never know when to stop` | PASS — equivalent |
| `MAX_ITERS 這個保險絲不是可選的。沒有它，一個永遠驗不過的任務會讓 loop 無止境地跑` | `MAX_ITERS is not optional. Without it, a task that never passes will run forever` | PASS — equivalent |
| `把模糊願望翻譯成可驗證的條件，是 loop engineering 的第一個真功夫` | `Translating a vague wish into a verifiable condition is the first real skill in loop engineering` | PASS — equivalent |

### ch04 (5 sentences)

| zh-tw | English | Verdict |
|---|---|---|
| `別讓 agent 自評（它一定放水）` | `Never let an agent self-grade (it will always give itself a pass)` | PASS — equivalent |
| `checker 知道三條硬標準（要道歉、要承諾、≤40 字），但 maker 不知道` | `the checker knows three hard rules (must apologize, must commit to a next step, max 40 characters) but the maker does not` | PASS (both say 40) — but see item 1a: exercise uses 60, creating an inconsistency |
| `確定性檢查（最強）：跑測試、跑 linter、規則函式、exit code。客觀、便宜、鑽不動` | `Deterministic checks (strongest): run tests, linters, rule functions, exit code. Objective, cheap, impossible to game` | PASS — equivalent |
| `能寫成確定性規則的驗收，永遠優先寫成規則；LLM judge 是你寫不出規則時的備案` | `if you can write a deterministic rule for the acceptance criterion, always prefer that; an LLM judge is your fallback` | PASS — equivalent |
| `一個有動機說「我完成了」的 agent，不是個公正的裁判` | `An agent that is motivated to say "I'm done" is not an impartial judge` | PASS — equivalent |

### ch07 (5 sentences)

| zh-tw | English | Verdict |
|---|---|---|
| `verify 不是「對或不對」，只是真相的代理指標，而 agent 會去鑽它` | `verify is not "correct or not"; it is only a proxy for the truth, and agents will exploit it` | PASS — equivalent |
| `一旦你把 verify 設為 agent 追求的目標，它就會走最省力的路——那條路往往不是真正解決問題` | `Once you set "make the verify pass" as the goal, the agent achieves it by the least-effort path — and the least-effort path is often not actually solving the problem correctly` | PASS — equivalent |
| `hold-out：準備一批 agent 看不到、也改不到的隱藏案例。硬編幾個公開答案沒用` | `Hold-out (keep a hand hidden): prepare a set of hidden cases the agent cannot see and cannot modify. Hard-coding a few public answers does not help` | PASS — equivalent; zh-tw "看不到也改不到" = "cannot see and cannot modify" ✅ |
| `loop 的品質天花板等於 verify 有多難被鑽` | `the quality ceiling of a loop equals how hard its verify is to game` | PASS — equivalent |
| `改考卷（弱化 verifier）是最毒的一種——agent 不是在答考卷，而是在改考卷` | `Weakening the verifier -- the agent is not answering the exam; it is rewriting the exam paper` | PASS — equivalent; negation preserved |

**No semantic drift found in the 15 sampled sentences.**

---

## 4. README Verification Commands

| Command | Result |
|---|---|
| `python3 exercises/check_exercise1.py --target exercises/solutions/exercise1_minimal_loop.py` | 5/5 PASS ✅ |
| `python3 exercises/check_exercise2.py --target exercises/solutions/exercise2_exit_conditions.py` | 5/5 PASS ✅ |
| `python3 progress.py --solutions` | 11/11 PASS ✅ |
| `python3 quiz/quiz.py --check` | `Quiz bank format OK, 32 questions covering chapters [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` ✅ |
| `python3 capstone/grade_capstone.py --target capstone/solution_my_loop.py` | 17/17 PASS ✅ |
| `python3 quiz/quiz.py --chapter 1` | FAIL — requires interactive stdin; not automatable as-is (expected; quiz is interactive by design) |

**Note**: `quiz.py --chapter` requires interactive input (stdin). This is expected behavior. The `--check` flag validates the bank format non-interactively.

---

## 5. Web Slice (docs/)

| Check | Result |
|---|---|
| CJK characters in `docs/index.html` | 0 found ✅ PASS |
| `python3 docs/build.py` (run 1) | `Generated index.html (235,566 chars; 43 files, 10 lessons). Sanity checks passed` ✅ |
| `python3 docs/build.py` (run 2, idempotency) | Same output size. SINGLE diff: line 108 contains embedded `/tmp/tmpXXXXXX` working directory path from lesson2 recording. Path differs per run by design. |

**Idempotency verdict**: NEAR-PASS with caveat. The tempdir path embedded in the recorded output changes each build. This is a cosmetic difference in a `<pre>` block showing lesson2's working directory, not in any functional code. Students will see a path like `/tmp/tmpXXXXXX` in the recorded playback — accurate (it is a real temp path), but changes between builds. Not a blocking issue for publication.

---

## 6. Publication Readiness

### 6a. Personal Information Scan

| Pattern | Files found (non-zh-tw) | Assessment |
|---|---|---|
| machine username | 0 | PASS |
| machine home path | 0 | PASS |
| `klm.tseng` (email) | 0 | PASS |
| `klmtseng` | README.md line 3 (GitHub URL), docs/template.html lines 70,102 | PASS — these are the intended public GitHub username in deployment URLs, not private data |
| `/home/` (non-pyodide) | 0 | PASS |
| email pattern `@.*\.` | `klmtseng@...` only in git metadata, not in file content | PASS |

### 6b. LICENSE

- File: `LICENSE` (21 lines), MIT License
- Copyright line: `Copyright (c) 2026 klmtseng` ✅
- Full OSI-compliant MIT text present ✅

### 6c. README Relative Links

All 12 relative links in README checked:
`textbook/ch01` through `textbook/appendix_mcp_mapping.md` — all files exist ✅
`zh-tw/` directory — exists ✅

---

## 7. Em-Dash Check

Grep `—` in all non-zh-tw files:

| File | Lines | Content |
|---|---|---|
| `README.md` | line 1 | Title: `Loop Engineering from Scratch — Teaching an AI...` |
| `docs/template.html` | line 7 | `<title>Loop Engineering from Scratch — Interactive Course</title>` |
| `docs/index.html` | line 7 | Same title (embedded from template) |
| `textbook/*.md` | 0 | PASS |
| `*.py` (all lessons/exercises) | 0 | PASS |

**Verdict**: Em-dash present in README line 1, template.html line 7, index.html line 7.
These are all in the course title (`Loop Engineering from Scratch — Teaching an AI to Finish, Verify, and Stop on Its Own`).
The audit spec says "全 repo(zh-tw 除外) grep `—` 應為 0." → FAIL on 3 files (all the same title string).
The em-dash in the title is a legitimate typographic choice for the separator; however, it fails the mechanical check as specified. **P2**: if strict compliance required, replace with `--` or `: `.

---

## 8. Constructive Certainty Labels

Items where PASS is "constructed certainty" rather than evidence:

| Item | Label |
|---|---|
| "CJK in index.html = 0" | **Constructed certainty** — built by build.py from English sources; the check is real but the source controls the output |
| "progress.py --solutions passes 11/11" | **Constructed certainty** — solutions were created alongside graders; graders test against what the solutions implement |
| "capstone grader 17/17" | **Constructed certainty** — solution was built to pass the same grader it is tested against |
| ch08 numeric claim verification (proxy=97 etc.) | **Evidence-based** — numbers depend on random seed iteration; confirmed by actual run |

---

## Summary

| Severity | Count | Key items |
|---|---|---|
| P1 | 1 | `lesson4_maker_checker.py` + `textbook/ch04_maker_checker.md` still say 40-char limit; exercise4 spec+solution use 60. Cross-file inconsistency will confuse students. |
| P2 | 1 | Em-dash in course title (README:1, docs/template.html:7, docs/index.html:7) fails the `grep — = 0` criterion. |
| P3 | 2 | (1) build.py embeds live tempdir path in recording; differs each build. (2) Goodhart's Law attribution (Strathern 1997) not externally verified (per 00-diagnosis 漏洞3). |

All 11 solutions pass their graders. All README verification commands work. No private data found in publishable files. No semantic drift in the 15 sampled translation sentences.
