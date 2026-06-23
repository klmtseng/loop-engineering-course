# Capstone —— 總驗收:自己組一個能放生的維運 loop

前六課每課只練一個零件。這個 capstone 沒有鷹架——**你要把零件自己組起來**,
做出一個「夜間維運 loop」:它撈一個待辦佇列,逐件處理、獨立驗收、記帳記錄,
預算用罄就 escalate,而且能被 cron 用 `--once` 呼叫。

## 怎麼做

```bash
cp my_loop_template.py my_loop.py     # 複製範本,在 my_loop.py 裡實作
nano my_loop.py
python3 grade_capstone.py             # 驗收(預設驗 my_loop.py)
```

## 你的 my_loop.py 必須具備的六項要件

評分器靠下列「介面」做行為測試,所以請照簽名實作(內部怎麼寫隨你):

| # | 要件 | 介面 | 通過條件 |
|---|---|---|---|
| 1 | **保險絲 + 預算** | `Budget(max_iters, max_tokens)`,有 `.can_continue()`、`.charge(tokens)` | 圈數或 token 任一到頂就不能繼續 |
| 2 | **run-log** | `log_event(logfile, **fields)` | 每次 append 一行 JSONL,**不覆蓋** |
| 3 | **獨立 checker** | `checker(task, result) -> bool` | 好結果 True、壞結果 False |
| 4 | **主迴圈(整合要件 7)** | `run(world, logfile, budget, level)` | 逐件處理:**每個任務用 `solve_task(task_agent(task), …)` 跑**(別繞過 best-so-far),SUCCESS→done、FAIL→escalate;預算用罄要 escalate;回傳含 `done`/`escalated`/`budget_exhausted` 的 dict |
| 5 | **L1 安全** | `run(..., level="L1")` | L1 時不真的執行副作用(world 的 `executed` 計數維持 0) |
| 6 | **可隔離 + 可排程** | `worker_dir(base, name)` 給每 worker 不同路徑;`python3 my_loop.py --once` 跑一拍後 exit 0 | 路徑互異且在 base 下;`--once` 正常退出 |
| 7 | **對 noisy agent 穩健** | `solve_task(agent, max_iters)` —— 用 best-so-far 迭代一個會退步的 agent | 中途達標即記住;回傳歷史最佳而非末圈;從未達標回 FAIL+最佳 |

## 提示

- 要件 1/2 直接搬第 3 課;要件 3 搬第 4 課;要件 4/5 是第 3、6 課的合體;
  要件 6 的隔離搬第 5 課、排程搬第 6 課;**要件 7 搬第 8 課的 best-so-far**。
- 要件 7 的 `solve_task(agent, max_iters)`:`agent(attempt)` 回一個覆蓋率(int),達標線 = `GOAL`(90);
  每圈記住歷史最佳,best ≥ GOAL 就回 `("SUCCESS", best)`,燒完回 `("FAIL", best)`。
  這是真正需要你**設計判斷**的一題:真 agent 會退步,只信末圈會把好結果丟掉。
- `world` 物件由評分器提供,長這樣:有 `todos`(list)、`done`(list)、`escalated`(list)、
  `executed`(int 計數器,你每真的執行一次副作用就 +1)。範本裡有給一個可用的 `World`。
- 卡死了看 `solution_my_loop.py`(看完自己重打一遍)。
