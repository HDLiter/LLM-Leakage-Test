# R-1b Historical Family Recurrence 白板分析

生成时间：2026-05-24

方法：clean-room-first。阶段 1 只使用 R-1b kickoff 指定的阶段 1 输入来独立推导；阶段 2 再对照 WS0.5 旧 memo、reviewer 决策链、walkthrough 提议与 R-0 原报告。

---

> ## ⚠ STATUS (2026-05-24): R-1b LOCKED — canonical = `R1b_DECISIONS.md`(同目录)
>
> 本文件是 Codex Pass A 主白板 + 后续 stress-test / dual-model 审查的 **audit trail**。下游 agent 与所有需要 R-1b 当前 lock-in 状态的引用,**应只读 `R1b_DECISIONS.md`**(time-static 决策清单)。本文件正文(尤其各段 trade-off 推导)可能与最终 lock-in 不一致,以 DECISIONS.md 为准。
>
> 同目录其它 audit trail 文件:`construct_stress_test.md`、`construct_second_opinion_claude.md`、`bch_second_opinion_claude.md`。

## 阶段 1 白板结论

### (a) Construct：数哪一层 row

> **2026-05-24 stress-test 改判**：本段在 R-1b 主白板之后做了一轮专项
> stress-test（`construct_stress_test.md`），meta-question 是 Recurrence
> 究竟是 pure text exposure proxy 还是 outcome-leakage proxy。Codex 推翻
> 主白板 (a) 段的 validity 派论证，把主 construct 从 unfiltered L2
> subject 改为 **L2 subject + `tradable_at_event=true`**。下文是 stress-
> test 后的最终版。

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 阶段 1 判断 |
|---|---|---|---|
| L1 mention | 最接近“模型读到过这个名字”的宽口径曝光；不用 subject ID；保留顺带提及、bundle、转发、追踪 | 顺带提及经常不是“标的 × 事件家族”；如果文章主体是别的公司，给所有被顺带点名的股票套同一个事件类型会很吵；会更像 Target Salience | 可作为 robustness / appendix，不适合主选 |
| L2 subject (unfiltered) | 只数 target 是文章主体的 `(article, target)` row；更接近“这只股票发生了这类事”的重复曝光；与 Pool B case row 口径自然相邻；不触发架构扩展 | 会漏掉模型确实看过的弱曝光；依赖 subject ID 质量；只覆盖 pure exposure，与 outcome-leakage β3 有 gap | **不选为主 construct**（stress-test 改判） |
| L3 = L1 + 当时可交易 | case admissibility 与 recurrence 同口径；排除非交易标的的 mention | 把上市生命周期混进 recurrence；触发 Pool D（给 L1 加 `tradable_at_event` 列） | 不选 |
| **L2 subject + `tradable_at_event=true`** | 主体口径干净；reference rows 与 outcome-leakage construct 同口径；只数有可验证 market outcome 的历史 target-family rows；L2 schema 已有字段，不触发 Pool D | 会漏掉 non-tradable text exposure，因此不是最宽的 Carlini-style surface exposure proxy | **主选**（stress-test 改判） |

#### 主选

主选：**L2 subject + `tradable_at_event=true` construct**。也就是 recurrence count 的基本单位是 reference window 内满足 `is_subject=true` 且 `tradable_at_event=true` 的 `(article_id, target_entity_id)` row。

理由链：

1. R-1b 要测的是“某个标的在某类事件里反复出现”对记忆的影响，不是“名字出现过多少次”。  
   只要文章主体不是该 target，事件类型往往描述的是别的经济主体。把这种顺带提及计入 target 的 event family，会把 recurrence 变成一个很宽、很嘈杂的 salience proxy。
2. L2 subject 正好保留“target 是这篇文章的中心经济 actor”这一点。  
   对金融新闻来说，模型更可能从这种 row 学到“贵州茅台 × 业绩/监管/经营事件”这种可复用模式。
3. L2 subject + tradable 不需要激活 Pool D。R-0 已要求 L2 有 `tradable_at_event` 字段；这里是在 L2/L3 view 上加 reference-row filter，不是给 L1 增加 tradability。
4. Recurrence 的主统计角色是 `Cutoff Exposure × Recurrence -> leakage`。如果 leakage 的物理 driver 是 outcome/direction memory，reference rows 必须是 outcome-bearing rows；在 A 股 CLS 中，`tradable_at_event=true` 已足以保证存在可计算 market outcome（T+1/T+5/任意 horizon 真实收益均可算方向），不依赖 R-6 落定 outcome-verifiable schema。
5. 它和 R-1c Target Salience 拉开距离。  
   R-1c 很可能会关心 all-event mention / coverage；R-1b 主选如果也用 L1 mention all-event，会让两个因子高度重叠。

#### tradable construct 的哲学判决（2026-05-24 stress-test 后改判）

