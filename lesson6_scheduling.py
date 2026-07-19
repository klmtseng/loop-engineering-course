"""
Lesson 6 (Capstone) -- Scheduling and Unattended Loops
=======================================================
All five earlier loops had one thing in common: you had to press "run" manually.
The last puzzle piece is letting the loop wake itself up. Attach a loop to a
scheduler (cron) and it transforms from "a script" into "a system" -- one that
patrols while you sleep, handles what it can, and only calls you when it cannot.

    "Design AI loops that ship while you sleep."

This lesson assembles the parts from Lessons 1-5 into a mini "unattended patrol
loop" and shows its most natural form -- a tick():

    triage  Scan the world -- is there anything to handle? (if not, do nothing -- this matters)
    act     If there is, take one step (with maker/checker, with verify)     <- Lessons 1, 2, 4
    log     Whether or not anything happened, write one line to the run-log  <- Lesson 3
    decide  Done -> record; can't handle -> escalate and call a human        <- Lesson 3

Then hand tick() to a scheduler and let it run "every N minutes / every morning."

This lesson uses a self-built mini-scheduler to call tick() several times
(--once calls it just once); the real cron installation command is printed at the
end and is also in textbook Chapter 6. Standard library only; zero API keys.

Run:
    python3 lesson6_scheduling.py           # watch: run several ticks in memory
    python3 lesson6_scheduling.py --once    # one tick only (this is how cron calls it)
    python3 lesson6_scheduling.py --animate # slow-motion: watch the scheduler clear the queue
"""

import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# A simulated "world" -- the pending-work queue. In production this would be:
#   open GitHub issues / red CI runs / outdated dependencies / incoming support tickets ...
# ===========================================================================
class World:
    def __init__(self, todos, done=None, escalated=None):
        self.todos = list(todos)                        # pending
        self.done = list(done or [])                    # completed
        self.escalated = list(escalated or [])          # could not handle; handed to a human

    def has_work(self):
        return bool(self.todos)

    def to_dict(self):
        return {"todos": self.todos, "done": self.done, "escalated": self.escalated}


# ===========================================================================
# Real external state -- why a cron loop is reliable: state lives outside the process
# ===========================================================================
# Every cron invocation is a fresh process with no memory. So the pending-work
# queue must be read from and written to an external file (here JSON; in
# production it is a DB / issue queue / message queue).
# This is why consecutive --once runs "resume" instead of "restart from scratch"
# and why completed tasks are never re-done (deduplication).
def load_world(state_file, seed):
    if os.path.exists(state_file):
        with open(state_file) as f:
            d = json.load(f)
        return World(d["todos"], d["done"], d["escalated"])
    return World(seed)  # first run: initialize from seed queue


def save_world(state_file, world):
    with open(state_file, "w") as f:
        json.dump(world.to_dict(), f, ensure_ascii=False, indent=2)


# ===========================================================================
# Parts from Lesson 4: maker / checker (minimal version)
# ===========================================================================
def maker(task):
    # Simulate: most tasks succeed, but "deploy" high-risk tasks fail (return None)
    return None if task.startswith("deploy") else f"completed [{task}]"


def checker(task, result):
    return result is not None and result.startswith("completed")


# ===========================================================================
# Parts from Lesson 3: run-log
# ===========================================================================
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


# ===========================================================================
# Capstone: one tick -- the heartbeat of an unattended loop
# ===========================================================================
def tick(world, logfile):
    # --- triage: is there work? if not, do nothing cleanly (this is the right behavior) ---
    if not world.has_work():
        log_event(logfile, event="idle")
        print("   [tick] no pending work -> quiet skip (doing nothing is also a correct result)")
        return

    task = world.todos.pop(0)
    print(f"   [tick] picked up task: {task}")

    # --- act + verify: maker produces, checker verifies independently (Lesson 4) ---
    anim.step("✎", "act: maker at work")
    anim.step("🔍", "verify: independent checker")
    result = maker(task)
    if checker(task, result):
        world.done.append(task)
        log_event(logfile, event="done", task=task)
        print(f"          ✅ done and verified: {task}")
    else:
        # --- decide: checker rejects = cannot handle autonomously -> escalate to human (Lesson 3) ---
        world.escalated.append(task)
        log_event(logfile, event="escalate", task=task, reason="checker rejected")
        print(f"          🔺 cannot handle, escalating to human: {task}")


# ===========================================================================
# Mini-scheduler -- in production this layer is replaced by cron / systemd timer / GitHub Actions
# ===========================================================================
def scheduler(world, logfile, ticks, interval):
    for n in range(1, ticks + 1):
        print(f"\n-- Tick {n} ({time.strftime('%H:%M:%S')}) --")
        anim.fuse(n - 1, ticks, label="scheduler")
        tick(world, logfile)
        anim.pause()
        if n < ticks:
            time.sleep(interval)


# ===========================================================================
# Demo
# ===========================================================================
SEED = [
    "triage issue #312", "bump dependency lodash",
    "deploy v2.1 to staging", "triage issue #313",
]
# External state file. Each cron invocation is a new process; this file carries state across runs.
STATE_FILE = "/tmp/loop6_queue.json"
PERSIST_LOG = "/tmp/loop6_run.jsonl"

if __name__ == "__main__":
    anim.from_argv()

    if "--reset" in sys.argv:
        for p in (STATE_FILE, PERSIST_LOG):
            if os.path.exists(p):
                os.remove(p)
        print(f"State cleared: {STATE_FILE}")
        sys.exit(0)

    print("=" * 64)
    print("Unattended patrol loop -- assembling Lessons 1-5 parts into a self-waking system")
    print("=" * 64)

    if "--once" in sys.argv:
        # ===== cron mode: read external state -> run one tick -> write back. consecutive runs resume =====
        world = load_world(STATE_FILE, SEED)
        print(f"\n(--once: this is how cron calls it each time. state read from {STATE_FILE})")
        print(f"  queue at start of this tick: {world.todos}")
        tick(world, PERSIST_LOG)
        save_world(STATE_FILE, world)
        print(f"  queue at end of this tick:   {world.todos}")
        print("-" * 64)
        print(f"Totals: done {len(world.done)}, escalated {len(world.escalated)}, pending {len(world.todos)}")
        print(f"-> Run --once again and it will pick up the NEXT item, not restart from the beginning")
        print(f"   (this is 'external state storage' in action).")
        print(f"-> To reset: python3 lesson6_scheduling.py --reset")
    else:
        # ===== live-view mode: run 6 ticks in memory, watch the queue drain =====
        with tempfile.TemporaryDirectory() as base:
            logfile = os.path.join(base, "run.jsonl")
            world = World(SEED)
            scheduler(world, logfile, ticks=6, interval=0.3)
            print("\n" + "=" * 64)
            print(f"Summary: done {len(world.done)}, escalated {len(world.escalated)}, remaining {len(world.todos)}")
            print(f"  completed: {world.done}")
            print(f"  handed to human: {world.escalated}")

    # --- How to make it truly "wake itself up" ---
    print("=" * 64)
    print("To truly let it 'wake itself up', attach --once mode to cron (state continues via STATE_FILE):")
    print()
    print("  # Run one tick every day at 9 AM (paste this into crontab -e):")
    print(f"  0 9 * * *  cd {os.getcwd()} && /usr/bin/python3 lesson6_scheduling.py --once >> ~/loop.log 2>&1")
    print()
    print("  # Or every 15 minutes:")
    print("  */15 * * * *  ...same command... --once")
    print("=" * 64)
    print("This is the endpoint of loop engineering: you design it once, the system runs it")
    print("indefinitely -- shipping while you sleep.")
