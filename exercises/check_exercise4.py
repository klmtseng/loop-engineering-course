"""autograder:練習 4 (maker/checker)。用法:python3 check_exercise4.py [--target 你的檔.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise4_maker_checker.py")))
g = Grader("練習 4 · maker/checker")


def grade():
    good = "不好意思造成困擾,我們會在 24 小時內回覆您。"
    ok, msg = mod.checker(good)
    g.check(ok is True, f"合格回覆 → approve(得到 {ok}, {msg!r})")

    ok, msg = mod.checker("您的問題我們已經收到了,謝謝。")  # 無道歉、無承諾
    g.check(ok is False and "道歉" in msg, f"缺道歉 → reject 且點出道歉(得到 {msg!r})")
    g.check("承諾" in msg or "下一步" in msg, f"缺承諾 → reject 且點出下一步(得到 {msg!r})")

    ok, msg = mod.checker("抱歉,我們會儘快處理" + "好" * 50)  # 太長
    g.check(ok is False and "長" in msg, f"太長 → reject 且點出太長(得到 {msg!r})")

    ok, msg = mod.checker("不好意思,我們會處理")  # 有道歉有承諾且夠短
    g.check(ok is True, f"道歉+承諾+夠短 → approve(得到 {ok}, {msg!r})")

    # 端到端:用學生的 checker 跑給好的 loop,應逼出完全合格的成品
    result = mod.loop(mod.checker)
    g.check(result is not None and mod.checker(result)[0],
            f"端到端:loop 用你的 checker 收斂到合格成品(得到 {result!r})")


sys.exit(run(grade, g))
