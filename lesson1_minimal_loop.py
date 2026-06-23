"""
第 1 課 —— 最小的閉環 (The Minimal Loop)
==========================================
這堂課唯一要你內化的觀念:

    Prompt engineering 是「你想好一句話 → 丟給 agent → 看一次結果」。
    Loop engineering 是「你設計一個系統,讓它自己反覆『做 → 驗 → 決定要不要再來』,
    直到達標或撞上限才停」。

    換句話說:loop engineering 是把『那個一直盯著 agent、決定要不要再 prompt
    一次的人』—— 也就是你 —— 換成一段程式。

一個 loop 的最小骨架,永遠是這四件事:

    goal      明確、可被機器判定的目標 (不是「弄好一點」,而是「verify 回傳 True」)
    act       做一步 (呼叫 agent / 跑一個命令 / 改一個檔)
    verify    驗一下:達標了嗎?(這一步才是 loop 的靈魂,第 2 課整課在講它)
    decide    沒達標就帶著回饋再來一圈;達標、或圈數燒完,就停

本課用一個「假 agent」當替身,讓你先看清楚迴圈本身。真正的 agent
(Claude Code / Codex / 你自己的 LLM 呼叫) 怎麼接進來,textbook 第 1 章有說。

執行:
    python3 lesson1_minimal_loop.py
    python3 lesson1_minimal_loop.py --animate    # 慢放,看 loop 一圈圈轉
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 任務設定 —— 一個「機器可判定」的目標
# ===========================================================================
# 目標:產出一段標語,必須同時 (a) 含有關鍵字「省時」 (b) 不超過 12 個字。
# 注意這個目標的關鍵特性:它可以被一段程式「客觀判定對或錯」。
# 模糊的目標 (「寫得好看一點」) 沒辦法做成 loop —— 因為 verify 不知道何時該停。
GOAL_KEYWORD = "省時"
GOAL_MAXLEN = 12


def verify(draft):
    """驗證閘門。回傳 (是否達標, 給下一圈的回饋)。

    loop 的成敗幾乎全押在這個函式上:它定義了「做完」到底是什麼意思。
    回饋不是裝飾 —— 它是下一圈 agent 唯一知道「上次哪裡不對」的管道。
    """
    if GOAL_KEYWORD not in draft:
        return False, f"缺少關鍵字「{GOAL_KEYWORD}」"
    if len(draft) > GOAL_MAXLEN:
        return False, f"太長了({len(draft)} 字),要 ≤ {GOAL_MAXLEN} 字"
    return True, "通過"


# ===========================================================================
# 假 agent —— 真實世界這裡會是一次 LLM 呼叫 / 一次 Claude Code 執行
# ===========================================================================
# 它接收「任務 + 上一圈的回饋」,吐出一個新草稿。
# 重點不在它多聰明,而在它「每一圈都看得到上一圈的回饋」—— 這就是 agent
# 能在迴圈裡愈做愈好的全部祕密。我們刻意讓它一開始故意做不好,看 loop 怎麼救回來。
_DRAFTS = [
    "讓您的生活更美好更精彩又開心",  # 沒關鍵字、又太長 —— 故意的
    "省時又省力,生活更輕鬆愉快真好",  # 有關鍵字了,但還是太長
    "省時省力好幫手",                 # 兩個條件都過
]


def mock_agent(task, feedback, attempt):
    """回傳第 attempt 次嘗試的草稿。真實 agent 會根據 feedback 真的去修改;
    這裡用預先排好的三個草稿來模擬「一圈比一圈好」的過程。"""
    draft = _DRAFTS[min(attempt, len(_DRAFTS) - 1)]
    print(f"   agent 看到的回饋:「{feedback}」 → 產出:「{draft}」")
    return draft


# ===========================================================================
# ★ 本課的全部重點:loop() —— 不到 15 行
# ===========================================================================
MAX_ITERS = 5  # 保險絲。沒有它,一個永遠驗不過的任務會讓迴圈跑到天荒地老 (= 燒錢)。


def loop(task):
    feedback = "(這是第一圈,還沒有回饋)"

    for i in range(1, MAX_ITERS + 1):
        print(f"\n[第 {i} 圈]")
        anim.fuse(i - 1, MAX_ITERS)

        # --- act:做一步 ---
        anim.step("✎", "act:請 agent 產一版草稿")
        draft = mock_agent(task, feedback, attempt=i - 1)

        # --- verify:驗一下 ---
        anim.step("🔍", "verify:檢查達標沒")
        passed, feedback = verify(draft)
        anim.pause()

        # --- decide:達標就收工,否則帶著回饋再來 ---
        if passed:
            print(f"   ✅ verify 通過 → 收工。成品:「{draft}」")
            return draft
        anim.step("↻", "decide:沒過,帶著回饋再轉一圈")
        print(f"   ✗ verify 不過:{feedback} → 再來一圈")

    # 迴圈正常結束 = 圈數燒完都還沒過 = 保險絲斷了
    print(f"\n⚠️  跑了 {MAX_ITERS} 圈仍未達標 —— 保險絲斷,該停下來看看是任務太難還是 verify 太嚴。")
    return None


# ===========================================================================
# Demo
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    print("=" * 64)
    print(f"任務:寫一句標語,要含「{GOAL_KEYWORD}」且 ≤ {GOAL_MAXLEN} 字")
    print("=" * 64)

    result = loop("寫一句產品標語")

    print("\n" + "=" * 64)
    print("你剛剛看到的,就是所有 loop engineering 的心跳:")
    print("  act(做一步) → verify(驗) → 不過就帶回饋再來 → 過了或燒完才停。")
    print("把 mock_agent 換成真的 agent、把 verify 換成跑測試,這個骨架原封不動。")
    print("=" * 64)
