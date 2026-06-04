# R-1g 事实密度(Fact Density)— 最终决策

**状态**: 锁定 2026-06-03(定义 + 操作化 + 候选池准入)
**结局**: **A — 进入 R-1e 候选池**
**pilot 前闸门**: 标注 rubric/prompt 调好 → 双 agent 抽取全量 → 用户全量审定稿,方可进入 pilot。未过闸门 → DROP,不重开 R-1g 定义。

**审计轨迹**: 本候选池快速轮无独立白板文件;三步快速判 + 操作化决定内嵌于本文件。

---

## 1. 定义

事实密度量的是:**一篇文章单位文本里塞了多少"事实颗粒"**——数字、命名实体、
因果断言的密度。密度高 = 信息浓,模型要记的硬信息多。

| 字段 | 值 |
|---|---|
| 因子类型 | **Type 1**(纯文本属性;把所有模型拿走,密度还在) |
| 粒度 | **article 级**(同一 article_id → 同一密度,与 focal entity 无关),与 F_template 同级 |
| 泄露机制链环节 | **③ 可记忆性**(文本内容有多少硬信息可供记忆) |

**与 F_template(模板刚性)的镜像关系**:F_template 看"文本有多套路"(语料高频
n-gram 骨架占比),Fact Density 看"文本塞了多少硬事实"。一篇高度模板化的监管
公告,可以事实密集(满是财务数字)也可以事实稀疏(寥寥几个数字)——两者量的是
正交的维度。

---

## 2. 事实颗粒的三类(+ 日期单列)

| 类 | 范围 | 进主规格分子? |
|---|---|---|
| **数字** | 百分比 / 金额 / 同比环比增速 / 股数份额等量化事实 | ✅ |
| **命名实体** | 公司 / 人名 / 监管机构 / 交易所(优先复用实体识别管线已匹配的上市公司 + 一张金融机构词典作参照) | ✅ |
| **因果断言** | 因为 / 由于 / 导致 / 受…影响 / 带动 / 归因于 … 等显式因果陈述 | ✅ |
| **日期 / 时间** | 绝对日期 + 相对时间(昨日 / 近日 / 上月 …) | ❌ 不进主规格(让位 F_temporal;数日期版作稳健性) |

**日期不进主规格的理由**:框架里已有 **F_temporal(时间线索强度)** 因子专管
时间锚有多明显 / 多可移除;density 再数日期会与 F_temporal 在"时间锚密度"上
共线。主规格让 density 专注"数字 + 实体 + 因果"三类硬信息,把时间锚维度整个
让给 F_temporal,从源头避开撞车。日期仍**抽取**(供数日期版稳健性),只是
主规格不计入分子。

---

## 3. 标注方法:双 agent 抽取 + 用户审定稿

| 字段 | 值 |
|---|---|
| 抽取 | **Codex + Claude 双 agent** 在原文上抽取事实颗粒(逐项标类);抽取 prompt rubric 由用户 pre-pilot 调 |
| 定稿 | **用户全量审定**(主 run ~2,560 样本规模,人工审定可行);审定稿是权威,双 agent 仅加速 |
| 性质 | **一次性标注产物,不是运行时算法**(同 R-1f core_name 标注:机械初标 + AI 辅助 + 用户审核) |
| 输入 | agent 读**原文**(不喂分词结果);分子(事实计数)与分母(文本长度)是对同一原文的两遍**独立**计算 |

**红线论证**:因子值 = **人审定稿的客观计数**,与 fleet 模型的行为各自独立 ——
"这段文字有几个数字"和"模型有没有背下这条新闻"是两回事 → 守住"因子不依赖算子
输出"。即便抽取 agent 与 fleet 成员同源(Codex ≈ fleet 的 GPT-5.1、本 session
Claude vs fleet 的 Claude Sonnet),因是**客观可审计抽取 + 人审定稿**,循环风险可忽略。
**此论证只对"客观可审计抽取"成立,不外推到方向标签族**(那族"判方向"本身就是
被测任务,循环为真)。

**标注 hygiene**:抽取 agent 优先用与 fleet 成员相异的实例 / 版本;frozen prompt
+ frozen annotation snapshot 保证可复现。

---

## 4. 聚合公式

```text
fact_units[article]   = #数字 + #实体 + #因果断言      # 三类等权,合成一张事实颗粒清单数总数
length_chars[article] = 正文字符数(去空白)
fact_density[article] = fact_units / length_chars
```

| 决定 | 值 | 理由 |
|---|---|---|
| **加权** | **等权**(三类合一数总数) | 透明、无任意权重,符合密度度量惯例。诚实交代:数字基数最大 → 主规格密度由数字主导,对金融新闻事实密度可接受;三类**分项计数另存**供诊断 |
| **归一** | **正文字符数** | 零依赖、可复现(不吃 jieba 版本 / 词典差异)、与 agent 标注完全解耦(此因子不需 jieba);jieba 词数归一作稳健性 |
| **必须归一** | 不用原始计数 | 原始计数会退化成与 F_len 高相关;**归一是 density 区别于 F_len 的命根** |
| **变换** | **原始密度比值(不 log)** | R-1b/c/f 用 log1p 是为压**跨数量级计数**的重尾;density 是**已归一比值**,无此重尾,原值更可解读。预登记 log1p 稳健性,pilot 现强右偏再切 |

---

## 5. 区分度检查

