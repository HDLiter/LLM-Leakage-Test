# BENCHMARK_PROPOSAL R1 Review — Quant Agent
**Date:** 2026-04-12
**Reviewer:** Codex (senior quantitative researcher persona)
**Reasoning effort:** xhigh

---

## 1. Executive verdict
Go with major changes. As written, this is worth 2-3 months only if you want an EMNLP-style benchmark paper; it is not yet worth 2-3 months as a production-quant validation program. The fatal gap is that it measures article-level leakage proxies, not whether contamination changes signal ranking, model selection, sizing, or out-of-sample decay on tradeable names. A PM will say: “interesting, but does this proxy load on fake alpha?” If you add a minimal contamination-to-alpha track, make the outcome definition point-in-time and tradeable, and stop forcing CN/EN into one pooled story, the work is justified. Otherwise it stays academically interesting and operationally weak.

## 2. What the proposal gets right (from quant lens)
- The diagnosis of the current 606-case set is correct: missing verified outcomes, imbalance, and tiny crossed cells are structural defects, not cleanup items.
- Requiring verified outcomes and killing generic false-outcome probes is the right direction.
- Same-article different-task contrasts are useful. They map to a real production question: which prompt family is unsafe as a backtest primitive.
- CPT on open models is the right causal anchor. Without a calibrated positive control, the rest is just pattern description.
- The proposal is correctly pivoting away from “CFLS proves leakage” toward “what exactly are these probes measuring?”

