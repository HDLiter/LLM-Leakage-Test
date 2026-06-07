# R-1c Target Salience 白板分析

生成时间: 2026-05-25

方法: 两阶段 clean-room。阶段 1 只读 kickoff 允许材料并先写入
`whiteboard_analysis_stage1_codex_draft.md`；阶段 2 才读取 WS0.5 §3.3、WS0.5-era
旧提案、R-1b construct audit trail、Kong sanity check 与补充文献。

---

## 阶段 1 白板结论

### (1) Stance / framing: Target Salience 测什么

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| A. CLS-内 prominence | 说法最诚实:就是 CLS 内目标曝光 | 与模型真实训练语料之间有 gap | 可作为措辞护栏 |
| B. General fame / public attention | 直觉强,接近"出名" | 若主 metric 仍只用 CLS,就需要外部信号撑桥 | 不做主 framing |
| C. Corpus exposure intensity, CLS proxy | 对准 memorization 的 exposure channel,同时承认不可观测 | reviewer 会问为什么 CLS 能 proxy 训练语料 | **主选** |

#### 主选

主选: **C, 但用 A 的诚实措辞约束 claim**。

论文句子应写成:

> Target Salience 是目标实体在可观测 CLS 中文金融新闻语料中的曝光强度,用作模型预训练语料中该实体曝光强度的 domain-specific proxy。

不要写成"模型实际见过多少次",也不要写成"公众知名度"。CLS 不是 Common Crawl / 百科 / 论坛 / 财经数据库的全集,只能做同域、同语言、同新闻风格的 proxy。

Carlini 2023 可以作为机制锚点,但只能这样用:训练数据里的重复频次会提高 memorization / extraction；CLS count 是我们能观测到的中文金融新闻曝光 proxy。不能把 Carlini 的 training-data frequency 直接偷换成 CLS frequency。

#### 这个 framing 对后 7 项的约束

- Construct 应偏宽,因为 exposure 不是"只有主体文章才算"。
- Family 应是 target-only,因为 prominence 是实体属性,不是事件家族属性。
- Denominator 不必做复杂 share,因为 fixed common window 下分母是常数。
- Window 应固定到所有模型共同可见的 `[corpus_start, min_cutoff)`。
- Tradable filter 不应进入 salience reference rows,因为实体被看见不要求当时可交易。
- Discriminant check 必须做,因为 target fame 与 target-event recurrence 会相关。
- Robustness 应检查尾部 leverage 与 proxy 局限,不是把 R-1c 扩成外部 fame 数据工程。

#### 兼容性 check

- R-0: 在既有 L1/L2/L3 容器内算,不新增层,不依赖 operator。
- R-4a: 产出 case-level continuous factor,主报 effect size + 95% CI 可消费。
- R-1b: 与 locked recurrence 的 outcome-leakage framing 区分清楚。
- 下游: `log1p(0)=0` 可直接进 R-1e / R-4b。

#### R-5 sampling sanity check

这个 framing 天然暴露 sampling 耦合:高媒体覆盖实体在语料中有更多 case,按 case 随机抽会过采高 salience target。这不是 metric 错,而是 population choice。R-1c 不替 R-5 拍 Pool H / entity cap,但必须把这个 note 交给 R-5。

#### 留给下游

R-1e 可因 pilot 弱信号或 collinearity drop 掉 Salience。R-5 可选择自然 case distribution 或 entity-balanced distribution。R-1c 只锁 factor 定义。

### (2) Construct: 数哪一层 row

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| L1 mention | 最贴近"模型看见过目标实体";保留顺带提及 | 噪声更宽,与 sampling 耦合更强 | **主选** |
| L2 subject | 更像"关于目标的文章";更干净 | 把 exposure 缩成 subject-only,接近 R-1b | 不做主选 |
| L1 + tradable | 宽曝光 + 市场口径 | 触发 Pool D,且 tradable 与 salience claim 正交 | 不选 |
| L2 + tradable | 与 R-1b 同 construct | 高相关风险,把 Salience 变成 Recurrence 近邻 | 不选 |

