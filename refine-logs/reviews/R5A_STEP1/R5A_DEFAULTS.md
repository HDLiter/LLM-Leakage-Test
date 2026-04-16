---
title: R5A — Opening defaults for Step 2
stage: R5A Step 1.5 (between Step 1 synthesis and Step 2 convergence)
date: 2026-04-15
status: OPENING POSITIONS — not frozen decisions
author: Claude Code orchestrator, grounded in R5A_STEP1_SYNTHESIS.md
scope: 9 of 10 detectors from the Step 1 pool (D4 ADG deferred to temporal-cue session)
---

# R5A — Opening defaults for Step 2

## 0. What this document is (and is not)

This document is the **opening position** for R5A Step 2, not a frozen set of rulings. It exists so that the four Step 2 Codex lens agents (Quant / NLP / Stats / Editor) do not have to start from a blank page when they review the Step 1 pool.

**Read this way**:

- Each position below is a **starting stance** grounded in the Step 1 lens outputs. Step 2 agents are **free and encouraged to overturn any position** if they find a stronger argument — that is their job.
- Each position is paired with (a) the **evaluation question** that would decide whether the stance survives contact with reality, and (b) the **explicit freedoms** Step 2 agents have to revise it.
- **Implementation specifics are deferred**. Whether D3 uses vanilla Min-K%++ or a calibrated variant, whether D8 uses masked suffix or prefix continuation, whether D6 NoOp clauses are length-matched to the base article or length-normalized — all of these are implementation-level decisions that depend on pilot data quality and will be settled in a later dedicated implementation section, not here. This document focuses on **whether a detector belongs in the pool and how we would judge it**, not on how to build it.
- **The detector pool is deliberately kept broad**. Step 1's Editor lens argued for a hard ceiling of 5 detectors in the 9-page paper; the user has relaxed this for R5A — we prefer to carry a broader pool into Step 2 and let data quality + pilot evidence drive the eventual main-text shortlist, rather than prune prematurely.
- **R4's "no new factors" rule is softened.** Per user clarification 2026-04-15, the v6.2 decision doc's "do not add factors in R5" language is to be read as a hygiene rule for staying on-topic during detector discussions, not as a hard gate before pre-commit. Step 2 agents may propose new factors if they are load-bearing for detector evaluation.

## 1. D4 ADG is on hold

D4 (As-of Date Gating) is held out of this document because its design is entangled with the upcoming temporal-cue session. NLP lens's Step 1 proposal treats ADG as a single detector, but user discussion on 2026-04-15 identified two distinct operating modes (ADG-contradiction when in-text temporal cues are preserved vs ADG-misdirection when in-text temporal cues are masked first). That decomposition depends on first settling how temporal cues are handled across the benchmark, so D4 is deferred to the next round.

Everywhere else in this document, treat D4 as "pending" and do not re-open it here.

## 2. Opening positions on the 7 Step 1 tensions

Each tension is stated as an opening stance, the evaluation question that would decide it, and the explicit freedoms a Step 2 agent has to revise it.

### T1. EAD — standalone detector vs P5 field only

**Step 1 split**: Stats and Quant want EAD as a standalone detector (within-case paired intervention with a clean identification argument). NLP and Editor want EAS as a cross-detector stratification field (no standalone slot).

**Opening position**: **Both roles simultaneously.** D7 EAD is a standalone detector AND its computation automatically yields EAS stratification fields for every other detector in the pool. Report structure at the paper level is a separate question (see §5 on pool size management) and does not force a choice here at the measurement level.

**Evaluation question**: Does EAD's standalone output (raw-minus-masked delta on the same detector) carry information that is not already captured by the EAS stratification field applied to D1/D3/D5/D6/D8? If the two are strongly correlated (say ρ > 0.85), the standalone role is redundant and EAD should collapse into the field role only. If not, the dual role is justified.

