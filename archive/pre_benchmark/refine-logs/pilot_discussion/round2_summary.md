# Round 2 Summary — After Challenger Review

**Date:** 2026-04-06
**Agents:** Quant, NLP, Stats, Editor (all responded to Challenger findings)

---

## Position Revisions

### All 4 agents revised on CFLS interpretation
- **Round 1 consensus:** "CFLS is broken / measurement failure"
- **Round 2 consensus:** "CFLS is **uncalibrated and non-diagnostic** — the pilot cannot distinguish true negative from insensitive measurement"
- All 4 agree: **positive control testing** (known-memorized items) is the essential next step before any conclusion

### All 4 agents revised on CPT interpretation
- **Round 1 consensus:** "CPT is more promising than CFLS as a leakage detector"
- **Round 2 consensus:** "CPT measures **contextual override / in-context persuasion susceptibility**, not memorization per se"
  - **Quant:** "Relabel as a robustness statistic, not a leakage statistic — still economically relevant for production"
  - **NLP:** "Conflict-resolution metric, useful only as complement to direct familiarity probes"
  - **Stats:** "No clean exclusion restriction — becomes informative only when interacted with exposure proxy"
  - **Editor:** "Most promising anomaly probe, but needs correlation with independent exposure proxies"

### Quant revised on economic validation scope
- **Round 1:** Wanted IC/hit-rate/decile analysis
- **Round 2:** Agrees to drop XGBoost/economic validation from this paper; keep production rationale for event selection only

### Editor revised on venue and narrative
- **Round 1:** EMNLP main track with reframing
- **Round 2:** "ACL/EMNLP Findings is more realistic" without cross-model replication and non-finance generalization

---

## Final Convergent Points (4/4 agree)

### FC1. CFLS is uncalibrated, not proven broken
The pilot result is non-diagnostic. Positive controls are required before claiming either measurement failure or true negative.

### FC2. Three cheap diagnostics BEFORE benchmark redesign
All 4 agree this is the correct sequencing:
1. **Verbatim completion probes** — test whether DeepSeek shows any detectable direct recall at all
2. **Temporal split** (pre- vs. post-training-cutoff) — strongest causal leverage for exposure-linked variation
3. **CFLS stratified by event rarity** in existing pilot data — directly tests the bidirectional coverage hypothesis

### FC3. CPT measures conflict susceptibility, not memorization
Raw flip rate is ambiguous. CPT becomes informative only when:
- Interacted with an exposure proxy (Stats)
- Correlated with independent evidence: Min-K%, temporal split, or completion probes (NLP, Editor)
- Relabeled appropriately in the paper (Quant)

### FC4. Sentiment analysis leakage risk is heterogeneous
- Common/schematic events: leakage risk is low because task is largely skill-based
- Rare/idiosyncratic events: leakage risk is higher because the model might benefit from article-specific or outcome-specific knowledge
- The paper must distinguish between these regimes (NLP, Editor)

### FC5. Drop XGBoost downstream analysis from this paper
Belongs in a follow-up application paper. Keep production rationale for benchmark design only.

### FC6. Bidirectional confound is a hypothesis, not yet a contribution
Must be validated by:
- Positive controls showing CFLS does detect memorization when present
- Rarity/frequency stratification showing the confound operates differently across event types
- Ideally, replication outside Chinese finance to show generality (for EMNLP main track)

---

## Remaining Open Questions

1. **Go/no-go for the project premise:** If diagnostics show true negative (no memorization), the project may need to rethink its research premise rather than just redesign the benchmark.
2. **DeepSeek training cutoff:** Is it credibly known? How sharp is it? This determines the quality of the temporal split design.
3. **Min-K% on Qwen:** Already in the project plan (RQ2), but should be moved up as a diagnostic, not just a benchmark component.
4. **Cross-model replication:** Editor says EMNLP main track requires it; at minimum need 3 model families.

---

## Convergence Assessment

**CONVERGED.** All 4 domain agents revised their positions in response to the Challenger. No 2v2 splits or unresolved disagreements. The Challenger's core challenge ("you're salvaging a null before understanding it") was accepted by all agents.

**Action items are clear and sequenced:**
1. Run 3 cheap diagnostics (verbatim probes, temporal split, rarity stratification)
2. Based on results, decide: measurement paper (confound is real) vs. true-negative paper (leakage is absent) vs. premise revision
3. Only then proceed to 1000-case benchmark design

**No Round 3 needed.**
