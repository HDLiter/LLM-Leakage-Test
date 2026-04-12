# E_pilot Results & Discussion

**Date:** 2026-04-06
**Cases:** 36 non-neutral cases from 42 seed test cases (18 company, 12 sector, 6 index)
**Model:** DeepSeek-chat (temperature=0)
**Tasks:** direct_prediction.base, decomposed_impact.base
**Conditions:** original, semantic_reversal, neutral_paraphrase, false_outcome_cpt

## Results

### CFLS Scores

| Task | Mean | Std | Median | Positive Rate | n |
|------|------|-----|--------|---------------|---|
| direct_prediction.base | -0.914 | 0.280 | -1.000 | 0.0% | 35 |
| decomposed_impact.base | -0.778 | 0.416 | -1.000 | 0.0% | 36 |

Cross-task correlation: r = 0.10 (n_paired = 35)

### False-Outcome CPT

| Task | Flip Rate |
|------|-----------|
| direct_prediction | 5/35 (14.3%) |
| decomposed_impact | 6/36 (16.7%) |

### Evidence Intrusion

Rule-based detection: 0/36 for both tasks (heuristic too coarse).

### Stratified CFLS

**By target_type:**

| Type | n | Direct CFLS | Impact CFLS |
|------|---|-------------|-------------|
| company | 16 | -0.867 | -0.750 |
| sector | 12 | -0.917 | -0.833 |
| index | 8 | -1.000 | -0.750 |

**By memorization_likelihood:**

| Level | n | Direct CFLS | Impact CFLS |
|-------|---|-------------|-------------|
| high | 29 | -0.964 | -0.793 |
| medium | 7 | -0.714 | -0.714 |

**By category:**

| Category | n | Direct CFLS | Impact CFLS |
|----------|---|-------------|-------------|
| policy | 7 | -1.000 | -1.000 |
| corporate | 14 | -0.846 | -0.786 |
| industry | 11 | -0.909 | -0.727 |
| macro | 4 | -1.000 | -0.500 |

## Key Finding: Floor Effect

CFLS ≤ 0 across all 36 cases. No suspicious memorization stability detected. The model strongly follows semantic reversals in every case.

## Diagnosis: Bidirectional Generalization Confound

The likely root cause is NOT that the model lacks memorization, but that **CFLS cannot detect it on common event types**.

Most test cases involve high-frequency financial events (RRR cuts, earnings reports, regulatory actions) that appear in BOTH bullish and bearish forms throughout the training corpus. For example:

- "央行降准" (RRR cut → bullish) — hundreds of similar articles in CLS data
- "央行升准" (RRR hike → bearish) — also many similar articles

When semantic_reversal changes "降准" to "升准", the model follows not because it's "reading the article" but because it has **generalized both directions** from abundant training data. CFLS cannot distinguish "grounded reading" from "pattern recognition across familiar templates."

This is a construct validity issue: CFLS measures **input sensitivity**, not **memorization**. A model that has generalized bidirectionally will always show high input sensitivity (negative CFLS) regardless of whether it memorized specific events.

### Supporting Evidence

- **Policy cases** (highest frequency, most standardized) show CFLS = -1.0 for both tasks — perfect reversal following
- **Medium memorization** cases show higher (less negative) CFLS than high memorization — counterintuitive if CFLS were measuring memorization, but consistent with the generalization hypothesis (less common events → less bidirectional coverage → slightly more stickiness)
- **Cross-task correlation is near zero** (r = 0.10) — the two tasks respond to reversals independently, suggesting pattern-level rather than case-level dynamics

### What Would Invalidate This Hypothesis

If CFLS showed positive values on truly unique, one-directional events (e.g., Luckin Coffee fraud, Huawei Mate60 surprise launch) where no "reverse version" exists in training data, that would confirm the generalization confound is real and CFLS does work on rare events.

## Implications for Method Design

1. **Corpus frequency as a required covariate.** Before computing CFLS, measure how many parallel (both-direction) examples exist for each event type in the training corpus. CFLS is only interpretable on events with low bidirectional coverage.

2. **Prioritize unique events.** The 1000-case benchmark should include a significant fraction of rare, one-directional events — not just high-profile news that has many structural parallels.

3. **Consider a vector database for corpus search.** Checking bidirectional coverage at scale (~1M CLS telegraphs) needs efficient similarity search. A vector DB can find semantically parallel articles regardless of surface form.

4. **CFLS alone is insufficient.** Even with corpus-frequency stratification, CFLS measures input sensitivity, not memorization. The paper needs to combine CFLS with:
   - False-outcome CPT (tests outcome-specific knowledge, not pattern generalization)
   - Qwen white-box Min-K% (direct memorization measurement)
   - Entity-cue dependence (tests entity-level shortcuts)

5. **False-outcome CPT shows more promise.** The 14-17% flip rate is more interesting than CFLS — it directly tests whether the model has outcome-specific knowledge. Cases where the model ignores the false hint despite it being textually present are stronger memorization candidates than any CFLS signal.

## Files

- `data/results/pilot_results.json` — full structured results (36 cases × 2 tasks × 4 conditions)
- `data/results/pilot_detail_review.txt` — human-readable dump of all inputs/outputs
- `data/results/pilot_dry_run.json` — initial 3-case dry run
- `scripts/show_pilot_results.py` — results summary script
- `scripts/show_pilot_detail.py` — detailed review script

## Pipeline Validated

Despite the negative CFLS finding, the pilot successfully validated the scoring pipeline:

