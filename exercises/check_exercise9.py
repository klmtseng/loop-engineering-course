"""autograder:練習 9 (spec-in-repo 上下文策略)。用法:python3 check_exercise9.py [--target 你的檔.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise9_context_strategy.py")))
g = Grader("練習 9 · spec-in-repo 上下文策略")


def grade():
    # 1. guess = 最小未試數字
    _, guess = mod.strat_spec_in_repo([], [])
    g.check(guess == 1, f"空集合 → 猜 1(得到 {guess})")
    _, guess = mod.strat_spec_in_repo([1, 2, 4], ["x", "y", "z"])
    g.check(guess == 3, f"已試 1,2,4 → 猜最小未試 3(得到 {guess})")

    # 2. context 必須有界:tried 大小從 0 變大,ctx 不能跟著變大
    ctx0, _ = mod.strat_spec_in_repo([], [])
    big_tried = list(range(1, 16))
    ctx_big, _ = mod.strat_spec_in_repo(big_tried, ["m"] * 15)
    g.check(ctx_big == ctx0, f"context 有界:tried 變大但 ctx 不變({ctx0} vs {ctx_big})")
    g.check(ctx0 == mod.BASE_TOKENS + mod.SPEC_TOKENS, f"ctx = BASE+SPEC(得到 {ctx0})")

    # 3. 跑整個 loop:應在有界 context 下猜中 13
    tried, history, peak = [], [], 0
    found_at = None
    for i in range(1, 21):
        ctx, gss = mod.strat_spec_in_repo(tried, history)
        peak = max(peak, ctx)
        history.append(gss)
        if gss not in tried:
            tried.append(gss)
        if gss == 13:
            found_at = i
            break
    g.check(found_at is not None, f"在 20 圈內猜中 13(第 {found_at} 圈)")
    g.check(peak <= mod.BASE_TOKENS + mod.SPEC_TOKENS,
            f"全程 context 峰值有界(峰值 {peak},上限 {mod.BASE_TOKENS + mod.SPEC_TOKENS})")


sys.exit(run(grade, g))
