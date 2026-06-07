# R-1c Target Salience — clean-room whiteboard (Claude sub-agent)

> 这是 Claude sub-agent 在 clean-room-first 协议下,与 Codex 并行独立产出的白板分析。
> 阶段 1 只读 R-0/R-4a/R-1b DECISIONS 锁定内容 + RESEARCH_PROPOSAL + MEASUREMENT_FRAMEWORK
> + pending_items + worktable + Carlini 2023 + subfield_lit_scan。**未读** WS0.5 §3.3、
> WS0.5-era Codex Target Salience 旧提案、R-1b whiteboard 推导过程、CROSS_SYNTH §A.🟡-4(a)。
> 阶段 2 写完后再对照。

---

## 阶段 1 白板结论(8 个决策点,framing 在最前)

### (1) Framing / measurement claim —— Target Salience 测的到底是什么

**决策**:**Framing C — Corpus exposure intensity(显式承认 CLS 是 proxy)**。

#### 候选与 trade-off

| Framing | Claim | 我对它的判断 |
|---|---|---|
| A. CLS-内 prominence | "实体在 CLS 财经新闻里的曝光强度" | 太窄。一个 case-level continuous factor 若只 claim "CLS 内有多少 mention",与论文整体在测的"训练数据泄露"之间断了。β3(Salience × Cutoff Exposure)的可解释性就薄了 —— 读者会问"为什么 CLS 内 mention 应该 modulate cutoff 泄露",答不上来。 |
| **B. General fame / public attention** | "实体的公众知名度,用 CLS 作 financially-relevant 部分代理" | 野心大。若 main metric 只用 CLS 而 claim 是 "general fame",claim 与 metric 之间有真断层;补不上 cross-corpus 信号(百度搜索 / 维基 page view / 其它金融媒体)就是空头支票。R-1c 本 session 没有承诺建外部信号管线,B 是 over-claim。 |
| **C. Corpus exposure intensity (CLS 作 best-available proxy)** | "实体在模型预训练 corpus 里的累计曝光强度;CLS mention count 是手头能拿到的 best-available proxy" | 推荐。claim 与 metric 之间有一个**显式的、可论证的代理桥**:模型预训练用了 Common Crawl / 百科 / 公告 / 金融数据库 / 论坛 / CLS-like 财经源;CLS 是这些金融文本一类的实例。一个实体 CLS mention 越多,其在金融语料 / 媒体提及的整体强度越可能高,从而预训练曝光强度越可能高。这是**单调代理**(非线性精确,但方向一致),足以支撑 case-level continuous factor 的角色。 |

#### 决策理由链

1. R-1c 在论文里的角色是 confirmatory 因子之一,与 Cutoff Exposure 交互(β3),测"prominence-mediated memorization channel"。claim 必须能支撑这个角色。
2. claim 与 metric 之间的桥越短越好。A 的 claim 太窄不能支撑;B 的 claim 远超 metric。**C 是最小可辩护的中间路径**。
3. C 不需要 R-1c session 承诺 cross-corpus 管线;但留口子,稳健性段可挂外部信号(决策 8 会考虑)。
4. Carlini 2023 anchor 怎么处理:Carlini 测 training-data 内重复频次,我们测 proxy corpus 内 mention count。framing C 显式承认这个 gap,论文方法节需写一段:"CLS mention count 是 training-data 实际曝光的 monotone proxy,我们不 claim 严格 log-linear,只 claim 单调关系"。这就够了,不要硬把 Carlini 当 endorsement。

#### 后续 7 项被 framing C 怎样约束

- **(2) Construct**:framing 是 "exposure intensity",任何顺带提及都算 exposure → L1 mention 比 L2 subject 更贴。
- **(3) Family**:framing 不是 "事件家族关联记忆"(那是 R-1b),是 "整体 prominence" → target only 比 target × event 更贴。
- **(4) Denominator**:framing 不需要相对量(prominence 是绝对量,"全网络曝光强度";相对 share 反而引入分母噪音)→ count + log1p。
- **(5) Window**:framing 是 "model 预训练时见过多少",最干净的 cutoff-respecting 实现 = 与 R-1b 同窗口(`[corpus_start, min_cutoff)`)。case-relative 会引入 R-1b 早就排掉的 post-cutoff 倒灌。
- **(6) Tradable**:framing 与 tradable 正交。entity 出名不需要它当时上市(港股 / 美股 / 退市股都可能在 CLS 被反复提)。tradable filter 是 R-1b 因 outcome-leakage proxy 才加的,R-1c 没有这个理由 → **不加**。
- **(7) Discriminant**:framing 与 R-1b 不同 + construct / family / tradable 都不同 → 默认 VIF 应该自然不超阈;阈值沿用、fallback 用残差化即可。
- **(8) Robustness**:framing C 不强求外部 cross-corpus 信号(那是 framing B 的承诺);保持 R-1b 风格的 0 个 pre-commit。

#### 与下游需求的兼容性

- L4 estimand: Salience 是 case-level continuous,`log1p(0)=0` 合法 → β3 估计直接喂混合模型,framing C 不影响。
- R-1e / R-4b power: framing C 下 Salience 的 effect size 是"prominence 强度对 cutoff 泄露的放大量",pilot 数据估计起来与 framing 选择无关。
- R-5 sampling: framing C 不暗中 mandate sampling 策略(随机抽 / Pool G / Pool H 都能算 Salience);但 R-5 sanity check note 见 §最后一节。
- B-2 schema: framing C 决定 `factor_provenance.run_inputs.per_task.target_salience.claim = corpus_exposure_intensity_cls_proxy` 这一字段语义(具体字段名 B-2 决定)。
- WS0.5 §3.3 重写: framing C 是新基线,WS0.5 §3.3 必须以"CLS 是 proxy" 显式架桥写法重写,不再悬而未决。

#### 留给下游的选择空间

- B-2 字段命名 / 风格留 B-2。
- R-5 是否在 Pool G 上叠 Salience-stratified 分层留 R-5(R-1c 只提 sanity check input)。
- cross-corpus 外部信号(百度 / 维基)若团队后续愿意建,可以作为 R-1c 之后的 stretch-goal robustness paper subsection,不强求 R-1c session 承诺。

---

### (2) Construct —— Salience 计数数 R-0 容器哪一层

**决策**:**L1 mention**(`(article, target)` long-form row,不要求 `is_subject=true`,不要求 `tradable_at_event=true`)。

#### 候选与 Pool D 影响

| 候选 | 描述 | Pool D | 我对它的判断 |
|---|---|---|---|
| **L1 mention** | 任何 (article, target) pair 都算 | **不触发**(L1 不带 tradable 列,本 metric 也不需要) | **推荐**。最贴 framing C "exposure intensity"。 |
| L2 subject | 只数 `is_subject=true` | 不触发 | 与 R-1b 完全同基底 → 高 VIF 必然。即使能算,价值不大。 |
| L3 view = L1 + tradable | mention + 当时可交易 | **触发 Pool D 架构扩展** | 引入 Pool D 成本但 framing 不需要 tradable → 不合算。 |
| L3 view = L2 + tradable | subject + tradable(R-1b 完全同 construct) | 不触发 | metric 与 R-1b 完全同,VIF 接近 1 必然 → discriminant check 永远跑不出非冗余信号。 |

#### 决策理由链(核心张力 —— 必须正面表态)

两派最强论证:

- **"与 R-1b 同基底"派(L2 subject + tradable)**:metric 可比,discriminant check 在同分布上跑;construct 一致避免无谓 variance source。
- **"分家"派(L1 mention)**:Salience 与 Recurrence 测不同信号,construct 也应不同;L1 包含所有顺带提及,prominence claim 更贴 "见过多少" 而非 "被讲过多少"。

我选**分家派(L1 mention)**,理由:

1. **construct 同 base 会让 discriminant check 失去意义**。VIF 检查的目的是发现两个看似不同的因子是否实际测同一件事;如果 R-1c 一开始就和 R-1b 同 base,VIF 必然高(几乎是同一个 count 加 case 自己的那一行),根本无法做"这两个因子是否独立"的判断。R-1b 已锁同 base 的 L2 subject + tradable → R-1c 必须分家,VIF check 才有信息。
2. **framing C 决定 construct**。模型预训练时见 "茅台被顺带提了一句" 与 "茅台是文章主语" 都是 exposure。模型不会区分这两类。L1 mention 才符合 "exposure intensity"。L2 subject 是 outcome-leakage proxy 的 construct(R-1b 用它有意义,因为 outcome 关联记忆需要 subject 是核心经济主体)。
3. **Pool D 成本不必背**。L3 = L1 + tradable 触发 Pool D 架构扩展(R-0 §4 标 ⚠️),需要给 L1 candidate subset 加 `tradable_at_event` 列。这是真实的实现成本。L1 mention 不需要 tradable → 不触发 Pool D → 省一个架构扩展。

驳"分家"的反对论证("L1 包含 non-tradable target 的 mentions,与 R-1b 的 cohort 不一致,VIF 解读复杂"):VIF 解读的是 "这两个因子是否高度共线",不要求 cohort 一致。R-1b reference rows 是 L2 subject + tradable;R-1c metric 是 L1 mention(包含 non-tradable target、包含非 subject 的 mention)。两个 case-level 连续变量的 VIF 在同一个 case sample 上算,case sample 是 L3 base view(Pool B 子集,universal admissibility 已过)。**两个 metric 都是 case 的属性**,VIF 在 case 维度上算,与 reference rows 是哪个 cohort 无关。

#### 兼容性 check

- R-0 容器:L1 layer 是合法计数 base(R-0 §1)。L1 不带 tradable 列也是合法的(R-0 §1 显式锁)。✓
- R-4a:L1 metric 严在 operators 之前。✓
- R-1b 锁:R-1c 自决 construct,L1 mention 在 R-1b 选择空间内(R-1b §5.2 显式列 L2 subject 是 "参考")。✓
- R-1b §7.2 "显式不在 R-1b 范围内的 construct":有一条 "L1 mention(任何形式)若需 mention-based salience 留 R-1c session" —— 这正是 R-1b 把 L1 mention 留给 R-1c 的明示。✓

