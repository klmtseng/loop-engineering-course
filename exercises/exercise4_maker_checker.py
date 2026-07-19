"""
Exercise 4 -- maker / checker (corresponds to Lesson 4)
=========================================================
The maker and loop are provided. You need to implement an independent, strict checker().

Spec for checker(draft) you must implement -- returns (approved, message):
  Three hard criteria, all must pass before approving; list every flaw as feedback:
    1. Must contain an apology word: "sorry" or "apologies"  -> otherwise note "missing apology"
    2. Must contain a clear commitment: draft must include "will"  -> otherwise note "missing commitment"
    3. Length must be <= 60 characters                           -> otherwise note "too long"
  All pass -> return (True, "approve")
  Any flaw -> return (False, "flaw1;flaw2...")

Run the autograder when done:
    python3 check_exercise4.py
"""

MAX_ITERS = 6

_DRAFTS = [
    "We have received your inquiry. Thank you.",
    "Sorry for the trouble -- thank you for your patience.",
    "Sorry for the trouble. We will reply within 24 hours.",
]


def maker(feedback, attempt):
    """[Provided] Stand-in maker. The autograder will replace it."""
    return _DRAFTS[min(attempt, len(_DRAFTS) - 1)]


def checker(draft):
    # ===================================================================
    # TODO: implement an independent, strict checker (see the three hard criteria above)
    # ===================================================================
    raise NotImplementedError("implement your checker()")


def loop(grader):
    """[Provided] maker produces -> grader checks -> on reject, feed the comment back."""
    feedback = "(round 1)"
    for i in range(1, MAX_ITERS + 1):
        draft = maker(feedback, attempt=i - 1)
        approved, comment = grader(draft)
        if approved:
            return draft
        feedback = comment
    return None