#### 主选

主选: **L1 entity-mention row**。

计数单位是一个 `(article_id, target_entity_id)` row,不是同一篇文章里字符串出现几次。`mention_count_in_article` 可保留作审计字段,但主 count 不求和。原因很直接:一篇 CLS 电报反复提同一实体五次,更像一个 article-level exposure event,不是五个独立训练样本。

#### "与 R-1b 同" vs "与 R-1b 分家" 的判决

我站 **分家**。

同 construct 派的最强论证是:同一 row universe 上比较 R-1b/R-1c,VIF 更容易解释,也减少 measurement variance。

但这会让 R-1c 失去自己的 construct。R-1b 已锁为 L2 subject + tradable + event_super_type,它测 outcome-bearing family recurrence。R-1c 要测 target exposure。顺带提及"茅台"的行业新闻不是茅台某事件家族的复现,但它确实让模型多看见一次"茅台"及其上下文。Salience 应数这个。

VIF check 不要求两个变量同 row universe。它问的是最终 case-level 数值是否冗余。不同 construct 的两个变量如果高度相关,照样会被 check 抓到。

#### 替代方案与何时换

只有在 B-2 发现 L1 entity match 噪声高到不可接受时,才退到 L2 subject。不要为了"和 R-1b 可比"退到 L2 + tradable。

#### 兼容性 check

- R-0: L1 已定义,保留 non-tradable rows,不触发 Pool D。
- R-4a: pre-operator factor。
- R-1b: 与 R-1b 主 construct 清楚分离。
- B-2: 需记录 L1 source layer、row unit、count unit、entity alias/disambiguation hashes。
- Topic-classify: 主 target-only metric 不需要给全 L1 跑 topic-classify。

#### R-5 sampling sanity check

L1 mention 会放大 row-random sampling 与 salience 的机械关系,因为有更多 L1 曝光的实体往往也有更多可抽 case。R-5 应显式说明是否接受这种自然媒体覆盖分布。

#### 留给下游

R-5 可用 entity cap / Pool H 控制 mega-target 占比。R-1e 用 pilot 看 L1 口径是否有独立解释力。

### (3) Family granularity / event collapse

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| target only | 最贴近实体 prominence | 会与 target-event recurrence 有相关 | **主选** |
| target x complement-super_type | 与 R-1b disjoint | 同一 target 的 salience 随 case event 变,直觉怪 | fallback |
| target x super_type reweighting | 试图去事件频率偏差 | 权重难解释,像 cherry-pick | 不选 |
| industry / concept | 稀疏性更低 | 换成行业先验,不是目标实体 salience | 不选 |

#### 主选

主选: **target only, across all event types**。

公式形状:

```text
target_salience_count[case] =
  COUNT(L1 rows r in fixed window
        where r.target_entity_id == case.target_entity_id
        and r.article_id != case.article_id)
```

排除同一 `article_id` 是为了避免 focal article 自己把低曝光 case 从 0 推到 1,尤其是 pre-min-cutoff case。其它不同 article 的原报、转发、追踪按 no-dedup 计。

#### 为什么不把 complement 做主口径

Complement-super_type 适合作 fallback,不适合作主 metric。否则会出现"茅台很出名,但这个 case 是财报,所以财报新闻不算茅台 salience"这种难解释口径。Prominence 不应随 case event type 改变。

#### 兼容性 check

- R-0: target-only 可在 entity-first 后直接算。
- R-4a: 一个 continuous factor,zero 合法。
- R-1b: family 维度不同于 `(target_entity_id, event_super_type)`。
- 下游: B-2 可不扩 topic-classify 范围,除非 fallback 激活。

#### R-5 sampling sanity check

