---
title: Lens B — Statistical & numerical correctness
date: 2026-04-29
review_id: R5A_DESIGN_REVIEW_R2_20260429
lens: B_statistics
codex_thread_id: codex-local-review
status: complete
---

# Lens B Verdict

The Path E detector is directionally faithful to the Round 1 recommendation: it fits the requested piecewise linear/change-in-level WLS model, grid-searches an admissible month-level knee, bootstraps article cases within month, and applies the specified CI-width plus drop-lower-bound acceptance rule.

The Phase 8 power script is not statistically faithful to the current plan. It is a closed-form planning calculator, not the §8.8 simulation. It also applies a model/family random-intercept SE formula to `E_CMMD` even though the current plan defines `E_CMMD` as a case-level fleet aggregate with case-cluster bootstrap inference, not as a case-by-model mixed model.

## Critical math errors

1. **`scripts/simulate_phase8_power.py` does not implement the planned Phase 8 power simulation.** Plan §8.8 requires `B = 2000` synthetic datasets, refitting planned models, preserving eligibility/missingness/cross-estimand covariance, and applying Westfall-Young in each replicate (`plans/phase7-pilot-implementation.md:910-945`). The script explicitly uses closed-form SEs (`scripts/simulate_phase8_power.py:15-19`), leaves `--b-outer` informational (`scripts/simulate_phase8_power.py:193-199`), and only adds cosmetic binomial MC intervals to closed-form powers (`scripts/simulate_phase8_power.py:404-415`).

2. **`E_CMMD` power is calibrated with the wrong analysis unit.** The plan says `E_CMMD` is a fleet-aggregated case-level score with no model random effect after aggregation (`plans/phase7-pilot-implementation.md:799-809`). The script instead computes `E_CMMD` SE with model and family random-intercept terms over 14 P_predict models (`scripts/simulate_phase8_power.py:272-295`). This makes the default main-run CMMD SE about `sqrt(((1/2560 + 0.35^2)/14) + 0.20^2/4) = 0.137`, giving only about 9% WY power for `beta=0.20`; Round 1 expected roughly 87-99% under the CMMD anchor (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:20-27`).

3. **The power script reports MC uncertainty where no Monte Carlo estimator exists.** `sqrt(p(1-p)/B)` is meaningful for `power_j = B^-1 sum I[p_j^(WY,b)<alpha]` in the planned simulation (`plans/phase7-pilot-implementation.md:934-945`), but not for the script's deterministic closed-form probability (`scripts/simulate_phase8_power.py:116-129`, `scripts/simulate_phase8_power.py:404-415`).

## Calibration mismatches against Round 1 anchors

1. **PCSG numeric SE anchors match §5, but the label is ambiguous.** The script's `sigma_pair_residual = 4.5` gives `4.5/sqrt(2048*0.98) = 0.1004` for one pair and `4.5/sqrt(2048*0.98*2) = 0.0710` for two pairs (`scripts/simulate_phase8_power.py:315-324`). That matches the Round 1 interaction-SE table (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:102-112`). The row name `E_PCSG_beta_cutoff` can be read as the main cutoff coefficient, but the calibration is for the weaker interaction coefficient.

2. **`reweighted_phase8 = 0.85x` is not specified by the plan.** Plan §8.8 says to reweight coefficients to expected `category × cutoff window` composition (`plans/phase7-pilot-implementation.md:912-918`). The fixed 0.85 multiplier is a heuristic introduced in code (`scripts/simulate_phase8_power.py:173-183`).

3. **CMMD variance-component constants are heuristic.** Round 1 specified inflation factors `1.0, 1.2, 1.35` (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:29`), but not base `sigma_model = 0.35` and `sigma_family = 0.20` for CMMD. The `0.35` anchor appears in Round 1 for capacity-curve model clustering, not for fleet-aggregated CMMD (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:37-42`).

4. **Path E CI endpoint rounding is anti-conservative on the upper bound.** `int(np.percentile(..., 97.5))` floors the upper CI endpoint (`src/r5a/analysis/cutoff_probe.py:403-410`). For integer knees, the lower endpoint should be floored and the upper endpoint ceiled, or the empirical quantile should be reported with an explicit discrete convention.

## Path E findings (`cutoff_probe.py`)

