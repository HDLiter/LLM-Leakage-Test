# R-1a Cutoff Exposure —— Codex clean-room 白板分析

## 0. 我对这个因子的独立理解

Cutoff Exposure 测的是一个简单物理问题:某条 case 的公开文本时间,相对某个模型训练 cutoff,是在前面还是后面,以及离 cutoff 有多远。它不是在判断模型实际上有没有背下来,而是在给"有机会见过"这条通道一个可追溯的数值轴。因为 cutoff 是模型属性、case event date 是 case 属性,这个因子天然是 case x model。它还会被其它因子交互,所以主口径必须简单、稳定、可解释,不能用模型输出反过来校准自己。

## 决策点 1: Case event date 口径

- 可选方案: (i) 用 `published_at` 发文日; (ii) 用文中的实际事件发生日; (iii) 主用 `published_at`,显式 in-text event date 只作 robustness。
- 推荐: **主 metric 用 `published_at`;in-text event date 只在可确定性抽取且覆盖足够时作 appendix robustness。**
- 理由: Cutoff leakage 的最近物理通道是"模型训练语料可能见过这条 CLS 文本及其结果",这个时间点首先是发文时间,不是事件在现实中发生的时间。`published_at` 已在 S0 有结构化字段,确定、全覆盖、可复现,也不需要 LLM 抽取,不会撞 R-0 的 "factor metric 不依赖 operator 输出" 红线。in-text event date 对回顾/预告文章更贴近事件本体,但很多电报没有明确日期,规则抽取会稀疏且歧义大,LLM 抽取又会把一个本该干净的因子变成模型辅助标注问题。
- 风险 / caveat: 对回顾类文章,`published_at` 可能晚于真实事件;若 cutoff 落在两者之间,主 metric 会说"未见过这条 CLS 文本",但模型可能从其它渠道见过同一事件。对预告类文章,`published_at` 可能早于实际结果;这时它衡量的是文本 exposure,不是结果 exposure。这个风险应通过 event type / case audit 解释,不应把主口径改成低覆盖的 in-text 日期。

## 决策点 2: per-model cutoff manifest 来源

- 可选方案: (i) 直接用 `config/fleet/r5a_fleet.yaml` 的 `cutoff_date`; (ii) 用 Path-E 实测 horizon 替换; (iii) 主用 yaml,Path-E 作验证 / sensitivity。
- 推荐: **主 metric 只用 fleet yaml 的 `cutoff_date`;`cutoff_source` 进入 provenance / 风险标记;Path-E 不替换主 cutoff manifest。**
- 理由: R-1b/R-1c 的 reference window 右端点已经要求来自同一份 fleet cutoff manifest,R-1a 若改用另一套 cutoff,三个因子的时间基准会互相打架。Path-E 只能覆盖白盒 logprob 模型,不能覆盖 4 个黑盒;若用它替换主 cutoff,case x model 面板会出现白盒和黑盒不同来源的时间轴。更关键的是,Path-E 是基于 Min-K%++ / logprob 行为探针的模型输出证据,适合验证 cutoff 声明是否可信,不适合作 factor metric 的输入。
- 风险 / caveat: yaml 中 `community_paraphrase` 和 `operator_inferred` 的可信度不一致,日期误差会稀释 R-1a 主效应。这个风险要显式记录,尤其是 operator-inferred 模型;但用不完整的行为探针来替换主 manifest,会引入更大的可比性问题。

## 决策点 3: metric 连续化形态

- 可选方案: (i) 裸 signed 天数差; (ii) `log(abs(days))`; (iii) signed-log; (iv) 月度分桶; (v) pre/post binary。
- 推荐: **主连续值用 signed-log month scale:**

```text
delta_days[case, model] = (model.cutoff_date - date(case.published_at)).days
cutoff_exposure[case, model] =
    sign(delta_days) * log1p(abs(delta_days) / 30.4375)
```

正值表示 case 在该模型 cutoff 之前,模型训练时有机会见过;负值表示 case 在 cutoff 之后,按 cutoff 不应见过。`delta_days = 0` 记为 0。

- 理由: 裸天数差会暗含"多早一天就线性多一点 exposure",这不符合训练语料覆盖的粗粒度现实;离 cutoff 3 年和 4 年的差异不应像离 cutoff 1 天和 1 年那样重要。signed-log 保留方向,压缩远离 cutoff 的巨大量级,同时让 cutoff 附近的差异仍有分辨率。按月缩放也承认多数 cutoff 本身只有月级可信度,避免给日期精度过度背书。
- 风险 / caveat: signed-log 在 0 附近有一个方向切换,解释不如裸天数直观;实现时应同时保留 `delta_days` 原始列用于审计。`30.4375` 是换算常数,不代表 cutoff 真能精确到平均月份。

