"""
練習 9 —— spec-in-repo 上下文策略 (對應第 9 課)
================================================
stateless(沒記憶)和 conversation(context 爆炸)都給你了當對照。你要實作生產級的
spec-in-repo:每圈用乾淨 context + 一份精簡 spec,既有記憶、context 又有界。

要實作的 strat_spec_in_repo(tried, history) 規格,回傳 (ctx_tokens, guess):
  - ctx_tokens 必須【有界】:= BASE_TOKENS + SPEC_TOKENS,**不可隨 history/tried 變大**
  - guess = UNIVERSE(1..20)裡【還沒試過】的最小數字(用 tried 去重 → 才不會鬼打牆)

完成後驗收:
    python3 check_exercise9.py
"""

UNIVERSE = list(range(1, 21))
BASE_TOKENS = 30
MSG_TOKENS = 12
SPEC_TOKENS = 8


def strat_stateless(tried, history):
    """【對照,不用改】沒記憶:context 最省但會鬼打牆。"""
    return BASE_TOKENS, (len(history) % 5) + 1


def strat_conversation(tried, history):
    """【對照,不用改】記得全部,但 context 每圈長大。"""
    return BASE_TOKENS + len(history) * MSG_TOKENS, next(n for n in UNIVERSE if n not in tried)


def strat_spec_in_repo(tried, history):
    # ===================================================================
    # TODO: 回傳 (有界的 ctx_tokens, 還沒試過的最小數字)
    # ===================================================================
    raise NotImplementedError("實作你的 strat_spec_in_repo()")
