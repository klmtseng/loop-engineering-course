"""
Capstone grader. Verifies all six requirements (see SPEC.md). Grades each requirement
independently: pass ✅, fail ❌, not implemented ⬜ -- a missing requirement never blocks
the others so you can always see your partial progress.
Usage:
    python3 grade_capstone.py                          # grade my_loop.py
    python3 grade_capstone.py --target solution_my_loop.py
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "exercises"))
from _grader_utils import Grader, load, requirement, target_path  # noqa: E402

tpath = target_path(os.path.join(HERE, "my_loop.py"))
mod = load(tpath, name="capstone_module",
           missing_hint="Capstone: first run: cp my_loop_template.py my_loop.py, then implement the TODOs")
g = Grader("Capstone - a loop you can deploy")


def r1_budget():
    b = mod.Budget(2, 100)
    b.charge(10)
    g.check(b.can_continue() is True, "[Req1] Budget has headroom -> can continue")
    b.charge(10)
    g.check(b.can_continue() is False, "[Req1] iter count exhausted -> stop")
    b2 = mod.Budget(99, 50); b2.charge(60)
    g.check(b2.can_continue() is False, "[Req1] token count exhausted -> stop")


def r2_runlog():
    with tempfile.TemporaryDirectory() as wd:
        lf = os.path.join(wd, "r.jsonl")
        mod.log_event(lf, event="a")
        mod.log_event(lf, event="b")
        lines = [l for l in open(lf) if l.strip()]
        g.check(len(lines) == 2, f"[Req2] run-log appends two lines without overwriting (got {len(lines)} lines)")


def r3_checker():
    g.check(mod.checker("t", "completed [t]") is True, "[Req3] checker approves good result")
    g.check(mod.checker("t", None) is False, "[Req3] checker rejects bad result")


def r6a_isolation():
    base = "/tmp/cap_base"
    da, db = mod.worker_dir(base, "A"), mod.worker_dir(base, "B")
    g.check(da != db and da.startswith(base) and db.startswith(base),
            f"[Req6] worker_dir is distinct per worker and under base ({da} / {db})")


def r4_mainloop():
    with tempfile.TemporaryDirectory() as wd:
        # integration check: run() must actually call solve_task (do not bypass Req 7)
        spy = {"n": 0}
        orig = mod.solve_task
        def wrapped(agent, max_iters):
            spy["n"] += 1
            return orig(agent, max_iters)
        mod.solve_task = wrapped
        w0 = mod.World(["triage #0"])
        mod.run(w0, os.path.join(wd, "l0.jsonl"), mod.Budget(99, 10000), level="L3")
        mod.solve_task = orig
        g.check(spy["n"] >= 1, f"[Req4] run() actually calls solve_task (integration; called {spy['n']} times)")

        w = mod.World(["triage #1", "deploy v2", "triage #2"])
        s = mod.run(w, os.path.join(wd, "l.jsonl"), mod.Budget(99, 10000), level="L3")
        g.check(s["done"] == 2, f"[Req4] two normal tasks completed (done={s['done']})")
        g.check(s["escalated"] == 1, f"[Req4] deploy escalated (escalated={s['escalated']})")
        g.check(s["budget_exhausted"] is False, "[Req4] budget_exhausted=False when budget is sufficient")
        w2 = mod.World(["a", "b", "c", "d"])
        s2 = mod.run(w2, os.path.join(wd, "l2.jsonl"), mod.Budget(1, 10000), level="L3")
        g.check(s2["budget_exhausted"] is True, "[Req4] tiny budget -> budget_exhausted=True")
        g.check(s2["done"] < 4, "[Req4] did not complete all tasks when budget exhausted")


def r5_l1safety():
    with tempfile.TemporaryDirectory() as wd:
        w3 = mod.World(["triage #1", "triage #2"])
        mod.run(w3, os.path.join(wd, "l3.jsonl"), mod.Budget(99, 10000), level="L1")
        g.check(w3.executed == 0, f"[Req5] L1 executes no side effects throughout (world.executed={w3.executed})")


def r6b_schedule():
    proc = subprocess.run([sys.executable, os.path.abspath(tpath), "--once"],
                          capture_output=True, text=True, timeout=30)
    g.check(proc.returncode == 0, f"[Req6] `--once` runs one tick then exits cleanly (exit={proc.returncode})")


def r7_robust():
    seq = lambda vals: (lambda attempt: vals[min(attempt, len(vals) - 1)])
    # peaks mid-run to 95 then regresses to 50: best-so-far must remember 95
    status, best = mod.solve_task(seq([50, 95, 50, 50]), 4)
    g.check(status == "SUCCESS" and best == 95,
            f"[Req7] noisy agent regresses but historical best 95 is remembered (got {status},{best})")
    # never reaches goal: FAIL with best (88), not last-round value
    status, best = mod.solve_task(seq([88, 70, 60, 50]), 4)
    g.check(status == "FAIL" and best == 88,
            f"[Req7] never meets goal -> FAIL with best 88, not last-round value (got {status},{best})")


# Grade each requirement independently: a missing requirement only marks ⬜, does not block others
requirement(g, "Req1 - fuse + budget", r1_budget)
requirement(g, "Req2 - run-log", r2_runlog)
requirement(g, "Req3 - independent checker", r3_checker)
requirement(g, "Req6 (isolation) - worker_dir", r6a_isolation)
requirement(g, "Req4 - main loop", r4_mainloop)
requirement(g, "Req5 - L1 safety", r5_l1safety)
requirement(g, "Req6 (scheduling) - --once", r6b_schedule)
requirement(g, "Req7 - robust against noisy agent", r7_robust)

sys.exit(g.report())
