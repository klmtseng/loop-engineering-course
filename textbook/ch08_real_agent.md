# Chapter 8 -- Non-Determinism and Real Agents

> **Chapter goal**: Recognize the fundamental difference between the well-behaved
> stubs from the first seven lessons and a real LLM agent -- **real agents are
> stochastic** -- and learn to design loops for a "distribution" rather than a
> "fixed value": best-so-far, retry with backoff, idempotency, and a look at
> wrapping a real LLM in a loop.
> After this chapter you will remember: **your loop must be designed for an agent
> that can drift, regress, and fail.**
>
> Reference solution: [`lesson8_real_agent.py`](../lesson8_real_agent.py)

**TL;DR**: The same prompt run twice gives different results. A loop's output
is a distribution, not a fixed value -- so track the historical best (best-so-far),
use exponential backoff for retries, and make actions idempotent.

## 8.1 Concept: Stubs Are Well-Behaved; Real Agents Are Not

The mock agents in the first seven lessons improved steadily each round and
converged in a predictable number of iterations -- that was deliberate, to let
you see the skeleton clearly. Real LLMs are different:

- **Non-deterministic**: the same prompt with the same context can produce a
  different answer on a second run.
- **They regress**: coverage climbs to 95 in round 2, then drops back to 60 in
  round 5. Progress is not monotone.
- **They fail**: context window overflow, rate limits, tool calls crash, output
  format changes unexpectedly.

> **Non-determinism does not come only from sampling** -- many people get this
> wrong. Even with `temperature=0` (greedy, no sampling at all), real inference
> services **can still produce different results across runs**: servers batch
> multiple requests together, and **batch size changes the accumulation order of
> floating-point operations** (the batch-invariance problem, systematically
> characterized and fixed by Thinking Machines Lab in 2025).
> **Conclusion: you cannot assume an agent becomes deterministic by setting
> temperature to 0. Always design for a distribution.**

`lesson8_real_agent.py` uses a randomly-walking `noisy_agent` to make this
concrete: the same loop run with 5 different seeds -- some finish in round 1,
some only by round 5, some never finish. **That is a real agent -- the result
is a distribution.**

## 8.2 A Bug You May Not Have Noticed Yet: "Look Only at the Last Round"

A very common mistake -- and one hidden in earlier lessons' code -- is:
**let the agent run N rounds, then judge only the output of the final round.**

If the agent reaches 95 in round 2 (goal met!) then drops to 75 in round 6,
this loop will report "failure" -- **it threw away the perfect result from the
middle.** It never goes wrong with a monotone stub; with a real agent it will
go wrong every time.

The fix is **best-so-far**: remember the historical best across rounds so that
a late regression cannot erase it.

```python
best = None
for i in range(1, MAX_ITERS + 1):
    cov = agent(i - 1, feedback=...)
    if best is None or cov > best:
        best = cov                 # remember the best
    if verify(best):
        return ("SUCCESS", i, best)
return ("FAIL", MAX_ITERS, best)   # even on FAIL, return best, not the last round
```

> In file-editing scenarios, "remember the best" = commit or take a worktree
> snapshot each round; on failure, `reset` to the snapshot of the best round.
> This is another use of the isolation from Chapter 5: **rollback capability.**

### Warning: best-so-far amplifies Chapter 7's Goodhart problem

best-so-far is essentially "**take the maximum verify score across all rounds**."
If verify is a **noisy or gameable proxy metric** (Chapter 7), then "taking the
max" **systematically selects the lucky run** -- this is called the
**optimizer's curse / maximization bias** (the same effect Double Q-learning in
RL was designed to correct; the auction "winner's curse" is an intuitive
analogy): the run you pick is often not the genuinely best, but the one with the
**highest noise / most gamed score.**

`lesson8`'s demo shows this: best-so-far (by proxy) selects a version with a
proxy score of 97, but its true value is only 82; the genuinely best version
(true value 86) had a proxy of only 90 and was not selected.

> **This is where Chapter 7 and Chapter 8 intersect**: best-so-far (defends
> against regression) and verify-gaming (defends against cheating) are each
> correct on their own, but together they create tension -- **running best-so-far
> on a weak verify is equivalent to actively seeking the luckiest fake-high
> score.** **Fix**: re-verify the "best" you selected using a **hold-out set**
> (Chapter 7). High proxy score != genuinely good. The more reliable your
> verify, the more trustworthy best-so-far becomes.

