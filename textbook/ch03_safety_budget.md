# 第 3 章 —— 安全與成本

> **本章目標**:認識把「玩具 loop」變成「能放生的 loop」的四道防線:保險絲、預算、
> run-log、分階段上線 (L1→L3)。做完後你會建立一個觀念:**loop engineering 真正難的
> 不是讓它跑,而是讓它安全地跑、花得起地跑。**
>
> 參考解答:[`lesson3_safety_budget.py`](../lesson3_safety_budget.py)

**TL;DR**:放生 loop 前的四道防線——max-iter 保險絲、預算、append-only 的 run-log、
以及從 L1(dry-run)分階段上線到 L3(全自動)。

## 3.1 概念:一個會自己跑的系統,也會自己出事

把前兩課的能力說白一點:

- 一個會「自己反覆呼叫 agent」的系統 = 一個會**自己反覆花錢**的系統。
- 一個會「自己改檔 / 自己推 commit」的系統 = 一個能在你睡覺時**自己把事情搞砸**的系統。

所以放生任何 loop 之前,先確認下面四道防線都到位。它們是地板,不是進階選項。

## 3.2 四道防線

### 防線 1:max-iter 保險絲

第 1、2 章已經有了,這裡只強調:**沒有它,一切免談。** 一個鬼打牆的 agent
可以在一夜之間燒光你的額度。保險絲是 loop 的安全帶。

### 防線 2:預算 (budget) —— 先估、邊跑邊扣、扣光就停

圈數只是其一。真實成本要用 **token / 金額 / wall-clock 時間** 設硬上限:

```python
class Budget:
    def can_continue(self):
        return self.used_iters < self.max_iters and self.used_tokens < self.max_tokens
    def charge(self, tokens):
        self.used_iters += 1
        self.used_tokens += tokens
```

精神是「先估再跑」:在啟動前就用「頻率 × 每圈 token × 單價」估出這個 loop 一天/一月
大概花多少,別等帳單來才知道。社群工具如 `loop-cost` 做的就是這件事。

> **本課的 token 是捏造的數字,真實世界怎麼拿?** 每次 LLM API 回應裡都有一個 `usage` 欄位
> (`prompt_tokens` / `completion_tokens`),把每一圈的 `usage` 累加,就是這個 loop 的**真實**花費——
> 不用猜。姊妹課 [agent-from-scratch 第 1 課](../../agent-from-scratch/textbook/ch01_minimal_llm.md)
> 就示範了從回應裡讀 `usage`。把那個數字接到這裡的 `Budget.charge()`,預算就從「估算」變「實測」。
>
> 補充:有些聚合服務(如 OpenRouter)的 `usage` 還**直接回傳 `cost`(實際扣款金額)**,
> 連「token × 單價」都不用自己算——直接把 `cost` 累加進 `Budget` 就是實測花費。

### 防線 3:run-log —— 沒有日誌的自動化 = 沒發生過

每一圈寫一行 JSONL,append-only,**永不覆蓋**。出事時這是你唯一的黑盒子:

```python
def log_event(logfile, **fields):
    fields["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(logfile, "a") as f:                       # "a" = append,絕不覆蓋
        f.write(json.dumps(fields, ensure_ascii=False) + "\n")
```

一個無人值守的 loop 如果沒有 run-log,等於你把車鑰匙交給它、卻不裝行車記錄器。

### 防線 4:分階段上線 L1 → L2 → L3

**最重要、也最常被跳過的一條。** 不要一上來就讓 loop 全自動改你的東西。分三階段:

| 等級 | 行為 | 你在驗證什麼 |
|---|---|---|
| **L1 report** | 只觀察、只報告,**絕不動手** (dry-run) | 它「想做什麼」對不對? |
| **L2 assisted** | 會動手,但每個有副作用的動作前先停下來問人 | 它「做的方式」對不對? |
| **L3 unattended** | 全自動,只在出錯或預算用罄時 escalate 叫人 | 確認前兩階段都穩了才放生 |

這背後是一個 agent 安全的通用骨架:**propose / commit 分離**。
agent 永遠只「提議」一個動作,「要不要真的執行」由 loop 依自治等級決定:

```python
if level is Level.L1_REPORT:
    log_event(..., proposed=action, executed=False)   # 只記錄,不執行
else:
    result = execute(action, workdir)                 # L2/L3 才真的動手
    log_event(..., proposed=action, executed=True, result=result)
```

