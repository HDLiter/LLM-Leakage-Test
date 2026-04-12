# Project Timeline & Document Index

> 本文档是项目探索过程的时间轴索引，供后续 agent 快速理解项目历史和文档关系。
> 最后更新：2026-04-11

## 项目概述

本项目研究中文金融新闻 LLM 流水线中的 look-ahead leakage：同一组 `(article, target)` 输入，在不同 task design 下是否会开启不同的 parametric memory 路径。项目已经从早期 notebook 式探索，推进到开题、多轮多-agent 反驳、pilot/diagnostic、`deep-floating-lake` v3 扩样重跑，以及 `amber-mirror-lattice` 的 bug audit + rerun。当前最稳的结论不是“统一检测到泄露”，而是更细的区分：CFLS 更像输入敏感性/读文能力指标；false-outcome CPT 在 `direct_prediction` 上主要暴露 suggestibility，在 `decomposed_impact` 上经 Bug 3 修复后出现 memorization-direction 关联，但仍需要更干净的正控或 2×2 CPT 设计巩固。

当前仓库没有 `notebooks/` 目录；早期 notebook 已在 2026-04-05 被归档到 `archive/pilot_phase/notebooks/`。

## 时间轴

### Phase 0: 初步探索（2026-03-12 ~ 2026-04-04）

- **Notebooks**: 当前 `notebooks/` 不存在；补充线索是归档目录中的 `00_data_prep`、`01_memorization_audit`、`02_counterfactual`、`03_ablation`、`04_output_format`、`05_mitigation_compare`、`06_prompt_optimization`，用途可从文件名推断为数据准备、记忆审计、反事实、消融、输出格式、缓解对比与提示优化。
- **产出文档**: 这一阶段正式文档很少，主要以 notebook、seed JSON、memory 条目和后续在 `PROPOSAL_BRAINSTORM.md` 中被回收的想法为主。
- **关键提交**: `6df2e12`、`b3716cf`、`be41713`、`2279799`、`2c8fe04`、`9f12576`、`ffc50d2`。
- **关键发现**: 项目先验证“历史评估可能被 parametric memory 污染”，随后把注意力从单纯的 memorization audit 推向“任务设计是否决定泄露暴露方式”。

### Phase 1: 开题（2026-04-05 ~ 2026-04-06）

- **Notebooks**: 无新增 notebook，工作重心转为 proposal、roadmap、多-agent review 与 literature synthesis。
- **产出文档**: `LANDSCAPE.md`、`ROADMAP.md`、`PROPOSAL_BRAINSTORM.md`、`RESEARCH_PROPOSAL.md`、`AUTO_REVIEW.md`、`RESEARCH_PROPOSAL_v2.md`，以及 `refine-logs/` 下的大量讨论、辩论、文献检索和 reviewer 记录。
- **关键提交**: `928c78a`、`f7fcafc`、`8c0b73f`、`a198840`、`515fb07`、`44e0080`、`142045a`。
- **关键发现**: 项目从 “EI/CF 指标论文” 转成 “Task Design Gates Look-Ahead Memory” 的机制论文；Type A / Type B memory、same-article different-task 设计、false-outcome CPT 成为核心叙事。

### Phase 2: Diagnostic（2026-04-06 ~ 2026-04-08）

- **Notebooks**: 无新增 notebook；E_pilot 与 diagnostic 主要通过代码和结果文档推进。
- **产出文档**: `PILOT_RESULTS.md` 初版与 diagnostic 追加段落，`refine-logs/pilot_discussion/` 全套 round 1 / 1.5 / 2 / 3 讨论记录。
- **关键提交**: `cae01f7`、`ef93f7e`、`14725e9`、`7466ce0`、`8910021`、`b8678ac`、`e3b9661`、`8a594cf`、`dc92c04`、`1d7361a`、`1cd2a7c`。
- **关键发现**: pilot 暴露了 CFLS floor effect 与 bidirectional generalization confound；diagnostic 扩到 192 cases 后，论文重心从“证明有泄露”进一步转向“当前 probe 到底在测什么”。

### Phase 3: deep-floating-lake v3（2026-04-09 ~ 2026-04-11，后被 amber 接管）

- **Notebooks**: 无；改由 `deep-floating-lake` 计划驱动大样本标注、anchor/frequency 分层和 batched pipeline。
- **产出文档**: `ANCHOR_RUBRIC.md`、`FIRTH_DECISION.md`、`PILOT_RESULTS.md` 的 Phase 3 段落，以及 v3 seed / annotation / frequency / strata 配置。
- **关键提交**: `87f0211`。
- **关键发现**: 682 条 v3 标注样本、606 条 eligible case 的 stratified rerun 仍显示 CFLS 更像读文敏感性，CPT 更像 suggestibility；这一“过于干净的 null”直接触发了后续 bug audit。

### Phase 4: amber-mirror-lattice（2026-04-11）

