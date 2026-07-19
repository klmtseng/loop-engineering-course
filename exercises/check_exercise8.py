"""autograder: Exercise 8 (best-so-far loop). Usage: python3 check_exercise8.py [--target yourfile.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise8_best_so_far.py")))
g = Grader("Exercise 8 - best-so-far loop")


def seq_agent(values):
    """Deterministic injection agent: returns a fixed sequence by attempt (stable grading, no randomness)."""
    return lambda attempt, feedback: values[min(attempt, len(values) - 1)]


def grade():
    # 1. Peaks mid-run then regresses: best-so-far must remember the peak and report SUCCESS
    status, iters, best = mod.best_so_far_loop(seq_agent([50, 95, 60, 70, 65, 55]))
    g.check(status == "SUCCESS", f"peaks mid-run, regresses at end -> still SUCCESS (got {status})")
    g.check(best == 95, f"returns historical best 95, not last-round 55 (got {best})")
    g.check(iters == 2, f"stops as soon as goal is met in round 2 (got round {iters})")

    # 2. First round is the highest, all subsequent rounds regress: still SUCCESS and remembers 95
    status, iters, best = mod.best_so_far_loop(seq_agent([95, 50, 50, 50, 50, 50]))
    g.check(status == "SUCCESS" and best == 95 and iters == 1,
            f"first round meets goal, stop immediately, remember 95 (got {status},{best},round {iters})")

    # 3. Never meets goal: FAIL, return historical best not last round
    status, iters, best = mod.best_so_far_loop(seq_agent([88, 85, 80, 70, 60, 50]))
    g.check(status == "FAIL", f"never reaches 90 -> FAIL (got {status})")
    g.check(best == 88, f"on FAIL, return historical best 88, not last-round 50 (got {best})")


sys.exit(run(grade, g))
