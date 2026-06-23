"""
quiz_bank.py —— 各章知識測驗題庫
=================================
三種題型:
  mcq     單選,可自動批改 (answer = 正解的選項索引,從 0 起算)
  short   簡答,可自動批改 (accept = 可接受的關鍵字清單,答案含任一即算對)
  reflect 反思題,無法自動批改 → 顯示參考答案,由你自評

題庫格式由 quiz.py --check 驗證。
"""

BANK = [
    # ---------- 第 1 章 ----------
    {"ch": 1, "type": "mcq",
     "q": "Loop engineering 和 prompt engineering 最根本的差別是?",
     "options": [
         "loop 用比較貴的模型",
         "loop 把『決定要不要再 prompt 一次的人』換成程式",
         "loop 一定要用多個 agent",
         "loop 不需要 prompt"],
     "answer": 1,
     "model": "你交付的不再是一句 prompt,而是一個會自己迭代(act→verify→decide)的系統。"},
    {"ch": 1, "type": "short",
     "q": "一個 loop 的四件事 goal / act / verify / decide 裡,哪一步是靈魂?",
     "accept": ["verify", "驗"],
     "model": "verify —— 它定義了『做完』是什麼意思,決定 loop 何時該停。"},
    {"ch": 1, "type": "reflect",
     "q": "為什麼『把文案寫漂亮』不能做成 loop,『文案含關鍵字 X 且 ≤ N 字』可以?",
     "model": "因為目標必須機器可判定。verify 要能客觀回答對或錯,否則 loop 永遠不知道何時該停。"},

    # ---------- 第 2 章 ----------
    {"ch": 2, "type": "mcq",
     "q": "between-iteration command(每圈跑的檢查命令)用什麼來判斷是否通過?",
     "options": ["agent 的自我感覺", "命令的結束碼 exit code", "輸出的字數", "花的時間"],
     "answer": 1,
     "model": "結束碼 0 = 通過。去問編譯器/測試/linter,別問 agent『你好了嗎』。"},
    {"ch": 2, "type": "short",
     "q": "連續兩圈產出完全相同,應該觸發哪一個退出條件?",
     "accept": ["stall", "卡住", "卡"],
     "model": "STALL —— agent 鬼打牆了,提早止血,不必把 max-iter 燒完。"},
    {"ch": 2, "type": "reflect",
     "q": "為什麼『檢查命令的輸出要原封不動餵回 agent』?",
     "model": "那串錯誤訊息/失敗的測試名,是 agent 下一圈修錯的唯一線索;吞掉它 agent 就學不到東西。"},

    # ---------- 第 3 章 ----------
    {"ch": 3, "type": "mcq",
     "q": "下列何者『不是』放生 loop 前的四道防線之一?",
     "options": ["max-iter 保險絲", "預算上限", "run-log", "用最新的模型"],
     "answer": 3,
     "model": "四道防線是:保險絲、預算、run-log、分階段上線(L1→L3)。用哪個模型無關安全。"},
    {"ch": 3, "type": "mcq",
     "q": "自治等級 L1(report)會做什麼?",
     "options": ["全自動執行", "只觀察、只報告,絕不動手", "動手前問人", "只在出錯時動手"],
     "answer": 1,
     "model": "L1 是 dry-run:先零風險地看 agent『想做什麼』,確認沒問題再往 L2/L3 放。"},
    {"ch": 3, "type": "short",
     "q": "run-log 要用什麼寫入模式,才不會把歷史蓋掉?",
     "accept": ["append", "附加", "不覆蓋", "a"],
     "model": "append-only(附加)。沒有日誌的自動化等於沒發生過,它是出事時的黑盒子。"},
    {"ch": 3, "type": "reflect",
     "q": "『propose / commit 分離』是什麼?它如何讓 L1 變成零風險?",
     "model": "agent 只『提議』動作,『要不要執行』由 loop 依等級決定。L1 只記錄提議、從不執行,所以零風險。"},

    # ---------- 第 4 章 ----------
    {"ch": 4, "type": "mcq",
     "q": "為什麼不該讓做事的 agent 自己驗收自己的成果?",
     "options": [
         "太慢", "會自我感覺良好(grading inflation),幾乎一定放水",
         "太貴", "模型不支援"],
     "answer": 1,
     "model": "有動機說『我完成了』的 agent 不是公正的裁判。要交給獨立、更嚴的 checker。"},
    {"ch": 4, "type": "short",
     "q": "checker 判定 reject 時,除了『不通過』還必須回傳什麼,maker 才改得動?",
     "accept": ["原因", "怎麼改", "具體", "回饋", "缺點"],
     "model": "具體該怎麼改(reject 原因)。只回 reject 不給原因,maker 只能瞎猜、loop 空轉。"},
    {"ch": 4, "type": "reflect",
     "q": "真實世界要怎麼讓 checker 真正『獨立』於 maker?",
     "model": "用不同的 system prompt、甚至不同的模型,且 checker 不該知道 maker 多努力,只看成品對不對。"},

    # ---------- 第 5 章 ----------
    {"ch": 5, "type": "mcq",
     "q": "同時跑多個 loop 的前提是?",
     "options": ["買更多 CPU", "隔離(每個 loop 有自己的工作空間)", "用同一個目錄省空間", "關掉保險絲"],
     "answer": 1,
     "model": "沒有隔離,平行的 loop 會互相覆蓋檔案、交叉污染,產出沒人能負責。"},
    {"ch": 5, "type": "short",
     "q": "在寫程式的場景,讓多個 agent 平行又互不干擾的標準 git 手段是?",
     "accept": ["worktree", "git worktree"],
     "model": "git worktree —— 同一 repo 長出多個獨立 checkout,共享物件庫但檔案分開。"},
    {"ch": 5, "type": "reflect",
     "q": "為什麼說『隔離不是效能優化,是正確性的前提』?",
     "model": "沒隔離時平行產出會互相污染,結果根本不可信;隔離保的是正確性,不是速度。"},

    # ---------- 第 6 章 ----------
    {"ch": 6, "type": "mcq",
     "q": "把 loop 變成會自己醒來的系統,正確的寫法是?",
     "options": [
         "while True: sleep 的常駐進程", "寫成 --once,交給 cron 每次呼叫一次",
         "讓人每天手動跑", "用一個超長的 max-iter"],
     "answer": 1,
     "model": "--once + cron 天然抗當機:每次都是乾淨新進程,狀態靠外部保存。"},
    {"ch": 6, "type": "mcq",
     "q": "排程 loop 的某一拍發現沒有待辦事項時,正確的行為是?",
     "options": ["硬找事做", "瘋狂呼叫 agent", "安靜跳過、記一筆 idle", "報錯中止"],
     "answer": 2,
     "model": "『沒事就什麼都不做』是正確結果,不是失敗。好公民的 loop 會安靜跳過。"},
    {"ch": 6, "type": "reflect",
     "q": "一個 tick 做哪四件事?分別用到了前面哪幾課的零件?",
     "model": "triage(找事)→ act(第1/2課)→ verify(第4課獨立 checker)→ log+decide(第3課 run-log/escalate)。"},

    # ---------- 第 7 章 ----------
    {"ch": 7, "type": "mcq",
     "q": "agent 要讓 verify 變綠,最省力的方式往往是?",
     "options": [
         "真的把問題徹底解決", "鑽 verify(硬編答案/改弱測試),而不是解決問題",
         "多跑幾圈", "換一個模型"],
     "answer": 1,
     "model": "agent 追逐的是『讓 verify 綠』,不是『把問題解對』;最省力常常就是鑽漏洞。"},
    {"ch": 7, "type": "short",
     "q": "「當一個指標變成目標,它就不再是好指標」——這是哪個定律?",
     "accept": ["goodhart", "古哈特"],
     "model": "Goodhart 定律。verify 一旦變成 agent 追逐的目標,就開始失真、被鑽。"},
    {"ch": 7, "type": "mcq",
     "q": "下列何者『不是』把 verify 變難鑽的對策?",
     "options": ["hold-out 隱藏案例", "多組 + 隨機輸入", "讓 agent 也能改 verify/測試", "人定期抽查"],
     "answer": 2,
     "model": "正好相反——要『隔離』,讓 agent 不能改 verify/測試本身(否則它直接改考卷)。"},
    {"ch": 7, "type": "reflect",
     "q": "第 2 課的 `print(20 + 22)` 為什麼其實是一次作弊?它說明了什麼?",
     "model": "它沒寫出會計算的程式,而是把答案硬編進去、只過那一個檢查;說明『通過 verify』≠『解決問題』,verify 只是代理指標。"},

    # ---------- 第 8 章 ----------
    {"ch": 8, "type": "mcq",
     "q": "真實 LLM agent 跟前幾課的乖寶寶 stub,最大的差別是?",
     "options": ["比較貴", "它是非決定性的——會亂跳、會退步、同 prompt 兩次結果不同", "比較慢", "需要 GPU"],
     "answer": 1,
     "model": "真 agent 的輸出是一個分佈,不是定值;所以 loop 要為分佈設計(best-so-far、重試、冪等)。"},
    {"ch": 8, "type": "short",
     "q": "跨圈記住歷史最佳結果、末圈退步也不受影響的做法,叫什麼?",
     "accept": ["best-so-far", "best so far", "歷史最佳", "最佳"],
     "model": "best-so-far。只看最後一圈會丟掉中途更好的結果;真 agent 會退步,這個 bug 一定踩到。"},
    {"ch": 8, "type": "mcq",
     "q": "agent 偶發失敗(rate limit/5xx),重試該怎麼做?",
     "options": ["固定間隔狂重試", "指數退避 + 抖動(jitter),且重試也要有上限", "立刻無限重試", "直接放棄"],
     "answer": 1,
     "model": "固定間隔狂重試會雪上加霜、且多 client 會撞在一起;退避+抖動把重試錯開。"},

    # ---------- 第 9 章 ----------
    {"ch": 9, "type": "mcq",
     "q": "把跨圈記憶塞進「對話歷史」最大的問題是?",
     "options": ["太簡單", "context 無上限長大 → 爆成本、撞 context window、還會 drift", "agent 看不懂", "不能存檔"],
     "answer": 1,
     "model": "對話每圈長大,遲早爆;改把記憶寫成 repo 裡的精簡 spec(durable spec),context 才有界。"},
    {"ch": 9, "type": "short",
     "q": "每圈用乾淨 context、把跨圈記憶寫進 repo 一份精簡檔——這份檔通稱什麼?",
     "accept": ["spec", "durable spec", "scratchpad"],
     "model": "durable spec。同時解決成本(有界)、drift(每圈乾淨)、抗當機(狀態在 repo)。"},
    {"ch": 9, "type": "reflect",
     "q": "stateless / conversation / spec-in-repo 三種上下文策略,各自的優點與致命傷?",
     "model": "stateless 省但無記憶會鬼打牆;conversation 有記憶但 context 爆炸且 drift;spec-in-repo 有記憶又有界(要自己維護 spec)。"},

    # ---------- 第 10 章 ----------
    {"ch": 10, "type": "mcq",
     "q": "要判斷一個 loop 值不值得上線,該看什麼?",
     "options": ["單一任務驗一次綠了就好", "對一整批任務的整體指標(成功率/圈數/escalation/成本)",
                 "跑得快不快", "程式碼行數"],
     "answer": 1,
     "model": "單任務單次是軼事;loop 的好壞要對 task suite 看分佈,而且要 A/B 比較才有意義。"},
    {"ch": 10, "type": "short",
     "q": "loop 級 eval 的四個基本指標,除了成功率,再說出一個。",
     "accept": ["平均圈數", "圈數", "escalation", "escalation 率", "成本", "平均成本", "mean_iters", "mean_cost"],
     "model": "成功率 / 平均圈數 / escalation 率 / 平均成本——四個一起看才看得出取捨。"},
    {"ch": 10, "type": "reflect",
     "q": "為什麼說 loop 的指標『只有在比較時才有意義』?",
     "model": "單看『成功率 0.9』不知好壞;A/B(如 max_iters 3 vs 8)才看得出你用成本換到了成功率,進而決策。"},
]