- **Notebooks**: 无；工作流改为 “先审计 bug，再修复，再 rerun，再做写作 gate review”。
- **产出文档**: `BUG_AUDIT_amber.md`、`REVIEW_amber_G1*.md`、`REVIEW_amber_G2*.md`、`REVIEW_amber_G3.md`、`REVIEW_amber_G4*.md`，以及 `PILOT_RESULTS.md` 的 Phase 4 段落。
- **关键提交**: `4421da2`、`dd76d01`、`5eb4cf4`。
- **关键发现**: Bug 1 修复后恢复约 150 个 CFLS 可评分 case；Bug 3 把 `decomposed_impact` 的 CPT 结论从“全零/退化”改写为 memorization-direction（pooled MH OR≈1.95），但 `direct_prediction` 仍主要呈现 suggestibility。

## 近 30 次提交参考

```text
5eb4cf4 2026-04-11 amber-mirror-lattice: Phase D re-run + Phase E results update
dd76d01 2026-04-11 amber G2a fix: add stale-data guardrails to analysis scripts
4421da2 2026-04-11 amber-mirror-lattice: Phase A audit + Phase B bug fixes (5 bugs)
87f0211 2026-04-11 deep-floating-lake: v3 stratified pipeline baseline
1cd2a7c 2026-04-08 CPT: LLM-based outcome negation instead of mechanical regex swap
1d7361a 2026-04-08 Fix 1 HIGH + 2 MEDIUM from Codex review of diagnostic commit
dc92c04 2026-04-08 Diagnostic phase: expand to 192 cases, run 3 diagnostics, fix H2/H3
8a594cf 2026-04-06 Pilot results doc, archive old results, organize paper library
e3b9661 2026-04-06 Add concurrent task execution to pilot runner (max_concurrency=20)
b8678ac 2026-04-06 Fix 2 high issues from fifth Codex review
8910021 2026-04-06 Fix 3 high issues from fourth Codex review
7466ce0 2026-04-06 Fix 4 high issues from third Codex review
14725e9 2026-04-06 Fix 4 issues from second Codex review
ef93f7e 2026-04-06 Fix 6 issues from Codex code review of E_pilot
cae01f7 2026-04-06 E_pilot implementation: same-template CFLS bridge + false-outcome CPT
142045a 2026-04-06 Multi-model review of proposal v2: 3 rounds + cross-domain lit search
44e0080 2026-04-05 Archive old README with pilot phase materials
515fb07 2026-04-05 Archive pilot phase notebooks and scripts to archive/pilot_phase/
a198840 2026-04-05 Prompt schema v2: add target, impact, reframe novelty
8c0b73f 2026-04-05 Add prompt schema, experiment pipeline, and smoke test
f7fcafc 2026-04-05 Revise research proposal after 3-round multi-perspective review loop
928c78a 2026-04-05 Add research proposal and literature landscape docs
67205ad 2026-04-04 Add project config: CLAUDE.md, AGENTS.md, update .gitignore
ffc50d2 2026-03-13 complete run through
9f12576 2026-03-13 Fix counterfactual card layout: wrap td content in div for max-height
2c8fe04 2026-03-13 Remove prediction/news text truncation in counterfactual display cards
2279799 2026-03-13 Strengthen counterfactual generation and validation prompts
be41713 2026-03-13 NB00: show 4 counterfactual previews (2 per type), fix enum display
b3716cf 2026-03-13 Fix SyntaxError: replace Chinese curly quotes with plain text in notebook 06
6df2e12 2026-03-13 Add commentary, strategy explanations, and plain-language interpretations across notebooks
```

## Notebook 线索

- `notebooks/` 当前不存在；按用户要求扫描结果为空。
- 补充线索：`archive/pilot_phase/notebooks/` 中可见 `00_data_prep.ipynb`、`01_memorization_audit.ipynb`、`02_counterfactual.ipynb`、`03_ablation.ipynb`、`04_output_format.ipynb`、`05_mitigation_compare.ipynb`、`06_prompt_optimization.ipynb`；仅依据文件名推断，它们对应 Phase 0 的主要探索轨迹。

## 文档索引

时间写法说明：优先采用文内显式日期；若无，则采用首次入库的 `git log --diff-filter=A` 日期；若两者都不可靠，则标“文件创建时间/推断”。

### 根目录

- `AUTO_REVIEW.md` — 时间：2026-04-05（文内）；背景：Phase 1，为把 `RESEARCH_PROPOSAL.md` 做三轮 autonomous review 并留下修订记录；内容：记录 reviewer 原始意见、聚合判断与 actions taken；依赖：先读 `RESEARCH_PROPOSAL.md`。

### docs/

