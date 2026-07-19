"""
Capstone template -- copy to my_loop.py and implement. See SPEC.md for details.
Implement all six requirements, then run `python3 grade_capstone.py` to verify.
"""

import json
import sys
import time


# ---- The grader provides this kind of world; this World is for your own --once runs ----
class World:
    def __init__(self, todos):
        self.todos = list(todos)
        self.done = []
        self.escalated = []
        self.executed = 0   # increment by 1 each time you actually execute a side effect


# ===== Requirement 1: Fuse + Budget =====
class Budget:
    def __init__(self, max_iters, max_tokens):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.used_iters = 0
        self.used_tokens = 0

    def can_continue(self):
        raise NotImplementedError  # TODO

    def charge(self, tokens):
        raise NotImplementedError  # TODO


# ===== Requirement 2: run-log =====
def log_event(logfile, **fields):
    raise NotImplementedError  # TODO: append one JSONL line, never overwrite


# ===== Requirement 3: independent checker =====
def checker(task, result):
    raise NotImplementedError  # TODO: True for good results, False for bad results


# ===== Requirement 6 (half): isolation =====
def worker_dir(base, name):
    raise NotImplementedError  # TODO: return a distinct path under base for each name


# ---- Per-task agent, used by your run() via solve_task (adjust as needed) ----
def task_agent(task):
    """Returns a coverage value. deploy* high-risk tasks never reach GOAL -> escalated; others succeed."""
    return (lambda attempt: 50) if task.startswith("deploy") else (lambda attempt: 95)


# ===== Requirements 4 + 5 (integrates Req 7): main loop =====
def run(world, logfile, budget, level="L3"):
    """Handle world.todos one by one: process each task via solve_task(task_agent(task), ...) (this is how best-so-far actually runs),
    SUCCESS -> done, FAIL -> escalate, log each; escalate when budget exhausted.
    When level == "L1", do not actually execute side effects (world.executed stays at 0).
    Returns dict: {"done": n, "escalated": n, "budget_exhausted": bool}."""
    raise NotImplementedError  # TODO (remember to call solve_task, do not bypass Req 7)


# ===== Requirement 7: robust against regressing noisy agents (best-so-far, from Lesson 8) =====
GOAL = 90


def solve_task(agent, max_iters):
    """agent(attempt) returns a coverage value (int). Track historical best each round;
    return ("SUCCESS", best) when best >= GOAL; return ("FAIL", best) when fuse burns out.
    Real agents regress -- do not trust only the last round."""
    raise NotImplementedError  # TODO


# ===== Requirement 6 (other half): scheduling =====
if __name__ == "__main__":
    once = "--once" in sys.argv
    # TODO: with --once, run one tick (handle one todo) then exit cleanly
    raise NotImplementedError
