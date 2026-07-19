# Capstone -- Final Assessment: Build a Loop You Can Deploy

Each earlier lesson practiced exactly one component. This capstone has no scaffolding -- **you assemble the components yourself** to build a "nightly maintenance loop": it polls a pending-work queue, handles each item, verifies independently, logs everything, escalates when budget is exhausted, and can be invoked by cron with `--once`.

## How to Start

```bash
cp my_loop_template.py my_loop.py     # copy the template, implement in my_loop.py
nano my_loop.py
python3 grade_capstone.py             # run the grader (grades my_loop.py by default)
```

## Six Requirements Your my_loop.py Must Satisfy

The grader uses the following **interfaces** for behavioral testing, so implement them with these signatures (internals are up to you):

| # | Requirement | Interface | Pass Condition |
|---|---|---|---|
| 1 | **Fuse + Budget** | `Budget(max_iters, max_tokens)` with `.can_continue()` and `.charge(tokens)` | Can no longer continue when either iter count or token count is exhausted |
| 2 | **run-log** | `log_event(logfile, **fields)` | Appends one JSONL line each call, **never overwrites** |
| 3 | **Independent checker** | `checker(task, result) -> bool` | Returns True for good results, False for bad results |
| 4 | **Main loop (integrates Req 7)** | `run(world, logfile, budget, level)` | Handles each task using `solve_task(task_agent(task), ...)` (do not bypass best-so-far); SUCCESS -> done, FAIL -> escalate; budget exhausted -> escalate; returns dict with `done`/`escalated`/`budget_exhausted` |
| 5 | **L1 safety** | `run(..., level="L1")` | In L1, no side effects are actually executed (world's `executed` counter stays at 0) |
| 6 | **Isolation + scheduling** | `worker_dir(base, name)` gives each worker a distinct path; `python3 my_loop.py --once` runs one tick then exits 0 | Paths are distinct and under base; `--once` exits cleanly |
| 7 | **Robust against noisy agents** | `solve_task(agent, max_iters)` -- uses best-so-far to iterate an agent that may regress | Remembers peak mid-run; returns historical best, not last-round value; returns FAIL+best if goal never reached |

## Hints

- Requirements 1/2 come directly from Lesson 3; Req 3 from Lesson 4; Reqs 4/5 are Lessons 3+6 combined;
  Req 6's isolation from Lesson 5, scheduling from Lesson 6; **Req 7 comes from Lesson 8's best-so-far**.
- Req 7's `solve_task(agent, max_iters)`: `agent(attempt)` returns a coverage value (int), goal = `GOAL` (90);
  track the historical best each round; when best >= GOAL return `("SUCCESS", best)`; when fuse burns out return `("FAIL", best)`.
  This is the one step that requires **design judgment**: real agents regress, trusting only the last round throws away good results.
- The `world` object is provided by the grader and has: `todos` (list), `done` (list), `escalated` (list),
  `executed` (int counter, increment by 1 each time you actually execute a side effect). The template includes a usable `World`.
- Stuck? Look at `solution_my_loop.py` (read it, then type it out yourself from scratch).