- `LANDSCAPE.md` — 时间：2026-04-05（文内/入库）；背景：Phase 1，开题前需要补齐金融 NLP 泄露问题的研究地景；内容：梳理 finance + contamination + Chinese gap 的文献背景；依赖：无，适合作为入口。
- `ROADMAP.md` — 时间：2026-04-05（git）；背景：Phase 0→1，需把早期 notebook 发现收束成论文路线图；内容：定义 positioning、RQ、theory backbone 与实验 scope 的 choice points；依赖：建议先读 `LANDSCAPE.md`。
- `PROPOSAL_BRAINSTORM.md` — 时间：2026-04-04/05（文内，推断）；背景：Phase 0→1，6 个 advisor agents 的 brainstorm 需要沉淀为开题原料；内容：多视角综合出的 thesis、framing 与实验要求；依赖：先读 `LANDSCAPE.md`、`ROADMAP.md`。
- `RESEARCH_PROPOSAL.md` — 时间：2026-04-05（git）；背景：Phase 1，形成第一版正式开题稿；内容：v1 proposal，仍带较强 metric/benchmark 色彩；依赖：先读 `ROADMAP.md`、`PROPOSAL_BRAINSTORM.md`。
- `RESEARCH_PROPOSAL_v2.md` — 时间：2026-04-06（git；文内命中的 2026-01-01 为引用噪声，不采用）；背景：Phase 1，因 `AUTO_REVIEW.md` 和多轮 debate 指出 narrative/identification 问题，需要重写 proposal；内容：把主线改写成 “Task Design Gates Look-Ahead Memory” 的机制论文；依赖：先读 `RESEARCH_PROPOSAL.md`、`AUTO_REVIEW.md`、`refine-logs/DISCUSSION_LOG_20260405.md`。
- `PILOT_RESULTS.md` — 时间：2026-04-06（首建，后续 04-08/04-09/04-11 连续追加）；背景：Phase 2 起，需要把 pilot、diagnostic、Phase 3、Phase 4 结果集中到一个 living results doc；内容：从 E_pilot 一直到 amber rerun 的主结果与解释都在此文件；依赖：先读 `RESEARCH_PROPOSAL_v2.md`，再按需跳到对应 phase 段落。
- `ANCHOR_RUBRIC.md` — 时间：2026-04-11（git；服务于 2026-04-09 的 `deep-floating-lake` 计划，时间属推断）；背景：Phase 3，因旧 `anchor_analysis.json` 是手写而非 rubric 驱动，需要重做 anchor_level 标注标准；内容：anchor 0-3 的操作定义、决策树与例子；依赖：先读 `~/.claude/plans/deep-floating-lake.md`。
- `FIRTH_DECISION.md` — 时间：2026-04-09（文内）/2026-04-11（入库）；背景：Phase 3，rare-event logistic 在 Python 3.12 环境下无法直接用 Firth，需要明确替代方案；内容：记录为何改用 `statsmodels.Logit.fit_regularized`；依赖：先读 `~/.claude/plans/deep-floating-lake.md` 或 `PILOT_RESULTS.md` Phase 3。
- `BUG_AUDIT_amber.md` — 时间：2026-04-11（文内/入库）；背景：Phase 4，G1 之前必须确认 v3 null 是否被 5 个 bug 污染；内容：逐条审计 Bug 1-5，量化其影响并说明哪些已证实、哪些仍只是 hazard；依赖：先读 `PILOT_RESULTS.md` Phase 3 和 `~/.claude/plans/amber-mirror-lattice.md`。
- `REVIEW_amber_G1.md` — 时间：2026-04-11（git）；背景：Phase 4，`amber` 计划要求的 G1 审阅门；内容：对 `BUG_AUDIT_amber.md` 与相关代码/数据做第一次 hostile review；依赖：先读 `BUG_AUDIT_amber.md`。
- `REVIEW_amber_G1_round2.md` — 时间：2026-04-11（git）；背景：Phase 4，G1 首轮要求改 wording 和分母口径后需要复审；内容：确认 revision uptake 是否到位；依赖：先读 `REVIEW_amber_G1.md`、`BUG_AUDIT_amber.md`。
- `REVIEW_amber_G2a.md` — 时间：2026-04-11（git）；背景：Phase 4，G2a 需要在重跑前对 bug-fix diff 做 hostile review；内容：核对 `4421da2` 的修复是否真的覆盖关键 bug；依赖：先读 `BUG_AUDIT_amber.md`。
- `REVIEW_amber_G2b.md` — 时间：2026-04-11（git）；背景：Phase 4，G2b 作为补充实现审阅，需要从 pre-fix code 与 audit claim 反推修复充分性；内容：以更“修 bug”视角复盘 5 个问题；依赖：先读 `REVIEW_amber_G2a.md`。
- `REVIEW_amber_G3.md` — 时间：2026-04-11（git）；背景：Phase 4，重跑完成后需要做数据一致性审阅；内容：直接用 `diagnostic_2_results.json` 复算 schema、stratum 和 headline numbers；依赖：先读 `PILOT_RESULTS.md` Phase 4 草稿。
- `REVIEW_amber_G4.md` — 时间：2026-04-11（git）；背景：Phase 4，写作阶段需要防止 overclaim；内容：指出 `PILOT_RESULTS.md` Phase 4 中哪些结论超出表格所能支持的范围；依赖：先读 `PILOT_RESULTS.md`。
- `REVIEW_amber_G4_round2.md` — 时间：2026-04-11（git）；背景：Phase 4，G4 首轮修改后要二次确认措辞已经收敛；内容：检查剩余 overclaim/phase contamination 问题；依赖：先读 `REVIEW_amber_G4.md` 与更新后的 `PILOT_RESULTS.md`。

