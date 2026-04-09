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
