"""
第 4 課 —— maker / checker 雙代理 (Independent Verification)
============================================================
到目前為止,做事的 agent 也是驗收的人 —— verify 函式由我們寫死。但當驗收
本身需要判斷力 (「這份摘要忠於原文嗎?」「這段重構有沒有偷改行為?」),
你會很想直接問做事的那個 agent:「你覺得你做完了嗎?」

千萬別。讓 agent 自己驗自己的成果,是 loop engineering 最常見的翻車點:

    它幾乎永遠會說「做得很好,通過!」—— 這叫自我感覺良好 (grading inflation)。
    一個有動機說「我完成了」的 agent,不是個公正的裁判。

解法是把角色拆開,這是品管界一百年前就懂的 maker/checker 原則:

    maker   (做事的) 只管產出,不管驗收
    checker (驗收的) 是「另一個」agent,帶著獨立、而且更嚴的標準,
            它只有兩個輸出:approve,或 reject + 具體該怎麼改

loop 變成:maker 做 → checker 驗 → reject 就把 checker 的意見當回饋丟回 maker
再做一輪 → 直到 checker approve,或圈數燒完。

關鍵字是「獨立」:checker 不該知道 maker「有多努力」,只看成品對不對。
真實世界裡 maker 和 checker 常用不同的 system prompt、甚至不同的模型,
確保它們不會犯一樣的盲點。

本課純標準庫。我們先示範「maker 自評」如何太早放水,再換成「獨立 checker」
把關,看同一份草稿的命運如何不同。

執行:
    python3 lesson4_maker_checker.py
    python3 lesson4_maker_checker.py --animate    # 慢放,看 maker↔checker 來回
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 任務:寫一句客服回覆。隱藏的硬標準 (checker 才知道,maker 不知道):
#   1. 必須有道歉字眼 (抱歉 / 不好意思)
#   2. 必須給出明確的下一步 (含「會」字的承諾)
#   3. 不能超過 40 字
# maker 只被告知「寫一句得體的客服回覆」—— 它不知道這三條細則,
# 所以它會覺得自己隨便寫寫就很好了。這正是為什麼需要獨立 checker。
# ===========================================================================
_MAKER_DRAFTS = [
    "您的問題我們已經收到了,謝謝。",                          # 沒道歉、沒承諾
    "不好意思造成困擾,謝謝您的耐心等候與體諒。",              # 有道歉,但沒給下一步
    "不好意思造成困擾,我們會在 24 小時內回覆您。",            # 三條全中
]


def maker(feedback, attempt):
    """做事的 agent:只負責產出。真實世界是一次 LLM 呼叫。"""
    draft = _MAKER_DRAFTS[min(attempt, len(_MAKER_DRAFTS) - 1)]
    print(f"   maker 收到回饋:「{feedback}」")
    print(f"   maker 產出:「{draft}」")
    return draft


def maker_self_grade(draft):
    """maker 自評 —— 故意演出『自我感覺良好』。它沒拿到硬標準,
    又有動機說自己做完了,於是隨便看看就放行。這就是反面教材。"""
    return True, "我覺得寫得不錯,通過!"


def checker(draft):
    """獨立驗收的 agent:帶著 maker 看不到的嚴格標準,只回 approve 或 reject+原因。
    真實世界這是『另一次』LLM 呼叫,用不同的 system prompt 扮演挑剔的審稿人。"""
    problems = []
    if not any(w in draft for w in ("抱歉", "不好意思")):
        problems.append("缺少道歉字眼")
    if "會" not in draft:
        problems.append("沒有給出明確的下一步承諾")
    if len(draft) > 40:
        problems.append(f"太長({len(draft)} 字),要 ≤ 40")
    if problems:
        return False, ";".join(problems)
    return True, "approve"


MAX_ITERS = 6


def loop(grader, grader_name):
    """同一個 loop 骨架,換不同的驗收者 (grader)。"""
    print(f"\n{'=' * 64}\n用「{grader_name}」當驗收者\n{'=' * 64}")
    feedback = "(第一圈,還沒有回饋)"

    for i in range(1, MAX_ITERS + 1):
        print(f"\n[第 {i} 圈]")
        anim.fuse(i - 1, MAX_ITERS)
        anim.step("✎", "maker:產一版草稿")
        draft = maker(feedback, attempt=i - 1)

        anim.step("🔍", "checker:獨立驗收")
        approved, comment = grader(draft)
        anim.pause()
        if approved:
            print(f"   驗收 → ✅ {comment}")
            print(f"   收工。成品:「{draft}」")
            return draft

        print(f"   驗收 → ✗ reject:{comment}")
        feedback = comment  # checker 的意見,就是 maker 下一圈的施工圖

    print(f"   ⚠️  {MAX_ITERS} 圈仍未通過")
    return None


# ===========================================================================
# Demo —— 同一個 maker,兩種驗收者,結局天差地別
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    print("情境 A:maker 自己驗自己 (反面教材)")
    a = loop(maker_self_grade, "maker 自評")

    print("\n\n情境 B:換成獨立的 checker 把關")
    b = loop(checker, "獨立 checker")

    print("\n" + "=" * 64)
    print("對照:")
    print(f"  自評收工的成品:「{a}」  ← 第一圈就放行,根本沒道歉、沒承諾")
    print(f"  checker 收工的成品:「{b}」  ← 被打回兩次,逼出真正合格的版本")
    print("=" * 64)
    print("教訓:會說『我做完了』的 agent 不是公正的裁判。")
    print("把 maker 和 checker 拆開、給 checker 獨立而更嚴的標準 —— 這是放生 loop 的前提。")
