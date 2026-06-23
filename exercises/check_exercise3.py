"""autograder:練習 3 (安全與成本)。用法:python3 check_exercise3.py [--target 你的檔.py]"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise3_safety_budget.py")))
g = Grader("練習 3 · 安全與成本")


def read_log(path):
    import json
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def grade():
    # --- TODO 1: Budget ---
    b = mod.Budget(max_iters=2, max_tokens=100)
    g.check(b.can_continue() is True, "Budget:剛開始可以繼續")
    b.charge(10)
    g.check(b.used_iters == 1 and b.used_tokens == 10, "Budget.charge:正確累加圈數與 token")
    b.charge(10)
    g.check(b.can_continue() is False, "Budget:圈數到上限就不能繼續")
    b2 = mod.Budget(max_iters=99, max_tokens=50)
    b2.charge(60)
    g.check(b2.can_continue() is False, "Budget:token 超過上限也不能繼續")

    # --- TODO 2: should_execute ---
    g.check(mod.should_execute(mod.Level.L1_REPORT) is False, "should_execute(L1)=False(只報告)")
    g.check(mod.should_execute(mod.Level.L3_UNATTENDED) is True, "should_execute(L3)=True(要執行)")

    # --- 整合:L1 不執行、L3 執行、預算用罄 escalate ---
    with tempfile.TemporaryDirectory() as wd:
        execs = {"n": 0}
        orig = mod.execute
        mod.execute = lambda a, w: execs.__setitem__("n", execs["n"] + 1) or "ok"

        log1 = os.path.join(wd, "l1.jsonl")
        mod.safe_loop(mod.Level.L1_REPORT, mod.Budget(5, 1000), log1, wd)
        g.check(execs["n"] == 0, f"L1 全程沒呼叫 execute(實際 {execs['n']} 次)")
        g.check(all(not e.get("executed", False) for e in read_log(log1)),
                "L1 的 run-log:每筆 executed 都是 False")

        execs["n"] = 0
        log3 = os.path.join(wd, "l3.jsonl")
        mod.safe_loop(mod.Level.L3_UNATTENDED, mod.Budget(5, 1000), log3, wd)
        g.check(execs["n"] >= 1, f"L3 有真的呼叫 execute(實際 {execs['n']} 次)")

        log_tiny = os.path.join(wd, "tiny.jsonl")
        ret = mod.safe_loop(mod.Level.L3_UNATTENDED, mod.Budget(1, 1000), log_tiny, wd)
        g.check(ret == "ESCALATED", f"預算超小 → 回傳 ESCALATED 而非 SUCCESS(得到 {ret!r})")
        mod.execute = orig


sys.exit(run(grade, g))