本轮 stress-test 后改判：R-1b 主 Recurrence 不是 pure exposure proxy，而是 outcome-leakage proxy。Tradability 对 case 主体当然是 admissibility 条件，但对 reference rows 也是 outcome-bearing 条件。Non-tradable subject rows 仍可能贡献 surface/text memorization，但不能提供同一意义上的 market outcome memory；把它们计入主 recurrence 会让 `E_FO` / `E_CMMD` 上的 β3 lift 难以解释。因此主 construct 使用 L2 subject rows filtered by `tradable_at_event=true`。

stress-test 完整论证见 `refine-logs/reviews/REOPEN_R1_R6/R1b_recurrence/construct_stress_test.md`（含 5 estimand × 两立场 driver 链覆盖矩阵、上一轮 validity 派论证的三层盲点剖析、A vs B count 实证 sanity-check ~2.91% non-tradable 触发词命中）。

#### 替代方案与何时换

1. **L1 mention robustness / appendix**：如果 pilot 发现 L2 subject 太稀疏，或者 subject ID 质量审计显示噪声高，可以在 appendix 报 L1 mention 版本。它回答的是“宽曝光是否也有信号”，不是主 construct。
2. **Unfiltered L2 subject 不再作为 R-1b 主 construct，也不默认放入 robustness**。它回答的是另一个问题：pure surface/text exposure 是否有信号。除非未来明确另开 surface-exposure factor，否则不在本轮 R-1b primary 口径中保留。

#### 兼容性 check

- R-0：仍在 L2/L3 container 内计算 factor；使用 L2 已有 `tradable_at_event` 字段，不新增层，不触发 L1 tradability / Pool D extension。
- R-4a：是 case-level continuous factor，`log1p(0)=0` 合法；不依赖 operator 输出。
- 下游：R-5 Pool G 使用 tradable-filtered L2-subject recurrence 分层；B-2 只需记录 reference_rows_filter。

#### 留给下游

- B-2 仍需决定 subject ID 的具体实现和审计字段。
- B-2 需在 provenance 中记录 `reference_rows_filter = is_subject_true AND tradable_at_event_true`。
- B-2/L2 完成后报告 A vs B count delta：`n_L2_subject_unfiltered`、`n_L2_subject_tradable`、`share_nontradable_subject_reference_rows`。
- R-5 仍可独立决定是否用 recurrence stratified Pool G。
- R-1c 不被迫继承 L2 subject + tradable filter；Salience 可以独立选 L1 / L2 / denominator / 是否同样加 tradable filter。

### (b) Family granularity：主键轴 × 事件折叠轴

#### 主键轴独立推导

| 主键 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| 单标的 | 直接对应 case target；最接近 identity-keyed memorization；和 C_anon / Target Salience 的解释链清楚 | 对冷门股票会稀疏，0 值多 | **主选** |
| 一级行业 | 稀疏性低；能测行业模板曝光 | 从“这只股票反复出现”滑到“这个行业经常出现”；更像行业先验 / reasoning template，不是 target recurrence | 不做主选 |
| 二级行业 | 比一级行业细，仍能缓解稀疏 | 行业 taxonomy 复杂且会变化；仍然不是 case target 的直接重复曝光 | 不做主选 |
| 概念板块 / 指数 / 市值 / 实控人等 | 可能捕捉金融市场真实分组 | 需要额外 point-in-time 数据、版本化和解释；对 R-1b 是过度工程 | 不选 |

主键轴主选：**单标的 `target_entity_id`**。

理由是 recurrence 的最强文献锚点来自训练数据重复频次：同一或相近文本模式被模型多次看见，更容易被记住。对本 benchmark 来说，最强 cue 是 case 的具体 target，而不是行业。行业级 exposure 当然可能影响模型判断，但那更像“行业知识 / 模板熟悉度”，不是“这个 target 的历史家族复现”。

#### 事件折叠轴独立推导

| 事件折叠 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| 不切事件 | 简单、稳定、少稀疏 | 基本退化成 target coverage / salience；很难说是“事件家族 recurrence” | 不做主选 |
| 5 大事件超类 | 保留“同类事件”的含义；比 13 类稳；能和 Target Salience 拉开距离 | 比 raw type 粗，会把同一超类下不同机制合并 | **主选** |
| 13 类原始事件类型 | 语义最细；最贴近具体事件 | 稀疏、分类误差更敏感、pilot N=780 下不稳 | robustness / appendix |
| 其它折叠 | 可按 pilot 调整 | 容易变成追数据调参 | 不选 |

事件轴主选：**按 Scheme A 的 5 大事件超类折叠**。

#### 组合候选

