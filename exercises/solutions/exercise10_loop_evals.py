"""練習 10 參考解答。對應第 10 課。"""

COST_PER_ITER = 100


def run_task(difficulty, max_iters):
    if difficulty <= max_iters:
        return {"status": "SUCCESS", "iters": difficulty, "cost": difficulty * COST_PER_ITER}
    return {"status": "ESCALATED", "iters": max_iters, "cost": max_iters * COST_PER_ITER}


def aggregate(records):
    n = len(records)
    succ = [r for r in records if r["status"] == "SUCCESS"]
    esc = [r for r in records if r["status"] == "ESCALATED"]
    return {
        "success_rate": round(len(succ) / n, 2),
        "mean_iters": round(sum(r["iters"] for r in succ) / len(succ), 1) if succ else 0.0,
        "escalation_rate": round(len(esc) / n, 2),
        "mean_cost": round(sum(r["cost"] for r in records) / n, 1),
    }
