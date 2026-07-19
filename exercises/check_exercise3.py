"""autograder: Exercise 3 (safety and cost). Usage: python3 check_exercise3.py [--target your_file.py]"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise3_safety_budget.py")))
g = Grader("Exercise 3 - Safety and Cost")


def read_log(path):
    import json
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def grade():
    # --- TODO 1: Budget ---
    b = mod.Budget(max_iters=2, max_tokens=100)
    g.check(b.can_continue() is True, "Budget: can_continue() is True at the start")
    b.charge(10)
    g.check(b.used_iters == 1 and b.used_tokens == 10, "Budget.charge: correctly accumulates iter count and tokens")
    b.charge(10)
    g.check(b.can_continue() is False, "Budget: can_continue() is False when iteration cap is reached")
    b2 = mod.Budget(max_iters=99, max_tokens=50)
    b2.charge(60)
    g.check(b2.can_continue() is False, "Budget: can_continue() is False when token cap is exceeded")

    # --- TODO 2: should_execute ---
    g.check(mod.should_execute(mod.Level.L1_REPORT) is False, "should_execute(L1) = False (report only)")
    g.check(mod.should_execute(mod.Level.L3_UNATTENDED) is True, "should_execute(L3) = True (execute)")

    # --- Integration: L1 does not execute, L3 does, budget exhaustion escalates ---
    with tempfile.TemporaryDirectory() as wd:
        execs = {"n": 0}
        orig = mod.execute
        mod.execute = lambda a, w: execs.__setitem__("n", execs["n"] + 1) or "ok"

        log1 = os.path.join(wd, "l1.jsonl")
        mod.safe_loop(mod.Level.L1_REPORT, mod.Budget(5, 1000), log1, wd)
        g.check(execs["n"] == 0, f"L1 never calls execute (called {execs['n']} times)")
        g.check(all(not e.get("executed", False) for e in read_log(log1)),
                "L1 run-log: every entry has executed=False")

        execs["n"] = 0
        log3 = os.path.join(wd, "l3.jsonl")
        mod.safe_loop(mod.Level.L3_UNATTENDED, mod.Budget(5, 1000), log3, wd)
        g.check(execs["n"] >= 1, f"L3 does call execute (called {execs['n']} times)")

        log_tiny = os.path.join(wd, "tiny.jsonl")
        ret = mod.safe_loop(mod.Level.L3_UNATTENDED, mod.Budget(1, 1000), log_tiny, wd)
        g.check(ret == "ESCALATED", f"tiny budget -> returns ESCALATED not SUCCESS (got {ret!r})")
        mod.execute = orig


sys.exit(run(grade, g))