target-only 是最能揭示 media-coverage bias 的口径。若 R-5 选择 Pool G,我的建议是:一旦 R-1c 锁定,Salience 分层就用 R-1c metric,不要继续用 R-1b recurrence 代理 salience。Recurrence 可作为另一条分层轴,但不应偷换。

#### 留给下游

R-5 决定是否做 salience-stratified / entity-balanced。R-1e 决定 Salience 是否进入 primary。

### (4) Denominator

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| `log1p(count)` | 简单,贴近 frequency 机制,zero 自然 | 受 corpus 规模影响 | **主选** |
| per-article share | 相对量 | fixed window 下只是常数缩放,数值挤在 0 附近 | 不选 |
| per-L1-row / all-target share | corpus-share 解释清楚 | 同样多是常数缩放,不解决核心问题 | provenance only |
| industry share | 行业内 prominence | 变成行业内相对地位 | 不选 |
| rank / percentile | 抗尾部 | 丢绝对频次尺度 | appendix sensitivity |

#### 主选

主选: **`log1p(target_l1_row_count)`**。

fixed common window 让分母在所有 case 上相同,所以 share 不提供真正的可比性增益。count 是 exposure proxy；`log1p` 处理重尾并保留 0。

原始 count 必须存。语料窗口内 S0 article 总数、L1 row 总数、all-target mention 总数可作为 provenance 存,但不进入主变量。

#### 替代方案与何时换

若 pilot 显示极少数 mega-target 支配回归,appendix 用 percentile 或 winsorized log count 做 tail-leverage sensitivity。不要把 percentile 升为 main,除非 raw log count 完全不可用。

#### 兼容性 check

- R-0/R-4a: `log1p(0)=0`,no-dedup 合法。
- R-1b: transform 与 recurrence 一致,但 construct/family 不同。
- R-4b: 可估计 variance、zero rate、tail concentration、VIF。

#### R-5 sampling sanity check

count 保留自然 skew。若 R-5 按 case random,高 count target 可能也有更多 sampled rows。R-5 可平衡,但 R-1c 不应用 percentile 主变量把 population skew 藏掉。

#### 留给下游

R-4b 可标准化 logged value。R-1e 可比较主 count 与 appendix percentile 的方向稳定性。

### (5) Lookup window

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| shared fixed `[start, min_cutoff)` | 所有模型共同可见,case-level | 低估晚 cutoff 模型 exposure | **主选** |
| case-relative `[T-X, T)` | 像"事件前热度" | post-cutoff case 会数进模型没见过的后期文本 | 不选 |
| fixed latest_cutoff | 数据更多 | 早 cutoff 模型不可见 | 不选 |
| per-model window | 更接近真实 exposure | 变 case x model,与 Cutoff Exposure 打架 | 不选 |

#### 主选

主选: **与 R-1b 共享 fixed half-open window**:

```text
[CLS first published_at, min(fleet model cutoff))
```

这是保守但干净的 common-exposure slice。它让 Target Salience 仍是 case-level factor,也让 R-1b/R-1c discriminant check 在同一时间段上跑。

#### 替代方案与何时换

R-1c 不切到 latest cutoff 或 per-model。若将来想测 model-specific target exposure,那是另一个 factor,不是 Target Salience 主定义。

#### 兼容性 check

- R-0: fixed window 合法。
- R-4a: case-level factor。
- R-1b: window 同口径,便于 VIF/correlation。
- 下游: `fleet_cutoff_manifest_hash` 必入 B-2 provenance。

#### R-5 sampling sanity check

对 2025-2026 case,Salience 仍只看 2020 到最早 cutoff 的曝光。若某目标 2024 后突然爆红,这个 metric 故意不数那部分,因为不是全 fleet 共同可见。R-5 抽样时不要把这个解释成当前热度。

#### 留给下游

R-1a 继续负责 cutoff exposure。R-1c 不吸收 temporal exposure 的角色。

