# 附錄 A —— 玩具概念 → 真實原語對照

這門課為了零依賴、看得清楚,把每個概念都用標準庫的小模型實作。但你在真實工具
(Claude Code、Codex、GitHub Actions、MCP 生態)裡做 loop engineering 時,這些概念
各自對應到一個現成的「原語(primitive)」。這張表幫你把學到的東西接到真實世界。

| 課程裡的玩具 | 對應的真實原語 | 說明 |
|---|---|---|
| `mock_agent` / `noisy_agent`(第 1、8 課) | **一次 agent CLI 執行 / LLM API 呼叫** | Claude Code / Codex 跑一輪 = 你 loop 的一個 `act`。內層 ReAct 它自己跑(見第 1 章內外層)。 |
| `verify` / `run_check`(第 2 課) | **測試 / linter / CI / build 的 exit code** | `pytest`、`ruff`、`npm run build`、健康檢查端點。能用確定性的就別用 LLM judge(第 4 章)。 |
| 四道防線(第 3 課) | **預算上限 / 結構化日誌 / 權限分級** | 真實的 `loop-cost`(估花費)、`loop-audit`(評健康度)就在自動化這些。 |
| maker / checker(第 4 課) | **sub-agents(子代理)** | 一個 agent 做、另一個帶不同 system prompt 獨立驗。Claude Code 的 subagent、多 agent 編排。 |
| `git worktree` 隔離(第 5 課) | **git worktree / 容器 / 沙盒** | 平行多個 loop 各自獨立 checkout;也防 agent 改到不該改的(injection 緩解)。 |
| `--once` + cron(第 6 課) | **cron / systemd timer / GitHub Actions / 排程雲端 agent** | 排程那層由它們取代;你的 loop 只要支援「跑一拍就退出」。 |
| 狀態外存 JSON(第 6 課) | **DB / issue 佇列 / 訊息佇列 / repo 檔案** | 進程外的持久狀態,讓排程 loop 能接續、去重、抗當機。 |
| durable spec(第 9 課) | **repo 裡的 `PLAN.md` / 測試 / issue;skills** | 把跨圈記憶寫進 repo,而不是塞進對話歷史。Claude Code 的 skills 也是一種持久知識。 |
| 連接外部系統(課程沒做) | **MCP(Model Context Protocol)connectors** | 讓 agent 安全地接 DB / API / 雲服務的標準協定;真實 loop 靠它取得 context、執行動作。 |
| loop 級 evals(第 10 課) | **eval harness / loop-audit / 觀測儀表板** | 對 task suite 量 success/iters/escalation/cost,A/B 設定後決定上線。 |

## 一句話

這門課教的是**外層編排迴圈的骨架與紀律**;真實世界只是把每個零件換成更強的原語
(agent CLI、MCP、worktree、Actions、eval harness)。**骨架不變——這正是為什麼先學骨架最值錢。**

→ 回到 [README](../README.md)
