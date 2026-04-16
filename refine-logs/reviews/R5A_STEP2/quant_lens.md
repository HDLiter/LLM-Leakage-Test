---
role: Quant / alpha-bridge
lens: R5A Step 2 detector-pool review
generated: 2026-04-15
inputs:
  - refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md
  - refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md
  - refine-logs/reviews/R5A_STEP1/quant_lens.md
  - refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md
  - refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md
---

# R5A Step 2 - Quant lens review

### 1. Tension Rulings (T1-T7)

**T1. EAD standalone vs field - MODIFY.**  
The defaults are directionally right at measurement time, but too generous at paper time. I want `target_mask_delta` and `non_target_mask_delta` computed everywhere as P5 fields, because that is the cleanest deployment-side "name-prior haircut." I only want D7 promoted to a standalone detector if it adds material incremental signal after conditioning on masked versions of D1/D3/D5/D8; otherwise it is a field, not a slot.

**T2. SR/FO paired vs separate - MODIFY.**  
One detector slot is right, but the two sub-measurements are not co-equal from a Quant lens. FO should be the primary estimand because it asks the backtest-integrity question directly: does the model keep the same tradable view after the visible outcome is falsified? SR is still useful, but it is more exposed to polarity-heuristic and rewrite-quality artifacts, so I would keep it as a diagnostic sub-measurement rather than a peer headline detector.

**T3. PCSG standalone vs fold - AGREE.**  
Keep D2 standalone. The paired late-minus-early contrast is exactly the kind of identification gain the pool needs: it differences out case difficulty and reuses D3 traces at near-zero marginal cost. With the fleet review's same-tokenizer temporal pairs and size-falsification controls, D2 has a cleaner alpha-contamination interpretation than absolute Min-K scores.

**T4. ADG - MODIFY.**  
The original deferral was correct. After the temporal-cue session, I support one D4 family slot with D4b misdirection as the primary measure and D4a contradiction as a matched-date diagnostic only. D4 belongs in the pool because it is the only within-model temporal gate test, but it should stay secondary/exploratory until the adjunct-coverage audit and subset pilot are done.

**T5. Extraction main vs reserve - AGREE.**  
I agree with keeping D8 in main text only in the narrow role the defaults assign it: corroborative hard-edge evidence, not an omnibus statistical detector. From a Quant lens, exact or near-exact reuse is the clearest way to keep the alpha story honest when broader detectors fire.

**T6. Debias Delta - AGREE.**  
Drop it from the main pool. It is mitigation-first, engineering-heavy, and does not currently clear the redundancy bar over D1/D2/D4. It belongs later as an R5B deployment layer if the main shortlist establishes contamination first.

**T7. RAVEN - AGREE.**  
Drop it. I do not see a distinct alpha-bridge construct here that survives separation from Template Rigidity and the existing surface/extraction family. It is venue framing, not necessary identification.

### 2. Per-Detector Verdicts

