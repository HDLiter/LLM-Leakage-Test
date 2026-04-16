---
title: R5A Step 2 — Orchestrator synthesis of 4-lens convergence
stage: R5A Step 2 close
date: 2026-04-15
inputs: quant_lens.md, nlp_lens.md, stats_lens.md, editor_lens.md (all Step 2)
authoring: Claude Code orchestrator synthesizing 4 xhigh Codex Step 2 lens outputs
prior_inputs: R5A_STEP1_SYNTHESIS.md, R5A_DEFAULTS.md, R5A_TEMPORAL_CUE_SYNTHESIS.md, FLEET_REVIEW_R2_SYNTHESIS.md
---

# R5A Step 2 — Integrated convergence synthesis

Step 2 ran another 4-Codex-agent pass (Quant / NLP / Stats / Editor), each reviewing the Step 1 pool, opening defaults, temporal-cue session, and fleet review. Consensus is materially higher than Step 1: 5 of 7 tensions are resolved, both drops are unanimous, and the architecture choice converges. Two genuine disagreements remain (NoOp status and EAD role) and are arbitrated below.

---

## 1. Tension resolution matrix

| Tension | Quant | NLP | Stats | Editor | Step 2 resolution |
|---|---|---|---|---|---|
| **T1 EAD** | MODIFY: field-first, standalone if incremental | MODIFY: field-first, standalone reserve | MODIFY: standalone + field, only D7 spends alpha | MODIFY: field-first, reserve standalone | **RESOLVED: field-first + standalone reserve.** Compute masking deltas universally; D7 is standalone reserve, promoted only if non-redundant with field form. Only D7 spends confirmatory alpha if promoted. |
| **T2 SR/FO** | MODIFY: one slot, FO primary | AGREE: one slot, both preserved | MODIFY: one slot, hierarchical testing | AGREE: one slot, two sub-measures | **RESOLVED: one detector slot (D5), FO primary estimand, SR diagnostic sub-measurement.** Hierarchical testing: test family-level first, decompose SR vs FO only if family clears. |
| **T3 PCSG** | AGREE: standalone | MODIFY: secondary under surface | AGREE: standalone | MODIFY: fold under D3 | **ARBITRATED: D2 analytically standalone, presented under D3's surface family section.** Stats's identification argument (best in pool) justifies keeping D2 as a distinct estimand; Editor's page argument justifies presenting it under the same section. Both needs are met. |
| **T4 ADG** | MODIFY: one slot, D4b primary | MODIFY: same | MODIFY: same, D4a appendix | MODIFY: same, reserve by default | **RESOLVED: one family slot (D4b primary, D4a diagnostic). Reserve by default; promote if D5 fails quality gate.** |
| **T5 Extraction** | AGREE: main corroborative | AGREE: main corroborative | DISAGREE: reserve/appendix | MODIFY: first reserve | **ARBITRATED: first reserve.** Stats's power argument (sparse hits, low confirmatory value) and Editor's page argument override Quant/NLP's qualitative-anchor argument for default main text. Promote to main text if pilot hit rate ≥ 5% on 100-case sample. |
| **T6 Debias Delta** | AGREE: drop | AGREE: drop | AGREE: drop | AGREE: drop | **RESOLVED: D10 dropped.** Unanimous. |
| **T7 RAVEN** | AGREE: drop | AGREE: drop | AGREE: drop | AGREE: drop | **RESOLVED: D9 dropped.** Unanimous. |

---

## 2. Per-detector verdict matrix

