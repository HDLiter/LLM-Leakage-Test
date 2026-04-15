# BENCHMARK R4 — Literature Sweep Kickoff

**Date created:** 2026-04-13 (end of R4, before R5)
**Status:** PENDING — to be executed in a FRESH session
**Purpose:** Retrospective literature validation of the 12-factor shortlist + broad prior-art sweep to prevent further MemGuard-Alpha-style surprise discoveries
**Predecessor:** R4 conceptually closed. See `docs/DECISION_20260413_mvp_direction.md` v5.2.
**Successor:** R5 detector investigation (after this sweep completes)

This document is a self-contained context packet for a fresh session whose sole job is to do a bounded, thorough literature sweep on R4's outputs. The output is an appendix to the decision document (bumping it to v6) + a list of candidate additional factors, reframings, and references.

---

## Why this sweep is needed

**The MemGuard-Alpha incident**: we only discovered MemGuard-Alpha (Roy & Roy 2026) AFTER R4 closed, because the user happened to mention they saw it. It turned out to be directly-adjacent prior art, and its absence from R1-R4 would have been a reviewer-fatal omission in the paper. This incident proves the existing review process (4 Codex domain agents + Challenger + cold reader) is **not a substitute for systematic literature search**. Each agent has a memorized distribution of the literature they read during training and their web search is ad-hoc; none of them systematically enumerated what exists.

**The 12 factors are under-backed**: some factors have strong literature backing (Cutoff Exposure → Dated Data, Set the Clock, Chronologically Consistent LLMs; Propagation Intensity → Kandpal, Carlini, Lee frequency-recall family). Others are under-backed or explicitly novel (Event Phase is user-proposed; Disclosure Regime has no cited precedent; Session Timing is motivated by DellaVigna & Pollet but not yet tied to memorization literature). R5 detector choices depend on how well-grounded the factors are.

**The chronologically-controlled baselines**: R4 has `DatedGPT` (Yan et al. 2026) and `ChronoBERT/ChronoGPT` (He et al. 2025) in the library but neither has been systematically evaluated for CMMD integration. The sweep should decide whether either enters the model fleet.

---

## Required reading before starting the sweep

1. **`docs/DECISION_20260413_mvp_direction.md` v5.2** — the authoritative decision document, especially:
   - "R4 Step 1 + Step 2 outcome: 12-factor shortlist" — the locked factor list
   - "Methodology principles (P1-P5)"
   - "R4 Step 2 convergent risks (R1-R4)"
   - "Open considerations for downstream tracks" — especially the Thales dedicated session section and CMMD fleet section
2. **`refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md`** — R4 closure
3. **`refine-logs/reviews/BENCHMARK_R4_FINAL_REVIEW.md`** — cold reader's critique; the biggest single risk is construct collapse
4. **`refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md`** — integration review that triggered the v5.2 cleanup; useful for knowing what was in tension
5. **`docs/CMMD_MODEL_FLEET_SURVEY.md`** — current fleet recommendation; Sub-task C references it directly
6. **`docs/THALES_SIGNAL_PROFILE_REVIEW.md`** — Thales topic/modality/authority review; Sub-task A's Modality and Authority literature checks depend on this
7. **`related papers/INDEX.md`** — what papers are already in the library
8. **`related papers/notes/*.md`** — topic-level summaries of library papers

**Scope boundary note**: this kickoff owns the **broad factor/provenance literature sweep**. R5 (`BENCHMARK_R5_KICKOFF.md`) owns a narrower **detector-specific targeted sweep** within R5 Step 1 only. The two do not overlap: this sweep focuses on factor-level prior art, chronologically-controlled baseline evaluation, broad 2024-2026 landscape, and construct validity; R5's sweep focuses on detector family state of the art. If a paper is relevant to both (e.g., MemGuard-Alpha), this sweep owns the factor-level interpretation and R5's sweep owns the detector-level interpretation.

---

## Scope

