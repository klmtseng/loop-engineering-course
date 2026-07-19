"""Reference solution for Exercise 3. Corresponds to Lesson 3."""

import json
import time
from enum import Enum


class Level(Enum):
    L1_REPORT = 1
    L2_ASSISTED = 2
    L3_UNATTENDED = 3


class Budget:
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


def should_execute(level):
    return level is not Level.L1_REPORT


def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


def agent(attempt):
    plan = [("write_file r.md", 120), ("write_file r.md", 90), ("done", 40)]
    return plan[min(attempt, len(plan) - 1)]


def execute(action, workdir):
    return f"executed {action}"


def safe_loop(level, budget, logfile, workdir):
    while budget.can_continue():
        action, tokens = agent(budget.used_iters)
        budget.charge(tokens)
        if action == "done":
            log_event(logfile, action="done")
            return "SUCCESS"
        if should_execute(level):
            result = execute(action, workdir)
            log_event(logfile, proposed=action, executed=True, result=result)
        else:
            log_event(logfile, proposed=action, executed=False)
    log_event(logfile, action="ESCALATE_budget_exhausted")
    return "ESCALATED"
