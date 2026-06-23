# 第 5 章 —— 平行與隔離

> **本章目標**:學會讓多個 loop 同時跑,並理解平行的前提是隔離。認識寫程式場景的
> 標準隔離手段 `git worktree`。做完後你會記住:**隔離不是效能優化,是正確性的前提。**
>
> 參考解答:[`lesson5_parallel_isolation.py`](../lesson5_parallel_isolation.py)

**TL;DR**:要平行跑多個 loop,前提是**隔離**;寫程式場景用 `git worktree` 給每個 loop
一個獨立 checkout,跑完再挑最好的 merge。

> **🧭 先備繞道(沒寫過多執行緒也沒關係)**
> 本章程式用 `ThreadPoolExecutor` 同時跑好幾個 worker——你只要把它想成
> 「同時開 3 個分身各做各的」。你**不需要**懂執行緒的細節,本章的重點不是並行技術,
> 而是「**並行之前要先隔離**」這個觀念。程式碼照抄就能跑,專心看「隔離 vs 互踩」的對照即可。

## 5.1 概念:平行的誘惑與陷阱

一個 loop 跑得動之後,下一個念頭幾乎必然是:「能不能同時跑好幾個?」

- 同時讓三個 agent 各修一個 bug。
- 同時試三種重構方案,跑完挑最好的。
- 同時對十個 repo 各跑一次依賴升級。

可以。但有個陷阱:**如果它們共用同一份工作目錄,它們會互相踩。**
多個 worker 同時寫同一個檔,行與行**交錯**纏在一起、分不出哪行是誰寫的、順序也不可信
(provenance/順序遺失)—— 最後產出一份「誰都不能為它負責」的成品。

> **精確一點(連機制也講對)**:本課 demo 是小筆 `append`,你看到的是**行交錯**(出處/順序遺失),
> 不是「位元級損毀」,也沒有真的「整檔被覆蓋」。而且每行之所以完整,**不是因為 GIL**——
> GIL 只序列化 Python bytecode,**不保證 OS 層的寫入原子性**。真正的原因是:每行是一次小的、
> 關檔即 flush 的 `write()` syscall,加上 `O_APPEND` 把「定位到檔尾 + 寫入」這步原子化。
> **注意這對一般檔案在 POSIX 並非嚴格保證、也不可移植**(更大的非原子寫入仍會位元級交錯)。
> 所以正解永遠是隔離,不是賭寫入原子性。對「平行 agent 的成品」而言,出處與順序遺失就已經夠致命。

## 5.2 概念:git worktree —— 同一個 repo,多個獨立工作目錄

寫程式場景的標準隔離手段是 `git worktree`。它讓同一個 repo 長出多個獨立的 checkout,
**共享 git 物件庫、但檔案完全分開**:

```bash
git worktree add ../wt-fix-a -b fix-a     # 長出一個獨立工作目錄,在新分支 fix-a
git worktree add ../wt-fix-b -b fix-b     # 再一個,在 fix-b
git worktree add ../wt-fix-c -b fix-c

# 三個 agent 各自在自己的 worktree 裡跑 loop —— 檔案互不干擾、commit 各自分支
# 跑完後比較三個分支,挑最好的 merge 回主線

git worktree remove ../wt-fix-a           # 收工後清掉
```

比起 `git clone` 三份,worktree 共享物件庫、省空間又快;比起共用一個目錄,
它給每個 loop 一個乾淨、獨立、可丟棄的沙盒。這正是 Claude Code 等工具
做「平行 agent」時底層在用的機制。

## 5.3 動手做

`lesson5_parallel_isolation.py` 用「各自一個暫存目錄」模擬 worktree 的隔離效果
(純標準庫好示範),並故意對比兩種情境:

```bash
python3 lesson5_parallel_isolation.py
```

**檢查點一(隔離)**:情境一給每個 worker 一個自己的目錄。
看輸出 —— 每個 worker 的私有檔乾乾淨淨,只有它自己的字句,沒被別人污染。
關鍵就是那一行 `wt = os.path.join(base, f"wt-{w}")`:每人一個目錄。

**檢查點二(災難)**:情境二讓三個 worker 共用同一個 `result.txt`。
看輸出 —— 三個 worker 的字句交錯纏在一起,九行裡混了三個作者。
這份檔已經沒有任何一個 agent 能為它負責了。**這就是沒有隔離的平行。**

> **注意**:這課用 thread + 暫存目錄「模擬」隔離,目的是讓你在零依賴下看清楚現象。
> 真實專案請用 `git worktree`,它還順帶給你分支管理和乾淨的 merge 路徑。

## 5.4 卡關排查

| 症狀 | 原因 | 解法 |
|---|---|---|
| 平行跑完成品互相污染 | 多個 loop 共用工作目錄/檔案 | 每個 loop 一個 worktree 或獨立目錄 |
| worktree 建不出來 | 路徑已存在 / 分支名重複 | 換路徑、換分支名,或先 `git worktree remove` |
| 平行沒有變快 | 工作是 CPU-bound 又用了 thread | 改用多進程,或意識到瓶頸在 LLM API 而非本機 |
| 跑完一堆 worktree 沒清 | 忘了 remove | 收尾一律 `git worktree remove`,或 `git worktree prune` |

## 5.5 自我檢查

1. 平行跑多個 loop 最大的風險是什麼?
2. `git worktree` 和 `git clone` 三份、以及共用一個目錄,各有什麼差別?
3. 為什麼說「隔離不是效能優化,是正確性的前提」?
4. demo 情境二裡,那份共用檔為什麼「誰都不能為它負責」?
5. 平行 N 個 loop 跑完後,通常下一步要做什麼?(提示:分支)

## 5.6 延伸練習

- **真 worktree**:在一個真的 git repo 裡,手動跑一遍 `git worktree add` 三個分支、
  各改一個檔、`git worktree list` 看狀態、再 remove。體會它和 clone 的差別。
- **挑最好的**:把 demo 改成每個 worker 回傳一個「分數」,跑完後自動選分數最高的那份結果
  (這就是「平行試多方案、擇優」的骨架)。
- **加隔離斷言**:在 worker 開頭斷言它的 workdir 是空的、且不等於別人的 workdir,
  讓「沒隔離」這個 bug 在第一時間就爆出來,而不是等成品污染才發現。

## 5.7 動手驗收

打開 [`exercises/exercise5_parallel_isolation.py`](../exercises/exercise5_parallel_isolation.py),
實作 `run_isolated()`(每個 worker 一個專屬目錄),跑 `python3 exercises/check_exercise5.py` 驗收。

## 5.8 自我檢查解答

1. 多個 loop 共用工作目錄 → 行交錯、出處與順序遺失(provenance loss),產出沒人能負責。
2. worktree:同 repo 多個獨立 checkout,共享物件庫、檔案分開、省空間又快;clone 三份較慢佔空間;共用目錄會互踩。
3. 沒隔離時平行產出會互相污染、結果不可信;隔離保的是正確性,不是速度。
4. 因為九行裡混了三個作者、字句交錯纏在一起,分不出哪行是誰,沒有任何 agent 能為它負責。
5. 比較各分支、挑最好的那個 merge 回主線(平行試多方案、擇優)。

---

✅ 過關條件:你能說出平行的風險、解釋 worktree 的隔離原理,並在 demo 裡指出「污染」如何發生。
最後一章,我們把前五課的零件組裝起來,接上排程器,讓 loop 自己醒來。
→ [第 6 章:排程與無人值守 (Capstone)](ch06_scheduling.md)
