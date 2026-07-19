"""
Exercise 9 -- spec-in-repo context strategy (corresponds to Lesson 9)
======================================================================
stateless (no memory) and conversation (exploding context) are provided as baselines.
You need to implement the production-grade spec-in-repo strategy:
fresh context every round plus a concise spec, giving you memory with bounded context.

Spec for strat_spec_in_repo(tried, history) you must implement -- returns (ctx_tokens, guess):
  - ctx_tokens must be BOUNDED: = BASE_TOKENS + SPEC_TOKENS, must NOT grow with history/tried
  - guess = the smallest number in UNIVERSE (1..20) that has NOT been tried yet
    (use the tried set to avoid repeating guesses)

Run the autograder when done:
    python3 check_exercise9.py
"""

UNIVERSE = list(range(1, 21))
BASE_TOKENS = 30
MSG_TOKENS = 12
SPEC_TOKENS = 8


def strat_stateless(tried, history):
    """[Baseline, do not change] No memory: cheapest context but gets stuck in a loop."""
    return BASE_TOKENS, (len(history) % 5) + 1


def strat_conversation(tried, history):
    """[Baseline, do not change] Remembers everything, but context grows every round."""
    return BASE_TOKENS + len(history) * MSG_TOKENS, next(n for n in UNIVERSE if n not in tried)


def strat_spec_in_repo(tried, history):
    # ===================================================================
    # TODO: return (bounded ctx_tokens, smallest untried number)
    # ===================================================================
    raise NotImplementedError("implement your strat_spec_in_repo()")
