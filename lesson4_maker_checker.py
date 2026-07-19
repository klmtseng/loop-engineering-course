"""
Lesson 4 -- maker / checker: Dual Agents (Independent Verification)
====================================================================
So far the agent doing the work has also been the one verifying it -- the
verify function was written by us. But when verification itself requires
judgment ("does this summary faithfully represent the source?", "did this
refactor silently change behavior?"), you will be tempted to ask the agent
doing the work: "Do you think you finished?"

Don't. Letting an agent verify its own output is the most common failure mode
in loop engineering:

    It will almost always say "looks great, passed!" -- this is called
    grading inflation (self-assessment bias).
    An agent motivated to say "I'm done" is not an impartial judge.

The fix is to separate roles -- something quality engineering figured out a
century ago, called the maker/checker principle:

    maker   (the doer)   produces output only; no assessment
    checker (the verifier) is a "different" agent with an independent,
            stricter standard; it has exactly two outputs:
            approve, or reject + exactly what to fix

The loop becomes: maker produces -> checker verifies -> on reject, feed
checker's notes back to maker -> another round -> until the checker approves
or the iter budget runs out.

The key word is "independent": the checker should not know how hard the maker
tried -- it looks only at the output. In production, maker and checker often
use different system prompts, even different models, to ensure they do not
share the same blind spots.

This lesson uses the standard library only. First we show how "maker
self-grades" gives a pass far too early; then we swap in an "independent
checker" and watch the same draft's fate change entirely.

Run:
    python3 lesson4_maker_checker.py
    python3 lesson4_maker_checker.py --animate    # slow-motion, watch maker<->checker exchange
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# Task: write a customer-service reply. Hidden hard rules (checker knows;
#   maker does not):
#   1. Must contain an apology word ("sorry" or "apologies")
#   2. Must give a clear next step (commitment containing "will")
#   3. Must be at most 60 characters
# The maker is only told "write a polite customer-service reply" -- it does
# not know these three rules, so it will think any casual reply is fine.
# That is precisely why we need an independent checker.
# ===========================================================================
_MAKER_DRAFTS = [
    "We have received your inquiry. Thank you.",                       # no apology, no commitment
    "Sorry for the trouble -- thank you for your patience.",           # apology, but no next-step commitment
    "Sorry for the trouble. We will reply within 24 hours.",          # all three rules met
]


def maker(feedback, attempt):
    """The producing agent: responsible for output only. In production this is one LLM call."""
    draft = _MAKER_DRAFTS[min(attempt, len(_MAKER_DRAFTS) - 1)]
    print(f"   maker received feedback: '{feedback}'")
    print(f"   maker produced: '{draft}'")
    return draft


def maker_self_grade(draft):
    """Maker self-grades -- deliberately shows 'self-assessment bias'. It was
    not given the hard rules and has an incentive to say it's done, so it
    glances at the draft and passes it. This is the counter-example."""
    return True, "I think this looks fine -- approved!"


def checker(draft):
    """Independent verification agent: holds strict rules the maker cannot see,
    returns only approve or reject + reason.
    In production this is 'another' LLM call with a different system prompt
    playing the role of a strict reviewer."""
    problems = []
    if not any(w in draft.lower() for w in ("sorry", "apologies")):
        problems.append("missing apology")
    if "will" not in draft.lower():
        problems.append("no next-step commitment")
    if len(draft) > 60:
        problems.append(f"too long ({len(draft)} chars, must be <= 60)")
    if problems:
        return False, ";".join(problems)
    return True, "approve"


MAX_ITERS = 6


def loop(grader, grader_name):
    """Same loop skeleton with different verifiers (grader) swapped in."""
    print(f"\n{'=' * 64}\nUsing '{grader_name}' as the verifier\n{'=' * 64}")
    feedback = "(first round, no feedback yet)"

    for i in range(1, MAX_ITERS + 1):
        print(f"\n[Round {i}]")
        anim.fuse(i - 1, MAX_ITERS)
        anim.step("✎", "maker: produce a draft")
        draft = maker(feedback, attempt=i - 1)

        anim.step("🔍", "checker: independent verification")
        approved, comment = grader(draft)
        anim.pause()
        if approved:
            print(f"   verification -> ✅ {comment}")
            print(f"   done. output: '{draft}'")
            return draft

        print(f"   verification -> ✗ reject: {comment}")
        feedback = comment  # checker's notes become the maker's blueprint for next round

    print(f"   ⚠️  still not passing after {MAX_ITERS} rounds")
    return None


# ===========================================================================
# Demo -- same maker, two different verifiers; dramatically different outcomes
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    print("Scenario A: maker grades itself (counter-example)")
    a = loop(maker_self_grade, "maker self-grade")

    print("\n\nScenario B: swap in an independent checker")
    b = loop(checker, "independent checker")

    print("\n" + "=" * 64)
    print("Comparison:")
    print(f"  Self-grade output: '{a}'  <- passed on round 1, no apology and no commitment")
    print(f"  Checker output:    '{b}'  <- rejected twice, finally a genuinely acceptable reply")
    print("=" * 64)
    print("Lesson: an agent that says 'I'm done' is not an impartial judge.")
    print("Separate maker and checker, give checker an independent, stricter standard --")
    print("that is the prerequisite for deploying a loop.")
