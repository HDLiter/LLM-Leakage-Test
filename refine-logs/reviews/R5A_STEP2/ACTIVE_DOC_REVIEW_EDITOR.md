## [Editor] Active Document Review

### 需要更新的文档
| 文档 | 问题类型 | 具体问题 | 建议修改 |
| --- | --- | --- | --- |
| `docs/FACTOR_LITERATURE_PROVENANCE.md` | 术语/范围 | 仍以 `v5.3 active+reserve shortlist` 的 15+2 口径组织，并沿用 `spine/secondary/auxiliary`；未对接 `13 primary factors / 4 blocs / Factor-Perturbation-Operator-Estimand` | 保留文献证据本体，重写导言与目录；按 13 个 primary factors 重排，并加一张"旧因子名 → 冻结框架名"映射表；把 `Modality`/`Authority` 明确标成 Bloc 3 候选/补充信息，而非现行 active factor |
| `docs/LITERATURE_SWEEP_2026_04.md` | 术语/事实过时 | 执行摘要仍写 `15 factors`、`v5.2 6-model fleet`、`3-bloc`、`detector` 语言；作为活跃综述会误导后续写作 | 在文首加 `historical sweep feeding v6.x, not current spec` 的说明；保留检索发现，但把"当前结论"改成对 frozen shortlist 的支撑性总结，并显式标注 fleet 结论已被 `FLEET_REVIEW_R2_SYNTHESIS` / frozen shortlist supersede |
| `docs/MEDIA_COVERAGE_FEASIBILITY.md` | 范围/事实过时 | 仍以"可晋升为第 13 个 active factor"与旧 `P1 headroom` 语言讨论，且仍沿用旧目标样本量口径 | 改写为"reserve-factor feasibility memo"；明确它不属于当前 frozen confirmatory scope，只是未来 reserve/candidate；同步 `N=2560` 口径，并删除"13th active factor"表述 |
| `docs/THALES_SIGNAL_PROFILE_REVIEW.md` | 语境过时 | 技术内容本身有价值，但 `P1`、旧 factor 计数、旧 Event Type 讨论语境仍在，容易被误读为当前规范 | 在开头增加"仅服务于 Bloc 3 operationalization"的定位；把 `Modality/Authority` 结论映射到当前 frozen framework，并删除任何会被读成"改变现行 factor 计数"的表述 |
| `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` | 术语轻度不一致 | 9-model core 与 frozen shortlist 一致，但仍大量使用 `detector` 语言，并保留 `GPT-5.4 optional 10th` 的预冻结表述 | 不改核心 fleet 内容；仅补一个 freeze note：当前 frozen core 为 9 模型，`GPT-5.4` 只是历史可选讨论；把 `logprob/behavioral detectors` 改写或脚注映射到 `P_logprob/P_predict` |
| `PAPER_INDEX.md` | 事实过时/索引缺失 | 仍停在 `2026-04-06`、`60 PDFs`；缺失 R4 Session 1+2、fleet review、construct validity、chronological control 等新增文献；存在重复项 | 全量刷新并去重；新增分类：memorization/MIA foundations、chronological controls、construct validity、finance look-ahead、fleet selection；注明新增来源批次 |
| `config/prompts/README.md` | 实现断裂/术语冲突 | 这是 `2026-04-05-v2` 的旧 task-probe prompt freeze，仍以 `direct_prediction/decomposed_impact/...` 为中心；与 frozen shortlist 的 `P_predict/P_logprob/P_extract` operator 设计脱节 | 明确标注该目录为 `legacy Phase 0-4 prompt schema`；另立 R5A operator prompt spec，定义 `P_predict/P_logprob/P_extract` 的现行 prompts、版本号、审计门槛和与 perturbation 的关系 |
| `docs/TIMELINE.md` | 索引修补 | 主体已正确，但 document index 仍把 `BENCHMARK_PROPOSAL.md` 视作活跃文档，且未提示 prompt schema 断裂 | 做一次轻量索引修补：给 `BENCHMARK_PROPOSAL.md`、`CMMD_MODEL_FLEET_SURVEY.md`、`plans/phase5-qwen-positive-control.md` 加 historical/archived 标记，并补一条 `config/prompts/README.md` 为 legacy schema 的说明 |

