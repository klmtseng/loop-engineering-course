"""
第 6 課 (Capstone) —— 排程與無人值守 (Scheduling & Unattended Loops)
====================================================================
前五課的 loop 都有一個共同點:你得「親手按下執行」。最後一塊拼圖,是讓
loop 自己醒來。把一個 loop 接上排程器 (cron),它就從「一個腳本」變成
「一個系統」—— 一個在你睡覺時也持續巡邏、發現問題就處理、處理不了才叫你的系統。

    "Design AI loops that ship while you sleep."

這一課把第 1~5 課的零件組裝成一個迷你的「無人值守巡檢 loop」,並示範它
最自然的形態 —— 一個 tick():

    triage  掃一遍世界,有沒有要處理的事?(沒事就什麼都不做,這很重要)
    act     有事就做一步 (帶 maker/checker、帶 verify)         ← 第 1、2、4 課
    log     不管做沒做,都寫一行 run-log                        ← 第 3 課
    decide  搞定 → 記錄收工;搞不定 → escalate 叫人              ← 第 3 課

然後把 tick() 交給排程器,讓它「每 N 分鐘 / 每天早上」自己跑。

本課用一個自製的迷你排程器把 tick() 連跑幾次 (--once 只跑一次),
真實的 cron 安裝指令在最後印出來,也在 textbook 第 6 章。純標準庫、零金鑰。

執行:
    python3 lesson6_scheduling.py           # 連跑幾個 tick,看它自己運轉
    python3 lesson6_scheduling.py --once    # 只跑一個 tick (cron 每次就是這樣呼叫)
    python3 lesson6_scheduling.py --animate # 慢放,看排程一拍拍把事做掉
"""

import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 一個模擬的「世界」—— 待辦事項佇列。真實世界這會是:
#   未處理的 GitHub issue / 紅掉的 CI / 過期的依賴 / 新進的客服信 ...
# ===========================================================================
class World:
    def __init__(self, todos, done=None, escalated=None):
        self.todos = list(todos)            # 待處理
        self.done = list(done or [])        # 已完成
        self.escalated = list(escalated or [])  # 處理不了、丟給人類的

    def has_work(self):
        return bool(self.todos)

    def to_dict(self):
        return {"todos": self.todos, "done": self.done, "escalated": self.escalated}


# ===========================================================================
# 真・外部狀態 —— cron 的 loop 為什麼可靠,全靠狀態存在進程「之外」
# ===========================================================================
# 每次 cron 呼叫都是一個全新進程,記憶體裡什麼都沒有。所以待辦佇列必須讀寫一個
# 進程外的檔案(這裡用 JSON;真實世界是 DB / issue 佇列 / 訊息佇列)。
# 這樣 --once 連跑兩次才會「接續」而不是「從頭再來」,做過的事也不會重做(去重)。
def load_world(state_file, seed):
    if os.path.exists(state_file):
        with open(state_file) as f:
            d = json.load(f)
        return World(d["todos"], d["done"], d["escalated"])
    return World(seed)  # 第一次:用種子佇列初始化


def save_world(state_file, world):
    with open(state_file, "w") as f:
        json.dump(world.to_dict(), f, ensure_ascii=False, indent=2)


# ===========================================================================
# 第 4 課的零件:maker / checker (極簡版)
# ===========================================================================
def maker(task):
    # 模擬:多數任務做得好,但 "deploy" 這種高風險任務它會做砸 (回傳 None)
    return None if task.startswith("deploy") else f"已完成 [{task}]"


def checker(task, result):
    return result is not None and result.startswith("已完成")


# ===========================================================================
# 第 3 課的零件:run-log
# ===========================================================================
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%H:%M:%S")
    with open(logfile, "a") as f:
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")


