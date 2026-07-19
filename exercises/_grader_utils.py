"""
_grader_utils.py -- shared utilities for autograders
==========================================
Every check_exerciseN.py (and capstone/grade_capstone.py) relies on these:
  1. load(path)        load the student's file as a module (regardless of where it lives)
  2. Grader            collect assertion results, then print a scorecard (pass / fail / todo)
  3. run / requirement turn "unimplemented TODOs" into friendly messages instead of ugly tracebacks

Design note: the autograder itself is a verify gate -- it imports the functions the student exposes,
feeds them controlled inputs, and asserts their behavior item by item, without parsing stdout (fragile).
This is exactly the "verification must be objective" principle the course teaches.
"""

import importlib.util
import os
import sys


def load(path, name="student_module", missing_hint=None):
    """Load an arbitrary .py file as a module and return it. Gives a friendly error if not found or incomplete."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"✗ File not found: {path}")
        if missing_hint:
            print(f"  {missing_hint}")
        print("  (Or use --target to specify your file)")
        sys.exit(2)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except NotImplementedError:
        print("✗ This file raises NotImplementedError on import (there are still TODOs to implement).")
        print("  Fill in the items marked TODO, then run the assessment again.")
        sys.exit(1)
    return mod


def target_path(default):
    """Parse the --target argument; use the default if not provided."""
    argv = sys.argv
    if "--target" in argv:
        return argv[argv.index("--target") + 1]
    return default


class Grader:
    """Collect check results, then report(). Status has three values: True pass / False fail / 'todo' pending.
    Any result that is not all True means exit code = 1."""

    def __init__(self, title):
        self.title = title
        self.results = []  # (status, msg); status in {True, False, "todo"}

    def check(self, passed, msg):
        self.results.append((bool(passed), msg))
        print(f"  {'✅' if passed else '❌'} {msg}")
        return passed

    def todo(self, msg):
        """A requirement is not yet implemented -- not a failure, marked as pending."""
        self.results.append(("todo", msg))
        print(f"  ⬜ pending  {msg}")

    def check_raises(self, fn, msg):
        """Expect fn() to raise an exception (used to verify that something that should be blocked is blocked)."""
        try:
            fn()
            self.check(False, msg + "(expected an exception but none was raised)")
        except Exception:
            self.check(True, msg)

    def report(self):
        passed = sum(1 for s, _ in self.results if s is True)
        todos = sum(1 for s, _ in self.results if s == "todo")
        wrong = sum(1 for s, _ in self.results if s is False)
        total = len(self.results)
        print("-" * 56)
        if passed == total:
            print(f"🎉 {self.title}: all {total} checks passed! You passed this lesson.")
            return 0
        tail = []
        if wrong:
            tail.append(f"{wrong} to fix (❌)")
        if todos:
            tail.append(f"{todos} not done (⬜)")
        print(f"📋 {self.title}: {passed}/{total} passed" + (", " + ", ".join(tail) if tail else "") + ".")
        print("   Fix the items marked ❌/⬜ one by one, then run again. (Check solutions/ only when truly stuck.)")
        return 1


def requirement(grader, label, fn):
    """Run one 'requirement' check. fn calls grader.check(...) internally.
    If fn hits an unimplemented section (NotImplementedError) -> mark as pending (does not abort other requirements);
    if fn raises any other error -> record as failure with the error. This lets students see partial progress
    on multi-requirement exercises."""
    try:
        fn()
    except NotImplementedError:
        grader.todo(f"{label} (not yet implemented)")
    except Exception as e:
        grader.check(False, f"{label} raised an error: {type(e).__name__}: {e}")


def run(grade_fn, grader):
    """For single-TODO exercises: if grade_fn hits an unimplemented section, give a friendly message. Returns exit code."""
    try:
        grade_fn()
    except NotImplementedError as e:
        print(f"\n✗ TODO not yet implemented: {e}")
        print("  Fill in the items marked TODO, then run again.")
        return 1
    return grader.report()
