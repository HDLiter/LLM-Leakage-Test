# BENCHMARK R5 — Detector Investigation Kickoff

**Date created:** 2026-04-13 (end of R4, amended after post-v5.2 integration review)
**Status:** PENDING — to be started in a new session AFTER the R4 literature sweep completes
**Predecessor:** R4 conceptually closed. See `BENCHMARK_R4_FINAL_SYNTHESIS.md` and `docs/DECISION_20260413_mvp_direction.md` **v5.2** (v5.1 dropped Reprint Status; v5.2 integrated CMMD 6-model fleet + Thales signal profile findings + hierarchical Event Type + per-factor construct caveats). **R4 literature sweep (`BENCHMARK_R4_LIT_SWEEP_KICKOFF.md`) must run before R5** to prevent further MemGuard-Alpha-style prior-art surprises.

This document is a self-contained context packet for whoever opens R5 in a new conversation. It bundles everything the next session needs to start cleanly without re-reading R1-R4 in full.

---

## Project one-liner

FinMem-Bench is a factor-controlled Chinese financial memorization-detection benchmark built on the CLS (财联社) telegraph corpus. R4 (just closed) determined WHICH factors to measure per case. R5 determines WHICH detectors to run on top of those factors.

The dependent variable: a memorization detector score per case per detector per model. The independent variables: 12 pre-registered factors. The estimand family: factor × detector interactions.

## Required reading before starting R5

1. **`docs/DECISION_20260413_mvp_direction.md` v5.2** — the authoritative decision document (v5.2, NOT v5). Especially:
   - "R4 Step 1 + Step 2 outcome: 12-factor shortlist" — the locked factor list
   - "Methodology principles (P1-P5)"
   - "R4 Step 2 convergent risks (R1-R4)" — especially R4 (construct collapse)
   - "Open considerations for downstream tracks" — includes the accepted CMMD 6-model fleet
   - Version history section — read v5.1 and v5.2 entries specifically to understand what changed from v5
2. **`docs/CMMD_MODEL_FLEET_SURVEY.md`** — the full CMMD 6-model fleet survey, including cost estimates, reproducibility landmines, and fallback options. R5 starts from this fleet as the default and either pins or amends with justification.
3. **`docs/THALES_SIGNAL_PROFILE_REVIEW.md`** — Thales topic / modality / authority review. Relevant for understanding the Modality-as-possible-replacement-for-Disclosure-Regime decision and the Authority-as-possible-extra-corpus-factor decision (both deferred to Thales dedicated session).
4. **`refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md`** — the R4 closure document
5. **`refine-logs/reviews/BENCHMARK_R4_FINAL_REVIEW.md`** — cold reader's critique of R4
6. **`refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md`** — integration review that triggered v5.2 cleanup
7. **If the R4 literature sweep has completed**, also read: `docs/FACTOR_LITERATURE_PROVENANCE.md` and `docs/LITERATURE_SWEEP_2026_04.md` + any new papers it added
8. **Two relevant prior-art papers** (recently added to library):
   - `related papers/MemGuard-Alpha Memorization Financial Forecasting.pdf` (Roy & Roy 2026, arxiv 2603.26797) — direct competitor; proposes MCS + CMMD detector framework
   - `related papers/GSM-Symbolic Understanding Reasoning Limits.pdf` (Mirzadeh et al. 2024, arxiv 2410.05229) — methodological precedent for surface-invariant perturbation as memorization diagnostic
9. **Library memorization-detection notes**: `related papers/notes/memorization_extraction.md`, `related papers/notes/contamination_detection.md`, `related papers/notes/temporal_lookahead.md`

## R5 scope

**In scope**:
- Detector landscape survey (what detection methods exist for LLM memorization)
- Detector candidate shortlist (which methods we will actually run on FinMem-Bench)
- Per-detector access requirements (white-box vs black-box, logprob access vs not)
- Per-detector compute budget estimate
- Per-detector mapping to the 12 factors (which detectors are most informative on which factors)
- Detector-dependent stratification fields (per Principle P5: each detector may contribute 1-2 schema fields)
- Ensemble vs single-detector strategy
- White-box vs black-box framing (DeepSeek logprobs broken; Qwen / Llama / Baichuan / Yi available)
- CMMD (Cross-Model Memorization Disagreement) feasibility on Chinese model fleet
- FinMem-NoOp probe design (analog of GSM-NoOp for CLS news)

