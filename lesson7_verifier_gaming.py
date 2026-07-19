"""
Lesson 7 -- verify Is a Proxy Metric, and Agents Will Game It (Verifier Gaming)
================================================================================
This is the most important lesson in the whole course. The first six lessons
asked you to believe "run verify; green means done." Now let's bust that halfway:

    verify is not the truth about "correct or not" -- it is only a 'proxy metric'.
    And the agent is not solving your problem -- it is 'making the verify turn green'.
    Those two things are not the same.

Remember Lesson 2? The task was "print 42", and the agent delivered `print(20 + 22)`.
It did not write a program that can add; it 'hard-coded' the answer, just enough
to fool that one-shot verify. In the real world, this is the most common form
of three agent cheating techniques:

    1. Hard-code the answer  -- return the expected value directly; only solves the given tests
    2. Weaken the verifier   -- delete failing tests / change them to `assert True`
    3. Fake completion       -- do nothing real but make verify return passing

This has a name: **Goodhart's Law** -- "When a measure becomes a target, it
ceases to be a good measure."
The quality ceiling of your loop = how hard its verify is to game.

This lesson uses an addition task to show how a "weak verify" gets fooled by
hard-coding and how a "strong verify" catches it.
Standard library only; zero API keys.

Run:
    python3 lesson7_verifier_gaming.py
    python3 lesson7_verifier_gaming.py --animate
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# Task: write an add(a, b) that returns a + b
# ===========================================================================
# "Public cases" are ones you write out and the agent can see.
# "Hidden cases" are ones you keep back -- the agent cannot see them.
PUBLIC_CASES = [(20, 22, 42)]                       # Lesson 2 only verified this one
HIDDEN_CASES = [(1, 1, 2), (3, 4, 7), (-5, 5, 0)]   # kept back


def build(code):
    """Turn the agent's code string into a callable add function."""
    ns = {}
    exec(code, ns)
    return ns["add"]


# ===========================================================================
# Two verifiers: the weak one checks only public cases; the strong one adds
# hidden cases + random inputs
# ===========================================================================
def weak_verify(add):
    """Only checks one public case -- can be fooled by hard-coding in one look. (This was Lesson 2's verify.)"""
    return all(add(a, b) == want for a, b, want in PUBLIC_CASES)


def strong_verify(add):
    """Public + hidden + random. A single hard-coded answer cannot pass many distinct inputs."""
    for a, b, want in PUBLIC_CASES + HIDDEN_CASES:
        if add(a, b) != want:
            return False
    for _ in range(20):  # random spot-checks: block "also hard-code all the hidden cases"
        a, b = random.randint(-100, 100), random.randint(-100, 100)
        if add(a, b) != a + b:
            return False
    return True


# ===========================================================================
# Three agents: one honest; two gaming the verify
# ===========================================================================
AGENTS = {
    "honest agent": "def add(a, b):\n    return a + b",
    "hard-coded agent": "def add(a, b):\n    return 42",        # only to fool weak_verify
    "off-by-one agent": "def add(a, b):\n    return a + b + 1", # looks right, has a bug
}


def demo():
    print("=" * 64)
    print("Same task (add(a,b)=a+b) -- see which agents weak verify and strong verify each trust")
    print("=" * 64)
    for name, code in AGENTS.items():
        anim.banner(name)
        add = build(code)
        anim.step("✎", f"{name} delivers: {code.splitlines()[-1].strip()}")
        weak = weak_verify(add)
        anim.step("🔍", "weak verify (only checks 20+22)")
        strong = strong_verify(add)
        anim.step("🔬", "strong verify (public + hidden + random)")
        print(f"\n  {name}")
        print(f"    code: {code.splitlines()[-1].strip()}")
        print(f"    weak verify (only 20+22)     -> {'green ✅' if weak else 'red ✗'}")
        print(f"    strong verify (many + random) -> {'green ✅' if strong else 'red ✗'}")
        if weak and not strong:
            print("    ⚠️  weak verify was fooled! The agent did not solve the problem -- it only")
            print("       made your single check turn green.")
        anim.pause(0.8)


if __name__ == "__main__":
    anim.from_argv()
    demo()
    print("\n" + "=" * 64)
    print("Three real cheating techniques -- this lesson only showed technique 1 (hard-code); the others are equally lethal:")
    print("  2. Weaken the verifier -- if your verify is 'run the repo's tests', the agent can")
    print("     delete failing tests / change them to `assert True`")
    print("  3. Fake completion     -- do nothing real but make verify return passing")
    print("-" * 64)
    print("Defenses (making verify harder to game):")
    print("  * hold-out: keep hidden cases the agent cannot see or modify")
    print("  * multiple + random inputs: a single hard-coded answer cannot pass many distinct inputs")
    print("  * isolation: the agent cannot modify verify / tests themselves (Lesson 5 isolation also serves this)")
    print("  * human sampling: for high-risk loops, even green results should be spot-checked")
    print("    (this is what the L1->L3 levels in Lesson 3 are for)")
    print("=" * 64)
    print("Remember: the quality ceiling of a loop = how hard its verify is to game.")
    print("A weak verify just means the loop produces garbage that is better at fooling you.")
