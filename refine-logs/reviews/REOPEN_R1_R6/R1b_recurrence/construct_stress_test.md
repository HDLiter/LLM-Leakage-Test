# R-1b Construct Stress Test: Recurrence 是 exposure proxy 还是 outcome-leakage proxy

生成时间: 2026-05-24

结论先行: **推翻上一轮 (a) 段的 unfiltered reference-row 选择,改选 B 立场: L2 subject + `tradable_at_event=true`**。核心理由是: R-1b 的 Recurrence 进入主模型时不是一个孤立的文本熟悉度描述,而是和 Cutoff Exposure 做 β3 交互来解释“泄露放大”。这个 β3 的物理 driver 是 outcome/direction memory,所以 reference rows 应该只数有可交易 outcome 的 subject rows。

证据来源:阶段 1 只使用 `docs/RESEARCH_PROPOSAL.md` 指定章节、`refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` 指定章节、`docs/DECISION_20260518_ws0_5_thales_alignment.md` §4.5,以及 Carlini et al. 2023 `Quantifying Memorization Across Neural Language Models` 的 arXiv/OpenReview 版本。阶段 2 才读取上一轮 `whiteboard_analysis.md` 的 (a) Construct 段。

## 阶段 1 独立判

### A 立场最强论证: pure text exposure proxy

A 的最强版本不是“方便”,而是“Recurrence 的文献锚点本来就是文本重复”。Carlini et al. 2023 的核心事实是:训练集中重复出现越多的序列,越容易被模型抽取或在给定前缀下复现；这个规律不关心文本对应的金融实体当时是否可交易。论文的 ICLR 版本把 extractability 定义为给训练前缀后模型能否逐字生成后缀,并报告重复频次、模型规模、上下文长度都提高 memorization。这个锚点支持的是 text frequency -> memorization,不是 tradable frequency -> memorization。

按这个定义,R-1b Recurrence 的 driver 链是:

1. Reference window 内 `(target_entity_id, event_super_type)` 的 L2 subject row 越多,模型在训练中越可能多次看到“这个标的发生这类事”的文本模式。
2. 重复文本会强化几条 memorization 路径: verbatim 或近似 verbatim span memory；target-event lexical association；模板和数值槽位的熟悉度；entity-conditioned continuation prior。
3. 这些路径会抬高 `P_predict` 的方向性输出,或者至少降低 article text 的 surprise。
4. 在 estimand 上,它最自然地进入 `E_CTS` 和 `E_PCSG`:高 recurrence 的文本对晚 cutoff 模型更熟,所以 tail surprise 更低、paired cutoff surprise gap 更大。它也能进入 `E_NoOp`:模板化/重复文本更可能被无关插入扰乱或触发 brittle matching。它可以解释一部分 `E_CMMD`,因为晚 cutoff 模型对高 recurrence target-family pattern 有更多 parametric familiarity。
5. β3 的读法是:Cutoff Exposure 给“模型可能见过”的时间门槛,Recurrence 给“同类文本重复强化”的剂量；两者相乘,预期泄露信号更强。

A 的优点是干净贴住 Carlini anchor,并且覆盖所有“surface familiarity”类 estimand。它也尊重 R-0 的一个架构直觉:non-tradable rows 保留在 L1/L2,可作为 factor-computation object,不因为不能做 P_predict subject 就从语料历史里消失。

A 的硬伤是:它把“模型见过同类文本”当作 Recurrence 的充分定义。只要 β3 最后主要由 `E_FO` 或方向预测 lift 驱动,A 就要解释为什么一些没有 actionable outcome 的 historical rows 也应该进入“泄露放大”剂量。它可以说这些 rows 仍然提高实体/模板熟悉度,但这已经不是 outcome leakage,而是 background familiarity。

### B 立场最强论证: outcome-leakage proxy