**Free for Step 2**: Which masking taxonomy EAD uses (full anonymization only, category-preserving only, or both), whether the target/non-target split NLP proposed is sufficient, whether additional masking dimensions (temporal cue masking — see temporal session) fold in here or stand apart.

**Not free for Step 2**: The principle that target-mask delta and non-target-mask delta must be stored separately — NLP's argument for this is unanimous and should be respected.

### T2. SR and FO — paired family, two detectors, or merged score

**Step 1 split**: Quant proposes FO only. NLP splits SR and FO into two detectors. Stats merges them as a single Counterfactual Fact Inertia (CFI) scalar. Editor wants a single paired family.

**Opening position**: **One detector slot (D5 Counterfactual Perturbation Pair) with two sub-measurements preserved.** SR (semantic polarity reversal) and FO (outcome slot replacement) are reported as two sub-fields of the same detector — analogous to how Propagation Intensity preserves event_burst and historical_family_recurrence as separate fields under a single factor label.

**Evaluation question**: Do SR and FO produce divergent MTMM-style predictions on the same cases, as NLP's nomological argument predicts (SR should track Cutoff Exposure; FO should track Anchor Strength)? If yes, the two-sub-field structure is justified. If SR and FO correlate at ρ > 0.9 on pilot data, Stats's merge is correct and they collapse to one scalar.

**Free for Step 2**: Whether SR and FO are generated from the same rule engine or separate pipelines, whether the merged CFI scalar is reported alongside the two sub-fields as a convenience summary, the exact perturbation-generation protocol (this is implementation-deferred).

**Not free for Step 2**: Dropping either SR or FO without the convergence evidence above. The two sub-measurements stay until data says they are redundant.

### T3. PCSG — keep as standalone or fold into Min-K%++

**Step 1 split**: Only Stats proposed PCSG. Stats's synthesis ranks it #1 by identifiability × power, arguing that the within-case paired contrast removes case-level confounds that single-model Min-K%++ cannot. Other lenses did not discuss it.

**Opening position**: **Keep D2 PCSG as a standalone detector.** Paired contrast designs are methodologically strong and PCSG's marginal cost is near-zero if it shares logprob traces with D3. Being a single-lens proposal is not a defect; it is an artifact of lens specialization.

**Evaluation question**: Does the PCSG gap on known-leakage pilot cases exceed the gap on matched placebo (clearly post-cutoff) cases by a margin that is stable under model-pair choice? If the gap is fragile to model-pair selection, PCSG collapses into a "model-quality detector" and should be folded into D3 as a stratification field.

**Free for Step 2**: How many model pairs PCSG uses, whether it runs on all 3 white-box models or a subset, whether it is reported alongside D3 in a combined "surface family" paper section.

**Not free for Step 2**: Dropping PCSG without running the placebo test above. Stats's identification argument is strong enough that it deserves an evidence-based rebuttal, not a lens-vote rebuttal.

### T4. D4 ADG — deferred

See §1.

### T5. Extraction (D8) — main text vs reserve

**Step 1 split**: Quant and NLP want extraction in the main text (Quant as "high-precision anchor", NLP as "narrow but exceptionally traceable construct"). Stats wants it demoted to reserve for power reasons. Editor treats it as a 5th-slot option competing with RAVEN.

**Opening position**: **Keep D8 in the main text, but redefine its role as corroborative hard-edge evidence, not as an omnibus statistical detector.** Report it primarily through qualitative case examples and exact-match rate, not through aggregated factor-crossed statistics. This reconciles Quant/NLP's construct argument with Stats's power concern — the detector's job is not to carry confirmatory power, it is to ground the other detectors in concrete examples of verbatim reuse.

**Evaluation question**: Is the exact-match rate on pilot data high enough (say ≥ 5% on 100-case sample) to produce a non-trivial number of concrete examples per factor stratum? If match rate is sub-1%, D8 loses its qualitative role and should be relegated to a single-paragraph mention.

