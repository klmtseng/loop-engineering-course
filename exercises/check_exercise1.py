"""autograder: Exercise 1 (minimal loop). Usage: python3 check_exercise1.py [--target your_file.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise1_minimal_loop.py")))
g = Grader("Exercise 1 - Minimal Loop")


def grade():
    # --- 1. Success path: return the passing draft at the moment it passes, then stop ---
    #   The "good answer" appears on round 2 and then goes bad again --
    #   this catches a bad loop that returns the last version after running all rounds.
    calls = {"n": 0, "feedbacks": []}

    def stub_progressive(task, feedback, attempt):
        calls["n"] += 1
        calls["feedbacks"].append(feedback)
        if attempt == 1:
            return "save-time helper"          # round 2: passes verify
        return "way too long and has no keyword at all here"   # others: fails (no keyword)

    mod.agent = stub_progressive
    result = mod.loop("t")
    g.check(result == "save-time helper",
            f"success path: return the passing draft immediately (got {result!r}, expected 'save-time helper')")
    g.check(calls["n"] == 2, f"stop on success: no extra rounds after round 2 passes (agent called {calls['n']} times, expected 2)")

    # --- 2. Feedback wired: previous verify message must reach the next agent call ---
    g.check(len(calls["feedbacks"]) >= 2 and "missing" not in calls["feedbacks"][0]
            and ("long" in calls["feedbacks"][1] or "missing" in calls["feedbacks"][1]),
            "feedback wired: verify message from the previous round reaches the agent in the next round")

    # --- 3. Fuse: when it never passes, return None after exactly MAX_ITERS rounds ---
    calls2 = {"n": 0}

    def stub_always_fail(task, feedback, attempt):
        calls2["n"] += 1
        return "this never contains the right keyword ever"

    mod.agent = stub_always_fail
    result2 = mod.loop("t")
    g.check(result2 is None, f"fuse: return None when it never passes (got {result2!r})")
    g.check(calls2["n"] == mod.MAX_ITERS, f"fuse: run exactly {mod.MAX_ITERS} rounds then stop (ran {calls2['n']} rounds)")


sys.exit(run(grade, g))
