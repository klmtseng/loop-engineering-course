# Loop Engineering from Scratch: Teaching an AI to Finish, Verify, and Stop on Its Own

> 🌐 **Interactive learning online (runs in your browser, no install needed)**:<https://klmtseng.github.io/loop-engineering-course/>
> (Currently covers Lesson 1 as an interactive slice; more lessons coming soon.)

> Prompt engineering is "you craft a sentence, hand it to the agent, and look at the result once."
> **Loop engineering is "you design a system that repeatedly cycles through act -> verify -> decide
> until the goal is met or a limit is hit."** In one sentence: replace the human who keeps watching
> and deciding whether to prompt again with a piece of code.

This course uses ten Python scripts -- one lesson = one core file (plus an optional shared anim.py for the --animate view) -- starting from an `act->verify->decide` loop
under 15 lines, and builds up to an unattended system that "wakes itself up, runs its own checks,
and only calls you when it cannot handle something," before exposing the most dangerous truth in this
field: **verify is just a proxy metric, and agents will game it.**

Every lesson **uses only the standard library, requires no API keys, and runs with `python3 lessonN.py`.**
The course uses a "mock agent" as a stand-in so you can see the loop structure clearly first.
How to plug in a real agent (Claude Code / Codex / your own LLM call) is covered in each lesson's
extended exercises and in the "Connecting a Real Agent" section below.

> This is the sequel to the sister course *agent-from-scratch* (which teaches you how to **build** an agent,
> not yet publicly released). This course teaches you **how to turn an agent into a self-running system.**
> You can learn either one first, but some familiarity with agent concepts is recommended.

## Before You Start: What You Need to Know (30-second self-check)

The **main track is for people who can write Python.** If you can answer the following three questions,
you are ready to begin:

1. Can you read and write a `for` / `while` loop and a `def` function?
2. Do you know that "exit code 0 means success" for shell commands? (Used in Chapter 2.)
3. Do you have a rough idea of what `git` and scheduling (cron) are? (Used in Chapters 5 and 6 -- no worries if not, see below.)

**Tiered paths**: The main track is intermediate, but two places that "jump a bit" have detours built in:

- Chapter 5 uses **threading (parallel execution)**: even if you have never written multi-threaded code,
  a primer box at the start of the chapter explains what you need.
- Chapter 6 uses **cron scheduling**: if you are not familiar with cron, a three-line box at the chapter
  start covers everything you need.
- Never worked with AI agents? First pick up the three concepts "LLM calls, tool calls, ReAct loop"
  from any introductory resource, then come back.
- **Platform**: all demos run on Linux/Mac. `git worktree` and `cron` in Chapters 5 and 6 are Unix tools;
  Windows students should use WSL, or treat those two chapters as conceptual (the runnable parts remain
  pure standard library and cross-platform).

> If you just want to "understand the concepts without coding," that is fine too: every chapter starts
> with a **TL;DR** sentence; reading that line plus the concept sections is enough.
> But the real value of this course is **doing it** -- the verification layer (see below) forces
> you to write the loop yourself.

## Course Contents

| # | File | Topic | Hands-on exercise | One-liner |
|---|------|------|------|--------|
| 1 | `lesson1_minimal_loop.py` | The minimal loop | `exercises/exercise1_*` | loop = act->verify->decide, replace human judgment with code |
| 2 | `lesson2_exit_conditions.py` | Exit conditions and the verify gate | `exercises/exercise2_*` | verify via "run a command, check exit code"; exits must cover SUCCESS/FUSE/STALL |
| 3 | `lesson3_safety_budget.py` | Safety and cost | `exercises/exercise3_*` | fuse + budget + run-log + staged rollout L1->L3: four safeguards before going live |
| 4 | `lesson4_maker_checker.py` | maker/checker dual-agent | `exercises/exercise4_*` | an agent that says "I'm done" is not an impartial judge of its own work |
| 5 | `lesson5_parallel_isolation.py` | Parallelism and isolation | `exercises/exercise5_*` | to parallelize, first isolate; use `git worktree` for coding scenarios |
| 6 | `lesson6_scheduling.py` | Scheduling and unattended operation | `exercises/exercise6_*` | connect to cron (with external state), turning the script into a system that ships while you sleep |
| 7 | `lesson7_verifier_gaming.py` | **verify is a proxy metric** | `exercises/exercise7_*` | agents are not solving the problem -- they are making the verify go green, and they will exploit it |

