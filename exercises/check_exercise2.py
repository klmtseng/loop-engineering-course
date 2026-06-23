"""autograder:練習 2 (退出條件)。用法:python3 check_exercise2.py [--target 你的檔.py]"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise2_exit_conditions.py")))
g = Grader("練習 2 · 退出條件")


def make_run_check(plan):
    """回傳一個 stub run_check,依呼叫次數吐 plan 裡的 True/False。"""
    state = {"i": 0}
    def stub(cmd, cwd):
        ok = plan[min(state["i"], len(plan) - 1)]
        state["i"] += 1
        return ok, ("綠" if ok else "紅:還沒對")
    return stub


def make_agent(codes):
    return lambda feedback, attempt: codes[min(attempt, len(codes) - 1)]


def grade():
    with tempfile.TemporaryDirectory() as wd:
        # --- SUCCESS:第 3 圈才綠 ---
        mod.agent = make_agent(["a\n", "b\n", "c\n"])
        mod.run_check = make_run_check([False, False, True])
        reason, code = mod.loop("x", wd)
        g.check(reason is mod.Exit.SUCCESS, f"SUCCESS 出口:第 3 圈綠了就回 SUCCESS(得到 {reason})")
        g.check(code == "c\n", f"SUCCESS 時回傳通過的那版程式碼(得到 {code!r})")

        # --- FUSE:每圈不同、永遠不綠 → 燒完 ---
        mod.agent = make_agent(["a\n", "b\n", "c\n", "d\n", "e\n", "f\n", "g\n"])
        mod.run_check = make_run_check([False])
        reason, code = mod.loop("x", wd)
        g.check(reason is mod.Exit.FUSE, f"FUSE 出口:永遠不綠且每圈不同 → 燒完(得到 {reason})")

        # --- STALL:連續兩圈相同 → 提早止血 (不應燒到 FUSE) ---
        calls = {"n": 0}
        def stalling_check(cmd, cwd):
            calls["n"] += 1
            return False, "紅"
        mod.agent = make_agent(["same\n", "same\n", "same\n"])
        mod.run_check = stalling_check
        reason, code = mod.loop("x", wd)
        g.check(reason is mod.Exit.STALL, f"STALL 出口:連續兩圈相同就停(得到 {reason})")
        g.check(calls["n"] == 1, f"STALL 是提早止血:只驗了第 1 圈就發現卡住(run_check 被呼叫 {calls['n']} 次,應為 1)")


sys.exit(run(grade, g))
