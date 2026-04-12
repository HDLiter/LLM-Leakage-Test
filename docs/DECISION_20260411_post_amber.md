# Decision Record: Post-Phase 4 Direction (2026-04-11)

**Date:** 2026-04-11
**Input:** 4-agent Codex discussion (Quant / NLP / Stats / Editor), each with independent web search and paper review
**Discussion logs:** `refine-logs/decision_20260411/AGENT_{QUANT,NLP,STATS,EDITOR}.md`
**Status:** Phase 4 (amber-mirror-lattice) complete; headline finding is `fo_flip_impact_hedged` OR=1.95, p=0.022

---

## Convergence Summary

### Unanimous (4/4 agents)

1. **Qwen positive control is the single highest priority.** The binding constraint is construct validity, not sample size. Without demonstrating that the metric moves when memorization is known to exist, the `impact_hedged` finding remains an association vulnerable to the "task artifact" objection.

2. **Do NOT prioritize adding more N or fixing annotation kappa first.** Those sharpen an instrument that is still not causally calibrated.

3. **EMNLP 2026 Findings is the right venue.** ARR deadline: **May 25, 2026**; commitment: August 2, 2026. Backup: FinNLP 2026 workshop.

### Strong Agreement (3-4/4)

4. **Pre-register `fo_flip_impact_hedged` as the single primary endpoint** before any confirmatory run. The `hedged` definition emerged from a bug fix and is post-hoc; freezing it now and confirming on fresh data neutralizes the strongest reviewer objection (Stats, Editor, NLP).

5. **Fix design confounds by design** before scaling: rebuild `frequency_class` as a period-invariant proxy; make CPT probe modality uniform or run 2x2 within-case cross (Stats, Quant, NLP).

6. **Reframe the paper around observability/identifiability**, not memorization claims. Lead with the task-dependent reversal (same model, same articles, same probe, different task, opposite conclusion). Present `impact_hedged` as "consistent with" memorization direction (Editor, NLP, Quant).

### Notable Divergences

| Agent | Unique Recommendation | Value |
|-------|----------------------|-------|
| NLP | Add a truly evidence-grounded task (e.g., source extraction, quote-grounded claim support) — current direct vs impact is "two outcome-prediction variants" | Strengthens the "task gates memory" claim substantially |
| Stats | Exact sample sizes: ~850 scorable (single primary) or ~1,200 (4-endpoint family) for 80% power at OR=1.95 | Anchors resource planning |
| Quant | Dose-response calibration: inject events 0/1/2/5 times on Qwen → fit contamination-dose curve | Makes the result more interpretable for applied audiences |
| Editor | Convert the 5-bug audit into a "Leakage Probe Audit Checklist" artifact | Turns a potential liability into a methodological contribution |

---

## Prioritized Action Plan

### Phase 5a: Qwen Positive Control (TOP PRIORITY)

**Goal:** Demonstrate that the pipeline detects memorization when it is known to exist.

**Design (reduced 4-run MVP):**

| Run | Article Exposure | Outcome Injection | Label |
|-----|-----------------|-------------------|-------|
| 1 | None (base Qwen) | None | `(0, none)` |
| 2 | Article only | None | `(1, none)` |
| 3 | Article + real outcome | None | `(1, real)` |
| 4 | Article + false outcome | None | `(1, false)` |

- Evaluate on `direct_prediction`, `decomposed_impact`, and one evidence-grounded task
- Read out `strict_flip`, `neutral_retreat`, evidence intrusion, Min-K%, logprob signals
- Use a subset of the 606 cases (e.g., 100 high-anchor pre-cutoff cases)
- Keep filler corpus, token budget, and held-out sanity checks fixed across arms

**Success criteria:**
- Run 3 (`1, real`) shows higher `impact_hedged` than Run 1 (`0, none`)
- Run 4 (`1, false`) shows flip toward false outcome on `direct_prediction`
- Effect is larger on outcome-proximal tasks than evidence-grounded task

**Risk:** Medium. CPT can induce capability drift if injection is too aggressive. Mitigation: small injection dose, capability sanity checks, filler corpus.

**Timeline:** 8-12 researcher-days

**Blocks:** Everything else. If the positive control fails, the paper pivots to "CFLS-as-comprehension + suggestibility taxonomy" (still publishable but weaker).

### Phase 5b: Metric Freeze + Pre-registration

**Goal:** Lock the confirmatory protocol before any new data collection.

**Actions:**
1. Designate `fo_flip_impact_hedged` as the **sole primary endpoint**
2. Primary analysis: stratified CMH by `anchor_binary`
3. Secondary/sensitivity: `impact_strict`, `direct_hedged`, `direct_strict`, exact conditional CMH, Zelen exact homogeneity
4. Multiplicity: hierarchical testing (primary → secondary) so only one claim is at risk
5. Document in a pre-registration file (`docs/PREREGISTRATION.md`)

**Timeline:** 1-2 researcher-days (can overlap with Phase 5a setup)

### Phase 5c: Conflict-Response Taxonomy Refactoring

**Goal:** Decompose `hedged_flip` into interpretable sub-outcomes.

**Actions:**
1. Reclassify all 606 cases into: `strict_reversal`, `neutral_retreat`, `steadfast`
2. Cross-tabulate with Qwen Min-K% familiarity scores (run on existing cases)
3. Add narrow evidence-intrusion labels (claim-level, not heuristic)
4. Determine whether `impact_hedged` is driven by memory, abstention, or both

**Timeline:** 5-7 researcher-days (can partially overlap with Phase 5a)

