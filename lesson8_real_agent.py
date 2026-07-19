"""
Lesson 8 -- Non-Determinism and Real Agents
============================================
All earlier agents were "well-behaved": they improved steadily each round and
converged in a predictable number of iterations. Real LLM agents are not like that.

    Real agents are stochastic. The same prompt run twice gives a different result.
    They drift, regress, succeed in round 3 one time and round 6 another time.
    (And non-determinism does not come only from sampling: even with temperature=0,
     server-side batching changes the floating-point accumulation order, so real
     inference services are still non-deterministic -- see Thinking Machines Lab
     2025 "Defeating Nondeterminism in LLM Inference".)

This lesson uses a randomly-walking `noisy_agent` to show this concretely, and
exposes a bug you may not have noticed yet: **if your loop "looks only at the
last round", it will throw away better results from the middle.**

The task is now more realistic: push test coverage to >= 90%. The agent reports
a coverage number each round; on average it trends up, but with noise per round
-- it might reach 95 in round 4 then drop back to 83 in round 6.

Run:
    python3 lesson8_real_agent.py
    python3 lesson8_real_agent.py --animate
    python3 lesson8_real_agent.py --real     # optional: connect to a real LLM (needs OPENROUTER_API_KEY; falls back to stub if absent)
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim

GOAL = 90        # coverage goal
MAX_ITERS = 6


def verify(coverage):
    return coverage >= GOAL


# ===========================================================================
# noisy_agent -- a randomly-drifting stub (seed-controlled for reproducible grading)
# ===========================================================================
def make_noisy_agent(seed):
    rng = random.Random(seed)

    def agent(attempt, feedback):
        # Base coverage trends up slowly with attempt, but each round gets Gaussian noise -> bounces around the goal
        base = 78 + attempt * 2.5
        return max(0, min(100, round(rng.gauss(base, 11))))

    return agent


# ===========================================================================
# Three loops: normal checks each round; naive looks only at the last; best-so-far tracks the best
# ===========================================================================
def loop_each_iter(agent):
    """Normal approach: check every round, stop as soon as goal is met.
    Used here to show the distribution of 'which round succeeds'."""
    for i in range(1, MAX_ITERS + 1):
        cov = agent(i - 1, feedback="")
        if verify(cov):
            return ("SUCCESS", i, cov)
    return ("FAIL", MAX_ITERS, cov)


def naive_final_only(agent):
    """Common hidden bug: let the agent run N rounds and judge only the LAST round's output.
    If the middle round hit the goal but the last one regressed, this reports failure
    and throws away the good result."""
    val = None
    for i in range(1, MAX_ITERS + 1):
        val = agent(i - 1, feedback="")
    return ("SUCCESS" if verify(val) else "FAIL", MAX_ITERS, val)


def best_so_far_loop(agent):
    """Correct approach: remember the historical best across rounds; late regression cannot hurt it."""
    best = None
    for i in range(1, MAX_ITERS + 1):
        cov = agent(i - 1, feedback=f"current best: {best}")
        if best is None or cov > best:
            best = cov
        if verify(best):
            return ("SUCCESS", i, best)
    return ("FAIL", MAX_ITERS, best)


# ===========================================================================
# Warning: best-so-far has a trap when verify is a noisy proxy metric (connects to Lesson 7)
# ===========================================================================
# best-so-far = "take the maximum verify score across all rounds." But if verify is a noisy
# or gameable 'proxy metric', taking the max will systematically select lucky runs --
# this is called optimizer's curse / maximization bias (Double Q-learning in RL fixes
# the same over-estimation; the auction "winner's curse" is an intuitive analogy):
# the run you pick is often the one with the highest noise, not the genuinely best.
def proxy_trap(seed, n=8):
    import random as _r
    rng = _r.Random(seed)
    trues = [rng.randint(70, 88) for _ in range(n)]              # true quality of each attempt
    proxies = [t + round(rng.gauss(0, 10)) for t in trues]       # what verify actually sees (noisy)
    picked = max(range(n), key=lambda i: proxies[i])             # best-so-far picks by proxy
    actual_best = max(range(n), key=lambda i: trues[i])          # the truly best attempt
    return trues, proxies, picked, actual_best


# ===========================================================================
# Optional: a real LLM agent (OpenAI-compatible API via OpenRouter)
# ===========================================================================
def try_real_agent_once():
    """Shows how to wrap one real LLM call in a loop. Falls back gracefully if no key -- never crashes the lesson."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("\n(--real: no OPENROUTER_API_KEY detected -> falling back to noisy stub.)")
        print(" To try the real path: export OPENROUTER_API_KEY=sk-or-... then add --real.")
        print(" The real path looks like this (excerpt):")
        print('   r = requests.post(URL, headers={"Authorization": f"Bearer {key}"},')
        print('                     json={"model": M, "messages": msgs}, timeout=60)')
        print('   reply = r.json()["choices"][0]["message"]["content"]')
        print('   used  = r.json()["usage"]["total_tokens"]   # OpenRouter usage also gives cost in dollars')
        return False
    try:
        import requests
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "openai/gpt-4o-mini",
                  "messages": [{"role": "user", "content": "Summarize loop engineering in one sentence."}]},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        print("\n[Real LLM response]", data["choices"][0]["message"]["content"])
        print("[Real token count]", data["usage"]["total_tokens"], "<- plug into Budget for measured cost")
        return True
    except Exception as e:
        print(f"\n(--real: call failed {e} -> fell back to stub. Network/quota issues should not block this lesson.)")
        return False


