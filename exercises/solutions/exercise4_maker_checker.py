"""練習 4 參考解答。對應第 4 課。"""

MAX_ITERS = 6

_DRAFTS = [
    "您的問題我們已經收到了,謝謝。",
    "不好意思造成困擾,謝謝您的耐心等候與體諒。",
    "不好意思造成困擾,我們會在 24 小時內回覆您。",
]


def maker(feedback, attempt):
    return _DRAFTS[min(attempt, len(_DRAFTS) - 1)]


def checker(draft):
    problems = []
    if not any(w in draft for w in ("抱歉", "不好意思")):
        problems.append("缺少道歉字眼")
    if "會" not in draft:
        problems.append("沒有承諾下一步")
    if len(draft) > 40:
        problems.append(f"太長({len(draft)} 字)")
    if problems:
        return False, ";".join(problems)
    return True, "approve"


def loop(grader):
    feedback = "(第一圈)"
    for i in range(1, MAX_ITERS + 1):
        draft = maker(feedback, attempt=i - 1)
        approved, comment = grader(draft)
        if approved:
            return draft
        feedback = comment
    return None
