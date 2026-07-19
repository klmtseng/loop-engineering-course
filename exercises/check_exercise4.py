"""autograder: Exercise 4 (maker/checker). Usage: python3 check_exercise4.py [--target yourfile.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise4_maker_checker.py")))
g = Grader("Exercise 4 - maker/checker")


def grade():
    good = "Sorry for the trouble. We will reply within 24 hours."
    ok, msg = mod.checker(good)
    g.check(ok is True, f"valid reply -> approve (got {ok}, {msg!r})")

    ok, msg = mod.checker("We have received your inquiry. Thank you.")  # no apology, no commitment
    g.check(ok is False and ("apolog" in msg.lower() or "apology" in msg.lower() or "sorry" in msg.lower() or "missing" in msg.lower()),
            f"missing apology -> reject and point it out (got {msg!r})")
    g.check("commit" in msg.lower() or "will" in msg.lower() or "next" in msg.lower() or "step" in msg.lower(),
            f"missing commitment -> reject and point it out (got {msg!r})")

    ok, msg = mod.checker("Sorry, we will handle this" + "x" * 50)  # too long
    g.check(ok is False and "long" in msg.lower(), f"too long -> reject and point it out (got {msg!r})")

    ok, msg = mod.checker("Sorry, we will fix this.")  # has apology, commitment, short enough
    g.check(ok is True, f"apology+commitment+short -> approve (got {ok}, {msg!r})")

    # end-to-end: run the loop with the student's checker; should converge to a valid reply
    result = mod.loop(mod.checker)
    g.check(result is not None and mod.checker(result)[0],
            f"end-to-end: loop converges to a valid reply with your checker (got {result!r})")


sys.exit(run(grade, g))
