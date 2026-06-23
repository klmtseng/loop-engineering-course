"""
progress.py —— 學習進度儀表板
==============================
跑遍全部六課的 autograder + capstone 評分器,一張表看完你過了哪幾關。
這支程式本身就是一個 loop:對你的學習進度跑一輪 verify —— 課程教的東西,我們自己也用。

    python3 progress.py              # 驗收你自己的練習檔(exerciseN_*.py / my_loop.py)
    python3 progress.py --solutions  # 改驗參考解答(想看「全綠長怎樣」時用)
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
USE_SOLUTIONS = "--solutions" in sys.argv

LESSONS = [
    ("第 1 課 · 最小閉環", "exercises/check_exercise1.py", "exercises/solutions/exercise1_minimal_loop.py"),
    ("第 2 課 · 退出條件", "exercises/check_exercise2.py", "exercises/solutions/exercise2_exit_conditions.py"),
    ("第 3 課 · 安全成本", "exercises/check_exercise3.py", "exercises/solutions/exercise3_safety_budget.py"),
    ("第 4 課 · maker/checker", "exercises/check_exercise4.py", "exercises/solutions/exercise4_maker_checker.py"),
    ("第 5 課 · 平行隔離", "exercises/check_exercise5.py", "exercises/solutions/exercise5_parallel_isolation.py"),
    ("第 6 課 · 排程心跳", "exercises/check_exercise6.py", "exercises/solutions/exercise6_scheduling.py"),
    ("第 7 課 · 鑽不動的 verify", "exercises/check_exercise7.py", "exercises/solutions/exercise7_verifier_gaming.py"),
    ("第 8 課 · best-so-far", "exercises/check_exercise8.py", "exercises/solutions/exercise8_best_so_far.py"),
    ("第 9 課 · 上下文策略", "exercises/check_exercise9.py", "exercises/solutions/exercise9_context_strategy.py"),
    ("第 10 課 · loop evals", "exercises/check_exercise10.py", "exercises/solutions/exercise10_loop_evals.py"),
    ("Capstone · 維運 loop", "capstone/grade_capstone.py", "capstone/solution_my_loop.py"),
]


def run_check(checker_rel, solution_rel):
    cmd = [sys.executable, os.path.join(HERE, checker_rel)]
    if USE_SOLUTIONS:
        cmd += ["--target", os.path.join(HERE, solution_rel)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return proc.returncode == 0


def main():
    print("=" * 56)
    print("  Loop Engineering 學習進度" + ("(參考解答模式)" if USE_SOLUTIONS else ""))
    print("=" * 56)
    passed = 0
    for title, checker, solution in LESSONS:
        ok = run_check(checker, solution)
        passed += ok
        print(f"  {'✅ 過關' if ok else '⬜ 待完成'}  {title}")
    print("-" * 56)
    total = len(LESSONS)
    bar = "◉" * passed + "◯" * (total - passed)
    print(f"  進度 [{bar}] {passed}/{total}")
    if passed == total:
        print("  🎓 全數過關!你已經能設計、寫出、驗收一個能放生的 loop。")
    elif passed == 0:
        print("  從第 1 課的練習開始:exercises/exercise1_minimal_loop.py")
    else:
        print("  繼續往下一關前進。卡住就看對應的 textbook 章節與 solutions/。")
    print("=" * 56)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
