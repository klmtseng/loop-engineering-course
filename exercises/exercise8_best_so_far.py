"""
Exercise 8 -- handling non-determinism: best-so-far loop (corresponds to Lesson 8)
====================================================================================
Real agents regress: they may hit 95 in round 2 then drop back to 60 in round 5.
A loop that "only looks at the last round" throws away good intermediate results.
You need to write a loop that remembers the historical best.

Spec for best_so_far_loop(agent) you must implement -- returns (status, iters, best):
  - Each round call cov = agent(attempt, feedback) (attempt starts at 0; feedback is up to you)
  - Maintain best = the maximum coverage seen so far across rounds
  - Once best meets the goal (verify(best) is True) -> immediately return ("SUCCESS", round_number, best)
  - After MAX_ITERS rounds without meeting the goal -> return ("FAIL", MAX_ITERS, best)
    (note: on FAIL, return the historical best, not the last round's value)

Run the autograder when done:
    python3 check_exercise8.py
"""

GOAL = 90
MAX_ITERS = 6


def verify(coverage):
    return coverage >= GOAL


def best_so_far_loop(agent):
    # ===================================================================
    # TODO: track historical best across rounds; return SUCCESS when goal is met, FAIL with best when fuse burns
    # ===================================================================
    raise NotImplementedError("implement your best_so_far_loop()")