| 字段 | 值 |
|---|---|
| 阈值 | **VIF ≥ 10 OR \|r\| ≥ 0.90**(沿用 R-1b/c/d/f) |
| 比较对象 | vs F_template(R-1d `template_rigidity`)、vs F_len(R-1i)、vs F_temporal、vs F_recur、vs F_salience |
| 预期结果 | 通过(概念论证见下;正式检查在 pilot) |
| 触发后行动 | **R-1e 决定**(无 metric 级 fallback;同 R-1c Option C) |

**概念区分度论证**:
- **vs F_template**:套路度 vs 事实量,正交。分歧案例:标准格式季报(高 template +
  高 density,满是财务数字)vs 标准格式停牌公告(高 template + 低 density)。
- **vs F_len**:总量 vs 单位密度;归一保证可分(长而稀的讲话稿 / 短而密的数据简报)。
- **vs F_temporal**:主规格不数日期,把时间锚维度让给 F_temporal,从源头避开共线。
- **vs F_recur / F_salience**:那两个是实体级频率(出现多少次),density 是文本
  内容属性,正交。

---

## 6. 稳健性(全 pre-commit,近零成本)

| 替代变量 | 测的是 | Slot |
|---|---|---|
| **含日期版** | 把日期也计入分子重跑 β3 —— 时间锚是否改变结论 + 与 F_temporal 的关系 | Appendix |
| **词数归一版** | 分母换"词数"(而非字符数)—— 结论是否依赖字符 vs 词的长度口径 | Appendix |
| **三类分项密度** | 同一标注按类拆开报告 —— 哪类(数字 / 实体 / 因果)在驱动 | 诊断 |

**词数归一版的分词器 + 分子算法 = 跟随 F_template 的路线选择**(R-1d 的 pilot 前
操作化 open item;两因子在此**耦合** —— F_template 那道 pre-pilot 审计须知会它
**同时影响 R1g**):

- **F_template 走路线 B**(agent 只切选中的几千 case + 子串匹配 L1 数 DF):R1g
  **借用同一份 agent case 分词**。同一 agent 在同一 case 上既切词、又标事实颗粒
  (令事实颗粒 = 整数个词)→ 词边界与事实颗粒边界**天然对齐**,§3/§4 的"分词
  切碎事实颗粒"耦合伪迹**自动消失**,分子分母同口径。
- **F_template 走路线 A**(jieba 切全体 L1 建 DF 表):无 agent 分词可借,词数分母
  用 jieba;**动手前必须先敲定分子-分母在 jieba 口径下如何对齐**,候选两种:
  ① 把落在某事实颗粒 span 内的 jieba token 并成 1 个词(该事实颗粒在分子、分母里都算 1);
  ② 分子改数"落在事实颗粒 span 内的 jieba 词数",密度退成"事实词占总词比例"。
  不先定,耦合伪迹仍在。

**主规格(字符数分母)对路线选择免疫** —— 分子是语义事实颗粒数、分母是字符数,
本就不同单位、无需对齐,两种路线下都干净,不受此条影响。

**路线 B 的子串边界近似**(词级 n-gram 表面串可能跨 L1 不同词边界):用户判可接受
(路线 A 的 jieba 本身也非精确分词),precision 影响留 pilot 时再看。

**显式不做**:**实体级密度**(只数围绕目标实体的事实)—— 事实归属到具体实体难、
标注量翻倍,性价比低,弃。

---

## 7. Standing discriminant input(给 R-1e / WS0.5 §3.3.3 接口)

- `fact_density` 在 `article_id` 维度、L1 去重文章集上算(§2 + §4)。
- R-1e session 做 VIF / correlation 时:density 是 article 级(同一 article_id
  唯一值),按 case 的 article_id 映射到 (case) 行(一对多,同文章同值),口径同
  R-1d §6。
- 触发阈值:VIF ≥ 10 或 |r| ≥ 0.90;无 metric 级 fallback,触发时 R-1e 降级。

---

## 8. B-2 schema requirements

`factor_provenance.run_inputs.per_task.fact_density` 须包含(字段命名 / 风格留
B-2 整体 session):

- `factor_name = fact_density`
- `framing_claim = textual_fact_density`
- `source_layer = L1_deduplicated_articles`(article content 口径)
- `row_unit = article_id`
- `fact_categories = [number, entity, causal]`(date 抽取但不计入主分子)
- `annotation_method = dual_agent_extract_plus_user_audit`(frozen prompt + frozen annotation snapshot)
- `weighting = equal`
- `denominator = content_char_count`
- `robustness_word_denominator = follows_R1d_template_route`(B:借 agent 分词,分子分母自动对齐;A:jieba + 须先定对齐规则;见 §6)
- `transform = raw`(robustness: `log1p`)
- `zero_policy = keep`
- `discriminant_threshold = {vif: 10, abs_correlation: 0.90}`
- `fallback_policy = no_metric_fallback; defer_to_r1e`
- `pre_pilot_gate = annotation_rubric_tuned + dual_agent_run + user_audit_passed`

### Provenance hashes
- S0 source snapshot hash · **annotation prompt / rubric hash** · **annotation snapshot hash**
  · layer / view definition hash · sampling manifest hash(when factor values tied to a sampled frame)

---

## 9. 不在 R-1g 范围内

- 抽取 prompt rubric 的具体措辞(用户 pre-pilot 调)
- R-1e 因子最终选择(R-1g 闭 + pilot 后)
- 实体级密度(已弃,§6)
- LLM 整体打分密度(本因子走逐项抽取 + 人审的客观计数,§3)
