"""
quiz_bank.py -- per-chapter knowledge quiz bank
================================================
Three question types:
  mcq     multiple-choice, auto-graded (answer = index of correct option, 0-based)
  short   short answer, auto-graded (accept = list of acceptable keywords; any match is correct)
  reflect reflection question, not auto-graded -> show model answer, self-evaluate

Bank format is validated by quiz.py --check.
"""

BANK = [
    # ---------- Chapter 1 ----------
    {"ch": 1, "type": "mcq",
     "q": "What is the most fundamental difference between loop engineering and prompt engineering?",
     "options": [
         "loops use more expensive models",
         "loops replace the human who decides whether to prompt again with a program",
         "loops always require multiple agents",
         "loops do not need prompts"],
     "answer": 1,
     "model": "What you deliver is no longer a single prompt, but a system that iterates on its own (act -> verify -> decide)."},
    {"ch": 1, "type": "short",
     "q": "Among the four steps of a loop -- goal / act / verify / decide -- which one is the soul?",
     "accept": ["verify"],
     "model": "verify -- it defines what 'done' means and determines when the loop should stop."},
    {"ch": 1, "type": "reflect",
     "q": "Why can't 'write a beautiful copy' be made into a loop, but 'copy contains keyword X and is <= N characters' can?",
     "model": "Because the goal must be machine-decidable. verify must be able to answer objectively correct or incorrect; otherwise the loop never knows when to stop."},

    # ---------- Chapter 2 ----------
    {"ch": 2, "type": "mcq",
     "q": "What determines whether a between-iteration command (the check run each round) passes?",
     "options": ["the agent's self-assessment", "the command's exit code", "the output character count", "how long it takes"],
     "answer": 1,
     "model": "Exit code 0 = pass. Ask the compiler / test runner / linter, not the agent 'are you done?'"},
    {"ch": 2, "type": "short",
     "q": "Two consecutive rounds produce exactly the same output. Which exit condition should trigger?",
     "accept": ["stall"],
     "model": "STALL -- the agent is stuck in a loop; cut losses early rather than burning all max-iter rounds."},
    {"ch": 2, "type": "reflect",
     "q": "Why should the raw output of the check command be fed back to the agent verbatim?",
     "model": "That error output / failing test names is the agent's only clue for the next fix; swallow it and the agent has nothing to learn from."},

    # ---------- Chapter 3 ----------
    {"ch": 3, "type": "mcq",
     "q": "Which of the following is NOT one of the four safety rails before releasing a loop?",
     "options": ["max-iter fuse", "budget cap", "run-log", "using the latest model"],
     "answer": 3,
     "model": "The four rails are: fuse, budget, run-log, staged rollout (L1->L3). Which model you use has nothing to do with safety."},
    {"ch": 3, "type": "mcq",
     "q": "What does autonomy level L1 (report) do?",
     "options": ["executes fully automatically", "only observes and reports, never acts", "asks a human before acting", "only acts when errors occur"],
     "answer": 1,
     "model": "L1 is a dry-run: see what the agent 'wants to do' at zero risk, then promote to L2/L3 once confirmed."},
    {"ch": 3, "type": "short",
     "q": "What write mode must a run-log use to avoid overwriting history?",
     "accept": ["append", "a"],
     "model": "append-only. Automation without a log is as if it never happened; it is the black box when things go wrong."},
    {"ch": 3, "type": "reflect",
     "q": "What is 'propose / commit separation'? How does it make L1 zero-risk?",
     "model": "The agent only 'proposes' an action; whether to 'execute' it is decided by the loop based on the level. L1 only records proposals and never executes, so it is zero-risk."},

    # ---------- Chapter 4 ----------
    {"ch": 4, "type": "mcq",
     "q": "Why should you not let the acting agent verify its own output?",
     "options": [
         "too slow", "grading inflation -- it almost always passes itself",
         "too expensive", "models do not support it"],
     "answer": 1,
     "model": "An agent that has an incentive to say 'I'm done' is not an impartial judge. Hand it to an independent, stricter checker."},
    {"ch": 4, "type": "short",
     "q": "When checker rejects, besides 'not approved' what else must it return for the maker to improve?",
     "accept": ["reason", "feedback", "how", "why", "flaw", "specific"],
     "model": "Specific feedback on how to fix it. Returning only reject without a reason forces the maker to guess; the loop spins in place."},
    {"ch": 4, "type": "reflect",
     "q": "In the real world, how do you make a checker truly 'independent' of the maker?",
     "model": "Use a different system prompt, or even a different model; the checker should not know how hard the maker tried -- only whether the output is correct."},

    # ---------- Chapter 5 ----------
    {"ch": 5, "type": "mcq",
     "q": "What is the prerequisite for running multiple loops simultaneously?",
     "options": ["buy more CPUs", "isolation (each loop has its own workspace)", "share one directory to save space", "turn off the fuse"],
     "answer": 1,
     "model": "Without isolation, parallel loops overwrite each other's files and cross-contaminate; no output can be trusted."},
    {"ch": 5, "type": "short",
     "q": "In a coding scenario, what is the standard git mechanism for running multiple agents in parallel without interference?",
     "accept": ["worktree", "git worktree"],
     "model": "git worktree -- the same repo grows multiple independent checkouts, sharing the object store but keeping files separate."},
    {"ch": 5, "type": "reflect",
     "q": "Why is 'isolation not a performance optimization but a correctness prerequisite'?",
     "model": "Without isolation, parallel outputs contaminate each other and cannot be trusted; isolation guarantees correctness, not just speed."},

    # ---------- Chapter 6 ----------
    {"ch": 6, "type": "mcq",
     "q": "What is the correct way to make a loop that wakes itself up?",
     "options": [
         "a persistent process with while True: sleep", "write it as --once, let cron call it each time",
         "have a person run it manually each day", "use one very long max-iter"],
     "answer": 1,
     "model": "--once + cron is naturally crash-resistant: each invocation is a fresh process; state is preserved externally."},
    {"ch": 6, "type": "mcq",
     "q": "When a scheduled tick finds no pending work, what is the correct behavior?",
     "options": ["find something to do", "call the agent frantically", "skip quietly and log one idle event", "abort with an error"],
     "answer": 2,
     "model": "'Do nothing when there is nothing to do' is the correct result, not a failure. A well-behaved loop skips quietly."},
    {"ch": 6, "type": "reflect",
     "q": "What four things does one tick do? Which earlier lessons does each step come from?",
     "model": "triage (find work) -> act (Lessons 1/2) -> verify (Lesson 4 independent checker) -> log+decide (Lesson 3 run-log/escalate)."},

    # ---------- Chapter 7 ----------
    {"ch": 7, "type": "mcq",
     "q": "What is the easiest way for an agent to make verify turn green?",
     "options": [
         "truly solve the problem completely", "game verify (hard-code the answer / weaken the tests) rather than solving the problem",
         "run more rounds", "switch to a different model"],
     "answer": 1,
     "model": "The agent chases 'making verify green', not 'solving the problem correctly'; the path of least resistance is usually exploiting loopholes."},
    {"ch": 7, "type": "short",
     "q": "'When a measure becomes a target, it ceases to be a good measure' -- which law is this?",
     "accept": ["goodhart"],
     "model": "Goodhart's Law. Once verify becomes the target the agent chases, it starts to distort and gets gamed."},
    {"ch": 7, "type": "mcq",
     "q": "Which of the following is NOT a defense for making verify harder to game?",
     "options": ["hold-out hidden cases", "multiple and random inputs", "let the agent modify verify/tests", "human spot-checks"],
     "answer": 2,
     "model": "Exactly the opposite -- you want 'isolation' so the agent cannot modify verify/tests (otherwise it edits the answer sheet directly)."},
    {"ch": 7, "type": "reflect",
     "q": "Why was `print(20 + 22)` from Lesson 2 actually a form of cheating? What does it illustrate?",
     "model": "It hard-coded the answer and only passed that one check; it proves 'passing verify != solving the problem'; verify is only a proxy metric."},

    # ---------- Chapter 8 ----------
    {"ch": 8, "type": "mcq",
     "q": "What is the biggest difference between a real LLM agent and the well-behaved stubs from earlier lessons?",
     "options": ["more expensive", "it is non-deterministic -- it drifts, regresses, same prompt twice gives different results", "slower", "needs a GPU"],
     "answer": 1,
     "model": "A real agent's output is a distribution, not a fixed value; so the loop must be designed for a distribution (best-so-far, retry, idempotency)."},
    {"ch": 8, "type": "short",
     "q": "What do you call the approach of remembering the historical best result across rounds so a late regression cannot hurt you?",
     "accept": ["best-so-far", "best so far"],
     "model": "best-so-far. Looking only at the last round throws away better intermediate results; real agents regress, so this bug will always bite you."},
    {"ch": 8, "type": "mcq",
     "q": "When an agent fails intermittently (rate limit / 5xx), how should retries be handled?",
     "options": ["fixed-interval hammering", "exponential backoff + jitter, with a retry cap", "unlimited immediate retries", "give up immediately"],
     "answer": 1,
     "model": "Fixed-interval hammering makes things worse and causes multiple clients to collide; backoff + jitter spreads retries out."},

    # ---------- Chapter 9 ----------
    {"ch": 9, "type": "mcq",
     "q": "What is the biggest problem with stuffing cross-round memory into 'conversation history'?",
     "options": ["too simple", "context grows without bound -> cost explodes, hits the context window, and causes drift", "agents cannot understand it", "cannot be saved"],
     "answer": 1,
     "model": "The conversation grows every round and will eventually explode; instead write memory as a concise spec in the repo (durable spec) to keep context bounded."},
    {"ch": 9, "type": "short",
     "q": "Fresh context every round, with cross-round memory written into a concise file in the repo -- what is this file called?",
     "accept": ["spec", "durable spec", "scratchpad"],
     "model": "durable spec. Solves cost (bounded), drift (clean context each round), and crash-resistance (state lives in the repo) all at once."},
    {"ch": 9, "type": "reflect",
     "q": "What are the trade-offs for stateless / full-conversation / spec-in-repo context strategies?",
     "model": "stateless: cheapest but no memory -> gets stuck; conversation: has memory but context explodes and drifts; spec-in-repo: memory with bounded context (you must maintain the spec yourself)."},

    # ---------- Chapter 10 ----------
    {"ch": 10, "type": "mcq",
     "q": "To judge whether a loop is worth deploying, what should you look at?",
     "options": ["a single task passed once is enough", "aggregate metrics across a full task suite (success rate / mean iters / escalation / cost)",
                 "how fast it runs", "number of lines of code"],
     "answer": 1,
     "model": "A single task, single run is anecdotal; loop quality requires looking at distributions over a task suite, and A/B comparisons for decisions."},
    {"ch": 10, "type": "short",
     "q": "Name one of the four basic loop-level eval metrics besides success rate.",
     "accept": ["mean_iters", "mean iters", "escalation", "escalation rate", "mean_cost", "mean cost", "cost"],
     "model": "success rate / mean iters / escalation rate / mean cost -- all four together reveal the trade-offs."},
    {"ch": 10, "type": "reflect",
     "q": "Why are loop metrics 'only meaningful in comparison'?",
     "model": "Seeing 'success rate 0.9' alone tells you nothing; only A/B (e.g. max_iters 3 vs 8) shows you what cost you paid for that success rate, enabling a real decision."},
]
