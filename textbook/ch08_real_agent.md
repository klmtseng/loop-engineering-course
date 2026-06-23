# 第 8 章 —— 非決定性與真實 agent

> **本章目標**:認清前七課的乖寶寶 stub 和真實 LLM agent 的根本差異——**真 agent 是隨機的**——
> 並學會為「分佈」而非「定值」設計 loop:best-so-far、重試退避、冪等,以及看一次 loop 包住真 LLM。
> 做完後你會記住:**你的 loop 要為 agent 會亂跳、會退步、會失敗而設計。**
>
> 參考解答:[`lesson8_real_agent.py`](../lesson8_real_agent.py)

**TL;DR**:同一個 prompt 跑兩次結果不同。loop 的輸出是一個分佈,不是一個定值——
所以要記住歷史最佳(best-so-far)、重試要退避、動作要冪等。

## 8.1 概念:stub 是乖寶寶,真 agent 不是

前七課的 mock agent 每圈穩定進步、固定圈數收斂——那是為了讓你看清骨架。但真實的 LLM:

- **非決定性**:同一個 prompt、同一份 context,跑兩次可能給不同答案。
- **會退步**:第 2 圈把覆蓋率衝到 95,第 5 圈一改又掉回 60。進步不是單調的。
- **會失敗**:context 爆窗、rate limit、工具呼叫炸掉、輸出格式跑掉。

> **非決定性不只來自取樣**——這點很多人搞錯。就算你把 `temperature=0`(greedy、完全不取樣),
> 真實推論服務**仍然**可能每次給不同結果:伺服器會把多個請求一起 batch,**batch 大小會改變浮點運算的累加順序**
> (batch-invariance 問題,Thinking Machines Lab 2025 才系統性釐清並修復)。
> **結論:你不能靠把 temperature 設 0 來假設 agent 變確定性**,還是得為「分佈」而非「定值」設計。

`lesson8_real_agent.py` 用一個隨機漫步的 `noisy_agent` 把這件事演出來:同一個 loop 換 5 個 seed,
有的第 1 圈就過、有的第 5 圈才過、有的根本沒過。**這就是真 agent——結果是一個分佈。**

## 8.2 你可能還沒發現的 bug:「只看最後一圈」

一個很常見、而且前面幾課的寫法就藏著的問題:**讓 agent 跑完 N 圈,只判定最後一圈的成品。**

如果 agent 第 2 圈衝到 95(達標!)、第 6 圈退步到 75,這種 loop 會回報「失敗」——
**它把中途那個完美的結果丟了。** 對單調進步的 stub 不會出事,對會退步的真 agent 一定出事。

對策是 **best-so-far**:跨圈記住歷史最佳,末圈退步也不影響。

```python
best = None
for i in range(1, MAX_ITERS + 1):
    cov = agent(i - 1, feedback=...)
    if best is None or cov > best:
        best = cov                 # 記住最好的
    if verify(best):
        return ("SUCCESS", i, best)
return ("FAIL", MAX_ITERS, best)   # 連 FAIL 都回最佳,不回末圈
```

> 在改檔案的場景,「記住最佳」=每圈用 git commit / worktree 快照,失敗就 `reset` 回最佳那一版。
> 這也是第 5 課隔離的另一個用途:**可回滾**。

### ⚠️ 但 best-so-far 有個陷阱:它會放大第 7 章的 Goodhart

