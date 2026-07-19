"""autograder: Exercise 6 (scheduled heartbeat tick). Usage: python3 check_exercise6.py [--target yourfile.py]"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise6_scheduling.py")))
g = Grader("Exercise 6 - scheduled heartbeat")


def grade():
    with tempfile.TemporaryDirectory() as wd:
        log = os.path.join(wd, "run.jsonl")
        world = mod.World(["triage #1", "deploy v2", "triage #2"])

        mod.tick(world, log)  # 1
        g.check("triage #1" in world.done, f"tick 1: normal task completed and added to done (done={world.done})")

        mod.tick(world, log)  # 2
        g.check("deploy v2" in world.escalated,
                f"tick 2: deploy high-risk -> checker fails -> escalate (escalated={world.escalated})")
        g.check("deploy v2" not in world.done, "tick 2: failed task must not appear in done")

        mod.tick(world, log)  # 3
        g.check("triage #2" in world.done, f"tick 3: back to normal task completed (done={world.done})")

        # idle tick: no crash, logs idle
        empty = mod.World([])
        idle_log = os.path.join(wd, "idle.jsonl")
        mod.tick(empty, idle_log)
        events = [json.loads(l)["event"] for l in open(idle_log) if l.strip()]
        g.check(events == ["idle"], f"idle tick: quietly logs idle and does nothing (log events={events})")


sys.exit(run(grade, g))
