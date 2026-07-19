"""
Lesson 2 -- Exit Conditions and the Verify Gate
=================================================================
Lesson 1's verify was a Python function. In the real world, the most reliable verify gate is usually
"run a command and check its exit code":

    pytest            -> 0 = all green
    ruff check .      -> 0 = no issues
    npm run build     -> 0 = build succeeded
    curl -f health    -> 0 = service alive

This kind of "between-iteration command" is the standard component in loop engineering:
after each iteration, run the check command once, and use its exit code to decide the loop's fate.

But "run until green" is just one exit condition. A loop that can survive in the real world
needs at least three exits simultaneously:

    1. SUCCESS  check command returns 0 -> goal met, stop (the outcome you want)
    2. FUSE     iterations exhausted, still not green -> max-iter fuse, abort (prevent infinite spending)
    3. STALL    two consecutive iterations produce identical output -> stuck; running more is pointless, stop early

Without STALL, a stuck loop burns through the entire max-iter budget before stopping --
every wasted iteration is money and time you did not need to spend.

Precise note: the STALL here only compares against the "previous iteration," so it only catches
fixed points -- two consecutive identical outputs. It cannot catch cycles of length >= 2,
such as an A, B, A, B, A, B oscillation -- those still burn to FUSE.
To catch cycles, you need to remember "the outputs of the last N iterations" and stop when a repeat
appears (still heuristic -- see the textbook extended exercises).
This lesson keeps STALL in its simplest form, but you should know where its boundary is.

This lesson builds a real subprocess-driven loop: the goal is to get an auto-generated Python file
to pass a check command. Pure standard library, no keys, no network.

Run:
    python3 lesson2_exit_conditions.py
    python3 lesson2_exit_conditions.py --animate    # slow motion: watch red -> red -> green + fuse
"""

import os
import subprocess
import sys
import tempfile
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# Verify gate -- run a real command, return (passed, output)
# ===========================================================================
def run_check(cmd, cwd):
    """Run the check command. Exit code 0 = passed. Output (stdout+stderr) is fed back to the agent.

    This is the between-iteration command in action. Notice we pass its output verbatim to the
    next iteration -- the agent's material for fixing the error is the real error message
    printed by the tests or compiler.
    """
    proc = subprocess.run(
        cmd, cwd=cwd, shell=True,
        capture_output=True, text=True, timeout=30,
    )
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output


# ===========================================================================
# Mock agent -- in the real world this would be Claude Code / Codex editing code
# ===========================================================================
# Task: write an add.py that prints "42". We let the first two attempts fail on purpose:
#   Attempt 0: syntax error (crashes immediately)           -> check command non-zero
#   Attempt 1: runs fine but wrong answer (prints 41)       -> check command non-zero
#   Attempt 2: correct                                      -> check command = 0
# A real agent would "read the error output from the previous iteration" and fix it;
# here we use pre-written versions to simulate that process.
_VERSIONS = [
    "print(40 + )\n",        # SyntaxError
    "print(20 + 21)\n",      # runs but = 41, wrong
    "print(20 + 22)\n",      # = 42, correct
]


def mock_agent(feedback, attempt):
    code = _VERSIONS[min(attempt, len(_VERSIONS) - 1)]
    print(f"   -> agent received feedback: {feedback[:50]!r}")
    print(f"   -> agent produced code: {code.strip()!r}")
    return code


# ===========================================================================
# ★ Key concept for this lesson: a loop with three exits
# ===========================================================================
class Exit(Enum):
    SUCCESS = "goal met, green"
    FUSE = "fuse blown (iterations exhausted)"
    STALL = "stalled (two consecutive identical outputs)"


MAX_ITERS = 6


def loop(check_cmd, workdir):
    feedback = "(first iteration, no feedback yet)"
    last_code = None  # remember the previous iteration's output to detect STALL

    for i in range(1, MAX_ITERS + 1):
        print(f"\n[Round {i}]")
        anim.fuse(i - 1, MAX_ITERS)

        # --- act: agent produces a new version, write it to the working directory ---
        anim.step("✎", "act: agent produces a version of the code")
        code = mock_agent(feedback, attempt=i - 1)

        # --- Exit 3: STALL -- this iteration is identical to the previous; running more is pointless ---
        if code == last_code:
            print("   ⏹  output identical to previous iteration -> STALL, stopping early")
            return Exit.STALL, None
        last_code = code

        target = os.path.join(workdir, "add.py")
        with open(target, "w") as f:
            f.write(code)

        # --- verify: run the real check command ---
        anim.step("🔍", "verify: run check command, read exit code")
        passed, output = run_check(check_cmd, cwd=workdir)
        print(f"   -> check command `{check_cmd}` -> {'green ✅' if passed else 'red ✗'}  output: {output!r}")
        anim.pause()

        # --- Exit 1: SUCCESS ---
        if passed:
            return Exit.SUCCESS, code

        feedback = output  # pass the error output to the next iteration

    # --- Exit 2: FUSE ---
    return Exit.FUSE, None


# ===========================================================================
# Check script -- the "between-iteration command" for this loop
# ===========================================================================
# In a real project this would be pytest / ruff / build. Here we write a small check script:
# run add.py, compare output, use exit code 0/1 as the gate, and print a message that
# both humans and the agent can read.
# Key: its output must be useful -- that is the agent's only material for the next fix.
CHECK_PY = r'''
import subprocess, sys
r = subprocess.run([sys.executable, "add.py"], capture_output=True, text=True)
got = r.stdout.strip()
if r.returncode != 0:
    print("add.py crashed:\n" + r.stderr.strip()); sys.exit(1)
if got != "42":
    print(f"ran fine, but printed {got!r} instead of '42'"); sys.exit(1)
print("OK: printed 42"); sys.exit(0)
'''


# ===========================================================================
# Demo
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    with tempfile.TemporaryDirectory() as workdir:
        with open(os.path.join(workdir, "check.py"), "w") as f:
            f.write(CHECK_PY)
        check_cmd = "python3 check.py"

        print("=" * 64)
        print("Task: have the agent iteratively fix add.py until `python3 add.py` prints 42")
        print(f"Working directory: {workdir}")
        print(f"Check command: {check_cmd}")
        print("=" * 64)

        reason, code = loop(check_cmd, workdir)

        print("\n" + "=" * 64)
        print(f"Exit reason: {reason.name} -- {reason.value}")
        if reason is Exit.SUCCESS:
            print(f"Passing code: {code.strip()!r}")
        print("=" * 64)
        print("Remember: verify via 'run a command, check exit code'; exit conditions need at least SUCCESS / FUSE / STALL.")
        print("Swap check_cmd for pytest, ruff, or a build command -- this loop needs zero changes.")