### refine-logs/

#### v1 计划与第一次开题收束

- `EXPERIMENT_PLAN.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，需要把 `ROADMAP.md` 落成可执行 block 和 claim map；内容：v1 实验总图、benchmark pipeline、E1-E6 设计；依赖：先读 `docs/ROADMAP.md`。
- `EXPERIMENT_TRACKER.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，需要给 v1 方案配套 run tracker；内容：按 milestone、指标、状态管理实验清单；依赖：先读 `EXPERIMENT_PLAN.md`。
- `REVIEW_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，Round 1 需要 Quant 视角审阅 v1 计划；内容：从 production/alpha 相关性上评估实验计划；依赖：先读 `EXPERIMENT_PLAN.md`。
- `REVIEW_NLP.md` — 时间：2026-04-06（git）；背景：Phase 1，Round 1 需要 NLP/ML 视角审阅 v1 计划；内容：指出 benchmark、task setup 与方法识别上的主要风险；依赖：先读 `EXPERIMENT_PLAN.md`。
- `REVIEW_STATS.md` — 时间：2026-04-06（git）；背景：Phase 1，Round 1 需要计量/统计视角检查可识别性；内容：批评 inference、gate、pre-spec 和 effect estimation；依赖：先读 `EXPERIMENT_PLAN.md`。
- `REVIEW_EDITOR.md` — 时间：2026-04-06（git）；背景：Phase 1，Round 1 需要编辑/venue 视角判断可发表性；内容：判断 v1 更像 Findings 级 measurement paper 还是过度展开；依赖：先读 `EXPERIMENT_PLAN.md`。
- `REVIEW_SUMMARY.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，需要把 4 份独立评审汇成行动项；内容：总结 convergent issues、得分和优先级；依赖：先读四份 `REVIEW_*.md`。
- `DISCUSSION_LOG_20260405.md` — 时间：2026-04-05（会话）/2026-04-06（入库）；背景：Phase 1，为把 v1 计划争论一路推进到 v2 proposal；内容：从 EI confound、entity masking、creative redesign 一直到 alpha value 的 9 轮 debate 总结；依赖：先读 `EXPERIMENT_PLAN.md`、`REVIEW_SUMMARY.md`。

#### 专题辩论、文献检索与方向选择

