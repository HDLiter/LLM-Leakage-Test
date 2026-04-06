# Quant Review of the Leakage Experiment Plan

## Score

**6.8 / 10**

**Verdict:** Promising measurement paper, not yet a production-changing quant validation plan.

If you execute Blocks 1-4 well, I would take the leakage-ordering result seriously and I would probably add a similar audit to an LLM signal approval process. I would **not** let the current E6 design change model selection, portfolio construction, or capital allocation decisions. The quant-facing endpoint is still too weak and too thin.

## Bottom Line

The core idea is good: fixed-input paired comparisons across task families, with matched-format and sham controls, is exactly the right way to test whether task design changes measured contamination exposure. That part is worth doing.

The weak point is the bridge from “interesting leakage measurement result” to “this changes how I run an A-share signal pipeline.” Right now that bridge is not strong enough. The benchmark construction is directionally right but still has several places where curation choices can dominate the result, and the downstream XGBoost section is not designed tightly enough to say anything operational about tradable alpha.

## What Is Strong

- The paper has a real mechanism question, not just a model horse race. Comparing direct prediction, sentiment, authority, and novelty on the same `(article, target)` inputs is the right design.
- Matched-format prompts and sham decomposition are the two controls a skeptical reviewer will ask for. Keeping them central is correct.
- Clustering propagated same-day rewrites is necessary. Reporting cluster counts rather than raw article counts is also correct.
- Treating E6 as supplementary is the right instinct. The main paper can stand on E1-E4 if those are clean.
- The plan correctly recognizes that benchmark quality, not compute, is the binding constraint.

## Major Weaknesses

### 1. The current repo state does not yet support the claimed M0/M1 readiness

There is a real execution gap between the written plan and the code/data you currently have.

- `R001` is marked done on an `84`-case seed set in `refine-logs/EXPERIMENT_TRACKER.md:5`, but `data/seed/test_cases.json` currently ends at `tc_042` and contains **42** cases, not 84.
- The frozen v2 prompts are target-conditioned everywhere (`config/prompts/task_prompts.yaml:78`, `131`, `176`, `230`, `274`, `390`, `622`), but the smoke harness still calls `render_user_prompt(task_id, article)` without `target` or `target_type` in `tests/smoke_test_prompts.py:248`.
- The current seed file has no `target` or `target_type` fields at all.
- The seed file also has no 2025 or 2026 cases, so it cannot validate the placebo/freshness logic that the main plan relies on.
- The loader risk called out in the plan is real: `src/news_loader.py:48-68` still assumes an older `ctime`-based raw format and hardcodes `category="macro"`.

This means M0 should be reopened. I would not treat the benchmark build as execution-ready yet.

### 2. The benchmark construction is plausible for a paper, but still not clean enough for strong quant interpretation

The main risk is not random noise. It is **systematic curation bias**.

- The single-target linking hierarchy is too aggressive for policy and macro news. A lot of A-share news is genuinely multi-target or basket-level. Forcing one benchmark target can create fake precision.
- The rule “prefer company if a company candidate passes threshold” will tend to over-individualize broad policy news.
- Using a `prominence_proxy_company` for sector/index targets (`refine-logs/EXPERIMENT_PLAN.md:165`) is economically wrong. Sector and index items should not inherit cap tier from whichever company happened to score highest in the text.
- Same-company same-day clustering (`refine-logs/EXPERIMENT_PLAN.md:173`) is acceptable as a first pass, but it will merge distinct events on busy days. A `collision_risk` flag is useful, but “keep the modal fingerprint article” is still throwing away economically distinct information.
- The plan does not yet include a serious **answerability / coverage** screen. On 90-120 character CLS telegraphs, authority and novelty prompts will often default to `unclear`. Lower measured leakage is not useful if it is bought by lower coverage and lower cross-sectional dispersion.

My view: the benchmark can support a bounded measurement claim if you fix target scope and answerability. It does not yet support strong claims about production signal quality.

### 3. The current metric implementation is not aligned with the task design

This is a bigger issue than it looks.