| 组合 | 定位 | 判断 |
|---|---|---|
| `target_entity_id × event_super_type` | “同一标的 + 同一粗事件家族”的历史主体复现 | **primary 推荐** |
| `target_entity_id × raw_event_type` | 更细事件族复现 | robustness / appendix；前提是 pilot 分布不过度稀疏 |
| `target_entity_id` all-event | 身份级历史覆盖 | 不作为 Recurrence primary；更接近 R-1c Salience，可作 discriminant / collinearity 诊断 |
| `industry_level_1 × event_super_type` | 行业模板曝光 | appendix 诊断即可；不建议进入 primary |

#### 主选

主选：**L2 subject rows 上的 `target_entity_id × event_super_type` count**，进入模型时用 `log1p(recurrence_count)`。

这组组合在三个方向上最小可辩护：

1. 不选行业级，因为行业级把 entity memory 和行业先验混在一起。
2. 不选 all-event，因为 all-event 会和 Target Salience 打架。
3. 不选 13 raw type 做主选，因为 pilot 和 main run 的目标是稳定刻画，不是把 event taxonomy 切到最细。

#### 替代方案与何时换

- **raw 13 type robustness**：如果 B-2 topic-classifier 的 13 类质量足够，且 pilot 中 `target × raw_type` 的非零比例不塌，可以放 robustness 或 appendix。
- **target-only all-event diagnostic**：只用于检查 Recurrence 与 Salience 的相关性，不作为 R-1b 的替代 primary。

#### 兼容性 check

- R-0：topic-classify 范围由 R-1b family 决定；本方案只要求 entity-first 后给相关 L1/L2 rows 标 `event_super_type`。
- R-4a：多档 robustness 不需要 family-wise correction；主报 per-estimand effect size + 95% CI。
- 下游：0 recurrence cases 不剔除；`log1p(0)=0` 直接进 R-4b power 和 R-1e pilot effect 评估。

#### 留给下游

- B-2 需要固定 V3 13-class → Scheme A 5-supertype 映射 hash。
- R-1e 根据 pilot 决定 Recurrence 是否进入 primary，而不是 R-1b 预先保证。
- R-5 如果用 Pool G，建议在 `event_super_type` 内做 recurrence 分层，避免只是抽到某些事件类。

### (c) Lookup window：窗口范式与长度

#### 候选清单与 trade-off

| 范式 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| 固定窗口：CLS 起点 → 全队最早 cutoff | case-independent；保持 Recurrence 是 case-level factor；最像“所有模型至少可能共同见过的 CLS 历史曝光”；不把 case 发布日热度混进 metric | 低估晚 cutoff 模型能见到的 CLS exposure；对早年 case 会包含 case 发布后的同家族报道 | **主选** |
| case-relative rolling window：case 发布前 X 天 | 每个 case 窗口长度一致；直觉上像“事件发生前的历史” | 混入 case 发布时点和市场热度；post-cutoff case 会查到模型没见过的 2025/2026 语料；偏离训练曝光 proxy | 不选 |
| per-model pre-cutoff window | 理论上最贴近每个模型自己的 cutoff | 把 Recurrence 变成 case×model；与 Cutoff Exposure 机械缠在一起；工程和解释都更重 | 不选主选 |
| 时间衰减 / 多窗口网格 | 可以看短期热度 vs 长期曝光 | 对 R-1b 是过度工程；容易把 factor 设计变成调参 | 不选 |

#### 哲学含义判断

我把 R-1b Recurrence 定义成 **CLS 历史训练曝光 proxy**，不是“case 发生前市场上有多热”的 proxy。

因此主窗口应该尽量像训练语料里的累计重复频次。Carlini 等重复频次 scaling 的直觉是：训练集中相同或相近模式出现越多，模型越容易记住。这个直觉不要求这些重复都发生在 focal case 之前；它要求它们在模型训练 cutoff 前进入训练语料。

case-relative rolling window 看起来很自然，但它回答的是另一个问题：某个事件发生前，市场媒体最近是否反复报道同类东西。这会把 2024 年的市场热度、2021 年的冷清度、行业周期全混进 recurrence。对真实预测任务也许有意义，但对“模型训练曝光”不是最干净的 proxy。

per-model window 在哲学上最接近“各模型实际 pre-cutoff exposure”，但在这个 benchmark 里不值得作为主选。R-4a/R-1b 下游明确需要一个 case-level continuous recurrence 来和 Cutoff Exposure 做交互；如果 recurrence 也变成 case×model，解释会变成“晚 cutoff 模型既 exposure 更高、recurrence window 也更长”，两个因子互相咬住。

#### 主选

主选：**固定参考窗口**。

定义：

- `reference_window_start = CLS S0 corpus first available published_at`，预期为 2020 年初。
- `reference_window_end = min(model_cutoff)`，用 `config/fleet/r5a_fleet.yaml` 锁定的全队最早 cutoff；预期约为 2024 年中。
- 窗口用半开区间：`[reference_window_start, reference_window_end)`。
- recurrence count 对每个 focal case 使用同一个 reference window。
- 若 focal case 的 `article_id` 本身落在 reference window 内，**排除 focal `article_id` 自身**，避免把“这篇文章自己”算成“历史复现”。其它 repost / follow-up 只要是不同 `article_id`，按 no-dedup 原则保留。

