# Project Timeline & Document Index

> 本文档是项目探索过程的时间轴索引，供后续 agent 快速理解项目历史和文档关系。
> 最后更新：2026-04-16

## 项目概述

本项目研究中文金融新闻（CLS 电报）中 LLM 的训练数据泄露问题，构建一个 factor-driven memorization benchmark。项目经历了从单模型检测到多模型 benchmark 的方向转折（Phase 5, 2026-04-12），当前采用四层测量框架（Factor → Perturbation → Operator → Estimand），已完成概念设计冻结（R5A, 2026-04-16），准备进入 pilot 实施阶段。

**当前权威文档**: `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`

## Authority chain (post-freeze, 2026-04-16)

> 任何新 agent 进入项目，权威文档以下列三份为准；其余 docs/ 与 refine-logs/ 内容均为历史/背景/可行性输入，**不构成当前 spec**：
>
> - `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — **frozen scope**（确认性/探索性估计量、质量门、晋升规则）
> - `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` — **framework definitions**（Factor / Perturbation / Operator / Estimand 四层框架与术语）
> - `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` — **frozen 9-model fleet**（5 white-box + 4 black-box；thinking-mode policy 见 MEASUREMENT_FRAMEWORK）

## Archive notice (2026-04-16)

Phase 1-4 的文档（proposals, debates, pilot results, bug audits）已归档到 `archive/pre_benchmark/`。Benchmark 早期审阅轮次（R1-R3）已归档到 `archive/benchmark_r1_r3/`。R4 / R5A 前置过程文档（R4 review chain, R5A Step 1-2 process, fleet review Round 1, literature sweep raw outputs, Phase 5 plan, R4 时期混合判定文档）已归档到 `archive/r4_r5a_lineage/`。详见各目录下的 README.md。

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
- **关键发现**: Bug 1 修复后恢复约 150 个 CFLS 可评分 case；Bug 3 把 `decomposed_impact` 的 CPT 结论从”全零/退化”改写为 memorization-direction（pooled MH OR≈1.95），但 `direct_prediction` 仍主要呈现 suggestibility。

### Phase 5: Qwen positive control → benchmark pivot（2026-04-12）

- **产出文档**: `PREREGISTRATION.md`（v1.3, now archived）、`DECISION_20260411_post_amber.md`（archived）、`plans/phase5-qwen-positive-control.md`、`BENCHMARK_PROPOSAL.md`。
- **关键发现**: Qwen 2.5 7B 未复现 DeepSeek 的 task-dependent 模式 → 论文方向 pivot 到 factor-controlled cross-model benchmark。
- **归档说明**: Phase 5 前的所有文档已移至 `archive/pre_benchmark/`。

### Phase 6: R5A — Benchmark design（2026-04-12 ~ 2026-04-16）

- **R4 文献综合（Apr 12-15）**: 4 轮 benchmark 审阅（R1-R3 已归档到 `archive/benchmark_r1_r3/`；R4 保留在 `refine-logs/reviews/`）。文献扫描产出 `docs/LITERATURE_SWEEP_2026_04.md` 和 `docs/FACTOR_LITERATURE_PROVENANCE.md`。Decision doc 从 v5.2 迭代到 v6.2 → `docs/DECISION_20260413_mvp_direction.md`。
- **R5A Step 1（Apr 14-15）**: 10 候选 estimand candidates 的 4-lens opening positions → convergence synthesis。产出 `refine-logs/reviews/R5A_STEP1/`（已归档）。
- **R5A Fleet Review（Apr 14-15）**: 9-model core fleet selection (FLEET_REVIEW R2) with 25+ paper survey。产出 `refine-logs/reviews/R5A_FLEET_REVIEW/`。Same-cutoff falsification pair (GLM-4-9B ↔ GPT-4.1) 是文献中的新设计。
- **R5A Temporal Cue（Apr 15）**: C_temporal perturbation deep dive → E_TDR design。产出 `refine-logs/reviews/R5A_TEMPORAL_CUE/`。
- **R5A Step 2（Apr 15-16）**: 4-lens convergence → **四层测量框架** (Factor/Perturbation/Operator/Estimand)，溶解 4 个设计张力。产出 `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md`。
- **R5A Freeze Session（Apr 16）**: P_schema 讨论（4-lens, Continuation=RESERVE, Cloze/QA=DEFER）→ 仲裁点闭合 → Challenger pass（10 项，3 高严重度全部关闭）→ Cold reader pass（Codex Reviewer 2, 构念效度攻击 → 三道防线）→ **概念 shortlist 冻结**。
- **关键提交**: `b6d20ae`（R5A Step 1）、`99a9e5c`（R5A Step 2 + four-layer framework）。
- **产出文档**: `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — **权威冻结文档**。

### Next: Phase 7 — Pilot implementation

1. P_logprob pipeline（白盒，5 models）
2. P_predict pipeline（9 models）
3. C_FO + C_NoOp perturbation generation + quality gates
4. ~100-case pilot run
5. Power analysis + pre-registration draft

## 近期提交参考