# ===========================================================================
# ★ Capstone:一個 tick —— 無人值守 loop 的一次心跳
# ===========================================================================
def tick(world, logfile):
    # --- triage:有事嗎?沒事就乾淨地什麼都不做 (這是好公民的 loop) ---
    if not world.has_work():
        log_event(logfile, event="idle")
        print("   [tick] 沒有待辦 → 安靜跳過 (不做事也是一種正確的結果)")
        return

    task = world.todos.pop(0)
    print(f"   [tick] 撿起任務:{task}")

    # --- act + verify:maker 做、checker 獨立驗 (第 4 課) ---
    anim.step("✎", "act:maker 動手")
    anim.step("🔍", "verify:checker 獨立驗收")
    result = maker(task)
    if checker(task, result):
        world.done.append(task)
        log_event(logfile, event="done", task=task)
        print(f"          ✅ 完成並通過驗收:{task}")
    else:
        # --- decide:checker 不過 = 自動處理不了 → escalate 叫人 (第 3 課) ---
        world.escalated.append(task)
        log_event(logfile, event="escalate", task=task, reason="checker 未通過")
        print(f"          🔺 處理不了,escalate 給人類:{task}")


# ===========================================================================
# 迷你排程器 —— 真實世界這層由 cron / systemd timer / GitHub Actions 取代
# ===========================================================================
def scheduler(world, logfile, ticks, interval):
    for n in range(1, ticks + 1):
        print(f"\n── 第 {n} 次排程觸發 ({time.strftime('%H:%M:%S')}) ──")
        anim.fuse(n - 1, ticks, label="排程")
        tick(world, logfile)
        anim.pause()
        if n < ticks:
            time.sleep(interval)


# ===========================================================================
# Demo
# ===========================================================================
SEED = [
    "triage issue #312", "bump dependency lodash",
    "deploy v2.1 to staging", "triage issue #313",
]
# 進程外的狀態檔。cron 每次呼叫都是新進程,就靠這個檔接續。
STATE_FILE = "/tmp/loop6_queue.json"
PERSIST_LOG = "/tmp/loop6_run.jsonl"

if __name__ == "__main__":
    anim.from_argv()

    if "--reset" in sys.argv:
        for p in (STATE_FILE, PERSIST_LOG):
            if os.path.exists(p):
                os.remove(p)
        print(f"已清空狀態:{STATE_FILE}")
        sys.exit(0)

    print("=" * 64)
    print("無人值守巡檢 loop —— 把第 1~5 課的零件組裝成一個會自己醒來的系統")
    print("=" * 64)

    if "--once" in sys.argv:
        # ===== cron 模式:讀外部狀態 → 跑一拍 → 寫回。連跑會接續、去重 =====
        world = load_world(STATE_FILE, SEED)
        print(f"\n(--once:cron 每次就這樣呼叫。狀態讀自 {STATE_FILE})")
        print(f"  這一拍開始前,佇列還剩:{world.todos}")
        tick(world, PERSIST_LOG)
        save_world(STATE_FILE, world)
        print(f"  這一拍結束後,佇列還剩:{world.todos}")
        print("-" * 64)
        print(f"累計:完成 {len(world.done)}、escalate {len(world.escalated)}、待辦 {len(world.todos)}")
        print(f"→ 再跑一次 `--once` 它會【接著】做下一件,不會從頭重來(這就是『狀態外存』)。")
        print(f"→ 想重置:python3 lesson6_scheduling.py --reset")
    else:
        # ===== 即時觀看模式:記憶體內連跑 6 拍,看它一拍拍把事做掉 =====
        with tempfile.TemporaryDirectory() as base:
            logfile = os.path.join(base, "run.jsonl")
            world = World(SEED)
            scheduler(world, logfile, ticks=6, interval=0.3)
            print("\n" + "=" * 64)
            print(f"結算:完成 {len(world.done)} 件、escalate {len(world.escalated)} 件、剩 {len(world.todos)} 件")
            print(f"  已完成:{world.done}")
            print(f"  丟給人類:{world.escalated}")

    # --- 真實世界怎麼讓它自己醒來 ---
    print("=" * 64)
    print("要讓它真的『自己醒來』,把 --once 模式掛上 cron 就行(狀態靠 STATE_FILE 接續):")
    print()
    print("  # 每天早上 9 點跑一拍 (crontab -e 貼這行):")
    print(f"  0 9 * * *  cd {os.getcwd()} && /usr/bin/python3 lesson6_scheduling.py --once >> ~/loop.log 2>&1")
    print()
    print("  # 或每 15 分鐘一次:")
    print("  */15 * * * *  ...同上... --once")
    print("=" * 64)
    print("這就是 loop engineering 的終點:你設計一次,系統替你跑無數次 —— 趁你睡覺時出貨。")
