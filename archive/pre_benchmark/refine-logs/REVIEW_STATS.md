# Statistical Review of the Experiment Plan

## Score and Verdict

**Score:** 7.3/10  
**Verdict:** Promising and close, but not yet fully econometrically tight. As written, this is adequate for a bounded ML/measurement paper if the remaining pre-specification gaps are closed. It is not yet at Journal of Econometrics / JFDS inferential standard.

## Bottom Line

The plan is much improved relative to a typical LLM-leakage proposal: it now treats the main contribution as measurement, not causal identification; it clusters at the event level; it recognizes multiplicity; and it demotes the weakest finance-facing object (`theta` in E6) to supplementary status. Those are the right moves.

The remaining problems are mostly about **precision of the inferential protocol**, not the broad design. The main ones are:

1. The **primary estimand hierarchy is still underspecified** relative to the actual success criteria.
2. The **power / MDE story is too loose** for the primary contrasts and placebo.
3. The **generated-regressor issue is only partially solved** in E6.
4. The **temporal decay and concordance analyses remain descriptive**, and the plan should say so more explicitly.
5. `src/metrics.py` does **not yet implement the cluster-level estimands or bounded confidence math** implied by the plan.

## Strengths

- The move from causal language to **measurement + diagnostic association** is correct.
- Clustering by company-day is the right first-order dependence correction for duplicated/propagated news.
- The combination of **matched-format ablation** and **sham decomposition** is a serious attempt to separate semantic task effects from format effects.
- Demoting E6 from the primary family is appropriate.
- Pre-registering one primary `k=0.20` and one primary 3-day return horizon is good discipline.
- Using a documented post-boundary placebo window is better than selecting breakpoints from the observed leakage curves.

## 1. Statistical Inference Protocol

### Assessment

The protocol is **directionally correct but incomplete**.

- For **E3/E4**, cluster bootstrap at the event-cluster level is sensible for confidence intervals, because the same cluster is observed under multiple prompts and rewrites.
- For **E3**, however, the natural primary test is not generic bootstrap significance; it is a **paired cluster-level randomization / permutation test** on pre-defined contrasts, because treatment variation is within cluster.
- For **E2** and especially **E6**, simple cluster bootstrap is not enough. There is likely residual dependence by publication date, issuer, and overlapping return horizon. The current prose says "grouped errors" and "HAC-style corrections," but that is not operationally specified.

### What is missing

- The resampling unit is clear for event dependence, but not for **date dependence**.
- There is no precise rule for when to use:
  - cluster bootstrap,
  - paired randomization inference,
  - date-block bootstrap,
  - two-way clustered covariance.
- Romano-Wolf is mentioned, but the actual family being corrected is not fully enumerated.

### Recommendation

Use the following rule set:

1. For **E3/E4 task contrasts**, compute cluster-level contrasts and use:
   \[
   D_g^{ab} = EI_{g,a} - EI_{g,b}
   \]
   with a paired sign-flip / randomization test as the primary p-value and clustered bootstrap for CIs.
2. For **E2 concordance**, use cluster bootstrap **and** a sensitivity check with date-block bootstrap.
3. For **E6**, use either:
   - two-way clustering by issuer and date in linear second-stage regressions, or
   - a date-block bootstrap of the full pipeline.
4. Report the number of effective clusters in every table, not just article counts.

## 2. Primary Estimand Hierarchy

### Assessment

This is the biggest remaining design issue. The plan says there are **two primary estimands**:

1. E3 ordered contrast in excess invariance across task types.
2. E2 partial Spearman concordance.

But the actual success criteria for E3 require **multiple inequalities**:

- `direct - sentiment > 0`
- `sentiment - authority > 0`
- `sentiment - novelty > 0`

Then E4 adds a sham contrast, and the matched-format ablation is described as central to the claim. In other words, the paper's confirmatory content is richer than the stated "two-test primary family."

### Why this matters

Without a precise hierarchy, multiplicity is understated. "Ordered contrast" is doing too much work. It is not clear whether E3 is:

- one global test,
- three one-sided pairwise tests,
- a trend test plus pairwise follow-ups,
- or an intersection-union claim requiring all inequalities.

Those are not inferentially equivalent.

### Recommendation

Pre-specify one of the following:

**Option A: Global-primary, components-secondary**

- Primary E3 test:
  \[
  H_0: \mu_{\text{direct}} \le \mu_{\text{sentiment}} \ \text{or} \ \mu_{\text{sentiment}} \le \mu_{\text{decomp}}
  \]
  implemented through a single monotonic contrast / isotonic test statistic.
