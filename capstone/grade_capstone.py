"""
Capstone 評分器。驗收六項要件(見 SPEC.md)。逐要件評分:做對 ✅、做錯 ❌、還沒做 ⬜,
任何一項沒實作都不會中止其他要件——你隨時看得到自己的部分進度。
用法:
    python3 grade_capstone.py                          # 驗 my_loop.py
    python3 grade_capstone.py --target solution_my_loop.py
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "exercises"))
from _grader_utils import Grader, load, requirement, target_path  # noqa: E402

tpath = target_path(os.path.join(HERE, "my_loop.py"))
mod = load(tpath, name="capstone_module",
           missing_hint="capstone 請先:cp my_loop_template.py my_loop.py,再實作裡面的 TODO")
g = Grader("Capstone · 能放生的維運 loop")


def r1_budget():
    b = mod.Budget(2, 100)
    b.charge(10)
    g.check(b.can_continue() is True, "[要件1] Budget 還有額度時可繼續")
    b.charge(10)
    g.check(b.can_continue() is False, "[要件1] 圈數到頂就停")
    b2 = mod.Budget(99, 50); b2.charge(60)
    g.check(b2.can_continue() is False, "[要件1] token 到頂也停")


def r2_runlog():
    with tempfile.TemporaryDirectory() as wd:
        lf = os.path.join(wd, "r.jsonl")
        mod.log_event(lf, event="a")
        mod.log_event(lf, event="b")
        lines = [l for l in open(lf) if l.strip()]
        g.check(len(lines) == 2, f"[要件2] run-log append 兩行不覆蓋(實際 {len(lines)} 行)")


def r3_checker():
    g.check(mod.checker("t", "已完成 [t]") is True, "[要件3] checker 認可好結果")
    g.check(mod.checker("t", None) is False, "[要件3] checker 擋下壞結果")


def r6a_isolation():
    base = "/tmp/cap_base"
    da, db = mod.worker_dir(base, "A"), mod.worker_dir(base, "B")
    g.check(da != db and da.startswith(base) and db.startswith(base),
            f"[要件6] worker_dir 每 worker 互異且在 base 下({da} / {db})")


def r4_mainloop():
    with tempfile.TemporaryDirectory() as wd:
        # 整合檢查:run() 必須真的呼叫 solve_task(別繞過要件 7 自己另寫一套)
        spy = {"n": 0}
        orig = mod.solve_task
        def wrapped(agent, max_iters):
            spy["n"] += 1
            return orig(agent, max_iters)
        mod.solve_task = wrapped
        w0 = mod.World(["triage #0"])
        mod.run(w0, os.path.join(wd, "l0.jsonl"), mod.Budget(99, 10000), level="L3")
        mod.solve_task = orig
        g.check(spy["n"] >= 1, f"[要件4] run() 確實透過 solve_task 處理任務(整合,呼叫 {spy['n']} 次)")

        w = mod.World(["triage #1", "deploy v2", "triage #2"])
        s = mod.run(w, os.path.join(wd, "l.jsonl"), mod.Budget(99, 10000), level="L3")
        g.check(s["done"] == 2, f"[要件4] 兩件一般任務完成(done={s['done']})")
        g.check(s["escalated"] == 1, f"[要件4] deploy 被 escalate(escalated={s['escalated']})")
        g.check(s["budget_exhausted"] is False, "[要件4] 額度夠時 budget_exhausted=False")
        w2 = mod.World(["a", "b", "c", "d"])
        s2 = mod.run(w2, os.path.join(wd, "l2.jsonl"), mod.Budget(1, 10000), level="L3")
        g.check(s2["budget_exhausted"] is True, "[要件4] 預算超小 → budget_exhausted=True")
        g.check(s2["done"] < 4, "[要件4] 預算用罄時沒做完全部")


def r5_l1safety():
    with tempfile.TemporaryDirectory() as wd:
        w3 = mod.World(["triage #1", "triage #2"])
        mod.run(w3, os.path.join(wd, "l3.jsonl"), mod.Budget(99, 10000), level="L1")
        g.check(w3.executed == 0, f"[要件5] L1 全程不執行副作用(world.executed={w3.executed})")


def r6b_schedule():
    proc = subprocess.run([sys.executable, os.path.abspath(tpath), "--once"],
                          capture_output=True, text=True, timeout=30)
    g.check(proc.returncode == 0, f"[要件6] `--once` 跑一拍後乾淨退出(exit={proc.returncode})")


def r7_robust():
    seq = lambda vals: (lambda attempt: vals[min(attempt, len(vals) - 1)])
    # 中途衝到 95、末圈退步到 50:best-so-far 要記得 95
    status, best = mod.solve_task(seq([50, 95, 50, 50]), 4)
    g.check(status == "SUCCESS" and best == 95,
            f"[要件7] noisy agent 退步時仍回歷史最佳 95(得到 {status},{best})")
    # 從未達標:FAIL 且回最佳(88)而非末圈
    status, best = mod.solve_task(seq([88, 70, 60, 50]), 4)
    g.check(status == "FAIL" and best == 88,
            f"[要件7] 從未達標 → FAIL 且回最佳 88,非末圈(得到 {status},{best})")


# 逐要件跑:任一要件未實作只標 ⬜,不影響其他要件的評分
requirement(g, "要件1 · 保險絲+預算", r1_budget)
requirement(g, "要件2 · run-log", r2_runlog)
requirement(g, "要件3 · 獨立 checker", r3_checker)
requirement(g, "要件6(隔離)· worker_dir", r6a_isolation)
requirement(g, "要件4 · 主迴圈", r4_mainloop)
requirement(g, "要件5 · L1 安全", r5_l1safety)
requirement(g, "要件6(排程)· --once", r6b_schedule)
requirement(g, "要件7 · 對 noisy agent 穩健", r7_robust)

sys.exit(g.report())
