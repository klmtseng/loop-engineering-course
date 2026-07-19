"""
Exercise 3 -- Safety and Cost (corresponds to Lesson 3)
====================================
You need to fill in two key components; the rest of the scaffolding
(safe_loop, log_event, agent, execute) is provided.

TODO 1 -- Two methods on the Budget class:
    can_continue() -> True only if BOTH iterations AND tokens are still under their caps
    charge(tokens) -> consume one iteration and accumulate tokens

TODO 2 -- should_execute(level):
    L1_REPORT -> False (report only, never execute)
    anything else (L2/L3) -> True

Assessment:
    python3 check_exercise3.py
"""

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
        # TODO 1a: return True only when both iterations and tokens are still under their caps
        raise NotImplementedError("implement can_continue()")

    def charge(self, tokens):
        # TODO 1b: consume one iteration and accumulate tokens
        raise NotImplementedError("implement charge()")


def should_execute(level):
    # TODO 2: L1 only reports (False); everything else executes (True)
    raise NotImplementedError("implement should_execute()")


# ---- The following is [Provided] -- it uses the two TODOs above ----
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