- Secondary confirmatory contrasts:
  - `direct - sentiment`
  - `sentiment - authority`
  - `sentiment - novelty`

**Option B: Closed testing / gatekeeping**

1. Test a single global E3 ordered-null.
2. Only if rejected, test the three pairwise one-sided contrasts.
3. Only if E3 passes, move to matched-format retention and sham falsification.
4. Treat E2 concordance as supporting rather than co-primary.

That would align the inferential family with the paper's narrative.

## 3. Success Criteria, Effect Sizes, and Power

### Assessment

The current thresholds are not quantitatively well grounded.

- `>= 0.05` sham gap is arbitrary.
- "Near-zero placebo" is not a statistical criterion.
- "Directionally identical" under matched-format is too weak.
- No pilot-based power or minimum detectable effect is provided for the primary E3 contrasts.

### Quantitative issue

For a paired cluster contrast \(D_g\), the approximate detectable effect is:

\[
\text{MDE} \approx (z_{1-\alpha^*} + z_{1-\beta}) \frac{\sigma_D}{\sqrt{G}}
\]

where \(G\) is the number of clusters and \(\sigma_D\) is the cross-cluster SD of the paired contrast.

With \(G \approx 1000\):

- if \(\sigma_D = 0.5\), MDE is roughly 0.04 to 0.05;
- if \(\sigma_D = 0.8\), MDE is roughly 0.07 to 0.08.

So a target gap of `0.05` is only reasonable if the paired contrast dispersion is fairly low. The plan currently assumes this without evidence.

### Recommendation

- Run a pilot on the frozen prompt set and estimate \(\sigma_D\) for:
  - `direct - sentiment`
  - `sentiment - authority`
  - `sentiment - novelty`
- Publish ex ante MDEs for the primary family.
- Replace "near-zero placebo" with an **equivalence test**:
  \[
  H_0: |\mu_{\text{placebo}}| \ge \delta_0
  \]
  for a pre-specified margin \(\delta_0\) such as 0.02 or 0.03.
- Replace "directionally identical" with a retained-effect criterion, e.g. matched-format contrast remains positive and retains at least a pre-specified fraction of the base contrast.

## 4. Generated-Regressor Problem

### Assessment

The plan **acknowledges** the generated-regressor issue, which is good. It does **not yet fully solve** it.

The current text says uncertainty will be propagated through cross-fitting and full-pipeline bootstrap. That is the correct direction, but the econometric object is still ambiguous:

- The contamination proxy \(C_i\) is partly a constructed measurement object, not a clean first-stage nuisance estimate.
- The orthogonalization step in E6 is a nuisance model.
- The second stage mixes ML prediction, rank IC, and a diagnostic interaction coefficient `theta`.

Cross-fitting alone does not make `theta` interpretable if the second stage is nonlinear or if tuning is done globally.

### Recommendation

- Treat E6 as a **predictive stability exercise**, not coefficient inference, unless the second stage is explicitly linear and fully specified.
- If `theta` is retained:
  - use **time-ordered cross-fitting**,
  - tune nuisance models **within folds**,
  - bootstrap the **entire pipeline**, including nuisance re-estimation and tuning.
- Make clear that cross-fitting addresses overfitting of nuisance steps; it does **not** identify causal leakage removal.

## 5. Temporal Decay and Data Snooping

### Assessment

The plan avoids the worst form of data snooping by not selecting cutoffs from the observed decay curve. That is good. But the temporal analysis is still not fully protected.

### Remaining concerns

- The smoother is not pre-specified: local regression vs penalized spline leaves room for researcher degrees of freedom.
- The benchmark is **stratified by time**, so the estimated decay curve is not automatically a population curve unless weighted back to the underlying corpus distribution.
- The "placebo frontier" is tied to a vendor model update date, not a verified training cutoff. This is acceptable as a descriptive freshness check, but not as a quasi-experimental untreated window.

### Recommendation

- Pre-specify:
  - one primary smoother,
  - its degrees of freedom / bandwidth,
  - one primary placebo window.
- Report both:
  - benchmark-weighted estimates, and
  - corpus-reweighted estimates using design weights.
- Add a stronger false-positive check using **synthetic post-boundary articles** or clearly fabricated fresh items, not only real post-2025 news.

## 6. Cross-Model Concordance: Is Partial Spearman the Right Choice?

### Assessment

