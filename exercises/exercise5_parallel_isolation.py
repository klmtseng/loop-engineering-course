"""
Exercise 5 -- Parallelism and Isolation (corresponds to Lesson 5)
=================================================================
run_one_loop is provided (each worker writes 3 lines in its own workdir and returns the file).
You need to implement run_isolated(): run multiple workers in parallel, each fully isolated.

Spec for run_isolated(workers, base) you must implement:
  - For each worker name, create a dedicated subdirectory under base (key: one per worker!)
  - Use ThreadPoolExecutor to run run_one_loop(name, that_worker_dir) in parallel
  - Return a dict: {worker_name: content returned by run_one_loop}

Run the autograder when done:
    python3 check_exercise5.py
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor


def run_one_loop(name, workdir):
    """[Provided] Run 3 rounds in workdir, append one line per round to a private result.txt, return its content."""
    own = os.path.join(workdir, "result.txt")
    for i in range(3):
        with open(own, "a") as f:
            f.write(f"{name} round {i}\n")
        time.sleep(0.005)
    with open(own) as f:
        return f.read().strip()


def run_isolated(workers, base):
    # ===================================================================
    # TODO: give each worker a dedicated subdirectory, run in parallel, return {name: content}
    # ===================================================================
    raise NotImplementedError("implement your run_isolated()")
