"""autograder:練習 7 (鑽不動的 verify)。用法:python3 check_exercise7.py [--target 你的檔.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise7_verifier_gaming.py")))
g = Grader("練習 7 · 鑽不動的 verify")


def grade():
    honest = mod.build("def add(a, b):\n    return a + b")
    hardcode = mod.build("def add(a, b):\n    return 42")
    offbyone = mod.build("def add(a, b):\n    return a + b + 1")
    constant = mod.build("def add(a, b):\n    return 0")

    g.check(mod.strong_verify(honest) is True, "放行老實的 add(a,b)=a+b")
    g.check(mod.strong_verify(hardcode) is False, "抓出硬編答案 return 42")
    g.check(mod.strong_verify(offbyone) is False, "抓出 a+b+1 的 bug")
    g.check(mod.strong_verify(constant) is False, "抓出回傳常數 return 0")

    # 觀念確認:弱 verify 確實會被硬編騙過(這就是為什麼需要 strong)
    g.check(mod.weak_verify(hardcode) is True,
            "(對照)弱 verify 真的被 return 42 騙過了 → 所以才需要 strong_verify")


sys.exit(run(grade, g))