| Detector | Verdict | Quant position |
|---|---|---|
| **D1 CMMD** | **KEEP** | The defaults' success condition is the right one: monotone cutoff-linked disagreement on exposed cases and no such monotone pattern on placebo cases. The dominant failure mode is capability/vendor noise, so same-cutoff falsification pairs and checkpoint pinning are mandatory, not optional. |
| **D2 PCSG** | **KEEP** | Keep as a primary white-box detector. Its success condition already targets the right estimand - larger leakage-vs-placebo paired gaps that are stable across model pairs - and its dominant failure mode, baseline miscalibration, is testable with the Qwen temporal pairs plus the size-falsification control. |
| **D3 Min-K++ / CTS** | **RESHAPE** | Keep only as a continuous white-box surface-familiarity baseline with calibration and explicit partialing against Template Rigidity. If the defaults' success condition fails and D3 remains highly correlated with boilerplate reuse, then it is not a memorization detector; it is a repetition detector. |
| **D4 ADG** | **RESHAPE** | R5A defaults held D4 out pending the temporal session. My Step 2 position is one reshaped family slot: D4b primary, D4a diagnostic, subset-first. The main failure mode is prompt-hierarchy or instruction-following confound, which is why D4a cannot be a co-equal headline result. |
| **D5 SR/FO** | **RESHAPE** | Keep one counterfactual slot, but FO primary and SR diagnostic. The defaults correctly center success on human-audited edit quality; the failure mode is Chinese rewrite artifact. That means no mixed generic-template fallback inside the confirmatory estimand. |
| **D6 NoOp** | **RESHAPE** | Keep only if the defaults' rule-based clause-bank coverage and irrelevance gate actually clears. Otherwise the dominant failure mode - entailment leak or CLS-style break - overwhelms any contamination interpretation, and D6 becomes reserve-only robustness evidence. |
| **D7 EAD** | **RESHAPE** | Keep `target_mask_delta` and `non_target_mask_delta` universally, but promote standalone D7 only if it adds information beyond masked parent-detector outputs. The defaults identify the right success condition - separable salience and distraction channels - and the right failure mode: generic information loss masquerading as identity-memory. |
| **D8 Extraction** | **KEEP** | Keep in the narrow corroborative role already specified in the defaults. Its success condition is modest but realistic, and its dominant failure mode - paraphrase or refusal - lowers recall rather than fabricating false contamination. |
| **D12 Schema-Completion** | **DROP** | The defaults' failure mode is decisive: if schema completion mostly tracks disclosure boilerplate, D12 duplicates D3 and Template Rigidity. From a Quant lens that is surface familiarity in institutional clothing, not new identification. |

### 3. D11 Temporal Dose-Response

**Verdict: RESHAPE.** Keep D11 only as a temporal sensitivity protocol, not a standalone detector. The primary backend should be **D1 CMMD**, because that gives the cleanest `text-side cue attenuation x model-side cutoff exposure` interaction. The optional second backend should be **D5-FO**, not D3, because FO asks the more operational question: does weakening temporal anchors reduce the model's tendency to ignore the visible outcome? The length-matched non-temporal deletion control is mandatory. Without it, D11 is just an information-loss assay. Confirmatory scope should stay to one backend; a second backend is exploratory only.

### 4. Bloc 3 Coverage

**Choice: Option 3 (interaction-menu only).**  
From a Quant perspective, Bloc 3 is primarily a moderator of contamination risk, not a detector construct that needs its own slot. Institutional source and disclosure regime should already express themselves through `detector x event_type`, `detector x disclosure_regime`, and `detector x event_phase` cells. Adding D12 would most likely create a second surface detector that rewards boilerplate completion and muddies the backtest story. If Bloc 3 effects remain weak after interaction modeling, I would accept that gap rather than pay for a redundant schema detector.

### 5. Pool Architecture

**Choice: Architecture A, with one predeclared primary score per family slot.**  
This is the best fit for the Quant/deployment bridge. The paper can carry 4-5 family slots without becoming a detector zoo, while still preserving the sub-measurements that matter operationally:

- `D1` cross-model temporal disagreement, with `D11` as a sensitivity protocol on top.
- `D2/D3` white-box familiarity, with `D2` the primary estimand and `D3` the calibrated level check.
- `D4` within-model temporal gating, with `D4b` primary and `D4a` diagnostic.
- `D5` counterfactual faithfulness, with `FO` primary and `SR` secondary.
- `D8` extraction as the hard-edge anchor.

That structure also maps cleanly to downstream veto/haircut logic: temporal exposure, white-box familiarity, counterfactual non-faithfulness, and verbatim recall are distinct deployment risks.

### 6. Open Questions

**Q1. Minimum Chinese counterfactual-edit audit standard.**  
The minimum acceptable standard is deterministic-or-template-bounded editing plus human audit on four dimensions: natural Chinese CLS style, target-local edit only, economic consistency outside the edited slot, and no extra temporal/entity cues added by the rewrite. I want `>= 85%` pass rate overall and no event type below `75%`. Any failing event type should leave confirmatory scope.

**Q6. Do we have enough `known_outcome` coverage for FO?**  
Yes for an eligibility-restricted detector, no for a pooled generic-template detector. Repo-local audit evidence shows `115` pre-cutoff cases with real `known_outcome` versus `217` pre-cutoff cases on the generic-template path, so the current pooled pre arm is modality-confounded. The fix is to freeze the FO estimand to real-known-outcome cases only, persist `cpt_mode`, and treat generic templates as a separate probe type. If the full benchmark stays near the same eligible share as `115 / 606`, that is still several hundred cases at R5 scale - enough for a paired detector.

