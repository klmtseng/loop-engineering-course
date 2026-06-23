"""
第 10 課 —— loop 級 evals (Evaluating the Loop in Aggregate)
============================================================
前面每一課都在驗「單一任務、單一次」。但「這個 loop 好不好」是另一個問題——
它要對**一整批任務、看整體表現**才答得出來。這是「敢不敢上線」的真憑據。

而且——記得第 8 課嗎?**真 agent 是隨機的**。所以同一個任務,同一個 loop,跑兩次結果可能不同。
這代表:**eval 一個 loop 不能每個任務只跑一次**,否則你量到的是運氣,不是實力。
正確做法是**每個任務重複跑 k 次**,看成功率這個「分佈」,而且要記得標 n(樣本數)。

懂 agent 的人用 eval 思考。一個 loop 的 eval,至少要看四個數字:

    成功率 success_rate     —— 整批 trial 裡,loop 自己搞定的比例
    平均圈數 mean_iters     —— 【僅成功案例】平均跑幾圈(要和 escalation 率併看)
    escalation 率           —— 被迫叫人的比例
    平均成本 mean_cost      —— 每個 trial 平均燒多少 token

執行:
    python3 lesson10_loop_evals.py
    python3 lesson10_loop_evals.py --animate
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim

GOAL = 90
COST_PER_ITER = 100   # 每圈約耗的 token(相對示意,非真實 tokenization)
REPEATS = 20          # 每個任務重複跑幾次(對隨機系統取樣)

# task suite:每個數字是任務的「起始覆蓋率 base」——越高越好解(越容易隨機漫步過 90)
SUITE = [86, 84, 82, 80, 78, 76, 74, 72, 70, 66]


def run_task(base, max_iters, rng):
    """跑一個任務一次(隨機!沿用第 8 課的 noisy 模型 + best-so-far)。
    覆蓋率每圈隨機漫步,best≥GOAL 即 SUCCESS;否則燒到 max_iters 後 escalate。"""
    best = 0
    for i in range(1, max_iters + 1):
        cov = max(0, min(100, round(rng.gauss(base + i * 2.0, 9))))
        best = max(best, cov)
        if best >= GOAL:
            return {"status": "SUCCESS", "iters": i, "cost": i * COST_PER_ITER}
    return {"status": "ESCALATED", "iters": max_iters, "cost": max_iters * COST_PER_ITER}


def aggregate(records):
    """把一批 per-trial 結果彙整成 loop 級指標。"""
    n = len(records)
    succ = [r for r in records if r["status"] == "SUCCESS"]
    esc = [r for r in records if r["status"] == "ESCALATED"]
    return {
        "success_rate": round(len(succ) / n, 2),
        "mean_iters": round(sum(r["iters"] for r in succ) / len(succ), 1) if succ else 0.0,  # 僅成功
        "escalation_rate": round(len(esc) / n, 2),
        "mean_cost": round(sum(r["cost"] for r in records) / n, 1),
    }


def evaluate_loop(suite, max_iters, master_seed):
    """對整個 suite、每個任務重複 REPEATS 次,回傳 (指標, n)。"""
    rng = random.Random(master_seed)
    records = [run_task(base, max_iters, rng) for base in suite for _ in range(REPEATS)]
    return aggregate(records), len(records)


if __name__ == "__main__":
    anim.from_argv()
    n_total = len(SUITE) * REPEATS
    print("=" * 72)
    print(f"對 {len(SUITE)} 個任務、每個重複 {REPEATS} 次(n={n_total} trials),A/B 兩種 loop 設定")
    print("=" * 72)
    print(f"  {'設定':<14}{'成功率(n)':<16}{'平均圈數*':<11}{'escalation':<12}{'平均成本'}")
    print("  " + "-" * 62)
    for max_iters in (3, 8):
        anim.step("→", f"跑 max_iters={max_iters}(每任務 {REPEATS} 次)")
        m, n = evaluate_loop(SUITE, max_iters, master_seed=0)
        print(f"  max_iters={max_iters:<4}{str(m['success_rate'])+f' (n={n})':<16}"
              f"{m['mean_iters']:<11}{m['escalation_rate']:<12}{m['mean_cost']}")
        anim.pause(0.6)
    print("  * 平均圈數僅計『成功案例』;要和 escalation 率併看,否則會把『很快放棄』誤讀成『很有效率』。")

    # 因為是隨機系統,同一個設定換 master seed 會有不同結果 → 報離散度,別只信單點
    print("\n  隨機系統的提醒:同設定換 5 個 seed,success_rate 的範圍")
    for max_iters in (3, 8):
        rates = [evaluate_loop(SUITE, max_iters, master_seed=s)[0]["success_rate"] for s in range(5)]
        print(f"    max_iters={max_iters}:{min(rates)} ~ {max(rates)}(單點估計會落在這個區間裡跳)")

    print("=" * 72)
    print("讀這張表(這就是調 loop 的日常):")
    print("  • max_iters 3 → 8:成功率上升、escalation 下降,但平均成本也上升。沒有最佳解,只有取捨。")
    print("  • 因為 agent 是隨機的(第 8 課),每個任務要重複跑、看分佈、標 n;單跑一次量到的是運氣。")
    print("-" * 72)
    print("心法:單任務 verify 綠了不代表 loop 好。對 task suite 重複取樣量四指標、A/B 設定再決定上線——")
    print("      這正是生態工具 loop-audit / loop-cost 在做的事。")