B 的最强版本是:这个 benchmark 不是一般文本记忆 benchmark,而是金融新闻 look-ahead leakage benchmark。研究问题问的是 LLM 在历史金融新闻预测任务上是否使用了训练时已知、发文当时未知的信息。R-4a 锁下来的 β3 结构也不是单看 Recurrence 主效应,而是 `Cutoff Exposure × Recurrence -> 泄露`。所以 Recurrence 的定义应该贴住“哪些重复历史 rows 能给模型提供 outcome/direction memory 的训练机会”,而不是贴住“哪些 rows 只让模型读过名字和模板”。

按 B 定义,driver 链是:

1. Reference window 内只数 L2 subject rows 且 `tradable_at_event=true`。这保留“target 是中心经济 actor”,同时要求当时存在可交易价格路径。
2. 在 A 股 CLS 语境里,只要实体是可交易 subject,就必然能从 T+1/T+5 或其他锁定 horizon 计算 realized direction。这个事实不需要 R-6 额外落定 `outcome_verifiable` 字段；R-0 L2 schema 已经有 `tradable_at_event`。
3. 这些 rows 给模型提供的是 target-family-outcome 的重复机会:同一标的反复发生同类事件,训练语料和后续市场报道里可能反复出现“事件文本 + 之后市场方向/结果”的组合。
4. memorization 路径不只是 verbatim span,还包括 target/event slot anchors、realized direction prior、post-event coverage association、以及在 false-outcome prompt 下回到 cached outcome 的倾向。
5. 在 estimand 上,B 最直接覆盖 `E_FO`:如果模型无视可见假结果,回到真实方向/真实结果,这正是 outcome memory。它也强覆盖 `E_CMMD`:晚 cutoff 模型比早 cutoff 模型更可能有 post-event outcome memory,所以方向预测产生 cutoff-monotone disagreement。它覆盖 `E_PCSG` 和 `E_CTS` 的方式较窄,但仍成立:tradable subject rows 本身也是文本曝光,只是 B 有意排除了不能产生 outcome memory 的那部分文本曝光。
6. β3 的读法更直:Cutoff Exposure 是“有没有机会看见该 case 后来的结果”,Recurrence 是“这个 target-family 的 outcome-bearing repetition 强度”。两者相乘就是泄露放大。

B 的优点是和主问题、P_predict 任务、`E_FO`、`E_CMMD`、以及 β3 解释最一致。它还不需要任何架构扩展:L2 已有 `tradable_at_event`;L3 base/Pool B 本来就使用这一字段。它不是把 case admissibility 偷渡进 factor,而是把 outcome-leakage construct 的 outcome-bearing 条件写进 reference rows。

B 的代价是:它不再是 Carlini 意义上的纯 exposure 计数。Non-tradable subject rows 即使被模型训练时见过,也可能提升 verbatim/surface familiarity；B 会故意不数它们。因此,Carlini 2023 在 B 下仍是 repetition -> memorization 的机制锚点,但不再是 reference-row inclusion rule。换句话说,Carlini 说明“重复会被记住”,B 另加一层项目内定义:“R-1b 主 Recurrence 只数能把这种记忆转成 outcome leakage 的重复”。

### 5 estimand × 两立场 driver 链覆盖矩阵

