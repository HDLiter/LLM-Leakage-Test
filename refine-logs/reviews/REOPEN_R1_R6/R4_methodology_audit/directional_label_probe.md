# directional-label 查证(P0 kickoff §6 并行项,2026-05-31)

> **status**:查证产物,登记备查。卡着四池 `four_layer_candidate_pools.md` §1.3 整族因子
> (F_textdir / F_corpusbal / F_predict / F_surprise)的命运——这族都需要一个"看涨/看跌/
> 可预测性"的方向打分,且**必须独立于被测 fleet 的 P_predict、且非真实股价 ex-post**。
> 纯查证,**不替 owner 拍**(此族最终取舍在因子扩展 decision)。

---

## 0. 一句话结论

**有一个现成的候选方向标注 `expected_direction`(~730–750 例,{up/down/neutral}),但它"合不合法"是 owner 要拍的一个真判断,不是自动 ✅。** 卡点 = 标注者是 GPT 家族(Codex),而 fleet 里**就有 GPT-5.1 和 Claude Sonnet 4.6**。

---

## 1. 查到了什么

- **字段**:`expected_direction` ∈ {`up`,`down`,`neutral`}。
- **位置**:`data/seed/v3_annotation_labels/v3_annotation_batch_*.json`(18 批)+ `v3_annotation_double/`(50 例重复标注做信度)。
- **覆盖**:~730–750 个 v3 candidate(每条都有该字段)。
- **怎么来的**:`scripts/annotate_v3_batch.py` 把 `docs/ANCHOR_RUBRIC.md` 逐字嵌进 system prompt,
  由 **Codex MCP(GPT-5.x)** 按 rubric 机械标注;driving agent 是 Claude Code。
- **CLS 原始语料本身无 sentiment 字段**:`data/cls_telegraph_raw/*.json` 每条电报字段 =
  id / title / content / time / category(恒"all")/ type / recommend / author / source。**无方向/情感列。**
- **Thales 源仓库**:无现成 sentiment/direction 标注;`signal_profile.py` 只有 modality/authority
  评分(官方公告/监管/舆论),**非**情感方向。无金融看涨看跌词典。

## 2. 合法性 —— 为什么不是干净的 ✅(要 surface 给 owner)

§1.3 红线:方向打分**必须独立于 P_predict**(否则混入模型 bias + 与被测任务循环);
合法外部 judge 的限定词是"**非 fleet 模型**"。

`expected_direction` 满足的:
- ✅ 不来自真实股价(无 ex-post outcome 对应)。
- ✅ 不来自 fleet 的 P_predict 产物(是独立 annotation pipeline、跑的是 rubric 标注任务,不是预测任务)。

**没干净满足的(= owner 要拍的点)**:
- ⚠️ 标注者是 **Codex = GPT 家族**;fleet 里**含 GPT-5.1、Claude Sonnet 4.6**。"外部 judge 须非 fleet 模型"
  这一条只**部分**成立。两种读法:
  - (a) 宽松:外部 judge 跑的是"按固定 rubric 打方向",与 fleet 的自由 P_predict 任务不同,且只当**因子**(分层用)不当被测量本身 → 独立性够。
  - (b) 保守:同模型家族 → 先验相关 → 给 F_textdir 这个**方向因子**埋软循环(模型自己的方向先验,既进标注又进被测)。
- ⚠️ 语义错位:`expected_direction` 是 **anchor rubric 标注的副产品**(主目的是 anchor_level / 案例识别力),
  含义 = "该**事件**期望方向",更贴近 F_structdir / F_textdir(事件类→方向),**不是**干净的人工 gold sentiment,
  也不是词典规则。当 F_textdir 用语义勉强对得上,当 F_corpusbal/F_surprise 不直接给。

## 3. 三选一判定

**(B 偏向)有候选标注但来源须 owner 裁定**:`expected_direction` 现成、零成本、覆盖够,
但"GPT 家族 judge + fleet 含 GPT/Claude"使其作**方向因子**的合法性需 owner 拍(宽松收下 / 保守另起)。

## 4. 若 owner 判不可用 —— 最低成本合法路径

1. **规则/词典**(最低成本、最干净独立):CLS 有结构化线索可借(标注里已抽出的 `category`/`subcategory`/
   `target_type`/`key_numbers` + 正文涨跌百分比)。如"回购/获批/中标"→up、"减持/违规/风险"→down、综述→neutral。
   缺点:噪声大、覆盖不全。
2. **真·非 fleet 外部 judge**:用一个**确定不在 fleet 里**的中文金融情感模型(如专用 FinBERT-zh / 第三方金融 NLP),
   彻底避开 GPT/Claude 家族污染。比规则干净、比现有标注合法性强。
3. **继续人工/judge 标注**:复用 `annotate_v3_batch.py` 管线,但换一个非 fleet 标注模型 + 抽样人审。

## 5. 给因子扩展 decision 的交接

- §1.3 整族**条件性解锁**:owner 判 `expected_direction` 可用 → 该族在现成数据上起步(F_textdir 最直接);
  判不可用 → 走 §4 的规则或非-fleet-judge 路径,成本上移。
- `expected_direction` 即便判可用,**当 F_textdir** 比当 F_corpusbal/F_surprise 自然;后两者仍要另算。
- 信度:有 50 例 double-annotation 可估一致性(未在本次量化,留因子扩展 decision pilot 时算)。
