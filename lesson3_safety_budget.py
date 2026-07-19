"""
Lesson 3 -- Safety, Budget & Staged Rollout
========================================================
The loop from the first two lessons can already act on its own, verify, and stop. The problem is:

    A system that "calls the agent repeatedly on its own" = one that "spends money repeatedly on its own."
    A system that "edits your files / pushes commits on its own" = one that can break things
    while you are asleep.

So the real challenge of loop engineering is not making it run -- it is making it run safely and affordably.
This lesson adds four safeguards. They are the minimum bar for turning a toy loop into a production loop:

    1. max-iter fuse          -- already in Lessons 1 and 2; emphasized again here: without it, nothing else matters
    2. budget                 -- set a hard cap on tokens / cost / iterations; estimate before running, deduct as you go
    3. run-log                -- write one JSONL line per iteration. Automation without logs is as if it never happened.
                                 This is your only black box when things go wrong.
    4. staged rollout L1->L3  -- do not let it act autonomously from day one. First see what it wants to do,
                                 then let it act but with human approval, and only then go fully automatic.

       L1 report      observe and report only, never modify anything (dry-run)
       L2 assisted    will act, but pauses to ask a human before each side-effecting action
       L3 unattended  fully automatic, only calls a human (escalates) on error or budget exhaustion

Pure standard library, no keys. We use made-up token counts to demonstrate budget deduction,
and run the same loop once at L1 and once at L3 so you can see the difference.

Run:
    python3 lesson3_safety_budget.py
    python3 lesson3_safety_budget.py --animate    # slow motion: watch the budget drain one unit at a time
"""

import json
import os
import sys
import tempfile
import time
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# Safeguard 4: autonomy level
# ===========================================================================
class Level(Enum):
    L1_REPORT = 1      # observe and report only, never act
    L2_ASSISTED = 2    # act, but ask a human first
    L3_UNATTENDED = 3  # fully automatic


# ===========================================================================
# Safeguard 2: budget -- estimate first, deduct as you go, stop when exhausted
# ===========================================================================
class Budget:
    """Double cap on iterations + tokens. If either is exhausted, the loop must stop.
    In the real world you would also add a dollar cap (= tokens x unit price) and a wall-clock time cap."""

    def __init__(self, max_iters, max_tokens):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.used_iters = 0
        self.used_tokens = 0

    def can_continue(self):
        return self.used_iters < self.max_iters and self.used_tokens < self.max_tokens

    def charge(self, tokens):
        self.used_iters += 1
        self.used_tokens += tokens

    def __str__(self):
        return (f"iters {self.used_iters}/{self.max_iters}, "
                f"tokens {self.used_tokens}/{self.max_tokens}")


# ===========================================================================
# Safeguard 3: run-log -- one JSONL line per iteration, append-only, never overwrite
# ===========================================================================
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


# ===========================================================================
# Mock agent -- returns "the action it proposes" + "how many tokens this used"
# ===========================================================================
# Key design point: the agent only ever "proposes" an action (propose); it does not execute.
# Whether to actually execute is decided by the loop based on autonomy level.
# This propose / commit separation is the skeleton of every safe agent system.
def mock_agent(attempt):
    plan = [
        ("write_file report.md", 120),
        ("write_file report.md", 90),
        ("done", 40),
    ]
    return plan[min(attempt, len(plan) - 1)]


def execute(action, workdir):
    """Actually carry out a side-effecting action (here we only demonstrate file writes)."""
    if action.startswith("write_file"):
        path = os.path.join(workdir, action.split()[1])
        with open(path, "a") as f:
            f.write(f"agent wrote at {time.strftime('%H:%M:%S')}\n")
        return f"wrote {path}"
    return "(no side effect)"


# ===========================================================================
# ★ Key concept for this lesson: a loop with all four safeguards
# ===========================================================================
def safe_loop(level, budget, logfile, workdir):
    print(f"\n--- Starting at level {level.name}, budget cap [{budget}] ---")

    while budget.can_continue():
        anim.fuse(budget.used_iters, budget.max_iters, label="iteration budget")
        anim.step("✎", "act: agent proposes an action")
        action, tokens = mock_agent(budget.used_iters)
        budget.charge(tokens)  # safeguard 2: deduct from budget first
        anim.pause()

        # agent signals it is done -> normal completion
        if action == "done":
            log_event(logfile, level=level.name, action="done", budget=str(budget))
            print(f"   [{budget}] agent finished ✅")
            return "SUCCESS"

        # safeguard 4: decide how to handle a side-effecting action based on autonomy level
        if level is Level.L1_REPORT:
            # only log; never execute
            print(f"   [{budget}] (L1 dry-run) agent wants to: {action} -- not executing, just logging")
            log_event(logfile, level=level.name, proposed=action, executed=False, budget=str(budget))
        else:
            if level is Level.L2_ASSISTED:
                # in a real scenario this would call input() to ask a human; here we assume approval
                print(f"   [{budget}] (L2) agent wants to: {action} -- [assuming human approved]")
            else:
                print(f"   [{budget}] (L3) agent auto-executing: {action}")
            result = execute(action, workdir)
            log_event(logfile, level=level.name, proposed=action, executed=True,
                      result=result, budget=str(budget))

    # while condition false = budget exhausted -> this is an abort, not a success. Human intervention required.
    print(f"   [{budget}] ⚠️  budget exhausted, escalating to human -- task incomplete, someone needs to look")
    log_event(logfile, level=level.name, action="ESCALATE_budget_exhausted", budget=str(budget))
    return "ESCALATED"


# ===========================================================================
# Demo -- same loop, run once at L1 and once at L3
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    with tempfile.TemporaryDirectory() as workdir:
        logfile = os.path.join(workdir, "run.jsonl")

        print("=" * 64)
        print("Same task: first L1 (report only), then L3 (fully automatic); watch the run-log grow")
        print("=" * 64)

        # L1: dry-run, see what the agent "wants to do" with zero risk
        safe_loop(Level.L1_REPORT, Budget(max_iters=5, max_tokens=1000), logfile, workdir)

        # L3: only after L1 looks fine do we go fully automatic
        safe_loop(Level.L3_UNATTENDED, Budget(max_iters=5, max_tokens=1000), logfile, workdir)

        # Intentionally set a tiny budget to demonstrate "budget exhausted -> escalate"
        print("\n--- Intentionally tiny budget to show 'budget exhausted -> escalate' ---")
        safe_loop(Level.L3_UNATTENDED, Budget(max_iters=1, max_tokens=1000), logfile, workdir)

        print("\n" + "=" * 64)
        print("Contents of run.jsonl (your black box -- read this when things go wrong):")
        print("-" * 64)
        with open(logfile) as f:
            print(f.read().strip())
        print("=" * 64)
        print("Before going live with any loop, confirm: fuse, budget, run-log, start at L1 -- all four in place?")
