---
role: Stats / power and identification
lens: R5A Step 2 detector pool review
generated: 2026-04-15
inputs:
  - refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md
  - refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md
  - refine-logs/reviews/R5A_STEP1/stats_lens.md
  - refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md
  - refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md
---

# R5A Step 2 — Stats Lens Review

Power statements below assume the current planning baseline: about `N ≈ 2,560` scorable cases, a `9-model` core fleet, `5` white-box models for logprob detectors, continuous detector outputs, stacked mixed-effects analysis with case/model structure retained, and confirmatory multiplicity controlled by **Westfall-Young stepdown max-T**. I am treating the main statistical risk as not raw sample size but **coefficient inflation from detector proliferation, detector decomposition, and Bloc 3 cell fragmentation**.

## 1. Tension Rulings (T1-T7)

| Tension | Position vs `R5A_DEFAULTS.md` | Stats ruling | Reason |
|---|---|---|---|
| **T1 EAD standalone vs field** | **MODIFY** | Keep **D7 EAD as a standalone detector**, and also store EAS-style deltas on other detectors, but **only D7 spends confirmatory alpha**. | The within-case intervention remains one of the cleanest identified designs in the pool and still deserves a detector slot. The default "both roles simultaneously" is fine at the measurement layer, but not at the inference layer: counting D7 and cross-detector EAS fields as separate confirmatory evidence would double-spend alpha on the same construct. |
| **T2 SR/FO paired vs separate** | **MODIFY** | Keep **one detector slot** with **SR and FO preserved separately**, but use **one family-level confirmatory test** and decompose only if that clears. | NLP is right that SR and FO are not the same mechanism; Editor is right that two headline detectors would bloat the slate; my Step 1 merge was too aggressive for construct validity. The power-optimal compromise is one slot, two sub-measures, hierarchical testing. |
| **T3 PCSG standalone vs fold** | **AGREE** | Keep **D2 PCSG standalone**. | This remains the best identification-to-cost trade in the pool. Fleet Round 2 strengthened it materially by adding same-tokenizer temporal pairs and same-cutoff falsification controls. Folding it into D3 would throw away the paired-contrast advantage. |
| **T4 ADG after temporal session** | **MODIFY** | Adopt **D4a/D4b as one family slot**, with **D4b primary** and **D4a diagnostic/appendix**. Do not count both confirmatorily. | The temporal session resolved the design question correctly. D4b is the better identified estimand; D4a is instruction-following contaminated. The important stats move is to prevent the split from becoming two new confirmatory detectors. |
| **T5 Extraction main vs reserve** | **DISAGREE** | Move **D8** to **reserve / appendix corroboration** by default. | The qualitative specificity is real, but the power problem did not go away. Sparse-hit detectors are exactly where multiplicity hurts most. Extraction can still appear in the paper as hard-edge evidence, but it should not occupy confirmatory budget unless pilot hit rates are unexpectedly healthy. |
| **T6 Debias Delta** | **AGREE** | Drop **D10**. | It is statistically redundant with stronger temporal designs already in the pool, while carrying the largest engineering burden. It is not a good use of confirmatory budget. |
| **T7 RAVEN** | **AGREE** | Drop **D9**. | The construct overlap problem remains decisive. Once D3, D5, and D8 are present, RAVEN does not buy enough unique identification to justify another family. |

## 2. Per-Detector Verdicts

Identification rank is relative to the current pool on causal cleanliness, not raw specificity alone.

