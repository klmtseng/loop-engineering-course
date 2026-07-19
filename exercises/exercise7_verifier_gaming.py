"""
Exercise 7 -- write a verify that cannot be gamed (corresponds to Lesson 7)
============================================================================
This is the hardest and most important exercise in the course: **verify is the soul of your loop
-- this exercise forces you to write that soul properly.**

A weak verify is provided (it only checks one public case and can be fooled by hard-coding).
You need to write strong_verify():

Spec for strong_verify(add) you must implement:
  - Passes only if add is correct for "public cases + hidden cases + a batch of random inputs"
  - Must catch: hard-coded answer (return 42), off-by-one (a+b+1), constant return (return 0)
  - Hint: checking only public cases is not enough; use HIDDEN_CASES, then add random spot-checks

Run the autograder when done:
    python3 check_exercise7.py
"""

import random

PUBLIC_CASES = [(20, 22, 42)]
HIDDEN_CASES = [(1, 1, 2), (3, 4, 7), (-5, 5, 0)]


def build(code):
    ns = {}
    exec(code, ns)
    return ns["add"]


def weak_verify(add):
    """[Provided, do not change] Only checks one public case -- trivially fooled by hard-coding. Counter-example."""
    return all(add(a, b) == want for a, b, want in PUBLIC_CASES)


def strong_verify(add):
    # ===================================================================
    # TODO: write a verify that cannot be gamed (see spec above: public + hidden + random)
    # ===================================================================
    raise NotImplementedError("implement your strong_verify()")
