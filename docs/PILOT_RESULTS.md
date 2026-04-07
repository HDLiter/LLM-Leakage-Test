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