## 3. Critical gaps and risks (ranked by severity)
1. The proposal still does not define the production estimand.
What is being estimated: article memorization, signal contamination, or model-selection distortion? Those are not the same. A PM does not care that a model “knows” an old outcome if the contamination does not change cross-sectional ranks, confidence, or sizing after normalization. The real production failure is that contaminated tasks win historical bake-offs and then die live. That is the attack a skeptical PM and a top finance reviewer will both use: this is a proxy benchmark that never shows the proxy maps to fake alpha. Recent finance-facing work is already pushing the bar in that direction, not toward more item-level probing alone: [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322), [He et al. 2025](https://arxiv.org/abs/2502.21206), [Lopez-Lira et al. 2025](https://arxiv.org/abs/2504.14765), [Zhang et al. 2026](https://arxiv.org/abs/2602.17234).

2. “Verified outcome” is economically underspecified.
“Direction + magnitude + traceable source” is not enough. You need exact outcome horizons and trade timing: next open, intraday to close, close-to-open, open-to-open 1d, open-to-open 3d; market- or sector-adjusted abnormal return; whether the name was halted, limit-up/down, ST, illiquid, or untradeable; and whether the target is a company, sector, or index. Right now the proposal mixes objects with different execution mechanics and different meanings of “outcome.” A finance reviewer will kill this immediately because the dependent variable is not point-in-time operationalized.

3. The temporal design is too coarse to separate different leakage channels.
Binary pre/post cutoff is not enough. You need to distinguish at least three things: the model saw the article, the model saw later narratives about the event, and the model saw the realized stock move or recap discussion weeks later. Those are different contamination paths. You also need outcome-realization lag. A one-day return on a company earnings miss is not the same object as a multi-day policy reaction or sector narrative drift. With closed models and approximate cutoffs, binary labeling becomes even weaker. As proposed, “pre” will mix article memory, consensus memory, and ex-post narrative memory.

4. The factor taxonomy is missing first-order market-structure variables, and some current factors are not first-order.
From a production lens, the dealbreakers if omitted are: tradability/liquidity, market-cap tier, time-of-day bucket, outcome horizon, realized abnormal-return magnitude, company/sector/index separation, and expectedness/surprise. Event rarity matters, but it is not the same as corpus frequency. Source credibility is fine as a task attribute or annotation field; it is not a top-level sampling axis for leakage detectability. If you omit the market-structure fields, you will end up with a beautifully balanced benchmark over economically mismatched cases.

5. Anchor strength and corpus frequency are not yet clean exposure proxies.
The current anchor rubric measures textual identifiability. That is not the same as training exposure, economic salience, or outcome memorization risk. Likewise, frequency computed on CLS near-duplicates is only one slice of exposure and can be confounded by calendar mechanics, repeated templates, and entity salience. You need at least three separate constructs: textual retrieval anchor, event-family template density, and entity salience/coverage. Keep them continuous, then bin for reporting. If you force strong/weak and singleton/periodic/frequent up front, you will hard-code noisy labels into the benchmark.

6. Cross-lingual parity is likely a distraction in v1.
CN CLS telegraphs and EN EDGAR plus Yahoo are not the same object. Different disclosure regimes, timing, microstructure, investor base, price-limit rules, and news plumbing mean “matched factors” can be surface-level only. Cross-lingual becomes valuable only as a replication across two market-specific benchmarks with a shared metadata schema, not as one pooled benchmark story. If you force parity too early, you burn half the budget proving weak comparability.

7. The scale is the wrong shape.
`2000 CN + 2000 EN` sounds large and is still the wrong answer. It is too expensive if every case needs deep audit and verified outcomes, and still too small once you add the factors that actually matter. The right design is barbell, not monolithic: a smaller deeply audited core for identification and a larger shallow panel for production realism and alpha-decay checks. Otherwise you will spend annotation budget on balanced cells instead of on the one thing that matters: whether contamination changes the signal you would actually trade.

## 4. Proposed additions or redesigns (concrete, implementable)
1. Add a minimal contamination-to-alpha track.
Make a company-only tradable panel the production core. For each case, store exact `publish_ts`, `ticker`, `exchange`, `news_time_bucket`, and point-in-time returns for `close_to_open`, `open_to_close`, `open_to_open_1d`, and `open_to_open_3d`, all market- or sector-adjusted. Score frozen model outputs from each task family and report daily rank IC, hit rate, and a simple top-minus-bottom spread after basic liquidity and sector controls. The key estimand is model-selection distortion: which task family wins on contaminated history and which survives on fresh holdout.

2. Freeze a real case schema.
At minimum add `target_scope`, `is_tradeable`, `market_cap_bucket`, `ADV20_bucket`, `halt_flag`, `limit_hit_flag`, `publish_ts`, `first_trade_ts`, `event_type`, `surprise_proxy`, `realized_ar_1d`, `realized_ar_3d`, `outcome_realization_lag_days`, `days_to_cutoff`, `followup_coverage_7d`, and `entity_salience_pre`. Without these fields, you cannot map benchmark findings to live pipeline relevance.

3. Replace binary exposure factors with continuous ones.
For temporal exposure, store `days_to_train_cutoff` and `days_to_first_followup_narrative`. For frequency, compute `near_duplicate_count_pre`, `event_family_count_90d`, `bidirectional_family_ratio`, and `entity_coverage_count_365d`. For anchor, split textual retrieval cues from salience cues: `locator_score` and `coverage_score`. Analyze them continuously or in quantile bins. Do not bake coarse bins into the dataset as the primitive.

4. Split the benchmark into modules.
Module A should be CN single-name tradable news. Module B can be CN sector/index/policy cases if you still want them. Module C can be EN single-name if you can source point-in-time items with comparable fields. Do not average across modules. Cross-lingual should be replication, not pooling.

5. Use a barbell sample design.
Deep-audit core: roughly 600-800 CN company cases with verified outcomes, surprise metadata, continuous exposure features, and CPT-compatible controls. If EN stays, keep it smaller, maybe 400-600. Separate shallow panel: 5K-10K company news items with exact timestamps and returns for the contamination-to-alpha track. This gives you enough depth for calibration and enough breadth for model-selection distortion.

6. Add surprise and economic effect as first-class fields.
For earnings and structured events, store actual vs consensus if available. For unstructured cases, use a defensible proxy such as prior template density, prior entity event frequency, or analyst/news expectation tags. Also store realized abnormal-return magnitude buckets. A memorized sign on a 20 bps move is not the same production problem as a memorized sign on a 4 sigma move.

7. Calibrate the benchmark with dose-controlled CPT.
Use Qwen/Llama CPT arms with `0/1/2/5` exposure doses and separate `article only`, `article + real outcome`, and `article + false outcome`. This gives you a contamination-response curve. Then you can say more than “metric moves”; you can estimate contamination-equivalent dose. That is far more interpretable for a quant audience.

8. Add one decision-critical claim track instead of more benchmark ornaments.
Require the model to state 1-3 claims supporting its prediction, then label whether each claim was available at the article timestamp. This is closer to the actual production concern than more masking variants. The proposal in [All Leaks Count, Some Count More](https://arxiv.org/abs/2602.17234) is directionally relevant here: not all leakage matters equally; decision-driving leakage is what matters.

## 5. Open questions the proposal didn't ask but should have
1. What exact decision in the signal-approval process will this benchmark change: prompt approval, task-family selection, model selection, sizing caps, or only research hygiene?
2. What exact execution rule defines the “verified outcome” for each case, and how does that rule change across intraday, post-close, weekend, halted, and price-limit events?
3. What fraction of the final benchmark is actually tradeable after liquidity, halt, and microstructure filters?
4. How will you penalize low-leakage tasks that achieve cleanliness by collapsing to `neutral`, `unclear`, or low-dispersion outputs?
5. How will you validate the exposure proxies themselves: against CPT dose-response, white-box familiarity, cross-model disagreement, or fresh-holdout decay?
6. If open-model CPT calibration and closed-model benchmark behavior disagree, which one governs the paper’s claim and the production recommendation?

## 6. Recommended priority actions for next round
1. Decide whether this is a benchmark paper or a production contamination-validation paper. If production relevance is real, add the company-only contamination-to-alpha track now.
2. Freeze the point-in-time outcome protocol and tradability schema before collecting more cases.
3. Replace `pre/post cutoff`, `anchor strength`, and `corpus frequency` as coarse primitives with continuous exposure metadata plus a CPT calibration plan.
4. Decide scope. My recommendation is CN-first core, EN as a separate companion only if you can source comparable single-name point-in-time events.
5. Reallocate sample budget to a barbell design and demote masking/multi-method compatibility extras until the alpha link and positive-control calibration are in place.
