"""Exercise 9 reference solution. Corresponds to Lesson 9."""

UNIVERSE = list(range(1, 21))
BASE_TOKENS = 30
MSG_TOKENS = 12
SPEC_TOKENS = 8


def strat_stateless(tried, history):
    return BASE_TOKENS, (len(history) % 5) + 1


def strat_conversation(tried, history):
    return BASE_TOKENS + len(history) * MSG_TOKENS, next(n for n in UNIVERSE if n not in tried)


def strat_spec_in_repo(tried, history):
    ctx = BASE_TOKENS + SPEC_TOKENS                       # bounded: does not grow with history
    guess = next(n for n in UNIVERSE if n not in tried)   # use tried to avoid repeating guesses
    return ctx, guess
