"""autograder:練習 10 (loop 級指標)。用法:python3 check_exercise10.py [--target 你的檔.py]"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise10_loop_evals.py")))
g = Grader("練習 10 · loop 級指標")


def grade():
    # 已知一批結果:2 成功(iters 2、4)、2 escalate(各 cost 800),總 4 筆
    records = [
        {"status": "SUCCESS", "iters": 2, "cost": 200},
        {"status": "SUCCESS", "iters": 4, "cost": 400},
        {"status": "ESCALATED", "iters": 8, "cost": 800},
        {"status": "ESCALATED", "iters": 8, "cost": 800},
    ]
    m = mod.aggregate(records)
    g.check(m["success_rate"] == 0.5, f"success_rate=0.5(得到 {m['success_rate']})")
    g.check(m["mean_iters"] == 3.0, f"mean_iters 只算成功的 (2+4)/2=3.0(得到 {m['mean_iters']})")
    g.check(m["escalation_rate"] == 0.5, f"escalation_rate=0.5(得到 {m['escalation_rate']})")
    g.check(m["mean_cost"] == 550.0, f"mean_cost (200+400+800+800)/4=550.0(得到 {m['mean_cost']})")

    # 邊界:全 escalate → mean_iters 應為 0.0、不可除以零
    allesc = [{"status": "ESCALATED", "iters": 3, "cost": 300}] * 2
    m2 = mod.aggregate(allesc)
    g.check(m2["success_rate"] == 0.0 and m2["mean_iters"] == 0.0,
            f"全 escalate:success_rate=0、mean_iters=0、不爆(得到 {m2['success_rate']},{m2['mean_iters']})")


sys.exit(run(grade, g))
