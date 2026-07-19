# 第 1 章 —— 最小的閉環

> **本章目標**:搞懂 loop engineering 到底是什麼、它和 prompt engineering 差在哪,
> 並親手寫出一個不到 15 行的閉環:`act → verify → decide`。
> 做完後你會相信一件事:**所謂「會自己把事情做完的 AI」,核心就是一個帶退出條件的 while 迴圈。**
>
> 參考解答:[`lesson1_minimal_loop.py`](../lesson1_minimal_loop.py)(先別看,卡死了再看)

**TL;DR**:loop engineering = 把「決定要不要再 prompt 一次的人」換成一段 `act→verify→decide` 的程式;
前提是目標必須**機器可判定**。

## 1.1 概念:從「prompt 一次」到「loop 到好」

你在 ChatGPT 打一句話、拿回一個答案,如果不滿意,**是你**再打一句「不對,再短一點」。
這個「看結果 → 決定要不要再要求一次 → 把意見打回去」的人,就是你。

```
你 ──prompt──→ agent ──回答──→ 你看了不滿意 ──再 prompt──→ agent ── …
↑___________________________你一直在迴圈裡當人肉判斷________________________↑
```

**Loop engineering 就是把迴圈裡那個「你」換成一段程式。** 原作者的定義最精準:

> 「Loop engineering 是把『負責去 prompt agent 的那個人』換成系統本身 —— 你設計一套會自己去 prompt agent 的系統。」

| | Prompt Engineering | Loop Engineering |
|---|---|---|
| 你交付的 | 一句好的 prompt | 一個會自己迭代的系統 |
| 誰決定「再來一次」 | 你(人肉) | 程式(verify + decide) |
| 何時停 | 你覺得夠了 | 達到可驗證的目標,或撞上限 |
| 產物 | 一次性的回答 | 可重複、可排程、可稽核的流程 |

### 一個 loop 永遠是這四件事

```
goal    明確、機器可判定的目標
act     做一步(呼叫 agent / 跑命令 / 改檔)
verify  驗一下:達標了嗎?            ← loop 的靈魂,第 2 章整章在講
decide  沒達標就帶回饋再來;達標或燒完就停
```

**最重要的一句話:目標必須「機器可判定」。**
「把文案寫好一點」不能做成 loop —— 因為 verify 永遠不知道何時該停。
「文案要含關鍵字『省時』且 ≤ 12 字」可以 —— 因為一個函式就能客觀回答對或錯。
把模糊願望翻譯成可驗證的條件,是 loop engineering 的第一個真功夫。

### 內層 vs 外層:你在「包住」agent,不是取代它

如果你學過 agent 的內部運作(例如姊妹課 agent-from-scratch 的 ReAct 迴圈),這裡要釐清一個
容易混淆的點——其實有**兩層巢狀的迴圈**:

```
外層(這門課在教的 loop engineering)
   你的程式:  派工 agent → verify → 沒過帶回饋再派 → 達標/燒完才停
   └─ 內層(agent 自己的事,你不用管)
        agent:  reason → act(用工具)→ observe → ……直到它認為自己做完
```

**內層**是 agent 自己的 reason/act/observe 心跳(Claude Code、Codex 內建,你呼叫一次它就跑完一整輪)。
**外層**才是你要設計的:把 agent 當一個黑盒子,**包住**它——給任務、收成品、客觀驗收、決定要不要再派一次。
你不是要改寫 agent 的腦袋,你是要當那個「決定要不要再派工、何時收手」的工頭。這門課從頭到尾講的都是外層。

### 什麼時候「不」該用 loop

loop 不是萬靈丹。它在這些情況是壞主意,硬上只會自動產出垃圾(原因見第 7 章):

| 別用 loop,如果… | 為什麼 |
|---|---|
| **驗證很貴或很慢** | 每圈都要跑驗證;驗證若要 10 分鐘或要花錢,迭代成本爆炸 |
| **驗證不可靠 / 寫不出客觀標準** | verify 是 loop 的地基;地基會騙人,loop 只會更快地騙你(第 7 章) |
| **任務開放式、沒有「做完」的定義** | 沒有退出條件 = 不是 loop,是無底洞 |
| **錯一次代價極高且不可逆** | 自動化的代價是偶爾失控;不可逆的事(刪資料、發錢)該留人把關 |

**判準**:有沒有一個**便宜、可靠、客觀**的「做完了沒」檢查?有 → 適合 loop;沒有 → 先別自動化。

## 1.2 動手做

打開 `lesson1_minimal_loop.py`,但建議自己跟著打一遍(手感是這套教材的一半)。