**Free for Step 2**: The specific extraction protocol (masked suffix, prefix continuation, or multi-span variants), how many prompt variants per case, whether aligned models (DeepSeek, Claude) are included given paraphrase-over-quote behavior, how the qualitative examples are selected for paper presentation.

**Not free for Step 2**: Using D8 as an omnibus statistical detector. Its role is deliberately narrower to match its actual evidential strength.

### T6. Debias Delta (D10) — detector or mitigation baseline

**Step 1 split**: Quant proposes it, all other lenses silent. Quant itself flags it as a heavier Step 2 candidate with materially higher engineering burden.

**Opening position**: **Drop from the main pool.** Merchant & Levy 2025 is already cited in the R5 reading queue and can be referenced as related work without building the detector. The engineering cost (15-25 GPU-hours + training retain/forget components) is not justified by a single-lens proposal when other detectors already cover the temporal-cutoff-conditional family (CMMD + PCSG + the pending ADG).

**Evaluation question**: Is there a Step 2 argument that Debias Delta measures something CMMD / PCSG / ADG do not? If yes, reconsider. If not, it stays dropped.

**Free for Step 2**: Overturning this entirely if a lens produces a novel construct-validity argument for why Debias Delta is not redundant. The default is "drop", but the decision is reversible at low cost (nothing is built yet).

**Not free for Step 2**: Keeping it because it is "interesting" without clearing the redundancy question.

### T7. RAVEN (D9) — fifth-slot detector or drop

**Step 1 split**: Only Editor proposed it. Editor itself warned of overlap with Template Rigidity.

**Opening position**: **Drop from the main pool.** Editor's own caveat about Template Rigidity overlap is the decisive argument. RAVEN's methodological niche (output-behavior memorization via novelty gap) is already addressed in paper framing by citing McCoy et al. 2021, and extraction (D8) provides stronger hard-edge evidence in the same general neighborhood.

**Evaluation question**: Does any Step 2 lens produce a concrete construct that RAVEN measures uniquely — something D3 / D5 / D8 do not cover even after the temporal session? If yes, revisit. If not, it stays dropped.

**Free for Step 2**: Overturning this if a lens builds a distinct novelty-gap construct argument that distinguishes RAVEN from Template Rigidity, the factor.

**Not free for Step 2**: Keeping it on EMNLP-audience-familiarity grounds alone. That argument is already covered by citing McCoy et al. in the related-work section.

## 3. Per-detector evaluation frameworks

For each detector in the post-tension pool, this section gives a **success condition**, a **dominant failure mode**, the **cheapest pilot** that could tell us whether to proceed, and the **data quality gate** that must clear before running. This is intentionally not an implementation spec — Step 2 agents and the later implementation section will settle how each detector is actually built.

### D1 — CMMD (Cross-Model Memorization Disagreement)

