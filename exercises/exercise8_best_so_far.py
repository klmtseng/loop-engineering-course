"""
練習 8 —— 對抗非決定性:best-so-far loop (對應第 8 課)
======================================================
真 agent 會退步:它可能第 2 圈衝到 95,第 5 圈又掉回 60。一個「只看最後一圈」的 loop
會把好結果丟掉。你要寫一個記住歷史最佳的 loop。

要實作的 best_so_far_loop(agent) 規格,回傳 (status, iters, best):
  - 每圈呼叫 cov = agent(attempt, feedback)(attempt 從 0 起;feedback 隨意)
  - 跨圈維護 best = 目前看過的最大覆蓋率
  - 一旦 best 達標(verify(best) 為真)→ 立刻回 ("SUCCESS", 這是第幾圈, best)
  - 跑完 MAX_ITERS 圈仍未達標 → 回 ("FAIL", MAX_ITERS, best)
    (注意:FAIL 時也要回『歷史最佳』,不是最後一圈的值)

完成後驗收:
    python3 check_exercise8.py
"""

GOAL = 90
MAX_ITERS = 6


def verify(coverage):
    return coverage >= GOAL


def best_so_far_loop(agent):
    # ===================================================================
    # TODO: 跨圈記住歷史最佳;達標就回 SUCCESS,燒完回 FAIL(帶最佳值)
    # ===================================================================
    raise NotImplementedError("實作你的 best_so_far_loop()")