**Q7. Continuous outputs or thresholds?**  
Stay continuous. Thresholds belong only in deployment translation or qualitative exemplar selection. Continuous scores preserve dose-response, pair gaps, and detector x factor interactions.

**Q8. Case x model repeated measures or flattened summaries?**  
Model the repeated-measures structure explicitly. For D1/D4/D11, use case-level repeated measures or precomputed within-case slopes/gaps; for D2, use within-case late-minus-early contrasts. Flattening to a single per-case average before estimation destroys the cutoff-exposure identification.

**Q9. Expected `cutoff_gap_days` distribution and placebo pseudo-cutoffs.**  
After symmetric gray-band exclusion, I expect model-specific and multi-modal realized distributions: early-cutoff models should carry heavier negative/post-cutoff mass, later-cutoff models heavier positive/exposed mass, and the near-zero region should be intentionally empty. I would preregister symmetric bins such as `<= -180`, `[-179, +179]` excluded, and `>= +180`, with an optional `>= +365` strong-exposure bin if sample supports it. Yes, preregister placebo pseudo-cutoff controls: at minimum one shifted sham cutoff per model with the same exclusion band, plus the same-cutoff architecture placebo pair `GLM-4-9B-0414` vs `gpt-4.1-2025-04-14`.

**Q11. Can CMMD be frozen reproducibly before paper-writing?**  
Checkpoint-wise, mostly yes. Causal-cutoff-wise, not yet. Hosted snapshots are pin-able, but the fleet verification work still marks Qwen2.5, Qwen3, GLM-4-9B-0414, and DeepSeek-V3-0324 cutoff dates as unverified. Until that changes, CMMD is safe as a primary detector only if the paper says "knowledge-cutoff-consistent temporal ordering" rather than "verified training cutoff."

**Q12. How should D3 be presented if it only runs on the white-box subset?**  
Present `D2/D3` as white-box corroboration, not as if they cover the whole fleet. Standardize effect sizes within detector, disclose the access split explicitly, and keep full-fleet headline comparisons on D1/D4/D5/D8.

### 7. Proposed Main-Text Shortlist

**Main text (5 family slots):**

1. **D1 CMMD**
2. **D2 PCSG + D3 CTS/Min-K++ as one white-box familiarity family**, with D2 primary
3. **D4 ADG**, with D4b primary and D4a diagnostic
4. **D5 SR/FO**, with FO primary and SR diagnostic
5. **D8 Extraction**

**Reserve:**

1. **D7 EAD**
2. **D6 NoOp**

**Rationale.**  
This slate gives the paper two temporal-identification routes (`D1`, `D4`), one strong paired white-box detector (`D2`), one behaviorally direct counterfactual detector (`D5-FO`), and one high-precision anchor (`D8`). It is diverse enough to survive reviewer attacks from both "this is just surface reuse" and "this is just prompt brittleness." `D7` is operationally valuable, but I would keep it field-first until it proves standalone incrementality. `D6` has the weakest current implementation admissibility. If the paper must compress to `4`, `D8` is the first main-text detector I would move to reserve.

### 8. Blocking Issues

1. **Temporal detectors still depend on unverified cutoff provenance for core open models.** If Qwen2.5, Qwen3, GLM-4-9B-0414, and DeepSeek-V3-0324 remain on proxy dates, the project must either verify them or explicitly narrow the claim language before R5A closes.
2. **D5 cannot close cleanly until FO eligibility and probe modality are frozen.** The current `known_outcome` vs generic-template split is a real estimand confound, not a cosmetic analysis issue.
3. **If D6 stays above reserve, the deterministic NoOp clause bank and audit gate are blocking dependencies.** Without them, NoOp is not interpretable enough for a frozen conceptual shortlist.
4. **D11 and full-population D4 claims depend on the adjunct-type coverage audit.** This is not a blocker if they are frozen as exploratory/subset-limited, but it is a blocker if the project still intends to treat them as full-corpus confirmatory detectors.
