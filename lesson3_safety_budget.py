"""
第 3 課 —— 安全與成本 (Safety, Budget & Staged Rollout)
========================================================
前兩課的 loop 已經會自己做、自己驗、自己停了。問題來了:

    一個會「自己反覆呼叫 agent」的系統,等於一個會「自己反覆花錢」的系統。
    而一個會「自己改你的檔案 / 自己推 commit」的系統,等於一個能在你睡覺時
    把事情搞砸的系統。

所以 loop engineering 真正難的不是讓它跑,而是讓它「安全地跑、花得起地跑」。
本課加上四道防線,它們是把玩具 loop 變成能放生的 loop 的最低門檻:

    1. max-iter 保險絲   —— 第 1、2 課就有了,這裡再強調:沒有它一切免談
    2. 預算 (budget)     —— 用 token / 金額 / 圈數設硬上限,先估再跑、邊跑邊扣
    3. run-log           —— 每一圈寫一行 JSONL。沒有日誌的自動化 = 沒發生過。
                            出事時這是你唯一的黑盒子。
    4. 分階段上線 L1→L3 —— 不要一上來就讓它自動執行。先看它「想做什麼」,
                            再讓它「做但問你」,最後才「自己做」。

       L1 report   只觀察、只報告,絕不改任何東西 (dry-run)
       L2 assisted 會動手,但每個有副作用的動作前先停下來問人
       L3 unattended 完全自動,只在出錯或預算用罄時才叫人 (escalate)

本課純標準庫、零金鑰。我們用「估算 token」的假數字示範預算怎麼扣,
並把同一個 loop 分別用 L1 / L3 跑一次,讓你看到差別。

執行:
    python3 lesson3_safety_budget.py
    python3 lesson3_safety_budget.py --animate    # 慢放,看預算一格格被扣
"""

import json
import os
import sys
import tempfile
import time
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 防線 4:自治等級
# ===========================================================================
class Level(Enum):
    L1_REPORT = 1      # 只報告,不動手
    L2_ASSISTED = 2    # 動手前問人
    L3_UNATTENDED = 3  # 全自動


# ===========================================================================
# 防線 2:預算 —— 先估、邊跑邊扣、扣光就停
# ===========================================================================
class Budget:
    """用『圈數 + token』雙重上限。任一個用罄,loop 就得停。
    真實世界你還會加上金額上限 (= token × 單價) 和 wall-clock 時間上限。"""

    def __init__(self, max_iters, max_tokens):
        self.max_iters = max_iters
        self.max_tokens = max_tokens
        self.used_iters = 0
        self.used_tokens = 0

    def can_continue(self):
        return self.used_iters < self.max_iters and self.used_tokens < self.max_tokens

    def charge(self, tokens):
        self.used_iters += 1
        self.used_tokens += tokens

    def __str__(self):
        return (f"圈數 {self.used_iters}/{self.max_iters}, "
                f"token {self.used_tokens}/{self.max_tokens}")


# ===========================================================================
# 防線 3:run-log —— 每圈一行 JSONL,append-only,永不覆蓋
# ===========================================================================
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


# ===========================================================================
# 假 agent —— 回傳「它想做的動作」+「這次花了幾個 token」
# ===========================================================================
# 注意這裡的設計:agent 永遠只「提議」一個動作 (propose),它自己不執行。
# 「要不要真的執行」由 loop 根據自治等級決定 —— 這個 propose / commit 的分離,
# 是所有安全 agent 系統的骨架。
def mock_agent(attempt):
    plan = [
        ("write_file report.md", 120),
        ("write_file report.md", 90),
        ("done", 40),
    ]
    return plan[min(attempt, len(plan) - 1)]


def execute(action, workdir):
    """真的執行一個有副作用的動作 (這裡只示範寫檔)。"""
    if action.startswith("write_file"):
        path = os.path.join(workdir, action.split()[1])
        with open(path, "a") as f:
            f.write(f"agent 寫入於 {time.strftime('%H:%M:%S')}\n")
        return f"已寫入 {path}"
    return "(無副作用)"


# ===========================================================================
# ★ 本課重點:帶四道防線的 loop
# ===========================================================================
def safe_loop(level, budget, logfile, workdir):
    print(f"\n--- 以 {level.name} 等級啟動,預算上限 [{budget}] ---")

    while budget.can_continue():
        anim.fuse(budget.used_iters, budget.max_iters, label="圈數預算")
        anim.step("✎", "act:agent 提議一個動作")
        action, tokens = mock_agent(budget.used_iters)
        budget.charge(tokens)  # 防線 2:先記帳
        anim.pause()

        # agent 說做完了 → 正常收工
        if action == "done":
            log_event(logfile, level=level.name, action="done", budget=str(budget))
            print(f"   [{budget}] agent 收工 ✅")
            return "SUCCESS"

        # 防線 4:依自治等級決定怎麼處理「有副作用的動作」
        if level is Level.L1_REPORT:
            # 只報告,絕不執行
            print(f"   [{budget}] (L1 dry-run) agent 想做:{action} —— 不執行,只記錄")
            log_event(logfile, level=level.name, proposed=action, executed=False, budget=str(budget))
        else:
            if level is Level.L2_ASSISTED:
                # 真實情境這裡會 input() 問人;教學裡我們假設人按了 y
                print(f"   [{budget}] (L2) agent 想做:{action} —— [假設人核准]")
            else:
                print(f"   [{budget}] (L3) agent 自動執行:{action}")
            result = execute(action, workdir)
            log_event(logfile, level=level.name, proposed=action, executed=True,
                      result=result, budget=str(budget))

    # while 條件為假 = 預算用罄 → 這是「中止」,不是「成功」。要叫人。
    print(f"   [{budget}] ⚠️  預算用罄,escalate 給人類 —— 沒做完就被斷,得有人來看")
    log_event(logfile, level=level.name, action="ESCALATE_budget_exhausted", budget=str(budget))
    return "ESCALATED"


# ===========================================================================
# Demo —— 同一個 loop,分別用 L1 和 L3 跑
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    with tempfile.TemporaryDirectory() as workdir:
        logfile = os.path.join(workdir, "run.jsonl")

        print("=" * 64)
        print("同一個任務,先 L1 (只報告) 再 L3 (全自動),看 run-log 怎麼長")
        print("=" * 64)

        # L1:dry-run,先看 agent「想幹嘛」,不冒任何風險
        safe_loop(Level.L1_REPORT, Budget(max_iters=5, max_tokens=1000), logfile, workdir)

        # L3:確認 L1 看起來沒問題後,才放生全自動
        safe_loop(Level.L3_UNATTENDED, Budget(max_iters=5, max_tokens=1000), logfile, workdir)

        # 故意給一個會被預算掐死的 loop,示範 escalate
        print("\n--- 故意把預算設超小,示範『預算用罄 → escalate』 ---")
        safe_loop(Level.L3_UNATTENDED, Budget(max_iters=1, max_tokens=1000), logfile, workdir)

        print("\n" + "=" * 64)
        print("run.jsonl 的內容 (你的黑盒子,出事時就看它):")
        print("-" * 64)
        with open(logfile) as f:
            print(f.read().strip())
        print("=" * 64)
        print("放生任何 loop 前,先確認:保險絲、預算、run-log、從 L1 開始 —— 四個都有了嗎?")
