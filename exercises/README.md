# 動手練習 + 自動評分器

每一課對應一組「挖空練習 + autograder」。**這是這門課真正的驗收**:你不是讀完就算,
是要自己把 loop 的關鍵幾行寫出來、被一個獨立的評分器驗過。
(很對味吧——這正是課程教的「別自評,跑一個 verify 閘門」。)

## 怎麼用

```bash
# 1. 打開練習檔,把標 TODO 的地方補完(鷹架都給你了,你只寫核心邏輯)
#    例如第 1 課:
nano exercise1_minimal_loop.py

# 2. 跑 autograder 驗收。全綠就過關,有 ❌ 就照回饋改、再跑一次
python3 check_exercise1.py

# 3. 真的卡死了,再看參考解答(看完務必自己重打一遍)
cat solutions/exercise1_minimal_loop.py
```

`check_exerciseN.py` 預設驗收同資料夾的 `exerciseN_*.py`;
也可以用 `--target` 指到別的檔(例如先拿解答確認評分器本身是對的):

```bash
python3 check_exercise1.py --target solutions/exercise1_minimal_loop.py
```

## 對照表

| 練習 | 對應課 | 你要實作的核心 |
|---|---|---|
| `exercise1_minimal_loop.py` | 第 1 課 | `loop()`:act→verify→decide + 保險絲 |
| `exercise2_exit_conditions.py` | 第 2 課 | `loop()`:SUCCESS / FUSE / STALL 三個出口 |
| `exercise3_safety_budget.py` | 第 3 課 | `Budget` 兩方法 + `should_execute()`(L1 不執行) |
| `exercise4_maker_checker.py` | 第 4 課 | `checker()`:獨立、嚴格、列出所有缺點 |
| `exercise5_parallel_isolation.py` | 第 5 課 | `run_isolated()`:每 worker 一個專屬目錄 |
| `exercise6_scheduling.py` | 第 6 課 | `tick()`:triage→act→verify→done/escalate |
| `exercise7_verifier_gaming.py` | 第 7 課 | `strong_verify()`:用 hold-out+隨機寫出鑽不動的驗證 |
| `exercise8_best_so_far.py` | 第 8 課 | `best_so_far_loop()`:agent 退步時仍回歷史最佳 |
| `exercise9_context_strategy.py` | 第 9 課 | `strat_spec_in_repo()`:有界 context + 去重 |
| `exercise10_loop_evals.py` | 第 10 課 | `aggregate()`:算 loop 級四指標 |

## 看整體進度

回到課程根目錄跑進度儀表板,一次看完六課 + capstone 過了沒:

```bash
python3 ../progress.py
```