FAILURE_GALLERY = """\
Real agent runtime failure catalog (the stub never shows these, but you will hit them in production):
  * Context window overflow  conversation keeps growing -> exceeds model limit -> use Ch.9 context strategy
  * Rate limit / 5xx         too frequent or server down -> retry + exponential backoff + jitter
  * Partial file write       action dies halfway -> idempotency + check-then-act (Ch.6)
  * Flaky verify             same output, different verdict on two runs -> verifier must be stable and re-runnable
  * Infinite tool-call       agent keeps calling in a loop -> the max-iter fuse from Ch.1 exists for this
"""


if __name__ == "__main__":
    anim.from_argv()

    if "--real" in sys.argv:
        try_real_agent_once()

    print("=" * 64)
    print("Non-determinism: same loop, 5 different seeds, each gives a different outcome")
    print("=" * 64)
    for seed in range(5):
        status, iters, val = loop_each_iter(make_noisy_agent(seed))
        anim.fuse(seed, 5, label="seed")
        print(f"  seed={seed}: same loop -> {status:7s} in round {iters}, coverage {val}")
        anim.pause(0.5)
    print("-> That is a real agent: the same loop produces a distribution, not a fixed value.")

    print("\n" + "=" * 64)
    print("Hidden bug: 'look only at the last round' throws away better intermediate results")
    print("=" * 64)
    # Find a seed where naive (last-round-only) fails but best-so-far succeeds
    for seed in range(500):
        n = naive_final_only(make_noisy_agent(seed))
        b = best_so_far_loop(make_noisy_agent(seed))
        if n[0] == "FAIL" and b[0] == "SUCCESS":
            print(f"  seed={seed}:")
            print(f"    naive_final_only -> {n[0]} (only trusts last round: {n[2]})")
            print(f"    best_so_far_loop -> {b[0]} (remembered round {b[1]}'s peak: {b[2]})")
            print("  ⚠️  same random sequence; naive says failure, best-so-far says success --")
            print("       the only difference is 'whether the historical best was remembered'.")
            break

    print("\n" + "=" * 64)
    print("But best-so-far has a trap: taking the max of a noisy proxy metric selects lucky runs (connects to Lesson 7)")
    print("=" * 64)
    for seed in range(300):  # find a case where proxy-selected != truly best
        trues, proxies, picked, best = proxy_trap(seed)
        if picked != best:
            print(f"  best-so-far (by proxy) selected attempt {picked}: proxy={proxies[picked]}, but true value is only {trues[picked]}")
            print(f"  the truly best attempt was {best}: true value {trues[best]} (its proxy was {proxies[best]}, so it was not selected)")
            print(f"  -> taking the max of a noisy proxy metric systematically picks the luckiest run,")
            print(f"     not the genuinely best one (optimizer's curse / maximization bias).")
            print(f"  -> fix: re-verify your selected 'best' with a Lesson 7 hold-out. high proxy != truly good.")
            break

    print("\n" + "=" * 64)
    print(FAILURE_GALLERY + "=" * 64)
    print("Conclusion: real agents are stochastic. Design your loop for a distribution, not a fixed value --")
    print("  remember the best (best-so-far), set a fuse, retry with backoff, make actions idempotent.")
