"""
build.py —— 把「真正的課程 .py 檔」內嵌進 index.html(單一真實來源,不複製、不分叉)。
每次課程內容改了,重跑這支就會同步網站。純標準庫。

用法:python3 site/build.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


# 網站第 1 課切片需要的真實檔案。key = 在 Pyodide 虛擬檔案系統裡的相對檔名。
FILES = {
    "anim.py": read("anim.py"),
    "lesson1_minimal_loop.py": read("lesson1_minimal_loop.py"),
    "_grader_utils.py": read("exercises/_grader_utils.py"),
    "exercise1_minimal_loop.py": read("exercises/exercise1_minimal_loop.py"),
    "check_exercise1.py": read("exercises/check_exercise1.py"),
    "solutions/exercise1_minimal_loop.py": read("exercises/solutions/exercise1_minimal_loop.py"),
}

CH01_MD = read("textbook/ch01_minimal_loop.md")


def main():
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        tpl = f.read()
    out = (tpl
           .replace("/*FILES_JSON*/", json.dumps(FILES, ensure_ascii=False))
           .replace("/*CH01_MD*/", json.dumps(CH01_MD, ensure_ascii=False)))
    dest = os.path.join(HERE, "index.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"✓ 已生成 {dest}({len(out):,} 字元,內嵌 {len(FILES)} 支 .py)")
    # 基本健全檢查
    assert "/*FILES_JSON*/" not in out and "/*CH01_MD*/" not in out, "placeholder 沒被替換"
    assert "loadPyodide" in out and "marked.parse" in out
    print("✓ 健全檢查通過(placeholder 已替換、Pyodide/marked 在位)")


if __name__ == "__main__":
    main()