| Estimand | 它主要测什么 | A: pure exposure 覆盖 | B: outcome-leakage 覆盖 | 判断 |
|---|---|---|---|---|
| `E_CTS` | 单模型文本 surface familiarity / tail surprise | **强**。所有训练文本重复都可能降低 surprise,tradability 无关。 | **中**。tradable rows 也是曝光,但会漏掉 non-tradable text familiarity。 | A 更自然；B 可覆盖但不是最宽口径。 |
| `E_PCSG` | late vs early cutoff paired surprise gap | **强**。高重复文本对 late model 更熟。 | **中到强**。如果 gap 来自 outcome-bearing subject text,B 对；如果来自纯模板/非交易文本,A 更宽。 | 两者都能解释,但解释的对象不同。 |
| `E_CMMD` | P_predict 跨模型 cutoff-monotone 方向分歧 | **中**。熟悉 target-family 可能影响方向 prior,但 outcome link 弱。 | **强**。晚 cutoff 有更多 outcome memory,方向分歧正是预期。 | B 更贴 β3 leakage。 |
| `E_FO` | 假结果下是否回到真实 outcome / direction | **弱到中**。A 只能说熟悉文本或模板让模型抵抗扰动,但不能说明为什么回到真实 outcome。 | **强**。这是 B 的核心路径:可交易 historical rows 才能提供 outcome memory。 | 若 `E_FO` lift 是主信号,A 有 conceptual gap。 |
| `E_NoOp` | 无关插入是否扰动预测 / brittle template matching | **中到强**。模板和 repeated surface pattern 很相关。 | **中**。outcome-bearing repeated rows 也可产生 cached response,但 NoOp 本身更像模板脆弱性。 | A 更自然；B 仍可解释 outcome-cache 稳定性/脆弱性。 |

覆盖总结:

- A 覆盖 surface/logprob 类最强:`E_CTS`, `E_PCSG`, `E_NoOp`。
- B 覆盖 outcome/behavior 类最强:`E_FO`, `E_CMMD`。
- `E_PCSG` 和 `E_CTS` 两边都覆盖,但 A 问的是“模型是否熟悉这类文本”,B 问的是“模型是否熟悉这类 outcome-bearing 文本”。
- 对本项目的主 β3 叙事来说,`E_FO` 和 `E_CMMD` 的解释权更关键,因为 proposal 的泄露定义是模型用训练后已知信息影响方向预测,不是只说文本 surprise 变低。

### 关键 sanity-check

如果 R-1b 选 A,但 β3 主要通过 `E_FO` lift:

有 conceptual gap。A 的 recurrence_count 包含一批不能产生 actionable market outcome 的 historical rows。若 `E_FO` 显著,我们会想解释为“重复历史 outcome-bearing cases 让模型更容易回到真实 outcome”。但 A 的分母里混入了上市前、停牌期、退市过渡等 rows,这些 rows 至多解释文本熟悉和模板熟悉,不能直接解释 outcome recall。这样 β3 的变量名是 exposure,结果解释却是 outcome leakage,中间少一环。

如果 R-1b 选 B,Carlini 2023 anchor 还成立吗:

成立,但降级为机制锚点,不是完整 construct anchor。Carlini 支持“重复文本更容易被模型记住/抽取”,它当然也支持 tradable subject rows 内部的重复频次。B 承认 non-tradable rows 也可能被记住,只是认为那不是 R-1b 主 Recurrence 想测的 outcome-leakage 剂量。B 不是反驳 Carlini,而是给 Carlini 的 text-frequency law 加一个金融任务层的 outcome-bearing filter。

### 实证 sanity-check: non-tradable subject row 占比与 A/B count 差

当前仓库没有已经生成的 L2 subject table,也没有可直接读取的 `tradable_at_event` 成品列。因此现在不能给真实的:

`sum(is_subject=true and tradable_at_event=false) / sum(is_subject=true)`

我做了一个只能判断数量级的原始 CLS 文本 proxy。方法:扫描 `data/cls_telegraph_raw` 的 1,207,243 篇原始 CLS article,用非交易相关触发词统计 article-level 命中。触发词组包括:

- halt/suspend: 停牌、临时停牌、继续停牌、暂停交易、暂停上市等。
- delist: 退市、终止上市、摘牌、退市整理等。
- pre-listing/IPO: 拟上市、上市申请、上市辅导、首次公开发行、IPO、新股申购、过会、提交注册、注册生效、招股等。
- listing-day: 上市首日、登陆 A 股、今日上市、明日上市等。

结果:

| Proxy 口径 | 命中篇数 | 占 raw CLS articles |
|---|---:|---:|
| 任一非交易相关触发词 union | 35,187 / 1,207,243 | 2.9147% |
| halt/suspend | 6,242 | 0.5170% |
| delist | 8,484 | 0.7028% |
| pre-listing/IPO | 20,460 | 1.6948% |
| listing-day | 1,599 | 0.1325% |

另一个较小的 `data/pilot/cutoff_probe/probe_set_monthly60_36mo.json` proxy 是 60 / 2,160 = 2.78%。这和 raw proxy 同量级。

解释边界很重要:

- 这不是 L2 subject row 的真实 non-tradable 占比。它没有 entity match,没有 subject ID,没有 point-in-time tradability join。
- 它可能高估,因为“退市风险”“IPO 过会率”“涉及拟上市企业”等文章不一定对应 benchmark target subject。
- 它也可能低估,因为真正的 `tradable_at_event=false` 还包括 price-limit/停复牌细节、上市日期边界、证券主数据有效期等触发词看不到的情况。
- 但作为数量级 sanity-check,raw CLS 中这类文本大概是 3% 左右,看起来 A 和 B 的 reference count 差值很可能小于 5%。真实差值仍必须等 B-2 生成 L2 后计算。

如果实证差 < 5%,选 A 还是 B 还重要吗:

重要。小差值会让 effect estimate 数值接近,但 construct label 和 reviewer defense 不一样。A 的论文句子是“Recurrence 是 text exposure density”；B 的论文句子是“Recurrence 是 outcome-bearing family recurrence”。如果主结果由 `E_FO` 或 `E_CMMD` lift 支撑,B 的解释闭环更短、更少需要补丁。既然实现成本几乎为零,L2 已有 `tradable_at_event`,没有理由为了 3% 左右的 surface exposure 保留一个会让 outcome-leakage 解释变松的口径。

### 独立选择

我选择 **B 立场: outcome-leakage proxy**。

一句话主理由: **R-1b Recurrence 的主用途是解释 `Cutoff Exposure × Recurrence -> leakage` 的 β3,而这个 leakage 在本项目里是 outcome/direction leakage,不是一般文本熟悉度；所以 reference rows 必须是能产生可验证 market outcome 的 tradable subject rows。**

## 阶段 2 对照

### 上一轮 validity 派论证关键句引述

引用: "主选：**L2 subject construct**。也就是 recurrence count 的基本单位是 reference window 内满足 `is_subject=true` 的 `(article_id, target_entity_id)` row，不按 `tradable_at_event` 过滤。"

引用: "我独立站在 **validity 派**：tradable mention / tradable subject 是一个工程上可做、审计上清楚的口径，但不该作为 R-1b 主 construct。"

引用: "这个论证在 sampling admissibility 上是对的，但它不应外推到 recurrence。case admissibility 解决的是“能不能把这个 target 放进预测 prompt”；recurrence 解决的是“模型训练时可能看过多少同类文本”。"

引用: "模型训练文本里没有一个显式字段告诉它“这家公司当时可交易”。如果某公司在上市前、停牌期、非交易状态下被 CLS 多次作为主体报道，这些文本仍然可能进入模型训练，并且仍然可能形成实体和事件模式的记忆。"

引用: "所以我的判决是：**tradability 是 case 主体 admissibility 的必要条件，不是 recurrence exposure proxy 的必要条件**。"

引用: "**L2 subject + tradable sensitivity 不建议默认做**：它会触发 Pool D / schema 复杂度，却不清楚回答哪个更好的科学问题。"

### stress-test 下经得起 outcome-leakage framing 反驳吗

经不起。上一轮论证只在 A 的前提下成立:Recurrence 已被定义为 pure exposure proxy,所以 `tradable_at_event` 看起来像把 sampling admissibility 外推到 factor metric。

