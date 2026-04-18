---
title: Phase 7 Pilot Plan — Lens Review Synthesis
date: 2026-04-17
stage: Phase 7 pre-kickoff review close
inputs:
  - refine-logs/reviews/PHASE7_PILOT/quant_lens.md
  - refine-logs/reviews/PHASE7_PILOT/nlp_lens.md
  - refine-logs/reviews/PHASE7_PILOT/stats_lens.md
  - refine-logs/reviews/PHASE7_PILOT/editor_lens.md
  - refine-logs/reviews/PHASE7_PILOT/ml_engineer_lens.md
verdicts:
  quant: GO-WITH-FIXES
  nlp: GO-WITH-FIXES
  stats: GO-WITH-FIXES
  editor: GO-WITH-FIXES
  ml_engineer: GO-WITH-FIXES
aggregate_verdict: GO-WITH-FIXES
---

# Phase 7 Pilot Plan — Lens Review Synthesis

## 1. Aggregate verdict
5 份 lens 一致支持 `GO-WITH-FIXES`。去重后建议形成 **8 项 P0、2 项 P1、1 项 P2、1 项 P3** action。最危险的 3 个结构性问题是：`estimand` 的分析单元/score/`n_eff` 仍未冻结，`C_FO/C_NoOp` 的 admissibility spec 还不够可审计，以及 runtime 与 prereg evidence chain 仍留有裁量缝隙。

## 2. Action list (prioritized)

### P0 — Must fix before Phase 7 kickoff
- **A01 Freeze estimand contract**
  - 来源 lens(es): [Quant blocking B-01/B-02, Quant major M-01, Stats blocking B02, Stats major M-01]
  - Plan section to edit: §6.4, §8.2, §8.3, 新增 §8.1A
  - Fix type: new subsection + edit section text
  - Concrete change: 在 §8.1 后新增 `Estimand-specific analysis units and scalar scores`，逐条冻结 `E_CMMD/E_CTS/E_PCSG/E_FO/E_NoOp` 的 analysis unit、scalar score、eligibility mask、primary coefficient，并把 §6.4 改成 `n_eff(estimand, factor_bin, analysis_unit)`。同时把 `baseline_confidence` 从 confirmatory primary model 移出，降为 `P_predict` family 的 sensitivity only。

- **A02 Formalize `BL2` and same-cutoff checks**
  - 来源 lens(es): [Stats blocking B03, Quant major M-05, Editor major]
  - Plan section to edit: §6.2, §8.6, §13 item 7
  - Fix type: edit section text + new subsection
  - Concrete change: 用预注册的 SESOI/TOST 规则替换当前 “`<25%` 或 CI overlap zero” 口径，并把 post-cutoff window 改成相对 latest approximate cutoff 有明确安全间隔的最远可行窗口。同步新增 same-cutoff early-warning ratio，并让 §13 item 7 只引用数值规则。

- **A03 Freeze Stage 2 adaptation and Gate 9**
  - 来源 lens(es): [Stats blocking B01, Stats major M05, Editor blocking, Editor major, Quant minor m-02]
  - Plan section to edit: §7.1, §7.2, §8.4, §13 item 9
  - Fix type: new subsection + edit section text
  - Concrete change: 在 §7.1 写死 `20/16/16/12` family states，并明写 `pilot cases are excluded from all Stage 2 confirmatory analyses`。把 §8.4 改成 deterministic regrouping tie-break：触发后保 `E_PCSG`、降 `E_CTS`；§7.2 限定 prompt wording 只能做 adapter hardening；§13 item 9 改成至少 `2` 个 retained estimand、覆盖 `1 temporal + 1 perturbation route` 且 `power >= 0.80` 才 automatic GO。

- **A04 Harden `C_FO/C_NoOp` admissibility**
  - 来源 lens(es): [NLP blocking B1/B2/B3, Quant blocking B-03, Editor major]
  - Plan section to edit: §5.4, §6.3, §7.1, §9.3-§9.6, §13 item 6
  - Fix type: edit section text + new subsection + new deliverable
  - Concrete change: 把“verified outcome”与“FO-slotable”拆成两个字段，并新增 `fo_slot_topology`、`slot_span`、`ineligible_reason` 等字段。把 `C_NoOp` 改成 host-aware insertion library，在 §9.3 补 6 类 cue-fail checklist，并把 frozen shortlist 的 3 条 quality gate 原样写回 §7.1/§13；若不额外做 placebo，`E_NoOp` 只能被表述为 robustness/template-brittleness signal。

