# Chapter 9 -- Context Strategy Across Iterations

> **Chapter goal**: Understand the most central, least-discussed design decision
> in real loop engineering -- **what context should you feed the agent each
> round?** Compare stateless / full-conversation / spec-in-repo strategies
> and their trade-offs, and learn the production default: clean context plus
> a concise spec inside the repo.
> After this chapter you will remember: **do not stuff memory into conversation
> history; stuff it into the repo.**
>
> Reference solution: [`lesson9_context_strategy.py`](../lesson9_context_strategy.py)

**TL;DR**: Conversation history grows without bound, exploding cost and causing
drift; write cross-round memory as a concise spec inside the repo, and re-task
the agent each round with a clean context + that spec -- this is the durable
spec, the default for coding agents.

## 9.1 Concept: The Decision Hidden by Earlier Lessons

The mock agents in earlier lessons received only a single `feedback` string.
But in a real project you must decide every round what to feed the agent:

| Strategy | Context each round | Advantage | Fatal flaw |
|---|---|---|---|
| **stateless (thin feedback)** | task + one thin feedback message | smallest context, cheapest | **when feedback cannot carry the needed memory**, repeats mistakes, cannot converge |
| **full conversation** | entire accumulated conversation history | agent remembers everything | context grows larger every round -> cost explodes linearly, will eventually hit context window, longer context = more drift |
| **spec-in-repo** | clean context + one concise spec file | has memory **and** bounded context | you must maintain that spec yourself |

## 9.2 Seeing the Gap in Numbers

`lesson9_context_strategy.py` runs four strategies on the same task (guess the
secret number 13) and measures context cost:

```
Strategy                   Result    Rounds  Peak ctx  Total ctx
stateless (thin feedback)  FAIL      20      30        600    <- feedback too thin, no memory -> can't converge
full conversation          SUCCESS   13      174       1326   <- converges but context explodes
spec-in-repo               SUCCESS   13      38        494    <- converges with bounded context
stateless (with signal)    SUCCESS   4       34        136    <- still no memory, but better feedback -> binary search, cheapest
```

**Key insight (and a common over-generalization to avoid)**: the failure in the
first row is **not** caused by "stateless" per se -- look at the last row. Same
stateless approach, same absence of memory; just replace the thin feedback with
"too high / too low" (a cumulative range signal), and the agent binary-searches
to the answer in 4 rounds with the smallest context of all. **The precise claim
is: stateless fails only when a single feedback message cannot carry the
required memory.**

Why recommend spec-in-repo then? Because in many real tasks the "required
memory" cannot be compressed into a comparison signal (e.g., "which files have
been changed so far and why they were designed that way"). In those cases writing
memory into a repo spec is more practical than conversation, which has no bound.

## 9.3 Concept: Durable Spec -- Memory in the Repo, Not the Conversation

The key insight:

> **Do not stuff cross-round memory into conversation history (it grows without
> bound). Write it into a concise spec/scratchpad inside the repo; re-task the
> agent each round with a clean context + that spec.**

This is what real loop-engineering frameworks call the **durable spec**. It
solves three problems at once:

- **Cost**: context is bounded and does not grow with the number of rounds.
- **Drift**: each round starts fresh, not anchored to dozens of rounds of noise.
- **Crash resilience**: the spec is in the repo; if the process dies and
  restarts, the memory is still there (echoing Chapter 6's external state
  storage).

In the coding-agent world this spec is often a `PLAN.md` / `TODO.md` / test
file / issue description inside the repo -- the agent reads and updates it
each round rather than relying on remembering something said thirty rounds ago.

## 9.4 Hands-On

```bash
python3 lesson9_context_strategy.py
```

**Checkpoint**: Compare the `peak context` column. The conversation strategy's
peak is several times larger than spec-in-repo's -- and **it will grow without
bound as the task gets longer**. Imagine a task requiring 100 rounds: the
conversation approach would have blown past the context window long before
finishing. spec-in-repo stays the same size regardless of the number of rounds.

## 9.5 Self-Check

1. What are the three context strategies? What is each one's advantage and
   fatal flaw?
2. Why will full conversation "eventually hit the context window"? What other
   problem does it have besides cost?
3. What is a durable spec? What three problems does it solve simultaneously?
4. In coding-agent practice, what does that spec typically look like inside the
   repo?
5. How is spec-in-repo related to Chapter 6's "external state storage"?
6. Why is "stateless always fails" imprecise? Use the demo's last row to rebut it.

## 9.6 Exercise

Open [`exercises/exercise9_context_strategy.py`](../exercises/exercise9_context_strategy.py),
implement `strat_spec_in_repo()` (bounded context + deduplication using `tried`).
Run `python3 exercises/check_exercise9.py` to verify.

## 9.7 Self-Check Answers

1. stateless (task + latest feedback: cheap, but no memory when feedback is thin
   -> cannot converge) / conversation (accumulated history: has memory but
   context explodes and drifts) / spec-in-repo (clean context + concise spec:
   has memory and bounded, but you must maintain the spec).
2. Conversation grows every round and will eventually exceed the model's context
   window; and the longer the context, **the more drift**: with a long context
   attention is diluted and early noise/errors keep being dragged along as
   premises, causing the model to go off-topic.
3. durable spec = write cross-round memory into a concise in-repo spec; solves
   cost (bounded context), drift (each round is clean), crash resilience
   (state is in the repo).
4. Often a `PLAN.md` / `TODO.md` / test file / issue description -- the agent
   reads and updates it each round.
5. Both store "state" in a persistent location outside the process; spec-in-repo
   applies the same idea to "memory" -- if the process dies and restarts, the
   memory is still there.
6. Imprecise: the failure is not caused by statelessness but by feedback that
   cannot carry the required memory. Demo last row: same stateless, same no
   memory, but feedback carries a "too high / too low" range -> binary search
   succeeds in 4 rounds with the smallest context -- the culprit is thin
   feedback, not no-state.

---

Passing condition: you can describe the trade-offs of all three context
strategies, explain the durable spec, and implement bounded-context spec-in-repo.
-> [Chapter 10: Loop-Level Evals](ch10_loop_evals.md)
