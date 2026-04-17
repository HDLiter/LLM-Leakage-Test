# Round 1 — Quant Agent (Senior Quantitative Researcher)

**Thread:** 019d65cd-0063-7cb1-8ea1-b911b47a3485

## Analysis

### 1. What CFLS ≤ 0 Means for Pipeline Reliability

If CFLS is non-positive in every case, the practical reading is: the model is not stubbornly clinging to a memorized market outcome when you invert the news. It follows the sign of the event. For production, that is mildly reassuring because it suggests the feature is primarily text-conditioned, not obviously contaminated by post-event knowledge. But it also means the model is behaving like an event-to-direction mapper, not a source of privileged foresight.

For A-share news, that is important. Many of these event classes are canonical and mechanically interpretable: easing is good, tightening is bad, supportive regulation is good, enforcement is bad. A model that cleanly flips with the text is reliable as a parser, but that does not imply alpha. In fact, it usually implies the opposite: the signal may be economically valid but already crowded, low-novelty, and fast-decaying. So the result is "pipeline-safe-ish, alpha-unproven."

### 2. False-Outcome CPT: 14–17% Flip Rate

A 14.3–16.7% flip rate is economically meaningful. One in six cases is too high to dismiss if the signal will be used systematically across a large news stream. Even if the perturbation pushes the model only from `up` to `neutral`, that still degrades rank ordering, lowers signal-to-noise, and can flatten position sizing exactly where conviction matters.

That said, this number does not look like "the model secretly knows the answer" in a strong sense. It looks more like a reasoning-plus-rationalization model: it mostly reasons from event semantics, but when you inject a contradictory future-outcome cue, it sometimes tries to reconcile with that cue. So the model's knowledge channel exists, but it is secondary.

### 3. Bidirectional Generalization: Problem or Feature?

For leakage measurement, it is a real confound. For trading, however, bidirectional generalization is mostly a feature. You want the model to understand both `降准` and `升准` without brittle prompt engineering. That improves operational robustness.

The catch: a feature can be operationally clean and economically dirty. If the model generalizes both directions well on common event families, the resulting signals are likely more standardized, more compressible into rule-based features, and more exposed to alpha decay. Cleaner as an NLP primitive, dirtier as a differentiated alpha source.

### 4. Medium > High Memorization CFLS Pattern

Direct CFLS moves from `-0.964` (high) to `-0.714` (medium). Medium-frequency cases likely involve more idiosyncratic causal chains, weaker consensus mappings, or event types where bullish/bearish analogs are not equally represented. From a quant perspective, the medium bucket is where signal quality becomes more interesting — harder, less commoditized, and more likely to carry differentiated alpha.

### 5. Benchmark Design

Move away from canonical, high-frequency event templates. Prioritize rarer, asymmetric, high-impact events: accounting irregularities, shareholder pledge stress, restructuring failures, supply-chain shocks, litigation, subsidy withdrawals, product accidents, export restrictions, ST designation dynamics.

Corpus frequency as formal covariate with three measures:
- `log(1 + event-template count)`
- Directional balance (bullish vs bearish analog ratio)
- Entity-event uniqueness

### 6. Cross-Task Correlation and XGBoost

r = 0.10 means the two prompting styles do not fail in the same way. Keep them separate in XGBoost; let the model learn conditional usefulness. Add disagreement features: task spread, confidence gap, neutral propensity, reversal consistency. Supports a gated ensemble, not a naïve ensemble.

### 7. Next Steps

1. Benchmark redesign around rarer and more tradable events with frequency/symmetry covariates
2. Direct economic validation: does each task improve out-of-sample IC, hit rate, or decile spread?
3. Reliability model: predict when to down-weight the LLM feature using event category, corpus frequency, prompt disagreement, and confidence
4. Stronger contamination tests: adversarial context variants, irrelevant-outcome distractors, temporal holdout checks