- `src/metrics.py:178-246` extracts a single label if present; otherwise it falls back to confidence similarity.
- That works for direct direction tasks.
- It does **not** naturally score multi-field authority and novelty outputs the way the plan describes. Those tasks have multiple edited and unchanged fields, but the generic metric does not yet encode field-level expected-change logic.

If you leave this as-is, decomposition tasks risk being judged on confidence stability rather than semantic field behavior. That would materially weaken E3.

You need task-family-specific excess invariance:

- edited-field change rate
- unchanged-field stability rate
- abstention / `unclear` rate
- a coverage-adjusted or entropy-adjusted version of the primary score

### 4. E6 is not well designed yet from a quant perspective

This is the main reason my score is below 7.

The current E6 setup in `refine-logs/EXPERIMENT_PLAN.md:84-87` and `docs/RESEARCH_PROPOSAL.md:118` is too thin to answer the question a fund actually cares about: *would leakage distort live model selection or portfolio construction?*

Problems:

- A 1,000-case balanced benchmark is too small for a serious XGBoost exercise once you enforce time splits, target filtering, and tradability rules.
- The target set mixes company, sector, and index objects. Those are not directly comparable return labels and not equally tradable.
- There is no explicit timestamp-to-trade protocol: next tick vs next open, lunch break handling, after-close news, weekend carry, halts, ST names, T+1, and price-limit locks all matter in A-shares.
- There is no portfolio construction rule: long-only vs market-neutral, universe, liquidity filter, sector neutrality, turnover control, and costs are unspecified.
- There is no strong baseline. A quant reviewer will ask whether the leakage-adjusted LLM features beat simple non-LLM baselines, not just whether raw beats orthogonalized.
- `decomposed_impact.*` is reserved for E6 only and is excluded from the counterfactual rewrite catalog (`config/prompts/README.md:42`, `113`; `refine-logs/EXPERIMENT_PLAN.md:28`). That means some E6 features are not audited by the same leakage machinery as the main paper.

As written, E6 is more “appendix color” than “economic validation.”

### 5. Statistical power is adequate for the main paired claim, but weak for the rest

For the main E3 ordering on 1,000 paired clusters, power is probably fine. With paired comparisons, you should be able to see a real 3-5 percentage point gap in excess invariance if it exists.

That is **not** true for:

- 72 individual cells
- most E5 subgroup stories
- the placebo frontier if 2026 cases are sparse
- any meaningful E6 holdout comparison after tradability filters

The current temporal matrix is especially problematic because `2025+` is pooled into one bin for sampling, while the placebo claim is specifically about `2026-01-01` to `2026-02-23`. If you do not explicitly oversample the 2026 frontier slice, you can end up with a nice-looking matrix and an underpowered placebo.

## Direct Answers to the Five Questions

### 1. Is the benchmark construction pipeline realistic and clean enough?

**Partly.** It is realistic enough to produce a publishable benchmark if you tighten target scope, answerability screening, and field-level scoring. It is **not** yet clean enough to support strong finance-facing interpretation.

The biggest fixes:

- separate target scopes instead of forcing everything into one target object
- remove proxy-company prominence for sector/index items
- add answerability / coverage diagnostics before freezing the sample
- use field-aware metrics for decomposition tasks

### 2. Are the economic endpoints and downstream validation well designed?

**No.**

E6 is the weak link. It is underpowered, underspecified on tradability, and too disconnected from the audited feature families. If you want a result that would actually change pipeline validation, the correct finance endpoint is not “raw vs orthogonalized XGBoost on 1,000 benchmark rows.” It is one of:

- a rolling fresh-holdout portfolio test with explicit execution and costs
- a model-selection distortion test: which task family wins on contaminated history vs freshest holdout
- a larger production-weighted company-news panel scored with a frozen feature set

### 3. Will the sampling matrix and stratification give enough power for the claims?

**For the main paired claim, yes. For most secondary claims, no.**

- `1000` paired clusters is enough for E3 if the effect is not tiny.
- `13-17` cases per cell is not enough for cell-level inference.
- `4-5` anchor items per cell is useful for audit coverage, not for strong QC inference.
- `2025+` as one pooled bin is not enough for a clean 2026 placebo unless you force a minimum frontier count.

