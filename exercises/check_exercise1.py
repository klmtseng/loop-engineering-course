"""autograder:練習 1 (最小閉環)。用法:python3 check_exercise1.py [--target 你的檔.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise1_minimal_loop.py")))
g = Grader("練習 1 · 最小閉環")


def grade():
    # --- 1. 成功時:回傳通過 verify 的 draft,且達標就停 ---
    #   刻意讓「合格答案」出現在第 2 圈、之後又變回不合格 ——
    #   這樣「跑完才回最後一版」的壞 loop 會抓到不合格的草稿,瞞不過去。
    calls = {"n": 0, "feedbacks": []}

    def stub_progressive(task, feedback, attempt):
        calls["n"] += 1
        calls["feedbacks"].append(feedback)
        if attempt == 1:
            return "省時好幫手"            # 第 2 圈:合格
        return "太長太長太長太長太長太長"   # 其餘:不合格(無關鍵字)

    mod.agent = stub_progressive
    result = mod.loop("t")
    g.check(result == "省時好幫手",
            f"成功路徑:達標當下就回傳那一版合格成品(得到 {result!r},應為「省時好幫手」)")
    g.check(calls["n"] == 2, f"達標就停:第 2 圈過關後不再多跑(實際呼叫 agent {calls['n']} 次,應為 2)")

    # --- 2. 回饋有接線:上一圈 verify 的訊息要餵進下一圈 ---
    g.check(len(calls["feedbacks"]) >= 2 and "缺少" not in calls["feedbacks"][0]
            and ("太長" in calls["feedbacks"][1] or "缺少" in calls["feedbacks"][1]),
            "回饋接線:上一圈 verify 的訊息有餵進下一圈的 agent")

    # --- 3. 保險絲:永遠不過時,回傳 None 且剛好燒滿 MAX_ITERS 圈 ---
    calls2 = {"n": 0}

    def stub_always_fail(task, feedback, attempt):
        calls2["n"] += 1
        return "永遠太長永遠太長永遠太長永遠"

    mod.agent = stub_always_fail
    result2 = mod.loop("t")
    g.check(result2 is None, f"保險絲:永遠驗不過時回傳 None(得到 {result2!r})")
    g.check(calls2["n"] == mod.MAX_ITERS, f"保險絲:剛好跑滿 {mod.MAX_ITERS} 圈才停(實際 {calls2['n']} 圈)")


sys.exit(run(grade, g))
