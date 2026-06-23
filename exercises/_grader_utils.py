"""
_grader_utils.py —— autograder 的共用零件
==========================================
每個 check_exerciseN.py(與 capstone 的 grade_capstone.py)都靠這幾件事:
  1. load(path)        把學生的檔當模組載進來 (不管它在哪)
  2. Grader            收集一條條 assert,最後印 計分卡(✅ 過 / ❌ 錯 / ⬜ 待完成)
  3. run / requirement 把「還沒實作的 TODO」轉成友善訊息,而不是醜 traceback

設計重點:autograder 自己就是一個 verify 閘門 —— 它 import 學生 expose 的函式、
餵受控輸入、逐項斷言行為,不解析 stdout (脆弱)。這正是本課教的「驗收要客觀」。
"""

import importlib.util
import os
import sys


def load(path, name="student_module", missing_hint=None):
    """把任意路徑的 .py 當模組載入並回傳。找不到/未完成就友善報錯。"""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"✗ 找不到檔案:{path}")
        if missing_hint:
            print(f"  {missing_hint}")
        print("  (或用 --target 指定你的檔案)")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except NotImplementedError:
        print("✗ 這支檔案載入時就丟出 NotImplementedError(還有 TODO 沒實作)。")
        print("  先把標 TODO 的地方補完,再來跑驗收。")
        sys.exit(1)
    return mod


def target_path(default):
    """解析 --target 參數;沒給就用預設。"""
    argv = sys.argv
    if "--target" in argv:
        return argv[argv.index("--target") + 1]
    return default


class Grader:
    """收集 check 結果,最後 report()。狀態三種:True 過 / False 錯 / 'todo' 待完成。
    只要不是全部 True,exit code = 1。"""

    def __init__(self, title):
        self.title = title
        self.results = []  # (status, msg);status ∈ {True, False, "todo"}

    def check(self, passed, msg):
        self.results.append((bool(passed), msg))
        print(f"  {'✅' if passed else '❌'} {msg}")
        return passed

    def todo(self, msg):
        """某個要件還沒實作 —— 不算錯,標成待完成。"""
        self.results.append(("todo", msg))
        print(f"  ⬜ 待完成  {msg}")

    def check_raises(self, fn, msg):
        """期望 fn() 丟例外 (用來驗『該擋的有擋住』)。"""
        try:
            fn()
            self.check(False, msg + "(預期該丟錯,但沒有)")
        except Exception:
            self.check(True, msg)

    def report(self):
        passed = sum(1 for s, _ in self.results if s is True)
        todos = sum(1 for s, _ in self.results if s == "todo")
        wrong = sum(1 for s, _ in self.results if s is False)
        total = len(self.results)
        print("-" * 56)
        if passed == total:
            print(f"🎉 {self.title}:全部 {total} 項通過!過關了。")
            return 0
        tail = []
        if wrong:
            tail.append(f"{wrong} 項要修(❌)")
        if todos:
            tail.append(f"{todos} 項還沒做(⬜)")
        print(f"📋 {self.title}:{passed}/{total} 項通過" + ("," + "、".join(tail) if tail else "") + "。")
        print("   照上面的 ❌/⬜ 一項一項補,改完再跑一次。(卡死了再看 solutions/ 參考解答)")
        return 1


def requirement(grader, label, fn):
    """跑一個『要件』的檢查。fn 內部自己呼叫 grader.check(...)。
    若 fn 撞到還沒實作的部分(NotImplementedError)→ 標成 ⬜ 待完成(不中止其他要件);
    若 fn 執行時爆其他錯 → 記成 ❌ 並附錯誤。這讓學生在多要件的關卡也能看到部分進度。"""
    try:
        fn()
    except NotImplementedError:
        grader.todo(f"{label}(還沒實作)")
    except Exception as e:
        grader.check(False, f"{label} 執行時出錯:{type(e).__name__}: {e}")


def run(grade_fn, grader):
    """單一 TODO 的練習用:grade_fn 內若碰到未實作就友善收尾。回傳 exit code。"""
    try:
        grade_fn()
    except NotImplementedError as e:
        print(f"\n✗ 還有 TODO 沒實作:{e}")
        print("  把標 TODO 的地方補完,再來驗收。")
        return 1
    return grader.report()
