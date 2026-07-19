# Hands-On Exercises + Autograder

Each lesson comes with a pair of "fill-in exercise + autograder." **This is the real assessment in this course:**
you do not pass just by reading -- you have to write the key lines of the loop yourself and have them
verified by an independent grader.
(Fitting, right -- that is exactly what the course teaches: "do not self-assess, run a verify gate.")

## How to Use

```bash
# 1. Open the exercise file and fill in the TODOs (scaffolding is provided; you write the core logic)
#    For example, Lesson 1:
nano exercise1_minimal_loop.py

# 2. Run the autograder. All green means you pass; fix anything marked red and run again
python3 check_exercise1.py

# 3. Only look at the reference solution when truly stuck (then retype it from scratch)
cat solutions/exercise1_minimal_loop.py
```

`check_exerciseN.py` defaults to checking `exerciseN_*.py` in the same directory.
You can also use `--target` to point at a different file (e.g., to confirm the grader itself is correct
by running it against the reference solution):

```bash
python3 check_exercise1.py --target solutions/exercise1_minimal_loop.py
```

## Exercise Reference Table

| Exercise | Lesson | What you implement |
|---|---|---|
| `exercise1_minimal_loop.py` | Lesson 1 | `loop()`: act->verify->decide + fuse |
| `exercise2_exit_conditions.py` | Lesson 2 | `loop()`: SUCCESS / FUSE / STALL exits |
| `exercise3_safety_budget.py` | Lesson 3 | `Budget` two methods + `should_execute()` (L1 does not execute) |
| `exercise4_maker_checker.py` | Lesson 4 | `checker()`: independent, strict, lists all defects |
| `exercise5_parallel_isolation.py` | Lesson 5 | `run_isolated()`: each worker gets its own dedicated directory |
| `exercise6_scheduling.py` | Lesson 6 | `tick()`: triage->act->verify->done/escalate |
| `exercise7_verifier_gaming.py` | Lesson 7 | `strong_verify()`: write a ungameable verify using hold-out + random inputs |
| `exercise8_best_so_far.py` | Lesson 8 | `best_so_far_loop()`: return the historical best even when the agent regresses |
| `exercise9_context_strategy.py` | Lesson 9 | `strat_spec_in_repo()`: bounded context + deduplication |
| `exercise10_loop_evals.py` | Lesson 10 | `aggregate()`: compute the four loop-level metrics |

## Checking Overall Progress

Go back to the course root and run the progress dashboard to see all ten lessons + capstone at a glance:

```bash
python3 ../progress.py
```