### (6) Tradable filter

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| 加 tradable | 与 R-1b 更像 | fame/exposure 不要求可交易;L1 还要扩字段 | 不选 |
| 不加 | 贴住 exposure claim;不触发 Pool D | 与 R-1b row universe 不同 | **主选** |
| 只分母加 | 试图折中 | 半生不熟,难解释 | 不选 |

#### 主选

主选: **Salience reference rows 不加 tradable filter**。

原因:模型预训练时可以看见上市前、停牌、拟上市、退市相关文本。实体是否可交易是 P_predict focal case admissibility 和 R-1b outcome-bearing recurrence 的条件,不是 entity exposure 的条件。

case 主体仍来自 L3 base view,必须 `tradable_at_event=true`。这里说的是历史 reference rows。

#### construct 一致性 vs claim 贴合

我选 claim 贴合。R-1b 加 tradable 是因为它测 outcome-leakage proxy。R-1c 测 target exposure,tradable filter 会把 construct 拉歪。VIF 解释复杂一点,但仍是正确问题:最终两个 case-level 变量是否冗余。

#### 替代方案与何时换

只有 R-1e/owner 明确把 Target Salience 改定义为"tradable-market attention"时才加 tradable。那是 framing 改变,不是实现细节。

#### 兼容性 check

- R-0: L1/L2 保留 non-tradable rows;L3 过滤 focal subjects。
- Pool D: 主 R-1c 不触发。
- B-2: `tradable_filter = none_for_salience_reference_rows`。

#### R-5 sampling sanity check

不加 tradable 可能提高有 pre-listing 或 non-tradable 覆盖目标的 salience。这符合 exposure claim。R-5 不应把它解释成"可交易市场关注度"。

#### 留给下游

R-5 仍只抽 tradable focal cases。R-1c 不要求把 non-tradable focal cases 放进 benchmark。

### (7) 与 R-1b discriminant check 边界

#### 阈值

沿用 standing routine:

```text
VIF >= 10 or |r| >= 0.90
```

不收紧。Salience 和 Recurrence 同源于 CLS count,中等相关是预期,不是失败。不放宽。若几乎同一个变量,就不应同时进 primary。

#### 主比较口径

```text
R-1c main = log1p(target_l1_row_count)
R-1b locked = log1p_recurrence_count
```

R-1b locked input 是 L2 subject + tradable + `(target_entity_id, event_super_type)`。

#### fallback metric 形态

若触发阈值,切到 **L1 complement-super_type fallback**:

```text
fallback_salience_count[case] =
  COUNT(L1 rows r in same fixed window
        where r.target_entity_id == case.target_entity_id
        and r.article_id != case.article_id
        and r.event_super_type != case.event_super_type)

fallback_target_salience = log1p(fallback_salience_count)
```

它保留 L1 exposure construct,但排除 case 自己的 event super_type,从而与 R-1b 的 same-super_type recurrence 拉开。它不如 target-only 直观,所以只作 fallback。

不推荐 residualizing salience against recurrence。残差依赖样本和变量进入顺序,不是一个好复现的 factor。

如果 fallback 仍超阈值,不要继续发明第三个 metric。R-1e 应把两者视作经验冗余,选择或降级其中一个。

#### 兼容性 check

- R-0: fallback 需要 L1 rows 有 `event_super_type`;可能条件性扩 topic-classify 范围。
- R-4a: 仍是 pre-operator factor。
- R-1b: 遵守 standing routine。
- B-2: 记录 fallback 是否激活、激活后的 row filter。

#### R-5 sampling sanity check

VIF/correlation 应在 pilot / actual sampled frame 上算,不是只在 full corpus 上算。采样策略会改变相关性:row-random 可能升高,entity-balanced 可能降低。

#### 留给下游

R-1e 决定冗余时的 factor 选择。R-1d 不受此影响。

### (8) Robustness / appendix candidates

#### 候选清单与 trade-off

