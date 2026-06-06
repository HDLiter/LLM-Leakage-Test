# Factor Pool Brainstorm(ARCHIVED — 历史 brainstorm,非当前 spec)

> **⛔ ARCHIVED**:因子候选池 review 已完(R-1g…R-1w,2026-06-05)。本文件**服役完毕**,
> 仅留作"被埋 / 被拒候选 + 概念工具(Type1/2 判据、粒度轴、泄露机制链 6 环节、
> directional-label 红线、A vs B)"的历史出处,**不是当前 spec**。
> **当前权威**:逐因子结局 = 各 `REOPEN_R1_R6/R1*_DECISIONS.md`;汇总索引 =
> `REOPEN_R1_R6/R4_methodology_audit/four_layer_candidate_pools.md` §1。
> 下游 agent 请读那一组,不要把本文件当 candidate 池现状。
> **不严谨是故意的** —— 这是想法地图,不是承诺。下游 agent 别把它当 canonical decision。

---

## 0. 预算 / 框架约束(先记死边界)

- **confirmatory 数 = power-bounded,不预设魔数**:最终 confirmatory factor 数由 **pilot + R-4b power** 决定 —— N=2560 对交互项(factor × cutoff)能稳健 confirm 几个,那个数就是上限(可能 4,可能 5-6)
  - 仍有**软压力**:叙事聚焦(10 个 confirmatory 通道讲不清)+ R-4a 锁的 "不做 family-wise multiplicity correction"(family 大小不被统计惩罚,所以唯一硬约束是 power 而非 multiplicity)
- **候选池可以 > 4** —— pilot 前(Stage 1)声明候选池;pilot 后从池里**选 / 降级**,**不追加池外新因子**(追加要开新 design memo,R-4a→R-6 接口路径 b)
- **sealed split 防 selection 污染**:pilot 上做 selection(exploratory,不耗 confirmatory alpha)→ main 上 confirm 选定的那几个(fresh data)。selection 规则 Stage 1 预先声明
- **未选中的候选不浪费**:进 exploratory(照常计算+报告+可视化,撑 benchmark coverage),或诊断/负对照

---

## 1. 这轮确立的概念工具(brainstorm 的真正产出)

1. **Type 1 vs Type 2 判据** —— "把所有模型拿走,这个属性还在吗?"
   - **在** = Type 1(corpus-intrinsic factor,有唯一真值,模型打分只是 noisy estimator 朝真值靠近)→ 合法 factor
   - **不在** = Type 2(model-reflexive,模型行为本身就是 target,无 corpus 真值)→ 不是 factor,归 estimand/诊断
   - 这正是 "factor 不依赖 operator 输出" 红线背后的理由(防 Type 1 滑向 Type 2)
2. **粒度轴**(正交于"因子内容"):同一概念可在 **article / entity / event-class / corpus-aggregate** 不同粒度做,测不同东西。每个因子 lock-in 时**显式声明粒度**,别默认
3. **泄露机制链 6 环节**(系统化找 gap 用):
   - ① 曝光**量**(见过多少次)② 曝光**时长**(见过多久)③ 内容**可记忆性**
   - ④ 带方向的**先验捷径** ⑤ **可推断性**(不靠记忆能否推出)⑥ **时间定位**
4. **directional-label 红线**:④方向先验 + ⑤可推断性 两族,都需要一个"看涨/看跌/可预测性"的方向打分。难点 = 这个打分必须**独立于 P_predict**(否则混入模型 bias,且和被测任务循环)。合法来源:规则/词典(噪声大)、Thales 已有 sentiment 标注(若有,最干净,**待查语料 schema**)、外部 judge(非 fleet 模型)。**禁**:真实股价(ex-post/R-6)、fleet 模型输出
5. **A vs B 区分**(directional 这族的核心):
   - **A = 文本客观方向信息**(text-intrinsic,有真值)→ Type 1 factor 候选
   - **B = 模型方向倾向**(model-wise bias)→ Type 2,诊断/负对照(Kong finance bias)
6. **Type A "先验良性" 闸门**:早期把"方向先验记忆"(降息利多周期股 等)整体判成"良性背景能力 Type A",排除在泄露外 → A 组方向先验全族因此蒸发。**这是 A 组能否复活的总闸门**。推翻它的钥匙:先验是良性还是泄露捷径,取决于"模型是否用先验代替读文本",而这**可用 C_SR/C_FO 扰动抵抗测**(扰动后预测不变 = 用先验代替读文本 = 泄露)

---

## 2. 正统 factor 候选(Type 1,corpus-intrinsic)

来源标记:【提】用户这轮提的 /【埋】agent 从 archive 挖的(用户先前没提)/【补】CC 补的

