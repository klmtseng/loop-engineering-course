"""
第 2 課 —— 退出條件與驗證閘門 (Exit Conditions & the Verify Gate)
=================================================================
第 1 課的 verify 是一個 Python 函式。真實世界裡,最可靠的驗證閘門通常是
「跑一個命令、看它的結束碼 (exit code)」:

    pytest            → 0 = 全綠
    ruff check .      → 0 = 沒問題
    npm run build     → 0 = 編得過
    curl -f health    → 0 = 服務還活著

這種「between-iteration command」是 loop engineering 的標準零件:
每一圈做完事,就跑一次檢查命令,用它的結束碼決定 loop 的命運。

但「跑到綠為止」只是其中一個退出條件。一個能在真實世界活下來的 loop,
至少要同時握有三個出口:

    1. SUCCESS  檢查命令回傳 0 → 達標,收工 (這是你要的結局)
    2. FUSE     圈數燒完仍未綠 → max-iter 保險絲,中止 (防無限燒錢)
    3. STALL    連續兩圈產出一模一樣 → 卡住了,再跑也是白跑,提早止血

少了 STALL,你的 loop 會在「鬼打牆」時把 max-iter 整個燒完才停 ——
能省下的那幾圈,就是省下的錢和時間。

⚠️ 講精確一點:這裡的 STALL 只比對「上一圈」,所以它只抓得到『不動點』(連續兩圈完全相同)。
   它抓【不到】長度 ≥ 2 的循環,例如 A,B,A,B,A,B 這種來回震盪——那種還是會燒到 FUSE。
   要抓循環,得記住「最近 N 圈的產出集合」,出現重複就判定打轉(仍是啟發式,見 textbook 延伸練習)。
   本課保持 STALL 最簡形式,但你要知道它的界線在哪。

本課做一個真的會跑 subprocess 的 loop:目標是讓一支自動產生的 Python 檔
能通過一條檢查命令。全程純標準庫,不需金鑰、不需網路。

執行:
    python3 lesson2_exit_conditions.py
    python3 lesson2_exit_conditions.py --animate    # 慢放,看紅→紅→綠 + 保險絲
"""

import os
import subprocess
import sys
import tempfile
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anim


# ===========================================================================
# 驗證閘門 —— 跑一個真的命令,回傳 (是否通過, 命令的輸出)
# ===========================================================================
def run_check(cmd, cwd):
    """跑檢查命令。結束碼 0 = 通過。輸出 (stdout+stderr) 當回饋餵回 agent。

    這就是「between-iteration command」的本體。注意我們把它的輸出原封不動
    交給下一圈 —— agent 修錯的依據,就是測試/編譯器吐出來的真實錯誤訊息。
    """
    proc = subprocess.run(
        cmd, cwd=cwd, shell=True,
        capture_output=True, text=True, timeout=30,
    )
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output


# ===========================================================================
# 假 agent —— 真實世界這裡是 Claude Code / Codex 去改程式碼
# ===========================================================================
# 任務:寫出一支會印出 "42" 的 add.py。我們讓它前兩次故意出包:
#   第 0 次:語法錯 (跑起來就炸)            → 檢查命令非 0
#   第 1 次:跑得過,但答案錯 (印出 41)       → 檢查命令非 0
#   第 2 次:正確                            → 檢查命令 = 0
# 真實 agent 會「讀上一圈的錯誤輸出」再修;這裡用排好的版本模擬那個過程。
_VERSIONS = [
    "print(40 + )\n",        # SyntaxError
    "print(20 + 21)\n",      # 跑得過但 = 41,不對
    "print(20 + 22)\n",      # = 42,正確
]


def mock_agent(feedback, attempt):
    code = _VERSIONS[min(attempt, len(_VERSIONS) - 1)]
    print(f"   ↳ agent 讀到的回饋:{feedback[:50]!r}")
    print(f"   ↳ agent 寫出的程式:{code.strip()!r}")
    return code


# ===========================================================================
# ★ 本課重點:一個握有三個出口的 loop
# ===========================================================================
class Exit(Enum):
    SUCCESS = "達標,綠了"
    FUSE = "保險絲斷 (圈數燒完)"
    STALL = "卡住 (連續兩圈產出相同)"


MAX_ITERS = 6


def loop(check_cmd, workdir):
    feedback = "(第一圈,還沒有回饋)"
    last_code = None  # 記住上一圈的產出,用來偵測 STALL

    for i in range(1, MAX_ITERS + 1):
        print(f"\n[第 {i} 圈]")
        anim.fuse(i - 1, MAX_ITERS)

        # --- act:agent 產出新版本,寫進工作目錄 ---
        anim.step("✎", "act:agent 產一版程式碼")
        code = mock_agent(feedback, attempt=i - 1)

        # --- 出口 3:STALL —— 這圈和上圈產出一模一樣,再跑也沒意義 ---
        if code == last_code:
            print("   ⏹  和上一圈產出完全相同 → STALL,提早止血")
            return Exit.STALL, None
        last_code = code

        target = os.path.join(workdir, "add.py")
        with open(target, "w") as f:
            f.write(code)

        # --- verify:跑真的檢查命令 ---
        anim.step("🔍", "verify:跑檢查命令看結束碼")
        passed, output = run_check(check_cmd, cwd=workdir)
        print(f"   ↳ 檢查命令 `{check_cmd}` → {'綠 ✅' if passed else '紅 ✗'}  輸出:{output!r}")
        anim.pause()

        # --- 出口 1:SUCCESS ---
        if passed:
            return Exit.SUCCESS, code

        feedback = output  # 把錯誤輸出餵給下一圈

    # --- 出口 2:FUSE ---
    return Exit.FUSE, None


# ===========================================================================
# 檢查腳本 —— loop 的「between-iteration command」就跑它
# ===========================================================================
# 真實專案裡這會是 pytest / ruff / build。這裡我們現寫一支小檢查腳本:
# 跑 add.py、比對輸出,結束碼 0/1 當閘門,並印出「人和 agent 都讀得懂」的訊息。
# 關鍵:它的輸出要有用 —— 那是下一圈 agent 修錯的唯一線索。
CHECK_PY = r'''
import subprocess, sys
r = subprocess.run([sys.executable, "add.py"], capture_output=True, text=True)
got = r.stdout.strip()
if r.returncode != 0:
    print("add.py 執行就炸了:\n" + r.stderr.strip()); sys.exit(1)
if got != "42":
    print(f"跑得過,但印出的是 {got!r},期望 '42'"); sys.exit(1)
print("OK:印出 42"); sys.exit(0)
'''


# ===========================================================================
# Demo
# ===========================================================================
if __name__ == "__main__":
    anim.from_argv()
    with tempfile.TemporaryDirectory() as workdir:
        with open(os.path.join(workdir, "check.py"), "w") as f:
            f.write(CHECK_PY)
        check_cmd = "python3 check.py"

        print("=" * 64)
        print("任務:讓 agent 反覆改 add.py,直到 `python3 add.py` 印出 42")
        print(f"工作目錄:{workdir}")
        print(f"檢查命令:{check_cmd}")
        print("=" * 64)

        reason, code = loop(check_cmd, workdir)

        print("\n" + "=" * 64)
        print(f"退出原因:{reason.name} —— {reason.value}")
        if reason is Exit.SUCCESS:
            print(f"通過的程式碼:{code.strip()!r}")
        print("=" * 64)
        print("記住:verify 用『跑命令看結束碼』,退出條件至少要有 SUCCESS / FUSE / STALL 三個。")
        print("換個 check_cmd (pytest、ruff、build…),這支 loop 一個字都不用改。")
