# Chapter 10 -- Loop-Level Evals

> **Chapter goal**: Step back from "verify one task once" and learn to evaluate
> the overall performance of a loop across an entire batch of tasks -- success
> rate, mean iterations, escalation rate, mean cost -- and use A/B comparison
> of different loop configurations to make deployment decisions.
> After this chapter you will remember: **a single task verify turning green
> does not mean the loop is good.**
>
> Reference solution: [`lesson10_loop_evals.py`](../lesson10_loop_evals.py)

**TL;DR**: A loop's quality must be measured by running it on a whole task
suite and measuring four numbers (success rate / mean iters / escalation /
cost), A/B-testing different configurations, then deciding which to deploy --
this is what `loop-audit` / `loop-cost` automate.

## 10.1 Concept: verify Green != Loop Good

Every earlier chapter asked "did this one task, this one time, pass?" But
deciding whether a loop is **worth deploying** is an aggregation question:
throw a whole batch of realistic tasks at it; how does it perform overall?
People who think in agent terms think in eval terms -- a loop needs its own
eval. Four basic metrics:

| Metric | Meaning | Better direction |
|---|---|---|
| **success_rate** | Fraction of the batch the loop handles on its own | Higher is better |
| **mean_iters** | Mean number of rounds for successful runs | Lower is faster and cheaper |
| **escalation rate** | Fraction of tasks forced to a human | Lower is more autonomous |
| **mean_cost** | Mean tokens burned per task | Lower is cheaper |

## 10.2 Concept: Metrics Only Mean Something In Comparison

**First, a prerequisite that is easy to get wrong: the agent is stochastic
(Chapter 8), so each task cannot be run only once.** If you do, you are
measuring luck. The correct approach is to **repeat each task k times, look at
the distribution, and always report n (sample size)**.
`lesson10` runs 10 tasks x 20 repetitions each (n=200) under two max-iter
settings:

```
Config        Success rate (n)   Mean iters*   Escalation   Mean cost
max_iters=3   0.48 (n=200)       2.1           0.52         254.5
max_iters=8   0.89 (n=200)       3.9           0.11         432.0
* Mean iters counts successful runs only -- must be read alongside escalation rate,
  otherwise "gives up very fast" looks like "very efficient."
```

**Relaxing the fuse (3 -> 8): success rate 0.48 -> 0.89, escalation 0.52 -> 0.11,
but mean cost 255 -> 432.**
You bought success rate with cost. There is no optimal solution -- only
trade-offs, driven by your business context: how much is one success worth? How
painful is one escalation?

And because it is a stochastic system, **point estimates bounce around**. The
same configuration run with 5 different seeds gives success rates of:

```
max_iters=3: 0.39 ~ 0.54     <- treating "0.48" as a fixed value is naive
max_iters=8: 0.89 ~ 0.92
```

So a rigorous conclusion is not "success rate = 0.48" but "success rate ~0.4-0.5
(n=200)." **Always report n; always think in intervals.**

## 10.3 Hands-On

```bash
python3 lesson10_loop_evals.py
```

**Checkpoint**: Look at the difference between the two rows. If you only tested
"max_iters=8 on one easy task", you would think the loop is perfect (success!).
The eval tells you the truth: with a suite that includes hard tasks, what are
the success rate and cost? **One success is an anecdote; a distribution is
evidence.**

> This is exactly what the ecosystem tools `loop-audit` (assessing loop health)
> and `loop-cost` (estimating token spend) automate -- and it echoes the
> consistent principle in agent evaluation: a loop you cannot measure cannot be
> called "useful."

## 10.4 Self-Check

1. Why is "a single task verify turning green" not enough to call a loop good?
2. What are the four basic loop-level eval metrics? Which direction is better for
   each?
3. Why do metrics "only mean something in comparison"? Use `lesson10`'s A/B as
   an example.
4. What do you buy and what do you give up when relaxing max_iters from 3 to 8?
5. What besides the metrics should inform the deployment decision?
6. The agent is stochastic -- what does that mean for how you run an eval? Why
   must you report success rate with n and think in intervals?

## 10.5 Exercise

Open [`exercises/exercise10_loop_evals.py`](../exercises/exercise10_loop_evals.py),
implement `aggregate()` to compute the four metrics (note: mean_iters counts
successful runs only; do not divide by zero when there are no successes).
Run `python3 exercises/check_exercise10.py` to verify.

## 10.6 Self-Check Answers

1. A single task run once may be just luck or an anecdote; a loop's value is its
   overall performance across a whole batch of tasks -- look at the distribution,
   not a single point.
2. success rate (higher) / mean iters (lower) / escalation rate (lower) /
   mean cost (lower).
3. "Success rate 0.9" tells you nothing without a baseline; A/B shows that
   max_iters 3 vs 8 spreads success rate and cost apart, revealing the trade-off.
4. Pay "higher mean cost (roughly 255 -> 432)" to buy "higher success rate
   (roughly 0.48 -> 0.89) + lower escalation."
5. Business weights: how much is one success worth? how painful is one
   escalation? what is the cost budget? Metrics feed decisions -- they do not
   make decisions.
6. Stochastic system means each task must be repeated k times; looking at
   distributions; reporting n so the reader knows the sample size; thinking in
   intervals so that a bouncing point estimate is not taken as a fixed truth.

---

Passing condition: you can name the four loop-level metrics, explain why A/B
comparison is needed, and implement a correct `aggregate()`.
Graduation: you have completed Part II. Back to [README](../README.md) or enter
[`capstone/`](../capstone/) for the final assessment.