- **A05 Freeze operator/runtime source of truth**
  - 来源 lens(es): [ML Engineer blocking B1/B2, NLP major M1/M3, Editor major]
  - Plan section to edit: §5.1, §5.2, §5.3, §10.1-§10.4
  - Fix type: add config field + edit section text
  - Concrete change: 在 `fleet.yaml` 增加 per-model × per-operator `thinking_control`、`prompt_overlay_policy`、`route_lock_required`，让 prose 退出 source-of-truth 角色。§5.2 需把 vLLM prompt-logprob request/response contract 写到可执行粒度；§5.3 需把 baseline `P_predict` 与 `E_ADG` overlay 完全切开。

- **A06 Replace pseudo-determinism with request-level lineage**
  - 来源 lens(es): [ML Engineer blocking B3/B4, Quant minor m-03]
  - Plan section to edit: §5.3, §5.5, §10.2-§10.4
  - Fix type: edit section text + add config field
  - Concrete change: 把 resume 改成 request-item 级状态机，显式记录 `request_id` 与 `pending/success/retryable/terminal_skipped`。把 seed 改成 `requested/supported/effective` 语义，并统一 provider fingerprint schema；duplicate rerun 必须同时覆盖 baseline 与 perturbation delta。

- **A07 Harden prereg evidence and execution governance**
  - 来源 lens(es): [Editor blocking x4, ML Engineer major, NLP blocking B3]
  - Plan section to edit: §7.1, §7.2, §9.1-§9.5, §11.1-§11.2, §14.4
  - Fix type: new subsection + new deliverable + new decision memo
  - Concrete change: 在 §7.1 新增 `Evidence package`，写明 signatories、prereg commit SHA、remote timestamp or signed tag、manifest hash 与 Phase 8 memo 的回链。§9/§11 改成现实 staffing model，默认 `2 reviewer + 1 adjudicator + 1 stats merge`；§7.2 增加 `Phase 7b reserve-promotion contingency`，避免把 reserve 执行路径偷塞进默认 critical path。

- **A08 Harden BL1 and power**
  - 来源 lens(es): [Quant major M-03/M-04, Stats major M02/M04, Editor blocking]
  - Plan section to edit: §5.6, §8.5, §8.8, §13 item 9
  - Fix type: edit section text + new deliverable
  - Concrete change: §8.5 需补 grouped-CV split unit，并新增一个低成本 text-light challenger；§8.8 改成 scenario-based power，至少输出 `20/16/12` family、conservative prior、Monte Carlo SE 与 realized missingness。禁止直接把 perturbation-rich pilot 点估计拿去做 Phase 8 planning prior。

### P1 — Must fix before pilot launch (WS4)
- **A11 Add supplementary diagnostics**
  - 来源 lens(es): [NLP major M2/M3]
  - Plan section to edit: §5.2, §5.3, §5.6, §7.1
  - Fix type: new deliverable + edit section text
  - Concrete change: 把 `explicit_memory_reference` 明写为 supplementary lower-bound signal，并补一个 precision audit 小表；同时为 `E_CTS/E_PCSG` 固定输出 digit ratio、ticker/code share、boilerplate share 与 raw vs masked sensitivity。

- **A12 Finish WS0 hygiene and missing controls**
  - 来源 lens(es): [ML Engineer major M1/M2/M3, Stats major M03, Editor major]
  - Plan section to edit: §5.1, §7.3, §10, §12, §14
  - Fix type: new deliverable + edit section text
  - Concrete change: 在 WS0 补 `pyproject.toml` 或 `environment.yml`、依赖 pinning 与 proxy hard requirement，并把 `C_temporal` 的 same-length non-temporal sham control 写回 exploratory path。同步扩 risk register，并把 decision memos 压成 decision log schema，减少主计划体量。

### P2 — Must address before Phase 8 gate
- **A21 Add gate-facing stability diagnostics**
  - 来源 lens(es): [NLP minor m1, Stats minor m02/m03, Quant minor m-03]
  - Plan section to edit: §5.6, §13
  - Fix type: new deliverable + edit section text
  - Concrete change: 在 go/no-go memo 中固定加入 shadow prompt-sensitivity、pair-aware resampling、realized missingness 与 perturbation-delta rerun stability，避免 Gate 9 只看一个 optimistic power 数字。

