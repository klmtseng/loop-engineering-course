"""
練習 10 —— loop 級指標 aggregate (對應第 10 課)
================================================
run_task 給你了。你要實作 aggregate():把一批 per-task 結果彙整成 loop 級的四個指標。

要實作的 aggregate(records) 規格,records 是 [{status, iters, cost}, ...],回傳 dict:
  - success_rate   :SUCCESS 筆數 / 總筆數,round 到小數 2 位
  - mean_iters     :只在 SUCCESS 的 iters 取平均,round 到小數 1 位(沒有 SUCCESS 則 0.0)
  - escalation_rate:ESCALATED 筆數 / 總筆數,round 到小數 2 位
  - mean_cost      :所有筆數的 cost 取平均,round 到小數 1 位

完成後驗收:
    python3 check_exercise10.py
"""

COST_PER_ITER = 100


def run_task(difficulty, max_iters):
    """【已給你】難度 difficulty 圈內解得開就 SUCCESS,否則 escalate。"""
    if difficulty <= max_iters:
        return {"status": "SUCCESS", "iters": difficulty, "cost": difficulty * COST_PER_ITER}
    return {"status": "ESCALATED", "iters": max_iters, "cost": max_iters * COST_PER_ITER}


def aggregate(records):
    # ===================================================================
    # TODO: 回傳 {success_rate, mean_iters, escalation_rate, mean_cost}(見檔頭規格)
    # ===================================================================
    raise NotImplementedError("實作你的 aggregate()")
