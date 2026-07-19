"""
quiz.py -- knowledge quiz runner
=================================
    python3 quiz.py --chapter 3     # quiz only chapter 3
    python3 quiz.py --all           # all chapters
    python3 quiz.py --check         # non-interactive: validate bank format only (for CI/verification)

mcq / short are auto-graded; reflect questions show the model answer for self-evaluation.
Be honest: auto-grade what can be auto-graded, provide model answers for what requires judgment --
this is exactly the spirit of Chapter 4.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiz_bank import BANK


def validate_bank():
    """--check: validate bank format. Returns a list of issues (empty = no problems)."""
    errs = []
    for i, q in enumerate(BANK):
        where = f"question {i} (ch{q.get('ch', '?')})"
        if q.get("type") not in ("mcq", "short", "reflect"):
            errs.append(f"{where}: invalid type")
        if not q.get("q"):
            errs.append(f"{where}: missing question text")
        if not q.get("model"):
            errs.append(f"{where}: missing model answer")
        if q.get("type") == "mcq":
            opts = q.get("options", [])
            if len(opts) < 2:
                errs.append(f"{where}: mcq has too few options")
            if not isinstance(q.get("answer"), int) or not (0 <= q.get("answer", -1) < len(opts)):
                errs.append(f"{where}: mcq answer index out of range")
        if q.get("type") == "short" and not q.get("accept"):
            errs.append(f"{where}: short answer missing accept keywords")
    return errs


def ask(q):
    """Ask one question, return (correct, auto_graded)."""
    print("\n" + q["q"])
    if q["type"] == "mcq":
        for i, opt in enumerate(q["options"]):
            print(f"  {i + 1}. {opt}")
        raw = input("Your answer (enter number): ").strip()
        ok = raw.isdigit() and int(raw) - 1 == q["answer"]
        print(("Correct!" if ok else f"Wrong. Correct answer is {q['answer'] + 1}.") + f" {q['model']}")
        return ok, True
    if q["type"] == "short":
        raw = input("Your answer: ").strip().lower()
        ok = any(kw.lower() in raw for kw in q["accept"])
        print(("Correct!" if ok else "Not quite.") + f" Model answer: {q['model']}")
        return ok, True
    # reflect
    input("(Think about your answer, then press Enter to see the model answer)")
    print(f"Model answer: {q['model']}")
    raw = input("Did your answer roughly match? (y/n): ").strip().lower()
    return raw.startswith("y"), False


def main():
    if "--check" in sys.argv:
        errs = validate_bank()
        if errs:
            print("Quiz bank format issues:")
            for e in errs:
                print("  - " + e)
            return 1
        print(f"Quiz bank format OK, {len(BANK)} questions covering chapters "
              f"{sorted(set(q['ch'] for q in BANK))}.")
        return 0

    if "--chapter" in sys.argv:
        ch = int(sys.argv[sys.argv.index("--chapter") + 1])
        questions = [q for q in BANK if q["ch"] == ch]
        title = f"Chapter {ch}"
    elif "--all" in sys.argv:
        questions = BANK
        title = "All Chapters"
    else:
        print(__doc__)
        return 0

    if not questions:
        print("No questions found for this chapter.")
        return 0

    print("=" * 56)
    print(f"  Knowledge Quiz - {title} ({len(questions)} questions)")
    print("=" * 56)

    auto_total = auto_right = reflect_right = reflect_total = 0
    for q in questions:
        ok, auto = ask(q)
        if auto:
            auto_total += 1
            auto_right += ok
        else:
            reflect_total += 1
            reflect_right += ok

    print("\n" + "=" * 56)
    if auto_total:
        print(f"  Auto-graded: {auto_right}/{auto_total} correct")
    if reflect_total:
        print(f"  Reflection (self-evaluated): {reflect_right}/{reflect_total} you felt OK about")
    print("=" * 56)
    return 0


if __name__ == "__main__":
    sys.exit(main())
