# BENCHMARK_PROPOSAL R1 Review — Stats Agent
**Date:** 2026-04-12
**Reviewer:** Codex (senior econometrician persona)
**Reasoning effort:** xhigh

---

# FinMem-Bench Statistical Review

## 1. Executive Verdict on Statistical Soundness

**Verdict: (b) fixable with significant revisions.**

As written, this is **not** a credible causal design for “natural memorization” in the benchmark arm. The proposal has four serious problems:

1. It never defines the target parameter. “Memorization” is a construct, not an estimand.
2. It treats `pre/post cutoff` as if it were training exposure. It is not. It is a noisy proxy with obvious time confounding.
3. It proposes cross-task, cross-model, cross-language, high-order interaction inference on a cell plan that is not powered for those claims.
4. It implicitly pools incomparable domains: Chinese CLS telegraphs, English news/filings, different market structures, different cutoffs, and different task metrics.

The **CPT positive-control program is the statistically strongest part of the project**. The benchmark can be good if you re-scope it as:

- a **calibrated descriptive benchmark** of leakage-sensitive behavior,
- with **construct validity anchored by CPT**,
- and with **causal claims restricted to the CPT intervention and, at most, exact-cutoff open-model local designs**.

If you insist on selling the benchmark itself as identifying the causal effect of natural pretraining exposure on memorization, it is **fatally flawed at the identification level**.

---

## 2. Estimand Definition

The proposal currently has no defined quantity of interest. That is not cosmetic. It kills sample-size planning, factor balancing, and multiplicity control.

### 2.1 Start with the outcome that is actually being measured

You need a fixed realized-outcome label first. For each case `i`, define:

```text
O_i = verified realized outcome for the target under a fixed rule
```

For finance, that cannot be “traceable source” in the abstract. It has to be something like:

```text
O_i = sign(benchmark-adjusted return over horizon H for the pre-specified target)
```

with `H`, benchmark, neutrality threshold, and target mapping fixed in advance. `company`, `sector`, and `index` probably need different outcome-construction rules. If they do, they should not be pooled without explicit standardization.

Then define the probe outcome:

```text
Y_i,t^FO = 1 if the model's response under false outcome moves toward the planted false outcome,
          relative to its original response, on task t
Y_i,t^NP = 1 if the model changes under a neutral paraphrase on task t
```

The proposal currently wants to use raw `fo_flip_hedged`. That is not enough, because flip rates depend on the model’s **original response distribution**. If one cell has more neutral originals, it mechanically has less room for “neutral retreat.” That is a design confound, not memorization.

A better task-level observed quantity is:

```text
psi_i,t = Y_i,t^FO - Y_i,t^NP
```

or, at the population level,

```text
Psi_t = E[Y_i,t^FO] - E[Y_i,t^NP]
```

That gives you **net false-outcome sensitivity above baseline task instability**. Without this normalization, cross-task comparisons are shaky because `fo_any_change` on authority is not on the same scale as `fo_flip_hedged` on impact.

### 2.2 The causal estimand you probably want

If the substantive question is “what is the effect of training exposure to the realized outcome on the probe?”, the estimand is:

```text
tau_nat(m,l,t) = E[ psi_i,m,l,t(A=1) - psi_i,m,l,t(A=0) ]
```

where:

- `A=1` means the model truly had outcome-bearing pretraining exposure for case `i`
- `A=0` means it did not
- `m` is model, `l` is language, `t` is task

This is the clean causal estimand. **Your benchmark does not identify it.**

### 2.3 The observational estimand you can actually identify

What your pre/post benchmark can estimate is:

```text
Delta_prepost(m,l,t,x) = E[psi | P=pre, X=x] - E[psi | P=post, X=x]
```

where `P` is pre/post cutoff and `X` is a vector of observed factors.

That is a **descriptive temporal contrast**, not a causal effect of exposure.

### 2.4 The CPT estimand you can identify

Your positive control does identify a causal quantity:

```text
tau_CPT(m,l,t) = E[ psi_i,m,l,t(Z=article+outcome) - psi_i,m,l,t(Z=article-only) ]
```

where `Z` is the controlled training intervention.

This is a **local causal effect of injected outcome memory on the probe**. It is the right construct-validity estimand.

### 2.5 The diagnostic-validity estimand

If the benchmark is supposed to detect latent memorization, you also need the measurement estimand:

```text
delta_diag(m,l,t) = E[psi | M=1] - E[psi | M=0]
```

where `M` is latent memorization / encoded outcome knowledge.

You do not observe `M`, which is why CPT matters. CPT does not estimate natural memorization prevalence. It calibrates whether the probe moves when memory is experimentally added.

**Bottom line:** before building anything, decide whether FinMem-Bench is estimating `tau_CPT`, `tau_nat`, `Delta_prepost`, or `delta_diag`. Right now it mixes all four.

---

## 3. Identification Strategy

### 3.1 Temporal proximity is not clean identification

`pre/post cutoff` is a **fuzzy exposure-opportunity proxy**, not treatment. The confounders are obvious:

- topic composition drift over time
- market regime changes
- source mix changes
- vocabulary/style drift
- different prevalence of policy/news/event types by period
- changing outcome verifiability by period
- different density of repeated or templated events by period
- closed-model post-training and refreshes
- multilingual exposure through translation or paraphrase

Your own pilot record already shows how fragile these associations are: DeepSeek produced the `impact_hedged` pattern; Qwen baseline did not; CFLS turned out to be comprehension, not memory; and factor imbalance generated Simpson’s paradox.

That is not what a clean causal design looks like.

### 3.2 Regression adjustment does not rescue this

Balancing or controlling for `anchor`, `direction`, `target_type`, `frequency`, and `credibility` does **not** solve unobserved time confounding. It helps comparability, but it does not convert `P=pre/post` into `A=exposed/unexposed`.

There is also no credible IV here. Publication date is not an instrument because it affects probe behavior through many channels besides training exposure.

### 3.3 RDiT is mostly not defensible here

A regression-discontinuity-in-time story would require:

- an exact cutoff,
- a sharp or at least strongly discontinuous jump in exposure probability at that cutoff,
- local continuity of potential outcomes absent exposure,
- no other discontinuities in the benchmark composition near the cutoff.

That is not true for closed models with approximate cutoffs. It is barely plausible for exact-cutoff open models, and even then only in a **narrow window** with:

- same source type,
- same task,
- same target type,
- local matching,
- placebo cutoffs,
- covariate continuity checks,
- and “first public timestamp” rather than just article publish date.

For DeepSeek and GPT-4o, the pre/post design should be **descriptive only**. For open models, maybe you can defend a local fuzzy-RDiT module, but only after major tightening.

### 3.4 Cross-lingual pooling is not identified

Chinese CLS telegraphs and English EDGAR/news are not the same data-generating process. Differences include:

- source genre
- article length and structure
- market microstructure
- event types
- outcome construction
- anchor behavior
- training-data prevalence

So no, you do **not** have one pooled cross-lingual estimand by default. You have **separate sub-studies**.

Formal pooling would require something like measurement invariance:

```text
E[psi | M=1, language=CN] - E[psi | M=0, language=CN]
=
E[psi | M=1, language=EN] - E[psi | M=0, language=EN]
```

That is a strong assumption and basically untestable here.

It gets worse: contamination can cross language barriers. A model can memorize translated or paraphrased versions of benchmark content, so CN and EN are not separate contamination universes. That is directly documented by Yao et al. (EMNLP 2024).

### 3.5 CPT is a causal anchor, but only for construct validity

The good news: `Arm 2 vs Arm 1` in your preregistered CPT design is close to a clean causal contrast. Same base model, same filler, same inference stack, same prompts, only the injected outcome differs. That is the right design for a positive control.

The bad news: it estimates **the effect of this CPT intervention on the probe**, not the effect of natural pretraining exposure in the wild. LoRA/CPT can also change:

- baseline calibration,
- neutrality propensity,
- decoding stability,
- JSON validity,
- token priors.

So CPT is **not** an unbiased estimate of natural memorization. It is a calibration experiment. That is enough. Use it for that.

### 3.6 FO generation is a genuine identification threat

You need an assumption like:

```text
F_i ⟂ O_i | X_i
```

except for the fact that `F_i` is false by construction.

Right now LLM-generated false outcomes do not satisfy that cleanly. The generator sees the article and may produce false outcomes whose plausibility, style, or lexical choices are correlated with the true outcome, target type, or source type.

That contaminates interpretation. A higher flip rate may reflect a more persuasive generator, not memory conflict.

You need to move to one of these:

- deterministic sign inversion from verified outcome with controlled templates
- matched magnitude bins and matched lexical length
- both bullish and bearish false outcomes generated for each case, with randomized assignment
- generator audits showing that true outcome is not predictable from the false outcome text alone

At minimum, run a blinded test: train a classifier on false-outcome text plus article metadata to predict the true outcome. If it beats chance, your FO generator is leaking structure.

---

## 4. Power and Design

### 4.1 The balance table is not power-based and is partly incoherent

The most basic problem: the proposal gives quota counts, not effect-size-driven power targets.

Worse, the “full 5-way cross” is arithmetically suspect. With the stated levels, even a 5-way cross of:

```text
period(2) × anchor(2) × frequency(3) × direction(2) × target_type(3)
```

has `72` cells. At `30` per cell, that is `2160` cases per language before adding `credibility`. Include credibility and you need `4320`.

So either the 5-way target is ambiguous or it is impossible.

### 4.2 Main period effect: Phase 4-sized effect

Using your Phase 4 headline effect for `impact_hedged`:

```text
p_pre  = 0.123
p_post = 0.068
OR     = 1.95
diff   = 0.0556
```

For a simple equal-size two-group comparison, the standard back-of-envelope sample size is:

```text
n per group ≈
[(1.96 * sqrt(2*pbar*(1-pbar)) + 0.84 * sqrt(p1*(1-p1) + p0*(1-p0)))^2] / (p1-p0)^2
```

This gives:

```text
n ≈ 426 per period group
```

So you need about **852 scorable cases per confirmatory comparison** to get 80% power for a Phase-4-sized effect at alpha 0.05.

Implications:

- `period × direction × anchor >= 100 per cell` is badly underpowered.
  Within a given `direction × anchor` stratum, that is `100 pre` vs `100 post`.
  Power is only about **0.28** for an OR around `1.95`.
- `direction × anchor >= 400 per cell` sounds large, but if period is balanced inside it, that is only `200 pre` vs `200 post`.
  Power is about **0.49**.
- If you have even a modest multiplicity correction, say alpha `0.005`, then `400 vs 400` only gives about **0.47** power.

So the current cell targets do **not** support confirmatory stratum-specific pre/post inference.

### 4.3 Three-way interaction: period × direction × anchor

Take the Phase 4 stratum rates as a rough guide:

```text
weak:   pre 0.167, post 0.071
strong: pre 0.088, post 0.065
```

The interaction on the risk-difference scale is:

```text
delta = (0.167 - 0.071) - (0.088 - 0.065) = 0.073
```

With equal `n` per cell, the standard error is roughly:

```text
SE ≈ sqrt( sum_j p_j(1-p_j) / n )
```

This implies:

- at `n = 100` per cell, power is only about **0.24**
- at `n = 200` per cell, power is about **0.42**
- you need roughly **510 per cell** for 80% power

So the proposed `>=100` per `period × direction × anchor` cell is nowhere close.

### 4.4 Four-way model × language × task × period interaction

First: **do not call this ANOVA**. The outcome is binary, rare-ish, repeated within case, and clustered across tasks/models. This needs mixed-effects logistic or GEE, not ANOVA.

Second: the power depends on what heterogeneity you actually want to detect.