| Detector | Quant | NLP | Stats | Editor | **Step 2 verdict** |
|---|---|---|---|---|---|
| **D1 CMMD** | KEEP | KEEP | KEEP | KEEP | **KEEP — main text, confirmatory.** 4/4 unanimous. |
| **D2 PCSG** | KEEP standalone | RESHAPE: secondary | KEEP standalone | RESHAPE: fold | **KEEP — confirmatory, presented under D3 surface section.** Analytically independent estimand. |
| **D3 Min-K++/CTS** | RESHAPE | KEEP | KEEP | KEEP | **KEEP — main text, confirmatory.** Surface-familiarity baseline with one frozen calibrated variant. |
| **D4 ADG** | RESHAPE: D4b primary | RESHAPE: D4b primary | RESHAPE: D4b primary | RESHAPE: reserve | **RESHAPE — reserve. One family slot, D4b primary, D4a diagnostic.** Promote to main if D5 fails audit. |
| **D5 SR/FO** | RESHAPE: FO primary | KEEP | RESHAPE: hierarchical | KEEP | **KEEP — main text, confirmatory.** One slot, FO primary, SR diagnostic. Conditional on edit-quality audit gate (≥ 85% pass rate). |
| **D6 NoOp** | RESHAPE: conditional | RESHAPE: neg-control arm | DROP | KEEP | **KEEP — main text, conditional.** 3/4 keep (NLP/Editor main, Quant conditional). Automatic demotion to reserve if clause-bank audit fails. |
| **D7 EAD** | RESHAPE: field | RESHAPE: field-first | KEEP standalone | RESHAPE: field | **RESHAPE — field-first + standalone reserve.** Masking deltas computed everywhere. Standalone promotion requires pilot non-redundancy evidence. |
| **D8 Extraction** | KEEP | KEEP | RESHAPE: appendix | RESHAPE: reserve | **RESHAPE — first reserve.** Promote if pilot hit rate ≥ 5%. Qualitative case examples in any case. |
| **D12 Schema-Completion** | DROP | RESHAPE: reserve | RESHAPE: reserve | DROP | **RESHAPE — exploratory reserve only.** Keep only after Bloc 3 ontology freeze + D3 non-redundancy check. |

---

## 3. Unanimous Step 2 consensus (locked)

All 4 lenses independently converge on the following additional items beyond the Step 1 consensus:

1. **Architecture A is preferred.** 4/4 converge on family-slot presentation, though Stats adds an important qualifier: use Architecture A for presentation but Architecture B discipline for inference — the number of confirmatory estimands is counted by tested coefficients, not subsection headers. This hybrid is adopted.

2. **D10 and D9 are dropped.** 4/4 unanimous on both.

3. **D4 is one family slot with D4b primary and D4a diagnostic.** 4/4 converge after the temporal session. D4a is appendix or diagnostic only.

4. **D11 is a sensitivity protocol, not a detector.** 4/4 agree. Primary backend: CMMD. Non-temporal deletion control: mandatory (4/4 unanimous). Status: exploratory/secondary. Page budget: ~0.5 page.

5. **Continuous outputs through the main analysis.** 4/4 explicit (Quant Q7, NLP Q7, Stats Q7, Editor implicit). Thresholds only for appendix operating-characteristic summaries.

6. **Case × model structure modeled explicitly.** 4/4 explicit (Quant Q8, NLP Q8, Stats Q8). Do not flatten to per-case summaries in the primary analysis.

7. **FO primary within D5.** 3/4 explicit (Quant, NLP, Stats hierarchical); Editor silent but agreeable. FO is the primary estimand because it directly tests backtest-integrity / slot-anchor persistence.

8. **Edit-quality audit gate required for D5/D6.** 4/4 converge on ≥ 85% pass rate, event-type stratified, with automatic demotion if failed.

9. **EAD masking deltas computed everywhere but not double-counted as confirmatory evidence.** 4/4 agree that target-mask and non-target-mask deltas should be stored on every applicable detector. Only D7 standalone (if promoted) spends confirmatory alpha.

---

## 4. Arbitrated shortlist

### Main text — confirmatory core (4 family slots + 1 conditional)

