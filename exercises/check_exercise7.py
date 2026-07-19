"""autograder: Exercise 7 (ungameable verify). Usage: python3 check_exercise7.py [--target yourfile.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise7_verifier_gaming.py")))
g = Grader("Exercise 7 - ungameable verify")


def grade():
    honest = mod.build("def add(a, b):\n    return a + b")
    hardcode = mod.build("def add(a, b):\n    return 42")
    offbyone = mod.build("def add(a, b):\n    return a + b + 1")
    constant = mod.build("def add(a, b):\n    return 0")

    g.check(mod.strong_verify(honest) is True, "pass the honest add(a,b)=a+b")
    g.check(mod.strong_verify(hardcode) is False, "catch hard-coded return 42")
    g.check(mod.strong_verify(offbyone) is False, "catch a+b+1 bug")
    g.check(mod.strong_verify(constant) is False, "catch constant return 0")

    # sanity check: weak verify is indeed fooled by hard-coding (that's why we need strong)
    g.check(mod.weak_verify(hardcode) is True,
            "(sanity) weak verify is indeed fooled by return 42 -> that's why strong_verify is needed")


sys.exit(run(grade, g))