## 决策点 4: case x model 处理(metric 层)

- 可选方案: (i) 只做 case-level exposure; (ii) 对每个 `(case, model)` cross join 后计算; (iii) 先按模型组聚合。
- 推荐: **在 metric 层物化一行 `(article_id, target_entity_id, model_id)` 一个值,不做聚合。**
- 理由: 同一条 case 对早 cutoff 模型和晚 cutoff 模型的 exposure 不同,所以数值必须在 case x model 层生成。具体做法是把 L3 admissible case rows 与 fleet models cross join,读取 case 的 `published_at` 和 model 的 `cutoff_date`,产出 `delta_days`、`cutoff_exposure`、`pre_cutoff_flag`。同一 article 的多个 target row 可以共享同一时间值;同 cutoff 的模型会得到相同 exposure 值,这是 manifest 事实,不是 metric 问题。
- 风险 / caveat: 哪些 `(case, model)` 进入哪个 estimand、缺失 operator 怎么处理、random effects 怎么设,都不在 R-1a 定义范围内。metric 表可以给全 fleet 产值,下游再按 estimand eligibility 过滤。

## 决策点 5: Path-E horizon 探针关系

- 可选方案: (i) Path-E 是主 metric 的 cutoff 来源; (ii) Path-E 是白盒验证手段; (iii) Path-E 只作事后解释材料。
- 推荐: **Path-E 定位为验证手段和 sensitivity 输入,不是 R-1a 主 metric 来源。**
- 理由: `exposure_horizon.py` 的接口已经把 `horizon_observed=None` 定义为"经验 horizon 不确定",并要求 downstream 回退到 `cutoff_date_yaml`。这说明它的正确角色是测试 yaml cutoff 附近是否真的出现熟悉度断点,并量化 cutoff 误差风险。它依赖 logprob 行为、只覆盖白盒、且有接受/拒绝规则;这些特征都不适合拿来定义一个全 fleet 的基础因子。
- 风险 / caveat: 如果 Path-E 对某些白盒模型给出清晰且大幅偏离 yaml 的 horizon,主分析仍用 yaml 会显得保守但可能有误分类。处理方式应是报告"yaml cutoff 风险升高",并在白盒子集做 sensitivity;不应静默替换主 metric。

## 决策点 6: continuous vs binary 最终形态

- 可选方案: (i) 只保留连续 signed-log; (ii) 主用 binary pre/post; (iii) 主用连续,保留 binary 作负对照 / 描述轴。
- 推荐: **主因子用连续 signed-log;同时保留 `pre_cutoff_flag = delta_days >= 0` 作为 BL2 post-cutoff 负对照和描述性切片。**
- 理由: 用户已经判断 cutoff 不是一个能钉死的硬日界线,训练覆盖也更像渐变,所以主效应应由连续值承载。binary 的价值是回答一个更粗的问题:"按 manifest,这条 case 是否在模型 cutoff 之后?" 这正好服务 R-4a 已锁的 BL2 post-cutoff 负对照,用 TOST/SESOI=0.15 检查 post-cutoff 轴上的效应是否接近 0。binary 不应替代主 metric,否则会把"离 cutoff 多远"的信息全部丢掉。
- 风险 / caveat: `pre_cutoff_flag` 对 cutoff 日期误差更敏感,特别是贴近 cutoff 的 case;因此它适合做负对照分层和 sanity check,不适合承担主 β1。robustness 形态只保留一个最小版本:对可确定性抽取 in-text event date 的子集,重算 signed-log exposure;不做多窗口或多 transform grid。

## 跨决策点的一致性检查

这 6 个选择是自洽的:事件时间来自 case 的 `published_at`,模型时间来自同一份 fleet yaml,两者 deterministic cross join 产出 case x model 的 signed-log 连续值。这个口径不依赖 P_predict / P_logprob / P_extract,因此守住 R-0 的 factor-before-operators 约束。它也不引入第二套 cutoff manifest,因此与 R-1b/R-1c 的 `min(model_cutoff)` 同源。Path-E 被放在验证和 sensitivity 层,可以提醒 cutoff 误差,但不改变主 metric。binary 只作为 BL2 post-cutoff 负对照轴,不会和连续主因子争同一个角色。

## 我最不确定的点 / 需要用户拍板的真分歧

最大的不确定点是 `published_at` 对"结果 exposure"的代理程度。若 benchmark 的核心 claim 是"模型见过这条 CLS 文本",`published_at` 明显正确;若 claim 强到"模型见过现实事件及结果",回顾类和预告类文章会产生边界误差。我建议不要为这个误差牺牲主 metric 的确定性和覆盖率,但需要用户确认:本因子的主叙述应写成"CLS text exposure / article availability",而不是更宽泛的"real-world event exposure"。
