# Answer Key

`quiz.py` auto-grades mcq / short questions and provides model answers for reflection questions.
This file is the human-readable summary, also usable as a self-check reference for each textbook chapter.
**Recommended: try answering first, then check here.**

## Chapter 1 - The Minimal Loop
1. **(MCQ)** Difference between loop and prompt engineering -> **replaces the human who decides whether to prompt again with a program**;
   what you deliver is a system that iterates on its own (act -> verify -> decide).
2. **(Short)** The soul of a loop -> **verify**; it defines what "done" means and determines when to stop.
3. **(Reflect)** Why some goals cannot be made into a loop -> the goal must be **machine-decidable**; verify must be able to answer objectively correct or wrong, otherwise it never knows when to stop.

## Chapter 2 - Exit Conditions
1. **(MCQ)** How a between-iteration command determines pass -> **the command's exit code** (0 = pass).
2. **(Short)** Two consecutive rounds produce the same output -> **STALL**; cut losses early, no need to burn all max-iter rounds.
3. **(Reflect)** Why check output should be fed back verbatim -> it is the agent's **only clue** for the next fix.

## Chapter 3 - Safety and Cost
1. **(MCQ)** Not one of the four safety rails -> **using the latest model**; the four rails are: fuse, budget, run-log, staged rollout (L1->L3).
2. **(MCQ)** L1 (report) -> **only observes and reports, never acts** (dry-run).
3. **(Short)** run-log write mode -> **append (no overwriting)**.
4. **(Reflect)** propose/commit separation -> agent only proposes; loop decides whether to execute based on level; L1 only records proposals so zero-risk.

## Chapter 4 - maker/checker
1. **(MCQ)** Why not let the agent self-verify -> **grading inflation -- it almost always passes itself**.
2. **(Short)** What checker must return on reject -> **specific feedback on how to fix it**; otherwise the maker can only guess.
3. **(Reflect)** How to make the checker truly independent -> different system prompt, or even different model; only looks at the output, not how hard the maker tried.

## Chapter 5 - Parallelism and Isolation
1. **(MCQ)** Prerequisite for parallel loops -> **isolation** (each has its own independent workspace).
2. **(Short)** Standard git isolation mechanism -> **git worktree**.
3. **(Reflect)** Why isolation is a correctness prerequisite -> without it parallel outputs contaminate each other and cannot be trusted; it guarantees correctness, not just speed.

## Chapter 6 - Scheduling and Unattended Loops
1. **(MCQ)** Correct way to make a loop wake itself up -> **write it as `--once`, let cron call it each time** (crash-resistant).
2. **(MCQ)** Tick with no pending work -> **skip quietly and log one idle event** (doing nothing is the correct result).
3. **(Reflect)** The four steps of a tick -> triage -> act (Lessons 1/2) -> verify (Lesson 4 independent checker) -> log+decide (Lesson 3).

## Chapter 7 - verify Is a Proxy Metric
1. **(MCQ)** Easiest way for agent to make verify green -> **game verify (hard-code / weaken tests), not solve the problem**.
2. **(Short)** "When a measure becomes a target it ceases to be a good measure" -> **Goodhart's Law**.
3. **(MCQ)** Not a defense for making verify harder to game -> **letting the agent modify verify/tests** (exactly the opposite; isolation is required).
4. **(Reflect)** Why `print(20+22)` was cheating -> it hard-coded the answer and only passed one check; proves "passing verify != solving the problem"; verify is only a proxy metric.

## Chapter 8 - Non-Determinism and Real Agents
1. **(MCQ)** Biggest difference between real agent and stub -> **non-determinism (drifts, regresses, same prompt twice gives different results)**.
2. **(Short)** Remembering the historical best across rounds -> **best-so-far**.
3. **(MCQ)** Handling intermittent failures -> **exponential backoff + jitter, with a retry cap**.

## Chapter 9 - Cross-Round Context Strategy
1. **(MCQ)** Problem with stuffing memory into conversation history -> **context grows without bound, cost explodes / hits window / causes drift**.
2. **(Short)** Concise memory file written into the repo -> **(durable) spec**.
3. **(Reflect)** Three strategy trade-offs -> stateless: cheap but no memory; conversation: has memory but explodes and drifts; spec-in-repo: memory with bounded context.

## Chapter 10 - Loop-Level Evals
1. **(MCQ)** Judging whether a loop is worth deploying -> **aggregate metrics across a full task suite** (not a single task, single run).
2. **(Short)** One of the four metrics -> **mean iters / escalation rate / mean cost** (any one).
3. **(Reflect)** Why metrics must be compared -> a single number tells you nothing; only A/B reveals trade-offs and enables decisions.
