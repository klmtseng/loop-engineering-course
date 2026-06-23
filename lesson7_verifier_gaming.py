"""
第 7 課 —— verify 是代理指標,而 agent 會鑽它 (Verifier Gaming)
================================================================
這是整門課最重要的一堂。前六課讓你相信「跑 verify、綠了就收工」。現在拆穿一半:

    verify 不是「對不對」的真相,它只是真相的『代理指標 (proxy)』。
    而 agent 不是在解你的問題 —— 它是在『讓 verify 變綠』。這兩件事不一定一樣。

還記得第 2 課嗎?任務是「印出 42」,agent 交出的是 `print(20 + 22)` ——
它沒寫出一個會加法的程式,它把答案『硬編』進去,剛好騙過那個只檢查一次的 verify。
在真實世界,這正是 agent 最常見的三種作弊:

    1. 硬編答案    —— 直接回傳期望值,不解決一般問題
    2. 改弱驗證    —— 把失敗的測試刪掉 / 改成 assert True
    3. 空轉假裝    —— 什麼都沒做,但讓 verify 通過

這有個名字:**Goodhart 定律** ——「當一個指標變成目標,它就不再是好指標」。
你的 loop 品質上限 = 你的 verify 有多難被鑽。

本課用一個會加法的任務,示範「弱 verify」如何被硬編騙過、「強 verify」如何抓出來。
純標準庫、零金鑰。

執行:
    python3 lesson7_verifier_gaming.py
    python3 lesson7_verifier_gaming.py --animate
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 任務:寫一個 add(a, b) 回傳 a + b
# ===========================================================================
# 「公開案例」是你寫得出來、agent 也看得到的;「隱藏案例」是你留一手、不給 agent 看的。
PUBLIC_CASES = [(20, 22, 42)]                       # 第 2 課就只驗了這一種
HIDDEN_CASES = [(1, 1, 2), (3, 4, 7), (-5, 5, 0)]   # 留一手


def build(code):
    """把 agent 交出的程式碼字串變成可呼叫的 add 函式。"""
    ns = {}
    exec(code, ns)
    return ns["add"]


# ===========================================================================
# 兩種 verify:弱的只驗公開案例;強的加上隱藏案例 + 隨機輸入
# ===========================================================================
def weak_verify(add):
    """只驗一組公開案例 —— 一眼就能被硬編騙過。(這就是第 2 課的 verify)"""
    return all(add(a, b) == want for a, b, want in PUBLIC_CASES)


def strong_verify(add):
    """公開 + 隱藏 + 隨機。硬編一個答案過不了多組互異輸入。"""
    for a, b, want in PUBLIC_CASES + HIDDEN_CASES:
        if add(a, b) != want:
            return False
    for _ in range(20):  # 隨機抽查:擋掉「把所有隱藏案例也硬編」的偷吃步
        a, b = random.randint(-100, 100), random.randint(-100, 100)
        if add(a, b) != a + b:
            return False
    return True


# ===========================================================================
# 三個 agent:一個老實,兩個在鑽 verify
# ===========================================================================
AGENTS = {
    "老實做事的 agent": "def add(a, b):\n    return a + b",
    "硬編答案的 agent": "def add(a, b):\n    return 42",          # 只為了騙 weak_verify
    "差一點點的 agent": "def add(a, b):\n    return a + b + 1",   # 看起來有寫,但有 bug
}


def demo():
    print("=" * 64)
    print("同一個任務(add(a,b)=a+b),看 弱verify 和 強verify 各自信了誰")
    print("=" * 64)
    for name, code in AGENTS.items():
        anim.banner(name)
        add = build(code)
        anim.step("✎", f"{name} 交出:{code.splitlines()[-1].strip()}")
        weak = weak_verify(add)
        anim.step("🔍", "弱 verify(只驗 20+22)")
        strong = strong_verify(add)
        anim.step("🔬", "強 verify(公開+隱藏+隨機)")
        print(f"\n  {name}")
        print(f"    程式碼:{code.splitlines()[-1].strip()}")
        print(f"    弱 verify(只驗 20+22)→ {'綠 ✅' if weak else '紅 ✗'}")
        print(f"    強 verify(多組+隨機)→ {'綠 ✅' if strong else '紅 ✗'}")
        if weak and not strong:
            print("    ⚠️  弱 verify 被騙了!agent 沒解決問題,只是讓你那一個檢查變綠。")
        anim.pause(0.8)


if __name__ == "__main__":
    anim.from_argv()
    demo()
    print("\n" + "=" * 64)
    print("三種真實作弊手法,本課只演了第 1 種(硬編);另外兩種一樣致命:")
    print("  2. 改弱驗證 —— 你的 verify 若是『跑 repo 的測試』,agent 可以把測試刪掉/改成 assert True")
    print("  3. 空轉假裝 —— 什麼都沒做,但讓 verify 通過")
    print("-" * 64)
    print("對策(把 verify 變難鑽):")
    print("  • hold-out:留一手、agent 看不到也改不到的隱藏案例")
    print("  • 多組 + 隨機輸入:一個硬編的答案過不了互異輸入")
    print("  • 隔離:agent 不能修改 verify / 測試本身(第 5 課的隔離也是為了這個)")
    print("  • 人抽查:高風險的 loop,綠了也要人定期抽看(這就是第 3 課 L1→L3 的意義)")
    print("=" * 64)
    print("記住:loop 的品質上限 = verify 有多難被鑽。verify 寫得爛,loop 只會更快地產出垃圾。")
