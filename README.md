# Loop Engineering from Scratch — 教 AI 自己把事情做完、做對、然後停

> 🌐 **線上互動學習(瀏覽器直接跑,零安裝)**:<https://klmtseng.github.io/loop-engineering-course/>
> (目前為第 1 課互動切片;其餘課程陸續上線。)

> Prompt engineering 是「你想好一句話,丟給 agent,看一次結果」。
> **Loop engineering 是「你設計一個系統,讓它自己反覆『做 → 驗 → 決定要不要再來』,
> 直到達標或撞上限才停」。** 一句話:把迴圈裡那個「一直盯著、決定要不要再 prompt 一次的你」,
> 換成一段程式。

這門課用七支單檔 Python 腳本,從一個不到 15 行的 `act→verify→decide` 閉環開始,
一路蓋到一個會「自己醒來、自己巡檢、處理不了才叫你」的無人值守系統,
最後拆穿這個領域最危險的真相:**verify 只是代理指標,而 agent 會鑽它。**

每一課**純標準庫、零 API 金鑰、`python3 lessonN.py` 直接可跑**。
課程用一個「假 agent」當替身,讓你先看清楚迴圈本身;真正的 agent(Claude Code / Codex /
你自己的 LLM 呼叫)怎麼接進來,每一課的延伸練習與下面的「接真 agent」一節都有說明。

> 這是姊妹課 *agent-from-scratch*(教你**蓋一個 agent**,尚未公開發佈)的續集:
> 這門教你**把 agent 變成一個會自己跑的系統**。先學會哪個都行,但建議先有一點 agent 概念。

## 先上課前:你需要會什麼?(30 秒自我檢查)

這門課的**主線是給會寫 Python 的人**。下面三題你心裡有答案,就可以直接上:

1. 你能讀懂並自己寫出一個 `for` / `while` 迴圈、一個 `def` 函式嗎?
2. 你知道「命令的結束碼(exit code)0 代表成功」嗎?(第 2 章用)
3. 你大概知道 `git` 和「排程(cron)」是什麼嗎?(第 5、6 章會用到,不熟也沒關係,見下)

**分級路徑**:主線維持中階,但兩個會「跳一下」的地方都幫你鋪了繞道——

- 第 5 章用到**並行(threading)**:沒寫過多執行緒也能懂,章首有「先備繞道」方框。
- 第 6 章用到**cron 排程**:不熟 cron 的話,章首方框三行講完你需要的部分。
- 完全沒碰過 AI agent?先補「LLM 呼叫、工具呼叫、ReAct 迴圈」三個概念(任何入門教材皆可),再回來。
- **平台**:示範全程在 Linux/Mac 上跑;第 5、6 章的 `git worktree` 與 `cron` 是 Unix 工具,
  Windows 學生請用 WSL,或把那兩課當概念理解(課程的可跑部分仍純標準庫、跨平台)。

> 只想「看懂概念、不寫程式」也行:每章 textbook 開頭都有一句 **TL;DR**,讀那行 + 概念段落即可。
> 但這門課真正的價值在**動手**——驗收層(見下)會逼你把 loop 自己寫出來。

## 課程目錄

| # | 檔案 | 主題 | 動手練習 | 一句話 |
|---|------|------|------|--------|
| 1 | `lesson1_minimal_loop.py` | 最小的閉環 | `exercises/exercise1_*` | loop = act→verify→decide,把人肉判斷換成程式 |
| 2 | `lesson2_exit_conditions.py` | 退出條件與驗證閘門 | `exercises/exercise2_*` | verify 用「跑命令看結束碼」;出口要有 SUCCESS/FUSE/STALL |
| 3 | `lesson3_safety_budget.py` | 安全與成本 | `exercises/exercise3_*` | 保險絲+預算+run-log+L1→L3 分階段,放生前的四道防線 |
| 4 | `lesson4_maker_checker.py` | maker/checker 雙代理 | `exercises/exercise4_*` | 會說「我做完了」的 agent 不是公正的裁判 |
| 5 | `lesson5_parallel_isolation.py` | 平行與隔離 | `exercises/exercise5_*` | 要平行,先隔離;寫程式場景用 `git worktree` |
| 6 | `lesson6_scheduling.py` | 排程與無人值守 | `exercises/exercise6_*` | 接上 cron(狀態外存),腳本變成「趁你睡覺時出貨」的系統 |
| 7 | `lesson7_verifier_gaming.py` | **verify 是代理指標** | `exercises/exercise7_*` | agent 不是在解問題,是在讓 verify 變綠——它會鑽你的 verify |

