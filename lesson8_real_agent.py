"""
第 8 課 —— 非決定性與真實 agent (Non-determinism & Real Agents)
================================================================
前七課的 agent 都是「乖寶寶」:每圈穩定進步、固定圈數收斂。真實的 LLM agent 不是這樣。

    真 agent 是隨機的。同一個 prompt 跑兩次,結果不一樣。
    它會震盪、會退步、會這次第 3 圈就過、下次跑到第 6 圈還沒過。
    (而且非決定性不只來自取樣:即使 temperature=0,伺服器端的 batching 會改變浮點累加順序,
     真實服務仍非確定性 —— 見 Thinking Machines Lab 2025「Defeating Nondeterminism in LLM Inference」。)

本課用一個會「隨機漫步」的 noisy_agent 把這件事演給你看,並戳破一個你到現在
可能都還沒發現的 bug:**如果你的 loop「只看最後一圈」,它會丟掉中途更好的結果。**

任務改成更像真案子的:把測試覆蓋率衝到 ≥ 90%。agent 每圈回報一個覆蓋率數字,
平均會往上爬,但每圈有雜訊 —— 可能第 4 圈衝到 95,第 6 圈又掉回 83。

執行:
    python3 lesson8_real_agent.py
    python3 lesson8_real_agent.py --animate
    python3 lesson8_real_agent.py --real     # 選用:接真的 LLM(需 OPENROUTER_API_KEY;沒有就自動走 stub)
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim

GOAL = 90        # 覆蓋率達標線
MAX_ITERS = 6


def verify(coverage):
    return coverage >= GOAL


# ===========================================================================
# noisy_agent —— 會亂跳/退步的隨機 stub(吃 seed 才能在驗收時重現)
# ===========================================================================
def make_noisy_agent(seed):
    rng = random.Random(seed)

    def agent(attempt, feedback):
        # 平均隨 attempt 緩步上升,但每圈加高斯雜訊 → 會在達標線附近上下亂跳
        base = 78 + attempt * 2.5
        return max(0, min(100, round(rng.gauss(base, 11))))

    return agent


# ===========================================================================
# 三種 loop:好的會逐圈檢查;naive 跑完只看末圈;best-so-far 記住歷史最佳
# ===========================================================================
def loop_each_iter(agent):
    """正常寫法:每圈都驗,一達標就收工。非決定性 demo 用它看『第幾圈成功』的分佈。"""
    for i in range(1, MAX_ITERS + 1):
        cov = agent(i - 1, feedback="")
        if verify(cov):
            return ("SUCCESS", i, cov)
    return ("FAIL", MAX_ITERS, cov)


def naive_final_only(agent):
    """常見的隱藏 bug:讓 agent 跑完 N 圈,只判定『最後一圈』的成品。
    中途明明達標過,末圈一退步,它就當作失敗、把好結果丟了。"""
    val = None
    for i in range(1, MAX_ITERS + 1):
        val = agent(i - 1, feedback="")
    return ("SUCCESS" if verify(val) else "FAIL", MAX_ITERS, val)


def best_so_far_loop(agent):
    """正確寫法:跨圈記住歷史最佳,末圈退步也不影響。"""
    best = None
    for i in range(1, MAX_ITERS + 1):
        cov = agent(i - 1, feedback=f"目前最佳 {best}")
        if best is None or cov > best:
            best = cov
        if verify(best):
            return ("SUCCESS", i, best)
    return ("FAIL", MAX_ITERS, best)


# ===========================================================================
# ⚠️ best-so-far 的陷阱:對「有雜訊的代理指標」取 max,會選到僥倖(接第 7 課)
# ===========================================================================
# best-so-far 是「取多圈裡 verify 讀數的最大值」。但若 verify 是有雜訊/可被鑽的『代理指標』,
# 取 max 會系統性高估 —— 這叫 optimizer's curse / maximization bias(RL 裡 Double Q-learning 解的就是這個高估;
# 拍賣的 winner's curse 是同一現象的直覺類比):你選中的往往不是真的最好,而是『雜訊最高』那次。
def proxy_trap(seed, n=8):
    import random as _r
    rng = _r.Random(seed)
    trues = [rng.randint(70, 88) for _ in range(n)]              # 每次嘗試的「真實品質」
    proxies = [t + round(rng.gauss(0, 10)) for t in trues]       # verify 看到的「有雜訊讀數」
    picked = max(range(n), key=lambda i: proxies[i])             # best-so-far 用 proxy 選
    actual_best = max(range(n), key=lambda i: trues[i])          # 真正最好的那次
    return trues, proxies, picked, actual_best


# ===========================================================================
# 選用:真的 LLM agent(借姊妹課 agent-from-scratch 的 OpenRouter 模式)
# ===========================================================================
def try_real_agent_once():
    """示範 loop 怎麼包住一次真實 LLM 呼叫。沒金鑰就友善退回,絕不讓課程當掉。"""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("\n(--real:沒偵測到 OPENROUTER_API_KEY → 自動走 noisy stub。)")
        print(" 想看真的:export OPENROUTER_API_KEY=sk-or-... 再加 --real。")
        print(" 真實路徑長這樣(節錄,完整見姊妹課 agent-from-scratch 第 1 課):")
        print('   r = requests.post(URL, headers={"Authorization": f"Bearer {key}"},')
        print('                     json={"model": M, "messages": msgs}, timeout=60)')
        print('   reply = r.json()["choices"][0]["message"]["content"]')
        print('   used  = r.json()["usage"]["total_tokens"]   # token;OpenRouter 的 usage 還直接給 cost(金額)')
        return False
    try:
        import requests
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "openai/gpt-4o-mini",
                  "messages": [{"role": "user", "content": "用一句話說 loop engineering 是什麼。"}]},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        print("\n[真 LLM 回應]", data["choices"][0]["message"]["content"])
        print("[真實 token]", data["usage"]["total_tokens"], "← 把它接到 Budget 就是實測成本")
        return True
    except Exception as e:
        print(f"\n(--real:呼叫失敗 {e} → 退回 stub。網路/額度問題不該讓你卡在這課。)")
        return False


FAILURE_GALLERY = """\
真 agent 的執行期失敗圖鑑(stub 不會演,但你上線一定會遇到):
  • context 爆窗     對話越滾越長 → 超過模型上限 → 用第 9 課的上下文策略
  • rate limit / 5xx 太頻繁/伺服器掛 → 重試 + 指數退避 + 抖動(jitter)
  • 寫檔寫一半       動作做到一半進程被砍 → 冪等 + check-then-act(第 6 課)
  • flaky verify     同一份成品驗兩次結果不同 → 驗證要穩定、可重跑
  • 無限 tool-call   agent 鬼打牆狂呼叫 → max-iter 保險絲(第 1 課)就是為這個