**A.1 Model formulation — correct.** `_piecewise_wls_fit` builds `[1, t, I(t > kappa), max(0, t-kappa)]` and solves WLS (`src/r5a/analysis/cutoff_probe.py:116-145`). `_grid_search_kappa` passes `kappa = k + 0.5`, so integer months `0..k` are pre and `k+1..n-1` are post (`src/r5a/analysis/cutoff_probe.py:149-176`). This matches the Round 1 sketch (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:68-76`) and correctly treats `k` as the last pre-cutoff month.

**A.2 Slope-change term — correct with one interpretation caveat.** The hinge is zero pre-knee and positive post-knee (`src/r5a/analysis/cutoff_probe.py:128-134`). This is a standard step-plus-piecewise-slope model. The reported `delta` is the discontinuity at the half-month knot; the observed first-post-month change is `delta + 0.5*lambda`, so `drop = -delta` is a level-discontinuity estimate, not a raw adjacent-month drop.

**A.3 `drop = -beta[2]` — correct.** Min-K logprobs are negative, and less negative means more familiar (`src/r5a/analysis/cutoff_probe.py:89-92`). A post-cutoff familiarity decrease makes scores more negative, so the fitted step `delta` is negative and `-delta` is a positive drop (`src/r5a/analysis/cutoff_probe.py:269-272`, `src/r5a/analysis/cutoff_probe.py:371`).

**A.4 WLS weights — depends.** `w = counts / variances` is the inverse-variance weight for a monthly mean under iid article noise (`src/r5a/analysis/cutoff_probe.py:179-218`). The default aggregator is the median (`src/r5a/analysis/cutoff_probe.py:276-285`), whose variance has an extra density-dependent factor; if monthly distributions are similarly shaped this is mostly a constant, but it is not exact. The singleton fallback to pooled variance is defensible and conservative, but because pooled variance includes between-month signal it may underweight singleton months rather than optimally weight them (`src/r5a/analysis/cutoff_probe.py:209-217`).

**A.5 Grid bounds — correct.** With `min_side = 6`, `lo = 5` and `hi = n - 7` (`src/r5a/analysis/cutoff_probe.py:162-176`). At `n=36`, this searches `5..29`: `k=5` leaves 6 pre months and 30 post months, while `k=29` leaves 30 pre months and 6 post months.

**A.6 Bootstrap resampling — mostly correct, conditional on the month grid.** `_bootstrap_kappa` is a stratified nonparametric case bootstrap within month, not a parametric bootstrap (`src/r5a/analysis/cutoff_probe.py:221-273`). It recomputes the monthly aggregator and WLS weights, so it captures finite-article noise in the monthly median/mean. It does not capture month-level shocks, temporal autocorrelation, source/topic regime shifts, or uncertainty from treating the observed month sequence itself as random.

**A.7 CI computation — wrong endpoint convention.** The percentile interpolation is fine, but casting both endpoints with `int()` floors both endpoints (`src/r5a/analysis/cutoff_probe.py:403-410`). For nonnegative integer knees this makes the upper bound too low when the 97.5th percentile is not already an integer. Fix sketch: `k_lo = floor(q025)`, `k_hi = ceil(q975)`, then clamp to valid month indices.

**A.8 Acceptance rule — correct.** `accept = (ci_width <= max_ci_width_months) and (drop_lo > drop_threshold)` exactly implements the Round 1 rule (`src/r5a/analysis/cutoff_probe.py:418-457`; `refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md:46-49`).

**A.9 Singular fits — not accepted, but reporting can mislead.** Singular candidates return `wss = inf` (`src/r5a/analysis/cutoff_probe.py:140-143`). If all candidates are singular, `_grid_search_kappa` still returns the lower grid bound with zero beta because it never checks `best_wss` for finiteness (`src/r5a/analysis/cutoff_probe.py:167-176`). The acceptance rule will reject because `drop_lo` is not positive, but the rejected point estimate can look like a real knee. Fix sketch: return `-1` when no finite WSS is found, and optionally reject ill-conditioned `XtWX` by condition number.

**A.10 Determinism — correct.** Months are sorted before fitting (`src/r5a/analysis/cutoff_probe.py:295`), and bootstrapping uses a local `np.random.default_rng(seed)` (`src/r5a/analysis/cutoff_probe.py:373-381`). Given the same `by_month`, seed, NumPy/BLAS behavior, and deterministic aggregator, output is deterministic.

**A.11 Null false-positive behavior — improved under iid article noise, fragile under month-level shocks.** Round 1 showed the old threshold detector had 50% FPR at monthly noise SD `0.10` (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:57-64`). A small local sketch with 36 months, 60 articles/month, and iid article noise chosen so median SE is about `0.10` used `sigma_article = 0.10*sqrt(60)/1.253 = 0.618` and accepted `0/20` null series with `B=150`. But when I simulated a month-level shock `N(0,0.10)` plus tiny within-month residual SD `0.02`, it accepted `1/20`. That is the expected failure mode: within-month case bootstrap can certify a spurious regime shift if the regime shift is a fixed month-level shock. The detector is much better than the threshold rule, but it is not a complete defense against the Round 1 regime-shift critique.