- **Success condition**: Disagreement among fleet models is monotone with model cutoff order on cases we know were likely in later-cutoff training windows, AND does not appear monotone on placebo cases in clearly post-cutoff windows where none of the fleet could have seen the article.
- **Dominant failure mode**: Cross-model disagreement is driven by architecture, Chinese financial competence, or hosted-model nondeterminism rather than cutoff-linked training exposure. If this dominates, CMMD becomes a "capability-ordering detector" that happens to correlate with cutoff because larger/newer models are both more capable and more recent.
- **Cheapest pilot**: Run 20 known-leakage candidate cases (where the event precedes at least one fleet model's cutoff by a clear margin) and 20 matched placebo cases (clearly post-cutoff for the entire fleet) through all 6 fleet models. Check whether the `cutoff_monotonicity_score` differs significantly between the two groups. Budget: ~240 API calls, under $1.
- **Data quality gate**: Fleet composition must be finalized (see fleet review session) and all 6 checkpoints pinned with reproducibility locks before main run. Placebo case pool must be verifiable (events that occurred after all 6 cutoffs).

### D2 — PCSG (Paired Cutoff Surprise Gap)

- **Success condition**: The within-case `late_cutoff_surprise − early_cutoff_surprise` gap is larger on known-leakage cases than on placebo cases under a pre-registered model-pair normalization, and the gap direction is stable across different model-pair choices within the 3 white-box fleet members.
- **Dominant failure mode**: Model-pair baseline miscalibration dominates the gap. If Qwen2.5-7B and Qwen3-14B have different fluency baselines on Chinese financial text for reasons unrelated to cutoff (e.g., better tokenizer coverage, different instruction-tuning data mix), the "paired contrast" is measuring calibration drift, not cutoff-linked memorization.
- **Cheapest pilot**: 10 known-leakage + 10 placebo cases, 2 model pairs (Qwen2.5-7B vs Qwen3-14B; GLM-4-9B vs Qwen3-14B). Compute Min-K%++ on each, take paired gaps, check whether gap distributions are separable. Budget: logprob passes on 60 inputs, <1 GPU-hour.
- **Data quality gate**: Stable logprob access on 3 white-box models (Qwen2.5-7B, GLM-4-9B, Qwen3-14B); pre-registered baseline normalization rule.

### D3 — Min-K%++ / Calibrated Tail Surprise

- **Success condition**: After calibration, correlation with Template Rigidity (char-5gram TF-IDF to nearest neighbors) is below some pre-registered threshold (tentative: ρ < 0.6). If calibrated and uncalibrated variants differ by more than a few points of Template-Rigidity correlation, the calibration is doing real work and is preferred.
- **Dominant failure mode**: The detector collapses into a Template Rigidity / boilerplate-reuse detector and the paper headline becomes "FinMem-Bench detects char-5gram similarity to CLS corpus", not "FinMem-Bench detects memorization". This is the single biggest Risk R4 vector in the pool.
- **Cheapest pilot**: On a ~50 case subset with existing Propagation Intensity labels, compute vanilla Min-K%++ and at least one calibrated variant. Measure partial correlation with Template Rigidity controlling for Propagation Intensity. Budget: a few hundred logprob passes.
- **Data quality gate**: Stable Chinese tokenization across the 3 white-box models; pre-committed Template Rigidity computation on the same cases so partial correlation is clean.

### D5 — Counterfactual Perturbation Pair (SR + FO)

- **Success condition**: On a human-audited subset, the generated perturbations (a) are linguistically natural in Chinese CLS style, (b) preserve every non-target aspect of the original, (c) change the intended target aspect cleanly and verifiably. Audit pass rate should be high enough that pilot noise does not dominate — tentative target ≥ 85%.
- **Dominant failure mode**: Chinese perturbation edit quality is inconsistent. If the rewrites are unnatural or partially inconsistent, the detector's "snap-back" signal becomes "unnatural-text rejection" — the model is resisting the edit not because it memorized the original, but because the edit reads as malformed CLS Chinese. This dominant failure mode is exactly what Editor, NLP, and Stats all flagged.
- **Cheapest pilot**: Generate 50 SR + 50 FO perturbations on representative CLS cases using a rule-based-first pipeline (event type templates + slot schema). Human-audit for naturalness, consistency, and target-clean edit. Budget: generation is cheap (~100 LLM calls); audit is the real cost (a few hours of labeler time).
- **Data quality gate**: Thales event_type labels and entity normalization are required for rule-based generation. Without them, SR/FO generation has to fall back to open-form LLM rewrites, which is exactly what all 4 lenses rejected.

### D6 — FinMem-NoOp

- **Success condition**: A rule-based NoOp clause bank (same-time-window, different normalized entity, different cluster, non-entailing) covers ≥ 80% of pilot cases with human-audited target-irrelevance. NoOp insertions on known-memorized cases produce a measurably different detector-score movement than NoOp insertions on novel cases.
- **Dominant failure mode**: The clause bank leaks — either by accidentally entailing the target (making the NoOp not actually no-op) or by disrupting CLS style enough that the detector measures generic prompt fragility, not memorization-specific brittleness.
- **Cheapest pilot**: 50 cases, rule-based clause generation + human audit of clause target-irrelevance. Tag failure causes (entailment leak, style break, time-window mismatch). Budget: ~100 LLM calls for generation; audit cost is the bottleneck.
- **Data quality gate**: Same as D5 (Thales event_type + entity normalization), plus time-window indexing over the CLS corpus for same-window clause retrieval.

### D7 — Entity-Anonymization Delta (EAD)

- **Success condition**: On high-salience cases (known-famous targets), the target-mask delta exceeds the delta on low-salience cases by a margin that is stable across detectors D1/D3/D5/D6/D8. The non-target-mask delta carries information about competing-entity distraction that is separable from the target-mask delta (i.e., the two deltas are not strongly correlated, ρ < 0.7).
- **Dominant failure mode**: Masking strips economically essential content (e.g., "证监会" → "某机构" removes the very signal that determines the policy interpretation). The detector then measures information-loss sensitivity rather than identity-keyed memory.
- **Cheapest pilot**: 50 cases, 4 mask variants (raw / target-full-anon / competitor-full-anon / both-full-anon), run through D1 and D3. Compare delta distributions and measure information loss via a simple downstream task (e.g., does the masked text still support correct sentiment labeling by a human reader?).
- **Data quality gate**: Reliable entity recognition on CLS (target span + competitor spans). Acceptable fallback if Thales entity normalization is delayed: simple rule-based matching on company names + stock codes + regulator names, which is probably good enough for pilot.

### D8 — Targeted Span Extraction

- **Success condition**: On pilot cases where manual inspection suggests verbatim memorization is plausible (long-tail repeat events with distinctive numeric content), exact-match or near-exact-match extraction rate is at least a few percent. High enough to produce concrete qualitative examples per factor stratum, not so low that the detector is empty.
- **Dominant failure mode**: Aligned models refuse or paraphrase rather than quote. Pretrained base models might extract verbatim; instruction-tuned aligned models (DeepSeek-chat, Claude) will often decline to reproduce specific spans and instead summarize, which nulls the detector without proving absence of memorization.
- **Cheapest pilot**: 100 cases with manually-marked "likely extractable" spans (numeric values, specific quoted phrases, specific regulatory language). Run masked suffix extraction across the full 6-model fleet. Measure exact match rate, near-match rate (Levenshtein), and refusal rate per model.
- **Data quality gate**: None — this detector can run on raw CLS text immediately. The only gate is sensible span selection, which can be rule-based.

### D10 — Debias Delta — DROPPED (see T6)

### D9 — RAVEN Novelty Gap — DROPPED (see T7)

### D12 candidate — Schema-Completion Probe (for Bloc 3)

This is a new proposal from this document, not from Step 1 lenses. It exists to address the Bloc 3 coverage gap flagged in §2 of the Step 1 synthesis.

- **Concept**: Give the model the opening of a CLS wire ("证监会今日宣布…", "财政部发布《…》", "公司公告：…") and score its completion. If the model completes formal-disclosure schemas (regulatory announcements, corporate filings) with systematically lower variance and higher "boilerplate fidelity" than commentary schemas, that is evidence of institutional-schema memorization — which is exactly what Bloc 3 factors (Disclosure Regime, Structured Event Type) are supposed to capture.
- **Success condition**: Schema-completion fidelity (e.g., token-level overlap with real CLS wire continuations) is measurably higher on formal disclosure types than on commentary types, and this gap scales with Cutoff Exposure (later-cutoff models show larger gaps).
- **Dominant failure mode**: Strong overlap with D3 Min-K%++ / CTS. If the schema-completion signal just tracks surface-form familiarity, D12 adds nothing that D3 does not already capture.
- **Cheapest pilot**: 40 cases split evenly between 4 institutional schemas (regulator / ministry / corporate filing / analyst commentary). 5-token prefix completion on all 6 fleet models. Measure completion fidelity per schema and partial correlation with D3.
- **Data quality gate**: Schema labels for CLS cases (requires either Thales taxonomy or lightweight rule-based classification).
- **Status**: **Optional candidate for Step 2 decision**. Step 2 agents should rule on whether D12 adds Bloc 3 coverage that is not captured by interaction-menu stratification alone (see §4).

## 4. Bloc 3 coverage gap

**Step 1 finding**: No detector in the Step 1 pool targets Bloc 3 (institutional stage / source — Structured Event Type, Disclosure Regime, Event Phase, Session Timing) as a primary. Stats explicitly flagged Bloc 3 as the most under-powered bloc for joint analysis.

**Opening position**: **Run Option 3 (interaction-menu coverage) as the baseline, AND offer D12 Schema-Completion Probe as an optional upgrade for Step 2 to rule on.**

Option 3 means: Bloc 3 factors are measured per case (via existing factor schema) and enter the analysis only through `detector × bloc-3-factor` stratification cells in the P4 interaction menu. No dedicated Bloc 3 detector is required by default. Every existing detector contributes to Bloc 3 through its response pattern across event type / disclosure regime / event phase / session timing cells.

**Evaluation question for Step 2**: Is Bloc 3 interaction-cell coverage sufficient, or does the bloc need a dedicated detector? A Step 2 agent arguing for D12 should demonstrate that Bloc 3 effect sizes are expected to be small enough that interaction-cell power (after multiplicity correction) is unreliable, and that a dedicated Bloc 3 detector would have materially better signal-to-noise on that bloc.

**Free for Step 2**: Whether D12 is adopted, replaced with a different Bloc 3 detector design, or rejected entirely in favor of Option 3 alone. Also free: whether Bloc 3 coverage in the paper is explicit ("we measure X, Y, Z in Bloc 3 via stratification") or implicit (Bloc 3 is reported only through factor results, not detector results).

## 5. Pool size and paper-structure management

**Current post-tension pool** (post-T6/T7 drops, pre-T4 resolution, pre-D12 decision):

| Detector | Status | Source |
|---|---|---|
| D1 CMMD | ✅ kept | unanimous |
| D2 PCSG | ✅ kept | Stats (single-lens but strong) |
| D3 Min-K%++/CTS | ✅ kept | 4-lens |
| D4 ADG | ⏸️ held | deferred to temporal session |
| D5 SR/FO Pair | ✅ kept as 1 slot + 2 sub-fields | 4-lens |
| D6 FinMem-NoOp | ✅ kept | 4-lens |
| D7 EAD | ✅ kept (dual role) | 2-lens detector + 2-lens field |
| D8 Extraction | ✅ kept (corroborative role) | 4-lens |
| D9 RAVEN | ❌ dropped | T7 |
| D10 Debias Delta | ❌ dropped | T6 |
| D11 Temporal Dose-Response | ⏸️ candidate | temporal session |
| D12 Schema-Completion | ⏸️ candidate | this doc |

**Working count**: 7 definite + D4 pending + D11/D12 candidates = 7-10 detectors in the active pool.

**Opening position on pool size management**: **Do not prune further at Step 2 opening**. The user explicitly prefers a broader pool to be narrowed later by data quality and pilot evidence rather than by lens consensus at this stage. Editor's "5-detector hard ceiling" argument applies to **main-text paper real estate**, not to the detector pool itself; pool-to-paper selection is a downstream decision based on pilot results.

**Paper-structure management for Step 2 to decide**: When Step 2 does approach main-text selection, two architectures are available:

- **Architecture A — 4-5 detector family slots with internal sub-measurements**: Group the pool into 4-5 "detector families" (surface / counterfactual / cross-model / extraction / bloc-3-schema) and let each family slot carry 1-3 internal sub-measurements. This is Editor's page-budget number without Stats's independence loss.
- **Architecture B — 4-5 true detectors with the rest in appendix**: Main text carries 4-5 independent detectors; remaining detectors are reported in a supplementary materials section.

**Opening position**: **Lean toward Architecture A** but do not lock it. Step 2 should revisit once D4 and D11/D12 are settled.

## 6. Explicit freedoms Step 2 agents have

To avoid any ambiguity, Step 2 Codex lens agents can:

- **Overturn any of the 7 tension positions (T1-T7)** with evidence or a construct-validity argument. Default stances are the starting point, not the conclusion.
- **Propose new detectors** beyond the Step 1 pool and this document's D12 candidate. The pool is open.
- **Propose new factors** if they are load-bearing for detector evaluation. The v6.2 "no new factors in R5" rule is softened to "do not derail detector discussions with factor debates" — proposals that are directly tied to detector design are welcome.
- **Revise the Bloc 3 approach** entirely. Option 1 (accept the gap) is back on the table if a strong argument supports it.
- **Change the pool architecture** (A vs B in §5) or propose a third architecture.
- **Revise the success condition / failure mode framing** in §3 for any detector. Those are first-cut judgments and are explicitly open to challenge.

To avoid chaos, Step 2 agents should NOT:

- **Re-open D4 ADG** — it is held for the temporal session, not Step 2.
- **Re-open the core 7 Step 1 consensus items** (see §3 of R5A_STEP1_SYNTHESIS.md): independent reporting over ensemble; deviate from MemGuard-Alpha's 5-MIA stack; CMMD is a top-3 pick; FinMem-NoOp must be rule-based first; EAS split into target/non-target deltas; accept Meeus 2024 SoK restriction on surface-form framing; 4-5 main text + 1-2 reserve target as a paper-structure target (pool size itself is open per §5). These were unanimous in Step 1 and should not be relitigated without new evidence.
- **Lock implementation specifics** — the later implementation session handles perturbation protocols, prompt variants, sample counts per case, decoding parameters, and related details. Step 2 should not pre-empt that session.

## 7. What Step 2 is expected to produce

Step 2 runs another 4-Codex-agent pass (Quant / NLP / Stats / Editor), each of which:

1. Reads this document + their own Step 1 output.
2. For each of T1-T7, states: agree / disagree / modify, with reasons.
3. For each detector in §3, states: keep / drop / reshape, with reference to the success condition and failure mode.
4. Answers the open questions in §3 of the Step 1 synthesis that fall within their lens competence.
5. Rules on the Bloc 3 gap: Option 1 / Option 3 / Option 3 + D12 / alternative proposal.
6. Rules on pool architecture A vs B.
7. Flags any Step 2-visible issue that should block R5A closure.

After Step 2: Challenger pass (cross-model check by Claude) → cold-reader pass (adversarial review) → R5A closes with a frozen conceptual shortlist. R5B (executable shortlist) then converges pending Thales pipeline / point-in-time / annotation tracks.

## 8. Reading order for Step 2 agents

1. `BENCHMARK_R5_KICKOFF.md` — the full R5 context packet (if not already in context)
2. `docs/DECISION_20260413_mvp_direction.md` v6.2 — authoritative factor and methodology state
3. `R5A_STEP1_SYNTHESIS.md` — Step 1 synthesis with cross-lens matrix and the 7 tensions
4. The Step 1 lens output that corresponds to the agent's own role (`quant_lens.md`, `nlp_lens.md`, `stats_lens.md`, `editor_lens.md`)
5. **This document** — opening positions and freedoms
6. (Upcoming) `R5A_TEMPORAL_CUE_DESIGN.md` — temporal cue design session output (when available)
7. (Upcoming) `FLEET_REVIEW_20260415.md` — fleet re-review session output (when available)

Items 6 and 7 are not yet written and are prerequisites for resolving D4 and finalizing CMMD/PCSG access requirements, respectively.
