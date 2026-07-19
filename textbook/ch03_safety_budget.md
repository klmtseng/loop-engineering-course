# Chapter 3 -- Safety and Cost

> **Chapter goal**: learn the four safeguards that turn a "toy loop" into a "production loop":
> fuse, budget, run-log, and staged rollout (L1->L3). By the end you will have this conviction:
> **the real challenge of loop engineering is not making it run -- it is making it run safely and affordably.**
>
> Reference solution: [`lesson3_safety_budget.py`](../lesson3_safety_budget.py)

**TL;DR**: four safeguards before going live -- max-iter fuse, budget, append-only run-log, and
staged rollout from L1 (dry-run) to L3 (fully automatic).

## 3.1 Concept: A System That Runs Itself Can Also Break Itself

To be blunt about what the first two lessons built:

- A system that "calls the agent repeatedly on its own" = a system that **spends money repeatedly on its own**.
- A system that "edits files / pushes commits on its own" = a system that can **break things while you sleep**.

So before you let any loop run unsupervised, make sure all four safeguards below are in place.
These are the floor, not advanced options.

## 3.2 The Four Safeguards

### Safeguard 1: max-iter fuse

Already present in Chapters 1 and 2. The only point to emphasize here: **without it, nothing else matters.**
A stuck agent can burn through your entire quota overnight. The fuse is the loop's seatbelt.

### Safeguard 2: Budget -- estimate first, deduct as you go, stop when exhausted

Iteration count is just one dimension. Real cost requires a hard cap on **tokens / dollar amount / wall-clock time**:

```python
class Budget:
    def can_continue(self):
        return self.used_iters < self.max_iters and self.used_tokens < self.max_tokens
    def charge(self, tokens):
        self.used_iters += 1
        self.used_tokens += tokens
```

The principle is "estimate before running": before starting, compute "frequency x tokens per iteration x unit price"
to estimate how much this loop will cost per day or per month. Do not wait for the bill to find out.
Community tools like `loop-cost` are built to do exactly this.

> **The token counts in this lesson are made up. How do you get real numbers?** Every LLM API response
> includes a `usage` field (`prompt_tokens` / `completion_tokens`). Accumulate each iteration's `usage`
> and you have the loop's **actual** cost -- no guessing needed. Any OpenAI-compatible API response JSON
> has a `usage` field you can read directly.
> Pipe that number into `Budget.charge()` and the budget shifts from "estimate" to "measured reality."
>
> Some aggregators (like OpenRouter) even return a `cost` field in `usage` (the actual charge in dollars),
> so you do not even need to compute `tokens x unit price` yourself -- just accumulate `cost` directly
> into `Budget`.

### Safeguard 3: run-log -- automation without logs is as if it never happened

Write one JSONL line per iteration, append-only, **never overwrite**. When things go wrong, this is your
only black box:

```python
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(logfile, "a") as f:                       # "a" = append, never overwrite
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")
```

Running an unattended loop without a run-log is like handing your car keys to it without installing a dashcam.

### Safeguard 4: Staged rollout L1 -> L2 -> L3

**The most important safeguard -- and the one most commonly skipped.** Do not let the loop
take automated actions from the very start. Roll it out in three stages:

| Level | Behavior | What you are verifying |
|---|---|---|
| **L1 report** | observe and report only, **never act** (dry-run) | is what it *wants to do* correct? |
| **L2 assisted** | will act, but pauses to ask a human before each side-effecting action | is *how it acts* correct? |
| **L3 unattended** | fully automatic, only escalates to a human on error or budget exhaustion | confirmed that the previous two stages were stable |

This is an instance of a general pattern for safe agent systems: **propose / commit separation**.
The agent always only "proposes" an action; whether to actually execute it is decided by the loop
based on the autonomy level:

```python
if level is Level.L1_REPORT:
    log_event(..., proposed=action, executed=False)   # log only, never execute
else:
    result = execute(action, workdir)                 # L2/L3 actually acts
    log_event(..., proposed=action, executed=True, result=result)
```

### When can you graduate from L1 to L2, and from L2 to L3?

