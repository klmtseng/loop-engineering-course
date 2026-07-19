"""Exercise 4 reference solution. Corresponds to Lesson 4."""

MAX_ITERS = 6

_DRAFTS = [
    "We have received your inquiry. Thank you.",
    "Sorry for the trouble -- thank you for your patience.",
    "Sorry for the trouble. We will reply within 24 hours.",
]


def maker(feedback, attempt):
    return _DRAFTS[min(attempt, len(_DRAFTS) - 1)]


def checker(draft):
    problems = []
    if not any(w in draft.lower() for w in ("sorry", "apologies")):
        problems.append("missing apology")
    if "will" not in draft.lower():
        problems.append("missing commitment")
    if len(draft) > 40:
        problems.append(f"too long ({len(draft)} chars)")
    if problems:
        return False, ";".join(problems)
    return True, "approve"


def loop(grader):
    feedback = "(round 1)"
    for i in range(1, MAX_ITERS + 1):
        draft = maker(feedback, attempt=i - 1)
        approved, comment = grader(draft)
        if approved:
            return draft
        feedback = comment
    return None