| 候选 | 优点 | 主要问题 | 判断 |
|---|---|---|---|
| 0 个 | 最简 | Salience count 重尾风险未显式检查 | 不够 |
| share-vs-count | 看似自然 | fixed window 下 share 多是常数缩放 | 不做 |
| cross-corpus | 支撑 fame framing | 覆盖、成本、可复现都麻烦；且未选 B framing | 不预承诺 |
| window sensitivity | 可看时间稳定性 | 容易变 grid | 不主推 |
| tail-leverage sensitivity | 直接检查 mega-target 是否驱动结果 | 是 appendix,不是新 construct | **主选 1 个** |

#### 主选

预 commit **1 个 appendix robustness slot**:

```text
Tail-leverage sensitivity:
  用 target_l1_row_count 的 percentile rank 或 winsorized log1p count
  重跑 R-1c 系数,检查方向和量级是否由极少数 mega-target 驱动。
```

具体用 percentile 还是 winsorized log,由 B-2/R-4b 在 pilot analysis 前固定。这个 slot 不改变 main metric。

不预 commit cross-corpus fame slot。可以未来 optional appendix 做 CLS salience 与百度/维基/其它媒体信号的相关性,但不要让主 benchmark 依赖外部覆盖。

#### 兼容性 check

- R-4a: appendix label,不做 family-wise correction。
- R-1b: discriminant fallback 与这个 robustness 分开。
- R-4b: primary power 用 main log count；appendix sensitivity 只辅助解释。

#### R-5 sampling sanity check

tail sensitivity 同时检查 sampling 是否被少数高曝光 target 支配。但它不替代 R-5 的 entity-balanced / capped sampling 决策。

#### 留给下游

R-4b 固定 winsor cutoff 或 percentile implementation。R-1e 看 pilot 后决定 Salience 是否进 primary。

---

## 阶段 2 对照

### 1. 与 WS0.5 §3.3 现状对照

#### 保留: log CLS count 取代 market cap / index ordinal

WS0.5 §3.3 把 v0.3 的 `static_reach` ordinal、市值/指数/metadata salience 删除,改为 `log1p(cls_target_mention_count)`。阶段 1 独立得到同方向:市场规模不是 fame,也会错分小市值高覆盖的妖股 / 热门事件股。

Verdict: **保留方向**。旧 reviewer / user 当时推对了:Target Salience 应是 corpus exposure proxy,不是 firm-size proxy。

#### 保留: Salience 是 scorer,不是 admissibility pre-filter

WS0.5 已把 centrality/tradability 从 Target Salience scorer 中剥离。R-0 又把它提升为 L3 base view / R-5 admissibility。阶段 1 同意:Target Salience 不应携带 target_validity flag 或 NA path。

Verdict: **保留,但按 R-0 改写**。旧 §3.3.1 的 pseudocode 只能当历史说明,不是 R-1c metric 定义。

#### 保留: fixed earliest-cutoff window

WS0.5 的 shared earliest-cutoff window 与阶段 1 一致。它避免 case-relative window 把模型 cutoff 后文本数进 exposure。

Verdict: **保留**。这不是 prototype 惯性,是正确的最小可辩护选择。

#### 修正: "Salience 与 Recurrence 只差 event-family filter" 已过时

旧 §3.3.2 写 Target Salience 与 Recurrence "only difference is event-family filter",且 Recurrence raw count 是 Salience sub-count。R-1b 已锁后,这句话不再成立。

现在:

- R-1c main = L1 all mentions, no tradable, target-only。
- R-1b = L2 subject, tradable, target x event_super_type。

Verdict: **必须重写**。两个 factor 不再是同一 pipeline 的 all-event vs same-event slice。它们共享 fixed window 和 entity IDs,但 construct、row layer、tradable filter、family key 都不同。

#### 修正: fallback 二选一要锁死

旧 §3.3.2 把 fallback 写成 complement 或 Baidu Baike entry length,留 addendum。阶段 1 锁为 complement-super_type fallback,不选 Baidu Baike。

