"""Exercise 5 reference solution. Corresponds to Lesson 5."""

import os
import time
from concurrent.futures import ThreadPoolExecutor


def run_one_loop(name, workdir):
    own = os.path.join(workdir, "result.txt")
    for i in range(3):
        with open(own, "a") as f:
            f.write(f"{name} round {i}\n")
        time.sleep(0.005)
    with open(own) as f:
        return f.read().strip()


def run_isolated(workers, base):
    results = {}
    with ThreadPoolExecutor(max_workers=len(workers)) as ex:
        futures = {}
        for w in workers:
            wt = os.path.join(base, f"wt-{w}")   # key: each worker gets its own dedicated directory
            os.makedirs(wt, exist_ok=True)
            futures[w] = ex.submit(run_one_loop, w, wt)
        for w, fut in futures.items():
            results[w] = fut.result()
    return results
