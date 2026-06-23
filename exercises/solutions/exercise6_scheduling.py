"""練習 6 參考解答。對應第 6 課。"""

import json
import time


class World:
    def __init__(self, todos):
        self.todos = list(todos)
        self.done = []
        self.escalated = []

    def has_work(self):
        return bool(self.todos)


def maker(task):
    return None if task.startswith("deploy") else f"已完成 [{task}]"


def checker(task, result):
    return result is not None and result.startswith("已完成")


def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


def tick(world, logfile):
    if not world.has_work():
        log_event(logfile, event="idle")
        return
    task = world.todos.pop(0)
    result = maker(task)
    if checker(task, result):
        world.done.append(task)
        log_event(logfile, event="done", task=task)
    else:
        world.escalated.append(task)
        log_event(logfile, event="escalate", task=task)
