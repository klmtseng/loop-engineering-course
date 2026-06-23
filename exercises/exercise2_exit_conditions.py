"""
練習 2 —— 退出條件與驗證閘門 (對應第 2 課)
==========================================
鷹架(Exit、agent、run_check、寫檔)都給你了。你只要實作 loop()。

要實作的 loop(check_cmd, workdir) 規格,回傳 (Exit, code_or_None):
  每圈 (最多 MAX_ITERS 圈):
    1. code = agent(feedback, attempt=i-1)
    2. 【STALL 出口】若 code 和上一圈完全相同 → return (Exit.STALL, None)
    3. 把 code 寫進 workdir/add.py (用給好的 write_code)
    4. passed, output = run_check(check_cmd, workdir)
    5. 【SUCCESS 出口】passed 為真 → return (Exit.SUCCESS, code)
    6. 否則把 output 當下一圈的 feedback
  跑完都沒過 → 【FUSE 出口】return (Exit.FUSE, None)

完成後驗收:
    python3 check_exercise2.py
"""

import os
import subprocess
from enum import Enum

MAX_ITERS = 6


class Exit(Enum):
    SUCCESS = "達標,綠了"
    FUSE = "保險絲斷(圈數燒完)"
    STALL = "卡住(連續兩圈產出相同)"


def run_check(cmd, cwd):
    """【已給你】跑命令,回傳 (是否通過, 輸出)。autograder 會替換它。"""
    p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=30)
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def agent(feedback, attempt):
    """【已給你】替身。autograder 會替換它。"""
    versions = ["print(40 + )\n", "print(20 + 21)\n", "print(20 + 22)\n"]
    return versions[min(attempt, len(versions) - 1)]


def write_code(code, workdir):
    """【已給你】把程式碼寫進 workdir/add.py。"""
    with open(os.path.join(workdir, "add.py"), "w") as f:
        f.write(code)


def loop(check_cmd, workdir):
    # ===================================================================
    # TODO: 實作握有 SUCCESS / FUSE / STALL 三個出口的 loop (見檔頭規格)
    # ===================================================================
    raise NotImplementedError("實作你的 loop()")
