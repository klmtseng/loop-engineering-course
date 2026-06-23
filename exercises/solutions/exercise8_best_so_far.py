"""練習 8 參考解答。對應第 8 課。"""

GOAL = 90
MAX_ITERS = 6


def verify(coverage):
    return coverage >= GOAL


def best_so_far_loop(agent):
    best = None
    for i in range(1, MAX_ITERS + 1):
        cov = agent(i - 1, feedback=f"目前最佳 {best}")
        if best is None or cov > best:
            best = cov
        if verify(best):
            return ("SUCCESS", i, best)
    return ("FAIL", MAX_ITERS, best)