**Part II -- Driving a Real Agent** (assumes you already understand agent basics: tool calls, ReAct, context):

| # | File | Topic | Hands-on exercise | One-liner |
|---|------|------|------|--------|
| 8 | `lesson8_real_agent.py` | Non-determinism and real agents | `exercises/exercise8_*` | real agents are stochastic and can regress; design for distributions + best-so-far (`--real` connects to a live LLM) |
| 9 | `lesson9_context_strategy.py` | Cross-iteration context strategy | `exercises/exercise9_*` | do not stuff memory into conversation history (it blows up); write it as a durable spec in the repo |
| 10 | `lesson10_loop_evals.py` | Loop-level evals | `exercises/exercise10_*` | one task passing is not the same as a good loop; measure success/iters/escalation/cost across a task suite |
| 🎓 | -- | **Capstone** | `capstone/` | assemble the pieces from all ten lessons into a robust, unattended maintenance loop that handles noisy agents |

> ⏱ Part I: each lesson takes about **15-25 minutes**. Part II: about **20-30 minutes** each. Capstone: about **45-60 minutes**. Total: roughly one day.

Each lesson comes with a textbook chapter (concepts + hands-on + self-check + extended exercises):
[`ch01`](textbook/ch01_minimal_loop.md) ·
[`ch02`](textbook/ch02_exit_conditions.md) ·
[`ch03`](textbook/ch03_safety_budget.md) ·
[`ch04`](textbook/ch04_maker_checker.md) ·
[`ch05`](textbook/ch05_parallel_isolation.md) ·
[`ch06`](textbook/ch06_scheduling.md) ·
[`ch07`](textbook/ch07_verifier_gaming.md) ·
[`ch08`](textbook/ch08_real_agent.md) ·
[`ch09`](textbook/ch09_context_strategy.md) ·
[`ch10`](textbook/ch10_loop_evals.md) ·
[Appendix A: Toy-to-Production Primitive Mapping](textbook/appendix_mcp_mapping.md)

## Setup

```bash
# Nothing to install. Python 3.8+ is all you need; every lesson uses only the standard library.
python3 lesson1_minimal_loop.py

# Want to watch the loop iterate round by round? Add --animate to any lesson:
python3 lesson1_minimal_loop.py --animate

# (Optional) Lesson 8 can connect to a real LLM. Without a key it falls back to the zero-dependency stub.
export OPENROUTER_API_KEY=sk-or-...   # no key needed; it just degrades gracefully
python3 lesson8_real_agent.py --real
```

Recommended workflow: read the textbook chapter, type through the lesson yourself, then compare with `lessonN_*.py`.

## Learning Flow Per Lesson

```
Read textbook/chNN  ->  Run lessonNN (add --animate to slow it down)  ->  Write exercises/exerciseNN
                    ->  Run check_exerciseNN to verify  ->  All green means you pass; go to the next lesson
```
Finish with `capstone/`, then run `python3 progress.py` to see your overall score.

## Core Concepts at a Glance

Every loop is always these four things:

```
goal    A clear, machine-checkable objective (not "make it better" -- it means "verify returns True")
act     Do one step (call the agent / run a command / edit a file)
verify  Check: did we reach the goal?         <- the soul of the loop
decide  If not, loop back with feedback; if yes, or if the budget is gone, stop
```

Pre-launch checklist for any loop (all from Chapter 3):