- `DEBATE_EI_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，用户质疑 EI 把 local CF 和 global paraphrase 相减是否引入 edit-magnitude confound；内容：Quant 视角论证该 confound 真实且 material；依赖：先读 `EXPERIMENT_PLAN.md`。
- `DEBATE_EI_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 视角解释为何当前 EI 更像 template/edit-distance 混合量；依赖：先读 `EXPERIMENT_PLAN.md`。
- `DEBATE_EI_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 视角把 EI 写成识别失败问题；依赖：先读 `EXPERIMENT_PLAN.md`。
- `DEBATE_EI_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 视角判断该 confound 会如何击穿论文叙事；依赖：先读 `EXPERIMENT_PLAN.md`。
- `DEBATE_MASKING_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，用户追问 entity-triggered memorization 是否需要 masking；内容：Quant 视角主张把 masking 作为 probe 而不是主 metric 修复；依赖：先读 `DEBATE_EI_*.md`。
- `DEBATE_MASKING_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 视角建议 Option B，自然替换优于粗暴 masking；依赖：先读 `DEBATE_EI_*.md`。
- `DEBATE_MASKING_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 视角指出 masking 不是 stand-alone causal control；依赖：先读 `DEBATE_EI_*.md`。
- `DEBATE_MASKING_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 视角判断 masking 对 EMNLP 叙事的重要程度；依赖：先读 `DEBATE_EI_*.md`。
- `CREATIVE_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，用户要求 “think out of the box”；内容：Quant 提出 utility-vs-leakage frontier/因子组合方向；依赖：先读 `DEBATE_MASKING_*.md`。
- `CREATIVE_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 提出 task-induced retrieval / evidence intrusion 一类更强的机制设计；依赖：先读 `DEBATE_MASKING_*.md`。
- `CREATIVE_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 提出 randomized exposure / 更清晰 estimand；依赖：先读 `DEBATE_MASKING_*.md`。
- `CREATIVE_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 主张大幅简化并突出论文 backbone；依赖：先读 `DEBATE_MASKING_*.md`。
- `LIT_COUNTERFACTUAL_METHODS.md` — 时间：2026-04-06（git；检索发生在 2026-04-05 左右，推断）；背景：Phase 1，需要文献确认 counterfactual contamination 方法的可比性与新意；内容：汇总 counterfactual benchmark / rewrite / contamination 检测相关文献；依赖：先读 `EXPERIMENT_PLAN.md`。
- `LIT_RETRIEVAL_TEMPORAL_METHODS.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，需要把 retrieval faithfulness、temporal boundary、causal contamination 方法接到本项目；内容：检索 retrieval / temporal / causal contamination 近邻工作；依赖：先读 `EXPERIMENT_PLAN.md`。
- `FINAL_DIRECTION_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，需把辩论与文献结果综合成最终研究方向；内容：Quant 对保留/删除/新增实验模块给出最终建议；依赖：先读 `CREATIVE_*.md` 与两份 `LIT_*.md`。
- `FINAL_DIRECTION_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 版本的最终方向建议，重点压缩到 evidence intrusion 与 bounded mechanism claim；依赖：先读 `CREATIVE_*.md` 与两份 `LIT_*.md`。
- `FINAL_DIRECTION_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 版本的最终方向建议，强调识别与 estimand 收缩；依赖：先读 `CREATIVE_*.md` 与两份 `LIT_*.md`。
- `FINAL_DIRECTION_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 版本的最终方向建议，直接服务 proposal v2 重写；依赖：先读 `CREATIVE_*.md` 与两份 `LIT_*.md`。
- `EXPLORE_MEMORY_TYPES_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，PI 提出 “常识性记忆 vs 前瞻性记忆” 后，需要把 memory type 讲清楚；内容：Quant 把 Type A/B 拆成更细的金融记忆桶；依赖：先读 `FINAL_DIRECTION_*.md`。
- `EXPLORE_MEMORY_TYPES_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 把 Type A/B 对齐到 semantic / factual / item-level trace 的文献语言；依赖：先读 `FINAL_DIRECTION_*.md`。
- `EXPLORE_MEMORY_TYPES_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 解释 article-only CPT 为什么混合了 familiarity 与 outcome memory；依赖：先读 `FINAL_DIRECTION_*.md`。
- `EXPLORE_MEMORY_TYPES_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 说明这一拆分如何把论文从 measurement 改写成 mechanism；依赖：先读 `FINAL_DIRECTION_*.md`。
- `EXPLORE_FALSE_OUTCOME_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，Type A/B 提出后，需要设计真正的 Type B 干预；内容：Quant 论证 false-outcome CPT 与 CF rewrites 的互补性；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `EXPLORE_FALSE_OUTCOME_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 解释 false-outcome 注入与 visible-evidence 编辑的机制差异；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `EXPLORE_FALSE_OUTCOME_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 给出 2×3/2×2 识别视角与 formal estimand；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `EXPLORE_FALSE_OUTCOME_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 说明 false-outcome CPT 如何升级论文说服力；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `LIT_NEWS_ALPHA.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，回答 “这个研究对 alpha 有什么意义”；内容：检索新闻/文本驱动收益预测与 leakage-aware finance 文献；依赖：先读 `RESEARCH_PROPOSAL_v2.md` 或 `DISCUSSION_LOG_20260405.md` Round 9。
- `LIT_SCENARIO1_ORTHOGONAL.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，PI 的 S1 场景需要文献支撑；内容：检索“正交低泄露 micro-factor + ensemble”相关工作；依赖：先读 `LIT_NEWS_ALPHA.md`。
- `LIT_SCENARIO2_STABILIZER.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，PI 的 S2 场景需要文献支撑；内容：检索 feature robustness / stabilizer / regularizer 文献；依赖：先读 `LIT_NEWS_ALPHA.md`。
- `LIT_SCENARIO3_PRIMING.md` — 时间：2026-04-05（文内）/2026-04-06（入库）；背景：Phase 1，PI 的 S3 场景需要文献支撑；内容：检索 decomposition-first / grounding / priming 方向文献；依赖：先读 `LIT_NEWS_ALPHA.md`。
- `ALPHA_VALUE_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，Round 9 需要回答 “so what / alpha value”；内容：Quant 对 S1-S3 的经济现实性与论文边界做判断；依赖：先读 `LIT_NEWS_ALPHA.md` 与三份 `LIT_SCENARIO*.md`。
- `ALPHA_VALUE_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 从 representation / prompting 角度评估 S1-S3；依赖：先读 `LIT_NEWS_ALPHA.md` 与三份 `LIT_SCENARIO*.md`。
- `ALPHA_VALUE_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 把 “污染特征不稳定” 转成更可检验的推论；依赖：先读 `LIT_NEWS_ALPHA.md` 与三份 `LIT_SCENARIO*.md`。
- `ALPHA_VALUE_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 判断论文不必证明 alpha，只需证明污染特征不可靠；依赖：先读 `LIT_NEWS_ALPHA.md` 与三份 `LIT_SCENARIO*.md`。

#### v2 proposal 审阅与理论 tightening

