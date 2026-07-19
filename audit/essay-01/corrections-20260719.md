# VA 裁決與更正記錄 — 2026-07-19(第一梯次:v2 四稿 + 兩 repo 回推)

兩段式:內審(sonnet 機械審計,`content_audit.md`)+ 獨立冷審(opus fresh-context,不看 ledger/內審,
全文 `cold-review-20260719.md`)。以下為主對話合併裁決與實際更正,全部已執行並驗證。

## 確認並已修(T1/發佈阻斷級)

| 發現 | 抓到者 | 更正 | 證據 |
|---|---|---|---|
| marketplace repo local `user.email=<personal-email>` 覆蓋,4 個回推 commit 帶真實 email(未 push) | 冷審 P1-1 | local config 改 noreply;`git rebase --exec '--reset-author'` 改寫 4 commits | rebase 後 `git log --format='%h %ae'` 全 noreply(cde4d74..f7aed9f) |
| validity-audit repo 無 LICENSE 檔,三稿 MIT 宣稱無法成立 | 內審 P1-B | 補 MIT LICENSE + commit b10d407(noreply) | `git log` ahead 2,LICENSE 在庫 |
| story-long「Six months of ledger entries」誇大(帳本實齡 16 天)且與同文「a month」自相矛盾 | 雙方獨立 | 改「A few weeks of ledger entries already say…」 | grep 無殘留 |
| 「a month of (my) failure ledger」×2(story/x-thread)誇大約 2× | 內審 P1-A | 皆改「a few weeks / weeks of」 | grep 無殘留 |
| 「A few weeks ago」(wigner 距發稿 11-13 天) | 內審 P2-A | story/linkedin 改「Two weeks ago」 | 已改 |
| battle-table psi-field 未標哪個是規格值 | 冷審 P1-2 | 改「from the spec value 70/20 to an off-spec 80/10」 | 已改 |
| 「2.5 of 6」半條無解釋 | 冷審 P2-1 | 加「(a partial hit counted as half)」 | 已改 |
| 「retracted two」精度(C1 是降級為恆真非撤回) | 內審 P3-A | 改「did not survive / struck down / rejected」 | 已改 |

## 裁決不改(記錄在案)

- **P2-2 選擇性呈現**(50%→70% 只舉 requests 組):單案例舉證合理;備查數據=同專案 yfinance strict 12%(broad 39%),被追問時出示。
- **P2-3「happened to match」**:已有下文補救,保留。
- **P3-B「3 new problems」vs 公開 README「two confirmed bugs」**:描述子集不同非矛盾,不改。
- **P3-1 story-long 頭部內部備註**:屬草稿鷹架,產出平台版時剝除(exports 流程負責)。

## 審計者互查記錄(誰驗證驗證者)

- 內審稱 marketplace「實際 3 commits」:主對話 `git rev-list --count` 實測=4,**內審自己數錯**,不採。
- 冷審 P1-2 的敘述過程有猶疑,最終結論(標示規格值)採納;其數字比對與來源逐字核可。

## 全數字核可清單(兩段一致)

KS p=0.000 / N=2000 p=0.219 / corr 0.71 / t=1.92 n.s. / 2 of 3 / 70/20→80/10 第三度 /
2.5/6→5/6+3 bonus / 5 template bugs / 50%→70% / shootout (date,pair) / 乘法k→加法δ翻案 /
兩支回推腳本實跑通過 / 四紅旗無觸犯 / 英中語義無漂移(除已修項)。

## 教訓寫回

- 失手帳本新條目:commit metadata 掃描盲區(見 judgment-rubrics.md 2026-07-19 條)。
- 待辦:全部 VA 結案時 `ledger.py append`(含 domain=content 與 metadata-scan 類別)。