best-so-far 的本質是「**取多圈裡 verify 讀數的最大值**」。如果 verify 是個**有雜訊、或可被鑽的代理指標**
(第 7 章),那「取 max」這個動作會**系統性地選到僥倖**——這叫 **optimizer's curse / maximization bias(最大化偏誤)**
(RL 裡 Double Q-learning 解的就是這個高估;拍賣的 *winner's curse* 是同一現象的直覺類比):
你挑中的那一次,往往不是真的最好,而是**雜訊最高 / 最被鑽高**的那一次。

`lesson8` 的 demo 演了這件事:best-so-far 依 proxy 選了一個讀數 97 的版本,但它真值只有 82;
真正最好的(真值 86)因為 proxy 只有 90 反而沒被選上。

> **這是第 7 章和第 8 章的交會點**:best-so-far(對抗退步)和 verify-gaming(對抗作弊)單獨看都對,
> 合在一起卻有張力——**對一個弱 verify 做 best-so-far,等於主動去挑最幸運的假高分**。
> **對策**:對你選出的「最佳」再用 **hold-out 複驗一次**(第 7 章),proxy 高 ≠ 真的好。
> verify 越可靠,best-so-far 才越值得信。

## 8.3 為「分佈」設計:重試、退避、冪等

既然 agent 會隨機失敗,你的 loop 要有韌性:

| 問題 | 對策 |
|---|---|
| 偶發失敗(rate limit、5xx、格式跑掉) | **重試**,而且要 **指數退避 + 抖動(jitter)**,別一秒打十次 |
| 重試/重跑造成重複副作用 | **冪等**:同一個動作做兩次,效果跟做一次一樣(第 6 章) |
| 鬼打牆無限重試 | 重試也要有上限——它是另一個保險絲 |
| 同一份成品驗兩次結果不同(flaky verify) | verify 本身要穩定、可重跑,否則你連「過了沒」都不能信 |

## 8.4 真 agent 失敗圖鑑

stub 不會演,但你一上線就會遇到。`lesson8` 結尾印的這份,值得貼在牆上:

- **context 爆窗**:對話越滾越長 → 超過模型上限 → 用第 9 章的上下文策略
- **rate limit / 5xx**:太頻繁或伺服器掛 → 重試 + 指數退避 + 抖動
- **寫檔寫一半**:動作做到一半進程被砍 → 冪等 + check-then-act(第 6 章)
- **flaky verify**:同一份成品驗兩次不同 → 驗證要穩定、可重跑
- **無限 tool-call**:agent 鬼打牆狂呼叫 → max-iter 保險絲(第 1 章)就是為這個

## 8.5 動手做:看 loop 包住真 LLM(選用)

```bash
python3 lesson8_real_agent.py            # 預設:零金鑰,跑 noisy stub
python3 lesson8_real_agent.py --real     # 選用:接真 LLM(需 OPENROUTER_API_KEY)
```

**檢查點**:`--real` 在**沒有金鑰時會友善退回 stub、印出真實路徑長怎樣,而不是當掉**——
這本身就是第 8 章的精神:為失敗設計。有金鑰時,你會看到真實回應 + `usage` 的 token 數,
那個數字接到第 3 章的 `Budget.charge()`,預算就從「估算」變「實測」。

> **真實路徑的骨架**(完整見姊妹課 agent-from-scratch 第 1 課):
> `requests.post(...)` → `r.json()["choices"][0]["message"]["content"]` 取回覆、
> `r.json()["usage"]["total_tokens"]` 取成本。loop 的骨架完全不變,只是 `agent()` 從 stub 換成這次呼叫。

## 8.6 自我檢查

1. 「真 agent 是隨機的」具體指什麼?為什麼說 loop 的輸出是一個分佈?
2. 「只看最後一圈」的 bug 在 stub 上為什麼不會出事、在真 agent 上一定出事?
3. best-so-far 怎麼救回這個 bug?在改檔案的場景它對應到什麼?(提示:git)
4. 為什麼重試要「指數退避 + 抖動」而不是固定間隔狂重試?
5. 失敗圖鑑裡挑兩個,說出它的對策對應到前面哪一章。

## 8.7 動手驗收

打開 [`exercises/exercise8_best_so_far.py`](../exercises/exercise8_best_so_far.py),
實作 `best_so_far_loop()`,讓它在 agent 退步時仍回傳歷史最佳。
跑 `python3 exercises/check_exercise8.py` 驗收。

## 8.8 自我檢查解答

1. 同一個 prompt、同一份 context,取樣隨機 → 每次輸出可能不同;多跑就會看到成功圈數/成敗的分佈。
2. stub 單調進步,末圈一定是最好的;真 agent 會退步,末圈可能比中途差,只看末圈就丟了中途的好結果。
3. 跨圈記住歷史最佳、達標就收;改檔場景=每圈 commit/快照,失敗 reset 回最佳那版(第 5 章隔離=可回滾)。
4. 固定間隔狂重試會在伺服器忙時雪上加霜、且多個 client 同步重試會撞在一起;退避+抖動把重試錯開、給系統喘息。
5. 例:context 爆窗→第 9 章上下文策略;寫檔寫一半→第 6 章冪等;無限 tool-call→第 1 章 max-iter。

---

✅ 過關條件:你能說出真 agent 的非決定性、實作 best-so-far、並說明重試退避與冪等為何必要。
→ [第 9 章:跨圈上下文策略](ch09_context_strategy.md)
