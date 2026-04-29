## Statistical Audit Verdict

Assumptions for the back-of-envelope numbers: standardized outcome SD = 1, two-sided Westfall-Young effective critical value about `z = 2.8` for the 20-coefficient family, pilot composition from plan §6.2, and PCSG vocab eligibility `75-90%` for conservative power tables.

### 1. Westfall-Young Family Size After Fleet Expansion

**Verdict: family size stays 20. Severity: fix-then-ship.**

The confirmatory family is still `5 estimands × 4 factors = 20` per `R5A_FROZEN_SHORTLIST.md §1` and `phase7 §7.1A`. Fleet expansion changes the covariance, effective sample size, and estimand noise, not the number of confirmatory coefficients. `E_PCSG_capacity_curve` and `E_FO_mech` are exploratory per shortlist §3, so they do not enter max-T.

But plan §8.8 still says simulate `N_model = 9`; that is now wrong. Use:

| Estimand | Simulation unit now |
|---|---:|
| `E_CMMD` | case-level aggregate from 14 models |
| `E_CTS` | case × 10 white-box |
| `E_PCSG` | case × 1 temporal pair, vocab-eligible only |
| `E_FO`, `E_NoOp` | case × 14 P_predict models, eligibility masked |

Approximate Westfall-Young-adjusted power:

| Coefficient | Effect, standardized | n=100 pilot | n=2560 main |
|---|---:|---:|---:|
| `E_CMMD β_cutoff`, with 20-35% fleet-noise inflation | `0.15` | `1-2%` | `55-84%` |
| `E_CMMD β_cutoff`, same | `0.20` | `2-4%` | `87-99%` |
| `E_PCSG β_cutoff`, 1 pair, 75-90% eligible | `0.20` | `2%` | `76-82%` |
| `E_PCSG β_cutoff`, 1 pair, 75-90% eligible | `0.25` | `3%` | `94-97%` |

Simulation parameters I would use: `B_outer = 2000` minimum per plan §8.8, preferably `5000` for final table; case-cluster resampling; model random intercepts; model-family random intercepts for Qwen2.5/Qwen3/GLM/API; PCSG eligibility `p = {0.75, 0.85, 0.95}`; CMMD fleet-noise inflation `1.0, 1.2, 1.35`; effect scenarios `β = {0.10, 0.15, 0.20, 0.30}`; cross-estimand correlations `ρ = 0.2-0.8`; family states `S20/S16a/S16b/S12`.

### 2. `E_PCSG_capacity_curve` OLS Slope at n=100

**Verdict: descriptive only at pilot. Severity: ship-with-caveat.**

For log2 parameter sizes:

| Family | Points | `Sxx` across model means | SE ignoring clustering, σ=0.75 | Proper SE, σ_model=0.35 and σ_article=0.75 |
|---|---:|---:|---:|---:|
| Qwen2.5 | 5 | `12.23` | `0.021` | `0.102` |
| Qwen3 | 4 | `4.84` | `0.034` | `0.163` |

Ignoring clustering treats `500` or `400` article-model rows as independent and understates SE by about `5x`. Proper inference has only `df=3` for Qwen2.5 and `df=2` for Qwen3. For `p<0.05`, the required slope is approximately:

| Family | t critical | Required slope, central SE |
|---|---:|---:|
| Qwen2.5 | `3.18` | `0.32` logprob units per doubling |
| Qwen3 | `4.30` | `0.70` logprob units per doubling |

For `p<0.01`, required slopes are about `0.60` and `1.62`. Pilot OLS has little chance of meaningful rejection unless the effect is very large.

### 3. Path E Knee Threshold `min_drop_magnitude=0.05`

**Verdict: replace threshold-only detection. Severity: fix-then-ship.**

The current implementation in `src/r5a/analysis/cutoff_probe.py` picks the breakpoint with the largest pre/post mean drop after 3-month smoothing and accepts it if drop `>=0.05`.

With 36 months and realistic month-level Min-K noise after 60 articles/month:

| Monthly noise SD | Null false positive rate for threshold 0.05 |
|---:|---:|
| `0.06` | `21%` |
| `0.08` | `38%` |
| `0.10` | `50%` |
| `0.12` | `59%` |

For a true drop of `0.10`, detection is high, but localization within ±1 month is only `20-47%` depending on noise. That is too unstable for `cutoff_observed` to enter §8.2 as a known covariate.

Recommendation: **piecewise linear/change-in-level regression with case bootstrap CI**.

Implementation sketch:
1. For each model, fit monthly Min-K with WLS:
   `score_t = α + γ*t + δ*I(t > κ) + λ*(t - κ)+ + ε_t`
2. Grid-search `κ` over months with at least 6 months on each side.
3. Bootstrap articles within month, `B=2000`, refit κ.
4. Report `κ_hat`, 95% CI, `P(drop > 0.05)`, and CI width.
5. Accept `cutoff_observed` only if CI width `<= 3 months` and lower CI for drop `>0.05`; otherwise mark cutoff uncertain and simulate exposure misclassification.

