"""
練習 6 —— 排程的一次心跳 tick (對應第 6 課)
============================================
World、maker、checker、log_event 都給你了。你要實作 tick():無人值守 loop 的一次心跳。

要實作的 tick(world, logfile) 規格:
  1. 【triage】world 沒有待辦 → log_event(logfile, event="idle") 後直接 return(什麼都不做也是對的)
  2. 從 world.todos 取出第一個 task (pop(0))
  3. 【act + verify】result = maker(task);用 checker(task, result) 驗
  4. 通過 → 加進 world.done,log_event(event="done", task=task)
  5. 不過 → 加進 world.escalated,log_event(event="escalate", task=task)

完成後驗收:
    python3 check_exercise6.py
"""

import json
import time


class World:
    """【已給你】模擬待辦世界。"""
    def __init__(self, todos):
        self.todos = list(todos)
        self.done = []
        self.escalated = []

    def has_work(self):
        return bool(self.todos)


def maker(task):
    """【已給你】deploy 類高風險任務會做砸(回 None)。"""
    return None if task.startswith("deploy") else f"已完成 [{task}]"


def checker(task, result):
    """【已給你】獨立驗收。"""
    return result is not None and result.startswith("已完成")


def log_event(logfile, **fields):
    """【已給你】"""
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


def tick(world, logfile):
    # ===================================================================
    # TODO: 實作一次心跳:triage → act → verify → done/escalate (見檔頭規格)
    # ===================================================================
    raise NotImplementedError("實作你的 tick()")
