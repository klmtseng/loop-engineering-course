# Chapter 1 -- The Minimal Loop

> **Chapter goal**: understand what loop engineering is, how it differs from prompt engineering,
> and write a closed loop under 15 lines: `act -> verify -> decide`.
> By the end you will believe one thing: **the core of "an AI that finishes things on its own"
> is a while loop with an exit condition.**
>
> Reference solution: [`lesson1_minimal_loop.py`](../lesson1_minimal_loop.py) (do not look until you are stuck)

**TL;DR**: loop engineering = replacing the human who decides whether to prompt again with
an `act->verify->decide` program; the prerequisite is that the goal must be **machine-checkable**.

## 1.1 Concept: From "Prompt Once" to "Loop Until Done"

When you type a sentence into ChatGPT and get an answer back, if you are not satisfied,
**you** type another message: "That is wrong, make it shorter." That act of "look at the result,
decide whether to ask again, and type the feedback back" -- that is you.

```
You --prompt--> agent --answer--> You are not satisfied --prompt again--> agent -- ...
^_____________You are always in the loop, acting as the human judge___________________^
```

**Loop engineering is replacing that "you" in the loop with a piece of code.**
The core idea: you stop prompting the agent yourself, and instead design a system that prompts it on its own.

| | Prompt Engineering | Loop Engineering |
|---|---|---|
| What you deliver | A well-crafted prompt | A system that iterates on its own |
| Who decides "try again" | You (human) | Code (verify + decide) |
| When it stops | When you feel satisfied | When a verifiable goal is met, or a limit is hit |
| Output | A one-off answer | A repeatable, schedulable, auditable process |

### A loop is always these four things

```
goal    A clear, machine-checkable objective
act     Do one step (call the agent / run a command / edit a file)
verify  Check: did we reach the goal?     <- the soul of the loop; the whole of Chapter 2 covers this
decide  If not, loop back with feedback; if yes, or if the budget is gone, stop
```

**The single most important sentence: the goal must be machine-checkable.**
"Make the copy better" cannot be turned into a loop -- verify would never know when to stop.
"The copy must contain the keyword 'save-time' and be at most 20 characters long" works --
because a function can give an objective yes or no.
Translating a vague wish into a verifiable condition is the first real skill in loop engineering.

### Inner loop vs outer loop: you are "wrapping" the agent, not replacing it

If you have studied the internals of an agent (for example the ReAct loop in the sister course
agent-from-scratch), there is one potentially confusing point to clarify -- there are actually
**two nested loops**:

```
Outer loop (what this course teaches -- loop engineering)
   Your code:  dispatch agent -> verify -> loop back with feedback if not done -> stop when done or budget gone
   |-- Inner loop (the agent's own business, not your concern)
        Agent:  reason -> act (use tools) -> observe -> ... until it thinks it is done
```

**The inner loop** is the agent's own reason/act/observe heartbeat (built into Claude Code or Codex;
calling it once runs a full turn). **The outer loop** is what you design: treat the agent as a black box,
**wrap it** -- give it a task, collect the artifact, verify objectively, and decide whether to dispatch again.
You are not rewriting the agent's brain; you are acting as the foreman who decides whether to dispatch
again and when to call it done. This course is entirely about the outer loop.

### When you should NOT use a loop

Loops are not a silver bullet. In these situations a loop is a bad idea, and forcing it just automates
garbage production (see Chapter 7 for why):

| Do not use a loop when... | Why |
|---|---|
| **Verification is expensive or slow** | verify runs every iteration; if it takes 10 minutes or costs money, iteration cost explodes |
| **Verification is unreliable, or you cannot write an objective criterion** | verify is the foundation of a loop; if the foundation lies, the loop just lies faster (Chapter 7) |
| **The task is open-ended, with no definition of "done"** | no exit condition = not a loop, it is a bottomless pit |
| **A single mistake is extremely costly and irreversible** | automation occasionally loses control; irreversible actions (deleting data, spending money) should keep a human in the loop |

**The test**: is there a **cheap, reliable, objective** "are we done?" check? Yes -> loop is appropriate. No -> do not automate yet.

## 1.2 Hands-On