Use evidence, not gut feeling. A practical graduation threshold:

- **L1 -> L2**: review N dry-run sessions (e.g., one week or 50 runs) in the run-log; every action
  the agent "wanted to take" was **something you would have approved**, without a single surprise.
  That means its judgment is trustworthy enough to let it act (but still asking a human each step).
- **L2 -> L3**: during the L2 phase, you almost always clicked approve and almost never blocked a step;
  the fuse, budget, run-log, and rollback are all in place. That means the human gate is not filtering
  anything anymore, and it is safe to remove it.
- **Any time you have a "good thing I was watching" intervention -> step back one level**, do not push through.

Graduation is the accumulation of one-way trust -- it does not happen automatically when a timer expires.

## 3.3 Hands-On

`lesson3_safety_budget.py` runs the same loop once at L1 and once at L3:

```bash
python3 lesson3_safety_budget.py
```

**Checkpoint one**: look at the L1 section -- the agent "wants to write a file," but because it is L1,
only the intention is logged; nothing is executed. You see exactly what it plans to do at zero risk.
Only after confirming it looks fine do you let it actually run at L3.

**Checkpoint two**: the last section intentionally sets the budget to `max_iters=1`. The agent has not
finished when it gets cut off, and the loop returns **ESCALATED rather than SUCCESS** -- "cut off by
budget" is an event that requires human attention; pretending it succeeded would hide the truth.
Check the last line of run.jsonl: `ESCALATE_budget_exhausted`.

**Checkpoint three**: read run.jsonl. What happened each iteration, how much it cost, whether it actually
executed -- all there. This is the only evidence you can rely on after going live.

## 3.4 Self-Check

1. Why is "a system that runs itself can also break itself"? Give two types of damage it can cause.
2. Besides iteration count, what other dimensions should a budget cover? What does "estimate before running" mean?
3. Why must the run-log be append-only and never overwritten?
4. What does each of L1 / L2 / L3 verify? Why should you not start at L3?
5. What is "propose / commit separation"? How does it make L1 zero-risk?
6. Why should a budget-exhausted loop return escalate rather than success?

## 3.5 Extended Exercises

- **Add a dollar cap**: give Budget a `max_usd` field, computed as `used_tokens x unit_price`, and stop
  when exceeded.
- **Add a kill switch**: have the loop check at the start of each iteration whether a file (e.g., `STOP`)
  exists; if it does, exit cleanly immediately. This is the emergency brake for unattended systems.
- **Implement real L2**: change the "assume human approves" in L2 to an actual `input("Execute? (y/n) ")`,
  and experience what human-in-the-loop feels like -- and why it cannot work for unattended operation.

## 3.6 Hands-On Assessment

Open [`exercises/exercise3_safety_budget.py`](../exercises/exercise3_safety_budget.py),
implement `Budget` and `should_execute()`, then run `python3 exercises/check_exercise3.py`.

## 3.7 Self-Check Answers

1. It spends money on its own and modifies files on its own; two types of damage: burning through the API bill, and breaking files or commits while you are not watching.
2. Also needs to cap tokens / dollar amount / wall-clock time; "estimate before running" means computing "frequency x tokens per iteration x unit price" before starting, not waiting for the bill.
3. Because it is the only black box when things go wrong; overwriting destroys the historical evidence.
4. L1 verifies "is what it wants to do correct?"; L2 verifies "is how it acts correct?"; L3 is only for what has been verified as safe; skipping straight to L3 means skipping verification that it is safe.
5. The agent only "proposes" actions; whether to execute is decided by the loop based on autonomy level; L1 only logs proposals and never executes, making it zero-risk.
6. Because "cut off by budget" means the task is unfinished and someone needs to look; pretending success masks an incomplete result.

---

Passing condition: you can name the four safeguards, explain the purpose of L1->L3, and point to an escalate event in the run-log.
Next, we handle the situation where verification itself requires judgment -- and why you cannot let the agent verify its own output.
-> [Chapter 4: maker/checker Dual-Agent](ch04_maker_checker.md)
