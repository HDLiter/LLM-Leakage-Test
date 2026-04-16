## [Stats] Active Document Review

### 需要更新的文档
| 文档 | 问题类型 | 具体问题 | 建议修改 |
|---|---|---|---|
| `docs/DECISION_20260413_mvp_direction.md` | 术语一致性；范围一致性；事实过时；缺失更新 | 仍以 `detector`/`detector score` 为核心对象，主叙事仍是 `12-factor shortlist`、`6-model` 参考 fleet、`N=3,200 gross`；缺少冻结后的 `5 estimands × 4 core factors = 20 coefficients`、`Westfall-Young stepdown max-T`、`E_FO/E_NoOp` 质量门、reserve promotion rules、`E_TDR = β₃=cutoff×dose` mixed-model 重定义。 | 顶部加醒目 superseded box；将本文件降级为"数据域/MVP 方向与历史沿革"，统计设计全部指向 `R5A_FROZEN_SHORTLIST.md` + `MEASUREMENT_FRAMEWORK.md`；最好补一个旧→新 crosswalk。 |
| `docs/FACTOR_LITERATURE_PROVENANCE.md` | 范围一致性；事实过时 | 仍写成 `v5.3 active+reserve shortlist = 15 factors + 2 additions` 的 provenance audit；和当前"13 primary factors / 4 blocs"及"4 core confirmatory factors"不对齐。 | 保留为 provenance 背景文档，但需在开头说明"不是当前 active factor map"；加一张 crosswalk：`4 core factors`、`Bloc 3 interaction-menu factors`、`reserve/candidate`。 |
| `docs/MEDIA_COVERAGE_FEASIBILITY.md` | 范围一致性；事实过时 | 仍以 `3,200` 为默认 operational N，并写成"不要立即升为第 13 个 active factor"；未对齐冻结后的 `2,560 scorable from 3,200 gross`，也未说明它不属于当前 frozen confirmatory family。 | 改成"candidate extra-corpus factor / pilot-gated background note"；把 N 表述改为"`3,200 gross / 2,560 scorable`"；删除"13th active factor"说法，明确其不会自动改变 20-coefficient confirmatory family。 |
| `docs/TIMELINE.md` | 范围一致性；事实过时 | 已正确指向 frozen shortlist，但仍把 `docs/DECISION_20260413_mvp_direction.md` 放在"权威文档"层，并把 `BENCHMARK_PROPOSAL.md`、`plans/phase5-qwen-positive-control.md` 继续挂在 active index。 | 将"权威文档"缩到 `R5A_FROZEN_SHORTLIST.md` + `MEASUREMENT_FRAMEWORK.md`；把 `DECISION...` 降为 background；把 Phase 5 文档移到 historical/background。 |
| `plans/phase5-qwen-positive-control.md` | 范围一致性；事实过时；缺失更新 | 仍以旧的单模型 CPT confirmatory protocol 为主，`confirmatory` 含义与当前 20-coefficient family 不同；当前仅"Qwen CPT causal anchor"仍相关。 | 若保留，顶部注明"仅 CPT causal anchor 仍有效，非当前 benchmark confirmatory family"；更好的做法是摘出 CPT anchor 依赖说明，原计划归档。 |
| `config/prompts/README.md` | 范围一致性；事实过时 | 仍是 `2026-04-05-v2` 的 `E1-E6 / probe protocol / direct_prediction / decomposed_*` 体系；与当前 `P_predict / P_extract / perturbation` 结构没有映射，但 frozen shortlist 又把 `config/prompts/` 当成 live prompt pointer。 | 重写 README：明确哪些 legacy prompts 仍服务于 `P_predict`/`P_extract`/`C_SR`/`C_FO`，哪些已废弃；否则把该 README 归档并新增一个 R5A prompt index。 |

