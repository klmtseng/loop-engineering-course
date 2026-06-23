"""autograder:練習 6 (排程心跳 tick)。用法:python3 check_exercise6.py [--target 你的檔.py]"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _grader_utils import Grader, load, run, target_path

mod = load(target_path(os.path.join(os.path.dirname(__file__), "exercise6_scheduling.py")))
g = Grader("練習 6 · 排程心跳")


def grade():
    with tempfile.TemporaryDirectory() as wd:
        log = os.path.join(wd, "run.jsonl")
        world = mod.World(["triage #1", "deploy v2", "triage #2"])

        mod.tick(world, log)  # 1
        g.check("triage #1" in world.done, f"第1拍:一般任務完成並入 done(done={world.done})")

        mod.tick(world, log)  # 2
        g.check("deploy v2" in world.escalated,
                f"第2拍:deploy 高風險 → checker 不過 → escalate(escalated={world.escalated})")
        g.check("deploy v2" not in world.done, "第2拍:失敗任務不該混進 done")

        mod.tick(world, log)  # 3
        g.check("triage #2" in world.done, f"第3拍:回到正常任務完成(done={world.done})")

        # 沒事做的一拍:不崩、記 idle
        empty = mod.World([])
        idle_log = os.path.join(wd, "idle.jsonl")
        mod.tick(empty, idle_log)
        events = [json.loads(l)["event"] for l in open(idle_log) if l.strip()]
        g.check(events == ["idle"], f"沒待辦的一拍:安靜記 idle、不做事(log events={events})")


sys.exit(run(grade, g))
