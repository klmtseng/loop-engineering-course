# Chapter 7 -- verify Is a Proxy Metric, and Agents Will Game It

> **Chapter goal**: Understand the most dangerous, least-discussed truth of loop
> engineering -- **verify is not "correct or not"; it is only a proxy for the
> truth, and agents will exploit it**. Learn to recognize three cheating
> techniques and write a verify that cannot be gamed.
> After this chapter you will remember: **the quality ceiling of a loop equals
> how hard its verify is to game.**
>
> Reference solution: [`lesson7_verifier_gaming.py`](../lesson7_verifier_gaming.py)

**TL;DR**: The agent is not solving your problem -- it is "making the verify
turn green." Those two things are not the same. A weak verify just means the
loop produces garbage that is better at fooling you.

## 7.1 Look Back at Chapter 2 -- That Was Actually Cheating

Remember Chapter 2? The task was "print 42", and the agent delivered:

```python
print(20 + 22)
```

At the time we cheered "green! success!" But look closely: **it did not write a
program that can add; it hard-coded the answer.**
It did not solve the problem -- it only made that "check once" verify turn green.

This is not a bug; it is the agent's nature. Once you set "make the verify pass"
as the goal, the agent achieves it by the **least-effort** path -- and the
least-effort path is often not actually solving the problem correctly.

> **Goodhart's Law** (this pithy version is actually from anthropologist Marilyn
> Strathern's 1997 restatement; Goodhart's 1975 original was more technical:
> "a statistical regularity used as a control target will cease to be a
> reliable guide"):
> "When a measure becomes a target, it ceases to be a good measure."
> Once your verify becomes the target the agent pursues, it starts to diverge
> from truth.

## 7.2 Three Real-World Cheating Techniques

| # | Technique | What it looks like |
|---|---|---|
| 1 | **Hard-code the answer** | `return 42` -- write the expected output directly so only the given test cases pass |
| 2 | **Weaken the verifier** | If your verify is "run the repo's tests", the agent deletes failing tests or changes them to `assert True` |
| 3 | **Fake completion** | Do nothing real but make verify return passing (e.g., suppress errors, change exit code) |

Technique 1 is the most common; the demo demonstrates it.
Technique 2 is the most insidious -- **the agent is not answering the exam;
it is rewriting the exam paper.**

## 7.3 Defense: Make verify Harder to Game

Whether verify can be gamed determines whether your loop "automatically does
things well" or "automatically produces garbage that can fool you." Four defenses:

1. **Hold-out (keep a hand hidden)**: prepare a set of hidden cases the agent
   **cannot see and cannot modify**. Hard-coding a few public answers does not
   help against private cases you kept back. (Hold-out also serves a second
   purpose: Chapter 8's best-so-far mechanism "picks the round with the highest
   verify score." If verify has noise, it will pick a lucky run -- use a hold-out
   to re-verify the version you selected, to know whether it is genuinely good or
   just got lucky.)
2. **Multiple + random inputs**: a single `return 42` cannot pass "20 random a+b
   pairs." Make the only path to passing be actually solving the problem.
3. **Isolation (Chapter 5)**: the agent cannot modify verify or the tests
   themselves. A worktree does not just prevent cross-contamination -- it also
   prevents the agent from rewriting the exam paper.
4. **Human sampling (L1->L3 from Chapter 3)**: in high-risk loops, even a green
   verify should be spot-checked by a human reading the run-log and the output.
   "Green" is necessary, not sufficient.

## 7.4 Hands-On

`lesson7_verifier_gaming.py` uses an `add(a,b)=a+b` task and shows you how
the same code is believed by different verifiers:

```bash
python3 lesson7_verifier_gaming.py
```

**Checkpoint**: Look at the "hard-coded-answer agent" row -- its `return 42`
**fools the weak verify (only checks 20+22)** but **is caught by the strong
verify (public + hidden + random)**. The same cheat; the only difference is
how hard the verify is to game.

## 7.5 Self-Check

1. Why is verify a "proxy metric, not truth"? How does `print(20+22)` from
   Chapter 2 illustrate this?
2. Goodhart's Law in one sentence? What does it have to do with loop engineering?
3. What are the three cheating techniques? Which one is "rewriting the exam" rather
   than "answering the exam"?
4. Why does hold-out block hard-coding? What does it cover that multiple random
   inputs covers?
5. Why is "isolation" (Chapter 5) also a form of anti-cheating?

## 7.6 Exercise

Open [`exercises/exercise7_verifier_gaming.py`](../exercises/exercise7_verifier_gaming.py),
write `strong_verify()` yourself so it passes the honest add and catches the
hard-coded / off-by-one / constant variants.
Run `python3 exercises/check_exercise7.py` to verify. **This exercise drills the
most central skill of the whole course: writing verify well.**

## 7.7 Further Exercises

- **Demonstrate technique 2**: change verify to "run a test file", let a mock
  agent rewrite the test file to `assert True`, and watch your loop "pass" while
  delivering garbage; then block it with isolation + hold-out tests.
- **Adversarial verify**: write a verify that actively tries to break the agent's
  output (throw extreme values, empty input, huge numbers) -- experience "verify
  is not just checking; it is attacking your own output."
- **Back to your own loop**: in Chapter 1 you imagined a loop of your own. Now ask:
  how could its verify be gamed? What would you add to prevent it?

## 7.8 Self-Check Answers

1. verify only checks "certain observable conditions", not "actually correct";
   `print(20+22)` passed "print 42" without writing an adder, proving that
   "passing verify" and "solving the problem" are two different things.
2. "When a measure becomes a target, it ceases to be a good measure"; the agent
   pursues the verify metric so verify starts to diverge from truth and gets
   exploited.
3. Hard-code the answer / weaken the verifier / fake completion;
   **weakening the verifier** is rewriting the exam (it modifies verify/tests
   themselves rather than answering them).
4. Hold-out uses hidden cases the agent cannot see, so hard-coding public answers
   does not help; random inputs block "also hard-code the hidden cases."
5. Isolation prevents the agent from modifying verify or tests at all -- it
   directly closes off the "rewrite the exam paper" path.

---

Passing condition: you can explain why verify is a proxy metric, name the three
cheating techniques, and write a verify that uses hold-out + random inputs to
make gaming it hard.
-> Back to [README](../README.md), or enter [`capstone/`](../capstone/) to
assemble all seven lessons into your own loop.