### 那「何時可以從 L1 升到 L2、再到 L3」?

別憑感覺,用證據。一個務實的晉級門檻:

- **L1 → L2**:連續看 N 次(例如一週、或 50 次)dry-run 的 run-log,agent「想做的動作」**100% 都是你會核准的**,
  沒有一次離譜。代表它的判斷可信了,可以讓它動手(但仍每步問人)。
- **L2 → L3**:在 L2 階段,你按下的核准幾乎都是「同意」、幾乎沒攔下過任何一步;
  且已有保險絲 + 預算 + run-log + 可回滾。代表人這道關卡已經沒在過濾東西,可以拿掉。
- **任何時候出現一次「還好我有看」的攔截 → 退回上一級**,別硬撐。

晉級是單向信任的累積,不是時間到了就自動發生。

## 3.3 動手做

`lesson3_safety_budget.py` 把同一個 loop 分別用 L1 和 L3 跑一次:

```bash
python3 lesson3_safety_budget.py
```

**檢查點一**:看 L1 那段 —— agent「想寫檔」,但因為是 L1,只記錄不執行。
你先用零風險的方式,看清楚它打算幹嘛。確認沒問題了,才在 L3 真的讓它寫。

**檢查點二**:最後一段故意把預算設成 `max_iters=1`。agent 還沒做完就被掐斷,
loop 回傳的是 **ESCALATED 而不是 SUCCESS** —— 「被預算斷掉」是要叫人的事件,
不能假裝成功。看 run.jsonl 最後一行 `ESCALATE_budget_exhausted`。

**檢查點三**:讀 run.jsonl。每一圈做了什麼、花了多少、有沒有真的執行,全在裡面。
這就是你放生之後唯一能依靠的證據。

## 3.4 自我檢查

1. 為什麼說「會自己跑的系統也會自己出事」?舉兩種它能造成的傷害。
2. 預算除了圈數,還該包含哪些維度?「先估再跑」是什麼意思?
3. run-log 為什麼一定要 append-only、不能覆蓋?
4. L1 / L2 / L3 各在驗證什麼?為什麼不該一上來就 L3?
5. 「propose / commit 分離」是什麼?它如何讓 L1 變得零風險?
6. 「預算用罄」為什麼要回傳 escalate 而不是 success?

## 3.5 延伸練習

- **加金額上限**:給 Budget 加一個 `max_usd`,用 `used_tokens × 單價` 算,超過就停。
- **加 kill-switch**:讓 loop 每圈開頭檢查某個檔案(如 `STOP`)是否存在,存在就立刻
  乾淨退出。這是無人值守系統的緊急煞車。
- **實作 L2**:把 L2 的「假設人核准」改成真的 `input("執行?(y/n) ")`,體會
  人在迴圈裡 (human-in-the-loop) 的感覺,以及它為什麼無法用於無人值守。

## 3.6 動手驗收

打開 [`exercises/exercise3_safety_budget.py`](../exercises/exercise3_safety_budget.py),
補完 `Budget` 與 `should_execute()`,跑 `python3 exercises/check_exercise3.py` 驗收。

## 3.7 自我檢查解答

1. 它會自己花錢、自己改檔;兩種傷害:燒爆 API 帳單、在你沒看著時把檔案/commit 搞砸。
2. 還要含 token / 金額 / wall-clock 時間;「先估再跑」= 啟動前用「頻率×每圈 token×單價」估出花費,別等帳單。
3. 因為它是出事時唯一的黑盒子;覆蓋會把歷史證據毀掉。
4. L1 驗「它想做什麼對不對」、L2 驗「做的方式對不對」、L3 才放生;不一上來 L3 是因為還沒驗證它安全。
5. agent 只「提議」、執行與否由 loop 依等級決定;L1 只記錄提議、從不執行,所以零風險。
6. 因為「被預算斷掉」是沒做完、要有人來看的事件;假裝 success 會掩蓋未完成的真相。

---

✅ 過關條件:你能說出四道防線、解釋 L1→L3 的用意,並在 run-log 裡指出一次 escalate。
下一章,我們處理「驗收本身需要判斷力」的情況 —— 為什麼不能讓 agent 自己驗自己。
→ [第 4 章:maker / checker 雙代理](ch04_maker_checker.md)
