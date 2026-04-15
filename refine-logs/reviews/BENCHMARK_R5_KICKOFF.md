# BENCHMARK R5 — Detector Investigation Kickoff

**Date created:** 2026-04-13 (end of R4)
**Last synced:** 2026-04-15 (to decision doc v6.2 + R4 literature sweep Session 1 + Session 2 outputs)
**Status:** **READY** — R4 literature sweep complete (Sessions 1 + 2). R5A conceptual shortlist can start immediately in a new session. R5B executable shortlist still waits for Thales / point-in-time / annotation tracks.
**Predecessor:** R4 conceptually closed. See `BENCHMARK_R4_FINAL_SYNTHESIS.md` and `docs/DECISION_20260413_mvp_direction.md` **v6.2** (current authoritative state).

This document is a self-contained context packet for whoever opens R5 in a new conversation. It bundles everything the next session needs to start cleanly without re-reading R1-R4 in full.

---

## Project one-liner

FinMem-Bench is a factor-controlled Chinese financial memorization-detection benchmark built on the CLS (财联社) telegraph corpus. R4 (closed) determined WHICH factors to measure per case. R5 determines WHICH detectors to run on top of those factors.

The dependent variable: a memorization detector score per case per detector per model. The independent variables: 12 pre-registered factors (plus 5 reserve). The estimand family: factor × detector interactions.

---

## Required reading before starting R5

### Primary authoritative state

1. **`docs/DECISION_20260413_mvp_direction.md` v6.2** — the authoritative decision document. **Do NOT read older versions.** Especially:
   - "R4 Step 1 + Step 2 outcome: 12-factor shortlist" — the locked factor list with v6 literature provenance additions per factor
   - "Factor literature provenance summary" (v6) — novelty distribution table (5 STRONG / 8 PARTIAL / 2 NOVEL)
   - "Methodology principles (P1-P5)"
   - "Risk R4 — Construct collapse" — **now a 4-bloc decomposition per v6.1 refinement** (Cutoff Exposure separated as its own Bloc 0 / "temporal exposure" bloc); downgraded from "validated latent structure" to "descriptive working hypothesis"
   - "Reserve (5 items)" — Exact-Span Rarity, Cluster Temporal Span, Interaction Menu, **Influence/Relevance (v6.2)**, **Eliteness (v6.2)**
   - "Dropped in v6.2" — Geographical Proximity explicitly dropped
   - "R5 reading queue (new P1 papers from R4 literature sweep)" — 8 new papers R5 should consider
   - "CMMD model fleet" — **v6 verdict table**, fleet unchanged from v5.2/v5.3 reference
   - Version history entries v6 / v6.1 / v6.2 — read all three to understand what changed post-R4 literature sweep

### R4 literature sweep outputs (mandatory — these did not exist at R5 kickoff creation time)