- [ ] **max-iter fuse** -- without it, a stuck agent burns through your quota indefinitely
- [ ] **budget** -- set a hard cap on tokens / cost / wall-clock time; estimate before you run
- [ ] **run-log** -- one JSONL line per iteration, append-only; your black box when things go wrong
- [ ] **start at L1** -- dry-run to see what it wants to do, ask a human before it acts, then go fully automatic
- [ ] **independent checker** -- do not let the agent verify its own output (Chapter 4)
- [ ] **isolation** -- for parallel work, use worktrees; do not share a working directory (Chapter 5)
- [ ] **verify that cannot be gamed** -- agents will hard-code answers or weaken tests to fool a weak verify;
      use hold-out sets, random inputs, and isolation (Chapter 7)
- [ ] **re-verify best-so-far** -- taking the max over a noisy or gameable verify picks lucky outliers
      (optimizer's curse / maximization bias); validate the selected best on a hold-out set (Chapter 8)

## Assessment: Confirm You Actually Learned It (Reading Is Not Enough)

The irony of this course: it teaches you "do not let the agent self-evaluate -- run a verify gate" --
so it applies the same principle to students. Three layers of assessment, each an objective gate:

```bash
# 1) Hands-on exercises + autograder (one set per lesson -- the most important)
#    Open exercises/exercise1_minimal_loop.py, fill in the TODOs, then:
python3 exercises/check_exercise1.py        # all green means you pass; fix anything marked red

# 2) Knowledge quiz (do you remember the concepts?)
python3 quiz/quiz.py --chapter 1            # or --all; MCQ/short-answer auto-graded, reflection prompts get reference answers

# 3) Capstone (can you assemble one yourself?)
#    Follow capstone/SPEC.md to write capstone/my_loop.py, then:
python3 capstone/grade_capstone.py

# Check overall progress (this script itself runs a verify loop over your learning)
python3 progress.py
```

`exercises/solutions/` contains reference solutions. **Look only when truly stuck, then retype the solution from scratch.**

## Connecting a Real Agent (Swap the Stand-in for the Real Thing)

The course's `mock_agent` is a stand-in to help you focus on the loop structure. Replacing it requires changing exactly one function:

- **Switch to an LLM call**: replace `mock_agent(...)` with a single chat API call,
  and pass the verify/checker feedback back as a user message.
  (If you have done `agent-from-scratch`, just reuse the `llm()` function from there.)
- **Switch to Claude Code / Codex CLI**: use `subprocess` to invoke the agent CLI,
  pass the task as the prompt, and treat its output as the iteration's artifact. verify runs the same.
- **Switch verify to a real check**: replace the Chapter 2 `check_cmd` with your project's
  `pytest` / `ruff` / `npm run build`.

The loop skeleton needs no changes at all -- that is precisely the point of this course:
**the value of a loop is in the skeleton, not in which agent you plug in.**

## Design Principles

1. **One lesson, one core concept** -- every lesson runs independently; the comments are the lecture notes
2. **Zero dependencies, zero API keys** -- standard library throughout; the stand-in agent is explained clearly before showing you how to replace it
3. **Honest** -- a mock is a mock, a simulation is a simulation; where `git worktree` is the right tool, nothing pretends otherwise
4. **Skeleton first** -- internalize act->verify->decide as muscle memory; patterns like "PR until green" are just variations on that skeleton

## References

- The tweet that started it all: a site aggregating loop engineering ideas from dozens of developers <https://loops.elorm.xyz/>
- `cobusgreyling/loop-engineering` (loop-init / loop-audit / loop-cost and other CLI tools)
  <https://github.com/cobusgreyling/loop-engineering>
- GitHub topic page <https://github.com/topics/loop-engineering>

---

> **Traditional Chinese version**: the original Traditional Chinese README and all textbook chapters
> are preserved in [`zh-tw/`](zh-tw/) as a bonus resource.
