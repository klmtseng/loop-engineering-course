"""
Lesson 5 -- Parallelism and Isolation
======================================
Once a single loop is working, the very next thought is almost always:
"Can I run several at once?" For example, three agents each fixing a
different bug, or three refactoring strategies running in parallel.

You can -- but there is a trap: **if they share the same working directory,
they will step on each other.** The demo shows one concrete form: multiple
workers writing to the same file simultaneously results in **interleaved
lines** where no one can tell who wrote what or in what order (provenance and
ordering are lost).
(Precise mechanics: this is not "bit-level corruption" -- each line is intact.
But not because of the GIL (the GIL serializes Python bytecodes, not OS write
atomicity). Lines survive because each is one small, file-close-flushes
write(), and O_APPEND makes "seek to end + write" atomic on most POSIX systems
for small writes -- but this is not strictly guaranteed for regular files on all
POSIX systems and is not portable for larger, non-atomic writes. The point
stands: for parallel agent output, losing provenance and ordering is already fatal.
Isolation is the answer, not betting on write atomicity.)

The standard isolation tool for coding workflows is git worktree:

    git worktree add ../wt-fix-a -b fix-a    # same repo, new independent working directory
    git worktree add ../wt-fix-b -b fix-b    # separate branch, no interference
    # three agents each run their loop inside their own worktree; merge the best when done
    git worktree remove ../wt-fix-a

Each worktree is an independent checkout of the same repo, sharing the git
object store but with separate file trees, so parallel agents never interfere
and each agent's commits land cleanly on its own branch.

This lesson uses "one temp directory per worker" to simulate worktree isolation
(standard library only, for clarity), and deliberately shows you the disaster
first ("shared directory -> stepping on each other") then the solution
("each isolated -> clean output").
The real worktree commands are in the textbook Chapter 5.

Run:
    python3 lesson5_parallel_isolation.py
    python3 lesson5_parallel_isolation.py --animate    # slow-motion: isolated vs. contaminated
"""

import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# A small loop that "does work and leaves a trace" -- each worker runs one copy
# ===========================================================================
def run_one_loop(name, workdir, shared_file):
    """Simulates an agent running 3 rounds inside workdir, writing one line per
    round to its own file. Also writes to shared_file -- to demonstrate the
    consequences of a 'shared file' being written to by multiple workers."""
    own_file = os.path.join(workdir, "result.txt")
    for i in range(3):
        # Private file: safe as long as workdir is unique
        with open(own_file, "a") as f:
            f.write(f"{name} round {i}\n")
        # Shared file: multiple workers racing for the same file = disaster
        with open(shared_file, "a") as f:
            f.write(f"{name} round {i}\n")
        time.sleep(0.01)  # amplify the race, make interleaving more visible
    # Report what this worker sees in its own private file (should be clean)
    with open(own_file) as f:
        return name, f.read().strip().replace("\n", " | ")


# ===========================================================================
# Demo
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    workers = ["fix-A", "fix-B", "fix-C"]

    # -----------------------------------------------------------------------
    # Scenario 1: each loop gets its own isolated directory (= worktree effect)
    # -----------------------------------------------------------------------
    print("=" * 64)
    print("Scenario 1: each loop has its own isolated working directory (simulates git worktree)")
    print("=" * 64)
    anim.step("🧵", "launching 3 loops in parallel, each with a dedicated directory...")
    anim.pause(1.0)
    with tempfile.TemporaryDirectory() as base:
        shared = os.path.join(base, "shared.txt")
        open(shared, "w").close()

        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = []
            for w in workers:
                wt = os.path.join(base, f"wt-{w}")  # <- one directory per worker; this is the key line
                os.makedirs(wt)
                futures.append(ex.submit(run_one_loop, w, wt, shared))
            results = [f.result() for f in futures]

        print("\nEach worker's private file content (isolated -> clean, not contaminated by others):")
        for name, content in sorted(results):
            print(f"  {name}: {content}")

    # -----------------------------------------------------------------------
    # Scenario 2: all three loops share one file (no isolation -> disaster)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 64)
    print("Scenario 2: three loops share one file (no isolation = disaster)")
    print("=" * 64)
    anim.step("🧵", "launching 3 loops in parallel, but this time sharing one directory...")
    anim.pause(1.0)
    with tempfile.TemporaryDirectory() as base:
        shared = os.path.join(base, "shared.txt")
        open(shared, "w").close()
        only_dir = os.path.join(base, "wt-shared")
        os.makedirs(only_dir)

        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(run_one_loop, w, only_dir, shared) for w in workers]
            [f.result() for f in futures]

        with open(os.path.join(only_dir, "result.txt")) as f:
            lines = f.read().strip().split("\n")
        print("\nShared result.txt content (all three workers' lines interleaved -- no one can trust it):")
        for ln in lines:
            print(f"  {ln}")
        print(f"\n  -> {len(lines)} lines written to one file by {len(set(l.split()[0] for l in lines))} workers.")
        print("    No single agent can be held responsible for this output.")

    print("\n" + "=" * 64)
    print("Conclusion: to run in parallel, first isolate. In coding workflows, use `git worktree`")
    print("to give each loop an independent checkout; pick the best branch and merge when done.")
    print("Isolation is not a performance optimization -- it is a correctness requirement.")
    print("=" * 64)