#### R-5 sampling 互动 sanity check

L1 mention count 与 sampling 的耦合:case sample 抽自 L3 base view(L2 subject + tradable + 其它 admissibility)。一个高 L1 mention 的实体不一定在 L3 base view 里有很多行 case 候选(它可能很多 mention 是非 subject)。**这反而是好事** —— L1 mention metric 的 case-level 值与 sampling 概率耦合更弱(相对 L2 subject 而言)。

但仍有耦合:高 prominence 实体在 L1 mention 多的同时,L2 subject 行也多 → case 候选多 → 在 random sample 里出现多。这是 Salience 与 sampling 的内在耦合,无法在 R-1c metric 选择层面完全消除;R-5 通过 Pool G stratified(R-1c metric 分层)或 Pool H entity-balanced 处理。**R-1c 只标 sanity-check note 给 R-5**,不替它决定。

#### 替代方案 / 何时换

若 pilot 显示 L1 mention 与 R-1b log1p_recurrence_count |r| > 0.90(尽管 construct 不同):触发 §决策 7 fallback。**但** L1 mention 与 L2 subject + tradable 的 count base 已经天然不同,经验上不应该出 VIF=10+。

#### 留给下游

- B-2: `factor_provenance.run_inputs.per_task.target_salience.source_layer = L1_mention`,`row_unit = (article_id, target_entity_id)`,`tradable_filter = false`(显式不加 tradable),`requires_pool_d_or_l1_tradability_extension = false`。
- topic-classify 范围:R-1c L1 mention 不依赖 super_type(决策 3 选 target only),所以 topic-classify 不需要扩到 candidate case rows 之外。R-1b 已锁 "只跑 entity-first 后的 reference rows + candidate case rows";R-1c 沿用,**不扩 topic-classify 范围**。

---

### (3) Family granularity / event collapse —— Salience 的 group-by 单位

**决策**:**target only**(单标的,所有 super_types 合并,不切事件)。

#### 候选与判断

| 候选 | 描述 | 我对它的判断 |
|---|---|---|
| **target only** | 同一标的所有 L1 mention 算一个 family | **推荐**。最贴 framing C "general prominence / exposure intensity"。 |
| target × complement-super_type | 同标的、case 自身 super_type 之外的 mention | 反直觉(茅台的财报新闻不算它的 prominence?)+ 复杂(还要拆 super_type)+ 与 framing C 不一致(framing 不是反 R-1b,是 general prominence)。 |
| target × 全 super_type + reweighting | 按 super_type 频率倒数加权 | 工程复杂,加权方案需说服 reviewer 不是 cherry-pick,得不偿失。 |
| target × 全 super_type(= target only) | 同 target only | 同 |
| target × super_type | 每个 super_type 单独算 | 与 R-1b family 维度同,VIF 必高,违反 framing C(把 prominence 切到 event-specific 没必要)。 |

#### 决策理由链

1. **framing C 决定 family**。"corpus exposure intensity" 是单标的层面的总曝光,不是事件-层面的关联曝光。target only 是 framing 的直接 operationalization。
2. **避免与 R-1b 重叠的反应不应该是过度拆分**。如果 R-1c construct 已经是 L1 mention(不同层),family 选 target only 就已经与 R-1b (`target × event_super_type` on L2 subject + tradable)有结构性区别。再加 complement-super_type 是 anti-overlap engineering 而非 framing-driven choice。
3. **R-1b §7.2 明示**:R-1b 把 "L1 mention" 与 "mention-based salience" 都留给 R-1c。R-1c 不需要在 family 维度再次反弹去构造 anti-overlap;construct 维度的分家已经够。
4. **target × complement-super_type 在反直觉处败下来**。若 case 自身 super_type 是 "财报",而 "茅台财报" 在 CLS 里出现 100 次,把这 100 次从 Salience 里剔掉,留下 "茅台" 在其它 4 个 super_type 里的 mention 作 "茅台的 Salience" —— 这测的不是茅台出名,测的是茅台**在其它事件里出名**。直觉上不对。

#### 已锁边界 check

- `log1p(0)=0` 合法(R-4a 锁):target only 不剔除 0-salience。✓
- 不做 family-wise multiplicity correction(R-4a 锁):target only 单 metric,无 family。✓
- discriminant check vs R-1b log1p_recurrence_count(R-1b §5.3):必须做,见决策 7。✓
- 标签语言 main / primary / supporting / robustness / appendix(R-4a 锁):决策 8 处理。✓

#### R-5 sampling 互动 sanity check

target only 下,高 prominence 实体的 L1 mention count 是其在 CLS 全局的出现总数。case sample 里高 prominence 实体出现频率高(它们的 L2 subject 行也多),Salience 值的分布会右偏。R-5 若用 Pool G stratified 可平衡。**R-1c 只标 note,不决定**。

#### 留给下游

- R-1d / R-1e:target only family 不约束 R-1d Template Rigidity 设计(它是 case-level 纯文本特征,与 target 维度无关)。R-1e 因子最终选择由 pilot 数据决定,target only 让 Salience 的 effect size 估计干净(没有不必要的事件维度分解)。
- B-2: `family_key = [target_entity_id]`,`event_collapse = none`(or `all_supertypes_merged`)。

---

### (4) Denominator —— count / share / log1p(count)

**决策**:**`log1p(target_mention_count)`**(裸 count + log1p transform,无分母)。

#### 候选与 trade-off

| 候选 | 公式 | 我对它的判断 |
|---|---|---|
| **count + log1p** | `log1p(target_mention_count_in_window)` | **推荐**。R-1b 同 transform。最简单。 |
| share (per-article) | `count / article_count_in_window` | 在固定窗口下,article count 是常数 → share 与 count 完全等价(差一个常数因子),log 后差一个常数。无信息增益。 |
| share (per-L1-row) | `count / L1_row_count_in_window` | 同上,L1_row_count 也是固定窗口下的常数。无信息增益。 |
| share (per-all-target-mentions) | `count / sum_over_all_targets(mention_count)` | 同上,分母也是常数。无信息增益。 |
| share (per-industry) | `count / sum_over_same_industry(mention_count)` | 不同实体的分母不同(实体属哪个行业)。但需要锁行业层级(一级 / 二级)、需要 ex-post 行业分类,引入新的依赖。framing C 是 "全局曝光",不是 "行业内相对"。不合算。 |
| rank / percentile | `rank(count) / N_targets` | 单调变换 + 抗尾,但破坏绝对量(框架里 `log1p(0)=0` 直接进模型就废了 —— 0 mention 实体的 percentile 不是 0)。与 R-4a 锁的 zero-policy 冲突。 |

#### 决策理由链

1. **R-1b 用 fixed window + 单标的 + log1p(count)**,denominator 在固定窗口下是常数。R-1c 用 fixed window + target only,同样情况:**任何 case-invariant 分母对 case-level metric 都是常数缩放**,log 后差一个 offset,**不影响系数估计的方向或显著性**,只影响绝对量级。
2. **rank / percentile 与 R-4a zero-policy 冲突**。`log1p(0)=0` 是合法值,任何 layer / window / construct 不剔除 0-salience cases(R-0 §5)。rank-based 变换让 0-salience 实体的 percentile 不再是 0(它们都映到某个尾部数字),破坏 zero-policy 的清晰语义。
3. **share-per-industry 引入 ex-post 行业分类依赖**,与 R-1b §7.2 显式排除 "一级 / 二级行业 grouping" 立场一致(虽然 R-1b 排的是 R-1b 自己的 grouping,但同样精神适用 R-1c —— 行业是 ex-post 后视镜分类)。
4. **log1p 的 transform 选择本身**:Carlini 2023 anchor 是 log-linear scaling(extraction rate vs duplication count),所以 log transform 是子领域 anchor 一致的选择。R-1b 也用 log1p。一致。
5. **没必要 ratchet 复杂度**。share / industry-internal / rank 都是 reviewer-可能-推 的方向,但在 framing C + fixed window + target only 下,它们都不提供额外 identifying variation。**最小可辩护 = count + log1p**。

#### 已锁边界 check

- `log1p(0) = 0` 合法(R-4a / R-0 §5):log1p 保留这个性质。✓
- no-dedup exposure 合法(R-0 §5):no-dedup 已是默认。

  注意 inter-article vs intra-article 区分:R-0 §5 锁 inter-article 多 articles 提到同 target 算多行;intra-article 同 article 多次提及只算一行(`mention_count_in_article` 是属性,不产生多行)。R-1c 的 L1 mention count = COUNT(L1 rows where target_entity_id = case.target_entity_id) within window。**这是 inter-article 计数**(每 article 一行)。intra-article 的 mention_count_in_article 是 article 内提及次数,R-1c 默认**不**乘进 count(否则就 over-weight 高 mention-per-article 的 article)。

  正面表态:**R-1c 用 article-level count**,不乘 `mention_count_in_article`。即 `target_mention_count = COUNT( L1 rows in window with target_entity_id = case.target_entity_id )`,每 article 贡献 ≤1(per L1 row unit)。这是 no-dedup-inter-article + de-duplicate-intra-article 的自然实现,与 R-0 §5 一致。
- article cluster 可追溯:L1 row 保留 article_id,Salience count 可后续按 cluster 调整(R-4b territory)。✓

#### 替代方案 / 何时换

若 pilot 显示 log1p(count) 分布过于右偏 / 出现 ceiling effect(极少数超高 prominence 实体把分布拉残):降为 log10 或 rank-based 是事后选项。但 R-1c session **不预 commit**;pilot 看了再说。R-4a 锁 "不锁因子数 / 实现细节是 pilot 后允许修订项",此 transform 调整属此类。

#### R-5 sampling 互动 sanity check

count 的尾分布会让 pilot 数据中少数高-Salience 实体支配高 effect-size region。如果 R-5 random sampling,高 prominence cases 多 → 高 Salience case 多 → effect size 估计可能被少数大公司主导。Pool G stratified by Salience(若 R-5 启用)可平衡。**R-1c 标 note**。

#### 留给下游

- B-2: `transform = log1p`, `denominator = null`(无分母), `dedup_policy = inter_article_no_dedup_intra_article_one_row_per_article`。
- R-4b power 计算:用 log1p(count) 分布的实证估计。

