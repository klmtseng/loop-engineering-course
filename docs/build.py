"""
build.py -- embeds the real course files into index.html (single source of truth, no copies or forks).
When course content changes, re-run this script to sync the website. Standard library only.

Browser (Pyodide/WASM) limitations and mitigations:
  - Lesson 2 uses subprocess, Lesson 5 uses real threads -> sandbox cannot run them ->
    at build time run them once on a real machine and record the output; shown on the website
    as recorded playback (honestly labeled).
  - Exercise 5 grading needs ThreadPoolExecutor -> embed _wasm_shims.py (sync executor),
    installed before grading.
  - The other 8 lessons' demos and all 10 exercise graders run live in the browser.

Usage: python3 docs/build.py
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def record(lesson_rel):
    """Run a lesson on the real machine and capture stdout (used as recorded playback for lessons the browser cannot run)."""
    proc = subprocess.run([sys.executable, os.path.join(ROOT, lesson_rel)],
                          capture_output=True, text=True, timeout=120, cwd=ROOT)
    assert proc.returncode == 0, f"{lesson_rel} recording failed:\n{proc.stderr[:500]}"
    return proc.stdout


WASM_SHIMS = '''\
"""Pyodide sandbox shim (website only): the browser has no real threads; use a sync executor instead.
Exercise 5 tests 'isolation semantics' (each worker has its own directory, output is clean);
synchronous execution does not change its correctness."""
import concurrent.futures as _cf


class _SyncFuture:
    def __init__(self, fn, *a, **k):
        try:
            self._r, self._e = fn(*a, **k), None
        except Exception as e:
            self._r, self._e = None, e

    def result(self, timeout=None):
        if self._e:
            raise self._e
        return self._r


class SyncExecutor:
    def __init__(self, max_workers=None):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def submit(self, fn, *a, **k):
        return _SyncFuture(fn, *a, **k)


def install():
    _cf.ThreadPoolExecutor = SyncExecutor
'''

# Per-lesson assets and mode. mode: live = runs live in browser; recorded = plays back output recorded at build time.
LESSONS = [
    {"id": 1, "title": "The Minimal Loop", "mode": "live",
     "lesson": "lesson1_minimal_loop.py", "ch": "textbook/ch01_minimal_loop.md",
     "ex": "exercise1_minimal_loop.py", "check": "check_exercise1.py"},
    {"id": 2, "title": "Exit Conditions and Verification Gates", "mode": "recorded",
     "lesson": "lesson2_exit_conditions.py", "ch": "textbook/ch02_exit_conditions.md",
     "ex": "exercise2_exit_conditions.py", "check": "check_exercise2.py"},
    {"id": 3, "title": "Safety and Cost", "mode": "live",
     "lesson": "lesson3_safety_budget.py", "ch": "textbook/ch03_safety_budget.md",
     "ex": "exercise3_safety_budget.py", "check": "check_exercise3.py"},
    {"id": 4, "title": "maker / checker Dual Agent", "mode": "live",
     "lesson": "lesson4_maker_checker.py", "ch": "textbook/ch04_maker_checker.md",
     "ex": "exercise4_maker_checker.py", "check": "check_exercise4.py"},
    {"id": 5, "title": "Parallelism and Isolation", "mode": "recorded",
     "lesson": "lesson5_parallel_isolation.py", "ch": "textbook/ch05_parallel_isolation.md",
     "ex": "exercise5_parallel_isolation.py", "check": "check_exercise5.py", "shim": True},
    {"id": 6, "title": "Scheduling and Unattended Loops", "mode": "live",
     "lesson": "lesson6_scheduling.py", "ch": "textbook/ch06_scheduling.md",
     "ex": "exercise6_scheduling.py", "check": "check_exercise6.py"},
    {"id": 7, "title": "verify Is a Proxy Metric", "mode": "live",
     "lesson": "lesson7_verifier_gaming.py", "ch": "textbook/ch07_verifier_gaming.md",
     "ex": "exercise7_verifier_gaming.py", "check": "check_exercise7.py"},
    {"id": 8, "title": "Non-Determinism and Real Agents", "mode": "live",
     "lesson": "lesson8_real_agent.py", "ch": "textbook/ch08_real_agent.md",
     "ex": "exercise8_best_so_far.py", "check": "check_exercise8.py"},
    {"id": 9, "title": "Cross-Round Context Strategy", "mode": "live",
     "lesson": "lesson9_context_strategy.py", "ch": "textbook/ch09_context_strategy.md",
     "ex": "exercise9_context_strategy.py", "check": "check_exercise9.py"},
    {"id": 10, "title": "Loop-Level Evals", "mode": "live",
     "lesson": "lesson10_loop_evals.py", "ch": "textbook/ch10_loop_evals.md",
     "ex": "exercise10_loop_evals.py", "check": "check_exercise10.py"},
]


def main():
    files = {"anim.py": read("anim.py"),
             "_grader_utils.py": read("exercises/_grader_utils.py"),
             "_wasm_shims.py": WASM_SHIMS}
    meta = []
    for L in LESSONS:
        files[L["lesson"]] = read(L["lesson"])
        files[L["ex"]] = read("exercises/" + L["ex"])
        files[L["check"]] = read("exercises/" + L["check"])
        files["solutions/" + L["ex"]] = read("exercises/solutions/" + L["ex"])
        m = {"id": L["id"], "title": L["title"], "mode": L["mode"],
             "lesson": L["lesson"], "ex": L["ex"], "check": L["check"],
             "ch": read(L["ch"]), "shim": L.get("shim", False)}
        if L["mode"] == "recorded":
            print(f"  Recording {L['lesson']} ...")
            m["recording"] = record(L["lesson"])
        meta.append(m)

    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        tpl = f.read()
    out = (tpl
           .replace("/*FILES_JSON*/", json.dumps(files, ensure_ascii=False))
           .replace("/*LESSONS_JSON*/", json.dumps(meta, ensure_ascii=False)))
    dest = os.path.join(HERE, "index.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Generated {dest} ({len(out):,} chars; {len(files)} files, {len(meta)} lessons)")
    assert "/*FILES_JSON*/" not in out and "/*LESSONS_JSON*/" not in out, "placeholder 沒被替換"
    assert "loadPyodide" in out and "marked.parse" in out
    print("Sanity checks passed")


if __name__ == "__main__":
    main()
