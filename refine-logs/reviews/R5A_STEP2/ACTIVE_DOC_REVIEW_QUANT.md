## [Quant] Active Document Review

### 需要更新的文档
| 文档 | 问题类型 | 具体问题 | 建议修改 |
|---|---|---|---|
| `docs/CMMD_MODEL_FLEET_SURVEY.md` | 事实过时 / 权威链 | 仍把 `6-model final fleet` 写成结论；含 `DeepSeek-V2.5`、`Claude Sonnet 4.5`；缺 `Qwen2.5-14B`、`Qwen3-8B`、`GPT-4.1`、`GPT-5.1`；成本按 `6 × 3,200` 估算；未区分 `P_logprob` 仅 5 白盒 vs `P_predict/P_extract` 9 模型 | 开头加 `superseded by FLEET_REVIEW_R2_SYNTHESIS + R5A_FROZEN_SHORTLIST`；顶部改成 frozen 9-model fleet；显式写 `5 white-box / 4 black-box`；把成本拆成 `P_logprob=5 WB(thinking OFF)`、`P_predict=9 default`、`P_extract=9 reserve` |
| `docs/DECISION_20260413_mvp_direction.md` | 术语 / 范围 / 定量方法 / 事实过时 | 仍以 `detector`、`12-factor shortlist`、`spine/secondary/auxiliary`、`6-model reference`、`N=3,200 gross` 为当前状态；`Disclosure Regime` 仍是 placeholder；`Tradability Tier` 仍按 auxiliary / alpha-bridge 叙事；缺 `Temporal Anchor Recoverability`；未写 frozen 的 `20-coefficient family + Westfall-Young max-T` | 保留为历史决策日志，但前置"measurement scope superseded"警示；新增 frozen 摘要：`E_CMMD/E_PCSG/E_CTS/E_FO/E_NoOp × 4 factors`、`FO/NoOp 质量门`、`E_TDR` 仅为交互项、`E_EAD_t` exploratory、`D9/D10 dropped`、`P_schema continuation reserve / cloze+QA defer`、`9-model fleet`、`2,560 target`、`English conditional stretch goal`；把 `Tradability Tier` 改写成 Bloc 2 ordinal stratifier，不再驱动 confirmatory 叙事 |
| `docs/FACTOR_LITERATURE_PROVENANCE.md` | 术语 / 范围 | 仍审计 `v5.3 15+2 factors`，使用旧因子名和旧 hierarchy；无 four-layer；未把当前 factor 状态区分为 confirmatory core / Bloc 3 / reserve / dropped | 作为文献溯源保留，但加"pre-freeze factor audit"标记；新增旧名→当前 L1 factor mapping；补 `Temporal Anchor Recoverability`；明确 `Tradability Tier` 当前是 Bloc 2 ordinal，`Disclosure Regime/Modality` 属 Bloc 3 覆盖，不是 confirmatory core |
| `docs/LITERATURE_SWEEP_2026_04.md` | 事实过时 / 术语 | 执行摘要仍给出 `keep v5.2 6-model fleet unchanged`；使用 `detector`、`12/15-factor`、`3-bloc` 语言；会被误读为当前方法定稿 | 顶部加 superseded 注；把所有当前式结论改成"historical R4 literature finding"；在摘要里明确：fleet 结论已被 `R5A Fleet Review R2` 替换，方法框架已改为 four-layer，最终 scope 以 freeze 为准 |
| `docs/MEDIA_COVERAGE_FEASIBILITY.md` | 术语 / 范围 | 仍嵌在旧 extra-corpus / Tradability 讨论里；没有说明该因子未进入 frozen shortlist；无 four-layer 用语 | 保留为候选 factor 可行性 memo；顶部注明"not in frozen shortlist; no effect on confirmatory alpha family"；把比较对象改写成 `L1 factor feasibility`，避免把 `Tradability Tier` 说成当前唯一 extra-corpus 支柱 |
| `refine-logs/reviews/R5A_STEP2/R5A_STEP2_SYNTHESIS.md` | 术语 / confirmatory family | 仍按 `D1-D12 detector slots` 组织；`D7/EAD`、`D6 NoOp` 的 alpha 计数是 pre-freeze 版本；`D11` 仍带 standalone 痕迹；`P_schema` 尚未写成已裁决状态 | 不必重写正文，但必须前置 superseded banner；加一页 crosswalk 指向 `MEASUREMENT_FRAMEWORK §6` 和 `R5A_FROZEN_SHORTLIST`；明确最终 confirmatory family 仅是 `E_CMMD/E_PCSG/E_CTS/E_FO/E_NoOp`，`EAD` 不花 confirmatory alpha，`E_TDR` 非 standalone，`P_schema` 仅 continuation reserve |
| `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` | 术语 / 实施细节 | Fleet 组成基本正确，但仍用 `detector` 语言；表中 `thinking varies` 容易与 frozen operator policy 冲突 | 轻量更新即可：顶部注明"fleet authority feeding freeze"；补一句 `P_logprob` 5 白盒统一 `thinking OFF`，`P_predict/P_extract` 走 9 模型默认模式；其余 9-model pairing 基本可保留 |
| `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md` | 术语 / 范围 | 文献综述本身有效，但对本项目仍多用 `detector`；个别 `6-model` 叙述若脱离上下文会被误读成项目选择 | 保留外部文献摘要；在开头加 frozen project box：9-model fleet、5 WB / 4 BB、operator split；把项目相关段落改成 `operator/estimand` 语言 |
| `refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md` | 术语 / 范围 / 事实过时 | 仍写 `D4/D11` 和 `6-model fleet`；未反映最终 `E_TDR`=混合模型交互项、`E_ADG` reserve trigger、`E_ADG_conflict` diagnostic only | 前置 banner；加 mapping：`D4b→E_ADG`、`D4a→E_ADG_conflict`、`D11→E_TDR interaction`；把 fleet/validation 改成 frozen split：`P_predict` 9 模型，`P_logprob` 5 白盒并行验证 |
| `PAPER_INDEX.md` | 事实过时 / 操作可用性 | `2026-04-06` 后未更新；遗漏 R4/R5A 大量论文；分类仍按旧项目结构；有重复项 | 重新索引并去重；新增 `temporal cutoff`、`construct validity`、`fleet methodology`、`memorization/extraction` 标签；优先补齐 freeze/step2/fleet review 直接引用的论文 |
| `config/prompts/README.md` | 范围 / 术语桥接 | 仍是 `E1-E6`、`direct_prediction/decomposed_impact` 旧实验命名；未说明与当前 `P_predict`/`P_extract` 的关系，易被误当成 benchmark spec | 顶部明确"implementation-level prompt schema, not measurement authority"；补一个旧任务→当前 operator 的映射；把 `E1-E6` 放入 `legacy` 小节，不再与 R5A `E_*` estimands 同层 |