### Phase 5d: Evidence-Grounded Task Addition

**Goal:** Add one task that is genuinely different from outcome prediction to sharpen the "task gates memory" claim.

**Candidates (pick one):**
- Authority/source extraction ("Who said what?")
- Quote-grounded claim support ("Does the article support this claim?")
- Article-only evidence selection with abstention

**Timeline:** 8-12 researcher-days (run on the positive-control Qwen arms)

### Phase 5e: Confirmatory Replication

**Goal:** Replicate the `impact_hedged` finding on fresh data with the frozen protocol.

**Actions:**
1. Fix `frequency_class` × `period` confound (period-invariant exposure proxy)
2. Make CPT probe modality uniform across arms (or run 2x2 within-case cross)
3. Finish B2 reliability protocol (κ + gold slice)
4. Add ~250-400 new cases to reach ~850 scorable (single-primary target)
5. Run frozen CMH analysis

**Timeline:** 10-15 researcher-days

---

## Critical Path

```
Phase 5b (metric freeze)  ──┐
                             ├──→  Phase 5a (Qwen positive control)
Phase 5c (taxonomy refactor) ┘            │
                                          ↓
                              Phase 5d (evidence-grounded task)
                                          │
                                          ↓
                              Phase 5e (confirmatory replication)
                                          │
                                          ↓
                                   Paper draft
```

**Total estimated timeline:** 30-45 researcher-days to paper submission
**ARR deadline:** May 25, 2026 (44 days from now)

**Minimum viable paper (if time-constrained):** Phase 5a + 5b + paper draft. This gives: CFLS-as-comprehension anchor + task-dependent CPT pattern + positive control calibration. Drop Phase 5d and 5e; bound claims tightly.

---

## Narrative Strategy (Editor recommendation)

**Title direction:** "Task Design Gates the Observability of Look-Ahead Memory in Financial News LLMs"

**Abstract structure:**
1. Problem: historical evaluation of LLM financial pipelines is vulnerable to look-ahead leakage
2. Finding: on the same articles with the same probe, different task designs yield opposite conclusions about whether the model uses memorized outcomes
3. Anchor: positive control on an open model confirms the probe detects real memorization
4. Contribution: evaluation methodology + construct-validity analysis + Chinese financial NLP benchmark

**Lead with:** The task-dependent reversal (suggestibility on direct, memorization-direction on impact)
**Anchor with:** CFLS-as-comprehension (cleanest, most robust finding, p=0.0065)
**Present cautiously:** `impact_hedged` OR=1.95 as "consistent with" memorization direction
**Appendix:** Bug audit → Leakage Probe Audit Checklist (methodological artifact)

---

## Wild Cards Worth Considering

1. **Dose-response curve** (Quant): Inject events 0/1/2/5 times on Qwen, fit contamination-dose curve, map DeepSeek's OR to an implied contamination-equivalent dose. High novelty but adds ~5 days.

2. **Empirical calibration** (Stats): Build negative-control and positive-control reference sets, calibrate p-values against that error distribution. Standard in pharma epidemiology, novel in LLM leakage. Adds ~3 days if positive control exists.

3. **Ceilinged contamination-trap** (NLP): Design benchmark items with known Bayes ceilings so future models exceeding the ceiling reveal contamination by construction. Good for the benchmark artifact, not urgent for this paper.

4. **Leakage Probe Audit Checklist** (Editor): Formalize the 5-bug audit into a reusable checklist for the community. Low effort, high reviewer goodwill.

---

## Statistical Guardrails (Stats Agent)

| Finding | Raw p | Holm-adjusted p | Power | Risk Level |
|---------|-------|-----------------|-------|------------|
| CFLS temporal (direct) | 0.0065 | — | High | **Low** (robust anchor) |
| `impact_hedged` MH | 0.022 | 0.088 | 0.63 | **Moderate-high** (needs confirmation) |
| `direct_hedged` MH | 0.036 | 0.108 | — | **Exploratory only** |
| `impact_strict` MH | 0.058 | — | — | **Degenerate** (zero cells) |

**Key warning:** The headline OR=1.95 does not survive multiplicity correction (Holm p=0.088). This is why pre-registration with a single primary endpoint is essential before confirmation.

---

## References (from agent web searches, 2024-2026)

- He et al., Chronologically Consistent LLMs (2025): arxiv 2502.21206
- Impact of Post-training on Data Contamination (2026): arxiv 2601.06103
- All Leaks Count, Some Count More (2026): arxiv 2602.17234
- Lopez-Lira et al., The Memorization Problem (2025): arxiv 2504.14765
- Li et al., Profit Mirage (2025): arxiv 2510.07920
- Gao et al., A Test of Lookahead Bias (2025): arxiv 2512.23847
- Wu et al., AntiLeakBench (ACL 2025): aclanthology 2025.acl-long.901
- MMLU-CF (ACL 2025): aclanthology 2025.acl-long.656
- Li et al., Diagnosing Memorization in CoT (EMNLP 2025): aclanthology 2025.emnlp-main.157
- Huang et al., Selective Abstention (ACL 2025): aclanthology 2025.acl-long.1199
- Yan et al., DatedGPT (2026): arxiv 2603.11838
- Ishida et al., Publishing Benchmarks Without Answers (2025): arxiv 2505.18102
- AttenMIA (2026): arxiv 2601.18110
- Reason to Rote (EMNLP 2025): aclanthology 2025.emnlp-main.437
- LastingBench (Findings EMNLP 2025): aclanthology 2025.findings-emnlp.993