---

### (5) Lookup window —— 与 R-1b 共享 / 还是别的

**决策**:**与 R-1b 完全共享**:`[CLS corpus first published_at, min(fleet model cutoff))`,half-open。

#### 候选与判断

| 候选 | 我对它的判断 |
|---|---|
| **与 R-1b 共享同窗口** | **推荐**。framing C 要 "model 预训练 cutoff 之前曝光",fixed 窗口右端点对所有 model cutoff 安全。 |
| case-relative 滚动窗口 `[T-X, case.published_at)` | 同 R-1b 排除理由:post-cutoff case 把 model cutoff 后才出现的 mentions 当 exposure 计数。与 framing C 不一致(framing 是 "pre-cutoff 曝光",不能让 post-cutoff 信号倒灌)。 |
| fixed 但不同端点 | 没理由换。R-1b 已锁 `[corpus_start, min_cutoff)`,R-1c 换端点会让 discriminant check VIF 计算口径变,得不偿失。 |
| per-model 滚动窗口 | 让 Salience 变 case×model factor,与 R-1c 作为 case-level factor 的角色冲突。 |

#### 决策理由链

1. **framing C 的"预训练曝光" claim 要求 right-endpoint ≤ model cutoff**。最严的 cutoff 是 `min(fleet model cutoff)`(~2024 mid)—— 在此之前的 mention,**所有 fleet model 都可能见过**。这是干净的 case-level statement。
2. **与 R-1b 共享窗口 → discriminant check 在同窗口跑**,VIF 计算口径一致,可比性强。若窗口不同,VIF 解读会问 "是 construct 共线还是窗口选择导致";共享窗口消除这层歧义。
3. **case-relative 滚动**是 reviewer 直觉但严重的 framing 错配:它把 case 自身发文时间之后但 model cutoff 之前的 mention 也排除掉了(因为 T < case.published_at),反而 lose信息;同时 post-cutoff case 在 case-relative 窗口里会看到 post-cutoff mention(因为 case.published_at > model cutoff,窗口右端点在 cutoff 之后)。两头错。
4. **post-cutoff case 的 Salience 怎么办**(自然问题):pilot 80 pre + 700 post,post-cutoff 案例只做 BL2 baseline(R-4a 锁)。对 post-cutoff case 算 Salience(在 fixed `[corpus_start, min_cutoff)` 窗口里数 target mention)依然合法,**而且这恰好是想测的"模型在 cutoff 之前对这个 entity 见了多少"**。post-cutoff case 用的 Salience 与 pre-cutoff case 用的 Salience 在同一窗口口径上,主因子 β3 估计有意义。

#### 已锁边界 check

- CLS 语料 2020-01 到现在:left endpoint = CLS first published_at(R-0)。✓
- min(fleet model cutoff) 来源:`config/fleet/r5a_fleet.yaml`(R-1b 已锁同源)。✓
- half-open 区间(R-1b 同):严格 `< min_cutoff`,避免 boundary case。✓

#### 替代方案 / 何时换

无。fixed [corpus_start, min_cutoff) 是 framing C 在 fleet 设计下的唯一干净选择。

#### R-5 sampling 互动 sanity check

窗口固定 → Salience 是 case 的纯属性(不随 case.published_at 变)→ 与 sampling 无新增耦合(沿 §决策 3 / §决策 4 的耦合)。✓

#### 留给下游

- B-2: `reference_window = { start = cls_corpus_first_published_at, end = min_fleet_model_cutoff, interval = half_open }`,与 R-1b 同源。
- 若 fleet 后续调整,manifest 改动,R-1b / R-1c 同步重算。两个 metric 在同一 cutoff manifest 下保持一致。

---

### (6) Tradable filter —— 是否给 Salience 计数加 `tradable_at_event=true`

**决策**:**不加 tradable filter**。分子分母都不加。

#### 候选与判断

| 候选 | 我对它的判断 |
|---|---|
| 加 tradable filter(与 R-1b 同) | 不推荐。与 framing C "exposure intensity / prominence" 在 construct 层错配(实体出名不需要它当时上市)。 |
| **不加(L1 客体保留 non-tradable)** | **推荐**。R-0 §1 显式锁 L1 不带 tradable 列;L1 mention construct 自然不加。 |
| 只分母加,分子不加 | 半生不熟混合。framing 没动机要这样做,直接 reject。 |

#### 决策理由链(核心张力 —— 必须正面表态)

构造层面 vs 一致性层面的张力:

- **"construct 一致性派"(加 tradable filter)**:与 R-1b 同 cohort,discriminant check 在同 metric 口径上跑,VIF 解读直接。
- **"claim 贴合派"(不加 tradable filter)**:framing C "exposure intensity / prominence" 与 tradable 在 construct 层正交。entity 出名不需要它当时上市。强加 tradable filter 是 over-constraint,损失 framing 一致性。

我选**claim 贴合派**,理由:

1. **R-0 §1 已锁:L1 不带 `tradable_at_event` 字段**。L1 mention 的自然定义就是不需要 tradable 信息。如果非要给 L1 加 tradable filter,需触发 Pool D(R-0 §4)架构扩展 —— 用一个真实成本换一个 "VIF 解读方便"。不值。
2. **case 主体(P_predict)仍是 tradable**(universal admissibility,R-0 §3),这是 R-0 锁的"客体保留 / 主体过滤"原则。R-1c 不破坏这个原则 —— **Salience metric 是 case 的属性(数 entity 在 corpus 里的 exposure),不是 case 主体的 eligibility 条件**。两件事不要混。
3. **claim "prominence" 的对照实验逻辑要求计入 non-tradable mentions**。譬如某新经济实体 IPO 前在 CLS 已被反复提及(传闻 / 战略融资),IPO 后才作为 case 出现 —— 这些 IPO 前的 mention 都是模型预训练时的 exposure。tradable filter 把它们剔掉是错的。
4. **discriminant check 在不同 metric 口径上跑也合法**。VIF / |r| 不要求两个 metric 同基底;它衡量的是 case-level 上两个连续变量的共线性。R-1c L1 mention(包含 non-tradable rows)与 R-1b L2 subject + tradable 在 case 维度上完全可以算 VIF;就算两者结果共线度低,也是有意义的发现(说明 prominence 与 family-recurrence 测的不是同一件事)。

驳"加 tradable filter 让 VIF 解读直接":VIF 解读是不是"直接"取决于 sample 大小 + 实际共线度,不取决于 base cohort 是否一致。若两个 metric framing 不同(R-1b outcome-leakage proxy / R-1c prominence proxy),hardcoded 一致的 base 反而 mask 它们应该不同的本质。

#### 已锁边界 check

- R-0 §1: L1 / L2 保留 non-tradable rows 作 Salience / Recurrence 分母客体;**R-1c L1 mention 完全在这个授权内**。✓
- R-0 §3 universal admissibility 不破:case 主体仍过 tradable;R-1c 只动 metric 计数 base。✓
- Pool D 不触发:R-1c 选 L1 mention 不加 tradable → 不需要 Pool D 扩展。✓(R-1b 也 dormant)

#### R-5 sampling 互动 sanity check

case sample 仍抽自 L3 base view(tradable 主体),所以 case 自身的 Salience 值是 "tradable case 对应的 entity 在 CLS(含 non-tradable mention 的 corpus 全集)里的 mention count"。这种"主体 tradable + count base 包含 non-tradable" 的组合是 framing C 的精确实现,与 R-5 sampling 无冲突。R-5 仍可选 Pool G stratified。

#### 留给下游

- B-2: `tradable_filter = false`,`row_unit_includes_nontradable = true`,`requires_pool_d_or_l1_tradability_extension = false`。
- 必报 A/B count delta(类比 R-1b §6.3):
  - `n_target_L1_mentions_total`(L1 mention 总数,target = case.target_entity_id,窗口内)
  - `n_target_L1_mentions_if_tradable_filtered`(同上,但加 tradable filter,**仅诊断用**,不进 metric)
  - `share_nontradable_in_target_L1_mentions`(尾部诊断)
  
  预期诊断结果:non-tradable share 大多数 case 可能很低(因为 case 主体本身必 tradable,target 在大部分时段也 tradable),但**偶发会高**(IPO 前 / 停牌 / 退市段)。这个 share 高的 case 就是 R-1c L1 mention vs R-1b L2 subject + tradable 拉开的地方,VIF 区分性的物理来源。

---

### (7) Discriminant check —— 阈值与 fallback metric 形态

**决策**:
- **阈值沿用 R-1b §5.3**:VIF ≥ 10 OR `|r| ≥ 0.90` 触发 fallback。
- **Fallback metric**:**残差化(partial out R-1b log1p_recurrence_count)**。即报 `log1p_target_salience.residual_against_recurrence` 作为 fallback metric,β3 用残差化版重估。

#### 阈值

R-1b §5.3 锁的 VIF=10 / |r|=0.90 是子领域 / 统计教科书通用阈值。R-1c 没有特殊理由收紧或放宽:

- 收紧(VIF ≥ 5 / |r| ≥ 0.7)的理由:Salience 与 Recurrence 共用 CLS 大 corpus,先验高相关 → 阈值应严以早期 trigger fallback。但**前提**是没做 construct 分家。我们已经分家(L1 mention vs L2 subject + tradable;target only vs target × super_type),先验相关性应该被 construct 层面拉开;不需要在阈值层面再加保险。
- 放宽(VIF ≥ 20)的理由:case-level 两个 mention-derived continuous factor 高度相关是预期,放宽阈值避免常常 fire fallback。但**阈值的目的是质量门**,不是为不 fire 而设。放宽阈值 = soft-pedal collinearity 问题。

**沿用是最小可辩护选择**。

#### Fallback metric 形态

候选:

| Fallback 候选 | 描述 | 我对它的判断 |
|---|---|---|
| complement-family(target × 非 case super_type 的 mentions) | WS0.5 §3.3.2 的预案(只读了 prompt 介绍,未读 WS0.5 §3.3 原文) | 复杂,改 construct,而且我决策 3 已经选 target only,complement-family 等于退回到 family 维度 ad-hoc。 |
| **residualize (partial out R-1b)** | 报告 `residual = log1p_target_salience - β_fit × log1p_recurrence` | **推荐**。clean、只动一步、保留 L1 mention 的 construct 本质。 |
| switch denominator(从 count 切到 share / industry / rank) | | 不解决 collinearity 根本(分母是常数变换),只是变形。 |
| switch window | | window 已锁 [corpus_start, min_cutoff),没有更窄的合法选择。 |

#### 决策理由链(fallback)

1. **残差化是最小干预**。construct / family / window / tradable 全部锁定不动;只在 β3 估计这一步用残差量替代原 Salience。这保证 R-1c metric 的 framing C 解释不被 fallback 改写。
2. **残差化的统计解释干净**。"控制 R-1b log1p_recurrence_count 后的 Salience 净效应" —— 这是标准回归语言,reviewer 不会有 ad-hoc 之嫌。
3. **complement-family 等于退回 family 维度做手术**,引入 super_type-specific count 的新概念,且 R-1c 已锁 target only family。前后不一致,叙事难写。
4. **fallback 是条件分支,不替换主 metric**。R-1c primary metric 仍是 log1p(L1 mention count) ;只在 discriminant check 超阈时报 residualized 版作为 conditional analysis。报告 prose:"Primary β3 uses raw log1p_target_salience; if discriminant check fires, we additionally report β3' on residualized Salience (orthogonal to Recurrence) as a conditional collinearity-adjusted estimate."

#### 已锁边界 check

- R-1b §5.3 / §8 锁的 standing routine: VIF + correlation 检查,阈值 VIF≥10 / |r|≥0.90。✓
- fallback **必须 R-1c session 自决,不传给 R-1d**(prompt 强调):本决策点已自决。✓

#### R-5 sampling 互动 sanity check

VIF / correlation 在 case sample 上算。如果 R-5 random sample → 高 Salience case 多 → VIF 估计可能比 stratified Pool G 上更稳定但更乐观(因为高 Salience case 多 → 与 high Recurrence 重合的 dense region 主导)。Stratified Pool G(若启用)会让 VIF 估计涵盖低 Salience 段,更保守。

**R-1c 不替 R-5 决定**,但标 sanity-check note:"discriminant check 结果对 sampling 分布敏感;pilot 上若 Pool G 启用,VIF 报告应同时给 Pool G 与 row-random 两种 sample 上的估计供 R-1e 判断"。

#### 留给下游

- R-4b power 计算:若 pilot discriminant 接近阈值,R-4b 用残差化版做 power simulation 兜底。
- B-2: `discriminant_check_threshold = { vif = 10, abs_correlation = 0.90 }`,`fallback_metric = residualize_against_r1b_log1p_recurrence_count`。

---

### (8) Robustness / appendix candidates —— pre-commit 几个 slot

**决策**:**Pre-commit 0 个 robustness slot**。与 R-1b 同 pattern,只保留 1 个 appendix conditional reanalysis(条件未触发不报)。

#### 候选与判断

| 候选 | 我对它的判断 |
|---|---|
| **Pre-commit 0 个 + 1 个 appendix conditional**(同 R-1b pattern) | **推荐**。最小可辩护,与 R-1b 一致 minimal 风格。 |
| Pre-commit 1 个 share-vs-count slot | 在固定窗口 + target only 下 share 与 count 等价(决策 4 已论)。无信息增益。不做。 |
| Pre-commit 1 个 cross-corpus 信号 slot | framing C 不强求外部信号(那是 framing B 的承诺)。建外部信号(百度搜索 / 维基 page view / 其它金融媒体)是新管线工作,R-1c session 不能承诺;留 stretch goal。不做。 |
| Pre-commit 1 个 window-length sensitivity slot | R-1b §7.2 显式排除 "多窗口 grid robustness" 因为窗口不同 construct 不同。R-1c 同理。不做。 |
| 别的 | — |

#### 决策理由链

1. **R-1b 锁 0 pre-commit + 1 appendix conditional**(R-1b §7.1)。R-1c follow same pattern 是结构性 minimal 选择。
2. **R-4a 不锁因子数 / 不强制 robustness pile-on**。预 commit 越多 robustness slot,后期越受约束,且 R-4a 锁 "不做 family-wise multiplicity correction" → robustness 的纸面价值有限。
3. **cross-corpus signal slot 在论文里是 high-value 但 R-1c session 承诺不了它**。如果团队后续愿意建百度搜索量爬虫 / 维基 page view dump 等,作为 R-1c 主 lock-in 之后的 follow-up robustness paper section 是合理的;但 R-1c 当前不预 commit 这块工程。
4. **share / window / rank robustness 都是 cosmetic** —— 在 framing C + fixed window + target only + log1p(count) 下,这些变体提供的信息增益接近零。pile-up robustness 只能让 reviewer 觉得复杂,不能提供 incremental evidence。

#### Appendix conditional reanalysis(类比 R-1b §7.1)

| 字段 | 值 |
|---|---|
| 候选 conditional reanalysis | L1 mention vs L2 subject 的构造对比(若 pilot 显示两个 count `|r| ≥ 0.95` ,即 framing-driven construct 分家未拉开预期差异,补报 L2 subject 版本的 β3 作 robustness)|
| **激活 condition** | pilot N=80 跑完后, `corr( log1p(L1_mention_count), log1p(L2_subject_count[r1b basis no tradable]) ) ≥ 0.95` |
| 激活后 action | 补报 L2 subject + no-tradable 版的 β3,与 primary β3 对比,prose 解释 L1/L2 区分是否 empirically meaningful |
| 不激活 | **不报,连 prose 都不写** |
| Slot | **Appendix**(同 R-1b 模式)|

这是个 cheap insurance:它的成本几乎为零(L2 subject count 在 R-1b 管线里已经算),trigger 后是单一对照报告,不会膨胀 robustness family。

#### 已锁边界 check

- R-4a 锁 main / primary / supporting / robustness / appendix 标签:appendix conditional 走 appendix 标签。✓
- 不做 family-wise multiplicity correction(R-4a 锁):0 pre-commit + 1 conditional appendix 不构成 family,无需 correction。✓

#### R-5 sampling 互动 sanity check

robustness 不与 sampling 有新增耦合(robustness 是 metric 形态变体,sampling 是 case 分布)。✓

#### 留给下游

- B-2: `robustness_precommit_slots = 0`,`appendix_conditional_l1_vs_l2_construct_check = { trigger_corr_threshold = 0.95 }`。
- R-1e / R-4b:若 appendix conditional 触发,R-1e 因子最终选择应纳入 L1 vs L2 对比作为参考(但 framing C 仍指向 L1 mention 为 primary)。

---

## R-5 sampling 互动 — 集中 sanity check note(隐含逐点 check 之外)

R-1c 决策点 1-8 集中起来,对 R-5 的 sanity-check input 是:

1. **R-1c metric(log1p L1 mention count, target only, no tradable, fixed [corpus_start, min_cutoff))与 random sampling 有内在耦合**:高 prominence 实体在 corpus 里出现条数多,L2 subject 行也多,random sample 会偏向高 Salience case。
2. **R-1c 与 sampling 分布不独立**这一事实**不**意味着 R-5 必须用 Pool G。R-5 可选:
   - random sampling(接受 Salience 分布右偏作为自然 prevalence)
   - Pool G stratified by R-1c log1p(L1 mention count)(平衡低 / 中 / 高 Salience 段)
   - Pool H entity-balanced (anti-survivorship per Kong §2.2 警告)
   - 组合
3. **R-1c 推荐 R-5 在 pilot 同时跑 random + Pool G 两种 sample 上算 discriminant check 与 effect size**,R-1e 根据这两份数据判断哪种 sampling 更适合 main run。但 **R-1c 不命令 R-5**,只标 input note。
4. **Kong §2.2 survivorship 警告**(media coverage correlates with ongoing corporate activity):R-1c 用 L1 mention count(包含 non-tradable)+ no tradable filter,**反而部分缓解** Kong 警告 —— 它让 IPO 前 / 退市 / 停牌段的 mention 也进 Salience 计数,降低 "Salience 与 survivorship 重合" 的偏差。tradable filter 加在 R-1b 是因为它的 framing 需要 outcome,R-1c 不加 tradable 是 framing C 的必然 + Kong 警告的 collateral 减损。

---

## 阶段 1 决策汇总 (Pre-stage-2)

| # | 决策点 | 主选 | 一行理由 |
|---|---|---|---|
| 1 | Framing | **C — Corpus exposure intensity(CLS as proxy)** | 最小可辩护中间路径;claim 与 metric 之间有可论证的 monotone-proxy 桥;不需 cross-corpus 承诺。 |
| 2 | Construct | **L1 mention**(`(article, target_entity_id)` pair, no tradable, no subject filter) | framing C 决定:任何 mention 都是 exposure;与 R-1b L2 subject + tradable 结构分家。 |
| 3 | Family | **target only**(全 super_type 合并) | framing C "general prominence";target only 是直接 operationalization。 |
| 4 | Denominator | **`log1p(target_mention_count)`,无分母** | fixed window 下任何 case-invariant 分母对 case-level metric 是常数缩放,无信息增益。 |
| 5 | Window | **与 R-1b 共享:`[CLS first published_at, min(fleet model cutoff))`,half-open** | framing C 要求 pre-cutoff 窗口;共享窗口让 discriminant check 在同口径跑。 |
| 6 | Tradable filter | **不加**(分子分母都不加) | L1 layer 不带 tradable 列(R-0 §1);framing 与 tradable 正交。 |
| 7 | Discriminant + fallback | **沿用 VIF≥10 / `|r|`≥0.90 阈值;fallback = 残差化** | 阈值是子领域 / 教科书标准;残差化最小干预,construct 不变,统计解释干净。 |
| 8 | Robustness slots | **0 pre-commit + 1 appendix conditional**(L1 mention vs L2 subject 对比若 pilot `|r|≥0.95` 触发) | follow R-1b minimal pattern;robustness pile-up 不增加 incremental evidence。 |

---

## 阶段 2 对照

