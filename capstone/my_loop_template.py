"""
Capstone 範本 —— 複製成 my_loop.py 再實作。詳見 SPEC.md。
把六項要件都做出來,然後 `python3 grade_capstone.py` 驗收。
"""

import json
import sys
import time


# ---- 評分器會提供這種 world;這個 World 給你自己跑 --once 時用 ----
class World:
    def __init__(self, todos):
        self.todos = list(todos)
        self.done = []
        self.escalated = []
        self.executed = 0   # 每真的執行一次副作用就 +1


# ===== 要件 1:保險絲 + 預算 =====
class Budget:
    def __init__(self, max_iters, max_tokens):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.used_iters = 0
        self.used_tokens = 0

    def can_continue(self):
        raise NotImplementedError  # TODO

    def charge(self, tokens):
        raise NotImplementedError  # TODO


# ===== 要件 2:run-log =====
def log_event(logfile, **fields):
    raise NotImplementedError  # TODO:append 一行 JSONL,不覆蓋


# ===== 要件 3:獨立 checker =====
def checker(task, result):
    raise NotImplementedError  # TODO:好結果 True,壞結果 False


# ===== 要件 6(一半):可隔離 =====
def worker_dir(base, name):
    raise NotImplementedError  # TODO:回傳 base 底下、每個 name 互異的路徑


# ---- 每個任務的 agent,供你的 run() 透過 solve_task 處理(可自行調整) ----
def task_agent(task):
    """回一個覆蓋率。deploy* 高風險永遠到不了 GOAL → 會被 escalate;其餘會達標。"""
    return (lambda attempt: 50) if task.startswith("deploy") else (lambda attempt: 95)


# ===== 要件 4 + 5(整合要件 7):主迴圈 =====
def run(world, logfile, budget, level="L3"):
    """逐件處理 world.todos:每個任務用 solve_task(task_agent(task), ...) 處理(這樣才真的跑到 best-so-far),
    SUCCESS→done、FAIL→escalate,逐筆記 log;預算用罄要 escalate。
    level == "L1" 時不真的執行副作用(world.executed 維持 0)。
    回傳 dict:{"done": n, "escalated": n, "budget_exhausted": bool}。"""
    raise NotImplementedError  # TODO(記得呼叫 solve_task,別繞過要件 7)


# ===== 要件 7:對會退步的 noisy agent 穩健(best-so-far,搬第 8 課) =====
GOAL = 90


def solve_task(agent, max_iters):
    """agent(attempt) 回一個覆蓋率(int)。每圈記住歷史最佳;best≥GOAL 回 ("SUCCESS", best),
    燒完回 ("FAIL", best)。真 agent 會退步,別只信末圈。"""
    raise NotImplementedError  # TODO


# ===== 要件 6(另一半):可排程 =====
if __name__ == "__main__":
    once = "--once" in sys.argv
    # TODO:用 --once 跑一拍(處理一件 todo)後乾淨退出
    raise NotImplementedError