```text
99a9e5c 2026-04-15 R5A Step 2: 4-lens convergence + four-layer measurement framework
b6d20ae 2026-04-15 R5A detector investigation: Step 1 complete, pre-Step 2 sessions done
aca99bc 2026-04-14 R4 literature sweep: Sessions 1+2 complete, decision doc v5.3 → v6.2
6806383 2026-04-13 decision doc v5.3: user clarifications on 5 open questions
f4bbcf5 2026-04-13 R4 closure: apply post-v5.2 integration review fixes
c12a43f 2026-04-12 benchmark proposal: add masking/mitigation track + multi-method compatibility
605e56b 2026-04-12 Phase 5 B: Qwen baseline results + FinMem-Bench proposal
d33f4a9 2026-04-12 Phase 5 setup: pre-registration (v1.3) + decision record + execution plan
```

See `git log --oneline -30` for full recent history.

## 当前文档索引（Phase 6+ 活跃文档）

> Phase 1-4 文档已归档到 `archive/pre_benchmark/`，详见该目录 README。
> R1-R3 审阅轮次已归档到 `archive/benchmark_r1_r3/`，详见该目录 README。

### 权威文档（从这里开始读）

仅以下两份冻结文档为权威：

- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — **R5A 冻结概念 shortlist**。定义确认性/探索性估计量、质量门、晋升规则、Challenger/Cold reader 行动项。
- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` — **四层测量框架**。Factor/Perturbation/Operator/Estimand 定义与术语。

> 注：`docs/DECISION_20260413_mvp_direction.md` 已归档至 `archive/r4_r5a_lineage/docs/`，作为历史决策背景保留，不再列为权威文档（其统计层 12-factor / 6-model / N=3200 等已 pre-freeze）。9-model fleet 与 thinking-mode policy 现以 `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` + `MEASUREMENT_FRAMEWORK.md` 为准。

### docs/（活跃）

> `BENCHMARK_PROPOSAL.md` 与 `CMMD_MODEL_FLEET_SURVEY.md` 已移至 `archive/r4_r5a_lineage/docs/`。

- `FACTOR_LITERATURE_PROVENANCE.md` — pre-freeze 15+2 因子溯源审计。**非当前活跃因子图**；当前因子范围由 `R5A_FROZEN_SHORTLIST.md`（4 core confirmatory + Bloc 0-3 inventory）定义。Old → new 映射见 `refine-logs/reviews/R5A_STEP2/ACTIVE_DOC_REVIEW_SYNTHESIS.md` §2 (Priority B crosswalk)。
- `LITERATURE_SWEEP_2026_04.md` — 历史 R4 文献扫描（25+ papers），feed into decision-doc v5.3→v6.2。结论中关于 fleet/scope 的部分已被 `FLEET_REVIEW_R2_SYNTHESIS.md` + `R5A_FROZEN_SHORTLIST.md` 取代；保留作为引用溯源。
- `MEDIA_COVERAGE_FEASIBILITY.md` — Coverage Breadth 储备因子可行性 memo。**不在冻结 confirmatory family 中**；不读为"第 13 个活跃因子"。
- `THALES_SIGNAL_PROFILE_REVIEW.md` — Thales quant engine 信号档案；Bloc 3 operationalization input（Structured Event Type / Modality / Authority）。不改变冻结 confirmatory family。
- `TIMELINE.md` — 本文档。

### refine-logs/reviews/（活跃）

post-archive 仅保留以下 R5A 后期文档；R4 系列、R5_KICKOFF、R5A_STEP1/、R5A_STEP2/R5A_STEP2_SYNTHESIS.md、R5A_TEMPORAL_CUE/、FLEET_REVIEW_SYNTHESIS.md、LIT_SWEEP_*.md 已归档至 `archive/r4_r5a_lineage/refine-logs/reviews/`。

- `R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — **权威冻结文档**
- `R5A_STEP2/MEASUREMENT_FRAMEWORK.md` — **权威四层框架**
- `R5A_STEP2/ACTIVE_DOC_REVIEW_*.md` — 4 lens reports + synthesis（post-freeze cleanup）
- `R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` — current 9-model fleet authority
- `R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md` — external lit review

### plans/（活跃）

> 当前为空。`plans/phase5-qwen-positive-control.md` 已归档；其 Qwen CPT causal anchor 概念已纳入 `R5A_FROZEN_SHORTLIST.md`（Construct validity strategy: multi-signal convergence + Qwen CPT causal anchor）。

### archive/

- `pilot_phase/` — Phase 0 notebooks + scripts（2026-03-12 to 2026-04-04）
- `pre_benchmark/` — Phase 1-4 docs, refine-logs, plans（2026-04-05 to 2026-04-12）
- `benchmark_r1_r3/` — Benchmark review rounds 1-3（superseded by R4+R5A）
- `r4_r5a_lineage/` — Pre-R5A-freeze docs (R4 review chain, R5A Step 1-2 process, fleet review Round 1, literature sweep raw outputs, Phase 5 plan, mixed-verdict docs from R4 era). Date archived: 2026-04-16.

### 其他活跃文件

- `PAPER_INDEX.md` — 参考论文索引
- `related papers/` — 论文 PDF 和笔记
- `config/prompts/` — 冻结 prompt schema
- `data/seed/` — 测试数据（Phase 0-3 seed files, to be expanded in Phase 7）
