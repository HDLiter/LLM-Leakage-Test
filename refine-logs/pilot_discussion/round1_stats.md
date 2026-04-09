# Round 1 — Stats Agent (Senior Econometrician)

**Thread:** 019d65d4-01a1-7393-8838-f01c11b50be1

## Analysis

### 1. Identification Failure

The pilot shows the CFLS estimand is **not point-identified**. Two observationally equivalent DGPs produce the same CFLS distribution: (a) low memorization + genuine reading, and (b) high memorization + strong bidirectional generalization. Since both yield S_i ≈ -1, M_i is not recoverable from S_i.

**Violated assumptions:**
- **Exclusion restriction:** A must affect outcomes only through reasoning channel. DAG already shows A → D, so this fails.
- **Monotonicity/sign restriction:** More memorization must not increase counterfactual sensitivity. Bidirectional generalization violates this.
- **Practical overlap/support:** All scores at or below zero, medians at -1 — no empirical variation to separate latent states.

### 2. Bidirectional Generalization as Omitted Variable Bias

Let B_i = bidirectional coverage. Structural relation:

S_i = α + τ M_i + γ B_i + u_i

where τ = effect of memorization on CFLS, γ = direct effect of bidirectional coverage on CFLS.

- γ < 0 (more bidirectional coverage → more reversal following → more negative CFLS)
- Cov(M_i, B_i) > 0 (more frequent events → higher memorization potential)

Omitting B_i yields: plim τ̂ = τ + γ · Cov(M_i, B_i) / Var(M_i). Bias is **negative**. The cases most likely memorized are also the cases most likely to look highly counterfactually sensitive. This can fully attenuate or reverse the true relation.

### 3. Sample Size and Power

n=36 overall, cells of n=7 and n=4 support only descriptive statements. In the n=4 macro cell, one observation moves a proportion by 25pp.

For 1000-case benchmark with SD ≈ 0.35: SE ≈ 0.011 for overall mean. Balanced two-group comparisons: ~80% power for d ≈ 0.18. For flip rates near 15%, 95% margin of error ≈ ±2.5pp.

**Critical:** 1000 is not automatically well-powered for subgroup analysis. Pre-specify minimum cell counts.

### 4. Cross-Task Correlation r = 0.10

At n=35, Fisher's z gives 95% CI ≈ [-0.24, 0.42], p ≈ 0.57. Data consistent with modest negative, zero, or modest positive correlation. Severe censoring at -1 likely attenuates the correlation (range restriction). Correct conclusion: "pilot cannot establish convergent validity," not "tasks are unrelated."

### 5. False-Outcome CPT: Need a Proper Null

Testing against null of zero is inappropriate — prompt perturbations can induce flips under no memorization. Correct null:

H_0: P(flip | false-outcome CPT, no memorization) = p_0 ≠ 0

Estimate p_0 from **negative controls**: matched synthetic cases, temporally impossible cases, or placebo prompt modifications. Cleanest design: paired within case — compare flip under false-outcome CPT vs. matched placebo, test with conditional logistic model or McNemar-style paired analysis.

### 6. Ecological Inference Risk in Stratification

The high-memorization / lower-CFLS reversal could be Simpson's paradox. Aggregate comparison mixes: category composition, recency, prominence, lexical polarity strength, reversal plausibility, bidirectional coverage. With only 7 medium cases, observed ranking is too fragile for causal interpretation.

### 7. Inference Protocol for 1000-Case Benchmark

**Multilevel design:** Repeated observations by case × task × condition. GLMM or Bayesian hierarchical model with:
- Condition effects adjusted for confounders (bidirectional coverage, recency, prominence, category, reversal plausibility)
- Random intercepts for cases, possibly random slopes by task

**Pre-registration should specify:**
- Primary estimands (confirmatory vs. exploratory)
- DAG-based adjustment set
- Minimum cell sizes for subgroup claims
- Exclusion rules, missing-data handling, detector thresholds
- Negative and positive controls
- Holdout split if thresholds/rubrics are tuned

**Multiplicity:** Holm for confirmatory endpoints, BH for exploratory subgroup analyses.

**Most importantly:** CFLS should be one indicator in a validated measurement battery, calibrated against controls that make identification assumptions empirically testable.
