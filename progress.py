"""
progress.py -- learning progress dashboard
==========================================
Runs every lesson's autograder plus the capstone grader and shows a single table
of which checkpoints you have passed. This script itself is a loop: it runs one
round of verify over your learning progress -- the same technique the course teaches.

    python3 progress.py              # grade your own exercise files (exerciseN_*.py / my_loop.py)
    python3 progress.py --solutions  # grade the reference solutions instead (to see what all-green looks like)
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
USE_SOLUTIONS = "--solutions" in sys.argv

LESSONS = [
    ("Lesson 1 - Minimal Loop", "exercises/check_exercise1.py", "exercises/solutions/exercise1_minimal_loop.py"),
    ("Lesson 2 - Exit Conditions", "exercises/check_exercise2.py", "exercises/solutions/exercise2_exit_conditions.py"),
    ("Lesson 3 - Safety and Cost", "exercises/check_exercise3.py", "exercises/solutions/exercise3_safety_budget.py"),
    ("Lesson 4 - maker/checker", "exercises/check_exercise4.py", "exercises/solutions/exercise4_maker_checker.py"),
    ("Lesson 5 - Parallelism and Isolation", "exercises/check_exercise5.py", "exercises/solutions/exercise5_parallel_isolation.py"),
    ("Lesson 6 - Scheduling Heartbeat", "exercises/check_exercise6.py", "exercises/solutions/exercise6_scheduling.py"),
    ("Lesson 7 - Ungameable verify", "exercises/check_exercise7.py", "exercises/solutions/exercise7_verifier_gaming.py"),
    ("Lesson 8 - best-so-far", "exercises/check_exercise8.py", "exercises/solutions/exercise8_best_so_far.py"),
    ("Lesson 9 - Context Strategy", "exercises/check_exercise9.py", "exercises/solutions/exercise9_context_strategy.py"),
    ("Lesson 10 - Loop Evals", "exercises/check_exercise10.py", "exercises/solutions/exercise10_loop_evals.py"),
    ("Capstone - Maintenance Loop", "capstone/grade_capstone.py", "capstone/solution_my_loop.py"),
]


def run_check(checker_rel, solution_rel):
    cmd = [sys.executable, os.path.join(HERE, checker_rel)]
    if USE_SOLUTIONS:
        cmd += ["--target", os.path.join(HERE, solution_rel)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return proc.returncode == 0


def main():
    print("=" * 56)
    print("  Loop Engineering Progress" + (" (reference solutions)" if USE_SOLUTIONS else ""))
    print("=" * 56)
    passed = 0
    for title, checker, solution in LESSONS:
        ok = run_check(checker, solution)
        passed += ok
        print(f"  {'[PASS]' if ok else '[    ]'}  {title}")
    print("-" * 56)
    total = len(LESSONS)
    bar = "o" * passed + "." * (total - passed)
    print(f"  Progress [{bar}] {passed}/{total}")
    if passed == total:
        print("  All passed! You can now design, write, and verify a loop you can deploy.")
    elif passed == 0:
        print("  Start with Lesson 1: exercises/exercise1_minimal_loop.py")
    else:
        print("  Keep going to the next checkpoint. If stuck, read the textbook chapter and check solutions/.")
    print("=" * 56)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
