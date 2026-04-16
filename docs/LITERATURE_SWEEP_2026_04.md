> **Status (2026-04-16, post-R5A-freeze)**: Historical R4 literature sweep feeding decision-doc v5.3→v6.2. Retained for citation provenance. Current scope conclusions (e.g., "keep 6-model fleet") have been **superseded** by `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` (9-model fleet) and `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` (four-layer measurement scope). Detector pool / D1-D12 terminology has been replaced by Factor / Perturbation / Operator / Estimand framework.

# FinMem-Bench — R4 Literature Sweep (2026-04-14)

**Status:** Session 1 of the sweep — Sub-tasks A, B, C completed. Sub-tasks D (cited-but-unread) and E (3-bloc construct-collapse validation) deferred to Session 2 by design (user mid-sweep checkpoint).
**Kickoff:** `refine-logs/reviews/BENCHMARK_R4_LIT_SWEEP_KICKOFF.md`
**Related outputs:** `docs/FACTOR_LITERATURE_PROVENANCE.md` (per-factor detail) + `refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md` / `LIT_SWEEP_B_BROAD_SWEEP.md` / `LIT_SWEEP_C_CHRONO_BASELINES.md` (raw Codex outputs)
**Version of decision doc this sweep feeds into:** v5.3 → proposed v6 (edit proposals in `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md`)
**Sweep persona for all 3 Codex calls:** senior NLP / memorization researcher, fresh session, no R1-R4 attachment, systematic bibliographer, aggressive arxiv+web_search user, no reliance on training-data memory for state of the art
**Total Codex xhigh calls used:** 3 (A, B, C), all successful, no rate-limit retries needed

---

## Executive summary (under 500 words)

The sweep did not surface any P0 direct competitor to FinMem-Bench. The novelty claim — a factor-controlled Chinese financial-news memorization benchmark — remains intact. No Chinese-financial, memorization-aware, factor-controlled benchmark exists in the 2024-2026 arxiv/web_search/Semantic-Scholar coverage. MemGuard-Alpha currently has zero Semantic Scholar citations as of 2026-04-14; Profit Mirage is cited by `All Leaks Count` and `LiveTradeBench`, both either in-library or discovered in this sweep.

**Factor provenance distribution** (15 factors audited): 5 STRONG_PRIOR_ART, 8 PARTIAL_PRIOR_ART, 2 NOVEL. The two novel factors are `Disclosure Regime` (already flagged as a placeholder in v5.3) and `Session Timing`. Both are the most exposed constructs in the paper and need mechanistic justification rather than literature-grounded justification. `Cutoff Exposure` has strong precedent but the `±K` gray-band exclusion is a benchmark-specific design choice with no verified published precedent — it should be labeled as such in the paper, not presented as a literature-standard convention.

**Chronologically-controlled baselines** (Sub-task C): the v5.2 6-model CMMD fleet should stand unchanged. DatedGPT (arxiv 2603.11838, 12 × 1.3B annual cutoffs 2013-2024) is the strongest methodological precedent but is NOT downloadable as of 2026-04-14 and is English-only. ChronoBERT / ChronoGPT / ChronoGPT-Instruct (He et al. 2025, arxiv 2502.21206) have public HF releases with verified commit SHAs (`manelalab/chrono-*-v1-20241231`) but are labeled English-only in every verified model card. Time Machine GPT (arxiv 2404.18543) is public (`Ti-Ma/TiMaGPT2-*`) but stops at 2022 and is English-only. Two new discoveries: `StoriesLM` (1900-1963, English BERT-style, public HF) and `NoLBERT` (arxiv 2509.01110, 1976-1995, introduces the "lookaback bias" concept). `PiT-Inference` is a vendor claim, REJECT. `Bendemra 2024` is a citation error — probably confused with Benhenda's Look-Ahead-Bench. `FINSABER` (arxiv 2505.07078, KDD 2026) is a benchmarking framework, not a model — cite as methodological precedent. Verdict: **keep fleet unchanged; cite chronological precedents in the paper's methods section**.

