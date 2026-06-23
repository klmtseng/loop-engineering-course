"""
練習 4 —— maker / checker (對應第 4 課)
========================================
maker 和 loop 都給你了。你要實作那個獨立、嚴格的 checker()。

要實作的 checker(draft) 規格,回傳 (是否通過, 訊息):
  三條硬標準,全過才 approve;沒過就把所有缺點列出來當回饋:
    1. 必須含道歉字眼:「抱歉」或「不好意思」  → 否則記「缺少道歉」
    2. 必須含明確下一步:字串裡要有「會」字     → 否則記「沒有承諾下一步」
    3. 長度必須 ≤ 40 字                          → 否則記「太長」
  全過 → return (True, "approve")
  有缺 → return (False, "缺點1;缺點2…")

完成後驗收:
    python3 check_exercise4.py
"""

MAX_ITERS = 6

_DRAFTS = [
    "您的問題我們已經收到了,謝謝。",
    "不好意思造成困擾,謝謝您的耐心等候與體諒。",
    "不好意思造成困擾,我們會在 24 小時內回覆您。",
]


def maker(feedback, attempt):
    """【已給你】替身 maker。autograder 會替換它。"""
    return _DRAFTS[min(attempt, len(_DRAFTS) - 1)]


def checker(draft):
    # ===================================================================
    # TODO: 實作獨立、嚴格的 checker (見檔頭三條硬標準)
    # ===================================================================
    raise NotImplementedError("實作你的 checker()")


def loop(grader):
    """【已給你】maker 做 → grader 驗 → reject 就把意見當回饋丟回。"""
    feedback = "(第一圈)"
    for i in range(1, MAX_ITERS + 1):
        draft = maker(feedback, attempt=i - 1)
        approved, comment = grader(draft)
        if approved:
            return draft
        feedback = comment
    return None