### 4. WS6 Trigger Denominator

**Verdict: use `6/10` white-box models. Severity: fix-then-ship.**

WS6 is mechanistic and requires hidden states, so the denominator is not 14. Black-box models cannot contribute to DS/KL/patch localization. The correct denominator is the white-box hidden-state-eligible fleet: `10`.

The old `5/9` threshold preserves a proportion of `55.6%`. Scaling that gives:

| Fleet basis | Correct threshold |
|---|---:|
| old 9-model full fleet | `5/9` |
| new 10 white-box WS6 fleet | `6/10` |
| new 14 P_predict behavioral fleet | `8/14` |

Do not keep fixed `5`. Under a per-model null hit rate of `25%`, `P(K>=5/14)=25.9%`, compared with `P(K>=5/9)=4.9%` and `P(K>=6/10)=2.0%`.

### 5. `E_PCSG` Effective Sample Size After Pair Reduction

**Verdict: pilot interaction power is effectively zero. Severity: fix-then-ship.**

The Qwen3 extension tokens are `<tool_response>`, `</tool_response>`, `<think>`, `</think>`. Real CLS Chinese financial news should almost never contain them. Expected vocab eligibility is `98-100%`, not `50-90%`, unless special-token handling is misconfigured.

The pair-count reduction still matters. Original `2 × 100 = 200`; new design is about `1 × 98-100`, so SE inflates by `sqrt(200/100)=1.41`. If eligibility were only `50`, SE inflation would be `2.0`.

For the §8.2 PCSG interaction `β3`, approximate SE:

| Design | Interaction SE | WY MDE at z=2.8 |
|---|---:|---:|
| pilot, 1 pair, pre-only 80 cases | `0.52` | `1.45 SD` |
| pilot, 1 pair, all 100 cases | `0.41` | `1.14 SD` |
| original pilot, 2 pairs | `0.29` | `0.81 SD` |
| main, 1 pair, n=2048 pre, 98% eligible | `0.10` | `0.29 SD` |
| original main, 2 pairs | `0.073` | `0.20 SD` |

Main-run power for 1-pair PCSG `β3`: `20%` at `β3=0.20`, `54%` at `0.30`, `86%` at `0.40`. Original 2-pair design would be about `48%`, `90%`, `~100%` for the same effects. So the new design is usable for the main cutoff coefficient, but weak for per-factor interactions.

### 6. Multiplicity for Exploratory Estimands

**Verdict: separate exploratory family. Severity: ship-with-caveat.**

Do not add exploratory estimands to the confirmatory Westfall-Young family. But reported p-values need a rule.

Use:
- Confirmatory: Westfall-Young FWER `α=0.05` over `S20/S16/S12`.
- Exploratory planned family: BH-FDR `q=0.10` if making discovery language.
- Descriptive-only option: effect sizes plus simultaneous bootstrap CIs, no “significant” claims.

Concrete grouping:
- `E_PCSG_capacity_curve`: two primary slopes, Qwen2.5 and Qwen3; BH across those two if p-values are shown.
- `E_FO_mech`: predefine final-25%-layer contrast; use cluster permutation or BH across `10 models × metrics`, not uncorrected layerwise tests.

### 7. BL2 TOST at SESOI `0.15`, n_post=20

**Verdict: n=20 cannot establish equivalence. Severity: block for Phase 8 automatic GO.**

With `n=20`, standardized SE is `1/sqrt(20)=0.224`. The 95% CI half-width is `1.96 × 0.224 = 0.44`, almost `3x` the SESOI. Even if the true effect is exactly zero, the probability that the 95% CI lies inside `[-0.15, +0.15]` is effectively `0%`.

Needed n under the current 95% CI rule:

| n_post | TOST power at true effect 0 |
|---:|---:|
| `20` | `0%` |
| `120` | `0%` |
| `180` | `4%` |
| `350` | `60%` |
| `700` | `96%` |

Remediation: keep 20 as a gross falsification screen only, then add a two-stage rule. If `|d_hat| <= 0.10` but CI is too wide, sample post-cutoff controls up to at least `350`; if `|d_hat| > 0.15` or same-direction signal appears, stop and review cutoff/scoring. Do not widen SESOI unless the paper is willing to defend a much weaker negative control.

## Highest-Priority Risks Before Cloud Spend

1. Update §8.8 power simulation from `N_model=9` to the actual `14/10/1-pair` design, including PCSG eligibility and model-family clustering.
2. Replace Path E hard-threshold knee detection with bootstrapped piecewise regression before using `cutoff_observed`.
3. Fix BL2: `n_post=20` cannot satisfy the current equivalence gate, so §13 automatic GO is mathematically impossible.

Can wait until prereg drafting:

1. Define the exploratory multiplicity rule: BH-FDR `q=0.10` or descriptive-only.
2. State that `E_PCSG_capacity_curve` pilot slopes are descriptive because 4-5 model points do not support stable p-values.