窗口长度就是 CLS 起点到最早 cutoff 的完整可用跨度，大约 4 年多。这里不再另选 90 / 365 / 1500 天，因为这些长度更像“近期热度”设计。R-1b 主问题是 cumulative exposure，full fixed window 是最小可辩护方案。

#### 数据约束 sanity-check

- CLS 从 2020 年初开始，最早 cutoff 约 2024 年中，所以 fixed window 有约 4 年参考历史，不是短到不可用。
- 晚 cutoff 模型 2024 下半年到 2025 下半年的额外 CLS exposure 会被低估；这是主选的已知保守代价。
- 这个代价比 case-relative rolling window 的混杂更可接受：rolling window 对 2026 post-cutoff negative control 会用到模型不可能见过的近年 CLS 文本，反而更偏离 exposure。
- 5 年 vs 6 年在当前数据边界下本来意义不大；主选被 earliest cutoff 卡住，不做触顶长度调参。

#### 兼容性 check

- R-0：factor metric 在 L2/L3 operators 前完成；window 只看 corpus metadata。
- R-4a：保持 case-level continuous value；`log1p(0)=0` 合法。
- 下游：R-4b power 只需 pilot 分布；R-5 Pool G 分层可以在 sampling 前算。

#### 留给下游

- R-1c 可继承该 fixed window，但不强制。
- B-2 需要在 provenance 里写明 window start/end、manifest hash、focal-article exclusion policy。
- R-1e 可在 pilot 后决定是否把短窗口作为 later robustness，但 R-1b 不预注册窗口网格。

### (d) 给 R-1c Target Salience 的锚点

R-1b 给 R-1c 的结论不是“照抄 Recurrence”，而是“共享容器，独立定义 salience”。

#### 必须共用

1. **R-0 四层容器**：S0 / L1 / L2 / L3 views，不新增层。
2. **entity-first pipeline**：先 entity match，再 topic / subject 等后续阶段。
3. **factor before operators**：Target Salience 不能依赖 P_predict / P_logprob / P_extract。
4. **0 合法**：如果是 count-based salience，`log1p(0)=0` 不能默认剔除。
5. **provenance discipline**：window、layer/view、alias/disambiguation、prompt/cache/hash 都要可审计。

#### 可继承但不强制

1. **Window**：R-1b 推荐 fixed window；R-1c 可以继承以便 Recurrence / Salience 可比，也可以独立选择。我的建议是 R-1c session 自决，但把 fixed window 作为强默认候选。
2. **主键轴**：R-1c primary 应该仍然是 target-level，因为它叫 Target Salience。可讨论 industry-normalized salience，但那是辅助口径，不应替代 target primary。
3. **log1p count transform**：如果 Salience 也是 count，继承 log1p 很自然，但 R-1c 可以选择 share / percentile / within-universe normalization。

#### 必须独立选择

1. **Construct**：R-1b 选 L2 subject，不代表 R-1c 必须 L2。Salience 常常更适合 L1 mention 或 unique article count，因为“被媒体提到”本身就是 salience。
2. **事件折叠**：R-1b 是 `target × event_super_type`；R-1c 一般应 all-event，不按 recurrence family 切。
3. **分母 / denominator**：R-1b 是 count，不需要分母。R-1c 如果定义成 share，就必须独立决定分母是 reference window article 数、L1 row 数、所有 target mentions、还是行业内 mentions。这个决定与 R-1b 相关但不能自动继承。
4. **与 Recurrence 的去重 / complement-family 处理**：如果 R-1c 想避免和 R-1b 高相关，可以讨论“all-event count minus focal event family count”等 complement 方案，但这必须由 R-1c 自己判断。

#### R-1c session 起跑清单

- 不要默认继承 R-1b 的 L2 subject construct。
- 可以把 R-1b fixed window 作为 baseline candidate。
- primary Salience 仍应 target-level，不建议用 industry-level 替代。
- denominator 是 R-1c 的核心问题，不能由 R-1b 代拍。
- R-1c 需要显式评估与 R-1b `log1p_recurrence_count` 的相关性 / VIF 风险。

### (e) Pool D 触发判断

阶段 1 主选是 **L2 subject、不过滤 `tradable_at_event` 的 recurrence construct**，所以：

- **不触发 Pool D**。
- **不需要给 L1 加 `tradable_at_event`**。
- **Pool D 保持 dormant**。
- B-2 schema 不需要新增 L1 tradability 字段；保留 R-0 已要求的 `tradability master snapshot hash` 即可，因为 L2 / L3 admissibility 仍会用到它。