- `REVIEW_V2_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，v2 proposal 成稿后需要重新做独立 domain review；内容：Quant 认为方向支持立项，但仍不是 alpha deployment 论文；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `REVIEW_V2_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 认为 v2 已接近 Findings 级，但仍有 inferability / construct validity 风险；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `REVIEW_V2_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 认为 v2 明显强于 v1，但仍需锁死 pre-registration 与主要混淆；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `REVIEW_V2_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 判断 v2 已进入可认真推进区间，但 scope 仍需继续收窄；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `REVIEW_V2_CHALLENGER.md` — 时间：2026-04-06（文内/入库）；背景：Phase 1，需要专门找 groupthink blind spots；内容：Claude Challenger 对 4 份 Codex 评审做 stress test；依赖：先读四份 `REVIEW_V2_*.md`。
- `DISCUSSION_LOG_20260406.md` — 时间：2026-04-06（文内/入库）；背景：Phase 1，需要把 v2 的独立 review、challenger 和 round2 响应串成一条线；内容：记录 convergent issues、divergences 与 remediation plan；依赖：先读四份 `REVIEW_V2_*.md` 与 `REVIEW_V2_CHALLENGER.md`。
- `ROUND2_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，Challenger 抬升了 CFLS construct-validity 风险后，需要二轮修正判断；内容：Quant 对 5 个攻击逐条回应并下调评分；依赖：先读 `REVIEW_V2_CHALLENGER.md`。
- `ROUND2_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 回应挑战并承认 CF template comparability 是 primary risk；依赖：先读 `REVIEW_V2_CHALLENGER.md`。
- `ROUND2_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 对 Challenger 的 A/E 攻击表示大体同意并要求更严 pre-spec；依赖：先读 `REVIEW_V2_CHALLENGER.md`。
- `ROUND2_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 重新评估 novelty risk、template mismatch 和 venue 策略；依赖：先读 `REVIEW_V2_CHALLENGER.md`。
- `EXPLORE_TEMPORAL_DIRECTIONALITY.md` — 时间：2026-04-06（git）；背景：Phase 1，PI 进一步提出 “时间可容许性” 应独立于 Type A/B；内容：把框架改成时间可得性/shortcut 类型/任务路径三轴；依赖：先读 `DISCUSSION_LOG_20260406.md`。
- `LIT_MEMORY_TAXONOMY_NLP.md` — 时间：2026-04-06（git）；背景：Phase 1，为时间方向性与 memory taxonomy 提供文献支撑；内容：从 NLP 文献整理 sequence/factual/schema/task memory 等维度；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `LIT_MEMORY_TAXONOMY_MECHINTERP.md` — 时间：2026-04-06（文内/入库）；背景：同上；内容：从 mechinterp 角度说明事实、实体、时间、上下文利用可能不是同一机制；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `LIT_MEMORY_TAXONOMY_FINANCE.md` — 时间：2026-04-06（文内）/附带 2025 文献日期；背景：同上；内容：把金融 look-ahead bias、LLM memorization、temporal evaluation 三条线连起来；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `LIT_MEMORY_TAXONOMY_COGSCI.md` — 时间：2026-04-06（git，文内未显式写日期）；背景：同上；内容：从认知科学角度为 memory taxonomy 找类比支撑；依赖：先读 `EXPLORE_MEMORY_TYPES_*.md`。
- `ROUND3_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1，在 temporal directionality 与多领域 taxonomy 到位后，需要第三轮独立收束；内容：Quant 对理论收缩和实验重心做最终判断；依赖：先读 `EXPLORE_TEMPORAL_DIRECTIONALITY.md` 与四份 `LIT_MEMORY_TAXONOMY_*.md`。
- `ROUND3_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 判断 v2 理论中心已需从 Type A/B 单轴改成三轴框架；依赖：先读 `EXPLORE_TEMPORAL_DIRECTIONALITY.md` 与四份 `LIT_MEMORY_TAXONOMY_*.md`。
- `ROUND3_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 要求把 “泄露” 定义明确写成依赖评估时点不可得信息；依赖：先读 `EXPLORE_TEMPORAL_DIRECTIONALITY.md` 与四份 `LIT_MEMORY_TAXONOMY_*.md`。
- `ROUND3_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 主张理论更精确但实验更收缩；依赖：先读 `EXPLORE_TEMPORAL_DIRECTIONALITY.md` 与四份 `LIT_MEMORY_TAXONOMY_*.md`。
- `EXPLORE_FAKE_REASONING_QUANT.md` — 时间：2026-04-06（git）；背景：Phase 1 late-stage，需区分分解任务收益来自真实 computation 还是 context priming / injected decomposition；内容：Quant 把它视为 context-faithful prompting vs fake reasoning 机制测验；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `EXPLORE_FAKE_REASONING_NLP.md` — 时间：2026-04-06（git）；背景：同上；内容：NLP 说明若 prefix 完全相同就不存在额外“自生成记忆”这一点；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `EXPLORE_FAKE_REASONING_STATS.md` — 时间：2026-04-06（git）；背景：同上；内容：Stats 给出 real vs injected decomposition 的 formal estimand；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `EXPLORE_FAKE_REASONING_EDITOR.md` — 时间：2026-04-06（git）；背景：同上；内容：Editor 警告 paper scope 已接近过载，fake reasoning 只能作为精简机制实验；依赖：先读 `docs/RESEARCH_PROPOSAL_v2.md`。
- `KICKOFF_TEMPLATE.md` — 时间：2026-04-06（git；文内未显式日期）；背景：Phase 1，多-agent 评审流程逐渐制度化，需要统一 kickoff 模板；内容：为后续 domain-agent 讨论提供标准化启动骨架；依赖：无，按需参考。