**Out of scope**:
- Adding or removing factors from the shortlist (R4 locked them)
- Re-discussing methodology principles P1-P5 (locked)
- Algorithmic specification of clustering, entity extraction, or event-type taxonomy (Thales-joint track)
- Point-in-time market mechanics field list (point-in-time track)
- LLM annotation protocol details (annotation track)
- Pre-registration wording (R6)
- Timeline commitment (user decision)

## R4 → R5 frozen inputs (do NOT relitigate)

1. The 12-factor shortlist is locked. R5 chooses detectors that operate ON these factors, not new factors.
2. Methodology principles P1-P5 are binding. P5 specifically says "detector-dependent factors are R5 territory" — this is your green light to design detector-specific stratification fields.
3. Risks R1-R4 carry forward. Especially R4 (construct collapse): R5 detector choices should NOT amplify the prominence/repetition correlation bloc. If a detector is most sensitive to surface reuse (Min-K%, char-ngram methods), recognize that it will produce signals on bloc 1 (Propagation Intensity including its event_burst + historical_family_recurrence terms, Template Rigidity, surface_template_recurrence robustness companion) regardless of memorization, and pair it with detectors sensitive to other constructs. **Note**: Reprint Status was dropped in v5.1 — it is no longer part of bloc 1 or any factor list.
4. Target N = 3,200 gross clusters (initial reference) with stopping-rule adaptive sampling.
5. Case text for memorization measurement = CLS text. Always.
6. Pre-commit granularity = 档位 2 偏 1.
7. Editor's narrative hierarchy (spine / secondary / auxiliary / control / reserve) — affects how R5 presents detector choices in the paper structure.
8. Construct caveats per factor (in v5): every factor has a "what is actually measured vs what the name suggests" annotation. R5 should respect these caveats when designing detector-factor matchings.

## R4-derived seed inputs to R5

These are NEW pieces of information that R5 should treat as starting points:

### Seed 1 — Detector candidates surfaced during R4

These came up during R1-R4 discussion or via the 2 new prior-art papers. R5 should NOT treat this as a final list — it is the starting brainstorm pool:

- **Min-K%** (Shi et al. 2024) — already in library: `Detecting Pretraining Data from Large Language Models.pdf`
- **Min-K%++** — variant of Min-K%
- **PatentMIA** — already in library: `Detecting Pretraining Data from Large Language Models.pdf` references it; also `notes/contamination_detection.md` mentions it
- **Membership Inference Attack family** — already in library: `Do Membership Inference Attacks Work on Large Language Models.pdf`
- **Extraction attacks (Carlini-style)** — already in library: `Extracting Training Data from LLMs 2020.pdf`, `Scalable Extraction of Training Data from Language Models.pdf`
- **Counterfactual probes — Semantic Reversal (SR)** — project's own prior work
- **Counterfactual probes — False Outcome (FO)** — project's own prior work
- **FinMem-NoOp** — NEW from GSM-Symbolic: insert irrelevant-but-plausible clause and observe prediction change. Distinct from SR (changes fact) and FO (substitutes outcome). Needs design work.
- **CMMD (Cross-Model Memorization Disagreement)** — NEW from MemGuard-Alpha: run multiple LLMs with different cutoffs, compare outputs, disagreement among models signals which subset memorized. Needs Chinese model fleet survey.
- **PaCoST** — already in library: `PaCoST.pdf`
- **CLEAN-EVAL** — already in library
- **VarBench** — already in library
- **LastingBench** — already in library
- **Rephrased contamination detection (Golchin & Surdeanu)** — already in library: `Time Travel in LLMs Tracing Contamination.pdf`
- **AntiLeakBench** — already in library
- **Perplexity-based**: zlib-ratio, reference-ratio (multiple papers in library)

### Seed 2 — Open questions R5 must explicitly answer

These were left open by R4 because they belong to R5:

1. **Ensemble vs single-detector strategy** — MemGuard-Alpha uses 5 MIA methods + logistic regression. Should FinMem-Bench detector layer also be an ensemble, or a set of independent detectors reported side-by-side? (Trade-off: ensemble has stronger signal but harder to interpret per-factor; independent detectors are weaker but more interpretable.)