Open `lesson1_minimal_loop.py`, but try typing through it yourself first (the physical act of writing is half the learning).

### Step 1: Write verify -- define what "done" means first

```python
GOAL_KEYWORD = "save-time"
GOAL_MAXLEN = 20

def verify(draft):
    if GOAL_KEYWORD not in draft:
        return False, f"missing keyword '{GOAL_KEYWORD}'"
    if len(draft) > GOAL_MAXLEN:
        return False, f"too long ({len(draft)} chars)"
    return True, "passed"
```

**Checkpoint**: notice that verify returns `(passed, feedback)`.
That feedback is not decoration -- it is the only channel through which the next-iteration agent
knows "what went wrong last time."

### Step 2: act -- one agent call

The course's `mock_agent` is a stand-in that simulates "getting better each round" with pre-written drafts.
In the real world this step is a single LLM call (see section 1.5 on how to swap it in).
The key point is: **it receives the previous iteration's feedback every round.**

### Step 3: Assemble the loop -- all the key ideas fit in 10 lines

```python
def loop(task):
    feedback = "(first iteration, no feedback yet)"
    for i in range(1, MAX_ITERS + 1):
        draft = mock_agent(task, feedback, attempt=i - 1)   # act
        passed, feedback = verify(draft)                    # verify
        if passed:                                          # decide
            return draft
    return None   # ran out of iterations without passing = fuse blown
```

**Checkpoint**: `MAX_ITERS` is not optional. Without it, a task that never passes will run forever --
in the real world, that means an infinite bill. Chapter 3 covers this in depth.

### Step 4: Run it

```bash
python3 lesson1_minimal_loop.py
```

You will see the draft get rejected by verify each round, receive feedback, and be revised until
it passes on round 3. **This act->verify->decide rhythm never changes across lessons -- only the
individual components get more realistic.**

## 1.3 Self-Check (Can you answer without looking above?)

1. In one sentence, what is the fundamental difference between loop engineering and prompt engineering?
2. What are the four components of a loop? Which one is the soul?
3. Why can "make the copy look nice" not be made into a loop, but "copy contains keyword X and is at most N characters" can?
4. Why does verify return "feedback" rather than just True/False?
5. What happens if you remove `MAX_ITERS`? What is the real-world cost?

## 1.4 Extended Exercises

- **Change the goal**: change verify to require "must contain an emoji and end with a question mark,"
  and observe whether the mock drafts get stuck, and how the loop handles that
  (this makes you experience "verify too strict -> always burns to fuse").
- **Real agent preview**: if you have done agent-from-scratch, replace `mock_agent` with that course's
  `llm()` call and feed the verify feedback back as a user message.
  You will find the loop skeleton does not need to change at all.
- **Design your own loop**: write down one task you have recently had to prompt an AI about
  multiple times before getting a good result. What are its goal and verify?
  Can they be machine-checked? (If you cannot define verify, it cannot be automated yet -- that is normal.)

## 1.5 Hands-On Assessment

Reading is not enough -- go write the loop yourself: open
[`exercises/exercise1_minimal_loop.py`](../exercises/exercise1_minimal_loop.py),
fill in `loop()`, run `python3 exercises/check_exercise1.py`, and get all green to pass this lesson.

## 1.6 Self-Check Answers

1. Prompt = you deliver one sentence and look at the result once; loop = you deliver a self-iterating system, and the code decides when to try again.
2. goal / act / **verify** / decide; verify is the soul -- it defines "done" and decides when to stop.
3. Because a loop needs verify to judge objectively; "nice" cannot be judged, but "contains X and is at most N characters" can be evaluated with a function.
4. Because feedback is the only clue the next-iteration agent has about "what went wrong last time"; without it, all it can do is guess.
5. It runs forever; the real-world cost is an infinite API bill (a stuck agent can burn through your quota overnight).

---

Passing condition: you can independently write an act->verify->decide loop and explain why the goal must be machine-checkable.
Next, we upgrade verify from "a function" to "running a real command," and add the other exits a loop needs.
-> [Chapter 2: Exit Conditions and the Verify Gate](ch02_exit_conditions.md)