| Detector | Verdict | Approx. power after correction | Identification rank | Multiplicity cost | Stats position |
|---|---|---|---|---|---|
| **D1 CMMD** | **KEEP** | Solid on full fleet; corrected `d ≈ 0.23-0.28` for main effects | **#5** | **Medium** | Core detector. Same-cutoff falsification pairs and cutoff-label shuffles now make the identification story materially stronger than in Step 1. |
| **D2 PCSG** | **KEEP** | Best-in-pool for a temporal detector; corrected `d ≈ 0.19-0.23` | **#1** | **Low** | Remains my top pick. Paired contrast removes a large share of case difficulty variance, and fleet redesign improved the falsification story rather than weakening it. |
| **D3 Min-K++ / CTS** | **KEEP** | Good on the 5-model white-box subfleet; corrected `d ≈ 0.23-0.28` | **#6** | **Medium** | Keep as the cheap surface baseline, but freeze one calibrated variant. The danger is not power; it is construct collapse into Template Rigidity. |
| **D4 ADG** | **RESHAPE** | `D4b`: likely `d ≈ 0.20-0.25` on a stratified subset; `D4a` weaker | **D4b #3 / D4a #8** | **Medium if one score, High if both** | Keep only as one family slot. D4b is the real detector; D4a is diagnostic. Start on a subset and do not let the split double the confirmatory family. |
| **D5 SR/FO** | **RESHAPE** | Medium; corrected `d ≈ 0.30-0.36` unless edit quality is excellent | **#4** | **Medium-High** | Worth keeping, but only with one family-level alpha spend and an explicit perturbation audit gate. If edit quality drifts, power estimates become meaningless. |
| **D6 NoOp** | **DROP** | Weak; corrected `d ≈ 0.32-0.40` even before quality stratification | **#9** | **High** | This should not remain in the shortlist absent a deterministic clause bank with audited irrelevance. It is the easiest detector in the pool to turn into generic prompt-fragility. |
| **D7 EAD** | **KEEP** | Strong paired-difference power; corrected `d ≈ 0.20-0.24` | **#2** | **Medium** | Top-tier detector. The only caveat is accounting: D7 is one confirmatory detector, not an excuse to count the same masking construct again inside other detectors. |
| **D8 Extraction** | **RESHAPE** | Low unless hit rates are unexpectedly high; roughly `4-6 pp` detectable risk difference only when baseline hit rate is already non-trivial | **#7 on broad inference, high on specificity** | **Low if reserve, High if confirmatory across strata** | Keep as reserve/appendix corroboration. Use for exemplars and exact-match evidence, not as a workhorse confirmatory detector. |
| **D12 Schema-Completion** | **RESHAPE** | Potentially usable at coarse schema bins; corrected `d ≈ 0.25-0.30` if collapsed to `2-4` predeclared contrasts | **#6/#7 provisional** | **Medium-High** | I support it as the best current answer to the Bloc 3 gap, but only if Disclosure Regime/Modality freezes and D12 shows partial non-redundancy with D3. Until then it is reserve, not core. |

## 3. D11 Temporal Dose-Response

**Position:** keep **D11** only in its reshaped temporal-sensitivity form, **not** as a standalone detector.

- **Confirmatory vs exploratory:** exploratory / secondary. I agree with the temporal session that D11 should be a protocol layered onto an existing detector, not another detector family. The cleanest primary backend is **CMMD only**. A second backend can be appendix-only.
- **Power for the dose-response slope:** acceptable only for the main linear trend on the adjunct-type subset. With roughly `1,600-2,100` eligible cases, `2-3` dose levels, and a within-case design, the main standardized slope is plausibly detectable around `d ≈ 0.10-0.15`. That is enough for one backend and one slope. It is **not** enough for many subgroup interactions or multi-backend confirmatory claims.
- **Multiplicity cost if promoted to confirmatory:** too expensive for what it buys. In the broad detector-by-factor accounting, adding D11 as a full confirmatory detector would effectively add another detector family and move the family back toward the `~60 → ~70+` coefficient regime immediately; if D11 is allowed to run on two backends, the cost is worse. In a trimmed family, one slope on one backend is only a few extra coefficients, but the real issue is that D11 runs on a smaller eligible subset, so its own corrected MDE is still worse than D1/D2/D7.
- **Hard requirement:** the **length-matched non-temporal deletion control** is mandatory. Without that control, I would not interpret a D11 slope as temporal-anchor sensitivity at all.

## 4. Bloc 3 Coverage

**Choice:** **Option 3 + D12**.

My reason is statistical, not narrative. **Option 3 alone is too weak** if Bloc 3 is supposed to support anything stronger than a descriptive aside. Bloc 3 is exactly where cell fragmentation and dependence kill power:

- With `N ≈ 2,560`, any Bloc 3 level with `20-25%` prevalence gives only `~500-650` cases before clustering and correction. That is still workable for coarse main effects, but corrected MDEs are already around `d ≈ 0.28-0.34`.
- Once a Bloc 3 level falls into the `10%` range, effective cell counts are closer to `~250`, and corrected MDEs jump to roughly `d > 0.40`.
- If Bloc 3 is carried only through detector-by-factor interactions, the coefficients proliferate quickly and most interesting cells will be underpowered after Westfall-Young.

That is why I prefer **Option 3 + D12**:

- **Option 3** preserves cross-detector stratification, which we need anyway.
- **D12** gives Bloc 3 one detector whose signal is concentrated in the institutional-schema channel rather than dispersed across many thin interaction cells.

The caveat is important: **D12 should stay reserve unless Bloc 3 freezes.** If `Disclosure Regime` remains unfrozen or is replaced late by `Modality`, D12 can only be exploratory.

## 5. Pool Architecture

**Choice:** **Alternative**.

My recommendation is:

- **Architecture B for inference**: a small set of true confirmatory detectors.
- **Architecture A for presentation**: group related detectors into family sections in the paper.

I do **not** want Architecture A to become a way of hiding multiplicity inside "family slots." The alpha budget depends on the number of tested estimands, not the number of subsection headers. The clean approach is:

- Count **true detector families** for confirmatory inference.
- Allow **within-family decomposition** only through gatekeeping.
- Present the paper in family blocks so the narrative stays readable.

That hybrid is the only version that keeps both the page budget and the multiplicity budget under control.

## 6. Open Questions

### Q5. Disclosure Regime / Modality

- **Freeze requirement:** if Bloc 3 enters the confirmatory family, `Disclosure Regime` must be frozen **before detector lock**. Otherwise keep Bloc 3 exploratory.
- **Reliability threshold:** for a categorical confirmatory factor, I would want `kappa/alpha >= 0.80`. The `0.67-0.79` band is usable only for exploratory or partially pooled descriptive work. For any anchor-strength rubric used numerically, I would want `weighted kappa` or `ICC >= 0.75`, with `0.80` preferred.
- **If replaced by `Modality`:**
  - **Survives with light rewriting:** CMMD and D4b arguments that concern formal-source versus commentary-like text; D12 if reframed as **modality-schema completion** rather than disclosure-regime completion.
  - **Needs substantive rewriting:** any claim about **institutional stage**, legal disclosure authority, or source-regime hierarchy. Those are not identical to modality and should not be treated as interchangeable in the analysis write-up.

### Q7. Continuous outputs or thresholds?

- **Continuous** for all main detectors.
- Thresholding should be reserved for appendix operating-characteristic summaries or example selection.
- D8 is the one exception because exact-match extraction is inherently sparse/binary, which is one reason I do not want it carrying confirmatory weight.

### Q8. Case × model structure or flattened summaries?

- Keep the **case × model** structure explicitly in the primary model.
- My default remains the stacked mixed-effects approach from Step 1: case intercepts, model intercepts, and a case×model random intercept when stacking detectors.
- Do **not** flatten to per-case summaries in the primary analysis. That throws away the very contrast structure that identifies D1, D2, D4, and D11.
- Per-case summaries are acceptable only as a robustness check for paper readability.

### Q9. `cutoff_gap_days` distribution and placebo pseudo-cutoff controls

- The realized `cutoff_gap_days` distribution must be audited **before** detector freeze. I would preregister histograms by model after gray-band exclusion and require usable support on both sides of the cutoff for any model that anchors a temporal claim.
- I would also preregister **three falsification controls**:
  - **Same-cutoff architecture pairs** such as `GLM-4-9B ↔ GPT-4.1`.
  - **Size falsification** at fixed cutoff such as `Qwen2.5-7B ↔ Qwen2.5-14B`.
  - **Pseudo-cutoff permutations / quarter-shifted placebo cutoffs** within model tiers or families.
- If a detector still shows a strong cutoff signal under these placebo controls, it should be interpreted as architecture or capability drift, not memorization.

### Q12. How should D3 be presented if it only runs on the white-box subfleet?

- Put D2/D3 in an explicitly labeled **white-box panel**, not in a misleading full-fleet ranking.
- Standardize within detector and analyze on the `5-model` white-box subset only.
- Treat D3 as **corroborative** relative to D1/D7, not as directly comparable in absolute magnitude to full-fleet detectors.

## 7. Multiplicity Budget

There are really two budgets.

### Broad budget I do **not** recommend

If every `detector × factor` coefficient is allowed to be confirmatory, the family blows up quickly:

- `5` main detectors at the Step 1/temporal-session scale imply roughly **`~60-65` confirmatory coefficients**.
- Adding `D4b` or `D12` as full confirmatory detectors pushes that toward **`~72-78`**.
- If `D11` is mistakenly treated as another detector, the family grows again.