**Tests under review.** `tests/r5a/test_cutoff_probe.py` passes locally (`7 passed`). The tests cover clean-step acceptance (`tests/r5a/test_cutoff_probe.py:88-116`), flat-series rejection (`tests/r5a/test_cutoff_probe.py:119-134`), noisy rejection (`tests/r5a/test_cutoff_probe.py:137-159`), too-few/no-data handling (`tests/r5a/test_cutoff_probe.py:162-174`), and article counts (`tests/r5a/test_cutoff_probe.py:177-189`). They do not exercise the CI rounding bug, singleton-month weights, sloped baselines with nonzero `lambda`, exact grid endpoints, singular WLS handling, or deterministic repeatability.

## Power sim findings (`simulate_phase8_power.py`)

**B.1 Family random-intercept formula — depends, and wrong for CMMD.** The formula `((sigma_w^2/n_case + sigma_m^2)/n_models) + sigma_f^2/n_families` is implemented as documented (`scripts/simulate_phase8_power.py:132-154`). It can be a rough design-effect approximation for averaging model-specific slopes with independent within-family model effects and family effects. It is not the SE of the §8.2 mixed model with random intercepts (`plans/phase7-pilot-implementation.md:776-795`), and it does not honor small family-level degrees of freedom beyond adding a variance term. With unbalanced families, family averaging should use model weights like `sum_g (n_g/N)^2`, not always `1/n_families`; for P_predict this is `58/196 = 0.296` rather than `0.25`. For `E_CMMD`, the formula contradicts the plan's case-level aggregate model (`plans/phase7-pilot-implementation.md:799-809`).