> 阶段 1 写完后,以下对照按 prompt 列出的 6 个对照对象逐项过:
> (i) WS0.5 §3.3 整章现状 prototype;
> (ii) WS0.5 memo frontmatter `revision_basis` 历史决策链;
> (iii) WS0.5-era Codex Target Salience construct 旧提案(2026-05-18);
> (iv) R-1b whiteboard (a) construct 段(L1 mention vs L2 subject 哲学判决);
> (v) CROSS_SYNTH §A.🟡-4 Kong §2.2 survivorship-bias sanity check;
> (vi) 同行文献(Tirumala / Shi / Carlini / AntiLeakBench)。
>
> 阶段 1 与对照项冲突处**坚持阶段 1**,不为兼容性修圆角。逐项过 8 个决策点。

---

### (i) 与 WS0.5 §3.3 现状 prototype 对照

**WS0.5 §3.3 现状摘要**(2026-05-18 v0.4 + 2026-05-23 PM late R-0 supersession note):

- §3.3.2 Target Salience metric = `log1p(cls_target_mention_count)` 在 `[corpus_start, earliest_model_cutoff)` 窗口数 CLS articles where confirmed salient entities include any alias in target_aliases。
- "Across all event types"(无 super_type filter)。
- "Computed off §5 recurrence pipeline — no new infrastructure": "alias-match count with the `super_type` filter removed"。
- Discriminant rule §3.3.3: VIF + 4×4 Pearson correlation,阈值 max VIF ≥ 10 / |r| ≥ 0.90 触发 fallback;fallback 候选 = "Target Salience on complement family-set" 或 "non-CLS proxy (Baidu Baike entry length)"。
- 注:R-0 supersession note 2026-05-23 PM late 把 §3.3.1 case admissibility lifted 到 R-5 L3 base view;§3.3.2 现状的 metric definition 本身仍是 WS0.5 prototype baseline。
- 注:WS0.5 §3.3.2 "salient entities" 的语义 = entities with `salience == "core"` from Thales entity pipeline,**这与 R-0 L1 layer 的 `(article, target)` 任意 pair 不完全等同** —— WS0.5 的 "core" entity 是带主观显著度判断的 subset,介于 L1 全部 pair 与 L2 subject 之间。

**逐决策点对照**:

| # | WS0.5 §3.3 现状 | 阶段 1 决策 | Verdict |
|---|---|---|---|
| 1 framing | "general prominence / plausible pretraining exposure" —— framing C 同向 | C(corpus exposure intensity as proxy) | **一致**。WS0.5 §3.3.2 现状 + C-1 redesign 已朝 framing C 方向走;阶段 1 独立得出同一结论,这是 reviewer "推得对" 的部分。**保留**。 |
| 2 construct | "alias-match count with the super_type filter removed" + 限制在 `salient_entities` 中 `salience == "core"` —— 比 L1 mention 窄,比 L2 subject 不完全等同 | L1 mention(任何 article × target pair,无 salience 限制,无 tradable filter) | **冲突,坚持阶段 1**。WS0.5 §3.3.2 的 "core entity" 限制是上一代 Thales entity pipeline 的产物,framing C "exposure intensity" 要求**任何提及都算 exposure**,不应被 "core" subjective tag 过滤。阶段 1 的 L1 mention 是 R-0 layer 锁后的正确选择,WS0.5 §3.3.2 现状是 super-early prototype。 |
| 3 family | "all event types" —— target only family,同向 | target only(全 super_type 合并) | **一致**。WS0.5 §3.3.2 现状对 family 折叠的判断与阶段 1 收敛。**保留**。 |
| 4 denominator | `log1p(cls_target_mention_count)` 裸 count + log1p,无分母 | `log1p(target_mention_count)` 裸 count + log1p,无分母 | **一致**。**保留**。 |
| 5 window | `[corpus_start, earliest_model_cutoff)` half-open | `[CLS first published_at, min(fleet model cutoff))` half-open | **一致**(`earliest_model_cutoff` = `min(fleet model cutoff)`)。**保留**。 |
| 6 tradable filter | WS0.5 §3.3.2 现状**不**显式说 tradable filter;但 "salient_entities" 含 type 限制 → 默认在 `salience==core` 的 alias-match 上算 → 隐式不强加 tradable filter(虽然 confounded 在 salience score 选择中) | 不加 tradable filter | **基本一致,但阶段 1 更显式**。阶段 1 显式声明 `tradable_filter = false` 并把 L1 layer 不带 tradable 列作为 R-0 锁的硬约束。WS0.5 §3.3.2 没显式表态,改写时按阶段 1 显式化。 |
| 7 discriminant | VIF ≥ 10 / `|r|` ≥ 0.90 阈值;fallback 候选 = complement-family OR non-CLS proxy | 沿用阈值;fallback = 残差化(partial out R-1b log1p_recurrence_count) | **阈值一致;fallback 形态冲突,坚持阶段 1**。WS0.5 §3.3.2 提的 complement-family fallback 是基于 WS0.5 那时 R-1b 还没锁、family 选择都是开放的语境;现在 R-1b 已锁 target × super_type,R-1c 阶段 1 选 target only,complement-family 等于改变 R-1c family 定义 —— 引入 family 维度不一致。残差化最小干预、construct 不变。WS0.5 §3.3.2 提的 Baidu Baike alternate proxy 也不必,framing C 不要求 cross-corpus 信号。 |
| 8 robustness | WS0.5 §3.3.2 没明示 pre-commit robustness slot 数 | 0 pre-commit + 1 appendix conditional(L1 vs L2 construct 对比触发条件) | **阶段 1 更显式**。WS0.5 §3.3 没在 robustness 维度做承诺;阶段 1 follow R-1b 0-precommit minimal 模式 + 1 个 cheap-insurance appendix conditional。**保留**。 |

**§3.3 重写指引**:R-1c 落定后,WS0.5 §3.3.2 应重写为:
- 改 "alias-match count with super_type filter removed" → "L1 mention count, target_entity_id, fixed [corpus_start, min(fleet model cutoff)) window, all super_types, no tradable filter, no salience-tag filter"
- 加 framing C "CLS as proxy for corpus exposure intensity" 显式语言
- 移除 §3.3.2 fallback 候选 "complement family-set" 与 "Baidu Baike"
- 加阶段 1 残差化 fallback 形态
- §3.3.1 case admissibility 已在 R-0 supersession note 中 lifted 到 R-5;此处只保留 R-5 base pool 引用,不重复 admissibility 规则

---

### (ii) 与 WS0.5 frontmatter `revision_basis` 决策链对照

WS0.5 §3.3 关键决策链:**C-1 redesign**(2026-05-20)— v0.2-v0.3 conflated filter + scorer,redesign 把 case-admissibility 拉出 Target Salience 内部 → §3.3.1 全局 pre-filter + §3.3.2 pure scorer。Target Salience 从 v0.2-v0.4 禁止 CLS mention count(用 market-cap / index 替代)反转为 `log1p(cls_target_mention_count)`。

理由(memo 原文):"market cap / index membership measures firm size, not fame, and misclassifies small-but-heavily-covered targets (妖股, hot new issues, scandal stocks) as low-salience"。

| 决策链节点 | 阶段 1 verdict |
|---|---|
| **C-1 reversal: 用 CLS mention count 替代 market-cap** | **推得对**。我阶段 1 独立选 framing C(CLS-as-proxy) + L1 mention,与 C-1 reversal 方向一致。market-cap / index membership 是 ex-post 后视镜分类(R-1b §7.2 同精神排除),与 "prominence / pretraining exposure" 在 construct 层不对齐。**保留**。 |
| **C-1: 把 case-admissibility 从 Target Salience 内部拉出** | **推得对**。case-admissibility 是 sampling-stage decision(R-0 supersession note 已 lift 到 R-5 L3 base view),不应嵌入 Target Salience metric。阶段 1 没碰这条决策(已被 R-0 supersede),与 C-1 一致。**保留**。 |
| **C-1: §3.3 删 v0.3 `context_gate` veto + `static_reach` 1/2/3 ordinal** | **推得对**。`context_gate` 与 `static_reach` 都是 reviewer 推的 ad-hoc 量;C-1 把它们合到 admissibility pre-filter 是合理简化。**保留**(不再出现在 R-1c 主 metric 里)。 |
| **C-2: window 从 per-case `[T-24mo, T)` 改成 fixed `[corpus_start, earliest_model_cutoff)`** | **推得对**。阶段 1 决策 5 独立选 fixed 同窗口。**保留**。 |
| **C-3: `log1p_recurrence_count` 替代 percentile / binary** | **推得对**(R-1b 已 lock-in)。R-1c 阶段 1 同样选 log1p(count)。**保留**。 |
| **C-4: no-dedup recurrence**(0.48% intra-day duplication probe) | **推得对**。R-0 §5 锁 no-dedup;R-1c 阶段 1 沿用。**保留**。 |
| **S-6: discriminant 收到 VIF + 4×4 Pearson** | **推得对**。阶段 1 决策 7 沿用 VIF + correlation 阈值。**保留**。 |
| **E-5/E-6/E-7 entity disambiguation 链** | **推得对 in spirit**:deterministic-first alias / disambiguation 是 B-2 实现资产,不替 R-1c 决定 construct。阶段 1 不碰这条(留 B-2)。**保留**。 |

**整体 verdict**:C-1/C-2/C-3/C-4/S-6 链条都是**正确修正**,不是 reviewer pile-on。阶段 1 独立得出与这些 reversal 一致的结论,双源验证。

**唯一 frontmatter 链节阶段 1 不采纳**:WS0.5 §3.3.2 提的 fallback metric 候选(complement family-set / Baidu Baike)—— 这两个候选属于 v0.4 写入时 framework 还没敲定的状态,现在 R-1b 锁 target × super_type / R-1c 锁 target only,残差化 fallback 是更干净的最小干预。

---

### (iii) 与 WS0.5-era Codex Target Salience construct 旧提案对照(2026-05-18)