### Step 1:寫 verify —— 先定義「做完」是什麼意思

```python
GOAL_KEYWORD = "省時"
GOAL_MAXLEN = 12

def verify(draft):
    if GOAL_KEYWORD not in draft:
        return False, f"缺少關鍵字「{GOAL_KEYWORD}」"
    if len(draft) > GOAL_MAXLEN:
        return False, f"太長了({len(draft)} 字)"
    return True, "通過"
```

**檢查點**:注意 verify 回傳的是 `(是否通過, 回饋)`。
那個回饋不是裝飾 —— 它是下一圈 agent 唯一知道「上次哪裡錯」的管道。

### Step 2:act —— 一次 agent 呼叫

本課的 `mock_agent` 是個替身,用排好的草稿模擬「一圈比一圈好」。
真實世界這一步就是一次 LLM 呼叫(見 1.5 怎麼換)。重點是:**它每圈都收到上一圈的 feedback。**

### Step 3:組成迴圈 —— 全部重點就這 10 行

```python
def loop(task):
    feedback = "(第一圈,還沒有回饋)"
    for i in range(1, MAX_ITERS + 1):
        draft = mock_agent(task, feedback, attempt=i - 1)   # act
        passed, feedback = verify(draft)                    # verify
        if passed:                                          # decide
            return draft
    return None   # 圈數燒完還沒過 = 保險絲斷
```

**檢查點**:`MAX_ITERS` 這個保險絲不是可選的。沒有它,一個永遠驗不過的任務會讓
迴圈跑到天荒地老 —— 在真實世界,那等於一張燒不完的帳單。第 3 章會把這件事講透。

### Step 4:跑起來

```bash
python3 lesson1_minimal_loop.py
```

你會看到草稿一圈圈被 verify 打回、帶著回饋修正,第 3 圈通過收工。
**這個 act→verify→decide 的節奏,之後每一課都不會變 —— 只是零件愈換愈真。**

## 1.3 自我檢查(不看上文,答得出來才算過關)

1. 用一句話說,loop engineering 和 prompt engineering 的根本差別是什麼?
2. 一個 loop 的四個組成是哪四個?哪一個是靈魂?
3. 為什麼「把文案寫漂亮」不能做成 loop,「文案含關鍵字 X 且 ≤ N 字」可以?
4. verify 為什麼要回傳「回饋」而不只是 True/False?
5. 拿掉 `MAX_ITERS` 會發生什麼事?在真實世界的代價是什麼?

## 1.4 延伸練習

- **換目標**:把 verify 改成「必須包含一個 emoji 且結尾是問號」,看 mock 草稿會不會卡住、
  以及卡住時 loop 怎麼處理(這逼你體會「verify 太嚴 → 永遠燒到保險絲」)。
- **真 agent 預習**:如果你做過 agent-from-scratch,把 `mock_agent` 換成那邊的 `llm()` 呼叫,
  把 verify 的回饋當成 user 訊息餵回去。你會發現整個 loop 骨架一個字都不用改。
- **想一個你自己的 loop**:寫下一件你最近重複手動 prompt AI 好幾次才弄好的事。
  它的 goal / verify 各是什麼?能不能機器判定?(答不出 verify = 還不能自動化,這很正常)

## 1.5 動手驗收

讀完別只是點頭——去把 loop 自己寫一遍:打開 [`exercises/exercise1_minimal_loop.py`](../exercises/exercise1_minimal_loop.py),
補完 `loop()`,跑 `python3 exercises/check_exercise1.py`,全綠才算過這一關。

## 1.6 自我檢查解答

1. prompt = 你交付一句話、看一次結果;loop = 你交付一個會自己迭代的系統,「再來一次」由程式決定。
2. goal / act / **verify** / decide;verify 是靈魂——它定義「做完」、決定何時停。
3. 因為 loop 需要 verify 客觀判定對錯;「漂亮」無法,「含 X 且 ≤ N 字」一個函式就能判。
4. 因為回饋是下一圈 agent 唯一知道「上次哪裡錯」的線索,只回 True/False 它無從改起。
5. 會無限跑下去;真實代價是一張燒不完的 API 帳單(鬼打牆的 agent 一夜燒光額度)。

---

✅ 過關條件:你能獨立寫出 act→verify→decide 的迴圈,並說清楚為什麼目標必須可被機器判定。
下一章,我們把 verify 從「一個函式」升級成「跑一個真的命令」,並補上 loop 的其他出口。
→ [第 2 章:退出條件與驗證閘門](ch02_exit_conditions.md)