| 候选 | 机制环节 | 测什么 | 粒度 | 红线 / 难点 | 落地 | 来源 |
|---|---|---|---|---|---|---|
| **实体 age / 曝光时长** | ② | 模型积累实体记忆的**时间窗** | entity | 上市时长(metadata)**或 corpus span**(语料内首现→事件,更纯) | **低** | 【补】+用户细化 |
| **事件多空对称性** | ④ | 事件类**天然单向**(破产必跌)vs 双向(财报可涨可跌) | event-class | 纯事件标注,intrinsic;**不踩 directional-label 红线**(是结构属性非语料统计) | 低-中 | 【补】 |
| 语料多空失衡比(A4) | ④ | 该事件类语料里多/空样本比 | corpus-aggregate(板块/事件类/实体) | ⚠️ **directional-label 红线** | 中 | 【埋】+用户构思 |
| 文本方向信息(A 文本版) | ④ | **这条** case 客观传达利好/利空 | article | ⚠️ **directional-label 红线** | 中 | 【提】(A vs B 区分出) |
| 结果可预测性(B1) | ⑤ | 结果能否不靠记忆推出;pilot 有"中频比高频更脆弱"反直觉 | article/entity/event-class | ⚠️ **directional-label 红线**(用户:难独立于 P_predict) | 中 | 【埋】+用户细化 |
| topic / 事件类型 | ③④⑤混 | 事件类型 | event-class | categorical 吃系数预算;与 Template/Recurrence 重叠 | 低(已标注) | 【提】 |
| industry / 行业 | ④ | 行业归属 → 板块方向先验 | sector | categorical;真实趋势需股价(ex-post);纯归属标注则干净但弱 | 低(归属)/高(趋势) | 【提】 |
| 事实密度(D1) | ③ | 数字/实体/日期/因果断言密度 | article(natural)/entity | 纯文本,干净;article vs entity 见粒度轴 | **极低** | 【埋】+用户细化 |
| 日期 hint 明显度 | ⑥ | 时间锚多明显(关联 mask-year 扰动) | article | = 现有 Temporal Anchor Recoverability | 低 | 【提】 |
| 确切日期分桶 | ⑥ | 年份/季度(模型对特定期记忆深) | temporal | 纯 metadata,干净 | **极低** | 【提】 |
| 事件意外性 surprise | ⑤ | 事件**发生**的不可预期(≠B1 结果方向) | event-class | 需语料事前定义(该类是否常被预告) | 中 | 【补】 |
| 文本长度 / 体量 | ③ | 总信息量(≠密度) | article | 早期降为 control,可重看是否升格 | 极低 | 【补】(早期埋) |
| 结果锚点性 / 标志性 | ③ | 涨停跌停等标志性结果(认知 anchoring) | article | ⚠️ "结果"涉真实涨跌→ex-post 风险;只能用**文本里出现的标志数字** | 中 | 【补】 |
| 实体 valence 先验(A3) | ④ | 实体名带方向("茅台常涨"),≠中性 Salience | entity | ⚠️ 不能用 LLM 输出;须白盒激活探针或语料共现比 | 高 | 【埋】 |
| 结构方向先验(A1) | ④ | event-class→方向("降息利多") | event-class | **Type A 良性闸门**;需先推翻"良性"判断 | 中(categorical) | 【埋】 |
| regime 风格记忆(A2) | ⑥ | 时期→市场风格("2020 后成长占优") | temporal | regime 标签需 ex-ante 定义 | 中 | 【埋】 |

---

## 3. 不是 factor 但有价值(归 estimand / 诊断 / 负对照,**不占 factor 预算**)

| 想法 | 类型 | 归宿 | 来源 |
|---|---|---|---|
| 模型方向倾向(B,"模型爱猜跌?") | Type 2 model-reflexive | R-3 负对照 / Kong finance bias 诊断 | 【提】 |
| 涨/跌预测的记忆不对称("涨预测时记忆更重?") | reflexive estimand(内生,因果分不清,只能描述) | exploratory estimand 池 | 【提】 |
| 信源记忆(C1,固定正文换信源标签) | 4 学科判"参数里近乎不存" | **null 负对照**(预期零效应);部分已并入 Disclosure Regime | 【埋】 |

---

## 4. 明确拒绝(不进任何池)

| 候选 | 拒绝理由 | 谁拒的 |
|---|---|---|
| **C2 跨事件语义溢出** | "从长得像的事件学到结局" = 因果推断/泛化的定义本身,记忆 vs 推断本质混淆,比 A 组更难分良性/泄露 | 用户 2026-05-26 |
| D2 Fund/Shock(慢基本面 vs 快情绪) | Fund/Shock 是模型打出的分 → 依赖算子输出,触红线 | CC(agent 标) |
| B2 false-outcome plausibility | 是 operator 属性(C_FO 可行性),不是干净 case factor | CC(agent 标) |
| industry-内 share 作 salience 分母 | (这是 R-1c 内部决策,非 pool 层)framing C 是全局曝光非行业相对;ex-post 行业分类 | R-1c 已锁 |

---

## 5. 已被现有 13 个吸收(不算新增,列出防遗漏)

- **C3 article-overlap / verbatim recall** = 现有 Template Rigidity + Propagation 的组合前身
- **retrospective / temporal directionality** = 现有 Bloc 0 Temporal Anchor Recoverability 前身
- 早期 task-level 概念(Novelty / Authority / Expectation Gap / Information Content / Outcome Horizon):多已 collapse 成 operator/perturbation;其中 Information Content 的 case-level 化身 = 上表"事实密度"

---

## 6. 悬置的总闸门 / 待决(candidate-pool review 时处理)

1. **Type A "先验良性" 判断要不要正式重开** —— A 组(A1/A2/A3 + A4/文本方向)全族能否进 confirmatory 的总闸门
2. **directional-label 方案** —— ④⑤ 两族(多空比/文本方向/可预测性/部分对称性)共享;须查 **Thales/CLS 语料是否已有合法 sentiment 标注**;否则规则 or 外部 judge

---

## 7. CC 当前初判(供 review 时参考,非结论)

- 最干净、最该补的两个 gap:**实体 age/曝光时长**(②,corpus span 实现最纯) + **事件多空对称性**(④,intrinsic 不踩 directional 红线)
- 最切用户关切但有红线的:A4 多空比 / 文本方向 / B1 可预测性 —— 全卡 directional-label,命运绑在"有没有合法 sentiment 标注"
- A 组(结构/regime/实体 valence 先验)命运绑在 Type A 闸门,推翻它要靠"先验×扰动抵抗"论证
- 极低成本可顺手做的:事实密度、确切日期分桶、文本长度(这几个纯结构/纯文本,不踩任何红线)
