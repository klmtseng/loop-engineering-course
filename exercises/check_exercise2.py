"""autograder: Exercise 2 (exit conditions). Usage: python3 check_exercise2.py [--target your_file.py]"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise2_exit_conditions.py")))
g = Grader("Exercise 2 - Exit Conditions")


def make_run_check(plan):
    """Return a stub run_check that emits True/False from plan in order."""
    state = {"i": 0}
    def stub(cmd, cwd):
        ok = plan[min(state["i"], len(plan) - 1)]
        state["i"] += 1
        return ok, ("green" if ok else "red: not correct yet")
    return stub


def make_agent(codes):
    return lambda feedback, attempt: codes[min(attempt, len(codes) - 1)]


def grade():
    with tempfile.TemporaryDirectory() as wd:
        # --- SUCCESS: green on round 3 ---
        mod.agent = make_agent(["a\n", "b\n", "c\n"])
        mod.run_check = make_run_check([False, False, True])
        reason, code = mod.loop("x", wd)
        g.check(reason is mod.Exit.SUCCESS, f"SUCCESS exit: green on round 3 returns SUCCESS (got {reason})")
        g.check(code == "c\n", f"SUCCESS returns the passing code version (got {code!r})")

        # --- FUSE: different each round, never green -> exhausted ---
        mod.agent = make_agent(["a\n", "b\n", "c\n", "d\n", "e\n", "f\n", "g\n"])
        mod.run_check = make_run_check([False])
        reason, code = mod.loop("x", wd)
        g.check(reason is mod.Exit.FUSE, f"FUSE exit: never green and different each round -> exhausted (got {reason})")

        # --- STALL: two consecutive identical outputs -> stop early (should not reach FUSE) ---
        calls = {"n": 0}
        def stalling_check(cmd, cwd):
            calls["n"] += 1
            return False, "red"
        mod.agent = make_agent(["same\n", "same\n", "same\n"])
        mod.run_check = stalling_check
        reason, code = mod.loop("x", wd)
        g.check(reason is mod.Exit.STALL, f"STALL exit: two consecutive identical outputs -> stop (got {reason})")
        g.check(calls["n"] == 1, f"STALL stops early: only round 1 was checked before detecting the stall (run_check called {calls['n']} times, expected 1)")


sys.exit(run(grade, g))