If one cell reproduces the DeepSeek-sized period effect (`12.5% vs 6.8%`) and another shows no period effect (`6.8% vs 6.8%`), the interaction is about `5.6` percentage points. Ignoring within-case correlation, `1000 pre` and `1000 post` in each relevant cell gives roughly **0.91** power.

But that is the optimistic, wrong calculation. Your design has repeated outputs per case across models and tasks. With `12` repeated outputs per case and an intra-case correlation around `0.2–0.3`, the effective sample size can collapse by a factor of roughly `3.2–4.3`. Then power for that same interaction drops into the **0.64 to 0.50s** range.

So the conclusion is simple:

- **main effects:** 2000 per language is plenty
- **a small number of pre-specified interactions:** maybe
- **a full cartography of model × language × task × factor interactions:** no

### 4.5 “30 per finest cell” is statistically unserious for rare-event confirmatory analysis

At a flip rate between `6.8%` and `12.5%`, `30` cases per cell implies only about:

- `2.0` expected events at `6.8%`
- `3.8` expected events at `12.5%`

That is separation territory. If your confirmatory model needs penalized rare-event logit to stand up at the cell level, the confirmatory design is underbuilt. Use partial pooling for exploratory analysis, but do not pretend these cells support stable confirmatory interaction claims.

### 4.6 Effective N will be lower than the article count

Your candidate corpus has repeated event types and likely repeated event clusters. If you include multiple near-duplicate telegraphs about the same event, the unit of independence is not the article. It is the event cluster.

That means raw case count overstates information. If you do not cluster inference at the event level, your standard errors will be too small.

---

## 5. Inference Plan

The proposal needs a much harsher hierarchy.

### 5.1 Confirmatory vs exploratory

Right now the comparison space explodes immediately:

```text
3 tasks × 4 conditions × 4 models × 2 languages = 96 cells
```

Before factors.

At alpha `0.05`, that implies about **4.8 expected false positives** under the global null. The family-wise error rate is about:

```text
1 - 0.95^96 ≈ 0.993
```

BH is fine for exploration. It is not enough for strong confirmatory claims across this many tests.

### 5.2 What should be primary

The cleanest preregistered structure is:

- **Primary family A:** CPT construct validity only
  - Qwen CN: `Arm 2 vs Arm 1` on one primary metric
  - Llama EN: same
  - Holm across the 2 tests
- **Primary family B:** only if you can defend exact-cutoff open-model observational design
  - one task only: `impact`
  - one contrast only: pre vs post
  - language-specific, not pooled by default
  - Holm across languages if both are confirmatory

Everything else should be secondary or exploratory.

### 5.3 What should not be primary

Do **not** make these confirmatory:

- SR results
- neutral paraphrase results
- authority-task pre/post effects
- closed-model cutoff analyses
- high-order factor interactions
- cross-model pooled “overall memorization” effects

Those are descriptive or exploratory.

### 5.4 Use the right model

For benchmark inference:

- paired within-case comparisons where possible
- cluster-robust SEs or random effects for `case_id`
- cluster at `event_cluster` or `source_event` if repeated events exist
- no ANOVA
- no large fixed-effect interaction grids as confirmatory rare-event models

For exploratory factor maps, use a hierarchical logistic model with partial pooling. That is the only sane way to estimate a sparse high-dimensional structure.

### 5.5 Missing outputs and parse failures

Do not silently drop invalid outputs and call the remainder “the analysis sample.” Invalidity is model behavior.

For the primary benchmark estimand, either:

- code invalid output as failure/non-success in an intention-to-evaluate analysis, or
- make validity a co-primary QC endpoint and do per-protocol as sensitivity only

If invalidity differs by task, condition, or factor cell, listwise deletion will bias you.

### 5.6 Stopping rules and benchmark overfitting

You also need a real benchmark protocol:

- freeze sampling and annotation before model evaluation
- have a dev split for pipeline tuning and a locked test split for confirmatory evaluation
- if the benchmark will be public, keep the answer key hidden or use a closed test / answer-obfuscation mechanism