Even with Westfall-Young, that is too much. The tests are dependent, so the correction is less severe than Bonferroni, but not free. A family in that size range behaves more like roughly **`18-25` effective independent tests**, which inflates MDEs by about **`1.38-1.40x`** relative to an uncorrected two-sided `0.05` test. That is exactly where medium-strength detectors and Bloc 3 cells start dropping out.

### Recommended budget

Use a **trimmed confirmatory family**:

- **Confirmatory detectors:** `D1 CMMD`, `D2 PCSG`, `D3 Min-K++/CTS`, `D5 SR/FO`, `D7 EAD`
- **Core confirmatory coefficients per detector:** `4`
  - `Cutoff Exposure`
  - `Historical Family Recurrence`
  - `Target Salience`
  - `Template Rigidity`
- **Total confirmatory coefficients:** **`20`**
- **Everything else:** secondary/exploratory with shrinkage and simultaneous intervals, not alpha-spending.

Under this trimmed family:

- Westfall-Young stepdown should keep **FWER at nominal `0.05`**, with realized error likely close to `0.04-0.05` under the global null because detector dependence is mostly positive.
- The `20` raw coefficients should behave more like roughly **`8-12` effective independent tests**.
- That implies MDE inflation of about **`1.28-1.32x`** versus an uncorrected test.

Approximate corrected MDEs in that budget:

| Detector | Corrected MDE |
|---|---|
| **D2 PCSG** | `beta ≈ 0.09-0.11`, roughly `d ≈ 0.19-0.23` |
| **D7 EAD** | `beta ≈ 0.09-0.11`, roughly `d ≈ 0.20-0.24` |
| **D1 CMMD** | `beta ≈ 0.10-0.13`, roughly `d ≈ 0.23-0.28` |
| **D3 Min-K++ / CTS** | `beta ≈ 0.10-0.13`, roughly `d ≈ 0.23-0.28` |
| **D5 SR/FO** | `beta ≈ 0.13-0.16`, roughly `d ≈ 0.30-0.36` |

This is the main reason I want D4b, D8, D11, and D12 outside the confirmatory family for now.

## 8. Proposed Main-Text Shortlist

### Main text / confirmatory core

1. **D2 PCSG**
   Best identification in the pool and very low marginal cost once white-box traces exist.
2. **D7 EAD**
   Best paired intervention and strongest P5-compatible detector.
3. **D1 CMMD**
   Best all-fleet detector and now much better defended by the same-cutoff falsification design.
4. **D3 Min-K++ / CTS**
   Cheap, high-power surface baseline that prevents overclaiming from more narrative-friendly detectors.
5. **D5 SR/FO**
   Keep only if the perturbation audit gate is passed; it is the most valuable intervention-style detector after EAD.

### Reserve

1. **D4 ADG**
   Promote only in its reshaped form (`D4b` primary, `D4a` diagnostic). This is the first reserve I would elevate if D5 fails the perturbation-quality gate.
2. **D12 Schema-Completion**
   Best current answer to the Bloc 3 gap, but only after Bloc 3 taxonomy freeze and a non-redundancy check against D3.

### Appendix-only corroboration

- **D8 Extraction**
  Use for exact-match case studies and qualitative corroboration, not as a power-bearing confirmatory detector.

## 9. Blocking Issues

These are the Step 2-visible issues that would block **R5A closure as a frozen conceptual shortlist** if left unresolved:

1. **No frozen confirmatory family.**
   If the project does not explicitly separate confirmatory from exploratory coefficients, the family drifts back toward the `~60+` coefficient regime and the power story stops being coherent.
2. **Bloc 3 not frozen, but still asked to carry confirmatory weight.**
   If `Disclosure Regime` vs `Modality` is still open, then Bloc 3 and D12 cannot enter the confirmatory family.
3. **Temporal detectors without falsification controls.**
   D1, D2, and D4 need same-cutoff architecture controls, size controls, and pseudo-cutoff controls preregistered. Without them the temporal identification story is too weak.
4. **D5 kept without an explicit edit-quality gate.**
   If there is no audited perturbation pass-rate threshold, D5 should not remain in the core shortlist.
5. **D11, D4a, or extraction allowed to spend confirmatory alpha by default.**
   Those are exactly the additions that create detector-zoo multiplicity without commensurate power.

If those five issues are resolved, I think R5A can close cleanly on a conceptual shortlist even before R5B implementation details are frozen.
