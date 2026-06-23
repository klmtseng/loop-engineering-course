# 第 2 章 —— 退出條件與驗證閘門

> **本章目標**:把第 1 章的 verify 升級成「跑一個真實命令、看結束碼」,並認識一個能在
> 真實世界活下來的 loop 至少要握有的三個出口:SUCCESS / FUSE / STALL。
> 做完後你會明白:**loop 的品質,幾乎全押在 verify 這一步上。**
>
> 參考解答:[`lesson2_exit_conditions.py`](../lesson2_exit_conditions.py)

**TL;DR**:verify 用「跑命令看結束碼」最可靠;一個能放生的 loop 至少要有
SUCCESS / FUSE / STALL 三個出口。

## 2.1 概念:最可靠的 verify 是「跑一個命令」

第 1 章的 verify 是手寫的 Python 函式。在寫程式的場景,你其實有個現成、零成本、
而且不會騙你的裁判 —— **命令的結束碼 (exit code)**:

| 命令 | 結束碼 0 代表 |
|---|---|
| `pytest` | 測試全綠 |
| `ruff check .` | 沒有 lint 問題 |
| `npm run build` | 編得過 |
| `curl -f https://.../health` | 服務還活著 |

這種「做完一圈就跑一次的檢查命令」,有個名字叫 **between-iteration command**,
是 loop engineering 最核心的零件。它的精神是:**別問 agent「你覺得好了嗎」,
去問編譯器、測試、linter —— 它們不會自我感覺良好。**

```python
def run_check(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, shell=True,
                          capture_output=True, text=True, timeout=30)
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output   # 0 = 通過;輸出當回饋餵回 agent
```

**關鍵細節**:命令的輸出(錯誤訊息、失敗的測試名)要原封不動交給下一圈。
那串紅字就是 agent 修錯的全部線索。本課的 demo 裡你會看到 agent 從 `SyntaxError`
→ 看到「印出的是 41,期望 42」→ 改對,完全靠這個回饋。

## 2.2 概念:一個出口不夠,要三個

「跑到綠為止」聽起來很美,但如果永遠不綠呢?一個能放生的 loop 至少要有三個出口:

| 出口 | 觸發條件 | 為什麼需要 |
|---|---|---|
| **SUCCESS** | 檢查命令回傳 0 | 你要的結局:達標收工 |
| **FUSE** | 圈數燒完仍未綠 | max-iter 保險絲,防無限燒錢(第 1 章就有) |
| **STALL** | 連續兩圈產出完全相同 | agent 鬼打牆了,再跑也白跑,**提早**止血 |

STALL 常被新手漏掉。少了它,一個卡住的 agent 會把 max-iter 整個燒完才停 ——
那中間白燒的每一圈,都是省得下的錢和時間。偵測它只要記住上一圈的產出:

```python
if code == last_code:        # 這圈和上圈一模一樣
    return Exit.STALL, None  # 不必等保險絲燒完,現在就停
last_code = code
```

> **⚠️ 講精確一點(這版 STALL 的界線)**:它只比對「上一圈」,所以只抓得到**不動點**——
> 連續兩圈完全相同。它**抓不到長度 ≥ 2 的循環**,例如 `A,B,A,B,A,B` 來回震盪(這在真 agent 上很常見),
> 那種還是會一路燒到 FUSE。「鬼打牆」這個詞會讓人以為它能抓「繞圈圈」,但實作只擋得住「原地不動」。
> 要抓循環,得記住**最近 N 圈的產出集合**,出現重複就判定打轉(而且這仍是啟發式,不保證抓到所有循環)。

> 真實世界還有更多出口:逾時 (timeout)、外部 kill-switch 檔案出現、預算用罄
> (第 3 章)。但 SUCCESS / FUSE / STALL 是地板,少一個都不該放生。

## 2.3 動手做

`lesson2_exit_conditions.py` 讓 agent 反覆改一支 `add.py`,直到它印出 `42`。
驗證閘門是一支現寫的 `check.py`(模擬真實專案裡的 pytest):

```python
check_cmd = "python3 check.py"
reason, code = loop(check_cmd, workdir)
```

跑跑看:

```bash
python3 lesson2_exit_conditions.py
```

**檢查點**:觀察每一圈的「檢查命令輸出」。第 1 圈是語法錯的 traceback、
第 2 圈是「印出的是 '41',期望 '42'」、第 3 圈才綠。agent 每一步都在讀
上一步的真實錯誤 —— 這就是 between-iteration command 的威力。

**第二個檢查點**:loop 函式本身完全不知道「42」這件事。它只知道「跑 check_cmd、
看結束碼」。所以你把 `check_cmd` 換成 `pytest`、`ruff`、`make`,這支 loop **一個字都不用改**。
這種「驗證與任務解耦」是好 loop 的標誌。

## 2.4 卡關排查

| 症狀 | 原因 | 解法 |
|---|---|---|
| loop 永遠跑到 FUSE | verify 條件太嚴,或 agent 根本沒能力達標 | 先手動確認「這任務人來做、命令會不會綠」 |
| 明明卡住卻燒完才停 | 沒做 STALL 偵測 | 比對連續兩圈產出,相同就提早退出 |
| 回饋是空字串、agent 學不到東西 | 檢查命令把輸出吞掉了(如 `grep -q`) | 讓 verify 印出人和 agent 都讀得懂的訊息 |
| subprocess 卡住不返回 | 命令會等待輸入 / 跑不完 | 一定要加 `timeout=`,逾時也是一個出口 |

## 2.5 自我檢查

1. 什麼是 between-iteration command?它比「問 agent 你做完了嗎」好在哪?
2. 一個能放生的 loop 至少要有哪三個出口?各自防的是什麼?
3. STALL 偵測為什麼能省錢?少了它最糟會怎樣?
4. 為什麼說「檢查命令的輸出要原封不動餵回 agent」?
5. 本課的 loop 換個 check_cmd 就能驗別的任務,這靠的是什麼設計性質?

## 2.6 延伸練習

- **換真檢查**:把 demo 改成讓 agent 寫一個函式,用 `pytest` 當 check_cmd
  (寫一支 `test_add.py`)。體會「測試即 verify」。
- **加第四個出口**:加上 timeout 出口 —— 如果某一圈的檢查命令跑超過 N 秒就中止並 escalate。
- **故意製造 STALL**:把 `_VERSIONS` 改成第 2、3 個版本一模一樣,確認 loop 真的在 STALL 提早停,
  而不是燒到 FUSE。
- **偵測循環(補上 STALL 的盲點)**:現在的 STALL 抓不到 `A,B,A,B` 震盪。改用一個 `seen = set()`
  記住最近 N 圈的產出,這圈的 code 若已在 `seen` 裡就判定「打轉」提早退出。先用一個會 A,B 來回的
  假 agent 確認原 STALL 抓不到、你的新版抓得到。(想想:N 該多大?會不會誤殺正常的重訪?)

## 2.7 動手驗收

打開 [`exercises/exercise2_exit_conditions.py`](../exercises/exercise2_exit_conditions.py),
把三個出口寫進 `loop()`,跑 `python3 exercises/check_exercise2.py` 驗收。

## 2.8 自我檢查解答

1. 它是每圈跑的檢查命令,用結束碼判斷;比「問 agent 你好了嗎」好在它客觀、不會自我感覺良好。
2. SUCCESS(達標收工)/ FUSE(圈數燒完,防無限燒錢)/ STALL(連兩圈相同,鬼打牆提早止血)。
3. STALL 在卡住當下就停,省下原本要白燒到 FUSE 的那幾圈;少了它最糟會燒滿 max-iter 才停。
4. 因為那串錯誤訊息是 agent 下一圈修錯的唯一線索,吞掉它 agent 就學不到、只能瞎改。
5. 靠「驗證與任務解耦」:loop 只負責跑 `check_cmd`、看結束碼,不綁死任何特定任務。

---

✅ 過關條件:你能用「跑命令看結束碼」實作 verify,並說出 SUCCESS/FUSE/STALL 各防什麼。
下一章,我們面對一個會自己花錢、自己改檔的系統 —— 怎麼讓它安全地、花得起地跑。
→ [第 3 章:安全與成本](ch03_safety_budget.md)