MMLU-CF and Ishida et al. are directly relevant here. An open benchmark with public answers is a short-lived benchmark.

---

## 6. Specific Fixes, Prioritized

### Must-have before building

- **Define the population of inference.** It is not “financial news.” It is “single-target, outcome-verifiable events under a fixed outcome-construction rule.”
- **Define the estimands in math.** At minimum: `tau_CPT`, `Delta_prepost`, and whether you are using raw `fo_flip` or net `FO - NP`.
- **Fix the outcome label.** Specify exact horizon, benchmark adjustment, neutrality threshold, and separate rules by target type if needed.
- **Stop treating pre/post as causal treatment.** For closed models it is descriptive only.
- **Collapse confirmatory ambition.** One primary probe family, one primary task, at most one or two confirmatory factors.
- **Drop the 5-way confirmatory fantasy.** `30 per cell` is exploratory only.
- **Use matched/constrained sampling, not quota balancing alone.** Require covariate-balance diagnostics such as standardized mean differences `< 0.1`.
- **Sample at the event-cluster level or cluster inference there.**
- **Task-normalize the outcome.** Compare FO behavior net of neutral-paraphrase instability, or condition explicitly on original non-neutral output.
- **Make FO generation deterministic or heavily audited.** Do not trust free-form LLM-generated false outcomes as if they were exogenous.
- **Treat CN and EN as separate modules.** No pooled causal estimand unless you can defend measurement invariance.
- **Create dev/test separation.** Do not tune prompts and then publish test results on the same cases.

### Should-have

- **Local-window exact-cutoff design** for any observational causal claim on open models.
- **Placebo cutoffs** to test whether “period effects” are just time trends.
- **A sham CPT arm** with lexically matched but outcome-irrelevant additions.
- **Factor reliability thresholds** for anchor/credibility/frequency before using them confirmatorily.
- **Continuous frequency score in analysis.** Bin only for sampling, not for final inference.
- **Source harmonization.** Do not use EDGAR as the English analogue of CLS telegraphs unless you explicitly want a different source-type module.
- **A small locked pilot first**: 200–300 cases per language, exact frozen generator, open-model calibration, then scale.

### Nice-to-have

- **Hidden-answer or ceilinged benchmark design** for longevity.
- **Periodic benchmark refreshes** rather than one static public release.
- **Exploratory Bayesian partial-pooling factor maps** after the confirmatory core is done.

---

## Bottom Line

The proposal is worth saving, but only if you stop asking one dataset to do three incompatible jobs.

It can be:

- a **good benchmark artifact**,
- a **good measurement paper**,
- and a **good CPT construct-validity paper**.

It cannot, as currently written, be a clean causal study of natural training-data memorization across models, languages, tasks, and factors.

The right move is not “build 4000 cases and hope balance fixes it.” The right move is:

1. lock the estimand,
2. shrink the confirmatory claim set,
3. calibrate the probe with CPT,
4. treat benchmark pre/post contrasts as descriptive unless exact-cutoff identification is real,
5. and only then scale.

## Sources

Internal project docs consulted:
- `docs/PREREGISTRATION.md`
- `docs/PILOT_RESULTS.md`
- `docs/DECISION_20260411_post_amber.md`
- `docs/FIRTH_DECISION.md`

External sources:
- Lopez-Lira et al., 2025, “The Memorization Problem: Can We Trust LLMs’ Economic Forecasts?” https://arxiv.org/abs/2504.14765
- Wu et al., 2025, “AntiLeakBench” https://aclanthology.org/2025.acl-long.901/
- Zhao et al., 2025, “MMLU-CF” https://aclanthology.org/2025.acl-long.656/
- Yao et al., 2024, “Data Contamination Can Cross Language Barriers” https://aclanthology.org/2024.emnlp-main.990/
- Ishida et al., 2025, “How Can I Publish My LLM Benchmark Without Giving the True Answers Away?” https://arxiv.org/abs/2505.18102