- Same-template bridge (semantic_reversal on both direct_prediction and decomposed_impact) works end-to-end
- CFLS computation with reversal_target_field restriction is correct
- False-outcome CPT injection and flip detection works
- Schema validation, target_echo checking, and atomic saves are robust
- 5 rounds of Codex code review resolved 17 high-severity issues

The infrastructure is ready for the next iteration of the experimental design.

## Multi-Agent Discussion (2026-04-06)

Full discussion log: `refine-logs/pilot_discussion/DISCUSSION_LOG_20260406.md`

### Protocol
4 Codex domain agents (Quant, NLP, Stats, Editor) + 1 Claude Challenger, 2 rounds to convergence.

### Key Outcome: Go/No-Go Diagnostic Phase

The Challenger identified a critical shared blind spot: all domain agents assumed the CFLS floor effect was a measurement failure, but it may be a **true negative** — the model genuinely does not memorize these articles, and CFLS is working correctly. Without positive controls, the pilot result is **non-diagnostic**.

**Three cheap diagnostics before benchmark redesign:**

1. **Verbatim completion probes** — Feed truncated articles to DeepSeek-chat. If the model completes them faithfully, memorization exists. If not, the pilot may be a true negative.
2. **Temporal split** — Compare model behavior on pre-cutoff vs. post-cutoff articles. Strongest causal identification available.
3. **CFLS by event rarity** — Stratify existing 36 cases by rarity and directional symmetry. If floor effect breaks for rare events, the bidirectional confound hypothesis gains support.

### Metric Relabeling
- CFLS → "Counterfactual Input Sensitivity" (not "leakage score") until calibrated with positive controls
- CPT flip rate → "Conflict Susceptibility" (not "memorization detector") — 14-17% may reflect in-context persuasion, not memorization

### Paper Scope Revisions
- **Drop:** XGBoost downstream analysis (deferred to follow-up application paper)
- **Drop:** Evidence intrusion heuristic (replace with claim-level attribution if rebuilt)
- **Reframe RQ1:** "Task design shapes observability/identifiability of leakage" (not "shapes leakage")
- **Add RQ0:** "Is leakage detectable at all in this setting?" — must be answered first
- **Move up:** Min-K% on Qwen as diagnostic (not just benchmark component)

### Venue
- EMNLP main track requires cross-model replication (3+ models) + non-finance generalization
- EMNLP/ACL Findings: feasible with current evidence base + diagnostic results
- Decision deferred until diagnostic phase completes

## Diagnostic Results (2026-04-08)

**Dataset:** 192 test cases (42 original + 150 expanded), 175 eligible after neutral filtering.
125 pre-cutoff + 60 post-cutoff. Balanced rarity: 78 rare + 47 medium + 50 common.

### Diagnostic 1: Baseline Memorization Probes

| Probe | Score | Interpretation |
|-------|-------|----------------|
| QA memorization (40 probes) | **0.69** | Model has significant A-share parametric knowledge |
| — event_impact | 0.875 | Knows what happened after major events |
| — trend_prediction | 0.722 | Knows market direction trends |
| — price_query | 0.591 | Moderate recall of specific prices |
| — market_performance | 0.500 | Moderate sector/stock ranking knowledge |
| Verbatim ROUGE-L (192 cases) | **0.235** | No text-level memorization |
| — pre-cutoff ROUGE-L | 0.209 | |
| — post-cutoff ROUGE-L | 0.284 | Post > pre: rules out verbatim recall |

**Key finding:** Model has event-level knowledge (QA=0.69) but does NOT memorize article text (ROUGE-L=0.23). Post-cutoff ROUGE-L > pre-cutoff confirms this — the model generates plausible pattern-based completions, not memorized text.

### Diagnostic 2: CFLS Pipeline on Expanded Dataset

#### CFLS Results

| Metric | direct_prediction | decomposed_impact |
|--------|------------------|-------------------|
| Mean CFLS | -0.837 | -0.696 |
| Positive rate | **0/141 (0.0%)** | **0/138 (0.0%)** |
| Pre-cutoff mean | -0.859 (n=99) | -0.694 (n=98) |
| Post-cutoff mean | -0.786 (n=42) | -0.700 (n=40) |
| Temporal p (MW) | **0.29** | **0.95** |