### refine-logs/pilot_discussion/

- `DISCUSSION_LOG_20260406.md` — 时间：2026-04-06（文内）/2026-04-08（入库）；背景：Phase 2，E_pilot 出结果后需要决定 go/no-go；内容：pilot 结果讨论的总日志，串起 round1、challenger、round2；依赖：先读 `docs/PILOT_RESULTS.md` 开头的 pilot 段。
- `round1_quant.md` — 时间：2026-04-08（git；内容属于 2026-04-06 讨论）；背景：Phase 2，pilot 结果的第一轮盲审；内容：Quant 把 CFLS≤0 解读为 pipeline-safe-ish 但 alpha-unproven；依赖：先读 `docs/PILOT_RESULTS.md`。
- `round1_nlp.md` — 时间：2026-04-08（git；内容属于 2026-04-06 讨论）；背景：同上；内容：NLP 认为全负 CFLS 更像 construct drift / uncalibrated metric；依赖：先读 `docs/PILOT_RESULTS.md`。
- `round1_stats.md` — 时间：2026-04-08（git；内容属于 2026-04-06 讨论）；背景：同上；内容：Stats 认为 pilot 不能点识别 memorization；依赖：先读 `docs/PILOT_RESULTS.md`。
- `round1_editor.md` — 时间：2026-04-08（git；内容属于 2026-04-06 讨论）；背景：同上；内容：Editor 主张 narrative 从 “decomposition reduces leakage” 改成 “CFLS 有构念问题”；依赖：先读 `docs/PILOT_RESULTS.md`。
- `round1.5_challenger.md` — 时间：2026-04-08（git）；背景：Phase 2，需要有人挑战四位 agent 对 “CFLS 坏掉了” 的共识；内容：指出 CFLS≤0 也可能是真阴性；依赖：先读四份 `round1_*.md`。
- `round1_summary.md` — 时间：2026-04-06（文内）/2026-04-08（入库）；背景：Phase 2，需要把四位 round1 agent 的结论压缩；内容：总结 round1 的 convergent points；依赖：先读四份 `round1_*.md`。
- `round2_quant.md` — 时间：2026-04-08（git）；背景：Phase 2，challenger 后第二轮修正；内容：Quant 接受 “无正控时 CFLS 非诊断性” 的修正；依赖：先读 `round1.5_challenger.md`。
- `round2_nlp.md` — 时间：2026-04-08（git）；背景：同上；内容：NLP 改口为 “CFLS 未校准，而非已证伪”；依赖：先读 `round1.5_challenger.md`。
- `round2_stats.md` — 时间：2026-04-08（git）；背景：同上；内容：Stats 认可真正缺的是 positive control / known-memorized items；依赖：先读 `round1.5_challenger.md`。
- `round2_editor.md` — 时间：2026-04-08（git）；背景：同上；内容：Editor 收缩到“先做 diagnostic，再决定 paper narrative”；依赖：先读 `round1.5_challenger.md`。
- `round2_summary.md` — 时间：2026-04-06（文内）/2026-04-08（入库）；背景：Phase 2，需要把 challenger 后的立场修正落成 actionable summary；内容：记录四位 agent 的 position revisions；依赖：先读四份 `round2_*.md`。
- `round3_summary.md` — 时间：2026-04-08（文内/入库）；背景：Phase 2，D1+D2 诊断与 code review 出来后需要再做一次总收束；内容：把 Q1/Q2/Q3、缺陷修复优先级和 paper reframing 聚合起来；依赖：先读 `docs/PILOT_RESULTS.md` 的 Diagnostic Results 段。

## 计划文件索引

> 计划文件已从 `~/.claude/plans/` 迁移至项目本地 `plans/` 目录（2026-04-12）。

- `phase5-qwen-positive-control.md` — 创建：2026-04-12；目的：Qwen 正向对照（CPT 4-arm 设计）+ 跨模型复制 + 综合分析；状态：**当前活跃计划**。
- `amber-mirror-lattice.md` — 创建：2026-04-11；目的：修复 v3 pipeline 的 5 个 silent bugs、重跑 D1、更新结果并设置 G1-G4 审阅门；状态：已完成。
- `deep-floating-lake.md` — 创建：2026-04-09；目的：把诊断样本扩到 400-700、重建 anchor/frequency/reversibility 标注，并实现 batched pipeline；状态：已完成。
- `gentle-bouncing-wozniak.md` — 创建：2026-04-06；目的：实现 E_pilot，包括 `direct_prediction` vs `decomposed_impact` 的 same-template bridge 和 false-outcome CPT；状态：已完成。

## Memory 索引摘要

