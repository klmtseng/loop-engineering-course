"""autograder: Exercise 9 (spec-in-repo context strategy). Usage: python3 check_exercise9.py [--target yourfile.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise9_context_strategy.py")))
g = Grader("Exercise 9 - spec-in-repo context strategy")


def grade():
    # 1. guess = smallest untried number
    _, guess = mod.strat_spec_in_repo([], [])
    g.check(guess == 1, f"empty tried set -> guess 1 (got {guess})")
    _, guess = mod.strat_spec_in_repo([1, 2, 4], ["x", "y", "z"])
    g.check(guess == 3, f"tried 1,2,4 -> guess smallest untried 3 (got {guess})")

    # 2. context must be bounded: ctx does not grow as tried grows
    ctx0, _ = mod.strat_spec_in_repo([], [])
    big_tried = list(range(1, 16))
    ctx_big, _ = mod.strat_spec_in_repo(big_tried, ["m"] * 15)
    g.check(ctx_big == ctx0, f"context is bounded: tried grows but ctx stays the same ({ctx0} vs {ctx_big})")
    g.check(ctx0 == mod.BASE_TOKENS + mod.SPEC_TOKENS, f"ctx = BASE+SPEC (got {ctx0})")

    # 3. run the full loop: should find 13 within bounded context
    tried, history, peak = [], [], 0
    found_at = None
    for i in range(1, 21):
        ctx, gss = mod.strat_spec_in_repo(tried, history)
        peak = max(peak, ctx)
        history.append(gss)
        if gss not in tried:
            tried.append(gss)
        if gss == 13:
            found_at = i
            break
    g.check(found_at is not None, f"finds 13 within 20 rounds (found at round {found_at})")
    g.check(peak <= mod.BASE_TOKENS + mod.SPEC_TOKENS,
            f"peak context throughout is bounded (peak {peak}, limit {mod.BASE_TOKENS + mod.SPEC_TOKENS})")


sys.exit(run(grade, g))
