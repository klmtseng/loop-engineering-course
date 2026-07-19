# Chapter 2 -- Exit Conditions and the Verify Gate

> **Chapter goal**: upgrade the verify from Chapter 1 to "run a real command and check its exit code,"
> and learn the three exits a loop needs to survive in the real world: SUCCESS / FUSE / STALL.
> By the end you will understand: **the quality of a loop rests almost entirely on the verify step.**
>
> Reference solution: [`lesson2_exit_conditions.py`](../lesson2_exit_conditions.py)

**TL;DR**: the most reliable verify is "run a command and check the exit code"; a loop ready for production
needs at least three exits: SUCCESS / FUSE / STALL.

## 2.1 Concept: The Most Reliable verify Is "Run a Command"

Chapter 1's verify was a hand-written Python function. In a coding context, you actually have
a ready-made, zero-cost, non-lying judge -- **the command exit code**:

| Command | Exit code 0 means |
|---|---|
| `pytest` | all tests pass |
| `ruff check .` | no lint issues |
| `npm run build` | build succeeded |
| `curl -f https://.../health` | service is alive |

This kind of "check command that runs after each iteration" is called a **between-iteration command**
and is the most central component in loop engineering. The idea is: **do not ask the agent "do you think
you are done?" -- ask the compiler, the tests, the linter -- they do not suffer from overconfidence.**

```python
def run_check(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, shell=True,
                          capture_output=True, text=True, timeout=30)
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output   # 0 = passed; output fed back to agent as feedback
```

**Key detail**: pass the command output (error messages, names of failing tests) verbatim to the next
iteration. That red text is the agent's only material for fixing the error. In this lesson's demo
you will see the agent go from `SyntaxError` to "printed 41, expected 42" to correct -- entirely
driven by this feedback.

## 2.2 Concept: One Exit Is Not Enough -- You Need Three

"Run until green" sounds great, but what if it never goes green? A loop ready for production needs
at least three exits:

| Exit | Trigger | Why it is needed |
|---|---|---|
| **SUCCESS** | check command returns 0 | the outcome you want: goal met, stop |
| **FUSE** | iterations exhausted, still not green | max-iter fuse, prevents infinite spending (already in Chapter 1) |
| **STALL** | two consecutive iterations produce identical output | the agent is stuck; running more would waste resources, stop **early** |

STALL is commonly missed by beginners. Without it, a stuck agent burns through the entire max-iter budget
before stopping -- every wasted iteration is money and time you did not need to spend.
Detecting it just requires remembering the previous iteration's output:

```python
if code == last_code:        # this iteration is identical to the previous
    return Exit.STALL, None  # no need to wait for the fuse; stop now
last_code = code
```

> **Precise note (the boundary of this STALL implementation)**: it only compares against "the previous
> iteration," so it only catches **fixed points** -- two consecutive identical outputs. It **cannot catch
> cycles of length >= 2**, such as an `A, B, A, B, A, B` oscillation (which is common with real agents);
> those still burn to FUSE. The word "stuck" might imply it catches "going in circles," but this
> implementation only blocks "standing still." To catch cycles, you need to remember **the outputs of the
> last N iterations** and stop when a repeat appears (still heuristic -- see the extended exercises in the
> textbook).

> The real world has more exits: timeout, an external kill-switch file appearing, budget exhausted
> (Chapter 3). But SUCCESS / FUSE / STALL are the floor -- missing any one of them means the loop
> is not ready to ship.

## 2.3 Hands-On

`lesson2_exit_conditions.py` has the agent repeatedly edit `add.py` until it prints `42`.
The verify gate is a small `check.py` script (simulating a real pytest in a project):

```python
check_cmd = "python3 check.py"
reason, code = loop(check_cmd, workdir)
```

Run it:

```bash
python3 lesson2_exit_conditions.py
```

**Checkpoint**: observe the "check command output" each iteration. Iteration 1 is a syntax error traceback,
iteration 2 is "printed '41', expected '42'", iteration 3 finally goes green. The agent reads the
actual error from the previous step every time -- that is the power of between-iteration commands.

**Second checkpoint**: the loop function knows nothing about "42". It only knows "run check_cmd,
check the exit code." So you can replace `check_cmd` with `pytest`, `ruff`, or `make`, and this loop
**does not need a single change**. This "decoupling of verification from task logic" is the hallmark
of a well-designed loop.

## 2.4 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Loop always runs to FUSE | verify condition too strict, or agent cannot meet the requirement | first manually confirm "if a human did it, would the command go green?" |
| Gets stuck but burns to FUSE instead of stopping early | no STALL detection | compare consecutive outputs; exit early when they match |
| Feedback is an empty string, agent learns nothing | check command swallows its output (e.g. `grep -q`) | make verify print messages that are readable by both humans and the agent |
| subprocess hangs and never returns | command waits for input or runs indefinitely | always set `timeout=`; timeout is also a valid exit |

## 2.5 Self-Check

1. What is a between-iteration command? Why is it better than "asking the agent if it's done"?
2. What are the three exits a production-ready loop must have? What does each one guard against?
3. Why does STALL detection save money? What is the worst case without it?
4. Why must the check command's output be passed back to the agent verbatim?
5. The loop in this lesson can verify any task by swapping `check_cmd`. What design property makes that possible?

## 2.6 Extended Exercises

- **Use a real check**: change the demo to have the agent write a function, and use `pytest` as the
  check_cmd (write a `test_add.py`). Experience "tests as verify."
- **Add a fourth exit**: add a timeout exit -- if any single check command run exceeds N seconds,
  abort and escalate.
- **Deliberately trigger STALL**: set `_VERSIONS` so iterations 2 and 3 are identical, and confirm
  the loop really stops at STALL rather than burning to FUSE.
- **Detect cycles (fix STALL's blind spot)**: the current STALL cannot catch `A, B, A, B` oscillations.
  Switch to a `seen = set()` that remembers the last N iterations' outputs; if the current output is
  already in `seen`, declare "cycling" and exit early. First confirm the original STALL cannot catch it,
  then confirm your new version can. (Think: how large should N be? Could it falsely trigger on a
  valid revisit?)

## 2.7 Hands-On Assessment

Open [`exercises/exercise2_exit_conditions.py`](../exercises/exercise2_exit_conditions.py),
implement the three exits in `loop()`, and run `python3 exercises/check_exercise2.py` to assess.

## 2.8 Self-Check Answers

1. It is a check command that runs every iteration, using exit code to judge; better than "asking the agent" because it is objective and does not suffer from overconfidence.
2. SUCCESS (goal met, stop) / FUSE (iterations exhausted, prevent infinite spending) / STALL (two identical outputs in a row, stop a stuck agent early).
3. STALL stops the moment the agent gets stuck, saving the iterations that would otherwise burn to FUSE; without it, the worst case is burning through the entire max-iter budget.
4. Because that error message is the agent's only clue for the next fix; swallowing it leaves the agent with nothing to go on.
5. "Decoupling verification from task logic": the loop only runs `check_cmd` and reads the exit code, with no knowledge of the specific task.

---

Passing condition: you can implement verify via "run a command and check the exit code," and explain what SUCCESS/FUSE/STALL each guard against.
Next, we face a system that spends money and modifies files on its own -- how to run it safely and affordably.
-> [Chapter 3: Safety and Cost](ch03_safety_budget.md)