- `User Profile` — 研究者画像：中文用户、Windows + conda、偏好简洁方案。
- `Project Setup` — 项目基础设施：ARIS skills、Codex MCP、`rag_finance`、vLLM Docker、代理与 CLS 数据位置。
- `Research Status` — 早期状态：6 个 notebooks 与 literature review 已完成，下一步是开题与方法深化。
- `Direction Pivot` — 2026-04-05 方向转折：binary contrast + evidence intrusion + Qwen continued pretraining / CPT 作为 causal anchor。
- `Discussion Log 2026-04-05` — 与 `refine-logs/DISCUSSION_LOG_20260405.md` 对应的 memory 快捷入口。
- `Infra Capabilities` — DeepSeek logprobs 不可用，Qwen vLLM white-box 可用，GPU 预算可调。
- `Literature Landscape` — 25+ papers 的方法地景与项目空白位。
- `Thales Connection` — 项目源自 Thales quant engine，alpha validation 是更深层动机。
- `Codex MCP Patterns` — Windows 上 Codex MCP 的使用经验与 token 分配策略。
- `Annotation Strategy` — 建议 LLM/sub-agent 先标，人工只复核分歧。
- `Agent Roles & Workflow` — 4 domain agents + 1 implementation gate 的固定分工。
- `API Concurrency` — DeepSeek=20、vLLM=16，不要使用默认 50。
- `CFLS Generalization Confound` — pilot 的核心记忆：CFLS 在常见金融事件上可能因双向泛化而失明。

## 数据资源索引

- `data/seed/memorization_probes.json` — Phase 0；最早的 probe 定义清单，用于初步 memorization audit；适合与归档 notebook 一起理解项目原点。
- `data/seed/test_cases.json` — Phase 2 前奏；约 42 条初始种子 case，是 E_pilot 的起点；先读它再看 `gentle-bouncing-wozniak.md` 最顺。
- `data/seed/annotation_batch_{1..3}.json` + `annotated_batch_{1..3}.json` — Phase 2；围绕 pilot/diagnostic 的早期扩样与标注批次；说明 seed set 是如何从小样本长出来的。
- `data/seed/expansion_candidates.json` — Phase 2；第一轮扩样候选池（count=85）；背景是 pilot 后需要补更多 case 做 diagnostic。
- `data/seed/test_cases_expanded.json` — Phase 2；192-case diagnostic 主样本；直接对应 `dc92c04` 和 `PILOT_RESULTS.md` 的 Diagnostic Results。
- `data/seed/expansion_candidates_v2.json` + `v2_batch_{1..4}.json` + `v2_annotated_{1..4}.json` — Phase 2→3 过渡；为 diagnostic 扩样与进一步重标注准备的 v2 中间产物。
- `data/seed/cases_for_anchor_analysis.json` + `anchor_analysis.json` — Phase 2→3；旧 anchor 分析材料与结果，后来因“手写/不可审计”被 `ANCHOR_RUBRIC.md` + v3 annotation 流程替代。
- `data/seed/expansion_candidates_v3.json` — Phase 3；两漏斗采样后的 v3 候选池（243 high-anchor + 247 low-anchor）；是 `deep-floating-lake` 采样策略的直接产物。
- `data/seed/test_cases_v3.json` — Phase 3；v3 主 case 集（count=682），所有 anchor/frequency 分析都以它为准；先读 `ANCHOR_RUBRIC.md` 再读它更容易理解字段。
- `data/seed/frequency_analysis_calibration.json` — Phase 3；BM25 `frequency_class` 阈值校准结果（n_cases=192）；服务于 v3 暴露代理构建。
- `data/seed/frequency_analysis.json` — Phase 3；682-case 的 frequency exposure 结果（n_cases=682）；对应 `deep-floating-lake` 里的 BM25 频率代理。
- `data/seed/strata_config.json` — Phase 3；记录为何最终把 4-level anchor collapse 成 `anchor_binary`；是后续所有 stratified analysis 的口径锚点。
- `data/seed/v3_annotation_prompts/*.json` + `v3_annotation_labels/*.json` + `v3_annotation_double/v3_double_annotation.json` — Phase 3；v3 标注 prompt、labels 和 double-annotation 可靠性材料；服务于 anchor/frequency/reliability 追溯。

## 配置索引

- `config/prompts/task_prompts.yaml` — 冻结版本：`2026-04-05-v2`；用途：定义 `direct_prediction`、`sentiment_classification`、`decomposed_authority`、`decomposed_novelty`、`decomposed_impact` 等任务 prompt 与输出 schema；产生阶段：Phase 1，为 v2 proposal 和 E_pilot/diagnostic 提供统一任务层。
- `config/prompts/counterfactual_templates.yaml` — 冻结版本：`2026-04-05-v2`，Phase 4 对共享 schema 做过 Bug 1 修复；用途：定义 `semantic_reversal`、`provenance_swap`、`novelty_toggle`、`sham_edits` 等 rewrite 模板及共享 `counterfactual_rewrite_v1` schema；产生阶段：Phase 1，后在 `amber` 中被审计与修复。