但这次 meta-question 正是在问这个前提是否对。如果 Recurrence 是 outcome-leakage proxy,那么 reference rows 与 case 主体使用同一 `tradable_at_event=true` 口径不是 admissibility 越界,而是 construct 的内在一致性。原因很简单:只有 tradable subject rows 才天然有可计算的 T+1/T+5 或其他 horizon realized outcome,也才有资格成为“模型可能记住 outcome/direction”的历史重复样本。

上一轮 validity 派论证的盲点有三层:

1. 它把“训练文本里没有 tradable 字段”误当成排除 tradable filter 的充分理由。模型不需要看到一个显式 tradable 字段；只要事件发生时有市场价格路径,训练语料和后续报道就可能提供 outcome/direction association。
2. 它把 `tradable_at_event` 只理解为 prompt admissibility。事实上,在 outcome-leakage framing 下,它也是 outcome existence filter。
3. 它没有检查 `E_FO` 和 `E_CMMD` 的 driver。如果主 β3 信号来自这些 outcome-driven estimands,unfiltered recurrence 会把 text exposure 和 outcome-bearing repetition 混在同一个变量里。

还有一个工程错误需要修正:上一轮说 L2 subject + tradable "会触发 Pool D / schema 复杂度"。这对 L1 mention + tradable 可能成立,但对 L2 subject + `tradable_at_event=true` 不成立。R-0 L2 required column 已经包含 `tradable_at_event`;这个 filter 是 L2/L3 view 组合,不需要给 L1 加字段,也不需要 Pool D extension。

### 表态:推翻

我推翻上一轮 (a) 段的 reference-row filter 结论。

我上一轮错在:把 Recurrence 默认定成“模型训练时见过多少同类文本”的 pure exposure factor,然后用这个默认去 reject tradable construct。这个判断没有正面回答本项目 β3 的 outcome-leakage driver。若 Recurrence 的角色是放大 Cutoff Exposure 带来的泄露,那么它应该数 outcome-bearing repetition,不是所有 subject text repetition。

新主选:

`L2 subject rows + tradable_at_event=true`

也就是:

```text
recurrence_count(case i) =
  count of reference rows r in fixed reference window
  where r.target_entity_id == i.target_entity_id
    and r.event_super_type == i.event_super_type
    and r.is_subject == true
    and r.tradable_at_event == true
    and r.article_id != i.article_id
```

保留上一轮已锁、不在本 stress-test scope 的部分:

- row unit 基础仍是 L2 subject,不回 L1 mention。
- family granularity 仍是 `target_entity_id × event_super_type`。
- window 仍是 fixed `[CLS corpus start, earliest fleet cutoff)`。
- `log1p`, 0 合法, focal article exclusion, no-dedup 原则不变。

## 最终 lock-in

### 主 construct

**L2 subject + `tradable_at_event=true` reference rows**。

### 一句话主理由

**Recurrence 在本项目主模型里的工作是 outcome-leakage 剂量,不是纯 text exposure 剂量；`tradable_at_event=true` 是 outcome-bearing reference row 的必要条件。**

### 对 R-1b 主报告 (a) 段的具体修订指令

只修 (a) Construct 段；(b)/(c)/(d)/(e)/(f)/(g)/(h) 是否同步由用户和 CC 决定。

1. `候选清单与 trade-off` 表:

   - `L2 subject` 行的阶段 1 判断从 `主选` 改为 `不选为主 construct: 只覆盖 pure exposure,与 outcome-leakage β3 有 gap`。
   - `L3 = L2 + 当时可交易` 行改写为:

```markdown
| L2 subject + `tradable_at_event=true` | 主体口径干净；reference rows 与 outcome-leakage construct 同口径；只数有可验证 market outcome 的历史 target-family rows；L2 schema 已有字段,不触发 Pool D | 会漏掉 non-tradable text exposure,因此不是最宽的 Carlini-style surface exposure proxy | **主选** |
```

   - 删除或修正原表里 `L3 = L2 + 当时可交易` 的 "触发 Pool D" 问题；L2 tradable filter 不触发 Pool D。

