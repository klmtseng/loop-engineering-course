"""
練習 7 —— 寫一個鑽不動的 verify (對應第 7 課)
==============================================
這是全課最難、也最重要的一題:**verify 是靈魂,這題逼你親手把靈魂寫好。**

弱 verify 已經給你了(它只驗一組公開案例,會被硬編騙過)。你要寫 strong_verify():

要實作的 strong_verify(add) 規格:
  - 通過條件:add 對「公開案例 + 隱藏案例 + 一批隨機輸入」全部都算對才回 True
  - 要能抓出:硬編答案(return 42)、差一點點(a+b+1)、回傳常數(return 0)等作弊/bug
  - 提示:光驗公開案例不夠;用 HIDDEN_CASES,再加 random 抽查幾十組 a+b

完成後驗收:
    python3 check_exercise7.py
"""

import random

PUBLIC_CASES = [(20, 22, 42)]
HIDDEN_CASES = [(1, 1, 2), (3, 4, 7), (-5, 5, 0)]


def build(code):
    ns = {}
    exec(code, ns)
    return ns["add"]


def weak_verify(add):
    """【已給你,不用改】只驗一組公開案例 —— 一眼被硬編騙過的反面教材。"""
    return all(add(a, b) == want for a, b, want in PUBLIC_CASES)


def strong_verify(add):
    # ===================================================================
    # TODO: 寫一個鑽不動的 verify(見檔頭規格:公開+隱藏+隨機都要對)
    # ===================================================================
    raise NotImplementedError("實作你的 strong_verify()")
