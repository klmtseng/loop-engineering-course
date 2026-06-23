"""
練習 3 —— 安全與成本 (對應第 3 課)
====================================
這課你要補兩個關鍵零件,其餘鷹架(safe_loop、log_event、agent、execute)都給好了。

TODO 1 —— Budget 類別的兩個方法:
    can_continue() → 圈數「且」token 都還沒到上限,才回 True
    charge(tokens) → 用掉一圈、累加 tokens

TODO 2 —— should_execute(level):
    L1_REPORT → False (只報告,絕不執行)
    其他(L2/L3) → True

完成後驗收:
    python3 check_exercise3.py
"""

import json
import time
from enum import Enum


class Level(Enum):
    L1_REPORT = 1
    L2_ASSISTED = 2
    L3_UNATTENDED = 3


class Budget:
    def __init__(self, max_iters, max_tokens):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.used_iters = 0
        self.used_tokens = 0

    def can_continue(self):
        # TODO 1a: 圈數與 token 都還沒到上限才回 True
        raise NotImplementedError("實作 can_continue()")

    def charge(self, tokens):
        # TODO 1b: 用掉一圈、累加 tokens
        raise NotImplementedError("實作 charge()")


def should_execute(level):
    # TODO 2: L1 只報告(False),其他要執行(True)
    raise NotImplementedError("實作 should_execute()")


# ---- 以下【已給你】,會用到上面兩個 TODO ----
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


def agent(attempt):
    plan = [("write_file r.md", 120), ("write_file r.md", 90), ("done", 40)]
    return plan[min(attempt, len(plan) - 1)]


def execute(action, workdir):
    return f"已執行 {action}"


def safe_loop(level, budget, logfile, workdir):
    while budget.can_continue():
        action, tokens = agent(budget.used_iters)
        budget.charge(tokens)
        if action == "done":
            log_event(logfile, action="done")
            return "SUCCESS"
        if should_execute(level):
            result = execute(action, workdir)
            log_event(logfile, proposed=action, executed=True, result=result)
        else:
            log_event(logfile, proposed=action, executed=False)
    log_event(logfile, action="ESCALATE_budget_exhausted")
    return "ESCALATED"