#### B-2 schema 建议字段

R-1b 主选要求 `factor_provenance.run_inputs.per_task.recurrence` 至少记录：

- `factor_name = historical_family_recurrence`
- `source_layer = L2_subject`
- `row_unit = [article_id, target_entity_id]`
- `count_unit = L2_subject_row`
- `reference_rows_filter = is_subject_true; no tradable_at_event filter`
- `family_key = [target_entity_id, event_super_type]`
- `event_scheme = Scheme_A_5_supertypes`
- `reference_window_start`
- `reference_window_end = min_fleet_model_cutoff`
- `window_interval_policy = half_open_start_inclusive_end_exclusive`
- `focal_article_policy = exclude_same_article_id`
- `dedup_policy = no_dedup_reference_rows`
- `zero_policy = keep_zero_log1p_zero`
- `transform = log1p`
- `topic_classify_scope = entity-first rows needed for L2 subject rows in reference window and candidate case rows; no full-CLS topic-first pass`
- hashes for S0 snapshot, alias table, disambiguation rules, topic classifier prompt/model/cache, subject ID prompt/model/cache or rule, layer/view definition, fleet cutoff manifest, and sampling manifest when relevant

#### R-5 note

If R-5 later chooses Pool G recurrence-stratified sampling, it can use this L2-subject `log1p_recurrence_count` directly. R-5 should sanity-check that low-recurrence / zero-recurrence rows remain represented and should not silently switch to a tradable-only recurrence denominator.

## 阶段 2 对照

### 1. 与 WS0.5 §5 现状的对照

#### 一致：fixed window、log1p、no-dedup、proxy 语言

WS0.5 §5 已经把 per-case `[T-24mo, T)` 窗口改成 `[corpus_start, earliest_model_cutoff)` fixed window。阶段 1 独立推导也得到同一个结论：R-1b 应测训练语料里的累计曝光 proxy，而不是 case 发生前的近期市场热度。

这里保留旧 §5 的四个点：

1. **fixed earliest-cutoff window 保留**。  
   它让 Recurrence 保持 case-level value，并保证参考窗口在所有模型 cutoff 之前。代价是低估晚 cutoff 模型曝光，但这是可解释的保守代价。
2. **`log1p(recurrence_count)` 保留**。  
   这是主变量；不做 percentile primary、不做 binary primary。
3. **no-dedup 保留**。  
   旧 §5 的 0.48% intra-day duplication probe 进一步支持阶段 1 的 no-dedup 判断。原报、转发、追踪和滚动快讯本身就是 exposure 的一部分。
4. **CLS proxy 语言保留**。  
   Recurrence 只能叫“pre-cutoff CLS family recurrence proxying training exposure”，不能写成模型真实训练语料曝光次数。

#### 冲突：mention-based construct 降级，subject construct 升为主选

旧 §5 的 primary 是 mention-based：只要 target / alias 在文章里出现并匹配 super_type，就计数。

阶段 1 与它冲突，并且我坚持阶段 1：**主 construct 改为 L2 subject count**。

原因不是 mention 不能做，而是 mention 太宽。旧 §5 的例子口径会把“券商金股列表里顺带出现茅台”计入“茅台 × 某事件家族”的复现。这个 count 的确表示模型见过“茅台”这个字符串，但不稳定表示“茅台作为事件主体发生了这类事”。R-1b 的名字叫 Historical Family Recurrence，不是 Target Mention Frequency；主变量应该让 target-event 关系尽量清楚。

因此旧 §5 的 mention construct 处理如下：

- 不作为 primary。
- 可保留为 appendix / robustness：`L1 mention × target_entity_id × event_super_type`。
- 若 R-1c 选择 L1 mention salience，旧 mention count 更适合迁移到 R-1c，而不是留在 R-1b 主变量。

#### 冲突：full-CLS topic-first 不采纳

旧 §5 Phase R1 是 full CLS topic classification。R-0 已经把 entity-first pipeline 锁为上层架构，阶段 1 也继承这个约束。

最终 stance：**full-CLS topic-first 是旧 prototype 惯性，应废弃**。

B-2 应按 R-0 的 entity-first 顺序实现：

1. 先 entity match 得到 L1。
2. 做 subject ID 得到 L2。
3. 对 R-1b 所需范围做 topic-classify / event_super_type 标注。
4. 在 L2 subject rows 上按 `target_entity_id × event_super_type` count。

如果 B-2 为了支持 L1 mention robustness，需要对更宽的 L1 reference rows 标 topic，也可以做；但这应由 chosen robustness 决定，不应默认 full CLS。

#### 可采纳但属 B-2：deterministic alias / disambiguation

旧 §5 的 AKShare master alias、former name effective date、type compatibility、precision-first disambiguation方向是合理的。它不替 R-1b 选 construct，但可以作为 B-2 的实现资产。

