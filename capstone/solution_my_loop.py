"""Capstone reference solution. Assembles components from all six lessons into a deployable maintenance loop."""

import json
import sys
import time


class World:
    def __init__(self, todos):
        self.todos = list(todos)
        self.done = []
        self.escalated = []
        self.executed = 0


# Requirement 1
class Budget:
    def __init__(self, max_iters, max_tokens):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.used_iters = 0
        self.used_tokens = 0

    def can_continue(self):
        return self.used_iters < self.max_iters and self.used_tokens < self.max_tokens

    def charge(self, tokens):
        self.used_iters += 1
        self.used_tokens += tokens


# Requirement 2
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


# Requirement 3
def checker(task, result):
    return result is not None and result.startswith("completed")


# Requirement 6 (isolation)
def worker_dir(base, name):
    import os
    return os.path.join(base, f"wt-{name}")


def task_agent(task):
    """Per-task agent: returns a coverage value. deploy* high-risk tasks never reach GOAL -> escalated."""
    return (lambda attempt: 50) if task.startswith("deploy") else (lambda attempt: 95)


# Requirements 4 + 5 (integrates Req 7: each task is processed via solve_task / best-so-far)
def run(world, logfile, budget, level="L3"):
    while world.todos and budget.can_continue():
        task = world.todos.pop(0)
        budget.charge(50)
        status, best = solve_task(task_agent(task), max_iters=4)   # <- actually uses best-so-far
        if status == "SUCCESS":
            if level != "L1":               # Req 5: L1 does not execute side effects
                world.executed += 1
            world.done.append(task)
            log_event(logfile, event="done", task=task, best=best, executed=(level != "L1"))
        else:
            world.escalated.append(task)
            log_event(logfile, event="escalate", task=task, best=best)
    budget_exhausted = bool(world.todos) and not budget.can_continue()
    if budget_exhausted:
        log_event(logfile, event="ESCALATE_budget_exhausted")
    return {"done": len(world.done), "escalated": len(world.escalated),
            "budget_exhausted": budget_exhausted}


GOAL = 90


def solve_task(agent, max_iters):
    best = None
    for i in range(max_iters):
        cov = agent(i)
        if best is None or cov > best:
            best = cov
        if best >= GOAL:
            return ("SUCCESS", best)
    return ("FAIL", best)


if __name__ == "__main__":
    once = "--once" in sys.argv
    world = World(["triage #1", "deploy v2", "triage #2"])
    summary = run(world, "/tmp/capstone_run.jsonl",
                  Budget(max_iters=1 if once else 99, max_tokens=10_000))
    print(f"summary: {summary}")
    sys.exit(0)