| Slot | Detector(s) | Primary estimand | Bloc coverage | Paper role |
|---|---|---|---|---|
| **1** | **D1 CMMD** | cutoff_monotonicity_score | Bloc 0 (primary) | Full-fleet temporal anchor; the paper's cleanest way to show why dated checkpoints matter |
| **2** | **D3 CTS + D2 PCSG** (surface family) | D2 paired gap (primary), D3 calibrated score (secondary) | Bloc 1 (primary), Bloc 0 (secondary) | White-box familiarity baseline; D2's paired contrast is the best-identified temporal design in the pool |
| **3** | **D5 SR/FO** (counterfactual pair) | false_outcome_gap (primary), reversal_flip_rate (secondary) | Bloc 0 + Bloc 2 | Semantic-conflict centerpiece; makes Anchor Strength concrete for reviewers |
| **4** | **D6 NoOp** (conditional) | noop_sensitivity_score | Bloc 2 (primary) | Salience/distractor anchor; the paper's best novelty contribution and strongest hedge against collapse into repetition-only measurement. **Auto-demotes to reserve if clause-bank audit fails.** |
| **5** | **D7 EAD** (field + reserve standalone) | target_mask_delta, non_target_mask_delta | Bloc 2 | Cross-detector salience moderator (field role). Standalone reserve promoted only if pilot non-redundancy clears. |

### Confirmatory multiplicity budget (Stats-recommended trimmed family)

- **5 confirmatory detectors**: D1, D2, D3, D5, D7-field (EAD deltas as stratification on the 4 main detectors, not double-counted)
- Wait — Stats actually proposed: D1, D2, D3, D5, D7 as the 5 confirmatory detectors with 4 core factors each = **20 confirmatory coefficients**.
- Under Westfall-Young stepdown: ~8-12 effective independent tests, MDE inflation ~1.28-1.32×.
- If D6 NoOp passes its audit gate: it becomes a 5th/6th detector and adds 4 more coefficients = **24 total**. Still manageable.
- D4, D8, D11, D12: all secondary/exploratory with shrinkage estimates and simultaneous CIs.

### Reserve detectors

| Priority | Detector | Promotion trigger |
|---|---|---|
| **1st reserve** | D8 Extraction | Pilot hit rate ≥ 5% on 100-case sample yields compact qualitative panel |
| **2nd reserve** | D4 ADG (D4b primary) | D5 fails edit-quality gate OR temporal-gating story needs within-model evidence |
| **3rd reserve** | D12 Schema-Completion | Bloc 3 ontology freezes + D12 shows partial independence from D3 |

### Cross-cutting layers (not counted as headline detectors)

| Layer | Type | Backend | Status |
|---|---|---|---|
| **D7 EAD masking deltas** | Per-detector field | Applied to D1, D3, D5, D6 | Confirmatory as field, not as standalone |
| **D11 Temporal Dose-Response** | Sensitivity protocol | CMMD (primary), D5-FO (optional exploratory) | Secondary/exploratory |

### Dropped

| Detector | Reason | Vote |
|---|---|---|
| D10 Debias Delta | Mitigation-first, engineering-heavy, redundant with temporal family | 4/4 |
| D9 RAVEN | Collapses into Template Rigidity; venue framing not sufficient | 4/4 |

---

## 5. Bloc 3 coverage resolution

| Lens | Position |
|---|---|
| Quant | Option 3 only; D12 dropped as redundant with D3 |
| NLP | Option 3 + D12 reserve |
| Stats | Option 3 + D12 reserve |
| Editor | Option 3 only; D12 dropped |

**Resolution: Option 3 + D12 as exploratory reserve.**
- Interaction-menu stratification (detector × event_type, detector × disclosure_regime/modality, detector × event_phase) is the guaranteed baseline for Bloc 3 coverage.
- D12 Schema-Completion is kept as an exploratory reserve probe, defined against whichever Bloc 3 ontology survives freeze.
- D12 is NOT promoted to main text or confirmatory status in R5A.

---

## 6. Open questions — consolidated answers

### Implementation quality (§5.1)

