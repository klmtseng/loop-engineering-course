"""
quiz.py —— 知識測驗 runner
===========================
    python3 quiz.py --chapter 3     # 只考第 3 章
    python3 quiz.py --all           # 全部章節
    python3 quiz.py --check         # 不互動,只檢查題庫格式是否正確(供 CI/驗證用)

mcq / short 自動批改;reflect(反思題)顯示參考答案後由你自評。
誠實面對:能自動批的就自動批,需要判斷力的就給範本答案讓你對照——這正是第 4 章的精神。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiz_bank import BANK


def validate_bank():
    """--check:驗證題庫格式。回傳問題清單(空 = 沒問題)。"""
    errs = []
    for i, q in enumerate(BANK):
        where = f"第 {i} 題 (ch{q.get('ch', '?')})"
        if q.get("type") not in ("mcq", "short", "reflect"):
            errs.append(f"{where}: type 不合法")
        if not q.get("q"):
            errs.append(f"{where}: 缺題目")
        if not q.get("model"):
            errs.append(f"{where}: 缺參考答案 model")
        if q.get("type") == "mcq":
            opts = q.get("options", [])
            if len(opts) < 2:
                errs.append(f"{where}: mcq 選項太少")
            if not isinstance(q.get("answer"), int) or not (0 <= q.get("answer", -1) < len(opts)):
                errs.append(f"{where}: mcq answer 索引超出範圍")
        if q.get("type") == "short" and not q.get("accept"):
            errs.append(f"{where}: short 缺 accept 關鍵字")
    return errs


def ask(q):
    """問一題,回傳 (是否答對, 是否可自動批改)。"""
    print("\n" + q["q"])
    if q["type"] == "mcq":
        for i, opt in enumerate(q["options"]):
            print(f"  {i + 1}. {opt}")
        raw = input("你的答案(輸入編號):").strip()
        ok = raw.isdigit() and int(raw) - 1 == q["answer"]
        print(("✅ 答對!" if ok else f"❌ 正解是 {q['answer'] + 1}。") + f" {q['model']}")
        return ok, True
    if q["type"] == "short":
        raw = input("你的答案:").strip().lower()
        ok = any(kw.lower() in raw for kw in q["accept"])
        print(("✅ 答對!" if ok else "❌ 不太對。") + f" 參考:{q['model']}")
        return ok, True
    # reflect
    input("(想好答案後按 Enter 看參考答案)")
    print(f"💡 參考答案:{q['model']}")
    raw = input("你答得差不多嗎?(y/n):").strip().lower()
    return raw.startswith("y"), False


def main():
    if "--check" in sys.argv:
        errs = validate_bank()
        if errs:
            print("題庫格式有問題:")
            for e in errs:
                print("  - " + e)
            return 1
        print(f"✅ 題庫格式正確,共 {len(BANK)} 題,涵蓋第 "
              f"{sorted(set(q['ch'] for q in BANK))} 章。")
        return 0

    if "--chapter" in sys.argv:
        ch = int(sys.argv[sys.argv.index("--chapter") + 1])
        questions = [q for q in BANK if q["ch"] == ch]
        title = f"第 {ch} 章"
    elif "--all" in sys.argv:
        questions = BANK
        title = "全章節"
    else:
        print(__doc__)
        return 0

    if not questions:
        print("這個章節沒有題目。")
        return 0

    print("=" * 56)
    print(f"  知識測驗 · {title}({len(questions)} 題)")
    print("=" * 56)

    auto_total = auto_right = reflect_right = reflect_total = 0
    for q in questions:
        ok, auto = ask(q)
        if auto:
            auto_total += 1
            auto_right += ok
        else:
            reflect_total += 1
            reflect_right += ok

    print("\n" + "=" * 56)
    if auto_total:
        print(f"  自動批改:{auto_right}/{auto_total} 答對")
    if reflect_total:
        print(f"  反思題(自評):{reflect_right}/{reflect_total} 你覺得答得不錯")
    print("=" * 56)
    return 0


if __name__ == "__main__":
    sys.exit(main())