2. `主选` 小节:

   - 原句:

```markdown
主选：**L2 subject construct**。也就是 recurrence count 的基本单位是 reference window 内满足 `is_subject=true` 的 `(article_id, target_entity_id)` row，不按 `tradable_at_event` 过滤。
```

   - 改为:

```markdown
主选：**L2 subject + `tradable_at_event=true` construct**。也就是 recurrence count 的基本单位是 reference window 内满足 `is_subject=true` 且 `tradable_at_event=true` 的 `(article_id, target_entity_id)` row。
```

3. `理由链` 小节:

   - 保留原第 1-2 点关于 L2 subject 区分 mention/salience 的论证。
   - 原第 3 点 `L2 subject 不需要激活 Pool D` 改为:

```markdown
3. L2 subject + tradable 不需要激活 Pool D。R-0 已要求 L2 有 `tradable_at_event` 字段；这里是在 L2/L3 view 上加 reference-row filter,不是给 L1 增加 tradability。
```

   - 新增一条:

```markdown
4. Recurrence 的主统计角色是 `Cutoff Exposure × Recurrence -> leakage`。如果 leakage 的物理 driver 是 outcome/direction memory,reference rows 必须是 outcome-bearing rows；在 A 股 CLS 中,`tradable_at_event=true` 已足以保证存在可计算 market outcome。
```

   - 原第 4 点与 R-1c 拉开距离可保留,编号顺延。

4. `tradable construct 的哲学判决` 整段替换:

   - 删除原核心判句:

```markdown
tradability 是 case 主体 admissibility 的必要条件，不是 recurrence exposure proxy 的必要条件
```

   - 替换为:

```markdown
本轮 stress-test 后改判：R-1b 主 Recurrence 不是 pure exposure proxy,而是 outcome-leakage proxy。Tradability 对 case 主体当然是 admissibility 条件,但对 reference rows 也是 outcome-bearing 条件。Non-tradable subject rows 仍可能贡献 surface/text memorization,但不能提供同一意义上的 market outcome memory；把它们计入主 recurrence 会让 `E_FO` / `E_CMMD` 上的 β3 lift 难以解释。因此主 construct 使用 L2 subject rows filtered by `tradable_at_event=true`。
```

5. `替代方案与何时换` 小节:

   - 删除:

```markdown
**L2 subject + tradable sensitivity 不建议默认做**
```

   - 改为:

```markdown
Unfiltered L2 subject 不再作为 R-1b 主 construct,也不默认放入 robustness。它回答的是另一个问题: pure surface/text exposure 是否有信号。除非未来明确另开 surface-exposure factor,否则不在本轮 R-1b primary 口径中保留。
```

6. `兼容性 check` 小节:

   - `R-0` bullet 改成:

```markdown
- R-0：仍在 L2/L3 container 内计算 factor；使用 L2 已有 `tradable_at_event` 字段,不新增层,不触发 L1 tradability / Pool D extension。
```

   - `下游` bullet 改成:

```markdown
- 下游：R-5 Pool G 使用 tradable-filtered L2-subject recurrence 分层；B-2 只需记录 reference_rows_filter。
```

7. `留给下游` 小节:

   - 增加:

```markdown
- B-2 需在 provenance 中记录 `reference_rows_filter = is_subject_true AND tradable_at_event_true`。
- B-2/L2 完成后报告 A vs B count delta: `n_L2_subject_unfiltered`, `n_L2_subject_tradable`, `share_nontradable_subject_reference_rows`。
```

### Signal verdict

stress-test verdict: **推翻改 B 立场 (tradable-filtered)**。关键 insight:上一轮 validity 派论证预设了 Recurrence 是 pure exposure proxy；在本项目 β3 的 outcome-leakage framing 下,`tradable_at_event=true` 是 reference rows 的 outcome-bearing 条件,不是 admissibility 越界。