### P3 — Nice-to-have
- **A31 Low-cost wording cleanup**
  - 来源 lens(es): [NLP minor m2, Quant minor m-01, Stats minor m01]
  - Plan section to edit: §5.4, §8.7, §9.3
  - Fix type: edit section text
  - Concrete change: 把 `C_NoOp` 的固定字数改写成 `inserted fragment` 指南，并把 `model_capability` 明确降格为 descriptive sensitivity，不解释 `beta4`。

## 3. Cross-lens convergence map
`✓` = 该 lens 明确提出；`—` = 未明确提出。经合并后未保留需要用“多数票”覆盖的直接对立意见，真正冲突见 §4。

| Issue | Quant | NLP | Stats | Editor | ML Eng |
|---|---|---|---|---|---|
| Estimand unit/score + `n_eff` contract | ✓ | — | ✓ | — | — |
| `baseline_confidence` 退出 primary model | ✓ | — | ✓ | — | — |
| `C_FO` slotability taxonomy | — | ✓ | — | — | — |
| `C_NoOp` host-aware bank + cue rubric | ✓ | ✓ | — | ✓ | — |
| Runtime source of truth: logprob contract / thinking / prompt boundary | — | ✓ | — | ✓ | ✓ |
| Stage 2 adaptation contract + Gate 9 determinism | ✓ | — | ✓ | ✓ | — |
| `BL2` formal negative control + same-cutoff early warning | ✓ | — | ✓ | ✓ | — |
| Request-level provenance / resume / seed realism | ✓ | — | — | — | ✓ |
| Power transportability / grouped CV / stronger baseline | ✓ | — | ✓ | ✓ | — |
| Audit governance / prereg evidence / staffing | — | ✓ | — | ✓ | ✓ |
| Reserve-promotion execution path | — | — | — | ✓ | — |

## 4. Conflicts and resolutions
- **Conflict 1: `E_NoOp` 是否应新增 placebo 作为 confirmatory 前提**
  - 各 lens 立场: Quant 要求“加 placebo 或降为 exploratory”；NLP 重点是 host-aware clause bank 与 cue taxonomy；其余 lens 未要求新增一条 confirmatory gate。
  - 裁决: 不新增 confirmatory demotion rule；仅补 `C_NoOp` 生成/审计规范，并把 `E_NoOp` 的解释上限收紧为 robustness/template-brittleness signal。若用户愿意付额外工程成本，可加一个 exploratory-only placebo diagnostic。
  - 理由: `R5A_FROZEN_SHORTLIST` 已冻结 `E_NoOp` 的 3 条 gate，不能暗中改 family contract；scope freeze 优先于单 lens 的额外 gate 建议。

- **Conflict 2: reserve promotion 要不要在默认 Phase 7 里预建执行路径**
  - 各 lens 立场: Editor 要求补 owner/budget/artifact；默认计划没有对应 workstream，若硬加则形成 scope expansion。
  - 裁决: 新增 `Phase 7b reserve-promotion contingency`，触发后才开，不把 reserve operator 预构建放入默认 critical path。
  - 理由: 既保住 frozen trigger，又避免“名义保留、实际失控”或“未审 scope 扩张”。

- **Conflict 3: thinking policy 与 prompt boundary 的 source of truth**
  - 各 lens 立场: NLP 要求 baseline prompt 与 `E_ADG` overlay 彻底切开；ML Engineer 要求把 thinking policy 从 prose 挪到 config 矩阵；现 plan 与相关 schema 文档存在冲突。
  - 裁决: `fleet.yaml` 的 per-model × per-operator `thinking_control` 与 `prompt_overlay_policy` 成为唯一 source of truth。
  - 理由: 工程可执行性冲突按优先级由 ML Engineer 裁决。

- **Conflict 4: `E_CTS`/`E_PCSG` 高相关时是否保双 confirmatory、合并 composite，还是只 narrative regroup**
  - 各 lens 立场: Quant/Editor 倾向保 progressive narrative；Stats 明确要求 deterministic tie-break，反对临时发明 composite。
  - 裁决: 触发 regrouping rule 时，保 `E_PCSG` 为 confirmatory，`E_CTS` 转 corroborative。
  - 理由: type-I validity 优先于 narrative 完整性；`E_PCSG` 的 identification 更强。