2. **`docs/FACTOR_LITERATURE_PROVENANCE.md`** — per-factor literature audit (Sub-task A). Tells R5 which factors have strong prior art (and which don't) so detector design is grounded.
3. **`docs/LITERATURE_SWEEP_2026_04.md`** — consolidated sweep report across Sub-tasks A-E. Read the executive summary, the Sub-task C chronological baseline verdict table (for CMMD fleet context), the Sub-task E construct-validity refinement (for Risk R4 framing), and the final Candidate new-factor queue section.
4. **`docs/MEDIA_COVERAGE_FEASIBILITY.md`** — feasibility analysis for the Coverage Breadth / Media Coverage candidate factor. R5 must treat Coverage Breadth as **NOT available** as a production factor and assume the pilot runs in parallel with R5 (not as a blocker).
5. **`docs/CMMD_MODEL_FLEET_SURVEY.md`** — the full CMMD 6-model fleet survey. **v6.2 verdict: fleet stands unchanged.** DatedGPT, ChronoBERT/ChronoGPT, Time Machine GPT, StoriesLM, NoLBERT, and FINSABER are METHOD_ONLY cited precedents, NOT fleet members (see v6 CMMD block in decision doc).
6. **`docs/THALES_SIGNAL_PROFILE_REVIEW.md`** — Thales topic / modality / authority review. Still relevant for understanding Modality-as-possible-replacement-for-Disclosure-Regime and Authority operationalization (both deferred to Thales dedicated session).

### R1-R4 review chain (for context, not for relitigation)

7. **`refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md`** — R4 closure document
8. **`refine-logs/reviews/BENCHMARK_R4_FINAL_REVIEW.md`** — cold reader's critique of R4 (biggest risk: construct collapse, now refactored to 4-bloc in v6.1)
9. **`refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md`** — integration review that triggered v5.2 cleanup
10. **`refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md`** — the edit proposal log for v6 / v6.1 / v6.2 changes, useful to understand why specific v6.x edits exist
11. **`refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md`**, **`LIT_SWEEP_B_BROAD_SWEEP.md`**, **`LIT_SWEEP_C_CHRONO_BASELINES.md`**, **`LIT_SWEEP_D_CITED_BUT_UNREAD.md`**, **`LIT_SWEEP_E_CONSTRUCT_VALIDATION.md`** — raw sweep outputs (only read if a specific detail in the consolidated report is ambiguous)

### Prior art papers in library (substantially expanded by the sweep)

The library now contains **40+ papers** in the memorization / contamination / temporal / financial NLP / construct-validity families. Of special relevance to R5:

**Direct competitors or closest prior art:**
- `MemGuard-Alpha Memorization Financial Forecasting.pdf` (Roy & Roy 2026, arxiv 2603.26797) — closest direct competitor; proposes MCS + CMMD detector framework
- `Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf` (Li et al. 2025, arxiv 2510.07920) — finance-LLM leakage benchmark; reviewer-visible
- `Look-Ahead-Bench Standardized Benchmark.pdf` (Benhenda 2026, arxiv 2601.13770) — standardized look-ahead benchmark for PiT LLMs in finance
- `LiveTradeBench Real-World Alpha LLM.pdf` (Yu et al. 2025, arxiv 2511.03628) — live-streaming backtest alternative that rejects offline contamination; cites Profit Mirage

**MIA and privacy foundations (added by Sub-task D):**
- `MIA Against Machine Learning Models.pdf` (Shokri et al. 2017, arxiv 1610.05820) — foundational MIA paper
- `MIA From First Principles.pdf` (Carlini et al. 2022, arxiv 2112.03570) — strongest post-Shokri baseline; MemGuard builds on this
- `Min-K++ Detecting Pretraining Data.pdf` (Zhang et al. 2024, arxiv 2404.02936) — direct Min-K% follow-up
- `Inherent Challenges Post-Hoc MIA LLMs.pdf` (Meeus et al. 2024, arxiv 2406.17975, aka SoK: Rushing Nowhere) — skepticism paper on the MIA family
- `RAVEN Linguistic Novelty LMs.pdf` (McCoy et al. 2021, TACL) — bridges memorization ↔ output novelty
- `Memorization Without Overfitting.pdf` (Tirumala et al. 2022, arxiv 2205.10770) — training dynamics theory

**Temporal / cutoff / chronological controls:**
- `Chronologically Consistent Large Language Models.pdf` (He et al. 2025, arxiv 2502.21206) — ChronoBERT/ChronoGPT, HF public
- `DatedGPT Preventing Lookahead Bias.pdf` (Yan et al. 2026, arxiv 2603.11838) — 12 × 1.3B annual cutoffs 2013-2024
- `Dated Data Tracing Knowledge Cutoffs.pdf` (Cheng et al. 2024)
- `Set the Clock Temporal Alignment LMs.pdf` (Zhao et al. 2024)
- `A Test of Lookahead Bias in LLM Forecasts.pdf` (Gao et al. 2026)
- `All Leaks Count, Some Count More Interpretable Temporal.pdf` (Zhang et al. 2026)
- `Fake Date Tests LLM Macro Forecasting.pdf`
- `Fast Effective Solution Look-ahead Bias LLMs.pdf` (Merchant & Levy 2025, arxiv 2512.06607) — inference-time mitigation
- `Do LLMs Understand Chronology.pdf` (Wongchamcharoen & Glasserman 2025, arxiv 2511.14214) — prerequisite paper for prompt-based boundaries
- `Time Machine GPT.pdf` (Drinkall et al. 2024, arxiv 2404.18543) — chrono-control precursor, HF public Ti-Ma/TiMaGPT2-*
- `Lookahead Bias in Pretrained LMs.pdf` (Sarkar & Vafa 2024) — direct conceptual predecessor
- `Caution Ahead Numerical Reasoning Look-ahead.pdf` (Levy 2024) — finance look-ahead + numerical reasoning
- `Memorization Problem LLMs Economic Forecasts.pdf` (Lopez-Lira 2025)
- `RealTime QA.pdf` (Kasai et al. 2022) — temporal-QA benchmark precursor
- `AIs Predictable Memory Financial Analysis.md` (Didisheim et al. 2025, from HTML→markdown) — finance memorization as measurable proxy

**Counterfactual / construct-validity methodology (added by Sub-task E):**
- `GSM-Symbolic Understanding Reasoning Limits.pdf` (Mirzadeh et al. 2024, arxiv 2410.05229) — surface-invariant perturbation precedent; seeds FinMem-NoOp probe
- `Anonymization and Information Loss.pdf` (Wu et al. 2025, arxiv 2511.15364) — anonymization tradeoff in finance sentiment
- `Quantifying Construct Validity LLM Evaluations.pdf` (Kearns 2026, arxiv 2602.15532) — latent factor models vs scale vs measurement error
- `Construct Validity LLM Nomological Networks.pdf` (Freiesleben 2026, arxiv 2603.15121) — nomological network argument
- `Evaluating NLG Metrics Measurement Theory.pdf` (Xiao et al. 2023, EMNLP) — MTMM + factor analysis for NLP eval
- `Structure of LM Capabilities Factor Analysis.pdf` (Burnell et al. 2023, arxiv 2306.10062) — factor analysis precedent
- `BenchBench Benchmark Agreement.pdf` (Perlitz et al. 2024, arxiv 2407.13696) — benchmark correlation stability

**Already-read essentials (Min-K%, MIA, contamination, extraction, entity memorization):**
- `Detecting Pretraining Data from Large Language Models.pdf` (Shi et al. 2024, Min-K%)
- `Do Membership Inference Attacks Work on Large Language Models.pdf`
- `Counterfactual Memorization in Neural Language Models.pdf`
- `Quantifying Memorization Across Neural LMs.pdf`
- `Entity-level Memorization in LLMs.pdf` (Zhou et al. 2023)
- `Secret Sharer Unintended Memorization.pdf`
- `Scalable Extraction of Training Data from Language Models.pdf`
- `Extracting Training Data from LLMs 2020.pdf`

**Topic notes**: `related papers/notes/memorization_extraction.md`, `contamination_detection.md`, `temporal_lookahead.md`, `financial_nlp.md` (all substantially expanded by Sessions 1 + 2).

---

## R5 scope

**In scope**:
- Detector landscape survey (what detection methods exist for LLM memorization)
- Detector candidate shortlist (which methods we will actually run on FinMem-Bench)
- Per-detector access requirements (white-box vs black-box, logprob access vs not)
- Per-detector compute budget estimate
- Per-detector mapping to the 12 factors (which detectors are most informative on which factors)
- Detector-dependent stratification fields per Principle P5 (each detector may contribute 1-2 schema fields) — **including Entity-Anonymization Sensitivity seeded from Sub-task E**
- Ensemble vs single-detector strategy
- White-box vs black-box framing (DeepSeek logprobs broken; Qwen / GLM / local vLLM models available)
- CMMD (Cross-Model Memorization Disagreement) feasibility — treat v6.2 6-model fleet as strong reference, not default lock-in
- FinMem-NoOp probe design (analog of GSM-NoOp for CLS news)

**Out of scope**:
- Adding or removing factors from the shortlist (R4 locked them; v6.2 resolved the candidate-new-factor queue — see "Final factor state post-sweep" below)
- Re-discussing methodology principles P1-P5 (locked)
- Relitigating Risk R4 bloc structure (v6.1 4-bloc refactor is final)
- Algorithmic specification of clustering, entity extraction, or event-type taxonomy (Thales-joint track)
- Point-in-time market mechanics field list (point-in-time track)
- LLM annotation protocol details (annotation track)
- Pre-registration wording (R6)
- Timeline commitment (user decision)

---

## Final factor state post-sweep (2026-04-15)

**Active shortlist**: 12 factors unchanged (4 spine + 4 secondary + 2 auxiliary + 1 control + 1 sampling-design). See v6.2 decision doc for full blocks.

**Reserve (5 items, grew from 3)**:
13. Exact-Span Rarity
14. Cluster Temporal Span / Repost Persistence
15. Pre-registered interaction menu (methodology, not factor)
16. **Influence / Relevance** (v6.2, from Sub-task E, user approved reserve status) — news-factor for audience impact breadth; LLM-agent semantic annotation is cheap
17. **Eliteness** (v6.2, from Sub-task E, user approved reserve status) — semantic/ontological institutional hierarchy (State Council > ministry > provincial regulator > listed firm > local enterprise); distinct from Entity Salience (frequency-based) and Target Scope (binary)

**Dropped in v6.2**:
- **Geographical Proximity** — LLM pretraining corpora are global and English-heavy, so geographic distance does not translate to training-data frequency differences

**Gated on feasibility pilot (parallel to R5)**:
- **Coverage Breadth / Media Coverage** — potential 2nd pure extra-corpus factor; feasibility verdict is FEASIBLE BUT EXPENSIVE (see `docs/MEDIA_COVERAGE_FEASIBILITY.md`). 100-cluster pilot runs in parallel with R5. R5 must assume Coverage Breadth is NOT available as a production factor but should design detectors that could incorporate it if the pilot succeeds.

**Routed to R5 as detector-level stratification field (not article-side factor)**:
- **Entity-Anonymization Sensitivity** — magnitude of detector-score change when entity names are replaced by anonymous placeholders; analogous to counterfactual detector's "反事实显著程度". Direct literature support: Glasserman & Lin 2024 arxiv 2309.17322, Nakagawa et al. 2024 arxiv 2411.00420, Wu et al. 2025 arxiv 2511.15364. **R5 Step 1 must evaluate**: whether to include it as a seeded detector-level field, and if yes, which detector families it applies to (Min-K%, MIA, CMMD, SR/FO, FinMem-NoOp).

---

## R4 → R5 frozen inputs (do NOT relitigate)

1. The 12-factor shortlist is locked. R5 chooses detectors that operate ON these factors, not new factors. Reserve additions Q3 and Q5 are NOT active for R5 detector design; they are only reactivated if R5 joint modeling surfaces independent signal.
2. Methodology principles P1-P5 are binding. P5 specifically says "detector-dependent factors are R5 territory" — this is your green light to design detector-specific stratification fields, and Sub-task E explicitly routed Entity-Anonymization Sensitivity here.
3. **Risks R1-R4 carry forward with v6.1 refinement**. The v6.1 Risk R4 refactor is binding:
   - **4-bloc structure** (not 3-bloc): Bloc 0 = temporal exposure (Cutoff Exposure); Bloc 1 = repetition/surface reuse (Propagation Intensity, Template Rigidity, surface_template_recurrence); Bloc 2 = prominence/entity prior knowledge (Entity Salience target, Target Scope, Tradability Tier); Bloc 3 = institutional stage/source (Structured Event Type, Disclosure Regime, Event Phase, Session Timing)
   - **Bloc status**: **descriptive working hypothesis, NOT literature-validated latent structure** per Cronbach & Meehl 1955, Xiao et al. 2023, Freiesleben 2026, Kearns 2026
   - R5 detector choices should NOT amplify the bloc structure by being purely within-bloc. If a detector is most sensitive to surface reuse (Min-K%, char-ngram methods), recognize it will correlate with Bloc 1 regardless of memorization, and pair it with detectors sensitive to Bloc 0, 2, or 3.
4. Target N = 3,200 gross clusters (initial reference) with stopping-rule adaptive sampling.
5. Case text for memorization measurement = CLS text. Always.
6. Pre-commit granularity = 档位 2 偏 1.
7. Editor's narrative hierarchy (spine / secondary / auxiliary / control / reserve) — affects how R5 presents detector choices in the paper structure.
8. **Per-factor construct caveats + v6 literature provenance additions**: every factor has a "what is actually measured vs what the name suggests" annotation plus a v6 literature provenance paragraph. R5 should respect these caveats when designing detector-factor matchings. In particular:
   - Cutoff Exposure ±K gray-band has **no published precedent** — treat as benchmark-specific design choice, not literature-standard
   - Disclosure Regime is **NOVEL** — no memorization-factor precedent found; if R5 pairs a detector specifically with Disclosure Regime, that pairing needs mechanism-level justification (not literature citation)
   - Session Timing is **NOVEL** — same caveat; treat as low-confidence auxiliary

---

## R4-derived seed inputs to R5

### Seed 1 — Detector candidate pool (updated post-sweep)

R5 Step 1 starts from this candidate pool, NOT a final shortlist:

**Already in library (before sweep):**
- **Min-K%** (Shi et al. 2024) — white-box logprob-based
- **Min-K%++** (Zhang et al. 2024, arxiv 2404.02936) — direct follow-up, added by Sub-task D
- **MIA family** — multiple variants: Do MIAs Work on LLMs (already in library), MIA Against ML Models (Shokri 2017, added by D), MIA From First Principles (Carlini 2022, added by D)
- **Inherent Challenges / SoK paper** (Meeus et al. 2024, added by D) — **critical skepticism reading** before committing to any MIA-family detector
- **PatentMIA** — mentioned in `notes/contamination_detection.md`
- **Extraction attacks** — Carlini Secret Sharer, Extracting Training Data, Scalable Extraction (all in library)
- **RAVEN** (McCoy et al. 2021, added by D) — bridges memorization ↔ output novelty; useful for FinMem-NoOp framing
- **Memorization Without Overfitting** (Tirumala et al. 2022, added by D) — training dynamics theory, useful for anchor interpretation
- **Counterfactual probes — Semantic Reversal (SR)** — project's own prior work
- **Counterfactual probes — False Outcome (FO)** — project's own prior work
- **FinMem-NoOp** — NEW design from GSM-Symbolic; insert irrelevant-but-plausible clause and observe prediction change
- **CMMD (Cross-Model Memorization Disagreement)** — from MemGuard-Alpha; needs Chinese model fleet survey (see Seed 2)
- **PaCoST**, **CLEAN-EVAL**, **VarBench**, **LastingBench**, **Time Travel (Golchin & Surdeanu)**, **AntiLeakBench** — contamination-detection family, all in library
- **Perplexity-based**: zlib-ratio, reference-ratio

**Finance-specific mitigation / benchmark precedents (added by Sessions 1 + 2):**
- **Fast and Effective Solution to Look-ahead Bias** (Merchant & Levy 2025, arxiv 2512.06607) — inference-time logit-adjustment; alternative to retraining PiT models; worth evaluating as a baseline method
- **Do LLMs Understand Chronology?** (Wongchamcharoen & Glasserman 2025, arxiv 2511.14214) — prerequisite for prompt-based anti-leakage; directly tests whether the Cutoff Exposure story can rely on prompt-only time instructions
- **Anonymization and Information Loss** (Wu et al. 2025, arxiv 2511.15364) — finance follow-up that argues anonymization info loss can exceed look-ahead bias; directly relevant to Entity-Anonymization Sensitivity detector-level field
- **LiveTradeBench** (Yu et al. 2025, arxiv 2511.03628) — live-streaming alternative to offline backtesting; adjacent benchmark, not a detector
- **Evaluating LLMs in Finance Requires Explicit Bias Consideration** (Kong et al. 2026, arxiv 2602.14233) — 5-bias structural validity framework; directly useful for R5 paper-facing methods language
- **A Comparative Analysis of LLM Memorization at Statistical and Internal Levels** (Chen et al. 2026, arxiv 2603.21658) — cross-model memorization follow-up to CMMD territory
- **Benchmarking LLMs Under Data Contamination Survey** (Chen et al. 2025, EMNLP) — methodological synthesis

**Construct-validity methodology (added by Sub-task E):**
- **Kearns 2026 Quantifying Construct Validity** (arxiv 2602.15532), **Freiesleben 2026 Nomological Networks** (arxiv 2603.15121), **Xiao et al. 2023 Measurement Theory** (EMNLP), **Burnell et al. 2023 Factor Analysis** (arxiv 2306.10062), **Perlitz et al. 2024 BenchBench** (arxiv 2407.13696) — these do NOT seed new detectors but they seed the R5 paper's methods-section framing of how factor × detector results should be interpreted (explicitly NOT as latent-construct validation)

### Seed 2 — Open questions R5 must explicitly answer

1. **Ensemble vs single-detector strategy** — MemGuard-Alpha uses 5 MIA methods + logistic regression. Should FinMem-Bench detector layer also be an ensemble, or a set of independent detectors reported side-by-side? Trade-off: ensemble has stronger signal but harder to interpret per-factor; independent detectors are weaker but more interpretable. The **SoK / Inherent Challenges** paper (Meeus 2024) argues MIA family post-hoc detectors have fundamental identification problems — read before committing to an MIA-heavy ensemble.

2. **White-box vs black-box split** — DeepSeek-chat has broken logprobs in the existing infrastructure (see project memory `infra_capabilities.md`). White-box detectors (Min-K%, MIA, perplexity) can ONLY run on Qwen / GLM / local vLLM models. The v6.2 CMMD fleet provides 3 local white-box members (Qwen 2.5-7B, GLM-4-9B-0414, Qwen3-14B) and 3 black-box hosted members. **Open question**: does R5 commit to white-box primary / black-box secondary, or both as parallel tracks reported side-by-side? This affects the detector × model matrix shape.

3. **CMMD feasibility** — **v6.2 verdict: 6-model fleet stands unchanged.** See `docs/CMMD_MODEL_FLEET_SURVEY.md` + v6 CMMD block in decision doc for the full verdict table. The sweep confirmed NO chronologically-controlled family clears the fleet-add gates (downloadable + non-redundant cutoff in 2023-10 to 2025-07 + usable Chinese capability + compute-fit). DatedGPT, ChronoBERT/ChronoGPT, Time Machine GPT, StoriesLM, NoLBERT, and FINSABER are METHOD_ONLY citations, not fleet members. PiT-Inference was rejected. "Bendemra 2024 Frontier Models" was a citation error. **Fleet (v6.2)**:
   1. Qwen 2.5-7B-Instruct (local, cutoff 2023-10, white-box)
   2. DeepSeek-V2.5 (OpenRouter, cutoff ~2024-03, black-box)
   3. GLM-4-9B-0414 (local, cutoff 2024-06-30, white-box)
   4. DeepSeek-V3 `deepseek-chat-v3-0324` (OpenRouter, cutoff 2024-07, black-box)
   5. Qwen3-14B (local, cutoff 2025-01, white-box)
   6. Claude Sonnet 4.5 `claude-sonnet-4-5-20250929` (OpenRouter, cutoff 2025-01 reliable / 2025-07 extended, black-box)

   Per v5.3 / v6.2, R5 still has freedom to amend the fleet with justification, but the sweep produced no new candidates that clear the gates. **Critical reproducibility requirement**: pre-commit MUST pin to dated checkpoints (`-0324`, `-20250929`, `-0414`, HF commit SHAs) and lock OpenRouter provider routing.

4. **FinMem-NoOp design** — what counts as "irrelevant but plausible" in CLS? How is it generated? Is it LLM-generated (introducing a new annotation dependency) or rule-based (e.g., insert a sentence about an unrelated ticker drawn from the same time window)? The **RAVEN** paper (McCoy 2021, newly added) gives framing for how to decide whether inserted material is "novel" or "copied."

5. **Detector-dependent factors (Principle P5)** — each detector may contribute 1-2 stratification fields. R5 must list them per detector. Examples that came up:
   - `text_reversibility_score` for SR/FO
   - `extractable_span_density` for extraction attacks
   - `logprob_tail_length` for Min-K%
   - `token_perplexity_variance` for MIA
   - `cross_model_agreement_score` for CMMD
   - **`entity_anonymization_sensitivity`** — NEW from Sub-task E; routed to R5 as a detector-level field (see "Final factor state post-sweep" above). R5 Step 1 must evaluate this explicitly.

6. **Integration with factor shortlist** — for each (detector, factor) pair, write a one-sentence prediction of how informative the detector is on that factor. The detector × factor matrix is the core R5 deliverable. Now that the factor shortlist has v6 literature provenance annotations, R5 can ground each prediction in the literature tier (STRONG / PARTIAL / NOVEL) of the target factor.

### Seed 3 — Construct-collapse mitigation guidance for R5 (v6.1 refinement)

Risk R4 is now a **4-bloc descriptive working hypothesis** (NOT a validated latent structure) per v6.1. R5 should deliberately diversify detector mechanism families so that the eventual analysis produces evidence from independent sources, not from 5 detectors that all measure the same surface-form sensitivity.

**Recommended detector family diversification (updated for 4-bloc)**:

- At least 1 from **surface-form sensitivity** family (Min-K%, char-ngram, perplexity) — likely strongest on Bloc 1 (repetition)
- At least 1 from **counterfactual perturbation** family (SR, FO, FinMem-NoOp) — less bloc-specific
- At least 1 from **cross-model disagreement** family (CMMD) — likely strongest on Bloc 0 (temporal)
- At least 1 from **extraction / verbatim recall** family (Carlini-style) — likely strongest on Bloc 1 + Bloc 2
- At least 1 from **temporal-cutoff-conditional** family (any detector that uses cutoff metadata) — Bloc 0-focused by construction

If 4 of 5 detectors are surface-form sensitive, Bloc 1 will dominate every result and the 4-bloc story collapses into "FinMem-Bench detects Propagation Intensity."

**Additional v6.1 guidance for R5 paper framing**: report factor × detector matrix results at the per-factor level primarily. **Bloc-level summaries are DESCRIPTIVE ROBUSTNESS, not construct-validation evidence** — cite Cronbach & Meehl 1955, Xiao et al. 2023, Freiesleben 2026, Perlitz et al. 2024 in the methods section when framing the analysis. The paper must avoid claiming that correlation structure validates a latent decomposition.

### Seed 4 — R5 reading queue (from R4 literature sweep)

Beyond the candidate detector pool in Seed 1, the following papers are **R5 reading queue** that support specific detector-design decisions. Some overlap with Seed 1 (where the paper is both a detector and a methodology input):

**Mandatory (cited in v6.x edits and referenced in detector-choice rationale)**:
- Merchant & Levy 2025 `Fast Effective Solution Look-ahead Bias LLMs` (arxiv 2512.06607)
- Kong et al. 2026 `Evaluating LLMs in Finance Requires Explicit Bias Consideration` (arxiv 2602.14233)
- Wongchamcharoen & Glasserman 2025 `Do LLMs Understand Chronology?` (arxiv 2511.14214)
- Wu et al. 2025 `Anonymization and Information Loss` (arxiv 2511.15364)
- Yu et al. 2025 `LiveTradeBench` (arxiv 2511.03628)
- Chen et al. 2026 `Cross-Model Memorization Statistical Internal` (arxiv 2603.21658)
- Chen et al. 2025 EMNLP `Benchmarking LLMs Under Data Contamination Survey`

**Strongly recommended (MIA family skepticism + construct validity)**:
- Meeus et al. 2024 `Inherent Challenges Post-Hoc MIA LLMs` (arxiv 2406.17975, aka SoK: Rushing Nowhere) — read before committing to MIA-heavy ensemble
- Carlini et al. 2022 `MIA From First Principles` (arxiv 2112.03570)
- Shokri et al. 2017 `MIA Against ML Models` (arxiv 1610.05820)
- Tirumala et al. 2022 `Memorization Without Overfitting` (arxiv 2205.10770)
- Zhang et al. 2024 `Min-K%++` (arxiv 2404.02936)
- Kearns 2026, Freiesleben 2026, Xiao 2023 EMNLP, Burnell 2023, Perlitz 2024 — all for methods-section framing

**Chrono-control precedents (METHOD_ONLY cites, read for paper related-work)**:
- Drinkall 2024 `Time Machine GPT` (arxiv 2404.18543)
- Sarkar & Vafa 2024 `Lookahead Bias in Pretrained LMs` (SSRN)
- Levy 2024 `Caution Ahead` (SSRN) — numerical-reasoning caveat important for detector interpretation

---

## R5 process recommendation

The cold reader recommended **splitting R5 into R5A and R5B**:

- **R5A — Conceptual shortlist**: detector landscape survey, family identification, conceptual matching to factors. Independent of execution gates. **Can start immediately.**
- **R5B — Executable shortlist**: pruning R5A's conceptual shortlist by feasibility — depends on Thales pipeline outputs being defined, model cutoff metadata being available, and CMMD model fleet being verified.

R5A would use the 4-Codex-agent + Challenger structure, with these role adaptations:

- **Quant** — alpha-bridge angle: which detectors give signals that survive translation to alpha contamination claims; CMMD's relevance to Thales downstream
- **NLP** — methodology angle: which detector families have the strongest construct validity arguments; FinMem-NoOp design; digest of Meeus 2024 MIA skepticism
- **Stats** — power and identification: detector-factor matrix power calc; multiple-comparison family across detectors; joint modeling structure for the 4-bloc framing
- **Editor** — narrative angle: how many detectors fit the paper's central claim without scope creep; venue fit (does the detector list pull toward EMNLP or finance venue); framing of the "correlation ≠ construct validation" paper-facing language
- **Challenger** — same role, look for detector-family blind spots from a non-Codex perspective

**Parallel track — Coverage Breadth 100-cluster pilot** (per user instruction 2026-04-15): runs in parallel with R5A, not as a blocker. If the pilot succeeds mid-R5, R5B can absorb Coverage Breadth as an extra factor to target with detector design; if the pilot fails, R5 proceeds without it.

---

## What to NOT spend R5 time on

Per the cold reader's recommendation + v6.2 state:
- Don't try to lock R5B before Thales / point-in-time / annotation tracks make progress
- Don't propose new factors. The candidate queue is fully resolved in v6.2 (Q1 gated, Q2 routed here as detector field, Q3/Q5 reserve, Q4 dropped).
- Don't redesign methodology principles
- Don't relitigate Risk R4 bloc structure — v6.1 4-bloc refactor is binding
- Don't relitigate venue-drift or alpha-bridge — those are settled at narrative level
- Don't try to commit to a timeline — that's a user decision
- **Don't run another broad literature sweep** — Sessions 1 + 2 covered factor provenance, chronological baselines, broad 2024-2026 discovery, cited-but-unread, and construct validity. R5 only runs **targeted detector-specific spot checks** if a specific detector family is unclear about its state of the art. Bounded spot-checking, NOT a broad sweep.

---

## Items to bring forward from R4 that should influence R5

1. The **Anchor Strength 150-case experiment** must run BEFORE any memorization detector is run on the main corpus. R5 should explicitly schedule this as an R5 prerequisite, not assume it happens out-of-band.
2. The **cluster-free robustness companion** to Propagation Intensity uses char-5gram TF-IDF — this is a detector-adjacent technique. R5 should be aware that this companion is a "detector lite" already in the factor schema.
3. **Construct caveats per factor** (v5) + **v6 literature provenance additions** directly affect R5. For example:
   - Cutoff Exposure is timing not exposure → R5 detectors should compute factors that are time-aware AND robust to cutoff misclassification
   - Cutoff Exposure ±K gray-band is a benchmark-specific design choice (no published precedent) → R5 should document its gray-band choice as a reproducibility parameter
   - Disclosure Regime and Session Timing are NOVEL → R5 should NOT pair them with detectors whose mechanism depends on established literature for those factors; if a detector is paired with them, the pairing needs mechanism-level justification
4. **4-bloc framing** for construct-collapse mitigation → R5 detector diversification should cover all 4 blocs, not just the original 3
5. **Entity-Anonymization Sensitivity** — pre-seeded as a detector-level field that R5 Step 1 must evaluate
6. **Media Coverage parallel pilot** — R5 cannot depend on Coverage Breadth being available, but should not preclude it either

---

## Suggested R5 first-session agenda

1. Read this kickoff + required reading list (especially v6.2 decision doc + Sub-task E output + FACTOR_LITERATURE_PROVENANCE.md + Risk R4 v6.1 section)
2. Confirm the v6.2 factor state: 12 active + 5 reserve + 1 dropped + 1 gated + 1 detector-level routed
3. Run R5A Step 1 — 4 Codex agents in parallel propose detector candidates from each lens. Each agent should produce 5-8 candidates with concept, mechanism, access requirement, factor relevance, bloc diversification, ensemble compatibility
4. Orchestrator synthesis of R5A Step 1 (expect 15-20 detector candidate pool)
5. R5A Step 2 — 4 Codex agents review the integrated detector shortlist; converge on 5-8 final detectors
6. Challenger pass for cross-model blind spots
7. Cold-reader pass (analogous to R4)
8. R5A closes with a frozen detector shortlist that R5B can pick up when its dependencies resolve

**Note on Codex MCP parallelism**: per user feedback 2026-04-15, multiple Codex MCP calls from a single main-thread message are serialized per-server. For true wall-clock parallelism, wrap each Codex call in its own `Agent` sub-agent (general-purpose). See user memory `feedback_codex_parallelism.md`.

---

## Literature sweep sequencing (resolved — historical note)

The earlier version of this kickoff proposed "R4 literature sweep runs before R5." That has happened. **R4 literature sweep Sessions 1 and 2 are complete**. R5 now inherits the sweep's outputs:

- `docs/FACTOR_LITERATURE_PROVENANCE.md` (Sub-task A)
- `docs/LITERATURE_SWEEP_2026_04.md` (A + B + C + D + E consolidated)
- `docs/MEDIA_COVERAGE_FEASIBILITY.md` (Q1 feasibility)
- `docs/CMMD_MODEL_FLEET_SURVEY.md` (unchanged but with v6 CMMD verdict block in decision doc)
- `docs/DECISION_20260413_mvp_direction.md` v6.2 (all edits applied)
- 27 new library papers (11 Session 1 + 14 Session 2 + 1 Didisheim markdown + 1 user-supplied Caution Ahead)

R5 does NOT run its own broad literature sweep. Targeted detector-specific spot checks during R5 Step 1 brainstorm are allowed and bounded.

**Known blind spots not covered by the sweep** (acknowledged limitations, R5 should flag if relevant):
1. CNKI Chinese-academic-index not searched — user declined the optional dedicated session
2. Fama-French-for-LLM-evaluation analog does not appear to exist in published literature (Sub-task E finding)
3. No finance/NLP paper runs SEM/EFA/CFA directly on article-side memorization factors (Sub-task E finding — FinMem-Bench enters under-theorized territory for factor-independence validation)

---

## Ready for next session

When the user opens R5 in a new conversation, the new session should:

1. Read this kickoff document first
2. Read the required reading list (especially the v6.2 decision doc + FACTOR_LITERATURE_PROVENANCE.md + LITERATURE_SWEEP_2026_04.md + MEDIA_COVERAGE_FEASIBILITY.md)
3. Skim the v6 / v6.1 / v6.2 version history entries to understand the sweep outcomes
4. Begin R5A Step 1 — 4-agent Codex brainstorm

The new session does NOT need to re-read R1-R4 reviews in full unless a specific question requires it. **v6.2 of the decision document is the authoritative state.**
