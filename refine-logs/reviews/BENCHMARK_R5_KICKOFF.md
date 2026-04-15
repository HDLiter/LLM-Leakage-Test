# BENCHMARK R5 — Detector Investigation Kickoff

**Date created:** 2026-04-13 (end of R4)
**Status:** PENDING — to be started in a new session
**Predecessor:** R4 closed (conceptually). See `BENCHMARK_R4_FINAL_SYNTHESIS.md` and `docs/DECISION_20260413_mvp_direction.md` v5.

This document is a self-contained context packet for whoever opens R5 in a new conversation. It bundles everything the next session needs to start cleanly without re-reading R1-R4 in full.

---

## Project one-liner

FinMem-Bench is a factor-controlled Chinese financial memorization-detection benchmark built on the CLS (财联社) telegraph corpus. R4 (just closed) determined WHICH factors to measure per case. R5 determines WHICH detectors to run on top of those factors.

The dependent variable: a memorization detector score per case per detector per model. The independent variables: 12 pre-registered factors. The estimand family: factor × detector interactions.

## Required reading before starting R5

1. **`docs/DECISION_20260413_mvp_direction.md` v5** — the authoritative decision document. Especially:
   - "R4 Step 1 + Step 2 outcome: 12-factor shortlist" — the locked factor list
   - "Methodology principles (P1-P5)"
   - "R4 Step 2 convergent risks (R1-R4)" — especially R4 (construct collapse)
   - "Open considerations for downstream tracks"
2. **`refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md`** — the R4 closure document
3. **`refine-logs/reviews/BENCHMARK_R4_FINAL_REVIEW.md`** — cold reader's critique of R4
4. **Two relevant prior-art papers** (recently added to library):
   - `related papers/MemGuard-Alpha Memorization Financial Forecasting.pdf` (Roy & Roy 2026, arxiv 2603.26797) — direct competitor; proposes MCS + CMMD detector framework
   - `related papers/GSM-Symbolic Understanding Reasoning Limits.pdf` (Mirzadeh et al. 2024, arxiv 2410.05229) — methodological precedent for surface-invariant perturbation as memorization diagnostic
5. **Library memorization-detection notes**: `related papers/notes/memorization_extraction.md`, `related papers/notes/contamination_detection.md`

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
3. Risks R1-R4 carry forward. Especially R4 (construct collapse): R5 detector choices should NOT amplify the prominence/repetition correlation bloc. If a detector is most sensitive to surface reuse (Min-K%, char-ngram methods), recognize that it will produce signals on bloc 1 (Propagation, Template, Reprint) regardless of memorization, and pair it with detectors sensitive to other constructs.
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

2. **White-box vs black-box split** — DeepSeek has broken logprobs (per `infra_capabilities.md` memory). White-box detectors (Min-K%, MIA, perplexity) can ONLY run on Qwen / Llama / Baichuan / Yi etc. Does R5 commit to white-box primary / black-box secondary, or vice versa? Or both as parallel tracks?

3. **CMMD feasibility** — can we assemble 3-4 Chinese LLMs with genuinely different training cutoffs?
   - Qwen 2.5 7B (cutoff ≈ 2024-03 to 2024-08)
   - Qwen 2 7B (cutoff ≈ 2023-08 to 2024-03)
   - DeepSeek-chat (cutoff approximate, possibly mid-2024)
   - ChatGLM3-6B (cutoff ≈ 2023-10)
   - Baichuan2-7B (cutoff ≈ 2023-09)
   - Yi-6B / Yi-9B (cutoff ≈ 2024)
   - InternLM2 7B (cutoff ≈ 2024)
   - DeepSeek-v3 (cutoff ≈ 2024-08)
   R5 needs to verify cutoffs and pick at least 3 with non-overlapping windows.

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

## Open question for the user before starting R5: literature review timing

The user (end of R4) raised the idea of a **broad literature review** after R5 — covering local papers + new online papers + papers cited by local papers — given how much value MemGuard-Alpha and GSM-Symbolic added to R4.

The orchestrator's recommendation (to be discussed before R5 starts):

**Yes, do a broad literature review. But split the timing into TWO passes**:

1. **Targeted detector-family sweep INSIDE R5**, between R5A Step 1 (brainstorm) and R5A Step 2 (shortlist convergence). This sweep specifically asks: "for each detector family proposed in Step 1, are there recent papers (2024-2026) we should be aware of that change our understanding of the family's strengths or weaknesses? Are there detector families we missed entirely?" This is BOUNDED — it scopes to detector papers only — and it directly informs R5A Step 2. Without this, R5 risks missing CMMD-equivalent gaps in our knowledge.

2. **Broad open-ended literature review AFTER R5 closes**, before paper-writing begins. This sweep covers: (a) all papers relevant to FinMem-Bench's claim (memorization, contamination, financial NLP, factor-controlled benchmarks), (b) papers cited by the papers we already have but we haven't read, (c) new papers from the last 6 months across these topics, (d) papers we may have missed because they are in adjacent fields (cognitive science, mechanistic interpretability, causal inference for ML). This sweep produces the related-work section of the paper and surfaces any framing risks before submission.

**Why split**: a single broad review before R5 wastes effort on detector-irrelevant papers; a single broad review after R5 leaves R5 vulnerable to CMMD-style misses. The split gives R5 tactical input early and the paper writing stage strategic input late.

**Why MemGuard-Alpha matters here**: it was discovered AFTER R4 closed. If we had done the targeted sweep at R4 entry, we might have absorbed it as input rather than as a post-hoc patch. R5 should not repeat this mistake.

---

## Ready for next session

When the user opens R5 in a new conversation, the new session should:

1. Read this kickoff document first
2. Read the required reading list
3. Decide on the literature review timing question above
4. Decide whether to run R5A Step 1 immediately or do the targeted literature sweep first
5. Begin R5

The new session does NOT need to re-read R1-R4 reviews in full unless a specific question requires it. v5 of the decision document is the authoritative state.
