"""
第 5 課 —— 平行與隔離 (Parallelism & Isolation)
================================================
一個 loop 跑得動之後,下一個念頭幾乎必然是:「能不能同時跑好幾個?」
例如同時讓三個 agent 各修一個 bug、各試一種重構方案。

可以,但有個陷阱:**如果它們共用同一份工作目錄,它們會互相踩。**
本課的 demo 會具體呈現一種:多個 worker 同時寫同一個檔,結果是**行與行交錯纏在一起、
分不出哪行是誰寫的、順序也不可信(provenance/順序遺失)**。
(注意精確說法:這不是「位元級損毀」,每行仍完整——但**不是因為 GIL**(GIL 只擋 Python bytecode 交錯,
不保證 OS 寫入原子性)。行完整是因為每行是一次小的、關檔即 flush 的 write(),加上 O_APPEND 把「定位檔尾+寫入」原子化;
而且這在 POSIX 對一般檔案並非嚴格保證、也不可移植——更大的非原子寫入仍會位元級交錯。
但對「平行 agent 的成品」來說,出處與順序遺失就已經夠致命了。)平行的前提是隔離,不是賭寫入原子性。

loop engineering 的標準隔離手段,在寫程式的場景就是 git worktree:

    git worktree add ../wt-fix-a -b fix-a    # 同一個 repo,長出一個獨立工作目錄
    git worktree add ../wt-fix-b -b fix-b    # 各自一個分支,互不干擾
    # 三個 agent 各自在自己的 worktree 裡跑 loop,跑完再 merge / 挑最好的
    git worktree remove ../wt-fix-a

每個 worktree 是同一個 repo 的獨立 checkout,共享 git 物件庫但檔案分開,
所以平行的 agent 不會互相干擾,各自的 commit 也乾乾淨淨分在各自分支上。

本課用「各自一個暫存目錄」來模擬 worktree 的隔離效果 (純標準庫、好示範),
並故意先讓你看到「共用目錄 → 互相踩」的災難,再看「各自隔離 → 平安」。
真實的 worktree 指令在 textbook 第 5 章。

執行:
    python3 lesson5_parallel_isolation.py
    python3 lesson5_parallel_isolation.py --animate    # 慢放,對照隔離 vs 互踩
"""

import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 一個會「做事 + 留下痕跡」的小 loop —— 每個 worker 跑一份
# ===========================================================================
def run_one_loop(name, workdir, shared_file):
    """模擬一個 agent 在 workdir 裡跑 3 圈,每圈寫一次它的工作檔。
    同時它也往 shared_file 寫 —— 用來示範『共用檔』被搶寫的後果。"""
    own_file = os.path.join(workdir, "result.txt")
    for i in range(3):
        # 各自的私有檔:只要 workdir 不同,就絕對安全
        with open(own_file, "a") as f:
            f.write(f"{name} 第 {i} 圈\n")
        # 共用檔:多個 worker 搶同一個檔 = 災難現場
        with open(shared_file, "a") as f:
            f.write(f"{name} 第 {i} 圈\n")
        time.sleep(0.01)  # 放大競爭,讓交錯更明顯
    # 回報這個 worker 自己看到的私有檔內容 (應該乾乾淨淨只有它自己)
    with open(own_file) as f:
        return name, f.read().strip().replace("\n", " | ")


# ===========================================================================
# Demo
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    workers = ["fix-A", "fix-B", "fix-C"]

    # -----------------------------------------------------------------------
    # 情境一:三個 loop 各自一個隔離目錄 (= worktree 的效果)
    # -----------------------------------------------------------------------
    print("=" * 64)
    print("情境一:每個 loop 各自一個隔離工作目錄 (模擬 git worktree)")
    print("=" * 64)
    anim.step("🧵", "平行啟動 3 個 loop,各有專屬目錄……")
    anim.pause(1.0)
    with tempfile.TemporaryDirectory() as base:
        shared = os.path.join(base, "shared.txt")
        open(shared, "w").close()

        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = []
            for w in workers:
                wt = os.path.join(base, f"wt-{w}")  # ← 每人一個目錄,關鍵就這行
                os.makedirs(wt)
                futures.append(ex.submit(run_one_loop, w, wt, shared))
            results = [f.result() for f in futures]

        print("\n每個 worker 私有檔的內容 (隔離 → 各自乾淨,沒被別人污染):")
        for name, content in sorted(results):
            print(f"  {name}: {content}")

    # -----------------------------------------------------------------------
    # 情境二:三個 loop 共用同一個工作檔 (沒有隔離 → 互相踩)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 64)
    print("情境二:三個 loop 共用同一個檔案 (沒有隔離 = 災難)")
    print("=" * 64)
    anim.step("🧵", "平行啟動 3 個 loop,但這次共用一個目錄……")
    anim.pause(1.0)
    with tempfile.TemporaryDirectory() as base:
        shared = os.path.join(base, "shared.txt")
        open(shared, "w").close()
        only_dir = os.path.join(base, "wt-shared")
        os.makedirs(only_dir)

        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(run_one_loop, w, only_dir, shared) for w in workers]
            [f.result() for f in futures]

        with open(os.path.join(only_dir, "result.txt")) as f:
            lines = f.read().strip().split("\n")
        print("\n共用 result.txt 的內容 (三個 worker 的字句交錯纏在一起,誰都不能信):")
        for ln in lines:
            print(f"  {ln}")
        print(f"\n  → 同一個檔被寫進 {len(lines)} 行、混了 {len(set(l.split()[0] for l in lines))} 個 worker。")
        print("    這份成品已經沒有任何一個 agent 能為它負責了。")

    print("\n" + "=" * 64)
    print("結論:要平行,先隔離。寫程式的場景用 `git worktree` 給每個 loop 一個獨立 checkout,")
    print("跑完再挑最好的分支 merge。隔離不是效能優化,是正確性的前提。")
    print("=" * 64)