**Codex WS0.5-era 旧提案摘要**(`ws0_5_target_salience_construct.md`):
- **Scheme A(首选)**:Metadata-Anchored Market-Reach Salience。3-level ordinal(1=low / 2=medium / 3=high),由 `context_gate`(in-headline / `mention_count ≥ 2`)× `static_reach`(SSE50/CSI300 / 普通上市 / 小盘等市场 reach)组合。**显式 don't**:"Do not use CLS historical mention counts, search-engine counts, Wikipedia/Baidu pages, or crawler output in Target Salience"。
- **Scheme B(alternative)**:Text-Only Target Prominence Salience。fall-back if metadata 不可得。
- 都是 ordinal,不是 continuous;都禁止 CLS mention count;都用 market-cap / index membership / static reach 等 metadata 信号。

**逐决策点对照**:

| # | Codex WS0.5-era 旧提案 | 阶段 1 决策 | Verdict |
|---|---|---|---|
| 1 framing | "cross-corpus training exposure to the target",但 metric 是 market-cap / static reach ordinal,**claim 与 metric 错位**(claim 是 exposure,metric 是 firm size)| C(corpus exposure intensity,CLS-as-proxy) | **冲突,坚持阶段 1**。旧提案的 claim 与 metric 错位是 C-1 redesign 后被 user 反弹的原因:market-cap 测 size 不测 fame,妖股 / hot new issues 系统性被误分类。framing C + CLS mention count 是 C-1 reversal 的方向,正是阶段 1 独立得出。 |
| 2 construct | 3-level ordinal(context_gate × static_reach),不是 row-count metric | L1 mention count(`(article, target)` pair, continuous) | **冲突,坚持阶段 1**。ordinal 已被 C-3 reversal 推翻(C-3 把 R-1b 改成 continuous log1p_recurrence_count;同精神适用 R-1c)。continuous + log1p 是 R-1b 同口径 + 子领域 anchor 一致(Carlini log-linear)。Codex 旧提案的 3-level ordinal 是 prototype-era ratchet。 |
| 3 family | 不适用(ordinal scheme 不数 row) | target only | **N/A**(旧提案不用 row count)。 |
| 4 denominator | 不适用 | log1p(count) | **N/A**。 |
| 5 window | "static_reach 基于 metadata snapshot,不需要 historical window" | `[corpus_start, min_cutoff)` historical window | **冲突,坚持阶段 1**。historical-window-based mention count 是 framing C 的直接 operationalization;static metadata snapshot 是错位 framing 的产物。 |
| 6 tradable filter | Codex 旧提案隐式要求 target 是 tradable(列在 5 个 target type 里 ETF/index/sector/listed company/macro)—— 实际是 case-admissibility,不是 Salience metric filter | 不加 tradable filter(L1 layer 不带) | **基本一致 in effect**:case 主体仍 tradable(R-0 universal admissibility 锁),但 Salience metric 不再加 tradable filter。Codex 旧提案 conflated case admissibility 与 metric filter,C-1 redesign 已分开。**保留分开**。 |
| 7 discriminant | "Spearman correlation `|rho|<0.50` desired, VIF<3" —— 比 R-1b 锁的 VIF≥10 / `|r|`≥0.90 严太多 | VIF≥10 / `|r|`≥0.90 | **冲突,坚持阶段 1**。Codex 旧提案的 VIF<3 阈值是 ordinal scheme 下的保守值,但 ordinal 已 deprecate;continuous metric 的子领域阈值就是 VIF=10。**S-6 reviewer 也 push 回 VIF=10 这条线**(S-6 lit review,collinearity_diagnostics_20260520.md),与阶段 1 一致。 |
| 8 robustness | "double-label 80 cases + 60-case audit + weighted kappa ≥ 0.70" —— annotation quality 范畴,不是 R-1c primary robustness slot | 0 pre-commit + 1 appendix conditional | **不冲突**(双方在不同维度)。annotation quality 是 B-2 / WS0.5 implementation 范畴,R-1c primary 不管;阶段 1 的 robustness 是 statistical-form variation。 |

**整体 verdict**:Codex WS0.5-era 旧提案是 super-early prototype + reviewer-driven complexity ratchet 的产物。它的核心选择(ordinal + market-cap-based + cross-validation kappa)在 C-1 / C-3 / S-6 三轮 reversal 中已被推翻,**框架完全废弃**。阶段 1 独立得出 framing C + continuous L1 mention + log1p 完全在 reversal 方向上,坚持阶段 1。

**唯一可借鉴**:Codex 旧提案 §1 target selection rule(deterministic, headline / core / disambiguation 规则)与 B-2 entity pipeline 相关,但那是 B-2 territory,不进 R-1c 主 metric 定义。

---

### (iv) 与 R-1b whiteboard (a) construct 段对照

**R-1b whiteboard (a) construct 段摘要**:R-1b 主白板初稿选 L2 subject(unfiltered),stress-test 后改判为 **L2 subject + tradable_at_event=true**(outcome-leakage proxy framing)。R-1b §(d) 对 R-1c 锚点说:

> "R-1b 选 L2 subject,不代表 R-1c 必须 L2。Salience 常常更适合 L1 mention 或 unique article count,因为'被媒体提到'本身就是 salience。"
>
> "不要默认继承 R-1b 的 L2 subject construct。"

R-1b §(a) 也说:"L1 mention robustness:如果 pilot 发现 L2 subject 太稀疏... 可以在 appendix 报 L1 mention 版本。"(R-1b 不把 L1 mention 进自己 robustness,但开口子给 R-1c。)

R-1b §阶段 2 §1 也明示:"若 R-1c 选择 L1 mention salience,旧 mention count 更适合迁移到 R-1c,而不是留在 R-1b 主变量。"

| 决策 | R-1b whiteboard 对 R-1c 的指示 | 阶段 1 决策 | Verdict |
|---|---|---|---|
| Construct | "可选 L1 mention,不要默认继承 L2 subject" | L1 mention | **一致**,且 R-1b 显式留口子给 R-1c。**保留**。 |
| Framing | R-1b 选 outcome-leakage proxy framing;R-1c 不一定 mirror | R-1c framing C(corpus exposure intensity / prominence) | **一致 in design**:R-1b prompt 显式提醒 "R-1c framing 可能不同,不要照搬"。阶段 1 独立选 C 不是 mirror,符合 R-1b 留的选择空间。 |
| Family | "事件折叠:R-1b 是 target × event_super_type;R-1c 一般应 all-event,不按 recurrence family 切" | target only | **一致**。R-1b 已显式建议 R-1c all-event(= target only)。**保留**。 |
| Window | R-1b 推荐 fixed window,但 "R-1c 可以继承以便可比,也可以独立选择" | 与 R-1b 共享 fixed | **一致**(选共享)。**保留**。 |
| log1p transform | "如果 Salience 也是 count,继承 log1p 很自然,但 R-1c 可以选择 share / percentile" | log1p(count) | **一致**(选继承)。**保留**。 |
| Tradable filter | R-1b 自己加了 tradable filter(outcome-leakage 需要 tradable outcome);R-1b §(d) 没强求 R-1c 也加 | 不加 tradable filter | **一致 in design**(R-1b 给的选择空间允许 R-1c 不加;framing C 决定不加)。**保留**。 |
| Pool D | R-1b dormant(L2 subject + tradable 不需要 Pool D);R-1c 选 L1 mention + no tradable 也 dormant | dormant | **一致**。Pool D 保持 dormant。 |
| Denominator | R-1b 是 count 不需要分母;"R-1c 如果定义成 share 就必须独立决定分母" | log1p(count),无分母 | **一致**(选 count)。**保留**。 |

**核心点**:R-1b whiteboard 给 R-1c 留的选择空间正好是阶段 1 选的路径。R-1b 的"L1 mention 不进 R-1b 自己的 robustness,留给 R-1c"是直接 endorse 阶段 1 的方向。**双源验证强**。

---

### (v) 与 CROSS_SYNTH §A.🟡-4 Kong §2.2 survivorship sanity check 对照

**CROSS_SYNTH §A.🟡-4(a) 摘要**(approved 2026-05-23):

> R-1c kickoff 把 Kong §2.2 (Survivorship Bias, Issue 1, page 3) 作为 input — Kong 原文:"media coverage inherently correlates with ongoing corporate activity and investor attention, firms that fail or quietly exit the market tend to be underrepresented". 这**直接**支持我们用 CLS mention count 作 prominence proxy 的 construct 选择(媒体覆盖 = 真实存活 / 活跃度 proxy,与市值无关)。

CROSS_SYNTH 也警告:"原 🟡-4 把 Kong §2.2 当 endorsement 是错配方向,修正后改成 sanity-check + sampling scope 扩展。"

| 阶段 1 与 Kong §2.2 的关系 | Verdict |
|---|---|
| Kong §2.2 = sampling-level warning(媒体覆盖 ↔ corporate activity / 退市公司 underrepresented)。阶段 1 framing C(CLS-as-proxy)对 Kong §2.2 的回应:**framing C 显式承认 CLS 是 proxy,gap 在论文里 surface** —— 这是对 Kong 警告的正面回应。 | **一致**。阶段 1 与 Kong sanity check 同方向(承认 proxy,不假装 CLS = 全宇宙 exposure)。 |
| Kong §2.2 警告 "退市公司 underrepresented" —— 阶段 1 选 **L1 mention + no tradable filter** **部分缓解**这个警告(IPO 前 / 退市 / 停牌段的 mention 进 Salience 计数;不要求当时 tradable)。 | **阶段 1 比 Kong 警告要求做得更多 in factor metric**。Kong §2.2 警告是 sampling-level,我们在 metric 层面也做了 anti-survivorship 努力(不加 tradable filter)。**保留**。 |
| Kong §2.2 不 endorse "Target Salience metric 选 CLS mention count" 是对的(原 🟡-4 错配方向,CROSS_SYNTH 已撤);Kong 是 sampling-level warning,不是 metric endorsement。 | **一致**(阶段 1 没把 Kong 当 endorsement,只当 framing C 的 proxy 承认 prompt 一致;Carlini 也只当 anchor 不当 direct endorsement)。 |
| Kong §2.2 真正暴露的张力:R-1c metric × R-5 sampling 的耦合(高 prominence 实体在 random sample 里多 → 低 prominence under-represented)。阶段 1 §R-5 sanity check note 已 flag 这点,留 R-5 决定 Pool G / H。 | **阶段 1 已正面 flag,不替 R-5 决定**。Kong §2.2 的 sampling-level 工作量正在 R-5 session 落地;R-1c 阶段 1 不抢 R-5 scope。 |

