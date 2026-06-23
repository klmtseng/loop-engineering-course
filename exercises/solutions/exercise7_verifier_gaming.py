"""練習 7 參考解答。對應第 7 課。"""

import random

PUBLIC_CASES = [(20, 22, 42)]
HIDDEN_CASES = [(1, 1, 2), (3, 4, 7), (-5, 5, 0)]


def build(code):
    ns = {}
    exec(code, ns)
    return ns["add"]


def weak_verify(add):
    return all(add(a, b) == want for a, b, want in PUBLIC_CASES)


def strong_verify(add):
    for a, b, want in PUBLIC_CASES + HIDDEN_CASES:
        if add(a, b) != want:
            return False
    for _ in range(50):
        a, b = random.randint(-1000, 1000), random.randint(-1000, 1000)
        if add(a, b) != a + b:
            return False
    return True