**Part II — 驅動真實 agent**(假設你已懂 agent 的基本概念:工具呼叫、ReAct、上下文):

| # | 檔案 | 主題 | 動手練習 | 一句話 |
|---|------|------|------|--------|
| 8 | `lesson8_real_agent.py` | 非決定性與真實 agent | `exercises/exercise8_*` | 真 agent 是隨機的、會退步;為「分佈」設計 + best-so-far(`--real` 可接真 LLM) |
| 9 | `lesson9_context_strategy.py` | 跨圈上下文策略 | `exercises/exercise9_*` | 別把記憶塞進對話歷史(會爆),寫成 repo 裡的 durable spec |
| 10 | `lesson10_loop_evals.py` | loop 級 evals | `exercises/exercise10_*` | 單任務綠 ≠ loop 好;對 task suite 量 success/iters/escalation/cost |
| 🎓 | — | **Capstone 總驗收** | `capstone/` | 把十課零件自己組成一個能放生、且對 noisy agent 穩健的維運 loop |

> ⏱ Part I 每課約 **15–25 分鐘**、Part II 每課 **20–30 分鐘**;Capstone 約 **45–60 分鐘**。整門課約一天。

每課都配一章 textbook(概念 + 動手 + 自我檢查 + 延伸練習):
[`ch01`](textbook/ch01_minimal_loop.md) ·
[`ch02`](textbook/ch02_exit_conditions.md) ·
[`ch03`](textbook/ch03_safety_budget.md) ·
[`ch04`](textbook/ch04_maker_checker.md) ·
[`ch05`](textbook/ch05_parallel_isolation.md) ·
[`ch06`](textbook/ch06_scheduling.md) ·
[`ch07`](textbook/ch07_verifier_gaming.md) ·
[`ch08`](textbook/ch08_real_agent.md) ·
[`ch09`](textbook/ch09_context_strategy.md) ·
[`ch10`](textbook/ch10_loop_evals.md) ·
[附錄A:玩具→真實原語對照](textbook/appendix_mcp_mapping.md)

## 環境設置

```bash
# 不用裝任何東西。Python 3.8+ 即可,十課全程只用標準庫。
python3 lesson1_minimal_loop.py

# 想「看著 loop 一圈圈轉」?任何一課加 --animate 就會慢放演示:
python3 lesson1_minimal_loop.py --animate

# (選用)第 8 課可接真 LLM:沒金鑰會自動退回零依賴 stub,不會當掉。
export OPENROUTER_API_KEY=sk-or-...   # 沒有也沒關係
python3 lesson8_real_agent.py --real
```

建議搭配 textbook 一章一章讀:先讀章、自己跟著打一遍、再對照 `lessonN_*.py`。

## 每課的學習動線

```
讀 textbook/chNN  →  跑 lessonNN(可加 --animate 慢放)  →  寫 exercises/exerciseNN
                  →  跑 check_exerciseNN 驗收  →  全綠就過關,進下一課
```
最後做 `capstone/`,再用 `python3 progress.py` 看自己過了幾關。

## 核心觀念速查

一個 loop 永遠是這四件事:

```
goal    明確、機器可判定的目標(不是「弄好一點」,而是「verify 回傳 True」)
act     做一步(呼叫 agent / 跑命令 / 改檔)
verify  驗一下:達標了嗎?         ← loop 的靈魂
decide  沒達標就帶回饋再來;達標或燒完就停
```