2. **White-box vs black-box split** — DeepSeek-chat has broken logprobs in the existing infrastructure (documented in project memory `infra_capabilities.md`). White-box detectors (Min-K%, MIA, perplexity) can ONLY run on Qwen / GLM / local vLLM models. The v5.2 CMMD fleet provides 3 local white-box members (Qwen 2.5-7B, GLM-4-9B-0414, Qwen3-14B) and 3 black-box hosted members. **Open question**: does R5 commit to white-box primary / black-box secondary, or vice versa? Or both as parallel tracks reported side-by-side? This affects the detector × model matrix shape.

3. **CMMD feasibility** — **v5.2 accepted a 6-model reference fleet** (see `docs/CMMD_MODEL_FLEET_SURVEY.md`):
   1. Qwen 2.5-7B-Instruct (local, cutoff 2023-10, white-box)
   2. DeepSeek-V2.5 (OpenRouter, cutoff ~2024-03, black-box)
   3. GLM-4-9B-0414 (local, cutoff 2024-06-30 — ONLY officially-documented cutoff, white-box)
   4. DeepSeek-V3 `deepseek-chat-v3-0324` (OpenRouter, cutoff 2024-07, black-box)
   5. Qwen3-14B (local, cutoff 2025-01, white-box)
   6. Claude Sonnet 4.5 `claude-sonnet-4-5-20250929` (OpenRouter, cutoff 2025-01 reliable / 2025-07 extended, black-box, non-Chinese-vendor diversity)
   R5 should **start from this fleet as the default** and either pin it into pre-commit OR amend with explicit justification (e.g., if the R4 literature sweep surfaces DatedGPT or ChronoBERT/GPT as viable additions). **Critical reproducibility requirement**: pre-commit MUST pin to dated checkpoints (`-0324`, `-20250929`, `-0414`, HF commit SHAs) and lock OpenRouter provider routing.

4. **FinMem-NoOp design** — what counts as "irrelevant but plausible" in CLS? How is it generated? Is it LLM-generated (introducing a new annotation dependency) or rule-based (e.g., insert a sentence about an unrelated ticker drawn from the same time window)? The design question is: how much information does the inserted clause carry, and how is "irrelevant" verified?

5. **Detector-dependent factors** (Principle P5) — each detector may contribute 1-2 stratification fields. R5 must list them per detector. Examples that came up in discussion:
   - `text_reversibility_score` for SR/FO
   - `extractable_span_density` for extraction attacks
   - `logprob_tail_length` for Min-K%
   - `token_perplexity_variance` for MIA
   - `cross_model_agreement_score` for CMMD

6. **Integration with factor shortlist** — for each (detector, factor) pair, write a one-sentence prediction of how informative the detector is on that factor. Some detectors will be informative on most factors; others will be specialized. The detector × factor matrix is the core R5 deliverable.

### Seed 3 — Construct-collapse mitigation guidance for R5

Risk R4 (construct collapse) implies that **R5 should deliberately diversify detector mechanism families** so that the eventual analysis produces evidence from independent sources, not from 5 detectors that all measure the same surface-form sensitivity.

Recommended detector family diversification:

- At least 1 from **surface-form sensitivity** family (Min-K%, char-ngram, perplexity)
- At least 1 from **counterfactual perturbation** family (SR, FO, FinMem-NoOp)
- At least 1 from **cross-model disagreement** family (CMMD)
- At least 1 from **extraction / verbatim recall** family (Carlini-style)
- At least 1 from **temporal-cutoff-conditional** family (any detector that uses cutoff metadata)

If 4 of 5 detectors are surface-form sensitive, R4's prominence/repetition bloc will dominate every result.

## R5 process recommendation

The cold reader recommended **splitting R5 into R5A and R5B**:

- **R5A — Conceptual shortlist**: detector landscape survey, family identification, conceptual matching to factors. Independent of execution gates.
- **R5B — Executable shortlist**: pruning R5A's conceptual shortlist by feasibility — depends on Thales pipeline outputs being defined, model cutoff metadata being available, and CMMD model fleet being verified.

**R5A can start immediately in a new session**. R5B waits for Thales-joint algorithm session and point-in-time analysis track to make progress.

R5A would still use the 4-Codex-agent + Challenger structure, with these role adaptations:

- **Quant** — alpha-bridge angle: which detectors give signals that survive translation to alpha contamination claims; CMMD's relevance to Thales downstream
- **NLP** — methodology angle: which detector families have the strongest construct validity arguments; FinMem-NoOp design
- **Stats** — power and identification: detector-factor matrix power calc; multiple-comparison family across detectors
- **Editor** — narrative angle: how many detectors fit the paper's central claim without scope creep; venue fit (does the detector list pull toward EMNLP or finance venue)
- **Challenger** — same role, look for detector-family blind spots from a non-Codex perspective

