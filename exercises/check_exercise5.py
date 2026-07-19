"""autograder: Exercise 5 (parallelism and isolation). Usage: python3 check_exercise5.py [--target yourfile.py]"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise5_parallel_isolation.py")))
g = Grader("Exercise 5 - parallelism and isolation")


def grade():
    workers = ["A", "B", "C"]
    with tempfile.TemporaryDirectory() as base:
        results = mod.run_isolated(workers, base)

        g.check(isinstance(results, dict) and set(results) == set(workers),
                f"returns dict covering all workers (got keys={list(results) if isinstance(results, dict) else results})")

        # isolation proof: each worker's content can only contain its own lines, exactly 3
        all_clean = True
        for w in workers:
            lines = results.get(w, "").strip().split("\n")
            clean = len(lines) == 3 and all(ln.startswith(w + " ") for ln in lines)
            if not clean:
                all_clean = False
            g.check(clean, f"{w}'s output is clean: 3 lines all belonging to itself (got {results.get(w)!r})")
        g.check(all_clean, "overall isolation success: no worker's file was contaminated by another")


sys.exit(run(grade, g))
