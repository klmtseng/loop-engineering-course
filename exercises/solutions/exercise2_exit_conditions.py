"""Reference solution for Exercise 2. Corresponds to Lesson 2."""

import os
import subprocess
from enum import Enum

MAX_ITERS = 6


class Exit(Enum):
    SUCCESS = "goal met, green"
    FUSE = "fuse blown (iterations exhausted)"
    STALL = "stalled (two consecutive identical outputs)"


def run_check(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=30)
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def agent(feedback, attempt):
    versions = ["print(40 + )\n", "print(20 + 21)\n", "print(20 + 22)\n"]
    return versions[min(attempt, len(versions) - 1)]


def write_code(code, workdir):
    with open(os.path.join(workdir, "add.py"), "w") as f:
        f.write(code)


def loop(check_cmd, workdir):
    feedback = "(first round)"
    last_code = None
    for i in range(1, MAX_ITERS + 1):
        code = agent(feedback, attempt=i - 1)
        if code == last_code:
            return Exit.STALL, None
        last_code = code
        write_code(code, workdir)
        passed, output = run_check(check_cmd, workdir)
        if passed:
            return Exit.SUCCESS, code
        feedback = output
    return Exit.FUSE, None
