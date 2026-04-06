# Round 3 — Editor Review

综合 [proposal v2](../docs/RESEARCH_PROPOSAL_v2.md)、[审阅汇总](DISCUSSION_LOG_20260406.md)、[时间方向性分析](EXPLORE_TEMPORAL_DIRECTIONALITY.md) 和四份 memory taxonomy，我的判断是：

这篇论文应该变得"理论上更精确，但实验上更收缩"。如果只是把 `Type A/B` 写得更复杂，稿子会更散；如果把主 estimand 改准，反而会更强。

**逐项判断**
1. `Type A/B` 不应再做 headline taxonomy。  
主 taxonomy 应改成三轴：`temporal admissibility`（是否可由 `C≤τ` 重建）、`memory object`（event-outcome / entity prior / article-overlap / provenance 等）、`path role`（support vs shortcut）。`Type A/B` 最多保留为功能性 shorthand，不要再让它同时承担"时间合法性 + 机制类型 + 方法论正当性"三件事。[RESEARCH_PROPOSAL_v2.md](../docs/RESEARCH_PROPOSAL_v2.md) 现在把这些压在一条轴上，已经被 [EXPLORE_TEMPORAL_DIRECTIONALITY.md](EXPLORE_TEMPORAL_DIRECTIONALITY.md) 实质性推翻了。

2. `Entity prior` 应成为独立测试维度，但不该膨胀成第二主线。  
它不是普通 covariate，而是与 forward leakage 不同、但同样会污染 historical evaluation 的 shortcut。金融、NLP、mechinterp 三条文献都支持这一点。[LIT_MEMORY_TAXONOMY_FINANCE.md](LIT_MEMORY_TAXONOMY_FINANCE.md) [LIT_MEMORY_TAXONOMY_MECHINTERP.md](LIT_MEMORY_TAXONOMY_MECHINTERP.md)  
纳入方式我建议是：
- 全样本做 `task × entity salience/head-tail × target_type` 交互与分层。
- 子样本做 `entity masking / ticker anonymization / neighbor-entity substitution`。
- Qwen familiarity 至少比较原文与 entity-masked 版本，而不是只给一个静态 Min-K%。

3. CFLS 的跨模板构念效度，根本解法不是"多加控制"，而是"换 primary contrast"。  
问题不在 scoring 细节，而在 [counterfactual_templates.yaml](../config/prompts/counterfactual_templates.yaml) 里 `semantic_reversal` 和 `provenance_swap` 根本不是同一种干预；直接拿它们比较 `Delta_CFLS`，主 estimand 就不干净了。这一点在 [DISCUSSION_LOG_20260406.md](DISCUSSION_LOG_20260406.md) 和 [REVIEW_V2_CHALLENGER.md](REVIEW_V2_CHALLENGER.md) 说得对。  
我建议：
- 把主比较改成"同模板、不同任务"，最自然的是 `direct_prediction` vs `decomposed_impact`，因为后者已经在 [task_prompts.yaml](../config/prompts/task_prompts.yaml) 里。
- 把 `authority` 降为 secondary assay，主要用 `evidence intrusion` 而不是 CFLS 来承载它的价值。
- 如果做不到同模板桥接，就必须把结论降格成 `prompt-task-template bundle effect`，不能再写成 clean task-pathway claim。

4. "泄露"应改定义为 `dependence on information not recoverable from C≤τ`。  
这是这轮 refinement 最重要的理论升级，我认为应该采纳。[EXPLORE_TEMPORAL_DIRECTIONALITY.md](EXPLORE_TEMPORAL_DIRECTIONALITY.md)  
但代价是：你们必须把两个概念分开写。
- `look-ahead leakage`：依赖 `C≤τ` 不可恢复的信息。
- `text-external shortcutting`：更宽的上位类，包含 entity prior、article overlap、template memory 等。  
这样一来，`CFLS` 不能再被表述为"泄露测度本身"，它更像 shortcut susceptibility；`evidence intrusion` 和 false-outcome CPT 才更接近 leakage 的高精度证据。

5. 这些变化会让论文更强，但前提是 scope 收缩。  
如果你们把多维 taxonomy、entity prior、recoverability、authority、novelty、sentiment、utility、temporal、CPT 全都并列推进，稿子会直接过载。  
如果改成下面这个 spine，反而更有发表性：
- 主 claim：task design changes exposure to temporally inadmissible information and other text-external shortcuts.
- 主实验：same-article, same-template bridge comparison。
- 核心 novelty：false-outcome CPT 必须保留，最好升为 core，而不是 optional。
- 次级证据：authority 的 evidence intrusion、entity-prior moderator、Qwen familiarity/temporal 只做 triangulation。
- appendix：novelty、sentiment、utility。  
按这个版本，我认为是更强的 Findings of EMNLP 稿；如果没有同模板桥接和 false-outcome sign-flip，仍然有"careful but unsurprising"的 reject 风险。[DISCUSSION_LOG_20260406.md](DISCUSSION_LOG_20260406.md)

**一句话建议**
理论上用"三轴 taxonomy"，实验上只保留"两条主线"：  
一条测 `same-template shortcut susceptibility`，一条测 `false-outcome causal leakage`。  
其余东西都降为 moderator、triangulation 或 appendix。

补一句现实判断：当前 [metrics.py](../src/metrics.py) 和 [experiment.py](../src/experiment.py) 还停留在 legacy 状态，所以现在最该做的不是继续扩概念，而是先跑一个 `50-100` 条的 hard pilot，把 template comparability 和 effect shape 验出来。
