# R-1d 模板刚性(Template Rigidity)— 最终决策

**状态**: 锁定 2026-06-02(定义 + 候选池准入)
**结局**: **进入 R-1e 候选池(confirmatory 候选)**
**pilot 前闸门**: 操作化必须在真实 CLS 数据上跑出经用户审计通过的计算方法,
方可进入 pilot。未通过此闸门 → 直接 DROP,不重开 R-1d 定义。

**审计轨迹**(下游 agent 不需要读;只在 debate / 翻推导过程时查):
- `whiteboard_analysis.md` — session 摘要(Q1–Q6 对话)
- `channel_analysis.md` — 四条影响通道 + pilot 预期特征
- `subfield_lit_scan.md` — Codex 文献扫描:NLP 中量化文本模板化程度的方法

---

## 1. 定义

Template Rigidity 量的是:**一篇文章有多大比例由 CLS 语料库高频文本片段组成。**
高频片段 = 不变的模板骨架;rigidity 高意味着文章大部分是套路框架,可变槽位少。

与 P_logprob(Min-K%)的概念镜像关系:P_logprob 看的是**最不常见**的 token
(有多意外);Template Rigidity 看的是**最常见**的 n-gram(有多套路)。
两者量的是同一频率分布的相反两端。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(语料固有属性;把所有模型拿走,这个属性还在) |
| 粒度 | **article 级**(同一 article_id → 同一 rigidity,不因 focal entity 而异) |
| 泄露机制链环节 | **③ 可记忆性**(文本结构影响模型如何处理/存储内容) |
| 影响通道(经验性,不预判) | 近邻记忆 / 偏见强化 / 泛化替代 / 纯表面熟悉度(详见 `channel_analysis.md`) |

**方法论先例**:
- **Lang & Stice-Lawrence (2015)** *Textual Analysis and International
  Financial Reporting* — 用 tetragram(4-gram)boilerplate share 量化英文 10-K
  年报的模板化程度。我们的操作化(CLS 语料高频 n-gram 覆盖率)直接借鉴自此。
  主要差异:中文 CLS(非英文 10-K)/ jieba 分词(非空格切词)/ Top-K% 平均
  DF 聚合(非二元句级覆盖)/ 异质语料(非单一文体)。
- **Rusty-DAWG (Meister et al. 2024, arXiv 2406.13069)** — 提出 **n-novelty**
  (文档中有多少 n-gram 在参考语料里找不到);我们量的是互补面
  (1 − n-novelty ≈ 模板化程度)。可作为备选实现路径。
- **Forsyth & Grabowski (2015)** — **Hapaxity** 等公式化程度指标;量的是文本
  多大程度依赖不可替换的固定片段。可作为稳健性备选。
- **直接先例空白**:无已发表工作把文本模板化程度作为 LLM 记忆/行为的调制因子;
  中文金融新闻模板化度量亦无先例。
- 完整文献扫描 → `related papers/notes/text_template_boilerplate.md`

---

## 2. 参考语料

| 字段 | 值 |
|---|---|
| 语料 universe | **L1 去重文章集**(L1 entity-matched rows 按 `article_id` 去重) |
| 为什么是 L1 而非 S0 | 过滤掉非金融内容(国际/政治/体育);DF 含义 = "在金融实体相关的 CLS 新闻里有多常见" |
| 为什么不是 L2 | L2 加了 `is_subject` + `tradable` 过滤,跟文本结构无关;会排除有用的模板信号 |
| 参考窗口 | `[CLS 语料起始, min(fleet model cutoff))`,半开,跟 R-1b/R-1c 同源 |
| 去重 | 按 `article_id`;一篇文章不论匹配到多少实体只计一次 |

---

## 3. 操作化框架

```
DF[ngram] = COUNT(DISTINCT article_id a WHERE ngram IN a.word_ngrams
            AND a.published_at >= cls_corpus_first
            AND a.published_at < min_fleet_cutoff)

article_ngrams[case] = word_ngrams(case.article.content)
top_k_ngrams[case]   = TOP K% of article_ngrams[case] BY DF DESC
template_rigidity[case] = MEAN(DF[ng] for ng in top_k_ngrams[case])
```

**主聚合候选**:Top-K% 平均 DF(与 Min-K% 形成镜像——一个看最罕见尾,一个看
最常见尾)。备选聚合方式(高频覆盖率、全均值)并行计算用于对比。

### Open items(全部在 pilot 前通过 empirical testing + 用户审计决定)