Verdict: **采纳 complement fallback,删除 Baidu Baike fallback**。外部 proxy 会改变 framing、覆盖和可复现边界,不适合当 standing fallback。

### 2. 与 frontmatter `revision_basis` 历史链对照

#### C-1: 从 ordinal / market metadata 改成 corpus count

Verdict: **保留**。C-1 的方向对:市值/指数是 size/reach,不是 observed exposure。阶段 1 独立推出 count metric。

#### C-2: shared fixed pre-cutoff window

Verdict: **保留**。阶段 1 独立推出同一窗口,但 R-1c 是自己选择共享,不是被 R-1b 强制。

#### C-3: continuous `log1p`

Verdict: **保留**。频次本身是 construct,不应先切 ordinal / tertile。bin 可用于 sampling,不是 main factor。

#### C-4: no-dedup

Verdict: **保留**。重复曝光是 exposure construct 的一部分。R-0 已锁 no-dedup 合法。

#### S-6: VIF + Pearson 最小诊断

Verdict: **保留**。VIF / Pearson 足够。condition number、partial correlation、GVIF 属于旧 reviewer ratchet,不需要复活。

#### 需要 revert 的链条

- v0.2 Issue #2 的 ordinal salience / metadata scorecard: **revert**。
- "R-1c 复用 §5 recurrence pipeline near-zero cost" 的实现叙事: **revert / 改写**。R-1c main 不需要 topic-classify;R-1b 也已不是旧 mention pipeline。
- "Target Salience 和 Recurrence 只差 event filter" 的 construct 叙事: **revert**。
- Baidu Baike fallback: **revert**。

### 3. 与 WS0.5-era Codex 旧提案对照

旧提案主推 Metadata-Anchored Market-Reach Salience,并明确说不要用 CLS historical mention counts。这是阶段 1 的主要冲突点。

Verdict: **推翻旧提案主方案**。

旧提案当时担心 CLS mention count 与 recurrence 重叠,所以用 market reach / metadata 维护 non-redundancy。这是用一个弱 proxy 逃避 collinearity。现在 R-0/R-1b/R-4a 已给更好的处理:

- R-1c 可直接用 count；
- R-1b 与 R-1c 在 construct/family 上分家；
- 高相关由 VIF/correlation 和 complement fallback 处理；
- 是否进 primary 由 R-1e + pilot 决定。

旧提案保留价值:

- 目标选择不能交给 P_predict 模型临场推断:保留为 R-5/B-2 manifest 规则。
- null target 不进 final P_predict manifest:保留为 R-5 admissibility。
- 不把 Target Scope / Tradability Tier 偷塞成额外 confirmatory factors:保留。

旧提案应撤销:

- 3-level ordinal salience；
- market cap / index / institution list 做主 salience；
- `|rho| < 0.50` / VIF `< 3` 的过紧阈值；
- 禁止 CLS historical mention counts。

### 4. 与 R-1b whiteboard / construct stress-test 对照

R-1b stress-test 结论是:Recurrence 不是 pure exposure proxy,而是 outcome-leakage proxy,所以锁 L2 subject + tradable。这个结论反而支持 R-1c 与 R-1b 分家。

Verdict: **借鉴 framing 方法,不照搬 construct**。

R-1b 选择 L2 subject + tradable 的理由是 outcome-bearing historical rows。R-1c 的 framing 是 entity exposure proxy。Carlini text-frequency anchor 对 R-1c 更直接,因为 R-1c 不需要 outcome-bearing filter。换句话说:

- R-1b: "同一标的 + 同类事件 + 可交易 outcome" 重复多少。
- R-1c: "这个标的作为文本实体被看见过多少"。

所以 R-1b 的 L1 mention 排除语句不能移植到 R-1c。R-1b 说 L1 mention 更像 Target Salience；R-1c 正是要测这个。

### 5. Kong §2.2 sanity check

Cross-synthesis 早期把 Kong §2.2 写成对 CLS mention count 的 endorsement。阶段 2 读完后,我认为要降级。

