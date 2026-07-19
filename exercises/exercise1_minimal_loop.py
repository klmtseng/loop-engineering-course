"""
Exercise 1 -- The Minimal Loop (corresponds to Lesson 1)
====================================
The scaffolding (verify, agent) is provided. You only need to implement one function: loop().

Specification for loop(task):
  - Run at most MAX_ITERS rounds
  - Each round: call agent(task, feedback, attempt=i-1) to get a draft
    (i starts at 1; attempt starts at 0)
  - Call verify(draft) to get (passed, feedback)
  - If passed is True -> immediately return that draft (do not run extra rounds)
  - If all rounds exhausted without passing -> return None
  - Use any string like "(first round)" for feedback in the first round

Assessment:
    python3 check_exercise1.py
"""

GOAL_KEYWORD = "save-time"
GOAL_MAXLEN = 20
MAX_ITERS = 5


def verify(draft):
    """[Provided -- do not modify] The verify gate; returns (passed, feedback)."""
    if GOAL_KEYWORD not in draft:
        return False, f"missing keyword '{GOAL_KEYWORD}'"
    if len(draft) > GOAL_MAXLEN:
        return False, f"too long ({len(draft)} chars)"
    return True, "passed"


def agent(task, feedback, attempt):
    """[Provided -- do not modify] Stand-in agent. The autograder will replace this with its own version."""
    drafts = [
        "make your life better and happier every day",
        "save-time and effort, live lighter",
        "save-time every day",
    ]
    return drafts[min(attempt, len(drafts) - 1)]


def loop(task):
    # ===================================================================
    # TODO: implement the act -> verify -> decide loop here (see spec above)
    # ===================================================================
    raise NotImplementedError("Delete this line and implement loop()")