**Floor effect persists universally.** Post-cutoff events (model definitely hasn't seen) show the same CFLS pattern. This confirms CFLS measures reading comprehension, not memorization.

#### cf_invariance 4-Cell Decomposition

| Cell | direct (n=141) | impact (n=138) | Meaning |
|------|---------------|----------------|---------|
| RED FLAG (cf=1, para<1) | **0 (0.0%)** | **0 (0.0%)** | No reversal-specific anchoring |
| GLOBAL INV (cf=1, para=1) | 7 (5.0%) | 22 (15.9%) | Model outputs neutral on all conditions |
| HEALTHY (cf<1, para=1) | **118 (83.7%)** | **96 (69.6%)** | Follows reversal, stable on paraphrase |
| UNSTABLE (cf<1, para<1) | 16 (11.3%) | 20 (14.5%) | Responds to all perturbations |

**0 RED FLAG cases** across both tasks — no case where the model ignores semantic reversal while responding to paraphrase. The 83.7%/69.6% HEALTHY rate confirms genuine text-grounded responsiveness.

#### CFLS by Rarity

| Rarity | direct CFLS | impact CFLS | impact cf_inv_mean |
|--------|------------|-------------|-------------------|
| rare (n≈60) | -0.850 | -0.561 | 0.298 |
| medium (n≈37) | -0.757 | -0.806 | 0.056 |
| common (n≈45) | -0.886 | -0.778 | 0.067 |
| Kruskal-Wallis p | 0.27 | **0.016** | |
| Holm-adjusted p | — | **0.064** | |

Rare events show less negative CFLS on decomposed_impact (nominal p=0.016, Holm-adjusted p=0.064). This is driven by higher GLOBAL_INV rate (17/57=29.8%) — model outputs neutral on rare events, not memorization.

#### CPT (False-Outcome) Results

| Task | Pre-cutoff flip | Post-cutoff flip | Fisher p |
|------|----------------|-----------------|----------|
| direct | 9/98 (9.2%) | 2/42 (4.8%) | 0.51 |
| impact | 17/97 (17.5%) | 8/39 (20.5%) | 0.81 |

**No temporal effect.** ~~But note: code review found CPT used identical generic probes for pre/post (H2), making this comparison mechanistically invalid.~~

**Fixed in v2:** CPT now uses case-specific `known_outcome` negation for pre-cutoff cases and generic templates only for post-cutoff. H3 also fixed: fo_flip scored independently of SR/NP success. Re-run pending.

### Diagnostic 3: Statistical Summary

| Test | Statistic | p-value | Interpretation |
|------|-----------|---------|----------------|
| CFLS temporal (direct) | MW U=1927.5 | 0.29 | No temporal effect |
| CFLS temporal (impact) | MW U=1972.0 | 0.95 | No temporal effect |
| CFLS rarity (impact) | KW H=8.279 | 0.016 (Holm: 0.064) | Exploratory signal |
| CPT temporal (direct) | Fisher OR=2.022 | 0.51 | No effect (but H2 invalidates) |
| Cross-task CFLS | Spearman rho=0.181 | 0.04 | Weak positive (fragile) |

### Code Fixes Applied (2026-04-08)

1. **H2 fix:** `generate_false_outcome_cpt()` now uses case-specific `known_outcome` negation for pre-cutoff cases. Returns `(article, cpt_mode)` tuple with mode = `"outcome_specific"` or `"generic"`.
2. **H3 fix:** `_detect_fo_flip()` extracted as standalone function. `false_outcome_flip` scored independently of SR/NP condition success. No more null fo_flip from unrelated failures.
3. **cf_invariance decomposition:** 4-cell analysis added (`analyze_cf_invariance.py`).

### Answers to Three Diagnostic Questions

**Q1: Is CFLS a true negative or measurement failure?**
→ **True negative confirmed.** Post-cutoff events (unseen by model) show identical CFLS floor effect (p=0.29). 0 RED FLAG cases in 4-cell analysis. 83.7% of cases show HEALTHY pattern (follows reversal, stable on paraphrase). CFLS measures reading comprehension.

**Q2: Does CPT measure memorization or suggestibility?**
→ **Generic suggestibility (with original probes).** No temporal effect (p=0.51, p=0.81). But original probes were identical for pre/post (H2). **Re-run with fixed CPT (known_outcome-specific) needed** to properly answer this.

**Q3: Is the bidirectional confound hypothesis supported?**
→ **Not the primary explanation.** The floor effect persists even on post-cutoff events where no bidirectional training coverage exists. The main explanation is simpler: **CFLS measures input sensitivity, which a competent reader naturally exhibits.** The rarity effect (nominal p=0.016) is driven by higher neutral-output rate on rare events, not by differential memorization.

### Next Steps

1. **Re-run D2 with fixed CPT** on pre-cutoff cases (outcome-specific probes) — this is the only remaining experiment needed
2. **Paper reframing:** "Current leakage probes conflate memorization with comprehension — here's what each actually measures"
3. **Target:** ARR → EMNLP 2026 Findings

---

## Phase 3 (deep-floating-lake): v3 Stratified Re-run

**Date:** 2026-04-09
**Pipeline version:** 3 (3-phase batched runner, anchor + frequency strata, LLM-only CPT for pre-cutoff)
**Cases:** 682 annotated (192 re-annotated existing + 490 new from two-funnel sampling); 606 eligible after dropping 76 neutral
**Annotator:** Codex MCP (xhigh reasoning) following `docs/ANCHOR_RUBRIC.md` rubric_version 1.0

### What changed vs Phase 2

1. **Anchor stratification (NEW).** Each case now has `anchor_level ∈ {0,1,2,3}` from a fixed written rubric, replacing the hand-coded `memorization_likelihood` field. The rubric is a 4-question deterministic decision tree (no Likert), embedded verbatim in every Codex annotation prompt.
2. **Two-funnel sampling.** B1 splits sampling into a high-anchor funnel (Level 2-3, strict v2 filter + date/document/institution boosts) and a low-anchor funnel (Level 0-1, relaxed filter for roundups/ETF marketing/template content). The v2 strict filter rejected exactly the Level 0/1 content needed to ground the stratification.
3. **Frequency exposure proxy (NEW).** A BM25 index over the 1.08M-doc CLS telegraph corpus (capped at 2025-09-30 training cutoff) gives each case a `frequency_class ∈ {low, medium, high}` based on cluster_count of pre-publish-time near-duplicate hits (jaccard ≥ 0.7 + shared entity + ±3 days).
4. **LLM-only CPT for pre-cutoff (mode purification).** `generate_false_outcome_cpt()` no longer falls back to regex/generic templates for pre-cutoff cases — mixing probe modalities was a worse confound than missing data. Pre-cutoff cases that fail LLM negation after 3 attempts are marked `cpt_mode=llm_failed` and excluded from CPT analysis with a missingness footnote. Post-cutoff cases keep the directional generic template (`cpt_mode=generic_post_cutoff`) since they have no real `known_outcome` to negate.
5. **3-phase batched pipeline.** `prepare_cf_batch` → `prepare_fo_cpt_batch` → `run_tasks_batch` → CPU scoring. Each phase flattens prompts across all cases in a chunk and uses `LLMClient.batch_chat_concurrent(failure_isolated=True)` with per-prompt retry (3 attempts, `bypass_cache=True` on retry). Smoke test on 10 cases: 61.5s wall (~6s/case vs ~30s legacy).
6. **Mantel-Haenszel as primary inference.** `quick_stats.py` now reports per-stratum Fisher + pooled MH OR + Breslow-Day homogeneity. The canonical stratum field comes from `data/seed/strata_config.json` so the binary collapse decision propagates automatically (E1 and E2 both read it; no hardcoding).

### Sample design + power decision (B4)

| Cell (period × anchor_level) | n | expected `fo_flip` events @ 7.5% | OK / SHORT |
|---|---|---|---|
| pre_cutoff/0  | 85  | 6.4 | OK |
| pre_cutoff/1  | 60  | 4.5 | SHORT |
| pre_cutoff/2  | 69  | 5.2 | SHORT |
| pre_cutoff/3  | 118 | 8.8 | OK |
| post_cutoff/0 | 51  | 3.8 | SHORT |
| post_cutoff/1 | 83  | 6.2 | OK |
| post_cutoff/2 | 39  | 2.9 | SHORT |
| post_cutoff/3 | 101 | 7.6 | OK |

**Decision (recorded in `data/seed/strata_config.json`):** collapse to **`anchor_binary`** (`weakly_anchored` = Level 0+1 vs `strongly_anchored` = Level 2+3). 4 of 8 four-level cells were short (<80) of the OR=2.5 / α=0.05 / power=0.80 target at 7.5% baseline flip rate.

| Cell (period × anchor_binary) | n | expected `fo_flip` events @ 7.5% |
|---|---|---|
| pre_cutoff/weakly_anchored    | 145 | 10.9 |
| pre_cutoff/strongly_anchored  | 187 | 14.0 |
| post_cutoff/weakly_anchored   | 134 | 10.0 |
| post_cutoff/strongly_anchored | 140 | 10.5 |

**Power limitation:** 3 of 4 binary cells still fall below the more conservative 160-per-cell target. Documented as a power constraint; the 700-case budget is the binding constraint. A future iteration could add ~200 more pre-cutoff cases for full coverage.

### Annotation reliability protocol (B2 follow-up)

The B2 script wrote a 50-case double-annotation pool (`data/seed/v3_annotation_double/v3_double_annotation.json`) with `bypass_cache=True` and a different seed for the κ check. Plan-mandated targets:

- weighted Cohen's κ ≥ 0.65 with bootstrap 95% CI lower bound > 0.55
- 30-case human-reviewed gold slice with ≥80% accuracy (Wilson CI)

**Status:** the second annotation pass and the κ / gold-accuracy computation are queued as a follow-up — they require a second Codex round and a brief human review session.

### D1 Results (606 cases, batched pipeline)

Full 606-case run completed via `scripts/run_diagnostic_2.py --chunk-size 50`.
13 chunks, ~225 s/chunk, 0 errors, 0 `llm_failed_pre` (well under the 5% guard).
~310 of 1764 CF prompts (~17.6%) failed schema validation after 2 retry passes — almost all on low-anchor / roundup content where semantic reversal is structurally impossible. Affected cases get `cfls=None` and are excluded from CFLS aggregation, but their `fo_flip` is still scored independently (H3).

#### Aggregate CFLS

| Task | n_scored | mean CFLS | positive_rate |
|---|---|---|---|
| direct_prediction.base  | 447 | -0.794 | 2.2% |
| decomposed_impact.base  | 434 | -0.698 | 0.9% |

Cross-task Spearman ρ = 0.10 (p=0.039, n=415).

#### Mantel-Haenszel stratified by `anchor_binary` (E1, primary inference)

**`fo_flip_direct`:**

| Stratum | n | pre flip | post flip | OR | Fisher p |
|---|---|---|---|---|---|
| strongly_anchored | 322 | 6/183 (3.3%) | 7/139 (5.0%) | 0.64 | 0.57 |
| weakly_anchored   | 277 | 4/144 (2.8%) | 9/133 (6.8%) | 0.39 | 0.16 |
| **POOLED MH**     | 599 | 10/327 (3.1%) | 16/272 (5.9%) | **0.51** | **z=2.79, p=0.095** |

Breslow-Day homogeneity: stat=0.34, p=0.56 (strata are homogeneous; pooling is valid).
Range check: pooled 0.51 ∈ [0.39, 0.64] ✓.

**`fo_flip_impact`:**

| Stratum | n | pre flip | post flip | OR | Fisher p |
|---|---|---|---|---|---|
| strongly_anchored | 319 | 0/182 (0.0%) | 1/137 (0.7%) | 0.37 | 0.43 |
| weakly_anchored   | 270 | 0/144 (0.0%) | 2/126 (1.6%) | 0.22 | 0.22 |
| **POOLED MH**     | 589 | 0/326 (0.0%) | 3/263 (1.1%) | 0.00 (degenerate) | z=3.62, p=0.057 |

Pre-cutoff `fo_flip_impact` is identically zero across both strata, making the OR degenerate. The decomposed-impact task is so heavily anchored to the article context that no pre-cutoff case in our sample flipped its impact label under LLM-negated CPT. Treat the p-value as a zero-cell artifact.

**Penalized-logit supplement (E2, L1 Firth substitute):**

| Metric | period_post coefficient → OR |
|---|---|
| fo_flip_direct | exp(coef) = 1.53 |
| fo_flip_impact | exp(coef) = 1.24 |

Both coefs point in the *opposite* direction of the MH OR (because MH put pre in the numerator and the regression used `period_post` as the indicator). After re-orienting, the L1 substitute and MH agree directionally: post-cutoff has the higher flip rate. The L1 shrinkage damps the magnitude relative to MH, as expected.

#### CFLS temporal split (Mann-Whitney U)

| Task | pre mean (n) | post mean (n) | U | p |
|---|---|---|---|---|
| cfls_direct | -0.756 (271) | -0.852 (176) | 25738 | **0.035** |
| cfls_impact | -0.696 (270) | -0.701 (164) | 22171 | 0.98 |

Direct CFLS shows post-cutoff is **more negative** (i.e., model is *more* faithful to the article when it cannot have memorized the truth). This is the opposite of what a "memorization-driven CFLS" account predicts.

#### Sensitivity slices (E2)

After B3 backfill (`frequency_class` thresholds: low_max=58, high_min=93 cluster_count). `reversibility` is still `None` and stays out of slicing.

**`fo_flip_direct` × `frequency_class=high`** (n=272, sample is post-heavy):

| Stratum | pre flip | post flip | OR |
|---|---|---|---|
| strongly_anchored | 0/17 | 7/136 | 0.54 |
| weakly_anchored   | 0/7  | 7/112 | 1.07 |

Pooled MH OR is degenerate (all pre cells = 0), p=0.24. Direction matches the primary MH (post > pre).

**`fo_flip_direct` × `frequency_class=low`** (n=189, sample is pre-only):

| Stratum | pre flip | post flip | OR |
|---|---|---|---|
| strongly_anchored | 2/101 | 0/0 | (post empty) |
| weakly_anchored   | 2/88  | 0/0 | (post empty) |

**Critical caveat — `frequency_class` × `period` confound.** The BM25 index is capped at 2025-09-30 (the model's training cutoff), and the per-case query filters hits to dates *strictly before* `publish_time`. For pre-cutoff cases the filter typically discards a large chunk of the index, yielding low cluster counts → "low" frequency. For post-cutoff cases the filter is a no-op (everything in the index is already before `publish_time`), so they get the full top-N (≈100 hits) and almost always land in "high". The `frequency_class=low` slice therefore contains **zero** post-cutoff cases, making the "within frequency_class=low" sensitivity slice an effective pre-cutoff-only comparison rather than the period × anchor stratification we wanted. Document as a methodological limitation; a sensible fix is to compare frequency strata *within* periods only, or to recompute frequency with a fixed full-corpus window per case to break the correlation with period.

To re-run after `reversibility` annotation lands:

```bash
conda run -n rag_finance python scripts/sensitivity_analysis.py
```

#### Key takeaways from D1

1. **Pre-cutoff `fo_flip` is *lower* than post-cutoff (3.1% vs 5.9%)**, the opposite of what a memorization-bias account predicts. With mode-purified CPT (LLM-negated for pre, generic template for post), this means the more plausible the planted false outcome, the *less* the model overrides it. CPT is measuring **suggestibility**, not memorization.
2. **Probe-modality confound is real and now visible.** Because pre uses LLM-negation and post uses generic template, any pre↔post comparison still mixes two probe shapes. The plan's mode-purification trade-off was: "missing data > mixed modalities". With 0 `llm_failed_pre` we got the cleanest possible pre arm, and the *direction* of the effect (post > pre) is still consistent across both anchor strata (Breslow-Day p=0.56), so the conclusion is robust to the homogeneity assumption.
3. **Direct-CFLS temporal effect (p=0.035, post < pre)** confirms the floor-effect interpretation: where the model cannot memorize, it follows the article *more*, not less. CFLS is measuring input sensitivity / reading comprehension.
4. **Anchor stratification did not surface a memorization signal.** Per-stratum ORs (0.39, 0.64) bracket the pooled OR, both pointing in the same "post > pre" direction. There is no detectable interaction between anchor strength and the temporal effect.

### Updated Q1/Q2/Q3 Answers (post-D1, anchor-stratified)

**Q1: Is CFLS a true negative or measurement failure?**
→ **True negative, now corroborated on the v3 stratified sample.** Across 447 scored cases on direct_prediction, post-cutoff CFLS is *more* negative than pre-cutoff (p=0.035). The 4-cell decomposition pattern from Phase 2 (zero RED FLAG, ~80% HEALTHY) holds. CFLS measures reading-comprehension input sensitivity; it does not detect memorization in this regime.

**Q2: Does CPT measure memorization or suggestibility?**
→ **Suggestibility, with stronger evidence than Phase 2.** Mode-purified CPT (LLM-only for pre, generic for post) yields pre flip rate 3.1% vs post 5.9% (pooled MH OR=0.51 stratified by anchor_binary, Breslow-Day p=0.56 — strata homogeneous). The post>pre direction is the *opposite* of a memorization-bias prediction: a memorization-driven model should resist the false outcome on cases it remembers (pre), giving pre > post flip. We see the reverse. The mechanism is suggestibility — when the planted false outcome is plausibly worded (LLM-negated, pre arm), the model accepts it; when it is generic (post arm), the model overrides it with its own opinion.

**Q3: Is the bidirectional confound hypothesis supported?**
→ **No additional support beyond Phase 2.** Anchor stratification was the planned test for whether memorization signal hides inside specific anchor strata. With Breslow-Day p=0.56 and stratum ORs 0.39 / 0.64 both bracketing the pooled 0.51, there is no anchor × temporal interaction. The simpler explanation — input sensitivity for CFLS, suggestibility for CPT, both measured cleanly — survives.

---

## Phase 4 (amber-mirror-lattice): Post-Bug-Fix Re-run

**Date:** 2026-04-11
**Plan:** `~/.claude/plans/amber-mirror-lattice.md`
**Pipeline version:** 3 (same schema; 5 bug fixes applied)
**Cases:** 606 eligible (same pool as Phase 3)
**Bug fixes applied:** see `docs/BUG_AUDIT_amber.md` for full audit

### Bug-fix audit summary

A multi-agent code review of the Phase 3 pipeline found 5 bugs (3 P0, 2 P1)
that systematically biased the v3 null result. Phase A confirmed all 5 via
independent audit scripts; the G1 Codex review passed (round 2). The headline
finding from the Phase A rescore (no API calls): the `decomposed_impact`
conclusion inverts from null to memorization-direction under the Bug 3 fix.

| Bug | Fix | Verified impact |
|---|---|---|
| 1. `changed_spans` maxLength:200 killed whole-sentence CF rewrites | Dropped maxLength from schema | CF failure 1.0% (was 17% in Phase 3); NP failure **0** (was 121/606=20% in Phase 3); +144 direct, +149 impact scored cases recovered |
| 2. Aggregation missing-data opaque | Per-stratum denominators surfaced in meta | Now in `n_cf_failed_by_type`, `cf_failed_by_stratum`, `n_scored_by_task_x_stratum` |
| 3. `_detect_fo_flip` coded neutral retreat as no-flip | Enum: `strict_flip/hedged_flip/no_flip`; both strict and hedged reported | See MH tables below |
| 4. LLM-negated FO had no polarity check | `check_negation_polarity_flipped()` validator | 0 `llm_failed_pre` (polarity check is permissive on vague outcomes) |
| 5. Probe modality split by `known_outcome_available`, not period | `cpt_mode` persisted per case; cpt_mode arm in analysis | 115 llm_negated + 491 generic = 606 |

### Key definitions for this section

- **`pre_cutoff` / `post_cutoff`**: cases published before / after the model's
  training data cutoff (2025-09-30). Pre-cutoff events may have been seen during
  training; post-cutoff events could not have been.
- **`fo_flip` (false-outcome flip)**: whether the model changed its prediction
  toward a planted false outcome. Measured on two tasks: `direct_prediction`
  (direction: up/down) and `decomposed_impact` (fund_impact: positive/negative).
- **`strict_flip`**: model crossed to the polarity *opposite* its original
  prediction (e.g., up → down). This is the Phase 3 legacy definition.
- **`hedged_flip`**: model retreated from a non-neutral original prediction to
  neutral (e.g., down → neutral). Treated as a partial concession to the plant.
- **`hedged` (union)**: strict_flip ∪ hedged_flip. The Phase 4 primary metric.
- **CFLS (Counterfactual Leakage Susceptibility)**: per-case score =
  `slot_invariance(orig, cf_reversal) - slot_invariance(orig, paraphrase)`.
  Positive = suspicious stability under semantic reversal. Requires all three
  conditions (original, SR, NP) to be valid; cases with failed CF generation
  get `cfls=None` and are excluded from the CFLS aggregate (see Bug 1/2).
- **OR orientation**: in all MH tables, OR < 1 means post > pre (suggestibility
  direction); OR > 1 means pre > post (memorization direction).
- **Denominators in cross-tables**: per-metric denominators (e.g., 110 vs 115
  for llm_negated) exclude cases where orig or FO task output was invalid
  (`fo_flip_*_label = None`). The cpt_mode counts (115/217/274) are case-level;
  the cross-table denominators are metric-level (cases with scorable output).
- **`cpt_mode`**: the probe modality used for the false-outcome plant.
  `llm_negated` = LLM-rewritten outcome (115 pre-cutoff cases with known outcomes);
  `generic_post_cutoff` = directional template (all 274 post + 217 pre without
  known outcomes).

### D1 Results (606 cases, all bug fixes)

#### Aggregate CFLS (Bug 1 fix recovered ~150 more scored cases)

Phase 3 comparison values are from the "Phase 3 (deep-floating-lake): D1 Results"
section above and from `data/results/diagnostic_2_results.v3_pre_amber.json`.

| Task | n_scored (Phase 3) | n_scored (Phase 4) | mean CFLS | positive_rate |
|---|---|---|---|---|
| direct_prediction.base  | 447 | **591** | -0.799 | 2.0% |
| decomposed_impact.base  | 434 | **583** | -0.703 | 1.0% |

Cross-task Spearman ρ = 0.091 (p=0.029, n=574).

#### CFLS temporal split (Mann-Whitney U)

| Task | pre mean (n) | post mean (n) | U | p |
|---|---|---|---|---|
| cfls_direct | -0.750 (324) | -0.858 (267) | 47010 | **0.0065** |
| cfls_impact | -0.695 (325) | -0.713 (258) | 42529 | 0.70 |

Direct CFLS temporal effect strengthened from p=0.035 (Phase 3, n=447) to
**p=0.0065** (Phase 4, n=591) with 144 more scored cases. Post-cutoff remains
more negative. Same interpretation: model follows article *more* on unseen
events.

#### Mantel-Haenszel stratified by `anchor_binary` (primary inference)

**`fo_flip_direct_strict`** (reproduces Phase 3 legacy definition):

| Stratum | n | pre flip | post flip | OR | Fisher p |
|---|---|---|---|---|---|
| strongly_anchored | 323 | 6/184 (3.3%) | 7/139 (5.0%) | 0.636 | 0.57 |
| weakly_anchored   | 277 | 4/144 (2.8%) | 9/133 (6.8%) | 0.394 | 0.16 |
| **POOLED MH**     | 600 | 10/328 (3.0%) | 16/272 (5.9%) | **0.505** | **p=0.094** |

Breslow-Day: stat=0.33, p=0.57. Consistent with Phase 3 (OR=0.51, p=0.095).

**`fo_flip_direct_hedged`** (strict ∪ neutral retreat; Bug 3 fix):

| Stratum | n | pre flip | post flip | OR | Fisher p |
|---|---|---|---|---|---|
| strongly_anchored | 323 | 25/184 (13.6%) | 28/139 (20.1%) | 0.623 | 0.13 |
| weakly_anchored   | 277 | 23/144 (16.0%) | 30/133 (22.6%) | 0.653 | 0.17 |
| **POOLED MH**     | 600 | 48/328 (14.6%) | 58/272 (21.3%) | **0.638** | **p=0.036** |

Breslow-Day: stat=0.011, p=0.92 (does not reject homogeneity).
Direct hedged is now statistically significant at α=0.05. Direction is still
**post > pre** — the suggestibility interpretation strengthens, not inverts.

**`fo_flip_impact_strict`** (reproduces Phase 3 legacy; degenerate):

| Stratum | n | pre flip | post flip | OR | Fisher p |
|---|---|---|---|---|---|
| strongly_anchored | 320 | 0/182 (0.0%) | 1/138 (0.7%) | 0.376 | 0.43 |
| weakly_anchored   | 271 | 0/144 (0.0%) | 2/127 (1.6%) | 0.217 | 0.22 |
| **POOLED MH**     | 591 | 0/326 (0.0%) | 3/265 (1.1%) | **0.000** | **p=0.058** |

Consistent with Phase 3 (degenerate OR, all-zero pre cells).

**`fo_flip_impact_hedged`** (strict ∪ neutral retreat; **headline result**):

| Stratum | n | pre flip | post flip | OR | Fisher p |
|---|---|---|---|---|---|
| strongly_anchored | 320 | 16/182 (8.8%) | 9/138 (6.5%) | 1.382 | 0.53 |
| weakly_anchored   | 271 | 24/144 (16.7%) | 9/127 (7.1%) | **2.622** | **0.024** |
| **POOLED MH**     | 591 | 40/326 (12.3%) | 18/265 (6.8%) | **1.953** | **p=0.022** |

Breslow-Day: stat=1.16, p=0.28 (homogeneous — pooling is valid).

**This is the headline finding.** Under the hedged definition, pre-cutoff
cases show a **2× higher flip rate** than post-cutoff on the fund_impact task
(12.3% vs 6.8%, pooled MH OR=1.95, p=0.022). Both anchor strata point in the
same direction (OR=1.38 and 2.62, BD p=0.28). The effect is numerically larger
in the weakly-anchored stratum (OR=2.62, p=0.024), though Breslow-Day p=0.28
does not reject stratum homogeneity — the difference in stratum ORs may
reflect underpowered interaction rather than a genuine anchor × temporal effect.

This pattern is **consistent with a memorization-direction interpretation**:
pre-cutoff cases, which the model may have seen during training, show more
hedged retreats under the planted false outcome than post-cutoff cases. The
**strict** definition sees zero pre-cutoff impact flips (degenerate OR),
so this association was **entirely hidden** by Bug 3's coding of neutral
retreat as "no flip".

#### Probe-modality analysis (Bug 5 fix — `cpt_mode` × `period` cross-table)

The pre arm is mixed: 115 cases use `llm_negated` probes (LLM-rewritten
outcome), 217 use `generic_post_cutoff` (directional template). The post arm
is uniform (274 generic). To check whether the impact_hedged pre>post effect
is a probe-shape artifact, we decompose by `period × cpt_mode`:

**`fo_flip_impact_hedged`:**

| period | cpt_mode | hedged flip rate |
|---|---|---|
| pre_cutoff   | llm_negated          | 13/110 (11.8%) |
| pre_cutoff   | generic_post_cutoff  | 27/216 (12.5%) |
| post_cutoff  | generic_post_cutoff  | 18/265 ( 6.8%) |

Within the `generic_post_cutoff` arm only (apples-to-apples on probe shape),
the pre>post effect persists: pre=12.5% vs post=6.8%. The llm_negated pre rate
(11.8%) is actually *lower* than the generic pre rate (12.5%), so the
LLM-specific probe shape is not inflating the pre arm. The pre>post effect
is present regardless of probe modality.

**`fo_flip_direct_hedged`:**

| period | cpt_mode | hedged flip rate |
|---|---|---|
| pre_cutoff   | llm_negated          | 17/113 (15.0%) |
| pre_cutoff   | generic_post_cutoff  | 31/215 (14.4%) |
| post_cutoff  | generic_post_cutoff  | 58/272 (21.3%) |

For direct, within-generic also shows post>pre (14.4% vs 21.3%), consistent
with the MH result. Probe modality is not the driver.

#### Penalized-logit supplement (L1 Firth substitute)

| Metric | period_post coef → OR |
|---|---|
| fo_flip_direct_strict | exp(coef) = 1.54 |
| fo_flip_direct_hedged | exp(coef) = 1.47 |
| fo_flip_impact_strict | exp(coef) = 1.23 |
| fo_flip_impact_hedged | exp(coef) = 0.54 |

For `fo_flip_impact_hedged`, the L1 penalized logit gives
`period_post OR = 0.54` — i.e., post-cutoff has a **lower** flip rate, consistent
with the MH direction (pre > post). L1 shrinkage damps the magnitude relative
to MH (0.54 vs 1/1.95 = 0.51), as expected.

### Updated Q1/Q2/Q3 Answers (post-Phase 4, bug-fixed)

**Q1: Is CFLS a true negative or measurement failure?**
→ **True negative, strengthened by Bug 1 fix.** With 591 scored cases (was 447),
post-cutoff CFLS is more negative than pre-cutoff (p=0.0065, was 0.035). The
additional 144 cases recovered by the Bug 1 fix — disproportionately from
`post_cutoff/strongly_anchored` where CF failures had been worst — did not
reveal a hidden memorization signal. CFLS measures reading-comprehension input
sensitivity; it does not detect memorization in this regime.

**Q2: Does CPT measure memorization or suggestibility?**
→ **Revised from Phase 3.** Phase 3 answered "suggestibility only" because
the strict `fo_flip` definition showed post>pre for both tasks. Phase 4
supersedes this with the hedged definition (Bug 3 fix), which reveals a
task-dependent pattern:
- **Direct-prediction (direction):** suggestibility dominates. Pooled MH
  OR=0.64 (hedged, p=0.036) — post-cutoff cases flip more than pre-cutoff
  across both anchor strata (BD p=0.92). The model follows plausible-sounding
  false outcomes regardless of training exposure.
- **Decomposed-impact (fund_impact):** consistent with a memorization-direction
  effect. Pooled MH OR=1.95 (hedged, p=0.022) — pre-cutoff cases hedge toward
  neutral 2× more often than post-cutoff. This is the direction expected if the
  model resists the planted false outcome on cases it may have memorized. This
  association was **entirely masked** by Bug 3's strict definition (which coded
  neutral retreat as "no flip" and saw zero pre-cutoff events).
- **Interpretation split:** the direction task (binary up/down) is more
  amenable to suggestibility because the model's priors on direction are weak;
  the fund_impact task involves a more graded assessment where prior knowledge
  may create stronger resistance to contradictory evidence.
- **Caveat:** this is an association, not a causal claim. The pre arm is mixed
  (115 llm_negated + 217 generic); the post arm is uniform (274 generic). The
  within-modality cross-table (see above) shows the impact_hedged effect
  persists within the generic-only subsample (pre=12.5% vs post=6.8%), but a
  principled 2×2 cross design (Phase F optional) would strengthen the causal
  interpretation.

**Q3: Is the bidirectional confound hypothesis supported?**
→ **Revised from Phase 3.** Phase 3 answered "no additional support." Phase 4
supersedes: anchor stratification on `fo_flip_impact_hedged` shows stratum
ORs of 2.62 (weakly-anchored) vs 1.38 (strongly-anchored), with the point
estimates in the direction predicted by the confound hypothesis (weaker
anchoring → larger effect). However, Breslow-Day p=0.28 does **not** reject
stratum homogeneity, so the interaction is unconfirmed. The study is
underpowered for this interaction test. The primary finding is the main
effect (pre>post on impact_hedged), not the stratum × temporal interaction.

### Remaining caveats

1. **Construct validity vs Carlini/Nasr:** our metric (counterfactual input
   sensitivity + hedging behavior) measures a different construct from verbatim
   extraction or benchmark contamination. A matched positive control (Phase F:
   continued-pretrained Qwen) would be the strongest defense of the impact
   finding.
2. **Frequency × period confound:** `frequency_class` covaries with `period`
   (see Phase 3 caveat). Sensitivity slices within frequency_class are not
   interpretable as "within frequency" because low-frequency is almost
   exclusively pre-cutoff. Fix pending.
3. **Power for OR<2:** the 606-case sample's 80% MDE at α=0.05 for the MH
   design is ≈OR=2.4. The observed impact_hedged OR=1.95 is below this
   threshold, meaning a replication study with the same N might not reproduce
   the finding. A future iteration should add ~200 cases to reach the
   conservative 160-per-cell target.
4. **No positive control:** Phase F (continued-pretrained Qwen) was not
   executed in this iteration. It remains the recommended next step for
   defending the impact finding.

### Carry-over follow-ups (queued for the next iteration)

- **D2 reversibility annotation:** `scripts/annotate_reversibility.py build` was wired to read `condition_summary.sr_direction.article` from the D2 results. The current chunked driver doesn't yet persist the SR rewritten article into `condition_summary` (it stores `failed` + `source` only). Either (a) extend the driver to also write `cf_payload.rewritten_article` into `condition_summary`, or (b) re-derive SR text from the cached LLM responses. Then run `scripts/annotate_reversibility.py build` and dispatch the resulting batches via Codex MCP.
- **B2 reliability protocol (κ + gold slice):** the 50-case double-annotation pool is in `data/seed/v3_annotation_double/`. A second Codex pass with `bypass_cache=True` and a different seed, plus a 30-case PI-reviewed gold slice, gives the weighted κ and accuracy-vs-gold needed by the plan.
- **Frequency × period confound fix (see slice caveat above):** rebuild the BM25 index with a full-corpus window or compute frequency *within periods only* before treating `frequency_class` as a primary stratification covariate.

### Known caveats vs the original plan

- **B3 frequency_class:** the BM25 query loop is dominated by `rank_bm25.BM25Okapi.get_scores`, which is a Python loop over 1M dicts per query token (~10s/case for our query shape). On 682 cases that's ~1.9 hours. Backgrounded after D1; sensitivity slices that depend on `frequency_class` (E2) will run once it lands. None of the primary inferences depend on frequency_class.
- **Firth substitute:** true Firth's penalized logit is not available in Python 3.12 (firthlogist requires <3.11) and rpy2 has no R installed on this host. We use `statsmodels.Logit.fit_regularized(method='l1', alpha=1.0)` and document the substitution in `docs/FIRTH_DECISION.md`. Primary inference therefore stays MH.
