"""Reference solution for Exercise 1 -- look only when truly stuck. Corresponds to Lesson 1."""

GOAL_KEYWORD = "save-time"
GOAL_MAXLEN = 20
MAX_ITERS = 5


def verify(draft):
    if GOAL_KEYWORD not in draft:
        return False, f"missing keyword '{GOAL_KEYWORD}'"
    if len(draft) > GOAL_MAXLEN:
        return False, f"too long ({len(draft)} chars)"
    return True, "passed"


def agent(task, feedback, attempt):
    drafts = [
        "make your life better and happier every day",
        "save-time and effort, live lighter",
        "save-time every day",
    ]
    return drafts[min(attempt, len(drafts) - 1)]


def loop(task):
    feedback = "(first round)"
    for i in range(1, MAX_ITERS + 1):
        draft = agent(task, feedback, attempt=i - 1)   # act
        passed, feedback = verify(draft)               # verify
        if passed:                                     # decide
            return draft
    return None