### 可归档的文档
| 文档 | 理由 |
|---|---|
| `docs/BENCHMARK_PROPOSAL.md` | Phase 5 pivot 历史稿；核心范围已被推翻：cross-lingual core、6 因子、`3 tasks × 4 conditions`、英文主线都不再是当前 spec |
| `refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md` | R4 Step 1 brainstorm 汇总；仅有 lineage 价值，当前 factor framework 已被 four-layer + freeze 完全替代 |
| `refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md` | 明确把 `v5.2` 当权威闭环；当前会误导读者回到 pre-freeze factor governance |
| `refine-logs/reviews/BENCHMARK_R4_CHALLENGER.md` | 挑战点多数已吸收进 freeze；仍用旧 hierarchy 和 pre-four-layer 语言，适合作为历史审稿记录归档 |
| `refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md` | 只服务于 `v5.2` 闭环 QA；其"剩余问题"大多已被 R5A freeze 重新定义或关闭 |
| `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md` | 作为 handoff packet 已过期；它仍把 `v6.2` 当当前 authority，并把 fleet/terminology 带回 pre-freeze 状态 |
| `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md` | 被 `FLEET_REVIEW_R2_SYNTHESIS.md` 和 frozen 9-model fleet 实质取代；还保留全 fleet thinking-OFF 这类与 frozen operator split 冲突的中间结论 |
| `refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md` | 明确是 opening defaults；pool/slot/6-model 假设都已被 Step 2 + freeze 覆盖 |
| `refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md` | Step 1 detector pool 历史文件；当前只适合做方法演化记录，不适合继续放在活跃规范链上 |
| `refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md` | 原始 sweep worklog；信息已汇总进 `docs/LITERATURE_SWEEP_2026_04.md`，再往前又被 freeze 吸收；继续活跃保留只会增加术语噪音 |
| `refine-logs/reviews/LIT_SWEEP_B_BROAD_SWEEP.md` | 同上 |
| `refine-logs/reviews/LIT_SWEEP_C_CHRONO_BASELINES.md` | 同上 |
| `refine-logs/reviews/LIT_SWEEP_D_CITED_BUT_UNREAD.md` | 同上 |
| `refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md` | 同上 |
| `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md` | 同上 |
| `plans/phase5-qwen-positive-control.md` | 整体计划已被 benchmark pivot 取代；唯一仍存活的是 "Qwen CPT causal anchor" 这一概念，已在 freeze 中单独保留，无需保留整份执行计划为活跃文档 |