Partial Spearman \(\rho\) is **acceptable as a descriptive summary**, but I would not make it the sole confirmatory concordance test.

Why:

- Excess invariance is likely discrete or heavily tied, especially if many outputs are classified in label mode.
- "Partial Spearman" is not uniquely defined in practice; different residualization procedures produce different answers.
- With strong ties and mixed discrete/continuous covariates, interpretation becomes fragile.

### Recommendation

Use partial Spearman as a reported summary, but add at least one sensitivity analysis:

- **Kendall's \(\tau_b\)** with tie correction,
- or a **rank-based semiparametric regression** of `EI` on `LAP` with controls,
- or within-stratum rank correlations (date/prominence/event-type strata) with meta-analytic aggregation.

Also expand the control set beyond length, date, and prominence. At minimum consider:

- event type,
- propagation size,
- collision-risk flag.

## 7. Identification Problems Not Fully Acknowledged

These are the main remaining identification threats.

### 7.1 Prompt-task bundle, not pure task semantics

Even with matched-format and sham controls, the estimand is still closer to a **prompt-task bundle effect** than a pure "task semantics" effect. That is fine, but it should be stated more bluntly.

### 7.2 Selection on rewriteability / QC pass

Cases that fail counterfactual generation or QC are replaced from reserve pools. That induces conditioning on a latent variable: being "rewriteable and QC-passable." If that propensity is correlated with leakage susceptibility, the benchmark estimand is not the corpus estimand.

### 7.3 Stratified-sample estimand versus population estimand

The benchmark is stratified and cell-filled. Unless design weights are used, the reported means are benchmark-weighted, not population-weighted.

### 7.4 Residual article salience confounding

In E2 and E6, omitted salience remains a real problem. Prominence alone is not enough. Propagation breadth, topic intensity, and event extremeness can drive both contamination proxies and true predictability.

### 7.5 Unknown vendor training / refresh process

The post-boundary placebo window is not genuinely untreated if the vendor model has undocumented rolling updates or retrieval augmentation. The current language still leans slightly too hard on the placebo interpretation.

## 8. Metrics Implementation Audit (`src/metrics.py`)

The implementation is not yet aligned with the inferential plan.

### 8.1 Confidence similarity is not scale-normalized

`confidence_invariance()` and `_confidence_similarity()` use:

\[
1 - |s_o - s_c|
\]

This only makes sense if the score lives on \([0,1]\). But the codebase also uses:

- scalar scores on `[-1, 1]`,
- confidence values on `[0, 100]`.

So the current fallback can be badly distorted. Correct normalization should be:

\[
1 - \frac{|s_o - s_c|}{R}
\]

where \(R\) is the range width (`2` for `[-1,1]`, `100` for `[0,100]`, `1` for probabilities).

### 8.2 `prediction_consistency()` silently accepts length mismatch

It zips the lists but divides by `len(orig_preds)`. If lengths differ, the metric is wrong and the failure is silent.

### 8.3 Cluster-level estimands are not implemented

The plan's primary metric is **mean cluster-level excess invariance** with paired cluster inference. But:

- `batch_excess_invariance()`
- `excess_invariance_by_task()`

simply average over observations/results. There is no cluster aggregation, no paired contrast construction, and no inferential wrapper.

### 8.4 `lap_score()` is under-integrated

`lap_score()` expects `list[float]`, but the client currently stores raw logprob objects from the API. The transformation from token logprob payloads to the exact bottom-`k%` statistic is not defined here, so the statistical object used in the proposal is not yet operationally pinned down in code.

## Specific Recommendations

1. Redefine the primary family so it matches the actual claim structure.
2. Use cluster-level paired randomization inference for E3/E4, not just clustered bootstrap.
3. Add pilot-based MDE calculations for the primary contrasts and placebo equivalence.
4. Make E2 supportive or add tie-robust concordance sensitivity checks.
5. Specify the full cross-fitting / bootstrap protocol for E6, or further demote `theta`.
6. Distinguish benchmark-weighted from population-weighted estimands.
7. Explicitly acknowledge selection on QC-passable rewrites.
8. Fix `src/metrics.py` before treating it as the operational definition of the paper's estimands.

## Overall Assessment

The design is now defensible as a **carefully bounded measurement study**. The main remaining work is inferential housekeeping: fully pre-specify the confirmatory family, justify quantitative thresholds, tighten the E6 pipeline, and align the code with the stated estimands. If those changes are made, the project can support a credible empirical paper. In its current form, the design is better than average for the space, but still short of econometric best practice.