## 5. Open questions requiring user decision
- **OPEN 1 — reserve promotion operating mode**
  - 冲突要点: 是现在就预建 `WS6-lite`，还是保留触发后再开 `Phase 7b`。
  - 选项: A. 预建 `WS6-lite`; B. 仅保留 `Phase 7b contingency`; C. 从本计划删除 executable path。
  - 建议选项: **B**。它最符合 frozen scope，也最不容易把默认 critical path 拉爆。

- **OPEN 2 — baseline `P_predict` template 采用哪种最小冻结形态**
  - 冲突要点: NLP 要求 zero-shot 或纯格式 few-shot；当前计划未定。
  - 选项: A. zero-shot; B. 非金融、无日期、纯格式 schema-only examples; C. 继续保留 few-shot 可调。
  - 建议选项: **A**。污染面最小，也最便于把 `E_ADG` overlay 与 baseline 切开。

- **OPEN 3 — 是否为 `C_NoOp` 额外支付 placebo diagnostic 成本**
  - 冲突要点: Quant 希望更强 identification；frozen scope 不允许把它变成新的 confirmatory gate。
  - 选项: A. 现在加 low-cost exploratory placebo; B. 不加 placebo，只收紧 claim language; C. 升级为新控制臂。
  - 建议选项: **B**；若用户明确追求更强 `E_NoOp` 机制叙事，再选 **A**。

- **OPEN 4 — 真实可用的人审配置**
  - 冲突要点: 计划默认 4 角色齐备，但现实可能只有 1-2 位人类协作者。
  - 选项: A. `2 reviewer + 1 adjudicator + 1 stats merge`; B. `1 reviewer + delayed second reviewer`; C. 先 agent dry-run、后小样本人审。
  - 建议选项: **A**；若做不到，选 **B**，并显式降低 IAA 解释强度。

## 6. Suggested plan revision workflow
建议 Claude Code 按下面顺序改 plan，先锁 inference contract，再补 operator spec，最后清理文档结构：

1. 先改 §8.2-§8.8 与 §6.4：冻结 estimand unit/score、移除 `baseline_confidence` primary role、重写 `BL2` 与 power。
2. 再改 §7.1-§7.3 与 §13：补 family-state table、Gate 9 硬规则、evidence package。
3. 再改 §5.2、§5.3、§10：冻结 logprob contract、thinking matrix、prompt overlay policy、request-level lineage。
4. 再改 §5.4、§6.3、§9：补 `fo_slot_topology`、host-aware `C_NoOp`、cue rubric、audit staffing。
5. 最后改 §12、§14：补缺失风险、decision log、runbook appendix。

## 7. Stage-1 prereg skeleton 的合成建议
- signatories、prereg commit SHA、remote timestamp or signed tag、pilot manifest hash、audit manifest hash。
- 允许的 Stage 2 family states：`20/16/16/12`，以及 `CTS→corroborative` regrouping tie-break。
- 明写 `pilot cases are excluded from all Stage 2 confirmatory analyses`。
- 每个 retained estimand 的 analysis unit、scalar score、eligibility mask、primary coefficient、`n_eff` 定义。
- per-model × per-operator `thinking_control`、`prompt_overlay_policy`、route lock policy。
- baseline `P_predict` 模板版本；`E_ADG` overlay 与 baseline semantic layer 的边界。
- `C_FO` slot-topology taxonomy；`C_NoOp` insertion classes；四维 rubric 与 cue-fail checklist。
- `E_FO/E_NoOp` 的完整 3 条 quality gate：audit pass、eligible coverage、baseline delta non-degeneracy。
- request-level `request_id` schema、fingerprint fields、seed semantics、cache-bypass duplicate policy。
- `BL1` grouped-CV split unit 与 baseline set；`BL2` SESOI/TOST rule；same-cutoff early-warning ratio。
- power scenario table、planning prior shrinkage rule、Monte Carlo SE 与 realized missingness reporting。
- reserve-promotion contingency、Phase 7b trigger 与 required decision memos。

## 8. Follow-up: what this synthesis does not cover
本 synthesis 只处理 plan 修订，不回答必须等 Phase 7 真跑完才知道的问题。仍需靠 pilot 实测的包括：`C_FO/C_NoOp` 的真实 pass rate 与 coverage、provider 的真实 failure rate、same-cutoff ratio、post-cutoff effect、shadow prompt attenuation，以及 conservative prior 下的主实验 power。
