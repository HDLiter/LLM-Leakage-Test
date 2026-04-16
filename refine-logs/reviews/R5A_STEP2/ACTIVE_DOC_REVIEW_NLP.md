## [NLP] Active Document Review

### 需要更新的文档
| 文档 | 问题类型 | 具体问题 | 建议修改 |
|---|---|---|---|
| [docs/BENCHMARK_PROPOSAL.md](</D:/GitRepos/LLM-Leakage-Test/docs/BENCHMARK_PROPOSAL.md>) | 术语一致性；范围一致性；事实过时；缺失更新 | 仍用 `probe protocol` / `task` / `condition` 语言；`semantic_reversal`、`false_outcome`、`neutral_paraphrase` 未映射到 `C_SR` / `C_FO` / `C_NoOp`；`masking strategies` 不符合 `C_anon` 的 `L0-L4` 多级设计；模型仍是 4-model 旧表；因素分类与冻结的 4 core factors 不一致。 | 按四层框架整体重写：以 `E_CMMD / E_PCSG / E_CTS / E_FO / E_NoOp` 为主；把 legacy conditions 映射到正式 perturbations；把 anonymization 改成 `C_anon L0-L4`；fleet 改为冻结 9-model，`P_logprob` 子集改为 5-model。若仅保留历史提案价值，转归档。 |
| [docs/CMMD_MODEL_FLEET_SURVEY.md](</D:/GitRepos/LLM-Leakage-Test/docs/CMMD_MODEL_FLEET_SURVEY.md>) | 事实过时；术语一致性；范围一致性 | 标题仍写 "6-model final fleet"；模型名单与冻结版不符，且 `Claude Sonnet 4.5`/`DeepSeek-V2.5` 已过时；仍用 `CMMD detector` 语言；"R5 Pre-commit Freeze" 与冻结 shortlist 冲突。 | 改成冻结 9-model fleet：`Qwen2.5-7B, Qwen2.5-14B, GLM-4-9B, DeepSeek-V3, GPT-4.1, GPT-5.1, Qwen3-8B, Qwen3-14B, Claude Sonnet 4.6`；单列 `P_logprob` 的 5-model 子集；把 `CMMD detector` 改写为 `E_CMMD (P_predict)`。 |
| [docs/DECISION_20260413_mvp_direction.md](</D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260413_mvp_direction.md>) | 术语一致性；范围一致性；事实过时；缺失更新 | 仍以 `detector investigation` 为主线；大量 `detector score`、`D11-D15`、`12-factor shortlist`、`detector-dependent factors`；factor 组织仍是旧的 spine/secondary/auxiliary；fleet 仍是 6-model；没有 `E/P/C/F` 映射。 | 至少加 superseded header，明确现行依据是 `R5A_FROZEN_SHORTLIST.md` 与 `MEASUREMENT_FRAMEWORK.md`；正文改成四层框架与 5 个 confirmatory estimands、4 个 core factors、9-model fleet；旧编号保留在附录 crosswalk。若不再作为现行决策源，转归档。 |
| [docs/FACTOR_LITERATURE_PROVENANCE.md](</D:/GitRepos/LLM-Leakage-Test/docs/FACTOR_LITERATURE_PROVENANCE.md>) | 术语一致性；缺失更新 | 文档仍停留在 pre-framework factor 语汇；对当前 4 core factors、exploratory/reserve 字段没有映射；出现 `detection methods` 等旧语。 | 保留文献 provenance 主体，但补一个 factor crosswalk：legacy factor names → `Cutoff Exposure / Historical Family Recurrence / Target Salience / Template Rigidity`，并注明哪些只属 exploratory。 |
| [docs/LITERATURE_SWEEP_2026_04.md](</D:/GitRepos/LLM-Leakage-Test/docs/LITERATURE_SWEEP_2026_04.md>) | 术语一致性；范围一致性；事实过时；缺失更新 | 通篇使用 `detector pool`、`detector candidates`、`detector-level stratification`；仍引用 `D1-D12`；沿用 6-model CMMD fleet；部分章节仍是 `3-bloc`；把 Entity-Anonymization Sensitivity 当成 detector-level field，而不是 perturbation。 | 重写为 estimand/operator/perturbation 家族语言；把 `D7 EAD` 改成 `E_EAD_t / E_EAD_nt + C_anon`；把 `D11` 改成 `E_TDR` interaction-only；删去 `D9/D10` 活跃措辞；fleet 与 bloc 结构更新到冻结版本。 |
| [docs/THALES_SIGNAL_PROFILE_REVIEW.md](</D:/GitRepos/LLM-Leakage-Test/docs/THALES_SIGNAL_PROFILE_REVIEW.md>) | 事实过时；缺失更新 | 虽然不是 estimand 文档，但 `Event Type` 仍写 `7-cat draft`，与当前层级化 `15-20 + 5-7` 不一致。 | 保持 scope 不变，但把 taxonomy 注释和结论更新到当前层级体系；无需强行套入四层框架。 |
| [docs/TIMELINE.md](</D:/GitRepos/LLM-Leakage-Test/docs/TIMELINE.md>) | 术语一致性；事实过时 | 已正确写出四层框架，但 Phase 6 仍写 `10 候选 detector`，fleet review 仍写 6-model。 | Phase 6 改成 frozen shortlist 的正式语言：confirmatory / exploratory estimands、operators、perturbations；fleet 改成冻结 9-model，并标明 `2026-04-16` 冻结。 |
| [PAPER_INDEX.md](</D:/GitRepos/LLM-Leakage-Test/PAPER_INDEX.md>) | 事实过时 | 纯 bibliography index，无框架问题，但停止在 `2026-04-06`，缺少后续新增论文。 | 补齐 `2026-04-06` 之后纳入的论文，并在文首标注 last-sync date。 |
| [config/prompts/README.md](</D:/GitRepos/LLM-Leakage-Test/config/prompts/README.md>) | 术语一致性；范围一致性；缺失更新 | 仍使用 `direct_prediction / decomposed_impact / decomposed_authority` 与 `E1-E6` 实验编号；没有 `P_predict / P_logprob / P_extract / P_schema` 语汇；当前 README 实际描述的是 Phase 0-4 frozen prompts，而不是 R5A schema。 | 将现 README 标成 historical schema；新增 R5A prompt schema 文档，按 operator 划分：`P_predict`、`P_logprob`、`P_extract`、`P_schema`(candidate/reserve)。 |