### 无需改动的文档
- `docs/TIMELINE.md`
- `docs/THALES_SIGNAL_PROFILE_REVIEW.md`

### 跨文档矛盾

1. **权威链冲突**：`docs/TIMELINE.md` 与 frozen 文档把 `R5A_FROZEN_SHORTLIST.md` 设为权威；`docs/DECISION_20260413_mvp_direction.md` 和 `BENCHMARK_R5_KICKOFF.md` 仍被写成当前 authority。新 agent 进入项目时可能跟随错误的权威链。

2. **Fleet 冲突**：仓内同时存在 `6-model`、`7-model`、`8-model`、`9-model` 版本；只有 `FLEET_REVIEW_R2_SYNTHESIS.md` + freeze 与最终一致。其他文档的 fleet 数据会误导成本估算和 power analysis。

3. **Thinking-mode 冲突**：`FLEET_REVIEW_SYNTHESIS.md` 倾向全 confirmatory fleet `thinking OFF`；frozen policy 是 `P_logprob` 才强制 `OFF`，`P_predict` 用默认模式。如果 pilot 实施时参考了错误的 synthesis，会产生不可逆的数据质量问题。

4. **Confirmatory family 冲突**：pre-freeze 文档仍按 detector slot 或把 `EAD/D11` 当可直接占 alpha 的对象；frozen family 已锁为 `5 estimands × 4 factors = 20 coefficients`，并对 `FO/NoOp` 设质量门。多处文档暗示 `D6 NoOp` 可自动扩展 confirmatory 到 24 coefficients 而无 gate，与 freeze 的质量门机制矛盾。

5. **Factor hierarchy 冲突**：R4/R5 kickoff 还是 `12-factor shortlist + spine/secondary/auxiliary + 3-bloc`；frozen state 是 four-layer terminology + 4-bloc inventory，且 `Temporal Anchor Recoverability` 已正式进入框架。

6. **Tradability / alpha-bridge 冲突**：若干旧文档仍把 `Tradability Tier` 写成 alpha-bridge 主轴或 auxiliary 特殊项；frozen state 下它只是 Bloc 2 ordinal factor，不应驱动 confirmatory family。

7. **Scope/N 冲突**：`BENCHMARK_PROPOSAL.md` 把英文扩展当核心；`DECISION...`/fleet survey 还用 `3,200`；freeze 已改为中文优先、英文 conditional，目标规模写成 `2,560 target`。

8. **Reserve/defer 冲突**：pre-freeze 文档对 `P_schema` 仍是 open/candidate；freeze 已裁决为 `Continuation=RESERVE`，`Cloze/QA=DEFER`。
