"""
Exercise 6 -- one heartbeat tick of a scheduled loop (corresponds to Lesson 6)
===============================================================================
World, maker, checker, and log_event are all provided. You need to implement tick():
the single heartbeat of an unattended loop.

Spec for tick(world, logfile) you must implement:
  1. [triage] If world has no pending work -> log_event(logfile, event="idle") then return immediately
  2. Pop the first task from world.todos (pop(0))
  3. [act + verify] result = maker(task); verify with checker(task, result)
  4. Pass -> append to world.done, log_event(event="done", task=task)
  5. Fail -> append to world.escalated, log_event(event="escalate", task=task)

Run the autograder when done:
    python3 check_exercise6.py
"""

import json
import time


class World:
    """[Provided] Simulated pending-work world."""
    def __init__(self, todos):
        self.todos = list(todos)
        self.done = []
        self.escalated = []

    def has_work(self):
        return bool(self.todos)


def maker(task):
    """[Provided] High-risk 'deploy' tasks fail (return None)."""
    return None if task.startswith("deploy") else f"completed [{task}]"


def checker(task, result):
    """[Provided] Independent verifier."""
    return result is not None and result.startswith("completed")


def log_event(logfile, **fields):
    """[Provided]"""
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


def tick(world, logfile):
    # ===================================================================
    # TODO: implement one heartbeat: triage -> act -> verify -> done/escalate (see spec above)
    # ===================================================================
    raise NotImplementedError("implement your tick()")