---

### (vi) 与同行文献对照

#### Carlini 2023 (Quantifying Memorization Across Neural LMs)

**核心数据点**:training data 内 (1) duplication count (2) model capacity (3) context length 三维 log-linear scaling。Carlini 的 duplication count 是 **真实 training data 内**(他们有 GPT-Neo / The Pile 全集访问),不是 proxy corpus。

| 阶段 1 与 Carlini 的关系 | Verdict |
|---|---|
| Carlini anchor:Salience(count proxy)→ memorization 的 log-linear 关系是子领域 anchor 的方向。但 Carlini 测的是 training-data 内频次,我们用 CLS proxy。framing C 显式承认这 gap,论文方法节需写一段桥论证 "CLS count 是 training-data exposure 的 monotone proxy"。 | **阶段 1 处理得当**:不假装 Carlini 是 direct endorsement,只用作 anchor 方向(log-linear)。**保留**。 |
| Carlini's log-linear shape 支持阶段 1 选 log1p transform(子领域 anchor 一致)。 | **一致**。**保留**。 |
| Carlini 没规定"必须用 L1 mention" or "L2 subject" —— 他在 training data 内数 duplication,不区分 "提及" vs "主语"。但他的 frequency 是**真实 exposure 频次**,与 framing C "任何 mention 都是 exposure" 同方向。 | **一致**。L1 mention 是 Carlini frequency 概念在 proxy corpus 上的最贴近实现。**保留**。 |

#### Shi 2024 (Detecting Pretraining Data, Min-K%/Min-K++)

Shi 在 WikiMIA 上把 detection difficulty 与 model size / text length / **occurrence frequency** / learning rate 分层分析。occurrence frequency 是 prominence/Salience 同类概念。

| 阶段 1 与 Shi 的关系 | Verdict |
|---|---|
| Shi 把 occurrence frequency 作 stratification 维度(不是 outcome),与阶段 1 "Salience 是 case-level continuous factor for β3 interaction"角色一致。 | **一致**。**保留**。 |
| Shi 在 WikiMIA pre-2017 member / post-2023 non-member 设计 sealed split —— 与我们 pilot 80 pre + 700 post + main 2560 的 split-tier 同方向(R-4a 已锁)。 | **R-1c 不动**(R-4a territory)。 |

#### AntiLeakBench 2025