**Broad sweep (Sub-task B)** discovered 8 new P1 papers that should enter the R5 reading queue: `AI's predictable memory in financial analysis` (Didisheim 2025, Economics Letters), `A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs` (Merchant & Levy 2025, arxiv 2512.06607), `Evaluating LLMs in Finance Requires Explicit Bias Consideration` (Kong et al. 2026, arxiv 2602.14233), `Do Large Language Models Understand Chronology?` (Wongchamcharoen & Glasserman 2025, arxiv 2511.14214), `Anonymization and Information Loss` (Wu et al. 2025, arxiv 2511.15364), `LiveTradeBench` (Yu et al. 2025, arxiv 2511.03628), `A Comparative Analysis of LLM Memorization at Statistical and Internal Levels` (Chen et al. 2026, arxiv 2603.21658), and `Benchmarking LLMs Under Data Contamination Survey` (EMNLP 2025).

**Candidate new-factor queue:** 2 concepts surfaced during the sweep that are NOT in the current 15+2 shortlist but have adjacent evidence worth a user decision: `Coverage Breadth / Media Coverage` (indirect support from finance attention literature) and `Entity-Anonymization Sensitivity` (direct support from Glasserman & Lin 2024 and Wu et al. 2025). Per user v5.3 clarification, these are queued for user review, not silently absorbed.

**Blind spots still open:** (1) CNKI-first Chinese literature under-covered — dedicated Chinese academic index session recommended; (2) Venue-only paywalled finance papers partially visible; (3) Sub-task D (cited-but-unread) and Sub-task E (3-bloc construct-collapse validation) deferred to Session 2.

---

## Sub-task A — Per-factor literature provenance (summary)

See `docs/FACTOR_LITERATURE_PROVENANCE.md` for the full per-factor audit. Summary:

### Novelty distribution

| Factor | Hierarchy | Verdict |
|---|---|---|
| Propagation Intensity | Spine | STRONG_PRIOR_ART |
| Cutoff Exposure | Spine | STRONG_PRIOR_ART |
| Anchor Strength | Spine | PARTIAL_PRIOR_ART |
| Entity Salience | Spine | STRONG_PRIOR_ART |
| Target Scope | Secondary | PARTIAL_PRIOR_ART |
| Structured Event Type | Secondary | PARTIAL_PRIOR_ART |
| Disclosure Regime | Secondary (PLACEHOLDER) | **NOVEL** |
| Template Rigidity | Secondary | STRONG_PRIOR_ART |
| Tradability Tier | Auxiliary | PARTIAL_PRIOR_ART |
| Session Timing | Auxiliary | **NOVEL** |
| Text Length | Control | PARTIAL_PRIOR_ART |
| Event Phase | Sampling-design | PARTIAL_PRIOR_ART |
| Exact-Span Rarity | Reserve | STRONG_PRIOR_ART |
| Cluster Temporal Span | Reserve | PARTIAL_PRIOR_ART |
| Interaction menu | Reserve (methodology) | PARTIAL_PRIOR_ART |
| Modality (under investigation) | possible addition | PARTIAL_PRIOR_ART |
| Authority (under investigation) | possible addition | PARTIAL_PRIOR_ART |

### Cross-factor observations

- **Strongest shared-paper bloc**: `{Propagation Intensity, Template Rigidity, Exact-Span Rarity, Text Length}` all cite the Kandpal/Carlini/Zhang/Ishihara repetition-frequency family. This is exactly the Risk R4 construct-collapse axis (repetition/surface-reuse bloc).
- **Cutoff Exposure gray-band exclusion (±K days)**: no published precedent verified. Present as a benchmark-specific design choice in v6, not as a literature-standard convention.
- **The weakest bloc**: `{Disclosure Regime, Modality, Authority, Event Phase}` — published work supports source/lifecycle taxonomies in finance and misinformation, but not these as memorization factors. This aligns with v5.3's treatment of Disclosure Regime as a placeholder and the deferral of Modality/Authority to the Thales dedicated session.
- **The cleanest "no direct factor precedent" cases** are `Disclosure Regime` and `Session Timing`. Both need mechanistic (not literature-grounded) justification in v6.

---

## Sub-task B — Broad 2024-2026 sweep

See `refine-logs/reviews/LIT_SWEEP_B_BROAD_SWEEP.md` for raw query-by-query output. Summary:

### Direct competitors discovered