### 可归档的文档
| 文档 | 理由 |
|---|---|
| [refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md>), [BENCHMARK_R4_FINAL_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md>), [BENCHMARK_R4_CHALLENGER.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/BENCHMARK_R4_CHALLENGER.md>), [BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md>) | 全部是 R4 / v5.2 时代的 detector-centered 综合件；`12-factor shortlist`、`D9/D10`、旧 fleet 与旧框架均已被 v6.2 + 冻结 shortlist 覆盖。保留溯源价值即可，不应继续充当现行依据。 |
| [refine-logs/reviews/BENCHMARK_R5_KICKOFF.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/BENCHMARK_R5_KICKOFF.md>) | 属于 kickoff 历史记录；虽对当时语境合理，但 `detector families`、`D1-D10`、旧 fleet 起点都已被四层框架替代。 |
| [refine-logs/reviews/R5A_STEP2/R5A_STEP2_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/R5A_STEP2_SYNTHESIS.md>) | 这是冻结 shortlist 的直接前身，概念上有高 provenance 价值，但术语已被 `MEASUREMENT_FRAMEWORK.md` 取代；应归入 pre-freeze rationale。 |
| [refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md>) | 中间版 fleet synthesis，已被 `FLEET_REVIEW_R2_SYNTHESIS.md` 覆盖。 |
| [refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md>) 与 [R5A_STEP1_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md>) | Step 1 pool 文档，只反映 pre-freeze 候选池与 `D1-D12` 命名；冻结后不应继续作为 shortlist 依据。 |
| [refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md>) | 其中有效内容已吸收到 `E_TDR`、`C_temporal` 与 factor 讨论中；旧 `D11/D7/D4` 命名不应继续裸用。 |
| [refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md>) 到 [LIT_SWEEP_E_CONSTRUCT_VALIDATION.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md>) | 这是 2026-04-14/15 的 pre-framework 工作底稿；适合作为 archive corpus，不适合作为现行术语或结构依据。 |
| [refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md>) | 编辑建议针对的是 pre-freeze 结构，尤其把 EAS 当 detector-level field；现已被 `C_anon` redesign 覆盖。 |
| [plans/phase5-qwen-positive-control.md](</D:/GitRepos/LLM-Leakage-Test/plans/phase5-qwen-positive-control.md>) | 明确属于 pre-benchmark-pivot 的历史计划；应移入历史目录或加 `historical / superseded` 标记。 |

### 无需改动的文档
[docs/MEDIA_COVERAGE_FEASIBILITY.md](</D:/GitRepos/LLM-Leakage-Test/docs/MEDIA_COVERAGE_FEASIBILITY.md>)  
[refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md>)  
[refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md](</D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md>)

### 跨文档矛盾
- **fleet 基线冲突最明显**：多份 active 文档仍写 6-model，而冻结基线已经是 9-model；`P_logprob` 子集也应固定为 5-model。
- **`detector / D1-D12` 与四层框架并存**，造成同一对象双重命名。建议统一 crosswalk：`D1→E_CMMD`，`D2→E_PCSG`，`D3→E_CTS`，`D4a→E_ADG_conflict`，`D4b→E_ADG`，`D5-SR→E_SR`，`D5-FO→E_FO`，`D6→E_NoOp`，`D7→E_EAD_t / E_EAD_nt`，`D8→E_extract`，`D11→E_TDR`，`D12→P_schema candidate family / E_schema_cont reserve`。
- **`C_anon` 设计冲突**：旧文档里的 `masking strategies`、binary anonymization、`detector-level field` 都与冻结版 `L0-L4` dose-response perturbation 不一致。
- **`E_TDR` 定义冲突**：旧文档把 `D11` 写成 standalone detector / protocol；现行定义是 mixed-effects model 里的 `cutoff × dose` interaction term，不能单列为 standalone estimand。
- **scope 冲突仍残留在旧 shortlist 资料中**：`D9 RAVEN`、`D10 Debias Delta` 已 dropped；`P_schema` 只有 continuation 仍在 reserve，`Cloze/QA` 都是 defer，不应再写成 active。
- **factor 组织冲突**：`12-factor shortlist`、`spine/secondary/auxiliary`、`3-bloc` 与冻结后的 `4 core confirmatory factors + exploratory/reserve` 不是同一层级，应避免混写。
- **governance 信息在多份 active 文档中缺失**：`E_FO` 与 `E_NoOp` 的 `≥85%` audit gate，以及 `E_ADG / E_extract / E_schema_cont` 的 reserve promotion rules，需要补到现行规范文档里。