## 8.3 Designing for a Distribution: Retries, Backoff, Idempotency

Since agents fail randomly, your loop needs resilience:

| Problem | Fix |
|---|---|
| Sporadic failure (rate limit, 5xx, malformed output) | **Retry**, with **exponential backoff + jitter** -- do not hammer the server once per second |
| Retries cause duplicate side effects | **Idempotency**: doing the same action twice has the same effect as doing it once (Chapter 6) |
| Infinite retry loop | Retries must also have a ceiling -- it is another fuse |
| Flaky verify (same output, different verdict on two runs) | The verify itself must be stable and re-runnable; otherwise you cannot trust "did it pass" |

## 8.4 Real Agent Failure Gallery

The stub never demonstrates these, but you will hit them the moment you go
live. Worth pinning to the wall:

- **Context window overflow**: conversation keeps growing -> exceeds model limit
  -> use the context strategy from Chapter 9
- **Rate limit / 5xx**: too frequent or server down -> retry + exponential
  backoff + jitter
- **Partial file write**: action dies halfway -> idempotency + check-then-act
  (Chapter 6)
- **Flaky verify**: same output, different verdict on two runs -> verifier must
  be stable and re-runnable
- **Infinite tool-call**: agent keeps calling tools in a loop -> the max-iter
  fuse from Chapter 1 exists for exactly this

## 8.5 Hands-On: Watching a Loop Wrap a Real LLM (Optional)

```bash
python3 lesson8_real_agent.py            # default: zero API key, runs noisy stub
python3 lesson8_real_agent.py --real     # optional: connects to a real LLM (requires OPENROUTER_API_KEY)
```

**Checkpoint**: `--real` **gracefully falls back to the stub when no key is
present, printing what the real path would look like, rather than crashing.**
This is Chapter 8's lesson in action: design for failure. When a key is present,
you will see a real LLM response plus the `usage` token count -- plug that into
Chapter 3's `Budget.charge()` and the budget goes from estimated to measured.

> **The real-path skeleton:**
> `requests.post(...)` -> `r.json()["choices"][0]["message"]["content"]` for the
> reply, `r.json()["usage"]["total_tokens"]` for the cost.
> The loop skeleton does not change at all; only the `agent()` function switches
> from stub to this API call.

## 8.6 Self-Check

1. What does "real agents are stochastic" mean concretely? Why is the loop's
   output a distribution?
2. Why does "look only at the last round" not hurt with a stub but always hurt
   with a real agent?
3. How does best-so-far fix this? In a file-editing scenario, what does it
   correspond to? (Hint: git)
4. Why "exponential backoff + jitter" rather than fixed-interval hammering for
   retries?
5. Pick two items from the failure gallery and name the chapter whose tool
   addresses them.

## 8.7 Exercise

Open [`exercises/exercise8_best_so_far.py`](../exercises/exercise8_best_so_far.py),
implement `best_so_far_loop()` so that it returns the historical best even when
the agent regresses.
Run `python3 exercises/check_exercise8.py` to verify.

## 8.8 Self-Check Answers

1. Same prompt, same context -- sampling is random -> different output each run;
   multiple runs reveal a distribution over success-round and success/failure.
2. Stubs improve monotonically so the last round is always the best; real agents
   regress so the last round may be worse than the middle, and "only the last
   round" throws away the better intermediate result.
3. Remember the historical best across rounds and stop as soon as it meets the
   goal; file-editing = commit / snapshot each round, reset to the best snapshot
   on failure (Chapter 5 isolation = rollback capability).
4. Fixed-interval hammering floods an already-busy server and causes multiple
   clients to retry at the same moment; backoff + jitter staggers retries and
   gives the system room to breathe.
5. Example: context overflow -> Chapter 9 context strategy; partial file write ->
   Chapter 6 idempotency; infinite tool-call -> Chapter 1 max-iter fuse.

---

Passing condition: you can describe real-agent non-determinism, implement
best-so-far, and explain why retry backoff and idempotency are necessary.
-> [Chapter 9: Context Strategy Across Iterations](ch09_context_strategy.md)