| 项目 | 候选 | 决策时机 |
|---|---|---|
| 分词 | jieba 词级(默认) / 其它中文分词器 / AI 分词 | pilot 前 testing |
| n-gram 大小 | 词级 2-gram / 3-gram / 4-gram / 多种 | pilot 前 testing |
| 聚合方式 | Top-K% 平均 DF / 高频覆盖率 / 全均值 | pilot 前 testing |
| K% 或阈值 T | 从分布 empirically 定 | pilot 前 testing |
| 变换 | 原值 / log1p / arcsin-sqrt(看分布形态) | pilot 前 testing |
| 通用 boilerplate 过滤 | 移除 DF > 90% 文章的 n-gram(可选) | pilot 前 testing |

### 零值策略

`template_rigidity = 0` 合法(极不可能但若出现);沿用 R-1b/R-1c 零值策略
(保留,不当 missing 剔除)。

### 成本

极低。一次性建 n-gram 频率表(~100 万 CLS 文章,jieba 分词 + 统计,单机几小时);
每篇文章打分 = 查表,边际成本近零。

---

## 4. 区分度检查(discriminant check)

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b §5.3 / R-1c §6 / WS0.5 §3.3.3) |
| 比较对象 | vs R-1b `log1p_recurrence_count` / vs R-1c `log1p_target_salience` |
| 预期结果 | 通过(概念论证见下;正式检查在 pilot) |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback;同 R-1c Option C) |

**概念区分度论证**:

Rigidity 量的是**文本结构**(文章句式有多套路);F_recur 和 F_salience 量的是
**实体级频率**(标的×事件家族出现过多少次 / 标的被提到多少次)。关键分歧案例:

- **高 rigidity + 低 recurrence**:小公司第一份季报(recurrence=0,但格式跟
  几千份其它季报一模一样)
- **低 rigidity + 高 recurrence**:大市值公司的第 50 篇深度分析(高 recurrence,
  但每篇都是原创报道)
- **高 rigidity + 低 salience**:冷门公司发标准监管通知(很少被提及,但通知是
  纯模板)
- **低 rigidity + 高 salience**:知名公司被写调查性报道(极高 salience,
  但叙事独特)

最强证据:**同一天关于同一家公司的两篇文章**,F_recur 和 F_salience 相同,
但 rigidity 截然不同(业绩公告 vs 调查性报道)。Rigidity 量的是跟实体频率
正交的维度。

---

## 5. 稳健性 / appendix 候选

### 5.1 Pre-commit: 参考语料敏感性(L1 vs S0)

| 字段 | 值 |
|---|---|
| 候选 | 参考语料从 L1 去重文章集换成 **S0 全体 CLS 电报**,重算 rigidity,重跑 β3 |
| Pre-commit vs conditional | **pre-commit**(不论 pilot 结果都做并报) |
| 测的是 | "rigidity 信号是否依赖于参考语料的范围选择——过滤掉非金融内容会不会扭曲 n-gram 频率结构" |
| Slot | **Appendix**(不进 main / primary / supporting / robustness 槽) |
| 成本 | 近乎零(同一套 pipeline 换输入集) |

**合理性**:L1(只含匹配到实体的文章)和 S0(全体 CLS,含国际/政治/体育)
对同一个 n-gram 给出不同的 DF。如果两种 DF 下 rigidity 排序高度一致(且 β3
方向/大小稳健),说明结果不是参考语料范围选择的伪迹;若不一致,说明非金融
内容的存在显著改变了"高频"的含义,需要在 paper 里讨论。

### 5.2 显式不在 R-1d 范围内的定义 / 操作化(不进任何 slot)

- **定义 B(信息披露 vs 原创报道分类)**:跟 event_type / F_topic 高度重叠,
  不是独立的因子维度;rigidity 应量文本结构,不应退化为新闻类型的分类标签
- **定义 E(标题-正文冗余度)**:太窄,只量了 CLS 电报编辑习惯的一个侧面,
  不等于"文本有多模板化"
- **LLM 评分 rigidity(让非 fleet 模型给每篇文章打模板化分数)**:增加对外部
  模型输出的依赖,且评分标准不透明、难复现;与 Type 1 因子"不提模型即可
  描述"的精神冲突。**注:LLM 分词(用 LLM 做中文分词/分片)仍在 open
  items 内,不排除——分词是文本预处理,不是因子评分**
