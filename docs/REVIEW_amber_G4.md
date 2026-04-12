# Review: Phase 4 (amber-mirror-lattice)

## Findings

1. **High:** The probe-modality paragraph overstates what the displayed table shows. At `docs/PILOT_RESULTS.md:519-525` the prose says the `cpt_mode` split "does NOT explain" the `impact_hedged` effect and that the higher `llm_negated` rate is "consistent with the memorization interpretation." The displayed table is period-mixed, so that specific comparison is not apples-to-apples. Recomputed from `data/results/diagnostic_2_results.json`: within the generic-only subsample the effect really does persist (`pre=27/216=12.5%`, `post=18/265=6.8%`, Fisher OR≈1.96, p≈0.040), but `llm_negated pre=13/110=11.8%` is **not** higher than `generic pre=27/216=12.5%`. The current wording wins the argument only by comparing `llm_negated` to the pooled generic arm `45/481=9.4%`, which is diluted by all post cases. Add a `period × cpt_mode` cross-tab or rewrite this paragraph.

2. **High:** The section repeatedly crosses from supported association to unsupported construct claim. At `docs/PILOT_RESULTS.md:499-510`, `557-563`, and `582-584`, `fo_flip_impact_hedged` is written up as a discovered "memorization signal," the model that "knows" the true `fund_impact`, and evidence that "validates the amber-mirror-lattice plan's premise." The actual support is narrower: pooled MH OR=1.95, p=0.022, BD p=0.28 shows more **hedged retreat under the planted false outcome** for pre-cutoff cases. Given the section's own caveats on construct validity, probe-modality confounding, underpower, and missing positive control, this should be framed as **consistent with** a memorization-direction interpretation, not as confirmation that the model knows the true `fund_impact`.

3. **Medium:** Q3 and part of the headline paragraph oversell anchor interaction. At `docs/PILOT_RESULTS.md:502-505` and `576-584`, the prose says the effect is "driven by the weakly-anchored stratum" and gives "Partial support" for the bidirectional confound hypothesis. The weak stratum estimate is numerically larger (OR 2.62 vs 1.38), but the planned heterogeneity test is negative: Breslow-Day p=0.28. That supports "point estimates differ in the expected direction, but interaction is unconfirmed/underpowered," not partial confirmation of the confound hypothesis.

4. **Medium:** Several Phase 3 comparison numbers are not reproducible from the evidence bundle you specified. Current Phase 4 numbers are reproducible from `data/results/diagnostic_2_results.json` and `data/results/sensitivity_analysis.json`, but Phase 3 comparison cells/phrases in this section are not: `n_scored (Phase 3)` 447/434, `was 17%`, `was 121/606=20%`, `p=0.035 (Phase 3)`, and `was 447`. They may be correct, but they require a prior-phase artifact outside the two files named in the review brief. If you want this section to be auditable from the stated evidence alone, those numbers need either an explicit extra source or removal.

5. **Medium:** The section does not pass the reader test for a reviewer who has not internalized Phase 3. A new reader still cannot reconstruct the experiment from this section alone: CFLS vs CPT are assumed, `strict` vs `hedged` is not operationally defined where first needed, OR orientation (`pre` in the numerator) is implicit, `cpt_mode=generic_post_cutoff` misleadingly looks post-only even though it contains 217 pre cases, and the section never locally restates what pre/post cutoff operationalizes. The missing `period × cpt_mode` table is the clearest symptom.

6. **Low-Medium:** The updated Q2/Q3 do conflict with the old Phase 3 answers, and the reversal is only implicit. Phase 3 said CPT was suggestibility-only and that the bidirectional confound had no added support; Phase 4 now says "Both" and "Partial support." The body hints at the reason (Bug 3 made neutral retreat invisible under the strict definition), but the Q&A section never states explicitly that these answers **supersede** the Phase 3 answers because the legacy coding was wrong.

## Spot Checks

Five independent spot-checks from the result JSONs matched the Phase 4 tables/prose after rounding:

1. `direct_prediction.base` aggregate CFLS: `n_scored=591`, mean `-0.7986 -> -0.799`, positive rate `12/591=2.03% -> 2.0%`.
2. Cross-task CFLS correlation: Spearman `rho=0.09105 -> 0.091`, `p=0.02916 -> 0.029`, `n=574`.
3. `cfls_direct` temporal split: `pre mean=-0.750 (n=324)`, `post mean=-0.858 (n=267)`, Mann-Whitney `U=47009.5 -> 47010`, `p=0.006529 -> 0.0065`.
4. `fo_flip_direct_hedged` pooled MH: `pre=48/328`, `post=58/272`, pooled OR `0.6376 -> 0.638`, `p=0.03616 -> 0.036`, BD `p=0.9151 -> 0.92`.
5. `fo_flip_impact_hedged` weak stratum and probe-modality table: weak-stratum `24/144` vs `9/127`, OR `2.6222 -> 2.622`, Fisher `p=0.02434 -> 0.024`; `llm_negated impact hedged = 13/110 = 11.8%`.

## Requested Checks

- **数字一致性:** Phase 4-native numbers I spot-checked are internally consistent. The main reproducibility problem is not wrong arithmetic; it is that multiple Phase 3 comparison numbers in this section cannot be regenerated from the two files you named.
- **Overclaiming:** Fails as written for the memorization-construct language and for the anchor-interaction framing.
- **Direction-of-effect framing:** Mostly improved relative to Phase 3 because `strict` vs `hedged` is now separated, but the prose still slides from "hedges more" to "knows the true outcome" too quickly.
- **Caveat 完整性:** Pass. The section does mention (a) Carlini/Nasr construct validity, (b) the v3 frequency × period confound, (c) residual underpower below OR<2, and (d) lack of a positive control with Phase F as future work.
- **Q1/Q2/Q3 一致性:** Q1 is stable. Q2/Q3 materially reverse the Phase 3 answers; the body partially explains why, but the reversal is not stated explicitly enough in the Q&A itself.
- **Reader test:** Fail. A reviewer could follow the conclusion trend, but not independently reconstruct the design and the probe-confound logic from this section alone.

Verdict: ITERATE