**B.2 PCSG SE formula — numerically correct for the §5 interaction anchor, label caveat.** `_se_pcsg_pair` computes `sigma/sqrt(n_eff*n_pairs)` with integer `n_eff` (`scripts/simulate_phase8_power.py:157-170`). With `sigma=4.5`, `n_eff=int(2048*0.98)=2007`: one pair gives `4.5/sqrt(2007)=0.1004`; two pairs gives `4.5/sqrt(4014)=0.0710`. WY power at `beta=0.20`, `z=2.8`, is about 21% for one pair and 51% for two pairs, consistent with the Round 1 §5 interaction table (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:102-112`). The caveat is that the code labels rows as `E_PCSG_beta_cutoff` (`scripts/simulate_phase8_power.py:337-352`), while the §5 anchor is for `beta3` interaction power.

**B.3 WY power formula — correct for current two-sided planning.** `_wy_power` computes `P(|Z| > z_wy | mean = beta/se)` (`scripts/simulate_phase8_power.py:116-129`). Round 1 explicitly used a two-sided WY-effective `z = 2.8` (`refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:1-3`). A one-sided test could be pre-registered for directional cutoff effects, but that is not the current documented multiplicity anchor.

**B.4 Scenario multipliers — wrong as an implementation of §8.8.** `unweighted_pilot` and `shrinkage_0.5` match the named scenarios. `reweighted_phase8 = beta*0.85` is not specified by the plan (`scripts/simulate_phase8_power.py:173-183`). The plan requires reweighting coefficients to expected Phase 8 `category × cutoff window` composition (`plans/phase7-pilot-implementation.md:912-918`), not applying a constant shrinkage factor.

**B.5 CMMD inflation factors — mixed.** The inflation factor grid `(1.0, 1.2, 1.35)` matches Round 1 (`scripts/simulate_phase8_power.py:85-93`; `refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/statistical_power_lens.md:29`). The base SDs `0.35` and `0.20` used for CMMD model/family components are heuristics (`scripts/simulate_phase8_power.py:272-295`). I found no CMMD-specific calibration anchor in the cited plan sections; the plan instead says to use observed variance components and empirical covariance from the pilot (`plans/phase7-pilot-implementation.md:922-931`).

**B.6 FO eligibility sweep — plausible stress range, not anchored.** The hard-coded `(0.5, 0.7, 0.9)` sweep (`scripts/simulate_phase8_power.py:355-384`) spans below-caveat, near-plausible, and optimistic coverage. The plan expects at least 60 pre-cutoff `C_FO`-eligible cases out of 80, i.e. about 75%, and requires coverage to be reported rather than gated (`plans/phase7-pilot-implementation.md:596-600`, `plans/phase7-pilot-implementation.md:653-659`). A better default would use pilot-realized FO and NoOp eligibility separately, with stress values around the 60% caveat boundary.

**B.7 MC SE bookkeeping — wrong for closed form.** The code adds `power_*_mc_se` and 95% intervals around deterministic closed-form power (`scripts/simulate_phase8_power.py:404-415`). This only has a sampling interpretation if the script actually estimates power as a Monte Carlo average over `B` simulated datasets, as in plan §8.8 (`plans/phase7-pilot-implementation.md:934-945`).

**B.8 `--b-outer` — misleading.** The top docstring says CLI args control bootstrap count (`scripts/simulate_phase8_power.py:28-36`), but argparse says `--b-outer` is informational and unused in the closed-form path (`scripts/simulate_phase8_power.py:193-199`). This does not meet the plan's "simulate `B = 2000` main-run datasets" requirement (`plans/phase7-pilot-implementation.md:922-933`).

**B.9 Family-state collapsing — correct for default, incomplete for dial-back.** Defaulting to `["S20"]` matches the 2026-04-29 gate-removal decision (`scripts/simulate_phase8_power.py:252-259`; `docs/DECISION_20260429_gate_removal.md:185-199`). If multiple states are passed, the script only labels rows; it does not adjust the family size, coefficient set, or WY critical value (`scripts/simulate_phase8_power.py:268-270`). That is acceptable only because non-S20 states are no longer legal defaults.

**B.10 Llama family handling — correct for the implemented estimands, incomplete overall.** The fleet summary correctly counts P_logprob as 12 with Llama and P_predict as 14 without Llama (`scripts/simulate_phase8_power.py:55-69`, `scripts/simulate_phase8_power.py:105-113`), matching the Llama decision (`docs/DECISION_20260429_llama_addition.md:81-99`). `E_CMMD` and `E_FO/E_NoOp` use `len(fleet.family_p_predict) = 4`, which is right because Llama is excluded from P_predict (`scripts/simulate_phase8_power.py:278-295`, `scripts/simulate_phase8_power.py:362-384`). The script still omits `E_CTS` power rows despite advertising 12 P_logprob models in the fleet summary.

## Recommended actions before pre-registration

1. Replace `simulate_phase8_power.py` with the actual §8.8 simulation or rename it as a coarse closed-form planning calculator and keep it out of preregistration-grade power claims.
2. For `E_CMMD`, remove model/family random-intercept SE terms unless the estimand is changed back to case-by-model; use the fleet-aggregated case-level model and case-cluster bootstrap plan.
3. Make power rows factor-specific: distinguish `beta1` cutoff exposure from `beta3` factor interactions, especially for PCSG.
4. Remove closed-form MC intervals, or compute them only after real `B`-replicate simulation.
5. Replace hard-coded `reweighted_phase8 = 0.85` with actual composition reweighting.
6. Fix Path E integer CI endpoints with `floor`/`ceil`, and return no knee when every WLS candidate has non-finite WSS.
7. Add cutoff-probe tests for CI rounding, singleton weights, sloped baselines, exact grid endpoints, all-singular WLS, repeatability under fixed seed, and a month-level shock placebo.

## Confidence

High for the code-vs-formula findings and the power-script mismatch with plan §8.8. Medium for the null-FPR calibration because I used a small local sketch rather than a full 2,000-replicate study; the qualitative conclusion is strong because the bootstrap is explicitly conditional within observed months.
