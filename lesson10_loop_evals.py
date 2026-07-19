"""
Lesson 10 -- Loop-Level Evals (Evaluating the Loop in Aggregate)
=================================================================
Every earlier lesson verified "one task, one run." But "is this loop good"
is a different question -- it requires looking at **a whole batch of tasks
and the overall performance**. This is the real basis for "dare we deploy it."

And -- remember Lesson 8? **Real agents are stochastic.** The same task run
through the same loop twice may give different results. This means: **when
evaluating a loop, you cannot run each task just once** -- you would be
measuring luck, not performance. The correct approach is **repeat each task
k times, look at the distribution, and always report n (sample size)**.

People who think in agent terms think in eval terms. A loop eval should
measure at least four numbers:

    success_rate     -- fraction of all trials the loop handles on its own
    mean_iters       -- [successful runs only] mean number of rounds (read alongside escalation rate)
    escalation rate  -- fraction of tasks escalated to a human
    mean_cost        -- mean tokens burned per trial

Run:
    python3 lesson10_loop_evals.py
    python3 lesson10_loop_evals.py --animate
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim

GOAL = 90
COST_PER_ITER = 100   # tokens per round (relative indicator, not real tokenization)
REPEATS = 20          # repetitions per task (sampling a stochastic system)

# task suite: each number is a task's "starting coverage base" -- higher means easier
# (more likely to randomly walk past 90)
SUITE = [86, 84, 82, 80, 78, 76, 74, 72, 70, 66]


def run_task(base, max_iters, rng):
    """Run one task once (stochastic! reuses Lesson 8's noisy model + best-so-far).
    Coverage random-walks each round; if best >= GOAL it is SUCCESS; otherwise ESCALATED."""
    best = 0
    for i in range(1, max_iters + 1):
        cov = max(0, min(100, round(rng.gauss(base + i * 2.0, 9))))
        best = max(best, cov)
        if best >= GOAL:
            return {"status": "SUCCESS", "iters": i, "cost": i * COST_PER_ITER}
    return {"status": "ESCALATED", "iters": max_iters, "cost": max_iters * COST_PER_ITER}


def aggregate(records):
    """Aggregate a batch of per-trial results into loop-level metrics."""
    n = len(records)
    succ = [r for r in records if r["status"] == "SUCCESS"]
    esc = [r for r in records if r["status"] == "ESCALATED"]
    return {
        "success_rate": round(len(succ) / n, 2),
        "mean_iters": round(sum(r["iters"] for r in succ) / len(succ), 1) if succ else 0.0,  # successful runs only
        "escalation_rate": round(len(esc) / n, 2),
        "mean_cost": round(sum(r["cost"] for r in records) / n, 1),
    }


def evaluate_loop(suite, max_iters, master_seed):
    """Run every task in the suite REPEATS times each; return (metrics, n)."""
    rng = random.Random(master_seed)
    records = [run_task(base, max_iters, rng) for base in suite for _ in range(REPEATS)]
    return aggregate(records), len(records)


if __name__ == "__main__":
    anim.from_argv()
    n_total = len(SUITE) * REPEATS
    print("=" * 72)
    print(f"Running {len(SUITE)} tasks x {REPEATS} repetitions each (n={n_total} trials), A/B two loop configs")
    print("=" * 72)
    print(f"  {'Config':<16}{'Success rate (n)':<18}{'Mean iters*':<13}{'Escalation':<12}{'Mean cost'}")
    print("  " + "-" * 62)
    for max_iters in (3, 8):
        anim.step("->", f"running max_iters={max_iters} ({REPEATS} runs per task)")
        m, n = evaluate_loop(SUITE, max_iters, master_seed=0)
        print(f"  max_iters={max_iters:<5}{str(m['success_rate'])+f' (n={n})':<18}"
              f"{m['mean_iters']:<13}{m['escalation_rate']:<12}{m['mean_cost']}")
        anim.pause(0.6)
    print("  * Mean iters counts successful runs only; read alongside escalation rate --")
    print("    otherwise 'giving up very fast' looks like 'very efficient'.")

    # Stochastic system: the same config run with different seeds gives a range, not a point
    print("\n  Stochastic reminder: same config, 5 different seeds, success_rate range:")
    for max_iters in (3, 8):
        rates = [evaluate_loop(SUITE, max_iters, master_seed=s)[0]["success_rate"] for s in range(5)]
        print(f"    max_iters={max_iters}: {min(rates)} ~ {max(rates)}  (a single point estimate bounces in this interval)")

    print("=" * 72)
    print("Reading the table (this is everyday loop tuning):")
    print("  * max_iters 3 -> 8: success rate up, escalation down, but mean cost up too. No optimal -- only trade-offs.")
    print("  * Because the agent is stochastic (Lesson 8), repeat each task and look at the distribution.")
    print("    Always report n; always think in intervals -- a single point estimate is just luck.")
    print("-" * 72)
    print("Mindset: a single task verify turning green does not make the loop good.")
    print("         Repeat-sample a task suite, measure four metrics, A/B configs before deploying --")
    print("         this is exactly what ecosystem tools loop-audit / loop-cost automate.")
