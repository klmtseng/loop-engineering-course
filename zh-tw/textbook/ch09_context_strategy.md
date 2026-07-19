# 第 9 章 —— 跨圈上下文策略

> **本章目標**:搞懂真實 loop engineering 最核心的設計決策——**每一圈要餵 agent 什麼 context?**
> 比較 stateless / full-conversation / spec-in-repo 三種策略的取捨,並學會生產預設:
> 乾淨 context + repo 裡一份精簡 spec。做完後你會記住:**別把記憶塞進對話歷史,塞進 repo。**
>
> 參考解答:[`lesson9_context_strategy.py`](../lesson9_context_strategy.py)

**TL;DR**:對話歷史會無上限長大、爆成本又 drift;把跨圈記憶寫成 repo 裡一份精簡 spec,
每圈用乾淨 context + 這份 spec 重新派工——這就是 durable spec,coding agent 的預設。

## 9.1 概念:被前面幾課藏起來的決策

前面的 mock agent 只收一個 `feedback` 字串。但真案子裡,每圈你都得決定餵 agent 什麼:

| 策略 | 每圈的 context | 優點 | 致命傷 |
|---|---|---|---|
| **stateless(乾話回饋)** | 任務 + 最新一條乾話回饋 | context 最省、最便宜 | **回饋承載不了記憶時**會重複犯錯、猜不到 |
| **full conversation** | 累積整段對話歷史 | agent 記得全部 | context 每圈長大 → 成本線性爆炸、終將撞 context window、越長越 drift |
| **spec-in-repo** | 乾淨 context + 一份精簡 spec | 有記憶 **且** context 有界 | 你得自己維護那份 spec |

## 9.2 用數字看差距

`lesson9_context_strategy.py` 讓四種策略猜同一個密碼(13),量 context 成本:

```
策略                    結果      圈數   峰值context   累計context
stateless(乾話回饋)     FAIL      20    30           600    ← 回饋太薄,承載不了記憶 → 猜不到
full conversation       SUCCESS   13    174          1326   ← 猜得到,但 context 爆炸
spec-in-repo            SUCCESS   13    38           494    ← 猜得到,context 還恆定有界
stateless(帶比較訊號)  SUCCESS   4     34           136    ← ★ 一樣沒記憶,但回饋夠 → 二分搜尋,最便宜
```

**重點(也是一個容易犯的過度概化)**:第一行的失敗,**兇手不是「stateless」本身,是「回饋太薄」**。
看最後一行——同樣 stateless、同樣不記憶,只要把回饋從一句乾話換成「太高/太低」累積出的範圍,
它二分搜尋 4 圈就猜到,而且 context 比誰都省。**精確的命題是:stateless 在「單條回饋無法承載所需記憶」時才失敗。**

那為什麼還推 spec-in-repo?因為很多真實任務的「所需記憶」沒辦法壓進一條比較訊號(例如「已經改過哪些檔、
為什麼這樣設計」),這時把記憶寫進 repo 的 spec 最實際。conversation 雖然也記得住,但 context 無上限長大、會撞牆。

## 9.3 概念:durable spec —— 把記憶放進 repo,不是對話

關鍵心法:

> **別把跨圈記憶塞進對話歷史(它無上限長大)。把它寫進 repo 裡一份精簡的 spec/scratchpad,
> 每圈用乾淨 context + 這份 spec 重新派工。**

這就是真實 loop-engineering 框架講的 **durable spec**。它同時解決三個問題:
- **成本**:context 恆定,不隨圈數爆炸。
- **drift**:每圈乾淨開始,不會被幾十輪的雜訊帶偏。
- **抗當機**:spec 在 repo 裡,進程死了重啟也還在(呼應第 6 章的狀態外存)。

在 coding agent 的世界,這份 spec 常常就是:repo 裡的一個 `PLAN.md` / `TODO.md` / 測試檔 /
issue 描述——agent 每圈讀它、更新它,而不是靠記住三十輪前說過的話。

## 9.4 動手做

```bash
python3 lesson9_context_strategy.py
```

**檢查點**:比較 `peak context` 那一欄。conversation 的峰值是 spec-in-repo 的好幾倍,而且
**會隨任務變長而無上限成長**——想像一個要 100 圈的任務,conversation 早就撞爆 context window 了。
spec-in-repo 不管幾圈,context 都那麼大。

## 9.5 自我檢查

1. 三種上下文策略各是什麼?各自的優點與致命傷?
2. 為什麼 full conversation「終將撞 context window」?它除了貴還有什麼問題?
3. 什麼是 durable spec?它同時解決了哪三個問題?
4. 在 coding agent 的場景,那份 spec 實際上常常是 repo 裡的什麼東西?
5. spec-in-repo 和第 6 章的「狀態外存」有什麼關聯?
6. 「stateless 就一定失敗」這句話哪裡不精確?用 demo 最後一行反駁它。

## 9.6 動手驗收

打開 [`exercises/exercise9_context_strategy.py`](../exercises/exercise9_context_strategy.py),
實作 `strat_spec_in_repo()`(有界 context + 用 tried 去重)。
跑 `python3 exercises/check_exercise9.py` 驗收。

## 9.7 自我檢查解答

1. stateless(任務+最新回饋:省,但回饋太薄時無記憶)/ conversation(累積對話:有記憶但 context 爆炸、drift)/
   spec-in-repo(乾淨 context+精簡 spec:有記憶又有界,但要自己維護 spec)。
2. 對話每圈長大,遲早超過模型的 context window;且越長越容易 drift——**為什麼**:長 context 下注意力被稀釋、
   早期的雜訊/錯誤一直被帶進來當前提,模型容易被它錨定而離題。成本也線性上升。
6. 不精確在於把「失敗」歸給 statelessness;真正原因是「回饋承載不了所需記憶」。demo 最後一行:同樣 stateless,
   只要回饋帶「太高/太低」的範圍,二分搜尋 4 圈就成功、context 還最省——可見兇手是回饋不足,不是無狀態。
3. durable spec = 把跨圈記憶寫進 repo 的精簡 spec;同時解決成本(context 有界)、drift(每圈乾淨)、抗當機(狀態在 repo)。
4. 常常是 `PLAN.md` / `TODO.md` / 測試檔 / issue 描述——agent 每圈讀它、更新它。
5. 兩者都把「狀態」放進進程之外的持久檔案;spec-in-repo 是把『記憶』也這樣處理,進程死了重啟仍在。

---

✅ 過關條件:你能說出三種上下文策略的取捨、解釋 durable spec,並實作出有界 context 的 spec-in-repo。
→ [第 10 章:loop 級 evals](ch10_loop_evals.md)
