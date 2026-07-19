"""
Exercise 2 -- Exit Conditions and the Verify Gate (corresponds to Lesson 2)
==========================================
The scaffolding (Exit, agent, run_check, file writing) is provided. You only need to implement loop().

Specification for loop(check_cmd, workdir), returns (Exit, code_or_None):
  Each round (at most MAX_ITERS rounds):
    1. code = agent(feedback, attempt=i-1)
    2. [STALL exit] if code is identical to the previous round -> return (Exit.STALL, None)
    3. Write code to workdir/add.py (use the provided write_code)
    4. passed, output = run_check(check_cmd, workdir)
    5. [SUCCESS exit] if passed is True -> return (Exit.SUCCESS, code)
    6. Otherwise set output as feedback for the next round
  If all rounds complete without passing -> [FUSE exit] return (Exit.FUSE, None)

Assessment:
    python3 check_exercise2.py
"""

import os
import subprocess
from enum import Enum

MAX_ITERS = 6


class Exit(Enum):
    SUCCESS = "goal met, green"
    FUSE = "fuse blown (iterations exhausted)"
    STALL = "stalled (two consecutive identical outputs)"


def run_check(cmd, cwd):
    """[Provided] Run the command, return (passed, output). The autograder will replace this."""
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=30)
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def agent(feedback, attempt):
    """[Provided] Stand-in agent. The autograder will replace this."""
    versions = ["print(40 + )\n", "print(20 + 21)\n", "print(20 + 22)\n"]
    return versions[min(attempt, len(versions) - 1)]


def write_code(code, workdir):
    """[Provided] Write code to workdir/add.py."""
    with open(os.path.join(workdir, "add.py"), "w") as f:
        f.write(code)


def loop(check_cmd, workdir):
    # ===================================================================
    # TODO: implement a loop with SUCCESS / FUSE / STALL exits (see spec above)
    # ===================================================================
    raise NotImplementedError("implement loop()")
