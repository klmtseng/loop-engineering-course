"""練習 1 參考解答 —— 卡死再看。對應第 1 課。"""

GOAL_KEYWORD = "省時"
GOAL_MAXLEN = 12
MAX_ITERS = 5


def verify(draft):
    if GOAL_KEYWORD not in draft:
        return False, f"缺少關鍵字「{GOAL_KEYWORD}」"
    if len(draft) > GOAL_MAXLEN:
        return False, f"太長了({len(draft)} 字)"
    return True, "通過"


def agent(task, feedback, attempt):
    drafts = ["讓您的生活更美好更精彩又開心", "省時又省力生活更輕鬆愉快真好", "省時省力好幫手"]
    return drafts[min(attempt, len(drafts) - 1)]


def loop(task):
    feedback = "(第一圈)"
    for i in range(1, MAX_ITERS + 1):
        draft = agent(task, feedback, attempt=i - 1)   # act
        passed, feedback = verify(draft)               # verify
        if passed:                                     # decide
            return draft
    return None
