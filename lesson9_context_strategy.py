"""
Lesson 9 -- Context Strategy Across Iterations
===============================================
This is the most central, least-discussed decision in real loop engineering:
**what context do you feed the agent each round?**

Earlier lessons' mocks accepted only a single `feedback` string, hiding this
entire decision. In a real project you must choose:

    1. stateless re-task   -- fresh context every round = task + one feedback message.
                              Cheap, but the agent has no memory.
    2. full conversation   -- keep accumulating the entire conversation history.
                              Agent remembers everything, but context grows every round
                              -> cost explodes linearly, will eventually hit the context
                              window, longer context = more drift.
    3. spec-in-repo        -- fresh context every round, but persist "cross-round state"
                              in a concise spec/scratchpad file inside the repo.
                              Agent has memory; context is bounded.
                              This is the production default for coding agents.

This lesson uses a "guess the secret number" task to compare all three: same
goal of guessing 13, see who can converge and how much context each burns.

Run:
    python3 lesson9_context_strategy.py
    python3 lesson9_context_strategy.py --animate
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim

SECRET = 13
UNIVERSE = list(range(1, 21))   # 1..20
MAX_ITERS = 20

# Token counts below are "relative indicators", not real tokenization -- the point
# is how they grow with the number of rounds, not the absolute values.
# (For real token counts, read usage from the API response as shown in Lesson 3.)
BASE_TOKENS = 30        # tokens for the task description itself
MSG_TOKENS = 12         # tokens added per conversation turn
SPEC_TOKENS = 8         # tokens for a concise spec (e.g., "tried: 1-7, 12")


# ===========================================================================
# Three strategies: each decides (how big is this round's context, what to guess)
# ===========================================================================
def strat_stateless(tried, history):
    """Only sees the 'latest feedback message'. Context stays minimal, but no memory ->
    simulate 'no memory = gets stuck in a loop' with a fixed small cycle (1..5)."""
    ctx = BASE_TOKENS                      # always just task + one feedback
    guess = (len(history) % 5) + 1         # cycles through 1..5, never reaches 13
    return ctx, guess


def strat_conversation(tried, history):
    """Keeps the entire conversation history in context. Remembers everything ->
    never repeats a guess -> will converge, but context grows linearly every round."""
    ctx = BASE_TOKENS + len(history) * MSG_TOKENS   # <- grows every round
    guess = next(n for n in UNIVERSE if n not in tried)
    return ctx, guess


def strat_spec_in_repo(tried, history):
    """Fresh context every round, but compresses 'tried set' into a concise spec.
    Remembers everything; context stays bounded -> best of both worlds."""
    ctx = BASE_TOKENS + SPEC_TOKENS                 # <- does not grow with history
    guess = next(n for n in UNIVERSE if n not in tried)
    return ctx, guess


def strat_stateless_with_signal(bounds):
    """Key counter-example: this strategy is still 'stateless' (only looks at what
    is passed in), but what is passed in is not a thin message -- it is the range
    (lo, hi) accumulated from 'too high / too low' comparison signals.
    It binary-searches to the answer -- and context stays bounded.
    Proof: the failure of the stateless strategy is not 'stateless' per se; it is
    'feedback too thin to carry the required memory'."""
    lo, hi = bounds
    ctx = BASE_TOKENS + 4          # carry only two boundary numbers -> still bounded
    return ctx, (lo + hi) // 2


def run(strategy):
    tried, history, ctx_log = [], [], []
    for i in range(1, MAX_ITERS + 1):
        ctx, guess = strategy(tried, history)
        ctx_log.append(ctx)
        history.append(guess)
        if guess not in tried:
            tried.append(guess)
        if guess == SECRET:
            return ("SUCCESS", i, max(ctx_log), sum(ctx_log))
    return ("FAIL", MAX_ITERS, max(ctx_log), sum(ctx_log))


def run_signal():
    """stateless, but feedback carries 'too high / too low' accumulated as a range -> binary search."""
    lo, hi, ctx_log = 1, 20, []
    for i in range(1, MAX_ITERS + 1):
        ctx, guess = strat_stateless_with_signal((lo, hi))
        ctx_log.append(ctx)
        if guess == SECRET:
            return ("SUCCESS", i, max(ctx_log), sum(ctx_log))
        lo, hi = (guess + 1, hi) if guess < SECRET else (lo, guess - 1)
    return ("FAIL", MAX_ITERS, max(ctx_log), sum(ctx_log))


if __name__ == "__main__":
    anim.from_argv()
    print("=" * 70)
    print(f"Task: guess the secret number {SECRET} (1..20). Compare three context strategies: who converges and at what cost?")
    print("=" * 70)
    print(f"  {'Strategy':<24}{'Result':<10}{'Rounds':<8}{'Peak ctx':<12}{'Total ctx'}")
    print("  " + "-" * 60)
    for name, strat in [("stateless (thin feedback)", strat_stateless),
                        ("full conversation", strat_conversation),
                        ("spec-in-repo", strat_spec_in_repo)]:
        anim.step("->", f"running {name}")
        status, iters, peak, total = run(strat)
        print(f"  {name:<28}{status:<10}{iters:<8}{peak:<12}{total}")
        anim.pause(0.6)
    # Counter-example: still stateless, but feedback carries 'too high / too low' range -> binary search works
    anim.step("->", "running stateless (with signal)")
    status, iters, peak, total = run_signal()
    print(f"  {'stateless (with signal)':<28}{status:<10}{iters:<8}{peak:<12}{total}")
    print("=" * 70)
    print("Reading the table:")
    print("  * stateless (thin feedback): cheapest context, but feedback cannot carry memory -> FAIL.")
    print("  * full conversation: converges, but peak/total context is largest -> cost explodes, will hit window.")
    print("  * spec-in-repo: converges, and context stays bounded -> the production default.")
    print("  * stateless (with signal): ★ still no memory, but better feedback -> binary search, cheapest of all.")
    print("-" * 70)
    print("Precise conclusion (do not over-generalize): **the failure culprit is not 'stateless' itself,")
    print("it is 'feedback too thin to carry the required memory'.**")
    print("  With enough signal, stateless can succeed too; what you really want to avoid is stuffing")
    print("  memory into an unbounded-growing conversation history.")
    print("Mindset: write cross-round memory into a concise spec inside the repo; re-task with a clean context.")
    print("         This is the durable spec in loop engineering.")