**In scope**:
- Per-factor literature provenance check for all 12 active factors + 3 reserve factors + 2 possible additions (Modality, Authority)
- Broad 2024-2026 sweep for memorization / contamination / financial NLP / factor-controlled benchmark papers we may have missed
- Chronologically-controlled baseline investigation (DatedGPT, ChronoBERT/ChronoGPT, Time Machine GPT, PiT-Inference models, FINSABER)
- Cited-but-unread papers from the existing library (papers that are referenced in our library notes but we haven't read)
- Targeted search for papers that would either validate or challenge the 3 latent blocs identified in Risk R4 (construct collapse)

**Out of scope**:
- Detector-specific literature (that's R5's targeted sweep, NOT this sweep)
- Writing prose for related work section (that's paper-writing time)
- Adding or removing factors (R4 locked the list; this sweep ONLY informs factor justification and Construct caveats)
- Non-memorization ML literature unless directly relevant
- Anything that requires modifying Thales source (explicitly forbidden per user instruction)

---

## Process

This sweep should use **fresh Codex calls** — NOT the R1-R4 Codex personas (Quant/NLP/Stats/Editor) because those agents already made choices under the 12-factor shortlist; they are biased to defend their own prior recommendations. The fresh session should use:

- **1 or 2 Codex calls** with the generic persona "senior NLP / memorization researcher, approaching this project fresh, systematic bibliographic researcher, uses web search aggressively"
- OR a **hybrid of Codex + targeted web search + arxiv crawling**

### Sub-task A — Per-factor literature provenance check

For each factor in the shortlist below, the sweep must answer:
1. **Prior art**: has this specific construct been used as a memorization / contamination / benchmark factor in published work? Cite ≥1 paper if yes; explicitly mark "novel, no prior art found" if no.
2. **Operationalization precedent**: has anyone published a specific operationalization for this construct? Does our proposed operationalization match or differ?
3. **Known failure modes**: what has been reported about this factor's failure modes or caveats in published work?
4. **Effect direction precedent**: has the predicted effect direction been validated or contradicted by prior work?
5. **Alternative names**: is this factor known by a different name in a different field that we may have missed?

Factors to check:

**Spine (4)**:
1. Propagation Intensity (composite of cluster_size + prior_family_count) — check Kandpal, Carlini, Lee family but also look for: Zhang et al. Counterfactual Memorization, Tirumala Memorization Without Overfitting (already in library), any 2024-2026 follow-ups
2. Cutoff Exposure (case×model cutoff timing) — check Dated Data (Cheng et al.), Set the Clock (Zhao et al.), Chronologically Consistent LLMs (He et al.), DatedGPT (Yan et al.), Fake Date Tests, A Test of Lookahead Bias. **Specifically look for published papers using pre/post cutoff as a factor with a gray-band exclusion zone.**
3. Anchor Strength (TBD rubric) — check Huet et al. 2025 (episodic event representation), Gurnee & Tegmark 2024 (space and time representations), Zhou et al. 2023 (entity-linked memorization). **Specifically look for rubrics for "event anchorability" in news text.**
4. Entity Salience (dual: target_salience + max_non_target_entity_salience) — check Zhou et al. 2023, Glasserman & Lin 2024 (distraction effect), any 2024-2026 follow-ups on entity-level memorization

**Secondary (4)**:
5. Target Scope (company vs non-company) — check finance benchmark papers (CFinBench, InvestorBench, FinBen) for precedent
6. Structured Event Type (Thales 13-type → refined) — check Zhou Trade the Event, finance news classification literature, any 2024-2026 memorization work using event type as a stratum
7. Disclosure Regime (formal vs commentary) — **unknown precedent**. Search specifically for "disclosure type" or "source provenance" as a memorization factor. If nothing found, this is a novel factor and the paper must justify it carefully.
8. Template Rigidity (char-5gram TF-IDF surface similarity) — check Zhang et al. 2021 templated texts, Lee et al. 2021 repetitive substrings, and any more recent surface-form memorization work

**Auxiliary (2)**:
9. Tradability Tier (ADV20 percentile) — check Fang & Peress 2009, Hirshleifer et al. 2023, and the MemGuard-Alpha 5-MIA features. Does anyone use market-cap or liquidity tiers as a memorization factor?
10. Session Timing (pre-open/intraday/post-close/non-trading) — check DellaVigna & Pollet 2009 (already cited for motivation), but this is about investor inattention not memorization. **Unknown memorization precedent.** Search specifically for "announcement timing" as a memorization or contamination factor.

**Sampling-design (1)**:
11. Event Phase (rumor/official/clarification/recap with two-stage sampling) — the phase classification rules came from Quant R1 brainstorm citing no prior art. Search specifically for "rumor vs confirmed news" as a memorization factor. Check: finance news lifecycle papers, signal decay literature.

**Control (1)**:
12. Text Length — standard nuisance control; minimal sweep required.

**Reserve (3)**:
13. Exact-Span Rarity — check Carlini 2019, Carlini 2021, Zhou 2023 for entity-level + rare-span memorization
14. Cluster Temporal Span / Repost Persistence — novel; Cheng et al. 2024 (Dated Data) is the closest precedent
15. Pre-registered interaction menu — methodological precedent in empirical methodology literature, not factor literature

**Possible additions under investigation**:
- Modality (Thales 7-enum) — search for "news type" or "modality" as a memorization / contamination factor
- Authority (Thales 8-enum, potentially extra-corpus via publisher metadata) — search for "source authority" or "publisher credibility" as a memorization factor

### Sub-task B — Broad 2024-2026 sweep for missed prior art

Open-ended web search + arxiv search for papers matching these queries:
- "LLM memorization" + "financial" + "benchmark" (2024-2026)
- "LLM contamination detection" + "financial forecasting"
- "factor-controlled benchmark" + "memorization"
- "Chinese financial NLP" + "memorization" (specifically Chinese)
- "cross-model memorization" (follow-ups to MemGuard-Alpha's CMMD)
- "look-ahead bias" + "LLM" (2024-2026)
- "temporal contamination" + "LLM" + "benchmark"
- "pretraining data detection" + "finance"

Explicitly look for:
- Direct competitors (papers proposing similar benchmarks)
- Direct methodological precedents (papers using the same factor design approach)
- Reviewer-killer prior art (papers whose existence would make reviewers say "this is derivative of X")

### Sub-task C — Chronologically-controlled baseline investigation

For the two chronologically-controlled LLM families already in the library, determine:
- **DatedGPT** (Yan et al. 2026, 12×1.3B models annual cutoffs 2013-2024):
  1. Are the models publicly downloadable? HuggingFace? author github?
  2. Model family name / checkpoint names
  3. Tokenizer and context length
  4. Chinese capability (was it trained on Chinese data? how much?)
  5. Benchmark performance on Chinese tasks if reported
  6. Memory / compute requirements to run locally
  7. Whether the temporal grid (2013 → 2014 → ... → 2024) maps cleanly to CLS data timeline
  8. **Verdict**: should DatedGPT enter the CMMD fleet as a controlled baseline (even if Chinese quality is modest)?
- **ChronoBERT / ChronoGPT** (He et al. 2025):
  1. Same 8 questions
  2. **Verdict**: should ChronoBERT/ChronoGPT enter the CMMD fleet?

Additional chronologically-controlled models to look up (mentioned in MemGuard-Alpha references but not verified):
- **Time Machine GPT** (Bendemra et al.)
- **PiT-Inference models**
- **Bendemra 2024 Frontier Models**
- **FINSABER framework at KDD 2026**
- Any other "LLM trained with strict temporal cutoffs" paper from 2024-2026

### Sub-task D — Cited-but-unread sweep

For each paper in `related papers/notes/*.md`, identify the top 3 most-cited papers in its bibliography that are NOT already in our library. Build a candidate list. For each, decide whether to download (high relevance) or skip (marginal relevance). Report the download list to the user before actually downloading; do not download more than ~10 papers without user approval.

### Sub-task E — Construct-collapse risk validation

Risk R4 (construct collapse) identifies 3 latent blocs:
1. Repetition / surface reuse
2. Prominence / attention
3. Institutional stage / source

**Search for published work that has measured correlations between similar factor blocs in financial NLP or benchmark design**. The question: is our 3-bloc structure supported by others' empirical analysis? If yes, cite. If the literature has a different (more granular or less granular) decomposition, report it. This strengthens the mitigation strategy in Risk R4.

---

## Output format

The sweep should produce:

1. **`docs/FACTOR_LITERATURE_PROVENANCE.md`** — per-factor literature audit, structured by factor, with:
   - Factor name + current construct caveat
   - Published precedent (citations)
   - Operationalization precedent
   - Effect direction precedent or contradiction
   - Alternative names
   - Novel vs prior-art assessment
   - Recommended update to the factor's construct caveat in decision doc v6
2. **`docs/LITERATURE_SWEEP_2026_04.md`** — broad sweep report, structured by sub-task:
   - Sub-task A findings summary
   - Sub-task B: new papers discovered, with priority ratings and inclusion recommendations
   - Sub-task C: DatedGPT and ChronoBERT/ChronoGPT evaluation + verdict on CMMD fleet inclusion
   - Sub-task D: cited-but-unread candidate list with priority
   - Sub-task E: 3-bloc structure validation
3. **Downloaded PDFs** for any new papers with high priority (if ≤10, auto-download; if >10, propose list to user first)
4. **`related papers/INDEX.md`** updated with new papers
5. **`related papers/notes/*.md`** updated with notes for new papers
6. **Recommendations for decision doc v6** — a concrete list of edits to `docs/DECISION_20260413_mvp_direction.md` based on sweep findings. NOT applied automatically; reviewed by user before v6 is cut.
7. **Summary memo** — a concise summary (under 500 words) of the sweep's biggest findings, biggest blind spots still open, and most important recommendations.

---

## What the sweep must NOT do

- Do NOT modify `docs/DECISION_20260413_mvp_direction.md` directly. Output recommendations, leave application to the user.
- Do NOT add new factors. The 12-factor shortlist is locked.
- Do NOT remove factors. Only inform construct caveats.
- Do NOT launch R5 or make R5 decisions.
- Do NOT touch `D:\GitRepos\Thales` — the Thales dedicated session is separate and the user will signal when it opens.
- Do NOT download more than 10 PDFs without user approval.
- Do NOT use the R1-R4 Codex agent personas (Quant/NLP/Stats/Editor); they are biased.

---

## Recommended session flow

1. **Session 1 (this one, if the fresh session is opened now)**: run Sub-tasks A-C in parallel using 2-3 Codex calls + heavy WebSearch. Target duration: 2-4 hours of work. Output: per-factor provenance + broad sweep + chronological baseline evaluation.
2. **Session 2 (optional follow-up)**: run Sub-task D (cited-but-unread) and Sub-task E (bloc validation). These are less time-critical.
3. **Session 3 (user review)**: user reviews all outputs, approves downloads, signs off on v6 edit list.
4. **v6 cut**: whoever owns v6 (Claude Code in a fresh session) applies the approved edits and bumps the decision document.
5. **Open R5** (separate session) — now with stronger factor grounding.

---

## Estimated effort

- Sub-task A: 45-90 minutes of Codex+WebSearch per factor group, total ~3-5 hours of agent runtime
- Sub-task B: 1-2 hours broad sweep
- Sub-task C: 1-2 hours targeted investigation
- Sub-task D: 30-60 minutes
- Sub-task E: 30-60 minutes
- Writing outputs: 1-2 hours (bundled with agent work)

Total fresh-session runtime: ~6-10 hours of wall-clock if sequential; ~3-4 hours if parallel sub-tasks.

---

## Ready for fresh session

When the user opens a new conversation and loads this kickoff, the new session can start immediately. It does NOT need to re-read R1-R4 in full — v5.2 of the decision document + `BENCHMARK_R4_FINAL_SYNTHESIS.md` + this kickoff document are sufficient context.

The expected output of the sweep is an appendix to v5.2 that strengthens construct validity and fills blind spots, NOT a rewrite. If the sweep finds something fatal (e.g., a published benchmark that directly supersedes FinMem-Bench), the user must be alerted immediately; the sweep should not silently absorb such findings.