放生任何 loop 前的檢查清單(全來自第 3 章):

- [ ] **max-iter 保險絲** — 沒有它,鬼打牆的 agent 會燒掉你的額度
- [ ] **預算** — token / 金額 / 時間設硬上限,先估再跑
- [ ] **run-log** — 每圈一行 JSONL,append-only,出事時的黑盒子
- [ ] **從 L1 開始** — 先 dry-run 看它想幹嘛 → 動手前問人 → 才全自動
- [ ] **獨立 checker** — 別讓 agent 自己驗自己(第 4 章)
- [ ] **隔離** — 要平行就用 worktree,別共用工作目錄(第 5 章)
- [ ] **verify 鑽不動** — agent 會硬編答案/改弱測試騙過弱 verify;用 hold-out + 隨機輸入 + 隔離(第 7 章)
- [ ] **best-so-far 要複驗** — 對有雜訊/可鑽的 verify 取 max 會選到僥倖(optimizer's curse / maximization bias);用 hold-out 複驗選出的最佳(第 8 章)

## 驗收:確認你真的學會了(不是「讀完就算」)

這門課的諷刺之處:它教你「別讓 agent 自評,要跑一個 verify 閘門」——所以它對學生也不搞自評。
三層驗收,每一層都是一個客觀的閘門:

```bash
# 1) 動手練習 + 自動評分器(每課一組,最重要)
#    打開 exercises/exercise1_minimal_loop.py 把 TODO 補完,然後:
python3 exercises/check_exercise1.py        # 全綠才過關;有 ❌ 照回饋改

# 2) 知識測驗(觀念有沒有記住)
python3 quiz/quiz.py --chapter 1            # 或 --all;mcq/簡答自動批,反思題給參考答案

# 3) Capstone 總驗收(能不能自己組一個出來)
#    照 capstone/SPEC.md 寫 capstone/my_loop.py,然後:
python3 capstone/grade_capstone.py

# 看整體進度(這支程式本身就是對你的學習跑一個 verify loop)
python3 progress.py
```

`exercises/solutions/` 有參考解答,**卡死再看,看完務必自己重打一遍**。

## 接真 agent(把替身換成真的)

課程的 `mock_agent` 是替身,讓你專心看迴圈。換成真的只動一個函式:

- **換成 LLM 呼叫**:把 `mock_agent(...)` 換成一次 chat API 呼叫,
  把 verify / checker 的回饋當成 user 訊息接在對話後面。
  (做過 `agent-from-scratch` 的話,直接借用那邊的 `llm()`。)
- **換成 Claude Code / Codex CLI**:用 `subprocess` 呼叫 agent 的 CLI,
  把任務當 prompt 傳入、把它的輸出當這一圈的產物。verify 一樣跑你的檢查命令。
- **verify 換成真檢查**:把第 2 章的 `check_cmd` 換成你專案的 `pytest` / `ruff` / `npm run build`。

骨架完全不用改 —— 這正是這門課的重點:**loop 的價值在骨架,不在 agent 是誰。**

## 設計原則

1. **一課一檔一觀念** — 每課可獨立執行,註解即講稿
2. **零依賴、零金鑰** — 全程標準庫,把「替身 agent」講清楚,再教你換真的
3. **誠實** — mock 是 mock、模擬是模擬,該用 `git worktree` 的地方絕不假裝
4. **骨架優先** — 先讓你把 act→verify→decide 內化成肌肉記憶,模式(PR-until-green 等)只是它的變奏

## 參考來源

- 推文(本課的緣起):彙整數十位開發者 loop engineering 思路的網站 <https://loops.elorm.xyz/>
- `cobusgreyling/loop-engineering`(loop-init / loop-audit / loop-cost 等 CLI 工具)
  <https://github.com/cobusgreyling/loop-engineering>
- GitHub 主題頁 <https://github.com/topics/loop-engineering>