需要更新的只是 count path 的对象：

- 旧 §5：confirmed mention matches。
- R-1b final：confirmed **subject** matches / L2 subject rows。

LLM alias smoke 可以保留为诊断或 tier-3 alias admission，不应成为 recurrence 主 count 的不透明步骤。

### 2. 与 frontmatter `revision_basis` 决策链的对照

#### 保留：C-2 的 fixed-window 方向

C-2 / user review 把 per-case 24mo window 改成 fixed pre-cutoff window。阶段 1 独立得到同一结论。

Verdict：**保留**。这不是 reviewer pile-on，而是对 construct 的正确修正。

#### 保留：C-3 的 continuous `log1p`

C-3 把 percentile / median split 从 confirmatory variable 中拿掉，保留 continuous `log1p(recurrence_count)`。阶段 1 独立同意。

Verdict：**保留**。重复频次的绝对量级才贴近 construct；percentile 适合抽样 bin 或诊断，不适合主 factor。

#### 保留：C-4 的 no-dedup primary，删除 dedup sensitivity 字段

C-4 起初引入 dedup sensitivity；后来 probe 显示 intra-day duplication 只有 0.48%，旧 §5 删除了 dedup sensitivity 字段。阶段 1 本身也认为 no-dedup 是合法 exposure。

Verdict：**保留最终简化版**。不恢复 `duplicate_ratio`、`recurrence_count_clustered`、`first_per_day` 等字段。

#### 保留：E-5 被 fixed window 溶解

E-5 曾要求 post-cutoff controls 的 recurrence 是 `null/not_applicable`。fixed window 后 recurrence 对 post-cutoff cases 也可计算，作为模型训练期 pattern familiarity covariate。

Verdict：**保留“所有 case 都计算 recurrence”**。这对 BL2 负对照也有用：post-cutoff outcome 不应被 recurrence 强预测。

#### 部分保留：E-6 deterministic-first entity pipeline

E-6 把 LLM disambiguation 从主路径拿掉，改成 deterministic master-data + precision-first rules。阶段 1 没深入 B-2 实现，但这个方向与最小可审计原则一致。

Verdict：**保留 deterministic-first；但 subject ID 是 B-2 独立实现问题**。不能因为旧 §5 的 mention pipeline 已有 R2-R4，就把 R-1b 主 construct 留在 mention。

#### Revert / 降级：v0.2 Issue #7 的 24mo、percentile、bin 稳定性链

v0.2 Issue #7 的旧合同包含 24mo window、within-super_type percentile、3-step entity matching、no-dedup。后来已被 C-2/C-3/C-4 大幅简化。

Verdict：

- 24mo：revert，不进 R-1b。
- percentile primary：revert，不进 R-1b。
- bin-stability / E-7 / S-5：revert，不进 R-1b。
- no-dedup：保留。
- entity matching：保留为 B-2 实现资产。

#### Revert：R-1c 必须共享 R-1b window 的旧锁法

frontmatter 记录 v0.4 曾把 Target Salience 与 Recurrence 共享 fixed window，说“两者只差 event-family filter”。阶段 1 对 R-1c 的判断更保守：R-1c 可以继承 fixed window，但不能被 R-1b 强制。

Verdict：**共享 window 是 R-1c 强默认候选，不是 R-1b lock-in**。R-1c session 必须自己决定 construct、denominator、是否 complement-family。

### 3. 与 walkthrough §A.1 / §A.2 的对照

#### A.1 四层 corpus framing

A.1 的用户提议把语料分成 full raw → A-share entity articles → subject articles → predictable/tradable articles。R-0 已经吸收为 S0 / L1 / L2 / L3 views。

阶段 1 与 A.1 的收敛点：

- entity-first 是对的。
- subject layer 是有必要的。
- predictable/tradable 不应是全局删除层，而应是 view / admissibility。

阶段 1 的不同点：

- R-1b recurrence 不进入 tradable/predictable layer。
- `tradable_at_event` 不作为 recurrence 主过滤条件。
- case sampling 可以从 Pool B 来，但 historical recurrence 的 reference rows 不必和 sampling admissibility 同口径。

Verdict：**A.1 的结构直觉保留；tradable layer 不升为 R-1b factor construct**。

#### A.2 subject-vs-mention construct shift

A.2 明确提出：Recurrence 从“mention density of `(target, family)`”改成“subject density of `(target, family)`”。阶段 1 在不读 A.2 正文前独立得出同一主选。

Verdict：**采纳 A.2 的 subject-only counting 作为 R-1b primary**。

这说明用户 walkthrough 当时抓到的是 construct validity 问题，不是单纯的成本优化。成本上 entity-first + subject-scope topic-classify 也更轻，但真正决定性理由是：subject row 更能表示 target-event pattern。

但 A.2 不能外推成：

