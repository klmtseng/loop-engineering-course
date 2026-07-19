"""
anim.py -- terminal animation helper (standard library only, optional)
=======================================================================
Lets students "watch the loop actually turning." Each lesson gains slow-motion
playback of the act -> verify -> decide rhythm with `--animate`, including a fuse
progress bar.

Key design: **when disabled (no --animate flag), all functions are no-ops** -- they
print nothing and do not sleep. The default output of each lesson is unchanged word
for word, and automated graders are completely unaffected.

Usage (inside a lesson script):
    import anim
    anim.from_argv()        # read --animate from argv; stay in normal mode if absent

    anim.pause()            # slow-motion pause (no sleep when disabled)
    anim.fuse(i, MAX)       # draw fuse bar: filled/empty circles (no print when disabled)
    anim.step("->", "do one step")  # narrated step line with pause (no print when disabled)
"""

import sys
import time

_ON = False  # whether animation mode (--animate) is active


def from_argv(argv=None):
    """Read command-line arguments and activate animation if --animate is present. Returns whether active."""
    global _ON
    argv = sys.argv if argv is None else argv
    _ON = "--animate" in argv
    return _ON


def on():
    return _ON


def pause(seconds=0.7):
    """Slow-motion pause. Does not sleep when disabled (so normal / CI runs are just as fast)."""
    if _ON:
        time.sleep(seconds)


def fuse(used, total, label="fuse"):
    """Draw a fuse / progress bar: filled circles used, empty circles remaining. No print when disabled."""
    if not _ON:
        return
    bar = "o" * used + "." * max(0, total - used)
    print(f"      {label} [{bar}] {used}/{total}")
    pause(0.25)


def step(glyph, msg, seconds=0.7):
    """Print a narrated step line with a glyph and pause. No print when disabled (default output unchanged)."""
    if not _ON:
        return
    print(f"      {glyph} {msg}")
    pause(seconds)


def banner(msg):
    """Small section header in animation mode. No print when disabled."""
    if not _ON:
        return
    print(f"\n  +-- {msg}")
    pause(0.4)