Kong 的有用点是:media coverage 与 corporate activity / investor attention 相关,失败或悄然退出的公司会 underrepresented。这提醒我们 Target Salience 与 sampling population 强耦合。

Verdict: **Kong 是反向 sampling sanity check,不是 metric endorsement**。

它不能证明"CLS mention count 是最好的 salience metric"。它提醒:

- 若按 case random,媒体覆盖高的实体会自然更多；
- 若过度 entity-balanced,又会改变自然 CLS population；
- R-5 必须显式说明抽样目标 population；
- R-1c 报告 salience effect 时要避免把 media coverage bias 包装成纯模型机制。

这与阶段 1 的 sampling note 一致。

### 6. 同行文献对照

#### Carlini 2023

Carlini 的核心结果是 memorization 随模型规模、训练数据重复频次、prompt context 长度增加而近 log-linear 上升。阶段 1 的 `log1p(count)` 与这个方向一致。

但 Carlini 数的是 actual training data duplicates。R-1c 数的是 CLS proxy corpus。最终报告必须保持这个边界。

Verdict: **支持 frequency/log-count 形状,不支持把 CLS count 写成真实训练频次**。

#### Tirumala 2022

Tirumala 显示更大模型更快记忆训练数据,且 nouns/numbers 等近似 unique identifier 更早被记住。Target 实体名在金融新闻中正是强 identifier。阶段 1 的 L1 mention 口径与这个机制相容。

Verdict: **支持 entity exposure / identifier framing**。

#### Shi 2024 / Min-K

Shi 的 pretraining-data detection 用 pre/post 时间构造 member/non-member,并发现 detection 难度与 model size、text length、occurrence frequency 等因素相关。它支持"更长/更频繁文本更容易显露 membership/memorization"的方向,但不替 R-1c 选 denominator。

Verdict: **支持 frequency as factor;不支持复杂 share/rank 主变量**。

#### AntiLeakBench 2025

AntiLeakBench 强调 post-cutoff updated knowledge 和 human verification。它对 R-1c 的直接帮助较小,但支持我们把 cutoff/window 与 data quality audit 写清楚。

Verdict: **支持 fixed cutoff discipline 和 quality transparency;不是 salience construct anchor**。

---

## 最终综合推荐

| 决策点 | 最终选择 | 一句话理由 |
|---|---|---|
| (1) Framing | CLS-measured corpus exposure proxy | 对准 memorization exposure channel,但不把 CLS 冒充真实训练全集 |
| (2) Construct | L1 entity-mention row | Salience 测"目标被看见多少",不是"目标是主体多少次" |
| (3) Family | target only, all event types | Prominence 是实体属性;event split 留给 R-1b |
| (4) Denominator | `log1p(count)`,无主分母 | fixed window 下 denominator 基本是常数,count 最贴近频次机制 |
| (5) Window | fixed `[CLS start, min_fleet_cutoff)`,half-open | 全 fleet 共同可见,保持 case-level |
| (6) Tradable filter | 不加 | exposure 不要求当时可交易;避免无谓 Pool D |
| (7) Discriminant | VIF >= 10 或 `|r| >= 0.90`;fallback = L1 target x non-case-super_type count | 沿用 minimal check;fallback 可解释且可复现 |
| (8) Robustness | 1 个 appendix tail-leverage sensitivity | 检查 mega-target 是否驱动结果,不扩成外部 fame 工程 |

最终主公式:

```text
target_salience_count[case] =
  COUNT(L1 entity-mention rows r WHERE
    r.target_entity_id == case.target_entity_id
    AND r.published_at >= cls_corpus_first_published_at
    AND r.published_at < min_fleet_model_cutoff
    AND r.article_id != case.article_id)

target_salience[case] = log1p(target_salience_count[case])
```

Main metric 不加 `event_super_type`,不加 `tradable_at_event`,不求和 `mention_count_in_article`,不做 dedup。

