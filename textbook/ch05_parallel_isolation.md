# Chapter 5 -- Parallelism and Isolation

> **Chapter goal**: Learn how to run multiple loops simultaneously and understand
> that isolation is the prerequisite for parallelism. Get familiar with `git
> worktree`, the standard isolation tool for coding workflows. After this chapter
> you will remember: **isolation is not a performance optimization -- it is a
> correctness requirement.**
>
> Reference solution: [`lesson5_parallel_isolation.py`](../lesson5_parallel_isolation.py)

**TL;DR**: To run multiple loops in parallel you must first **isolate** them.
In coding workflows use `git worktree` to give each loop an independent
checkout; when done, pick the best one and merge.

> **Navigation note (no threading background needed)**
> The demo uses `ThreadPoolExecutor` to run several workers concurrently --
> just think of it as "opening 3 copies of the agent and letting each do its
> own thing." You do **not** need to understand thread internals; the chapter's
> point is **"isolate before parallelizing"**, not parallel programming
> techniques. Copy-paste the code and run it; focus on the isolated vs.
> shared-file contrast.

## 5.1 Concept: The Temptation and the Trap

Once a single loop is working, the very next thought is almost always:
"Can I run several at once?"

- Three agents each fixing a different bug simultaneously.
- Three refactoring strategies running in parallel; pick the best at the end.
- A dependency upgrade applied to ten repos at the same time.

You can. But there is a trap: **if they share the same working directory,
they will step on each other.**

Multiple workers writing to the same file at the same time produces
**interleaved lines** -- you cannot tell who wrote what or in what order
(provenance and ordering are lost) -- and the result is an artifact that no
single agent can stand behind.

> **Precise mechanics**: the demo uses small `append` writes, so what you
> observe is **line interleaving** (provenance/ordering loss), not bit-level
> corruption or one file overwriting another. And each line is intact
> **not because of the GIL** -- the GIL serializes Python bytecodes but does
> **not** guarantee OS-level write atomicity. The real reason individual lines
> survive is that each is one small, file-close-flushes write() syscall, and
> `O_APPEND` makes "seek to end + write" atomic. **Note: this is not strictly
> guaranteed for regular files on POSIX and is not portable** (larger,
> non-atomic writes will still interleave at the bit level). So the correct
> answer is always isolation, not betting on write atomicity. For parallel
> agent output, losing provenance and ordering is already fatal.

## 5.2 Concept: git worktree -- One Repo, Multiple Independent Working Directories

The standard isolation tool for coding workflows is `git worktree`. It gives
one repo multiple independent checkouts that **share the git object store but
have completely separate file trees**:

```bash
git worktree add ../wt-fix-a -b fix-a     # a new independent working directory on branch fix-a
git worktree add ../wt-fix-b -b fix-b     # another, on fix-b
git worktree add ../wt-fix-c -b fix-c

# three agents each run their loop inside their own worktree
# files never interfere; commits land on separate branches
# when done, compare branches and merge the best one

git worktree remove ../wt-fix-a           # clean up
```

Compared with cloning the repo three times, a worktree shares the object
store (faster, less disk space). Compared with sharing one directory, it
gives each loop a clean, independent, disposable sandbox. This is the
mechanism Claude Code and similar tools use under the hood when they run
parallel agents.

## 5.3 Hands-On

`lesson5_parallel_isolation.py` simulates worktree isolation using temporary
directories (standard library only, for clarity), and deliberately contrasts
two scenarios:

```bash
python3 lesson5_parallel_isolation.py
```

**Checkpoint 1 (isolated)**: Scenario 1 gives each worker its own directory.
Read the output -- each worker's private file contains only its own lines,
untouched by anyone else.
The key line is `wt = os.path.join(base, f"wt-{w}")`: one directory per
worker.

**Checkpoint 2 (disaster)**: Scenario 2 has all three workers share a single
`result.txt`.
Read the output -- lines from all three workers are scrambled together;
no single agent can be held responsible for the file. **This is parallelism
without isolation.**

> **Note**: this lesson uses threads + temp directories to *simulate* isolation
> so you can see the effect with zero dependencies. Real projects should use
> `git worktree` -- it also gives you branch management and a clean merge path.

## 5.4 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Parallel outputs contaminate each other | Multiple loops share a working directory / file | Give each loop its own worktree or independent directory |
| Cannot create a worktree | Path already exists / branch name collision | Use a different path or branch name, or `git worktree remove` first |
| No speedup from parallelism | Work is CPU-bound and you used threads | Switch to multiple processes, or recognize that the bottleneck is the LLM API not the local machine |
| Stale worktrees piling up | Forgot to remove them | Always `git worktree remove` at cleanup, or run `git worktree prune` |

## 5.5 Self-Check

1. What is the biggest risk of running multiple loops in parallel?
2. How does `git worktree` differ from cloning the repo three times, and from
   sharing one directory?
3. Why is "isolation a correctness requirement, not a performance optimization"?
4. In demo scenario 2, why can "no single agent be held responsible" for the
   shared file?
5. What is typically the next step after N parallel loops finish? (Hint: branch)

## 5.6 Further Exercises

- **Real worktree**: in an actual git repo, manually run `git worktree add` for
  three branches, edit a file in each, `git worktree list` to see status, then
  remove them all. Feel the difference from cloning.
- **Pick the best**: modify the demo so each worker returns a "score"; after all
  workers finish, automatically select the highest-scoring result (this is the
  "run multiple strategies in parallel, pick the best" skeleton).
- **Isolation assertion**: at the start of each worker, assert that its workdir is
  empty and distinct from every other worker's workdir. Make "no isolation" a
  bug that is caught immediately, not discovered later when the output is already
  corrupt.

## 5.7 Exercise

Open [`exercises/exercise5_parallel_isolation.py`](../exercises/exercise5_parallel_isolation.py),
implement `run_isolated()` (each worker gets its own dedicated directory), then
run `python3 exercises/check_exercise5.py` to verify.

## 5.8 Self-Check Answers

1. Multiple loops share a working directory -> lines interleave, provenance and
   ordering are lost (provenance loss); no agent can be held responsible for the
   output.
2. Worktree: same repo, multiple independent checkouts, shared object store,
   separate file trees, faster and uses less disk than cloning; cloning is
   slower and wastes space; sharing one directory causes mutual contamination.
3. Without isolation, parallel outputs contaminate each other and results are
   untrustworthy; isolation protects correctness, not speed.
4. Nine lines mixed from three authors, interleaved in an unpredictable order --
   no agent can point to its section.
5. Compare branches, pick the best one, and merge it into the main line
   (parallel multi-strategy, best-of-N).

---

Passing condition: you can state the risk of parallelism, explain the
worktree isolation model, and point to where "contamination" occurs in the demo.
The last chapter assembles all five lessons' parts, hooks them to a scheduler,
and lets the loop wake itself up.
-> [Chapter 6: Scheduling and Unattended Loops](ch06_scheduling.md)
