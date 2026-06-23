"""
練習 5 —— 平行與隔離 (對應第 5 課)
====================================
run_one_loop 給你了(每個 worker 在自己的 workdir 寫 3 行,回傳私有檔內容)。
你要實作 run_isolated():讓多個 worker 平行跑,而且彼此隔離不互踩。

要實作的 run_isolated(workers, base) 規格:
  - 對每個 worker 名字,在 base 底下建一個「專屬」子目錄(關鍵:每人一個!)
  - 用 ThreadPoolExecutor 平行跑 run_one_loop(name, 該 worker 的專屬目錄)
  - 回傳 dict: {worker 名字: 該 worker run_one_loop 的回傳內容}

完成後驗收:
    python3 check_exercise5.py
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor


def run_one_loop(name, workdir):
    """【已給你】在 workdir 跑 3 圈,各寫一行到私有 result.txt,回傳其內容。"""
    own = os.path.join(workdir, "result.txt")
    for i in range(3):
        with open(own, "a") as f:
            f.write(f"{name} 第 {i} 圈\n")
        time.sleep(0.005)
    with open(own) as f:
        return f.read().strip()


def run_isolated(workers, base):
    # ===================================================================
    # TODO: 每個 worker 一個專屬子目錄,平行跑,回傳 {name: content}
    # ===================================================================
    raise NotImplementedError("實作你的 run_isolated()")