---

## 对下游的约束 / 留下的选择空间

### R-1e input

R-1c 不承诺 Target Salience 一定进 primary。R-1e 用 pilot 的 effect size、variance、zero/nonzero rate、tail concentration、与 R-1b VIF/correlation 决定。

### R-2 不变

R-1c 不改变扰动 inventory 或 perturbation-specific eligibility。C_anon / C_FO / C_NoOp 等仍由 R-2/R-6 定。

### R-5 sampling note

R-5 必须显式处理这个事实:case-random sampling 会自然偏向高 salience target。若 Pool G 是 salience 分层,应使用 R-1c `target_salience`；若 Pool G 是 recurrence 分层,用 R-1b `log1p_recurrence_count`。不要再用 recurrence 代理 salience。

Pool H / entity-balanced / cap 是否启用,仍由 R-5 决定。R-1c 只要求 R-5 在 population 说明里正面回应 media-coverage coupling。

### B-2 schema 内容需求

`factor_provenance.run_inputs.per_task.target_salience` 至少记录:

- `source_layer = L1_entity_mention`
- `row_unit = [article_id, target_entity_id]`
- `count_unit = L1_entity_mention_row`
- `family_key = [target_entity_id]`
- `reference_rows_filter = target_entity_id match; fixed window; exclude same article_id; no tradable filter`
- `reference_window.start = cls_corpus_first_published_at`
- `reference_window.end = min_fleet_model_cutoff`
- `reference_window.interval = half_open`
- `fleet_cutoff_manifest_hash`
- `focal_article_policy = exclude_same_article_id`
- `dedup_policy = no_dedup_across_articles; one row per article-target`
- `intra_article_mentions_policy = do_not_sum_mention_count_in_article_for_main`
- `zero_policy = keep_zero_log1p_zero`
- `transform = log1p`
- `denominator = none_for_main; corpus totals stored as provenance`
- `tradable_filter = none_for_salience_reference_rows`
- `requires_pool_d_or_l1_tradability_extension = false`
- `topic_classify_required_for_main = false`
- `discriminant_threshold = VIF >= 10 or abs(r) >= 0.90`
- `fallback_policy = L1 target x non-case-super_type count if threshold triggers`
- `topic_classify_required_for_fallback = true_if_fallback_activated`
- `appendix_tail_sensitivity = percentile_or_winsorized_log_count`

### R-4b power input

R-4b 需要:

- raw `target_salience_count`
- `target_salience = log1p(count)`
- zero rate / nonzero rate
- distribution by target and by sampled frame
- top-target concentration, e.g. top 10 targets' share of sampled rows
- correlation / VIF vs R-1b recurrence
- fallback metric distribution if triggered
- appendix percentile/winsorized metric if used

### R-1d 不受影响

Template Rigidity 是纯文本/模板化 factor。R-1c 不对 R-1d construct、window、row layer 施加约束。

### WS0.5 §3.3 重写指引

重写 §3.3 时:

1. 删除 Target Salience 与 Recurrence "only event filter differs" 的句子。
2. 把 Target Salience 写成 L1 target-only exposure proxy。
3. 把 central/tradable pre-filter 全部指向 R-0 / R-5 L3 base view。
4. 保留 fixed window、`log1p(count)`、VIF/Pearson minimal diagnostics。
5. 删除 Baidu Baike fallback。
6. 说明 main metric 不需要 topic-classify;只有 fallback 需要 L1 `event_super_type`。
7. 把 Kong §2.2 放在 sampling caveat,不要写成 metric endorsement。

---

## 留给用户拍板的开放点

1. 是否接受主口径排除 focal `article_id`。我建议排除,因为否则 pre-min-cutoff case 的最低 salience 会被自身机械抬到 1。
2. Appendix tail sensitivity 用 percentile rank 还是 winsorized log count。我的偏好是 winsorized log count,因为它保留频次尺度；percentile 更容易解释。
