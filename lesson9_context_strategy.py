"""
第 9 課 —— 跨圈上下文策略 (Context Strategy Across Iterations)
==============================================================
這是真實 loop engineering 最核心、卻最少被講的決策:**每一圈,你要餵 agent 什麼 context?**

前面幾課的 mock 只收一個 `feedback` 字串,把這整塊藏起來了。真案子裡你必須選:

    1. stateless 重派 —— 每圈全新 context = 任務 + 最新一條回饋。便宜,但 agent 沒記憶。
    2. full conversation —— 把整段對話一直累加。agent 記得全部,但 context 每圈長大、
                            成本線性爆炸,而且越長越容易 drift(離題)。
    3. spec-in-repo —— 每圈全新 context,但把「持久狀態」寫在一個精簡的 spec/scratchpad 檔裡。
                       agent 有記憶、context 又有界。這是 coding agent 的生產預設。

本課用一個「猜密碼」任務把三者攤開比:同樣要猜中 13,看誰猜得到、context 各燒多少。

執行:
    python3 lesson9_context_strategy.py
    python3 lesson9_context_strategy.py --animate
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim

SECRET = 13
UNIVERSE = list(range(1, 21))   # 1..20
MAX_ITERS = 20

# 下面的 token 數是「相對示意」,不是真實 tokenization —— 重點在它們隨圈數怎麼成長,不在絕對值。
# (真實 token 怎麼拿:見第 3 章從 API 回應讀 usage。)
BASE_TOKENS = 30        # 任務描述本身的 token
MSG_TOKENS = 12         # 對話每多一輪的 token
SPEC_TOKENS = 8         # 精簡 spec(例如「已試:1-7,12」)的 token


# ===========================================================================
# 三種策略:各自決定 (這一圈的 context 多大, 這一圈猜什麼)
# ===========================================================================
def strat_stateless(tried, history):
    """只看『最後一條回饋』。context 恆定最小,但記不住試過什麼 →
    這裡用一個固定的小迴圈(1..5)模擬『沒有記憶就會鬼打牆』。"""
    ctx = BASE_TOKENS                      # 永遠只有任務 + 一條回饋
    guess = (len(history) % 5) + 1         # 在 1..5 之間繞圈,永遠到不了 13
    return ctx, guess


def strat_conversation(tried, history):
    """把整段歷史都塞進 context。記得全部 → 不重複猜 → 會猜到,
    但 context 每圈長大(成本線性爆炸,終將撞 context window)。"""
    ctx = BASE_TOKENS + len(history) * MSG_TOKENS   # ← 每圈變大
    guess = next(n for n in UNIVERSE if n not in tried)
    return ctx, guess


def strat_spec_in_repo(tried, history):
    """每圈全新 context,但把『已試集合』壓成一個精簡 spec 帶進去。
    記得全部、context 又恆定有界 → 兩全其美。"""
    ctx = BASE_TOKENS + SPEC_TOKENS                 # ← 不隨歷史長大
    guess = next(n for n in UNIVERSE if n not in tried)
    return ctx, guess


def strat_stateless_with_signal(bounds):
    """關鍵反例:這個策略一樣『沒記憶』(只看傳進來的東西),但傳進來的不再是一條乾話,
    而是『目前還沒排除的範圍 (lo, hi)』這個 1-bit 比較訊號累積出的邊界。
    它二分搜尋就能猜到——而且 context 一樣恆定有界。
    證明:猜不到的兇手不是『stateless』,是『回饋太薄、承載不了所需記憶』。"""
    lo, hi = bounds
    ctx = BASE_TOKENS + 4          # 只帶兩個邊界數字 → 一樣有界
    return ctx, (lo + hi) // 2


def run(strategy):
    tried, history, ctx_log = [], [], []
    for i in range(1, MAX_ITERS + 1):
        ctx, guess = strategy(tried, history)
        ctx_log.append(ctx)
        history.append(guess)
        if guess not in tried:
            tried.append(guess)
        if guess == SECRET:
            return ("SUCCESS", i, max(ctx_log), sum(ctx_log))
    return ("FAIL", MAX_ITERS, max(ctx_log), sum(ctx_log))


def run_signal():
    """stateless,但回饋帶『太高/太低』累積出的範圍 → 二分搜尋。"""
    lo, hi, ctx_log = 1, 20, []
    for i in range(1, MAX_ITERS + 1):
        ctx, guess = strat_stateless_with_signal((lo, hi))
        ctx_log.append(ctx)
        if guess == SECRET:
            return ("SUCCESS", i, max(ctx_log), sum(ctx_log))
        lo, hi = (guess + 1, hi) if guess < SECRET else (lo, guess - 1)
    return ("FAIL", MAX_ITERS, max(ctx_log), sum(ctx_log))


if __name__ == "__main__":
    anim.from_argv()
    print("=" * 70)
    print(f"任務:猜中密碼 {SECRET}(1..20)。比三種上下文策略:誰猜到、context 各燒多少")
    print("=" * 70)
    print(f"  {'策略':<18}{'結果':<10}{'圈數':<6}{'峰值context':<12}{'累計context'}")
    print("  " + "-" * 60)
    for name, strat in [("stateless(乾話回饋)", strat_stateless),
                        ("full conversation", strat_conversation),
                        ("spec-in-repo", strat_spec_in_repo)]:
        anim.step("→", f"跑 {name}")
        status, iters, peak, total = run(strat)
        print(f"  {name:<22}{status:<10}{iters:<6}{peak:<12}{total}")
        anim.pause(0.6)
    # 反例:一樣 stateless,但回饋帶『太高/太低』的範圍 → 二分搜尋成功、context 一樣有界
    anim.step("→", "跑 stateless(帶比較訊號)")
    status, iters, peak, total = run_signal()
    print(f"  {'stateless(帶比較訊號)':<20}{status:<10}{iters:<6}{peak:<12}{total}")
    print("=" * 70)
    print("讀這張表:")
    print("  • stateless(乾話回饋):context 最省,但回饋承載不了記憶 → 猜不到(FAIL)。")
    print("  • full conversation:猜得到,但峰值/累計 context 最大 → 成本爆炸,終將撞 context window。")
    print("  • spec-in-repo:猜得到,而且 context 恆定有界 → 生產環境的預設選擇。")
    print("  • stateless(帶比較訊號):★ 一樣沒記憶,但回饋夠 → 二分搜尋就猜到,context 還是有界。")
    print("-" * 70)
    print("精確的結論(別過度概化):**失敗的兇手不是『stateless』本身,是『回饋承載不了所需記憶』。**")
    print("  給足訊號,stateless 也能成功;真正要避免的是把記憶塞進無上限長大的對話歷史。")
    print("心法:把跨圈記憶寫進 repo 裡一份精簡的 spec(或讓回饋帶足狀態),用乾淨 context 重新派工。")
    print("      這就是 loop engineering 的 durable spec。")
