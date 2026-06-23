"""autograder:練習 5 (平行與隔離)。用法:python3 check_exercise5.py [--target 你的檔.py]"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise5_parallel_isolation.py")))
g = Grader("練習 5 · 平行與隔離")


def grade():
    workers = ["A", "B", "C"]
    with tempfile.TemporaryDirectory() as base:
        results = mod.run_isolated(workers, base)

        g.check(isinstance(results, dict) and set(results) == set(workers),
                f"回傳 dict 且涵蓋全部 worker(得到 keys={list(results) if isinstance(results, dict) else results})")

        # 隔離的鐵證:每個 worker 的內容只能有它自己的字句,且剛好 3 行
        all_clean = True
        for w in workers:
            lines = results.get(w, "").strip().split("\n")
            clean = len(lines) == 3 and all(ln.startswith(w + " ") for ln in lines)
            if not clean:
                all_clean = False
            g.check(clean, f"{w} 的成品乾淨:3 行且全是自己的(得到 {results.get(w)!r})")
        g.check(all_clean, "整體隔離成功:沒有任何 worker 的檔被別人污染")


sys.exit(run(grade, g))