### 可归档的文档
| 文档 | 理由 |
| --- | --- |
| `docs/BENCHMARK_PROPOSAL.md` | Phase 5 早期 proposal，双语设计、4-model fleet、6-factor taxonomy、probe protocol 全部被 frozen shortlist / measurement framework supersede；适合作为 pivot 史料，不适合作为现行规范 |
| `docs/CMMD_MODEL_FLEET_SURVEY.md` | 6-model `R5 Pre-commit` 方案已被 `FLEET_REVIEW_R2_SYNTHESIS` 与 frozen 9-model fleet 完全取代；应转入 archive，并在原位置留指针 |
| `docs/DECISION_20260413_mvp_direction.md` | 这是 v6.2 历史决策总账，不再适合作为活跃设计文档：12-factor、6-model、R5 open items、`N=3200`、P1-P5 与 frozen scope 均冲突；建议保留 provenance，但移入 decision-history |
| `plans/phase5-qwen-positive-control.md` | 作为 benchmark pivot 前计划已整体过时；唯一仍活的是 "Qwen CPT causal anchor" 背景，应提炼到新文档后归档原计划 |
| `refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md`, `BENCHMARK_R4_FINAL_SYNTHESIS.md`, `BENCHMARK_R4_CHALLENGER.md`, `BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md`, `BENCHMARK_R5_KICKOFF.md` | 全部属于 pre-freeze 过程文档，术语与范围整体停留在 detector/12-factor 阶段；保留审议痕迹即可，不应继续暴露为活跃规范 |
| `refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md`, `refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md`, `refine-logs/reviews/R5A_STEP2/R5A_STEP2_SYNTHESIS.md`, `refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md` | 这些是 frozen lineage 的输入文档，不是现行口径；内容可保留为历史输入，但应整体标记 `historical input / superseded by MEASUREMENT_FRAMEWORK + R5A_FROZEN_SHORTLIST` |
| `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md` | Round 1 fleet verdict 已被 Round 2 取代，无继续保留为活跃文档的必要 |
| `refine-logs/reviews/LIT_SWEEP_*.md` | 这些是原始 sweep 输出与 edit proposals，历史价值大于现行规范价值；建议归档，只保留 `docs/LITERATURE_SWEEP_2026_04.md` 作为活跃汇总 |

### 无需改动的文档
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`
- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md`
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md`

### 跨文档矛盾
- `config/prompts/README.md` 与 `R5A_FROZEN_SHORTLIST.md`/`MEASUREMENT_FRAMEWORK.md` 存在"冻结对象"冲突：前者冻结的是旧 task-probe prompts，后者冻结的是 R5A measurement scope，且当前 operator schema 尚未真正落到 prompt 层。
- `docs/CMMD_MODEL_FLEET_SURVEY.md`、`docs/LITERATURE_SWEEP_2026_04.md`、`BENCHMARK_R5_KICKOFF.md`、`R5A_STEP1_SYNTHESIS.md`、`R5A_TEMPORAL_CUE_SYNTHESIS.md` 仍写 6-model fleet，而 frozen shortlist 的权威口径是 9-model core。
- `docs/DECISION_20260413_mvp_direction.md`、`docs/FACTOR_LITERATURE_PROVENANCE.md`、`docs/LITERATURE_SWEEP_2026_04.md` 仍用 `12-factor` 或 `15+2 shortlist` 加 `spine/secondary/auxiliary`；权威口径已经是 `13 primary factors / 4 blocs / four-layer framework`。
- `R5A_STEP2_SYNTHESIS.md` 仍把 D1-D12 detector slots 当作主设计单位，且一度把 `D7/EAD` 放进 confirmatory family；frozen shortlist 已改为 5 个 confirmatory estimands × 4 core factors，`EAD` 明确为 exploratory。
- `R5A_TEMPORAL_CUE_SYNTHESIS.md` 与若干旧文档仍把 `D11/E_TDR` 当成独立 detector/protocol；frozen shortlist 已把 `E_TDR` 改成 mixed-model 的二阶交互项，不再是 standalone estimand。
- `docs/DECISION_20260413_mvp_direction.md`、`docs/MEDIA_COVERAGE_FEASIBILITY.md`、旧 fleet review 成本测算仍大量使用 `N=3200`；当前 frozen target 已改为 `N=2560`。
- `docs/TIMELINE.md` 已认定 frozen shortlist 为权威，但索引层仍未把 `BENCHMARK_PROPOSAL.md`、`CMMD_MODEL_FLEET_SURVEY.md`、`phase5-qwen-positive-control.md` 标成历史文档，造成"权威口径已冻结、入口索引仍暴露旧规范"的状态漂移。
