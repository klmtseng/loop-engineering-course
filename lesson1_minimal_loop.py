"""
Lesson 1 -- The Minimal Loop
==========================================
The one idea this lesson wants you to internalize:

    Prompt engineering is "you craft a sentence, hand it to the agent, and look at the result once."
    Loop engineering is "you design a system that repeatedly cycles through act -> verify -> decide
    until the goal is met or a limit is hit."

    In other words: loop engineering replaces "the person who keeps watching the agent and deciding
    whether to prompt again" -- that is, you -- with a piece of code.

The minimal skeleton of a loop is always these four things:

    goal      A clear, machine-checkable objective (not "make it better" -- it means "verify returns True")
    act       Do one step (call the agent / run a command / edit a file)
    verify    Check: did we reach the goal? (this is the soul of the loop; the whole of Lesson 2 covers it)
    decide    If not, loop back with feedback; if the goal is met or iterations are exhausted, stop

This lesson uses a "mock agent" as a stand-in so you can focus on the loop structure.
How to plug in a real agent (Claude Code / Codex / your own LLM call) is covered in the textbook Chapter 1.

Run:
    python3 lesson1_minimal_loop.py
    python3 lesson1_minimal_loop.py --animate    # slow-motion view of the loop iterating round by round
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# Task setup -- a "machine-checkable" objective
# ===========================================================================
# Goal: produce a tagline that (a) contains the keyword "save-time" and (b) is at most 20 characters.
# Note the key property of this goal: it can be judged objectively by a program -- correct or not.
# A vague goal ("write something nice") cannot be made into a loop -- because verify never knows when to stop.
GOAL_KEYWORD = "save-time"
GOAL_MAXLEN = 20


def verify(draft):
    """The verify gate. Returns (passed, feedback_for_next_iteration).

    The success or failure of a loop depends almost entirely on this function:
    it defines what "done" actually means.
    Feedback is not decoration -- it is the only channel through which the next iteration's agent
    knows "what was wrong last time."
    """
    if GOAL_KEYWORD not in draft:
        return False, f"missing keyword '{GOAL_KEYWORD}'"
    if len(draft) > GOAL_MAXLEN:
        return False, f"too long ({len(draft)} chars), must be <= {GOAL_MAXLEN}"
    return True, "passed"


# ===========================================================================
# Mock agent -- in the real world this would be an LLM call / Claude Code run
# ===========================================================================
# It receives "task + previous iteration's feedback" and produces a new draft.
# The point is not how smart it is, but that "it sees the feedback from the previous iteration
# every round" -- that is the entire secret of how an agent gets better inside a loop.
# We deliberately make it start out wrong so you can see the loop recover.
_DRAFTS = [
    "make your life better and happier every day",   # no keyword, and too long -- intentional
    "save-time and effort, live lighter and freer",  # keyword present, but still too long
    "save-time every day",                           # both conditions met
]


def mock_agent(task, feedback, attempt):
    """Returns the draft for attempt number `attempt`. A real agent would actually revise based on
    feedback; here we use three pre-written drafts to simulate "getting better each round."""
    draft = _DRAFTS[min(attempt, len(_DRAFTS) - 1)]
    print(f"   agent sees feedback: '{feedback}' -> produces: '{draft}'")
    return draft


# ===========================================================================
# ★ The entire point of this lesson: loop() -- under 15 lines
# ===========================================================================
MAX_ITERS = 5  # The fuse. Without it, a task that never passes runs forever (= burns money).


def loop(task):
    feedback = "(first iteration, no feedback yet)"

    for i in range(1, MAX_ITERS + 1):
        print(f"\n[Round {i}]")
        anim.fuse(i - 1, MAX_ITERS)

        # --- act: do one step ---
        anim.step("✎", "act: ask the agent for a draft")
        draft = mock_agent(task, feedback, attempt=i - 1)

        # --- verify: check if the goal is met ---
        anim.step("🔍", "verify: check whether goal is met")
        passed, feedback = verify(draft)
        anim.pause()

        # --- decide: if passed, stop; otherwise loop back with feedback ---
        if passed:
            print(f"   ✅ verify passed -> done. Result: '{draft}'")
            return draft
        anim.step("↻", "decide: not passed, loop back with feedback")
        print(f"   ✗ verify failed: {feedback} -> trying again")

    # Loop ended normally = iterations exhausted without passing = fuse blown
    print(f"\n⚠️  Ran {MAX_ITERS} rounds without meeting the goal -- fuse blown."
          " Check whether the task is too hard or the verify condition is too strict.")
    return None


# ===========================================================================
# Demo
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    print("=" * 64)
    print(f"Task: write a tagline that contains '{GOAL_KEYWORD}' and is at most {GOAL_MAXLEN} characters")
    print("=" * 64)

    result = loop("write a product tagline")

    print("\n" + "=" * 64)
    print("What you just saw is the heartbeat of all loop engineering:")
    print("  act (do one step) -> verify -> loop back with feedback if not done -> stop when done or exhausted.")
    print("Swap mock_agent for a real agent and verify for running tests, and this skeleton stays identical.")
    print("=" * 64)