AntiLeakBench 用 post-cutoff updated knowledge + 3-annotator agreement(Raw Agreement + Gwet's AC1)。Salience-类 prominence 不作为 stratification(AntiLeakBench 关注 cutoff-dependent fresh knowledge,不关注 prominence 因子)。

| 阶段 1 与 AntiLeakBench 的关系 | Verdict |
|---|---|
| AntiLeakBench 不直接 anchor R-1c metric 选择(它不用 prominence factor)。 | **N/A**。 |
| AntiLeakBench 的 split-tier + annotation quality protocol 在 R-4a 已 anchor。 | **R-1c 不动**(R-4a territory)。 |

#### Tirumala 2022 (Memorization Without Overfitting)

Tirumala 测 model size / dataset size / learning rate 对 memorization 训练动态的影响。研究的是 training dynamics,不是 inference-time factor metric。

| 阶段 1 与 Tirumala 的关系 | Verdict |
|---|---|
| Tirumala 不直接 anchor R-1c case-level continuous factor 选择;他研究 training-side dynamics。 | **N/A**(不构成 R-1c specific anchor)。 |

#### Kong 2026 (Evaluating LLMs in Finance Requires Explicit Bias Consideration)

Kong §2.2 已在 (v) 处理。Kong §2.1.1 "Parametric Knowledge Leakage" 是我们 R5A 整个中心 channel,framing 层级 anchor 在 §1 motivation(CROSS_SYNTH 🟡-1)。Kong §3 Structural Validity Framework 是 framework-level 5 check binary pass/fail —— **不与 R-1c metric 选择直接对应**(Kong §3 是 deployment-level structural check,我们 R-1c 是 case-level continuous factor)。

| 阶段 1 与 Kong 的关系 | Verdict |
|---|---|
| framing C(CLS-as-proxy)与 Kong §2.2 警告同方向 —— honest disclosure of proxy gap。 | **一致**。 |
| Kong §3.3 Rationale Robustness 与 R-1c 不直接相关(那是 R-1d / R-2 territory)。 | **N/A**。 |

---

### 阶段 2 整体 stance

逐项汇总:**8 个决策点中,阶段 1 与对照对象都没有需要 revert 的冲突**。具体:

- 框架 C / target only / log1p(count) / 共享 fixed window / 不加 tradable / VIF 阈值沿用 / 0-precommit + 1 appendix:都与 R-1b whiteboard 留给 R-1c 的选择空间 + WS0.5 §3.3.2 现状的 C-1/C-2/C-3/S-6 reversal 方向一致(双源验证)。
- **L1 mention construct**:R-1b whiteboard 显式 endorse,WS0.5 §3.3.2 现状的 "alias-match with super_type filter removed" + `salience==core` 限制是 prototype 产物,L1 mention 是 R-0 layer 锁后的正确选择。**坚持阶段 1**。
- **残差化 fallback**:与 WS0.5 §3.3.2 提的 complement-family / Baidu Baike 候选不同,但残差化在 framework 已固定(R-1b lock + R-1c target only)情境下最小干预、构造清晰。**坚持阶段 1**。
- **Codex WS0.5-era 旧提案**(ordinal + market-cap-based)框架已被 C-1 reversal 整体废弃,阶段 1 独立得出与 reversal 一致结论,**坚持阶段 1**。
- **同行文献(Carlini / Shi / Tirumala / AntiLeakBench)**:Carlini log-linear shape + Shi frequency stratification 与阶段 1 同方向;framing C 已显式承认 Carlini 是 anchor 不是 direct endorsement(prompt 强调 anchor caveat,阶段 1 处理得当)。

**唯一在阶段 2 加上的显式 framing 输出**:Kong §2.2 的 anti-survivorship 警告在 R-1c metric 层面的 collateral 缓解(L1 mention + no tradable filter 让 IPO 前 / 退市 / 停牌段 mention 计入)。这是阶段 1 决策 6 已论证的副产品,在阶段 2 显式 surface。

---

## 最终综合推荐(R-1c lock-in 对照表)

| # | 决策点 | 最终选择 | 一句话理由 |
|---|---|---|---|
| 1 | **Framing** | **Framing C — Corpus exposure intensity(CLS as best-available proxy)** | claim 与 metric 之间 monotone-proxy 桥可论证;不强求 cross-corpus 信号;论文方法节显式架桥 "CLS count → training-data exposure" 的代理关系。 |
| 2 | **Construct(source layer / row unit)** | **L1 mention**:`(article_id, target_entity_id)` long-form row,不要求 `is_subject=true`,不要求 `tradable_at_event=true`,不要求 `salience=core` | framing C 决定:任何 mention 都是 exposure;与 R-1b L2 subject + tradable 在 construct 层分家;R-0 §1 L1 不带 tradable 列的硬约束自然落地;Pool D 保持 dormant。 |
| 3 | **Family granularity / event collapse** | **target only**(全 super_type 合并,不切事件) | framing C "general prominence" 的直接 operationalization;避免与 R-1b family 维度同;不引入 complement-super_type 等 anti-overlap engineering。 |
| 4 | **Denominator + transform** | **`log1p(target_mention_count)`**,无分母,inter-article no-dedup + intra-article 单 row(以 L1 row unit 计) | fixed window 下任何 case-invariant 分母对 case-level metric 是常数缩放,无信息增益;log1p 与 R-1b 同、与 Carlini log-linear anchor 同方向。 |
| 5 | **Lookup window** | **`[CLS corpus first published_at, min(fleet model cutoff))`**,half-open;与 R-1b 完全共享 | framing C 要求 pre-cutoff 窗口;共享 R-1b 窗口让 discriminant check 在同口径跑;case-relative / per-model 窗口被 framing C 排除。 |
| 6 | **Tradable filter** | **不加**(分子分母都不加) | L1 layer 不带 tradable 列(R-0 §1 锁);framing 与 tradable 正交(entity 出名不需要它当时上市);Kong §2.2 anti-survivorship 警告 collateral 缓解。 |
| 7 | **Discriminant + fallback** | **阈值沿用 R-1b §5.3:VIF ≥ 10 OR `|r|` ≥ 0.90**;**Fallback = 残差化**(report `log1p_target_salience` residualized against R-1b `log1p_recurrence_count`) | 阈值是子领域 / 教科书标准 + R-1b 同口径 + S-6 lit review 同向;残差化最小干预、construct 不变、统计解释干净(complement-family / Baidu Baike 不采纳)。 |
| 8 | **Robustness slots** | **0 pre-commit**;**1 appendix conditional**:if pilot `corr( log1p(L1_mention_count), log1p(L2_subject_count) ) ≥ 0.95` → 补报 L2 subject 版 β3 与 primary 对比 | follow R-1b 0-precommit minimal pattern;不为 robustness pile-up;1 个 cheap-insurance appendix 兜底 construct 选择 empirical 是否拉开预期。 |

---

## 对下游的约束 / 留下的选择空间

### R-1e 因子最终选择(R-1c → R-1e input)

- R-1c 选定的 Target Salience metric = `log1p(L1_mention_count, target_only, fixed [corpus_start, min_cutoff), no tradable)`;**R-1c 不预承诺 Salience 进 primary**(R-1e + pilot 决定,R-4a 不锁因子数)。
- pilot 后给 R-1e 的输入:
  - `target_mention_count` 原始 count
  - `log1p_target_salience` 主变量
  - non-zero rate / zero rate
  - distribution(在 pilot 80 pre + 700 post 上)
  - correlation / VIF against R-1b `log1p_recurrence_count`(discriminant check 结果)
  - L1 vs L2 subject construct 对比(若 appendix conditional 触发)
- R-1e 据这些数据判断 Salience 是否进 primary,以及 Salience effect size 是否够。

### R-2 / R-3 / R-4a 不变

- R-2(扰动)与 R-1c 正交,不受 R-1c 选择影响;R-2 仍卡 R-6(C_FO 机制)。
- R-3(负对照)BL2 走 TOST/SESOI=0.15(R-4a 锁),不受 R-1c 影响。
- R-4a 框架级 8 条不动;R-1c 在 R-4a 标签(main / primary / supporting / robustness / appendix)+ effect size + 95% CI 框架内汇报。

### R-4b power 输入

- pilot 80 pre + 700 post 上算 Salience effect size + 方差 + Salience-vs-Recurrence collinearity 实证数据。
- R-4b 用这些数 power simulation;若 discriminant 触发,R-4b 用残差化版兜底。

### R-5 sampling 配套 sanity check note

R-1c 不替 R-5 决定 sampling distribution。但留 R-5 的 sanity-check input:

1. **R-1c metric 与 random sampling 不独立**:高 prominence 实体在 corpus 行多 → random sample 偏向高 Salience case → 低 Salience under-represented。Kong §2.2-style survivorship 的 Salience-driven 版。
2. **Pool G stratified by R-1c log1p(L1_mention_count)** 是自然平衡工具;**Pool H entity-balanced cap** 也能反向平衡。R-5 全权选 (R-0 §4 + R-1b downstream notes 一致)。
3. **Pilot 上 R-5 建议同时跑 random + Pool G 两种 sample**,R-1e 看 discriminant check + effect size 在两种 sample 下的稳健性。**这是建议,不是 mandate**。
4. **L1 mention + no tradable filter** 在 metric 层面已 collateral 缓解 Kong §2.2 anti-survivorship 警告(IPO 前 / 退市 / 停牌段 mention 进 count),但**不替代** R-5 sampling 层面工作。

### B-2 schema 内容需求

`factor_provenance.run_inputs.per_task.target_salience` 必须包含(字段命名 / 风格 / 与其它 R-X session 输出整合留 B-2 整体 session):

- `factor_name = target_salience`
- `framing_claim = corpus_exposure_intensity_cls_proxy`
- `source_layer = L1_mention`
- `row_unit = [article_id, target_entity_id]`
- `count_unit = L1_row`
- `reference_rows_filter`: none(no `is_subject` filter, no `tradable_at_event` filter, no `salience` filter)
- `family_key = [target_entity_id]`
- `event_collapse = all_supertypes_merged`(或 `none`)
- `reference_window`:`start = cls_corpus_first_published_at`,`end = min_fleet_model_cutoff`,`interval = half_open`(与 R-1b §6.1 同)
- `focal_article_policy`:R-1c 不需要排除同 `article_id`(L1 mention 的本意就是数 corpus 内 mention,包括 case 自身文章是否计入由 framing 决定 —— **阶段 1 stance:不排除同 `article_id`**,因为 framing C 是 "训练前累计曝光",case 自身那篇文章在 model cutoff 前发表的话也是预训练 exposure)。**为对称性,可选排除以匹配 R-1b §3 focal_article_policy = exclude_same_article_id;但 framing 上不是 R-1c 必需。** 留 B-2 / 用户拍板,见下"留给用户拍板的开放点"。
- `dedup_policy = inter_article_no_dedup__intra_article_one_row_per_article`(per R-0 §5)
- `zero_policy = keep_zero_log1p_zero`
- `transform = log1p`
- `tradable_filter = false`
- `requires_pool_d_or_l1_tradability_extension = false`
- `discriminant_check`:
  - `vs = r1b_log1p_recurrence_count_tradable_filtered`(per R-1b §5.3 / §8)
  - `vif_threshold = 10`
  - `abs_correlation_threshold = 0.90`
  - `fallback_metric = residualize_against_r1b_log1p_recurrence_count`
- `robustness_precommit_slots = 0`
- `appendix_conditional_l1_vs_l2_construct_check = { trigger_corr_threshold = 0.95 }`
- Provenance hashes(同 R-1b §6.2):S0 source snapshot / entity alias table / disambiguation rule / topic-classifier prompt-model-cache(注:R-1c target only,family 不用 super_type,**topic-classify 范围在 R-1c 自身需求里其实不必扩**,但 R-1b 已要求 topic-classify reference rows + case candidate rows,R-1c 沿用即可)/ subject-ID prompt-model-cache 或 deterministic rule(R-1c L1 mention 其实**不需要 subject ID**,但 case 主体是 P_predict tradable 必过 universal admissibility 还是要 subject ID,所以 hash 仍 relevant) / layer-view definition / fleet cutoff manifest / tradability master snapshot / sampling manifest。

### WS0.5 §3.3 重写指引

R-1c 落定后,WS0.5 §3.3 重写:

- §3.3.1 case admissibility: R-0 supersession note 已 lift 到 R-5 L3 base view,**移除整段**或重写为 "see R-5 admissibility filter at L3 base view";保留 reference 而非重复规则。
- §3.3.2 Target Salience metric: **重写**:
  - 改 framing 段为 "Target Salience proxies the entity's corpus exposure intensity during model pretraining, with CLS mention count as the best-available proxy. The framing acknowledges the gap that CLS is a proper subset of the model's pretraining corpus."
  - 改 metric 公式为 `log1p(target_l1_mention_count)`,where `target_l1_mention_count = COUNT( L1 rows where target_entity_id = case.target_entity_id AND published_at ∈ [cls_corpus_first_published_at, min_fleet_model_cutoff) )`。
  - 移除 "across all event types but only `salience=core` entities" 限制;改为 "any L1 row counts" 。
  - 加 dedup_policy / focal_article_policy / zero_policy 显式定义。
- §3.3.3 Discriminant check: 阈值沿用,fallback 改为 "residualize against R-1b log1p_recurrence_count"(不再列 complement-family / Baidu Baike)。
- §3.3 与 Historical Family Recurrence 的关系段:从 "Recurrence is the same-family slice of Target Salience(correlated by construction)" 改为 "Recurrence and Salience differ in **two** dimensions: (a) family granularity (target × super_type vs target only); (b) source layer (L2 subject + tradable vs L1 mention)。两者只在 fixed window 上共享,construct 维度有结构性区别。VIF/correlation 在 case sample 上算,与 cohort 一致性无关。"

### R-1d / R-1a 不受 R-1c 影响声明

- R-1d Template Rigidity 是 case-level 纯文本特征,与 R-1c 在 L1↔L3 容器边界与 R-4a 框架级 8 条上并行,**无直接耦合**。R-1c 不预约束 R-1d 任何选择。
- R-1a Cutoff Exposure 是 case×model 时间因子,与 R-1c case-level Salience 是 R-1e primary 候选两个不同 bloc(Bloc 0 时间 vs Bloc 2 prominence),无直接耦合。**R-1c 不动**。

---

## 留给用户拍板的开放点

我的判断已对所有 8 个决策点给明确 stance。但以下 **1 个边界点**值得用户在 finalize 前确认:

### 开放点 A:`focal_article_policy` — R-1c 是否排除同 `article_id`?

R-1b 锁了 `focal_article_policy = exclude_same_article_id`(R-1b §3),因为 R-1b reference rows 是历史复现,case 自身文章不应被自己算复现。

R-1c framing C 是 "训练前累计曝光",case 自身文章在 model cutoff 之前发表的情况下,**它也是预训练 exposure 的一部分**。所以从 framing 看,**不应**排除同 `article_id`。

但是:
- pilot 80 pre-cutoff 的 case 都在 model cutoff 之前 → 它们的文章是预训练 exposure → R-1c L1 mention count 包含 case 自身文章那一行,合理。
- pilot 700 post-cutoff 的 case 在 model cutoff 之后 → 它们的文章**不在** `[corpus_start, min_cutoff)` 窗口内,所以不影响。

**结论**:R-1c **不需要** `exclude_same_article_id` policy,framing C 下 case 自身文章在窗口内时是 exposure 一部分。但**与 R-1b 不对称**(R-1b 排除,R-1c 不排除)。

**我的推荐 stance**:**R-1c 不排除同 `article_id`**(framing C 决定)。但若用户判断"对称美 / discriminant check 口径一致"更优先,可改为排除 —— **决策不会改 R-1c 主体设计**,只是边界一个 ±1 mention 的差异(对单 case 计数大多数情况影响 <5%)。

请用户在 finalize 时一句话确认这一开放点 stance。

### 开放点 B(次要):是否 pre-commit "stretch goal cross-corpus signal" appendix slot?

我阶段 1 选 0 pre-commit + 1 appendix conditional。如果用户认为外部 cross-corpus 信号(百度搜索量 / 维基中文 page view / 其它金融媒体)在论文 future-work 段值得 reference,可以 pre-commit 一个 stretch-goal robustness 段(不强制本论文实现,只为 paper narrative 留口子)。

**我的 stance**:**不 pre-commit**。stretch goal 在论文 §future work 或 discussion 段提及即可,robustness slot 应只给 actual computed values。**论文不写无数据的 robustness slot**(memory `feedback_doc_for_llm_context` 同精神 —— load-bearing docs 不写空槽)。

如果用户判断 paper positioning 需要 anchor 这个 future direction,我也接受改为 1 pre-commit slot,内容 = "framework expandable to cross-corpus prominence signals (Baidu / Wiki / 其它金融媒体);present paper limits to CLS-internal evidence"。但**这是 paper narrative 段而非 robustness section**,严格意义上不应占 robustness slot。

请用户在 finalize 时一句话表态(默认沿用我阶段 1 推荐:不 pre-commit)。

---

## R-1c 文档惯例 hand-off

按项目 documentation pattern(memory `feedback_doc_for_llm_context` 2026-05-24 update):本 session 产出 audit-trail(本文件 + Codex 并行白板) + 一份 < 200 行 time-static `R1c_DECISIONS.md`(canonical for downstream agents)。

`R1c_DECISIONS.md` 等用户双源对照后由主 session orchestrate 写。本白板分析是输入之一,不是 canonical lock-in 本身。

---

**End of Claude sub-agent stage 1 + stage 2 whiteboard.**
