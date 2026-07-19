"""autograder: Exercise 10 (loop-level metrics). Usage: python3 check_exercise10.py [--target yourfile.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise10_loop_evals.py")))
g = Grader("Exercise 10 - loop-level metrics")


def grade():
    # Known batch: 2 successes (iters 2 and 4), 2 escalations (each cost 800), total 4 records
    records = [
        {"status": "SUCCESS", "iters": 2, "cost": 200},
        {"status": "SUCCESS", "iters": 4, "cost": 400},
        {"status": "ESCALATED", "iters": 8, "cost": 800},
        {"status": "ESCALATED", "iters": 8, "cost": 800},
    ]
    m = mod.aggregate(records)
    g.check(m["success_rate"] == 0.5, f"success_rate=0.5 (got {m['success_rate']})")
    g.check(m["mean_iters"] == 3.0, f"mean_iters counts only successful runs (2+4)/2=3.0 (got {m['mean_iters']})")
    g.check(m["escalation_rate"] == 0.5, f"escalation_rate=0.5 (got {m['escalation_rate']})")
    g.check(m["mean_cost"] == 550.0, f"mean_cost (200+400+800+800)/4=550.0 (got {m['mean_cost']})")

    # edge case: all escalated -> mean_iters should be 0.0, no divide-by-zero
    allesc = [{"status": "ESCALATED", "iters": 3, "cost": 300}] * 2
    m2 = mod.aggregate(allesc)
    g.check(m2["success_rate"] == 0.0 and m2["mean_iters"] == 0.0,
            f"all escalated: success_rate=0, mean_iters=0, no crash (got {m2['success_rate']},{m2['mean_iters']})")


sys.exit(run(grade, g))