### 4. Are there practical quant concerns the plan misses?

Yes.

- tradability: T+1, price limits, halts, liquidity, after-hours timing
- coverage: lower leakage is not useful if the task produces many `unclear` labels
- signal dispersion: you need cross-sectional spread, not just lower contamination
- baselines: compare against non-LLM and simpler structured baselines
- production weighting: balanced benchmark composition is not the same as real event flow
- model-selection distortion: this matters more than regression coefficients
- data snooping: do not use the same benchmark to shape the task story and then claim downstream economic validation without a genuinely fresh panel

### 5. Is the 72-cell matrix overkill or justified?

**As a hard exact-fill requirement, mostly overkill. As an audit scaffold, defensible.**

I would not spend benchmark capital forcing perfect Tier2 fill in every one of 72 cells. That creates reserve-pool and backfill bias toward “easy” cases and burns time that would be better spent on:

- explicit 2026 frontier oversampling
- stronger target-link audits
- answerability screening
- a company-only tradable downstream panel

My recommendation is to keep the 72-cell structure for bookkeeping and reporting, but relax exact Tier2 fill if needed and use post-stratification weights in analysis.

## Specific Recommendations

### Must fix before running the main paper

1. Reopen M0.
   - Rebuild the seed set so it includes explicit `target` and `target_type`, and add 2026 frontier cases.
   - Rerun frozen prompt smoke on the actual target-conditioned schema.

2. Rewrite the primary metric for decomposed tasks.
   - Score edited-field flips and unchanged-field preservation explicitly.
   - Report abstention / `unclear` rates by task.
   - Do not let authority/novelty E3 rest on confidence similarity.

3. Add an answerability / coverage gate.
   - Before final freeze, estimate how often each task family is text-grounded on the sampled articles.
   - Report coverage-adjusted leakage, not just raw leakage.

4. Split target universes.
   - Company, sector, and index targets should be analyzed separately.
   - For E6, restrict the main result to a company-only tradable universe.

5. Replace proxy-company prominence for sector/index items.
   - Use target-type-specific prominence or liquidity measures.
   - If you cannot define a sensible measure, drop sector/index items from prominence-stratified claims.

6. Add a dedicated 2026 frontier stratum.
   - Do not hide the placebo window inside `2025+`.
   - Force a minimum fresh-item count.

### Should fix if you want real quant relevance

7. Redesign E6 around a production-weighted panel, not the balanced benchmark.
   - Keep CLS-Leak for leakage measurement.
   - Use a larger, rolling, tradable company-news panel for downstream validation.

8. Make the finance endpoint “model-selection distortion,” not just “orthogonalized XGBoost.”
   - Which task family would you pick using 2020-2024?
   - Which one survives on the freshest 2026 holdout after costs?

9. Specify the execution protocol.
   - timestamp-to-trade rule
   - T+1 and price-limit handling
   - halted/ST filters
   - liquidity floor
   - cost model
   - portfolio formation rule

10. Add strong baselines.
    - non-LLM event/category baseline
    - simple linear/ridge model baseline
    - current production feature baseline if available

11. Align E6 features with audited features.
    - If `decomposed_impact.*` goes into the downstream model, audit it too or clearly separate it from the main leakage story.

## What Would Actually Change My Pipeline

If Blocks 1-4 succeed after the fixes above, I would change validation practice in three ways:

- require counterfactual leakage audits before approving any new LLM task family
- require a fresh-holdout leakage placebo slice near the model frontier
- treat decomposed, text-grounded tasks as preferable **only if** they preserve enough coverage and dispersion

What I would **not** do from the current plan is change portfolio capital allocation based on E6. That part is not yet designed tightly enough.

## Final View

This is close to a good benchmark-and-measurement paper. It is not yet close to a strong quant validation paper.

The main result can matter for a systematic equity pipeline, but only as a **validation control** unless you rebuild E6 around investability, coverage, and model-selection distortion. Right now the plan is good enough to tell me whether a task family is suspicious. It is not yet good enough to tell me whether a signal family is deployable.
