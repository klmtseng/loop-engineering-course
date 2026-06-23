"""autograder:練習 8 (best-so-far loop)。用法:python3 check_exercise8.py [--target 你的檔.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise8_best_so_far.py")))
g = Grader("練習 8 · best-so-far loop")


def seq_agent(values):
    """確定性注入 agent:依 attempt 回固定序列(不靠隨機,評分才穩定)。"""
    return lambda attempt, feedback: values[min(attempt, len(values) - 1)]


def grade():
    # 1. 中途達標、末圈退步:best-so-far 要記得最佳並 SUCCESS,而非被末圈拖累
    status, iters, best = mod.best_so_far_loop(seq_agent([50, 95, 60, 70, 65, 55]))
    g.check(status == "SUCCESS", f"中途衝高、末圈退步 → 仍判 SUCCESS(得到 {status})")
    g.check(best == 95, f"回傳的是歷史最佳 95,而非末圈 55(得到 {best})")
    g.check(iters == 2, f"第 2 圈一達標就收工(得到第 {iters} 圈)")

    # 2. 第一圈就最高、之後一路退步:仍要 SUCCESS 且記得 95
    status, iters, best = mod.best_so_far_loop(seq_agent([95, 50, 50, 50, 50, 50]))
    g.check(status == "SUCCESS" and best == 95 and iters == 1,
            f"首圈達標即收工、記得 95(得到 {status},{best},第 {iters} 圈)")

    # 3. 從未達標:FAIL,且回傳『歷史最佳』而不是最後一圈
    status, iters, best = mod.best_so_far_loop(seq_agent([88, 85, 80, 70, 60, 50]))
    g.check(status == "FAIL", f"從未達 90 → FAIL(得到 {status})")
    g.check(best == 88, f"FAIL 時也回歷史最佳 88,而非末圈 50(得到 {best})")


sys.exit(run(grade, g))