"""


if __name__ == "__main__":
    anim.from_argv()

    if "--real" in sys.argv:
        try_real_agent_once()

    print("=" * 64)
    print("非決定性:同一個 loop,換 5 個 seed 跑,結局各不相同")
    print("=" * 64)
    for seed in range(5):
        status, iters, val = loop_each_iter(make_noisy_agent(seed))
        anim.fuse(seed, 5, label="seed")
        print(f"  seed={seed}:同一個 loop → {status:7s} 第 {iters} 圈,覆蓋率 {val}")
        anim.pause(0.5)
    print("→ 真 agent 就是這樣:同樣的 loop,結果是一個分佈,不是一個定值。")

    print("\n" + "=" * 64)
    print("隱藏 bug:『跑完只看最後一圈』會丟掉中途更好的結果")
    print("=" * 64)
    # 找一個 naive(只看末圈)失敗、但 best-so-far 成功的 seed
    for seed in range(500):
        n = naive_final_only(make_noisy_agent(seed))
        b = best_so_far_loop(make_noisy_agent(seed))
        if n[0] == "FAIL" and b[0] == "SUCCESS":
            print(f"  seed={seed}:")
            print(f"    naive_final_only → {n[0]}(只認末圈的 {n[2]})")
            print(f"    best_so_far_loop → {b[0]}(記得第 {b[1]} 圈衝到的 {b[2]})")
            print("  ⚠️  同一串隨機結果,naive 說失敗、best-so-far 說成功 —— 差別只在『有沒有記住最佳』。")
            break

    print("\n" + "=" * 64)
    print("但 best-so-far 也有陷阱:對『有雜訊的代理指標』取 max,會選到僥倖(接第 7 課)")
    print("=" * 64)
    for seed in range(300):                       # 找一個「被 proxy 選到的 ≠ 真正最好的」例子
        trues, proxies, picked, best = proxy_trap(seed)
        if picked != best:
            print(f"  best-so-far 用 proxy 選了第 {picked} 次:proxy={proxies[picked]},但真值只有 {trues[picked]}")
            print(f"  真正最好的其實是第 {best} 次:真值 {trues[best]}(它的 proxy={proxies[best]},沒被選上)")
            print(f"  → 對有雜訊的指標取 max,選中的常是『雜訊最高』那次,不是真的最好(optimizer's curse / maximization bias)。")
            print(f"  → 對策:用第 7 課的 hold-out 複驗你選出的『最佳』。proxy 高 ≠ 真的好。")
            break

    print("\n" + "=" * 64)
    print(FAILURE_GALLERY + "=" * 64)
    print("結論:真 agent 是隨機的。你的 loop 要為『分佈』設計,不是為『定值』——")
    print("  記住最佳(best-so-far)、設保險絲、重試要退避、動作要冪等。")
