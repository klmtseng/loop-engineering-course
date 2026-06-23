"""練習 9 參考解答。對應第 9 課。"""

UNIVERSE = list(range(1, 21))
BASE_TOKENS = 30
MSG_TOKENS = 12
SPEC_TOKENS = 8


def strat_stateless(tried, history):
    return BASE_TOKENS, (len(history) % 5) + 1


def strat_conversation(tried, history):
    return BASE_TOKENS + len(history) * MSG_TOKENS, next(n for n in UNIVERSE if n not in tried)


def strat_spec_in_repo(tried, history):
    ctx = BASE_TOKENS + SPEC_TOKENS                       # 有界:不隨歷史長大
    guess = next(n for n in UNIVERSE if n not in tried)   # 用 tried 去重 → 不鬼打牆
    return ctx, guess
