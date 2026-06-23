"""
練習 1 —— 最小的閉環 (對應第 1 課)
====================================
鷹架(verify、agent)都給你了。你只要實作一個函式:loop()。

要實作的 loop(task) 規格:
  - 最多跑 MAX_ITERS 圈
  - 每圈呼叫 agent(task, feedback, attempt=i-1) 取得一個 draft
    (i 從 1 開始;attempt 從 0 開始)
  - 用 verify(draft) 取得 (passed, feedback)
  - 一旦 passed 為真 → 立刻回傳該 draft (不要多跑)
  - 圈數燒完都沒過 → 回傳 None
  - 第一圈的 feedback 用 "(第一圈)" 這類字串即可

完成後驗收:
    python3 check_exercise1.py
"""

GOAL_KEYWORD = "省時"
GOAL_MAXLEN = 12
MAX_ITERS = 5


def verify(draft):
    """【已給你,不用改】驗證閘門,回傳 (是否通過, 回饋)。"""
    if GOAL_KEYWORD not in draft:
        return False, f"缺少關鍵字「{GOAL_KEYWORD}」"
    if len(draft) > GOAL_MAXLEN:
        return False, f"太長了({len(draft)} 字)"
    return True, "通過"


def agent(task, feedback, attempt):
    """【已給你,不用改】替身 agent。autograder 會用自己的版本替換它。"""
    drafts = ["讓您的生活更美好更精彩又開心", "省時又省力生活更輕鬆愉快真好", "省時省力好幫手"]
    return drafts[min(attempt, len(drafts) - 1)]


def loop(task):
    # ===================================================================
    # TODO: 在這裡實作 act → verify → decide 迴圈 (見檔頭規格)
    # ===================================================================
    raise NotImplementedError("把這行刪掉,實作你的 loop()")