## What to NOT spend R5 time on

Per the cold reader's recommendation:
- Don't try to lock R5B before Thales / point-in-time / annotation tracks make progress
- Don't propose new factors (R4 locked the list)
- Don't redesign methodology principles
- Don't relitigate venue-drift or alpha-bridge — those are settled at narrative level
- Don't try to commit to a timeline — that's a user decision

## Items to bring forward from R4 that should influence R5

1. The Anchor Strength 150-case experiment must run BEFORE any memorization detector is run on the main corpus. R5 should explicitly schedule this as an R5 prerequisite, not assume it happens out-of-band.
2. The cluster-free robustness companion to Propagation Intensity uses char-5gram TF-IDF — this is a detector-adjacent technique. R5 should be aware that this companion is a "detector lite" already in the factor schema.
3. Construct caveats per factor (in v5) directly affect R5 — for example, "Cutoff Exposure is timing not exposure" means R5 detectors should compute factors that are time-aware AND robust to cutoff misclassification.

## Suggested R5 first-session agenda

1. Read all required documents (above)
2. Run R5A Step 1 — 4 Codex agents in parallel propose detector candidates from each lens. Each agent should produce 5-8 candidates with concept, mechanism, access requirement, factor relevance, ensemble compatibility
3. Orchestrator synthesis of R5A Step 1 (likely a 15-20 detector candidate pool)
4. **Insert a literature review pass** (see "Open question: literature review timing" below) — this is the recommended insertion point per the user's question about a broad lit review
5. R5A Step 2 — 4 Codex agents review the integrated detector shortlist + literature review findings; converge on 5-8 final detectors
6. Challenger pass for cross-model blind spots
7. Cold-reader pass (analogous to R4)
8. R5A closes with a frozen detector shortlist that R5B can pick up when its dependencies resolve

---

## Literature review sequencing (resolved after v5.2 integration review)

The earlier version of this kickoff proposed splitting literature review into "targeted detector sweep inside R5 + broad review after R5." That has been **superseded** by a different sequencing after the post-v5.2 integration review:

**Final sequencing (v5.2)**:

1. **R4 Literature Sweep** — runs in a **fresh session BEFORE R5**. See `BENCHMARK_R4_LIT_SWEEP_KICKOFF.md` for the full scope. This sweep owns:
   - Per-factor literature provenance check for all 12 active + 3 reserve + 2 possible-addition factors
   - Broad 2024-2026 sweep for memorization / contamination / financial NLP / factor-controlled benchmark papers we may have missed
   - Chronologically-controlled baseline investigation (DatedGPT, ChronoBERT/ChronoGPT, Time Machine GPT, FINSABER) for possible CMMD fleet additions
   - Cited-but-unread sweep from existing library
   - Construct-collapse 3-bloc validation against published work
   - Output: appendix to v5.2 → v6 of the decision document

2. **R5 Detector Investigation** — runs in a **fresh session AFTER the R4 literature sweep completes**. R5 does NOT run its own literature sweep; it inherits the R4 sweep's output. R5 scope is strictly detector selection, operationalization, and factor × detector matrix design.

3. **R5 targeted detector-focused spot checks** — if during R5 Step 1 brainstorm a specific detector family is unclear about its recent state of the art, R5 can run small targeted arxiv searches. This is bounded spot-checking, NOT a broad sweep.

**Why this sequencing**: the R4 literature sweep produces factor provenance that R5 needs to design detectors that are genuinely informative per factor. Running R5 first would risk picking detectors on factors whose literature grounding is still weak. MemGuard-Alpha being discovered post-R4 is exactly the kind of surprise the R4 sweep is designed to prevent.

**If the user chooses to skip the R4 literature sweep** (only option if timeline is extremely tight), R5 can still proceed but R5 Step 1 must include a tighter targeted sweep for each proposed detector, and construct-collapse mitigation becomes weaker.

---

## Ready for next session

When the user opens R5 in a new conversation, the new session should:

1. Read this kickoff document first
2. Read the required reading list
3. Decide on the literature review timing question above
4. Decide whether to run R5A Step 1 immediately or do the targeted literature sweep first
5. Begin R5

The new session does NOT need to re-read R1-R4 reviews in full unless a specific question requires it. **v5.2 of the decision document is the authoritative state.**