- R-1c 也必须 subject-only；
- topic-classify 永远只跑 L2；
- L1 mention robustness 禁止；
- tradable subject 成为主 recurrence。

这些仍按各 session 自己的 construct 选择来定。

### 4. 与 R-0 Codex 主报告 §3 Pool 候选讨论的对照

R-0 原报告 §3 的作用是列 Pool A-I，并不替 R-1b/R-5 选 winner。阶段 2 后的 R-1b 结论与它的关系如下。

#### Pool B 仍是 case sampling base

R-1b 主 construct 是 L2 subject reference count；R-5 base pool 仍可保持 R-0 已锁的 Pool B：`L2 ∩ tradable_at_event ∩ text_length ∩ non-bundle`。

这不是矛盾。Pool B 决定“哪些 case 可以拿去问模型”；R-1b 决定“这些 case 的历史 exposure proxy 怎么算”。case 主体必须 tradable，是为了 prompt validity；历史 reference rows 不按 tradable 过滤，是为了 exposure proxy validity。

#### Pool D 不触发

R-0 原报告把 Pool D 写成 L1 mention + tradable_at_event，适合 supporting/robustness 或 C_anon-rich pool。阶段 1/2 的 R-1b 主选不需要这个扩展。

Verdict：**Pool D 保持 dormant**。它不是 ill-defined，也不是永远不能用；只是 R-1b primary 没有足够理由为它付复杂度成本。

#### Pool G 仍可用

R-0 原报告说 Pool G 是 salience / recurrence stratified distribution strategy。阶段 1/2 同意。

给 R-5 的具体 note：

- 若启用 Pool G，用最终 R-1b `log1p_recurrence_count` 分层。
- 分层最好在 `event_super_type` 内做，避免 recurrence bin 只是 event mix 的代理。
- 0-recurrence cases 必须保留。

### 5. 哪些旧 reviewer 推荐是“推对了”

以下推荐与阶段 1 独立结论收敛，应保留：

1. **C-2 / user review 的 fixed pre-cutoff window**：推对了。case-relative window 混入 case date 和市场热度，不适合作为主 exposure proxy。
2. **C-3 的 continuous log count**：推对了。不要 percentile / binary primary。
3. **C-4 最终 no-dedup 简化**：推对了。重复曝光本来就是 construct 的一部分；probe 进一步说明不需要 dedup machinery。
4. **E-5 溶解 post-cutoff null**：推对了。fixed window 后 post-cutoff cases 也能有 recurrence covariate。
5. **E-6 的 deterministic-first disambiguation**：方向对。主 factor pipeline 应优先可审计规则，LLM 放 smoke / user-reviewed alias tier。
6. **R-0 的 entity-first 架构**：推对了。full-CLS topic-first 是早期 prototype，不应保留。

### 6. 哪些旧链条是 reviewer pile-on 或 prototype 惯性，应 revert

1. **24mo rolling window**：revert。
2. **`recurrence_count_visible_to_model` / per-model censored sensitivity**：revert。主 factor 不变 case×model；Cutoff Exposure 已承担 cutoff 差异。
3. **percentile / median split / bin stability machinery**：revert。可有 sampling bin，不是主变量。
4. **dedup sensitivity fields**：revert。no-dedup primary 足够，probe 支持。
5. **full-CLS topic-classify first**：revert。entity-first 已锁。
6. **mention-based recurrence as primary**：revert 到 robustness / appendix；subject-based 升主选。
7. **R-1c 与 R-1b 强制共享 window/construct 的旧写法**：revert 成“可继承，R-1c 自决”。

## 最终综合推荐

| 决策点 | 最终选择 | 一句话理由 |
|---|---|---|
| (a) Construct | **L2 subject count；不按 `tradable_at_event` 过滤 reference rows** | Recurrence 要测 target-event 主体模式复现，不是宽 mention，也不是 admissibility 口径 |
| (b) Family 主键 | **单标的 `target_entity_id`** | identity-keyed memorization 最贴近 case-level leakage；行业级会滑向行业先验 |
| (b) Event 折叠 | **Scheme A 5 大 `event_super_type`** | 比 all-event 更像 event family，比 13 raw type 更稳 |
| (b) Primary family | **`target_entity_id × event_super_type`** | 最小可辩护地表达“同一标的 + 同类事件”的历史复现 |
| (c) Window | **fixed `[CLS corpus start, earliest fleet cutoff)`** | 保持 case-level exposure proxy，避免 case-relative 热度混杂 |
| (c) Focal article | **排除同一 `article_id` 自身** | 避免把 focal article 本身算成“历史复现”；其它不同 article follow-up 仍 no-dedup |
| (d) R-1c anchor | **共享容器，不强制继承 construct/window/denominator** | Salience 是独立因子，R-1b 只给强默认候选 |
| (e) Pool D | **不触发，保持 dormant** | 主选不需要 L1 tradability 扩展 |

