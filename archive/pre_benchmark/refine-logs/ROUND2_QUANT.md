**总判断**

Challenger 的报告有价值。严格说，A 和 C 的影子并非四位 Codex 完全没碰到，尤其 Stats/NLP 已经部分指出"模板不等价"和"跨站近重复"问题；但他把这些问题从普通 robustness/QC 风险上升成了主识别风险，这一步我是接受的。结合 [RESEARCH_PROPOSAL_v2.md#L178](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L178)、[counterfactual_templates.yaml#L70](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml#L70)、[counterfactual_templates.yaml#L104](/D:/GitRepos/LLM-Leakage-Test/config/prompts/counterfactual_templates.yaml#L104) 以及 [RESEARCH_PROPOSAL_v2.md#L153](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L153) 再看一遍后，我会把原来的 `8.1/10` 下调。

**逐条回应**

1. 攻击 A：部分同意，而且是高优先级问题。  
`CFLS` 作为"单任务内对目标改写的响应性"指标，我仍认为比旧 EI 更好；但跨任务比较时，`semantic_reversal` 和 `provenance_swap` 明显不是同构处理。前者要求翻转经济含义，后者要求保持经济事件不变只换信源框架，所以 `Delta_CFLS` 现在确实可能混入 rewrite salience、可察觉度、prompt compliance，而不只是 leakage。  
修补方案：先做 `50-100` 条 template-calibration pilot；逐模板报告 human label-flip agreement、changed-span 占比、edit distance、blinded detectability、QC pass rate；主结果按 matched salience band 分层；headline claim 改成 "task-conditioned counterfactual responsiveness gap"，不要直接写成 clean leakage parameter。并且把 coverage / abstention / answerable-subset sensitivity 变成强制报告项。

2. 攻击 B：部分同意。  
说它"严格是 tautology"我不同意，因为定义并不保证 gap 有多大、matched-format 后是否还在、authority 是否仍有残余 leakage、false-outcome 是否会 sign-flip。但如果论文最后只交付"问涨跌比问信源更容易受涨跌记忆污染"，那 novelty 的确偏弱。  
修补方案：把主贡献从"证明方向"改成"量化 gap 的大小、保留度和边界条件"；预注册 pilot MDE 和 matched-format retained-effect criterion；我现在比 Round 1 更倾向主文只保留 `direct_prediction` vs `decomposed_authority`，把 `sentiment` 下放附录，避免把直觉性的连续谱讲得太满。

3. 攻击 C：部分同意，其中"跨站重复"我强烈同意。  
CLS 电报确实短，当前计划里代表文长度中位数只有 `136` 字，[EXPERIMENT_PLAN.md#L179](/D:/GitRepos/LLM-Leakage-Test/refine-logs/EXPERIMENT_PLAN.md#L179)。在这种语料上做 semantic reversal，很容易从"局部改写"滑向"接近全文重写"。同时 authority prompt 本身也可能部分退化成模板 cue matching，[task_prompts.yaml#L259](/D:/GitRepos/LLM-Leakage-Test/config/prompts/task_prompts.yaml#L259)。再加上 Stage 3 目前只 against CLS corpus，[RESEARCH_PROPOSAL_v2.md#L153](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L153)，这对中文财经转载链明显不够。  
但我不同意"这已经动摇整个设计基础"这么重的表述。它削弱的是 item-level leakage interpretation，不是完全抹掉 same-article paired task comparison 的信息量。  
修补方案：Stage 3 扩到 CLS 之外的 Eastmoney / Sina / 公告站 / 搜索引擎 top-K；新增 `syndication_score` 并做高转载样本剔除敏感性；对 authority 增加 regex/rule baseline，如果规则系统都能高分，就不能再把 authority 卖成强 evidence-grounded reasoning task；所有结果强制按长度桶和 `unclear` 率分层。

4. 攻击 D：部分同意。  
Qwen 7B 上的 CPT 结果不能直接"解释" DeepSeek-V3 的行为，这点 Challenger 是对的。proposal 已把两者写成 complementary regimes，[RESEARCH_PROPOSAL_v2.md#L170](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L170) 和 [RESEARCH_PROPOSAL_v2.md#L171](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L171) 这个定位本身没错；问题是摘要和贡献段仍有些泛化过头，[RESEARCH_PROPOSAL_v2.md#L4](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L4) 和 [RESEARCH_PROPOSAL_v2.md#L362](/D:/GitRepos/LLM-Leakage-Test/docs/RESEARCH_PROPOSAL_v2.md#L362)。  
修补方案：明确改写成"DeepSeek 上的 behavioral evidence + Qwen 上的 mechanistic plausibility"，不要写成跨模型因果解释；Temporal 我现在更倾向 `Option C`；如果资源允许，补一个 `100-200` 条的第二模型 behavioral replication，比继续扩 DeepSeek 时间窗口更值。

5. 攻击 E：同意。  
这是我之前低估的 reject 风险。对 EMNLP reviewer 来说，方向性的结论太直觉化，论文必须靠 magnitude、retained effect、authority 的残余 leakage、false-outcome sign-flip，或者明确的 boundary conditions 才有 punch。否则很容易被归类成 careful but unsurprising measurement study。  
修补方案：先 pilot，再决定要不要扩到 `1000`；如果 pilot 看到的是"超大且过于干净的 gap + authority 几乎零 leakage"，我反而会先怀疑 artifact；utility 继续 appendix-only 或只在核心结果非常扎实后再做，不该拿半成品 backtest 去救 novelty。

**修正评分**

我把评分从 `8.1/10` 下调到 `7.7/10`。

下调主要来自三点：A 的构念效度风险、C 的 CLS 语料特殊性、E 的 novelty risk。我没有下调到 Challenger 的 `7.4`，因为这份 proposal 仍然有清楚的收缩边界、明确的 paired design、以及可修补的执行路径；但如果不先补 "template calibration + cross-site retrieval + scope shrink + pilot effect-size story"，我不会再维持 `8+` 的评分。