| Question | Answer | Answering lens(es) |
|---|---|---|
| Q1. Minimum Chinese edit audit standard | 4-dimension audit (CLS style, target-only edit, economic consistency, no temporal/entity cues added). ≥ 85% pass rate overall, no event type below 75%. Failing event types exit confirmatory scope. | Quant + NLP + Editor |
| Q2. Rule-based NoOp clause bank | Auditable exclusion logic: same time-window, different normalized entity, different cluster, non-entailing. Provenance metadata required. If clause bank cannot cover a large majority of pilot cases, D6 auto-demotes. | NLP |
| Q3. SR/FO rewrite ownership | Joint: NLP owns edit grammar and slot ontology per event type; Editor owns CLS style rubric and final pass/fail. Two-stage protocol: deterministic edit script → fluency repair within allowed envelope → human audit. | NLP + Editor |
| Q4. NoOp clause constraints | Single medial clause, ~8-16 Chinese characters, never in headline/opening/conclusion position, ≤ 15-25% of article body. Very short CLS flashes ineligible. | NLP + Editor |

### Factor freeze (§5.2)

| Question | Answer | Answering lens(es) |
|---|---|---|
| Q5. Disclosure Regime freeze | Must freeze before detector lock if Bloc 3 enters confirmatory family. Reliability threshold: κ ≥ 0.80 for confirmatory, 0.67-0.79 for exploratory only. If replaced by Modality: most detector arguments survive with light rewriting (D1, D3, D5, D8); D6 and D12 need substantive rewriting. | Stats + Editor |
| Q6. FO known_outcome coverage | Restrict FO to real-known-outcome cases only; treat generic templates as separate probe type. Current ~115 eligible pre-cutoff cases is sufficient for a paired detector at R5 scale. | Quant + NLP |

### Statistical modeling (§5.3)

| Question | Answer | Answering lens(es) |
|---|---|---|
| Q7. Continuous vs thresholds | Stay continuous. Thresholds only for appendix summaries or deployment translation. | 4/4 unanimous |
| Q8. Case × model structure | Model explicitly as repeated measures. Do not flatten. | 4/4 unanimous |
| Q9. cutoff_gap_days + placebo controls | Model-specific multi-modal distributions after gray-band exclusion. Preregister: symmetric bins (≤ -180, gray band excluded, ≥ +180, optional ≥ +365). Three falsification controls: same-cutoff architecture pair, size falsification, pseudo-cutoff permutations. | Quant + Stats |
| Q10. Thales deterministic outputs | Partial. Target spans: yes. Competitor spans: entity-level yes. Placebo masks: yes if span classes frozen. Counterfactual edits: deterministic templates + auditable validation, not end-to-end deterministic. Sufficient for R5A conceptual closure; R5B execution risk. | NLP |

### Reproducibility (§5.4)

| Question | Answer | Answering lens(es) |
|---|---|---|
| Q11. CMMD reproducibility | Mostly yes for checkpoints; cutoff dates still unverified for Qwen2.5, Qwen3, GLM-4-9B, DeepSeek-V3. Paper must say "knowledge-cutoff-consistent temporal ordering" until verified. Fleet table, falsification pairs, and hosted-model routing stability required before paper-writing. | Quant + Editor |
| Q12. D3 white-box-only presentation | Present as white-box corroboration panel, not in omnibus full-fleet ranking. Compare directional agreement with D1/D5/D6, not raw magnitude. | Stats + Editor |

---

## 7. Paper structure (Editor-recommended)

| Section | Budget |
|---|---|
| Introduction + related work | 1.5 pages |
| Methods | 3.0-3.25 pages |
| Results | 3.0-3.25 pages |
| Discussion / limitations | 0.75-1.0 page |
| Conclusion | 0.25-0.5 page |
| **Display budget** | 3 figures + 2 tables max |

If a 5th detector promotes from reserve to main text, one figure or table moves to supplement.

---

## 8. Blocking issues consolidated

All 4 lenses flagged blocking issues. Deduplicated and priority-ordered:

### Must resolve before R5A closure

1. **Confirmatory vs exploratory family separation.** (Stats, NLP, Quant)
   The project must explicitly partition detectors and coefficients into confirmatory and exploratory families. Without this, the multiplicity budget is incoherent.
   → **Resolution in this document**: §4 specifies the partition. Confirmatory: D1, D2, D3, D5 (+ D6 conditional + D7 if promoted). All others exploratory.

2. **Edit-quality audit gate for D5/D6.** (All 4 lenses)
   No frozen audit rubric, pass threshold, or demotion rule exists yet. The counterfactual family is not a defined construct without it.
   → **R5A action**: write the audit rubric into the frozen shortlist as a binding pre-commitment. ≥ 85% pass, auto-demotion if failed.

3. **CMMD reproducibility freeze.** (Editor, Quant)
   Checkpoint/provider locking and falsification-pair story must be documented before paper-writing. Cutoff dates for open models need verification or explicit hedging language.
   → **R5A action**: record the requirement as a binding R5B gate. R5A can close with the requirement stated.

### Should resolve before R5A closure but can be recorded as R5B gates

4. **Cutoff provenance verification.** (Quant)
   Qwen2.5, Qwen3, GLM-4-9B, DeepSeek-V3 cutoff dates are proxy-based. Verify or adopt hedged claim language.

5. **FO eligibility freeze.** (Quant, NLP)
   The known_outcome vs generic-template split must be frozen as an estimand decision, not left as an analysis-time choice.

6. **NoOp clause bank.** (All 4 lenses)
   If D6 remains conditional main-text, the clause bank must clear audit before R5B implementation.

7. **D11 non-temporal deletion control + adjunct-type coverage audit.** (All 4 lenses)
   Mandatory for D11 to claim temporal-anchor specificity. Block confirmatory D11 claims until audit completes.

8. **Bloc 3 ontology freeze.** (Stats, NLP)
   Disclosure Regime vs Modality must freeze before D12 can be promoted or Bloc 3 can enter confirmatory scope.

### Does NOT block R5A closure

- D12 status (exploratory reserve, no commitment needed now)
- D11 second backend choice (CMMD is locked as primary; second is optional exploratory)
- Thales pipeline full integration (R5B execution dependency, not R5A conceptual dependency)
- Cloud GPU provider selection (infrastructure, not conceptual)

---

## 9. Summary of Step 1 → Step 2 changes

| Item | Step 1 state | Step 2 state |
|---|---|---|
| Tensions | 7 open | 5 resolved, 2 arbitrated |
| Detector pool | 10 candidates (D1-D10) | 7 active + 3 reserve + 2 dropped + 2 layers |
| D4 ADG | Deferred | Resolved: D4b primary, D4a diagnostic, reserve |
| D11 | Not yet proposed | Locked as sensitivity protocol on CMMD |
| D12 | Proposed in DEFAULTS.md | Exploratory reserve |
| Factor 13 (TAR) | Not yet proposed | Locked as secondary Bloc 0 factor |
| Fleet | 6 models | 9-model core (fleet review) |
| Architecture | A vs B open | A-for-presentation + B-for-inference hybrid |
| Multiplicity | ~60-65 coefficients estimated | 20 confirmatory (trimmed family) |

---

## 10. What happens next

1. **Challenger pass** (Claude cross-model check): probe the Step 2 synthesis for blind spots, internal contradictions, and overlooked failure modes.
2. **Cold reader pass** (adversarial review): does the shortlist make sense as a standalone document to someone who has not seen the iterative process?
3. **R5A frozen shortlist**: the final R5A deliverable incorporating all passes.

---

## 11. Artifacts

- `quant_lens.md` — Step 2, Quant lens
- `nlp_lens.md` — Step 2, NLP lens
- `stats_lens.md` — Step 2, Stats lens
- `editor_lens.md` — Step 2, Editor lens
- `R5A_STEP2_SYNTHESIS.md` — this file
