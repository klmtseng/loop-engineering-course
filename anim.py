"""
anim.py —— 終端動畫小助手(純標準庫,選用)
=============================================
讓學生「看著 loop 真的在轉」。每一課加上 `--animate` 就會慢放演示
act→verify→decide 的節奏,並畫出保險絲進度條。

設計重點:**關閉時(沒給 --animate)所有函式都是 no-op**——不印任何東西、不 sleep。
所以課程的預設輸出一個字都不會變,自動化/autograder 也完全不受影響。

用法(在課程腳本裡):
    import anim
    anim.from_argv()        # 讀 argv 的 --animate;沒給就維持一般模式

    anim.pause()            # 慢放停頓(關閉時不 sleep)
    anim.fuse(i, MAX)       # 畫保險絲條 ◉◉◯◯(關閉時不印)
    anim.step("✎", "做一步")  # 帶停頓的敘述行(關閉時不印)
"""

import sys
import time

_ON = False  # 是否開啟動畫(--animate)


def from_argv(argv=None):
    """從命令列參數判斷要不要開動畫。回傳是否開啟。"""
    global _ON
    argv = sys.argv if argv is None else argv
    _ON = "--animate" in argv
    return _ON


def on():
    return _ON


def pause(seconds=0.7):
    """慢放停頓。關閉時不 sleep(所以一般/CI 跑起來照樣很快)。"""
    if _ON:
        time.sleep(seconds)


def fuse(used, total, label="保險絲"):
    """畫一條保險絲/進度條:◉ 已用、◯ 剩餘。關閉時不印。"""
    if not _ON:
        return
    bar = "◉" * used + "◯" * max(0, total - used)
    print(f"      {label} [{bar}] {used}/{total}")
    pause(0.25)


def step(glyph, msg, seconds=0.7):
    """印一行帶字形的敘述步驟並停頓。關閉時不印(預設輸出不變)。"""
    if not _ON:
        return
    print(f"      {glyph} {msg}")
    pause(seconds)


def banner(msg):
    """動畫模式下的小標題。關閉時不印。"""
    if not _ON:
        return
    print(f"\n  ╭─ {msg}")
    pause(0.4)