主变量定义：

```text
recurrence_count(case) =
  count of L2 subject rows r in fixed reference window
  where r.target_entity_id == case.target_entity_id
    and r.event_super_type == case.event_super_type
    and r.article_id != case.article_id

log1p_recurrence_count(case) = log1p(recurrence_count(case))
```

Reference rows **不**加 `tradable_at_event=true` filter。0 合法，`log1p(0)=0`。

推荐标签：

- `target × event_super_type` L2 subject count：**primary candidate for R-1e / pilot evaluation**。
- `target × raw_event_type` L2 subject count：**robustness / appendix candidate**，前提是 pilot 不过度稀疏。
- L1 mention version：**appendix diagnostic only**，用于说明宽 exposure 是否改变方向。
- industry-level family：**不推荐进主报**；最多作为 later appendix “industry template exposure”诊断。

## 对下游的约束 / 留下的选择空间

### R-1c session input

必须共用：

- R-0 S0/L1/L2/L3 容器。
- entity-first pipeline。
- factor-before-operator 边界。
- count-based factor 的 0 值合法原则。
- provenance / layer-view hash discipline。

可继承但不强制：

- R-1b fixed `[corpus_start, earliest_cutoff)` window。
- target-level 主键。
- `log1p` transform。
- VIF / Pearson discriminant check against Recurrence。

必须独立选择：

- Salience construct：L1 mention、unique article count、L2 subject count、tradable-only count等。
- denominator：article 数、L1 row 数、all-target mentions、industry内 denominator，或是否根本不用 share。
- 是否 all-event、是否 complement-family、是否引入外部 salience proxy。

### B-2 implementation / `run_inputs.per_task`

R-1b 要求 B-2 至少固定这些字段：

```yaml
historical_family_recurrence:
  source_layer: L2_subject
  row_unit: [article_id, target_entity_id]
  count_unit: L2_subject_row
  reference_rows_filter:
    is_subject: true
    tradable_at_event: not_filtered
  family_key: [target_entity_id, event_super_type]
  event_scheme: Scheme_A_5_supertypes
  reference_window:
    start: cls_corpus_first_published_at
    end: min_fleet_model_cutoff
    interval: half_open
  focal_article_policy: exclude_same_article_id
  dedup_policy: no_dedup_reference_rows
  zero_policy: keep_zero_log1p_zero
  transform: log1p
  topic_classify_scope: entity_first_rows_needed_for_L2_subject_reference_and_candidate_rows
  requires_pool_d_or_l1_tradability_extension: false
```

Provenance hashes：

- S0 source snapshot hash。
- entity alias table hash。
- disambiguation rule hash。
- topic-classifier prompt / model / cache hash。
- subject-ID prompt / model / cache hash or deterministic rule hash。
- layer / view definition hash。
- fleet cutoff manifest hash。
- tradability master snapshot hash 仍按 R-0 全局保留，但不是 Recurrence reference filter。
- sampling manifest hash when factor values are tied to a sampled frame。

### Topic-classify 范围

主选不需要 full-CLS topic-classify。范围应由 B-2 按“最终要计算哪些 factor values”定：

- primary 至少覆盖 fixed reference window 内、entity match 后、可能成为 L2 subject 的 rows，以及 candidate case rows。
- 如果要报 L1 mention robustness，再扩到对应 L1 reference rows。
- 不为了旧 §5 惯性跑 full raw CLS topic-first。

### R-5 sampling

- Pool B base 不变。
- Pool D 不因 R-1b 触发。
- 若启用 Pool G，用最终 `log1p_recurrence_count` 做 recurrence stratification。
- 分层建议在 `event_super_type` 内做，并显式保留 low / zero recurrence cases。
- R-5 不应把 R-1b 的 reference count 偷换成 tradable-only count。

### R-4b power / R-1e factor finalization

Pilot 后给 R-4b / R-1e 的输入是：

- `recurrence_count`
- `log1p_recurrence_count`
- nonzero rate / zero rate
- distribution by `event_super_type`
- correlation / VIF against Target Salience and other factors
- optional robustness distributions for raw 13 type and L1 mention versions if computed

R-1b 不承诺 Recurrence 一定进 primary；R-1e 根据 pilot effect size、variance、collinearity 和 interpretability 决定。

### R-2

R-1b 不改变 R-2。扰动 eligibility 仍由 R-2/R-6 定，不从 Recurrence construct 推出。

## 留给用户拍板的开放点

严格说没有阻塞 R-1b lock-in 的开放点。若用户要显式拍板，只有三处：

1. 是否接受 **L2 subject** 取代旧 §5 mention-based primary。
2. 是否接受 R-1c 不被强制共享 R-1b window，而是自己 session 自决。
3. 是否需要计算 L1 mention robustness；我的建议是 appendix-only，若 B-2 成本高可以暂缓到 pilot 后。