### 可归档的文档
| 文档 | 理由 |
|---|---|
| `docs/BENCHMARK_PROPOSAL.md` | 完全 pre-four-layer：`~2000 cases`、`6 factors`、`4 models`、`probe protocol`；已被 R5A benchmark design 全面取代。 |
| `docs/CMMD_MODEL_FLEET_SURVEY.md` | 明确写成 `6-model final fleet`，已被 `R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` 的 `9-model core fleet` 取代。 |
| `docs/LITERATURE_SWEEP_2026_04.md` | 这是 `v5.3→v6` 的 sweep bridge 文档，而且仅 Session 1 summary；保留研究轨迹价值，但不应继续作为 active methodology doc。 |
| `docs/THALES_SIGNAL_PROFILE_REVIEW.md` | 背景性 taxonomy/signal review，不是 frozen statistical authority；可转入 background/archive。 |
| `refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md`、`BENCHMARK_R4_FINAL_SYNTHESIS.md`、`BENCHMARK_R4_CHALLENGER.md`、`BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md` | 全部建立在 `12-factor shortlist` 和 pre-R5A detector handoff 上；现仅具历史审阅价值。 |
| `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md`、`R5A_STEP1/R5A_DEFAULTS.md`、`R5A_STEP1/R5A_STEP1_SYNTHESIS.md`、`R5A_STEP2/R5A_STEP2_SYNTHESIS.md`、`R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md` | 都是 pre-freeze detector-stage 设计日志；仍保留旧 `detector` 框架、旧 confirmatory composition、旧 `E_TDR` 语义。尤其 `R5A_STEP2_SYNTHESIS.md` 已被 frozen shortlist front matter 明确 supersede。 |
| `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md` | Round 1/7-model baseline；已被 Round 2 的 9-model synthesis supersede。 |
| `refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md`、`LIT_SWEEP_B_BROAD_SWEEP.md`、`LIT_SWEEP_C_CHRONO_BASELINES.md`、`LIT_SWEEP_D_CITED_BUT_UNREAD.md`、`LIT_SWEEP_E_CONSTRUCT_VALIDATION.md`、`LIT_SWEEP_V6_EDIT_PROPOSALS.md` | 原始 sweep 输出和 edit proposals；保留 provenance 价值，但不应继续作为 active project methodology 文档。 |

### 无需改动的文档
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md`
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md`
- `PAPER_INDEX.md`

### 跨文档矛盾
- `docs/TIMELINE.md` 仍把 `docs/DECISION_20260413_mvp_direction.md` 放在"权威文档"层，但后者的统计层仍是 pre-freeze；当前真正权威应是 `R5A_FROZEN_SHORTLIST.md` 和 `MEASUREMENT_FRAMEWORK.md`。
- Fleet 口径分裂：`docs/CMMD_MODEL_FLEET_SURVEY.md`、`BENCHMARK_R5_KICKOFF.md`、`docs/DECISION_20260413_mvp_direction.md` 仍保留 `6-model` 叙述，而 `FLEET_REVIEW_R2_SYNTHESIS.md`、`FLEET_SELECTION_LITERATURE.md`、`docs/TIMELINE.md`、`R5A_FROZEN_SHORTLIST.md` 已是 `9-model`。
- `E_TDR` 口径分裂：旧文档里仍是 standalone detector / sensitivity protocol；`MEASUREMENT_FRAMEWORK.md` 还是 second-order slope；最终权威是 `R5A_FROZEN_SHORTLIST.md` 中的 mixed-model interaction `β₃ = cutoff×dose`。
- `config/prompts/README.md` 仍是 legacy `E1-E6`/probe 体系，但项目当前已转为 `Factor / Perturbation / Operator / Estimand` 四层框架；live prompt pointer 与 live methodology layer 没有对齐。
- 多个成本/样本量文档仍直接写 `N=3,200`；冻结后应区分 `3,200 gross` 与 `2,560 scorable`，否则会把采样目标和分析样本混为一谈。