- **BPE / fleet 模型 tokenizer 分词**:绑定到具体模型的 tokenizer,违背
  Type 1(不同模型 tokenizer 不同 → 同一篇文章 rigidity 因模型而异)
- **字符级 n-gram(不分词)**:中文 2-3 字符 n-gram 粒度太细("公司""发布"
  等双字组合在所有文章中都高频),区分力弱

---

## 6. Standing discriminant input(给 WS0.5 §3.3.3 接口)

R-1d 给 WS0.5 discriminant check 框架(§3.3.3 / §5.4 / §5.5,WS0.5 已锁)
的输入:

- `template_rigidity` 在 `article_id` 维度、L1 去重文章集上算(§2 + §3)
- R-1e session 做 VIF / correlation 检查时的对比口径:
  - vs R-1b `log1p_recurrence_count`(L2 subject + tradable reference rows,
    §4 main variable formula of R1b_DECISIONS.md)
  - vs R-1c `log1p_target_salience`(L1 mention rows,
    §5 main variable formula of R1c_DECISIONS.md)
- 触发阈值:VIF ≥ 10 或 |r| ≥ 0.90
- Fallback:无 metric 级 fallback;触发时 R-1e 决定降级(同 R-1c Option C)
- **注**:rigidity 是 article 级(同一 article_id 对应唯一 rigidity),而
  R-1b/R-1c 是 case 级(article × entity 组合);VIF/correlation 计算时
  rigidity 按 case 的 article_id 映射(一对多:一篇文章可能对应多个 case,
  rigidity 值相同)

R-1d 不新增此 routine,仅提供输入接口。

---

## 7. 下游锚点

### R-1e(因子最终选择)
R-1d **不预承诺** Rigidity 进 primary。R-1e 根据 pilot 效应量、方差、共线性、
可解读性,以及操作化闸门(见文档头部)是否通过来决定。

### R-2(扰动)— 不受影响
Template Rigidity 是 case 级因子;扰动设计与之正交。

### R-4b(pilot 统计)
R-1d 给 pilot 的输入:`template_rigidity`(主变量,聚合方式 TBD)、分布、
与 R-1b/R-1c 的 correlation/VIF、通道特征 pattern(见 `channel_analysis.md`)。

### R-5(采样)
Pool G 分层:R-5 若启用,可用 `template_rigidity` 分层(若增加超出 R-1b/R-1c
的方差)。R-5 全权决定;R-1d 提供指标。

### B-2 schema
需要 `factor_provenance.run_inputs.per_task.template_rigidity` 字段
(具体 schema 由 B-2 session 整合;R-1d 提供内容需求)。

---

## 8. B-2 schema 需求

`factor_provenance.run_inputs.per_task.template_rigidity` 须包含:

- `factor_name = template_rigidity`
- `framing_claim = corpus_high_frequency_fragment_coverage`
- `source_layer = L1_deduplicated_articles`
- `row_unit = article_id`(article 级,非 entity 级)
- `reference_window`:同 R-1b/R-1c
- `tokenizer = TBD_pre_pilot`(jieba 为默认)
- `ngram_size = TBD_pre_pilot`
- `aggregation = TBD_pre_pilot`(Top-K% 平均 DF 为主候选)
- `transform = TBD_pre_pilot`
- `universal_boilerplate_filter = TBD_pre_pilot`
- `zero_policy = keep`
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pre_pilot_gate = operationalization_user_audit_required`

---

## 9. 不在 R-1d 范围内

- R-1e 因子最终选择(R-1d 闭 + pilot 后)
- R-4 第二轮辩论(R-1d 喂 evidence,不替它做)
- 判断哪条通道在跑(pilot 数据回答)
- 实现(WS0.5 在 R-1d 后)
- 具体 n-gram 大小 / 分词器 / 聚合方式选择(pilot 前 testing)

---

## 10. 因子准入判据(为何不设"无记忆基线"事前闸门)

**F_template 的准入只看三条:定义清晰、操作化可落地、与已有因子有区分度。**
"模板化经哪条机制影响读数"不作准入的事前闸门,理由:

1. 模板化至少有三条通道可能影响实验读数(近邻记忆、偏见强化、泛化替代)+
   纯表面熟悉度。哪条在跑是 pilot 数据说了算的经验问题,不是设计阶段能预判的。
2. 记忆是一族、偏见并入构念:若 rigidity 经偏见通道起作用,它仍在量构念里的东西。
3. 故通道判断不进准入三条判据;它属 pilot 经验,不作事前 gate。