**None.** No new benchmark is simultaneously Chinese-financial, memorization-aware, and factor-controlled in the FinMem-Bench design space. The closest adjacent benchmarks (`LiveTradeBench`, `FinGAIA`, `FinMCP-Bench`, `XFinBench`) do not match the core problem formulation.

### New P1 papers for the R5 reading queue

| Paper | Authors | arxiv_id / URL | Why relevant |
|---|---|---|---|
| AI's predictable memory in financial analysis | Didisheim et al. 2025 (Economics Letters) | [RePEc](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392) | Finance-specific memorization proxy via recall of historical stock returns |
| A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs | Merchant & Levy 2025 | [2512.06607](https://arxiv.org/abs/2512.06607) | Inference-time mitigation for verbatim + semantic future knowledge; alternative to retraining PiT models |
| Evaluating LLMs in Finance Requires Explicit Bias Consideration | Kong et al. 2026 | [2602.14233](https://arxiv.org/abs/2602.14233) | Structural validity framework naming 5 recurring finance evaluation biases; directly useful for FinMem-Bench methods section |
| Do Large Language Models Understand Chronology? | Wongchamcharoen & Glasserman 2025 | [2511.14214](https://arxiv.org/abs/2511.14214) | Prerequisite paper for prompt-based anti-look-ahead — if models do not reliably understand chronology, prompt-only historical boundaries are weaker than they appear |
| Anonymization and Information Loss | Wu et al. 2025 | [2511.15364](https://arxiv.org/abs/2511.15364) | Direct finance follow-up to Glasserman-Lin; argues anonymization info loss may exceed look-ahead bias in earnings-call sentiment |
| LiveTradeBench | Yu et al. 2025 | [2511.03628](https://arxiv.org/abs/2511.03628) | Adjacent benchmark replacing offline backtesting with live streaming to prevent leakage; cites Profit Mirage |
| A Comparative Analysis of LLM Memorization at Statistical and Internal Levels | Chen et al. 2026 | [2603.21658](https://arxiv.org/abs/2603.21658) | Strongest non-finance follow-up to cross-model memorization logic; shared vs family-specific memorization across model series |
| Benchmarking LLMs Under Data Contamination (Survey) | Chen et al. 2025 | [EMNLP](https://aclanthology.org/2025.emnlp-main.511/) | Methodological synthesis on dynamic contamination-aware benchmark design principles |

### P2 background references

- `Total Recall? Evaluating the Macroeconomic Knowledge of LLMs` (Crane et al. 2025, Federal Reserve FEDS paper) — macro recall + release timing
- `FinGAIA` and `FinMCP-Bench` — Chinese finance benchmarks, but agent/tool focused not memorization
- `FinTruthQA` — Chinese disclosure-quality benchmark, not contamination
- `Uncovering Representation Bias for Investment Decisions in Open-Source LLMs` — indirect support for Coverage Breadth concept
- `Toward Reliable Evaluation of LLM-Based Financial Multi-Agent Systems` — adjacent survey on finance evaluation failures

### Semantic Scholar citing-paper sweep

- **Citing MemGuard-Alpha** (arxiv 2603.26797): **zero citations** as of 2026-04-14.
- **Citing Profit Mirage** (arxiv 2510.07920): `All Leaks Count, Some Count More` (already in library) and `LiveTradeBench` (newly discovered).

---

## Sub-task C — Chronologically-controlled baseline investigation

See `refine-logs/reviews/LIT_SWEEP_C_CHRONO_BASELINES.md` for the full 8-point table per model. Summary verdict table:

| Model | Public? | Chinese? | Cutoff grid | Verdict |
|---|---|---|---|---|
| **DatedGPT** (Yan et al. 2026, arxiv 2603.11838) | No (demo only; weights pending acceptance) | English-only | Annual 2013-2024 | **METHOD_ONLY** — cite, don't use |
| **ChronoBERT / ChronoGPT / ChronoGPT-Instruct** (He et al. 2025, arxiv 2502.21206) | **Yes** (`manelalab/chrono-*-v1-*` with verified SHAs) | English-only per model cards | Annual 1999-2024 | **METHOD_ONLY** — closest to fleet-add if Chinese capability ever verified; optional smoke test on `chrono-gpt-instruct-v1-20241231` recommended |
| **Time Machine GPT** (arxiv 2404.18543, NAACL 2024 Findings) | Yes (`Ti-Ma/TiMaGPT2-*`) | English-only (WMT News + Wikipedia) | Annual 2011-2022 | **METHOD_ONLY** — too early, no 2023+ coverage |
| **StoriesLM** (new discovery) | Yes (`StoriesLM/StoriesLM-v1-*`) | English-only | 1900-1963 | **METHOD_ONLY** — historical context only |
| **NoLBERT** (arxiv 2509.01110, new discovery) | Yes (`alikLab/NoLBERT`) | English-only | 1976-1995 | **METHOD_ONLY** — introduces "lookaback bias" concept |
| **PiT-Inference** (pitinference.com) | Vendor claim; opaque | Unverified | Cutoff ~Jan 2020 per Look-Ahead-Bench | **REJECT** — no reproducible public release |
| **Bendemra 2024 Frontier Models** | Not verified | - | - | **REJECT** — probable citation error (likely confused with Benhenda Look-Ahead-Bench) |
| **FINSABER** (arxiv 2505.07078, KDD 2026) | Yes (GitHub `waylonli/FINSABER`) | Framework, not model | Framework-side PiT 2004-2024 | **METHOD_ONLY** — benchmarking framework precedent, not a model |

### Fleet verdict: keep v5.2 6-model fleet unchanged

No verified chronologically-controlled family clears all four fleet-add gates (downloadable + nonredundant cutoff in [2023-10, 2025-07] + usable Chinese capability + compute-fit). The v5.2 fleet (Qwen 2.5-7B, DeepSeek-V2.5, GLM-4-9B-0414, DeepSeek-V3-0324, Qwen3-14B, Claude Sonnet 4.5) should stand operationally. Cite DatedGPT and ChronoBERT/ChronoGPT prominently in the paper's methods section as the strongest chronological-control precedents. Optional one-off validation: run a Chinese smoke test on `chrono-gpt-instruct-v1-20241231` on a handful of CLS items to confirm the Chinese-capability concern — if it fails, the fleet decision is fully settled; if it passes, reopen the question.

---

## Sub-task D — Cited-but-unread sweep

**Executed 2026-04-15.** Full raw output at `refine-logs/reviews/LIT_SWEEP_D_CITED_BUT_UNREAD.md` (235 lines).

### Methodology

Walked backwards from 10 seed library papers (spine-factor precedents + chrono baselines + entity-level memorization) via Semantic Scholar Graph API for reference lists. 3 seeds fell back to arxiv HTML bibliography extraction due to Semantic Scholar rate limits. **Total references collected: 334. Unique after seed-to-seed dedup: 292. Not in INDEX: 273. Not already in Sweep B: 271.** Priority triage: 0 P0, 10 P1, 7 P2, 254 P3.

### Summary of findings

**No P0 hidden competitor surfaced.** The strongest misses are methodology papers, not benchmark competitors. Two distinct clusters emerged:

1. **Classical privacy/MIA foundations** (library is thinner here than on extraction):
   - Shokri et al. 2016/2017 "Membership Inference Attacks Against ML Models" (arxiv 1610.05820, 5056 citations) — cited by Seeds 7 + 8
   - Carlini et al. 2022 "Membership Inference Attacks From First Principles" (arxiv 2112.03570, 1026 citations) — cited by Seeds 1 + 8
   - McCoy et al. 2021 "How Much Do LMs Copy From Their Training Data? (RAVEN)" (TACL, 167 citations) — cited by Seeds 7 + 8

2. **Chronologically-controlled precursors beyond what Sub-task C covered**:
   - Drinkall et al. 2024 "Time Machine GPT" (arxiv 2404.18543) — already verified as public HF family by Sub-task C, cited by MemGuard-Alpha
   - Sarkar & Vafa 2024 "Lookahead Bias in Pretrained Language Models" (SSRN 4754678) — cited by ChronoBERT + MemGuard
   - Levy 2025 "Caution Ahead: Numerical Reasoning and Look-ahead Bias in AI Models" (SSRN 5082861) — cited by ChronoBERT + MemGuard
   - Sarkar 2024 "StoriesLM" (SSRN, partially covered by Sub-task C)

**Additional P1 hits:**
- Zhang et al. 2024 "Min-K%++" (arxiv 2404.02936) — direct detector follow-up to library's Min-K%
- Meeus et al. 2024 "Inherent Challenges of Post-Hoc MIA for LLMs" (arxiv 2406.17975) — skepticism paper on the MIA family MemGuard operationalizes
- Tirumala et al. 2022 "Memorization Without Overfitting" (arxiv 2205.10770) — cited by Glasserman-Lin, connects finance look-ahead to memorization dynamics
- Kasai et al. 2022 "RealTime QA" (arxiv 2207.13332) — temporal-QA benchmark predecessor cited by Dated Data + Set the Clock

### Cross-seed co-citation observations

- 3 papers cited by 3+ seeds are all background infrastructure (GPT-2, T5, The Pile) — not reviewer-killers
- Chrono ↔ memorization cross-domain edges: classical finance-text papers (Tetlock 2007, Loughran-McDonald "More than Words", Ke-Kelly-Xiu "Predicting Returns with Text Data") are cited by BOTH ChronoBERT and Glasserman-Lin — chrono-control story is more tightly connected to old finance NLP than the current library suggests
- Privacy/MIA foundations cluster cited by memorization seeds but NOT chrono-control seeds — this is exactly the gap MemGuard-Alpha newly operationalizes in finance

### Candidate new-factor queue contributions from D
None new. `Entity Neutering` (Engelberg et al. 2025, SSRN) surfaced as additional cited-but-unread support for the already-queued Entity-Anonymization Sensitivity concept.

### D's PDF download candidates (10 P1, exactly at cap)

See `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md` Section "v6.1 + post-Session-2 download approval".

---

## Sub-task E — 3-bloc construct-collapse validation

**Executed 2026-04-15.** Full raw output at `refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md` (412 lines). **This was the highest-value deferred item** — direct validation of the cold reader's biggest-risk finding.

### Headline verdict

**The 3-bloc structure is NOT literature-validated. Downgrade from "literature-validated latent structure" to "descriptive working hypothesis."** The strongest literature-backed refinement is a **4-bloc** stress test separating `Cutoff Exposure` / temporal exposure as its own construct. The strongest methodological counter-finding is that **modern construct-validity work treats correlation/factor structure as insufficient on its own** for construct validation.

### Executive answers to the three primary questions

**Q1. Is our 3-bloc structure validated by published work?** **No direct validation found.** Adjacent literature gives the conceptual ingredients but no published empirical validation of FinMem's exact three latent constructs.

**Q2. Does any published work propose a different decomposition?** **Yes**, three alternatives:
- **Burnell et al. 2023** "Revealing the structure of language model capabilities" (arxiv 2306.10062) — Bayesian + frequentist factor analysis across 29 LLMs × 27 tasks finds 3 latent factors, but they are `reasoning / comprehension / core LM`, not FinMem-style factors. **Shows that "three factors" is not itself validating — content matters.**
- **Petrova & Burden 2026** "Pressure Reveals Character" (arxiv 2602.20813) — factor analysis over 6 alignment categories collapses to **1 general factor**. Adjacent precedent that apparent category diversity can collapse completely.
- **Kearns 2026** "Quantifying construct validity in LLM evaluations" (arxiv 2602.15532) — argues standard latent factor models often proxy model scale and scaling laws ignore measurement error; proposes a **structured capabilities model** separating scale, latent capability, and measurement error. Not a fixed N-bloc.

**Q3. Does any published work challenge the construct-collapse framing itself?** **Yes, extensively.** The construct-validity tradition is explicit that correlation structure alone is insufficient for construct interpretation:
- **Cronbach & Meehl 1955** "Construct Validity in Psychological Tests" — foundational. Construct validity is a nomological network, not a single coefficient.
- **Xiao et al. 2023** "Evaluating Evaluation Metrics" (EMNLP) — factor analysis only indicates whether/how many latent dimensions may exist; naming them requires theorization. Recommends MTMM-style convergent/divergent validity.
- **Freiesleben 2026** "Establishing Construct Validity in LLM Capability Benchmarks Requires Nomological Networks" (arxiv 2603.15121) — direct LLM-benchmark application of construct-validity theory.
- **Perlitz et al. 2024** "Do These LLM Benchmarks Agree? BenchBench" (arxiv 2407.13696) — benchmark correlation itself is highly unstable to reference benchmark / model subset / thresholding choices, so high agreement is not clean evidence of shared construct.
- **Bean et al. 2025** "Measuring what Matters: Construct Validity in LLM Benchmarks" (arxiv 2511.04703) — systematic review of 445 benchmarks showing construct-validity problems are widespread.

### The 4-bloc refinement

Codex E's strongest literature-backed recommendation is to separate **temporal exposure** as a fourth bloc:

1. **Temporal exposure / cutoff overlap** — Cutoff Exposure (new, separated bloc)
2. Repetition / surface reuse — Propagation Intensity, Template Rigidity, surface_template_recurrence
3. Prominence / entity prior knowledge — Entity Salience (target), Target Scope, Tradability Tier
4. Institutional stage / source structure — Structured Event Type, Disclosure Regime, Event Phase, Session Timing

Rationale: **Cutoff Exposure is already outside all 3 blocs in the current v6 Risk R4 section** (the cold reader implicitly treated it as separate). Glasserman & Lin 2024 explicitly separate look-ahead bias from distraction/company-general-knowledge bias. Kong et al. 2026 treat look-ahead bias as one of five distinct structural biases. The 4-bloc refinement makes this implicit separation explicit and matches the literature.

### Additional refinement proposals from E

- **Prominence bloc should be internally split** between entity fame (Entity Salience target part) and market/investment relevance (Tradability Tier) — Boukes & Vliegenthart 2020 separate `eliteness` from `influence/relevance`; Glasserman-Lin separate general knowledge from sentiment; Nakagawa 2024 measures company-specific bias as distinct.
- **Institutional stage bundle should remain linked but not collapsed** — the economic-news literature (Boukes & Vliegenthart 2020 `continuity / eliteness / influence/relevance / outlet-type`) treats these as partly distinct newsroom routines. Correlations may reflect genuine domain structure, not redundancy.
- **Any latent reduction should be treated as descriptive robustness, not validity proof** — this is Cronbach-Meehl + Xiao + Freiesleben + Kearns converging.

### Cross-domain methodology precedents for Risk R4 mitigation

- **IRT / psychometrics for NLP**: Lalor 2016 (building NLP eval scales), Vania 2021 (comparing test sets with IRT), Byrd & Srivastava 2022 (predicting difficulty/discrimination), Zhou et al. 2025 "Lost in Benchmarks: IRT for LLM benchmarking" (arxiv 2505.15055)
- **Benchmark meta-analysis**: BenchBench (arxiv 2407.13696), Madaan 2024 "Quantifying Variance" (arxiv 2406.10229), Burnell 2023 (arxiv 2306.10062)
- **Fama-French-for-LLM-evaluation**: NOT found. Closest analogues are Kearns 2026 structured capabilities model + Kong et al. 2026 finance structural validity framework.
- **Domain-adjacent**: Boukes & Vliegenthart 2020 (arxiv: no — Sage Journals) — news factors in economic newsworthiness; `continuity / eliteness / influence/relevance / outlet-type`.

### Candidate new-factor queue contributions from E — resolved 2026-04-15

Three concepts entered the queue from Sub-task E and/or user follow-up (the user split Influence/Relevance from a separately-discussed Eliteness concept per "影响力和精英性可以看一下"):

- **Q3 Influence / Relevance** (from Boukes & Vliegenthart 2020) — news-factor concept for how broadly an event affects audience life/decisions/worldview, distinct from entity fame. **USER DECISION: RESERVE** (overriding orchestrator drop recommendation). User reasoning: LLM-agent semantic annotation is cheap (common-sense judgement, no external data), so reserve cost is low.
- **Q5 Eliteness** (new, from same Boukes & Vliegenthart source, surfaced by user follow-up distinguishing it from Influence/Relevance) — news-factor concept for semantic/ontological institutional hierarchy (e.g., State Council > central ministry > provincial regulator > listed firm > local enterprise). Distinct from Entity Salience (CLS-frequency Zipfian) and Target Scope (binary company vs non-company). **USER DECISION: RESERVE**. Same cheap-annotation reasoning.
- **Q4 Geographical Proximity** (from Boukes & Vliegenthart 2020) — standard news-factor concept. **USER DECISION: DROP**. User reasoning: LLM pretraining corpora are global and English-heavy, so geographical distance does not straightforwardly translate to training-data frequency differences; additional reasons documented in decision doc v6.2 Dropped section.

Both Q3 and Q5 are now recorded in `docs/DECISION_20260413_mvp_direction.md` v6.2 Reserve list (items 16 and 17). Q4 is recorded in the v6.2 Dropped section.

### E's 5 PDF download candidates + 8 v6.1 edit proposals

See `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md` Section "v6.1 edits — post Session-2 awaiting user approval".

---

## Session 2 wrap — updated summary memo

**Session 1 + Session 2 combined findings:**

- **FinMem-Bench novelty claim holds.** 5 Codex calls (A/B/C + D/E) across two sessions surfaced ZERO P0 direct competitors.
- **Factor literature provenance**: 5 STRONG / 8 PARTIAL / 2 NOVEL (Disclosure Regime, Session Timing). Unchanged from Session 1.
- **Biggest Session 2 finding — construct collapse framing needs refinement**: the cold reader's 3-bloc decomposition is NOT literature-validated. Recommended refinement is a **4-bloc** stress test separating Cutoff Exposure as its own construct, AND downgrading the entire bloc story from "validated latent structure" to "descriptive working hypothesis" per the Cronbach-Meehl / Xiao / Freiesleben / Kearns construct-validity tradition.
- **Cited-but-unread gap**: library is thinner on classical privacy/MIA foundations (Shokri 2016, Carlini 2022 "First Principles", RAVEN) than on extraction papers. Also thinner on chrono-control precursors (Time Machine GPT, Sarkar-Vafa 2024, Caution Ahead).
- **Candidate new-factor queue final state (2026-04-15 user decisions)**: Q1 Coverage Breadth gated on feasibility pilot; Q2 Entity-Anonymization Sensitivity routed to R5 as detector-level field under Principle P5; Q3 Influence/Relevance added to decision-doc Reserve (v6.2); Q4 Geographical Proximity DROPPED; Q5 Eliteness added to decision-doc Reserve (v6.2). Reserve list grew from 3 to 5 items.
- **Remaining blind spots**:
  1. CNKI Chinese literature still not searched (optional dedicated session)
  2. Fama-French-for-LLM-evaluation analog does NOT appear to exist in the literature — FinMem-Bench is entering under-theorized territory for factor-independence validation in memorization benchmarks
  3. No finance/NLP paper runs SEM/EFA/CFA directly on article-side memorization factors

---

---

## Candidate new-factor queue — final state (2026-04-15)

**Per v5.3 user clarification:** if during the sweep a promising factor concept surfaced that was NOT in the 15+2 shortlist, it was queued here for the user's decision rather than silently absorbed. All 5 queue items are now resolved. Final state below.

### Q1 — Coverage Breadth / Media Coverage — **GATED ON FEASIBILITY PILOT**

**Source:** Sub-task A cross-factor observations.
**Concept:** how broadly an event is covered across publishers, not only within-corpus duplication (distinct from Propagation Intensity's `cluster_size` and `prior_family_count_365d`, which are CLS-internal).
**Evidence tier:** indirect. Finance attention literature (Fang & Peress 2009, Hirshleifer et al. 2023) and representation-bias work (Dimino et al. 2025, arxiv 2510.05702).
**P1 source class:** potentially **extra-corpus** if operationalized via cross-publisher coverage counts — could restore P1 headroom.
**User decision (2026-04-15):** **GATED**. Hold as conditional candidate pending the 100-cluster feasibility pilot specified in `docs/MEDIA_COVERAGE_FEASIBILITY.md`. Do NOT promote until pilot completes.

### Q2 — Entity-Anonymization Sensitivity — **ROUTED TO R5 (detector-level)**

**Source:** Sub-task A + Sub-task B `Anonymization and Information Loss` (Wu et al. 2025, arxiv 2511.15364).
**Concept:** magnitude of detector-score change when entity names are replaced by anonymous placeholders.
**Evidence tier:** direct (Glasserman-Lin 2024, Nakagawa 2024, Wu et al. 2025).
**User decision (2026-04-14):** **ROUTED TO R5** as a detector-level stratification field under Principle P5. User explicitly noted it is analogous to the counterfactual detector's "反事实显著程度" — it is a property of the detector's response, not of the article. Already documented in decision doc v6.1 R5 handoff section as Edit P1.8.

### Q3 — Influence / Relevance — **RESERVE (decision doc v6.2 item 16)**

**Source:** Sub-task E + Boukes & Vliegenthart 2020 news-factor theory.
**Concept:** how broadly an event affects the audience's life, decisions, or worldview, distinct from entity fame.
**User decision (2026-04-15):** **RESERVE**. User overrode orchestrator drop recommendation. Reasoning: LLM-agent semantic annotation is cheap (common-sense judgement, no external data needed), so reserve cost is low. Re-evaluate after R5 results. Recorded in decision doc v6.2 Reserve section as item 16.

### Q4 — Geographical Proximity — **DROPPED**

**Source:** Sub-task E + Boukes & Vliegenthart 2020 news-factor theory.
**Concept:** standard news-factor concept of geographical distance from the audience.
**User decision (2026-04-15):** **DROP**. User reasoning: LLM pretraining corpora are global and English-heavy, so geographical distance does not straightforwardly translate to training-data frequency differences. Additional reasons documented in decision doc v6.2 Dropped section.

### Q5 — Eliteness — **RESERVE (decision doc v6.2 item 17)**

**Source:** Sub-task E + Boukes & Vliegenthart 2020 (user separated this from Q3 per "影响力和精英性可以看一下").
**Concept:** semantic/ontological "how high in the institutional hierarchy is the actor/event" (e.g., State Council > central ministry > provincial regulator > listed firm > local enterprise). Distinct from Entity Salience (CLS-frequency Zipfian) and Target Scope (binary company vs non-company).
**User decision (2026-04-15):** **RESERVE**. Same cheap-annotation reasoning as Q3. Recorded in decision doc v6.2 Reserve section as item 17. Promotion gated on R5 joint-modeling results showing independent signal vs Target Scope / Entity Salience / Authority.

---

## Blind spots remaining open

1. **CNKI-first Chinese literature under-covered.** The sweep used arxiv API + web_search + Semantic Scholar, but not a dedicated Chinese academic index. Some non-arxiv Chinese work on financial NLP memorization / contamination may exist. Recommended follow-up: a dedicated Chinese academic index session (can be a sub-agent or a focused /arxiv-style skill invocation).
2. **Venue-only paywalled finance papers partially visible.** Web snippets catch titles + abstracts but full-text verification is limited without download. Some P2 items in the broad sweep are at this level.
3. **BizFinBench primary source not verified.** Codex B saw secondary references but could not verify a primary citable paper in-session.
4. **Sub-task D (cited-but-unread)** and **Sub-task E (3-bloc construct-collapse validation)** are designed-in deferrals, not gaps.

---

## PDF download candidates (for user approval — ≤10 cap without approval)

See `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md` for the prioritized download list and approval request. Total across A + B: ~12 P1 candidates. The user must approve before any PDFs are downloaded and added to `related papers/INDEX.md`.

---

## Handoff to Session 2

When Session 2 opens:

1. User has reviewed this report and approved: (a) v6 edit proposals, (b) PDF download list, (c) candidate new-factor queue decisions.
2. Downloads execute with `INDEX.md` + `notes/*.md` updates.
3. Sub-task D (cited-but-unread) runs: consolidated reread of 5 most-relevant note files to surface not-yet-indexed paper titles, then Codex-qualify the top 10.
4. Sub-task E (3-bloc construct-collapse validation) runs: 1 Codex call targeted at published work measuring correlations between similar factor blocs in financial NLP or benchmark design.
5. Optional: dedicated Chinese academic index session for CNKI blind spot.
6. Session 2 output: finalized `docs/LITERATURE_SWEEP_2026_04.md` with D + E sections filled, and a v5.3 → v6 edit application (applied by a fresh session, not this sweep).
