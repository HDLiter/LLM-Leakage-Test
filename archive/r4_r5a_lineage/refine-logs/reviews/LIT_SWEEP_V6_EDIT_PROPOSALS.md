# Literature Sweep → Decision Doc v5.3 → v6 Edit Proposals

**Date:** 2026-04-14
**Status (2026-04-14 post-checkpoint):** **USER-APPROVED — READY FOR v6 APPLY**
**Based on:** R4 Literature Sweep Session 1 (Sub-tasks A + B + C).
**Source references:** `docs/FACTOR_LITERATURE_PROVENANCE.md`, `docs/LITERATURE_SWEEP_2026_04.md`, and the raw Codex outputs in `refine-logs/reviews/LIT_SWEEP_A_*.md` / `_B_*.md` / `_C_*.md`.

---

## User decisions at mid-sweep checkpoint (2026-04-14)

1. **All P0 edits (4)**: APPROVED — apply to v6.
2. **All P1 edits (7)**: APPROVED — apply to v6.
3. **All P2 edits (4)**: APPROVED — apply to v6.
4. **PDF download list**: APPROVED **option (A) — all 12 papers**. Download all, update `INDEX.md` and relevant `notes/*.md`.
5. **Candidate Q1 — Coverage Breadth / Media Coverage**: **GATED ON FEASIBILITY**. User notes the concept is semantically compelling but requires a feasibility analysis showing how the factor would be computed before any promotion decision. A dedicated feasibility document (`docs/MEDIA_COVERAGE_FEASIBILITY.md`) is being produced in parallel with the v6 apply. Edit P0.4 keeps Coverage Breadth as a P1-restoration candidate under Principle P1 but does NOT promote it to the factor list. Final promote / reserve / drop / defer decision waits on the feasibility analysis.
6. **Candidate Q2 — Entity-Anonymization Sensitivity**: **ROUTED TO R5 as a detector-level stratification field**. User explicitly notes it is analogous to the counterfactual detector's "反事实显著程度" — it is a property of the detector's response, not of the article, and therefore belongs under Principle P5 (detector-dependent factors are R5 territory). **Do NOT add to the factor list.** Instead, add a new edit (see Edit P1.8 below, added post-checkpoint) that records Entity-Anonymization Sensitivity in the R5 handoff notes as a seeded detector-level stratification field R5 must evaluate.

---

## Edit P1.8 (added post-checkpoint, approved) — Entity-Anonymization Sensitivity → R5 as detector-level stratification field

- **Action type:** ADD
- **Target:** R5 handoff section in `docs/DECISION_20260413_mvp_direction.md`, specifically the "Detector-dependent factors (Principle P5)" seeded list OR a new subsection "Detector-level stratification fields seeded by the R4 literature sweep"
- **Rationale:** The sweep surfaced Entity-Anonymization Sensitivity as a well-supported construct (Glasserman & Lin 2024 arxiv 2309.17322, Nakagawa et al. 2024 arxiv 2411.00420, Wu et al. 2025 arxiv 2511.15364). The user confirmed it is a **detector-level** property (like counterfactual significance / 反事实显著程度), not an article-level factor. Principle P5 already assigns detector-dependent fields to R5. This edit records the construct as a seeded R5 input so R5 Step 1 brainstorm does not re-discover it cold.
- **Proposed text to add (as a new bullet under the existing R5 handoff section's "Detector-dependent factors" or "Open questions R5 must explicitly address" block):**
  > **Detector-level stratification field — Entity-Anonymization Sensitivity.** Magnitude of a detector's score change when entity names in the measurement text are replaced by anonymous placeholders. Direct literature support: Glasserman & Lin 2024 (arxiv 2309.17322, anonymized-headlines distraction effect), Nakagawa et al. 2024 (arxiv 2411.00420, company-specific bias in financial sentiment), Wu et al. 2025 (arxiv 2511.15364, anonymization information-loss tradeoff). This is a **detector-level probe** analogous to the counterfactual detector's "反事实显著程度" — the stratum is a property of how the detector responds, not a property of the article text. R5 Step 1 should evaluate whether to include it as a seeded detector-level stratification field and, if yes, which detector families it applies to (Min-K%, MIA, CMMD, SR/FO counterfactual probes, FinMem-NoOp).

---

## How to read this file

Each edit proposal is tagged with:
- **Priority**: P0 = must apply to v6 (fixes an exposed construct or a factual error); P1 = strongly recommended; P2 = nice-to-have.
- **Action type**: `ADD`, `STRENGTHEN` (extend existing language), `REFRAME` (change emphasis or framing), `CAVEAT` (add a construct caveat), `CITATION` (add a citation without other change).
- **Target section** of `docs/DECISION_20260413_mvp_direction.md`.
- **Rationale**: which sweep finding drives this.

The total volume of proposed edits is intentionally modest. The sweep did not find P0 surprises — FinMem-Bench novelty holds. Most edits are caveat-strengthenings and literature-citation additions, not structural changes.

---

## P0 edits (must apply)

### Edit P0.1 — Cutoff Exposure gray-band is benchmark-specific, not literature-standard

- **Action type:** CAVEAT
- **Target:** Factor 2 (Cutoff Exposure) construct caveat in the 12-factor shortlist
- **Rationale:** Sub-task A explicitly searched for published precedent for a symmetric ±K gray-band exclusion zone around the cutoff and found NONE. The current construct caveat says the measure is timing not exposure but does not flag that the ±K exclusion is our design choice.
- **Proposed text to add to the existing construct caveat block:**
  > **Literature provenance (v6 addition):** The ±K gray-band exclusion is a benchmark-specific design choice to reduce misclassification around uncertain cutoffs. No verified published precedent exists for a symmetric gray-band exclusion zone as a factor-design convention. Document this in the pre-commit as a methodological choice, not a literature-standard convention.

### Edit P0.2 — Disclosure Regime must name its novel status explicitly

- **Action type:** STRENGTHEN
- **Target:** Factor 7 (Disclosure Regime) section in the 12-factor shortlist
- **Rationale:** v5.3 already says Disclosure Regime is a placeholder, but does not state that the sweep found **NO direct memorization-factor precedent for source provenance / disclosure type**. Current readers may assume "placeholder" means "minor operationalization gap"; the sweep confirms the construct itself is novel.
- **Proposed text to add:**
  > **Literature provenance (v6 addition):** The R4 literature sweep (2026-04-14) found no verified memorization/contamination benchmark that uses formal disclosure vs commentary/secondary coverage as a factor. Adjacent finance literature distinguishes official clarifications, regulatory filings, press releases, rumors, and commentary, but not as a memorization factor. This factor is therefore NOVEL in the memorization benchmark literature and must be justified mechanistically in the paper, not by citation. If retained through R5, its overlap with Modality, Authority, Event Phase, Template Rigidity, and Session Timing must be reported transparently.

### Edit P0.3 — Session Timing must name its novel status explicitly

- **Action type:** STRENGTHEN
- **Target:** Factor 10 (Session Timing) construct caveat in the 12-factor shortlist
- **Rationale:** v5.3 already says Session Timing's memorization mechanism is weak. The sweep confirms NO published memorization precedent exists for announcement timing as a factor. The caveat should name this explicitly so readers understand the factor is exploratory, not literature-backed.
- **Proposed text to add:**
  > **Literature provenance (v6 addition):** The R4 literature sweep (2026-04-14) found no verified memorization/contamination paper that uses announcement timing as a factor. Finance literature supports DellaVigna & Pollet 2009 style investor-inattention effects at the market level, but not memorization effects at the model level. This factor is therefore NOVEL in the memorization benchmark literature and should be treated as a low-confidence auxiliary with a weak proposed mechanism.

### Edit P0.4 — P1 Extra-corpus headroom discussion should reference sweep-surfaced candidates

- **Action type:** ADD
- **Target:** Principle P1 "Extra-corpus signal principle" section, specifically the "Possible P1 restorations (all deferred)" bullet list
- **Rationale:** Sub-task A queued Coverage Breadth / Media Coverage as a candidate new factor that could potentially be **extra-corpus** if operationalized via cross-publisher coverage counts. This is a genuinely new P1 restoration option that did not exist in v5.3.
- **Proposed text to add as a 4th bullet:**
  > (d) **Coverage Breadth / Media Coverage** as an extra-corpus factor candidate surfaced by the R4 literature sweep. Finance attention literature (Fang & Peress 2009, Hirshleifer et al. 2023) and recent representation-bias work (Dimino et al. 2025, arxiv 2510.05702) suggest cross-publisher coverage breadth drives visibility effects in LLMs. Operationalization would require an extra-corpus coverage count per event cluster from publishers outside CLS. **Status: queued in the candidate-new-factor list for user decision, not promoted.**

---

## P1 edits (strongly recommended)

### Edit P1.1 — Propagation Intensity should cite the Japanese newspaper replication

- **Action type:** CITATION
- **Target:** Factor 1 (Propagation Intensity) literature provenance notes
- **Rationale:** Ishihara & Takahashi 2024 "Quantifying Memorization and Detecting Training Data of Pre-trained Language Models using Japanese Newspaper" (arxiv 2404.17143) directly replicates the duplication/frequency memorization pattern in a news domain in a non-English language. This is the single strongest cross-lingual non-English replication relevant to FinMem-Bench's Chinese setting and should be cited in the paper.
- **Proposed addition:** add Ishihara 2024 to the factor provenance bullet list and queue the PDF for download.

### Edit P1.2 — Template Rigidity should cite Lee et al. 2021 explicitly

- **Action type:** CITATION
- **Target:** Factor 8 (Template Rigidity) literature provenance notes
- **Rationale:** Lee et al. 2021 "Deduplicating Training Data Makes Language Models Better" (arxiv 2107.06499) is the foundational near-duplicate / repetitive-substring paper. Currently not explicitly cited by the factor block. A direct cite strengthens the factor's literature standing from STRONG to IRON-CLAD.
- **Proposed addition:** add the citation and queue the PDF for download.

### Edit P1.3 — Anchor Strength rubric is novel; acknowledge in the factor block

- **Action type:** STRENGTHEN
- **Target:** Factor 3 (Anchor Strength) construct caveat
- **Rationale:** Sub-task A found that Huet et al. 2025 Episodic Memories Benchmark provides conceptual precedent (temporal + spatial + entity event representation), but NO published rubric matches our 3-way density/triple-specificity/0-3-ordinal comparison. The current caveat says rubric selection is a reliability screen, not construct validation, but does not acknowledge the rubric itself is novel.
- **Proposed text to add:**
  > **Literature provenance (v6 addition):** No published rubric matches our 3-way pre-registered comparison. Huet et al. 2025 (arxiv 2501.13121) provides the closest structured event representation, but not a benchmark-side scalar anchorability score. The Anchor Strength rubric chosen by P3 is therefore novel as an operational measure and should be described as "adapted from episodic-memory representation work" rather than "derived from prior literature."

### Edit P1.4 — Entity Salience split should cite Glasserman & Lin 2024 explicitly

- **Action type:** CITATION
- **Target:** Factor 4 (Entity Salience) construct caveat — the "dual field" explanation
- **Rationale:** The v5 construct caveat already separates Target Prominence and Competing-Entity Prominence. Glasserman & Lin 2024 (arxiv 2309.17322) is the direct published source for the distraction effect and should be cited as the motivation for the split, not just as a passing reference.
- **Proposed text to add:**
  > **Literature provenance (v6 addition):** The target-vs-competing split is directly motivated by Glasserman & Lin 2024 (arxiv 2309.17322), which reports that anonymized headlines outperform originals in-sample, with stronger effects for larger companies — evidence that competing-entity prominence drives distraction independently of target prominence. Nakagawa et al. 2024 (arxiv 2411.00420) and Wu et al. 2025 (arxiv 2511.15364) replicate the anonymization effect in financial sentiment.

### Edit P1.5 — Novelty distribution table should be added as a new sub-section

- **Action type:** ADD
- **Target:** after "R4 Step 1 + Step 2 outcome: 12-factor shortlist" section
- **Rationale:** The cold reader's critique (R4_FINAL_REVIEW) said the document describes the whole shortlist as equally literature-backed. The sweep now has an auditable per-factor novelty distribution (5 STRONG / 8 PARTIAL / 2 NOVEL). Adding this table separates strong, partial, and novel factors and is exactly what the cold reader asked for.
- **Proposed text:** add the novelty distribution table from `docs/LITERATURE_SWEEP_2026_04.md` as a new "Factor literature provenance summary" sub-section with a one-paragraph explanation.

### Edit P1.6 — CMMD fleet section should cite DatedGPT + ChronoBERT as precedent

- **Action type:** CITATION
- **Target:** "CMMD model fleet (R5 input from v5.2)" in Open considerations section
- **Rationale:** Sub-task C verified that the v5.2 6-model fleet should stand unchanged, but also verified that DatedGPT (arxiv 2603.11838) and ChronoBERT/ChronoGPT (arxiv 2502.21206, public HF checkpoints with SHAs) are the strongest chronologically-controlled precedents in the literature. These should be cited in the methods section of the paper even though they don't enter the operational fleet.
- **Proposed text to replace the "Research-grade chronologically-controlled alternatives to investigate in R4 literature sweep" bullet:**
  > **Research-grade chronologically-controlled precedents (v6 update post-R4 literature sweep):**
  > - **DatedGPT** (Yan et al. 2026, arxiv 2603.11838): 12 × 1.3B annual-cutoff 2013-2024. **Not yet downloadable** (weights pending paper acceptance per author page). **English-only** — no Chinese training data reported. Verdict: METHOD_ONLY, cite prominently in methods section, do not enter fleet.
  > - **ChronoBERT / ChronoGPT / ChronoGPT-Instruct** (He et al. 2025, arxiv 2502.21206): public HF releases at `manelalab/chrono-*-v1-20241231` with verified commit SHAs. **English-only** per every verified model card. Verdict: METHOD_ONLY. Optional: Chinese smoke test on `chrono-gpt-instruct-v1-20241231` to confirm Chinese-capability concern.
  > - **Time Machine GPT** (Guo et al. 2024, arxiv 2404.18543, NAACL Findings): public HF (`Ti-Ma/TiMaGPT2-*`), 2011-2022, GPT-2 small, English-only. METHOD_ONLY, too early for CLS-era.
  > - Additional chronologically-controlled families discovered by the sweep but not relevant to CLS era: **StoriesLM** (1900-1963), **NoLBERT** (arxiv 2509.01110, 1976-1995, introduces the "lookaback bias" concept). Both METHOD_ONLY.
  > - **PiT-Inference** — vendor claim, no reproducible public release. REJECT.
  > - **"Bendemra 2024 Frontier Models"** — probably a citation error (confused with Benhenda's Look-Ahead-Bench). Do not cite as a separate model family.
  > - **FINSABER** (arxiv 2505.07078, KDD 2026): benchmarking framework, not a model. Cite as methodological precedent for PiT benchmark design.
  >
  > **Fleet verdict:** the v5.2 6-model fleet should stand unchanged. No chronologically-controlled family clears all four fleet-add gates (downloadable + nonredundant cutoff in [2023-10, 2025-07] + usable Chinese capability + compute-fit).

### Edit P1.7 — R5 reading queue should absorb the 8 new P1 papers from broad sweep

- **Action type:** ADD
- **Target:** either a new "R5 reading queue" subsection in Open considerations, or folded into the existing R5 handoff notes
- **Rationale:** Sub-task B surfaced 8 new P1 papers that should be read before R5 detector decisions. They are not currently listed anywhere in v5.3.
- **Proposed content:** the table from `docs/LITERATURE_SWEEP_2026_04.md` Sub-task B "New P1 papers for the R5 reading queue".

---

## P2 edits (nice-to-have)

### Edit P2.1 — Add Profit Mirage + Look-Ahead-Bench as mandatory cites in the paper shell

- **Action type:** CITATION REMINDER
- **Target:** Decision 1 (framing deferred) or a new "paper citation obligations" note
- **Rationale:** Both papers are already in `related papers/` but the cold reader warned that factor-focus could bury them. Make the citation obligation explicit so the paper writer does not forget.
- **Proposed text:** add a one-line note in the paper-shell discussion: "Paper related-work section must cite MemGuard-Alpha (Roy & Roy 2026), Profit Mirage (Li et al. 2025, arxiv 2510.07920), and Look-Ahead-Bench (Benhenda 2026, arxiv 2601.13770) alongside the DatedGPT/ChronoBERT chronological-control precedents."

### Edit P2.2 — Event Phase literature precedent should be clarified

- **Action type:** STRENGTHEN
- **Target:** Factor 12 (Event Phase) construct caveat
- **Rationale:** Sub-task A found finance lifecycle precedent for rumor/confirmed-news phase distinction, but NO direct memorization-factor precedent. Current caveat says phase is "partly a sampling-design choice imposed by the benchmark" which is correct but does not acknowledge there is no published memorization direction to validate against.
- **Proposed text to add:**
  > **Literature provenance (v6 addition):** Finance event-study literature distinguishes rumor / clarification / official-announcement phases, and rumor-detection work treats rumor vs non-rumor as meaningful (Information Transmission Through Rumors in Stock Markets, 2016; M&A rumours in China, 2020). No published work validates event phase as a memorization factor. Treat the direction of any observed phase effect as a first-observation finding, not a replication of a known effect.

### Edit P2.3 — Interaction menu should cite multiverse/specification-curve methodology

- **Action type:** CITATION
- **Target:** Principle P4 (Pre-registered interaction menu)
- **Rationale:** Sub-task A surfaced multiverse analysis methodology (Ecker et al. 2023, arxiv 2308.16681) as the closest methodological precedent for pre-committed exploratory analysis. Current Principle P4 does not cite any methodology source for the interaction menu framework.
- **Proposed text:** add a one-line citation to multiverse/specification-curve analysis as methodological precedent for the interaction menu framework.

### Edit P2.4 — R5 handoff should note the CMMD "lookback/lookaback bias" concept

- **Action type:** ADD
- **Target:** R5 handoff section
- **Rationale:** NoLBERT (arxiv 2509.01110) introduces the "lookaback bias" concept as dual to lookahead bias. This is conceptually interesting for R5 detector design — a detector should probably measure both lookahead memorization AND memorization of pre-cutoff content. Not in v5.3 anywhere.
- **Proposed text:** add a paragraph to R5 handoff notes noting that the lookaback-bias concept from NoLBERT should be considered when designing detector coverage.

---

## Candidate new-factor queue (user decision required)

Per user v5.3 instruction: the sweep queues candidate new factors for user review rather than silently absorbing or recommending them. The user decides promotion / hold / drop.

### Queue item Q.1 — Coverage Breadth / Media Coverage

- **Source:** Sub-task A cross-factor observations + Sub-task B Didisheim 2025 + Dimino et al. 2025
- **Concept:** event coverage breadth across publishers outside CLS. Distinct from Propagation Intensity (within-CLS).
- **Novelty:** PARTIAL_PRIOR_ART. Indirect support from finance attention literature and representation-bias work. Not validated as a memorization factor directly.
- **P1 source class:** **extra-corpus** if operationalized via cross-publisher coverage counts — would restore P1 headroom.
- **User decision options:**
  - **(a) Promote** as a 13th active factor, auxiliary tier. Adds one extra-corpus factor to the shortlist.
  - **(b) Reserve** alongside Exact-Span Rarity.
  - **(c) Drop** as too close to Propagation Intensity + Authority.
  - **(d) Defer** to the Thales dedicated session for operationalization feasibility.

### Queue item Q.2 — Entity-Anonymization Sensitivity

- **Source:** Sub-task A + Sub-task B Wu et al. 2025 (arxiv 2511.15364)
- **Concept:** magnitude of detector-score change when entities in an article are replaced by anonymous placeholders. Operationalizes the Glasserman-Lin distraction-vs-leakage decomposition as an explicit probe.
- **Novelty:** STRONG_PRIOR_ART (Glasserman & Lin 2024, Nakagawa et al. 2024, Wu et al. 2025).
- **Category ambiguity:** this is a **detector-level feature**, not an article-side factor. It may be better placed under Principle P5 (detector-dependent factors are R5 territory) than in the factor shortlist.
- **User decision options:**
  - **(a) Promote** as a 13th active factor, auxiliary tier.
  - **(b) Route to R5** as a detector-level stratification field under Principle P5.
  - **(c) Drop.**

---

## PDF download candidates (for user approval)

The kickoff caps automatic PDF downloads at ≤10 without user approval. Total P1 candidates across Sub-tasks A + B: **12 papers**. Listed below in priority order. User should accept, reject, or trim each line.

### From Sub-task A

| # | Paper | Authors, year | arxiv_id | Why |
|---|---|---|---|---|
| 1 | Quantifying Memorization and Detecting Training Data of PLMs using Japanese Newspaper | Ishihara & Takahashi 2024 | [2404.17143](https://arxiv.org/abs/2404.17143) | Strongest cross-lingual non-English replication of duplication memorization. Directly relevant to Chinese CLS setting. |
| 2 | Deduplicating Training Data Makes Language Models Better | Lee et al. 2021 | [2107.06499](https://arxiv.org/abs/2107.06499) | Foundational near-duplicate / repetitive-substring paper. Iron-clad citation for Template Rigidity. |
| 3 | Fine-Grained Classification of Announcement News Events in the Chinese Stock Market | MDPI Electronics 2022 | [MDPI URL](https://www.mdpi.com/2079-9292/11/13/2058) | Chinese finance event taxonomy precedent, relevant to Structured Event Type + Modality. |
| 4 | One Model Many Scores: Multiverse Analysis | Ecker et al. 2023 | [2308.16681](https://arxiv.org/abs/2308.16681) | Methodological precedent for the interaction menu framework (Principle P4). |

### From Sub-task B

| # | Paper | Authors, year | arxiv_id | Why |
|---|---|---|---|---|
| 5 | AI's predictable memory in financial analysis | Didisheim et al. 2025 | [Economics Letters](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392) | Finance-specific journal paper on memorization-driven predictability. Reviewer-visible. |
| 6 | A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs | Merchant & Levy 2025 | [2512.06607](https://arxiv.org/abs/2512.06607) | Direct mitigation paper for finance backtesting contamination. |
| 7 | Evaluating LLMs in Finance Requires Explicit Bias Consideration | Kong et al. 2026 | [2602.14233](https://arxiv.org/abs/2602.14233) | Strongest finance-evaluation framework paper. Directly useful for structural validity language. |
| 8 | Do Large Language Models Understand Chronology? | Wongchamcharoen & Glasserman 2025 | [2511.14214](https://arxiv.org/abs/2511.14214) | Prerequisite paper for prompt-based anti-leakage protocols. |
| 9 | Anonymization and Information Loss | Wu et al. 2025 | [2511.15364](https://arxiv.org/abs/2511.15364) | Direct finance follow-up on anonymization vs look-ahead tradeoffs. |
| 10 | LiveTradeBench | Yu et al. 2025 | [2511.03628](https://arxiv.org/abs/2511.03628) | Reviewer-visible adjacent live benchmark. Cites Profit Mirage. |
| 11 | A Comparative Analysis of LLM Memorization at Statistical and Internal Levels | Chen et al. 2026 | [2603.21658](https://arxiv.org/abs/2603.21658) | Strongest cross-model memorization follow-up; CMMD relevance. |
| 12 | Benchmarking LLMs Under Data Contamination (Survey) | Chen et al. 2025 | [EMNLP 2025](https://aclanthology.org/2025.emnlp-main.511/) | Methodological benchmark-design synthesis. |

### Recommended cap decision

The user can:
- **(A) Approve all 12** — exceeds the ≤10 cap but is a one-time modest overage.
- **(B) Approve top 10** — drop candidates 11 and 12 (both methodologically useful but not factor-critical).
- **(C) Approve top 7** (#1, #2, #5, #6, #7, #8, #9) — the subset that directly strengthens the most exposed factors or fills the most reviewer-visible citation gaps. The remaining 5 can be added later.

**Orchestrator's recommendation: (B) approve top 10**, trim #11 and #12 until Session 2 produces a broader reading list from Sub-tasks D + E. The 2 dropped candidates can re-enter the list then.

### Also recommend (not new downloads, just notes updates)

- Add a note to `related papers/notes/contamination_detection.md` for the in-library papers `Profit_Mirage` and `Look-Ahead-Bench` explicitly framing them as direct adjacent prior art for FinMem-Bench, so the paper writer sees the obligation.

---

## What is NOT being proposed (Session 1)

- No factor added. No factor removed. No factor renamed.
- No modification of Principle P1-P5 core rules.
- No change to the 6-model CMMD fleet (it should stand).
- No change to the 3 latent blocs in Risk R4 (the sweep has not yet validated or refined the bloc structure — that is Sub-task E, deferred to Session 2).
- No change to the Thales dedicated session scope.
- No change to the Target N = 3,200 sampling reference.

The sweep is intentionally conservative in its edit proposals: its job is to strengthen the documentation's literature grounding, not to reopen R4 decisions.

---

# v6.1 edits — post Session-2 awaiting user approval

**Date added:** 2026-04-15
**Source:** `refine-logs/reviews/LIT_SWEEP_D_CITED_BUT_UNREAD.md` + `refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md`
**Status:** **PROPOSAL ONLY — awaiting user approval for v6.1 bump.** No file modifications applied.

Session 2 produced two categories of proposals:
1. **E's Risk R4 mitigation refinements** (8 edit proposals) — the core substantive update, addressing the cold reader's biggest-risk finding with now-literature-grounded language
2. **D's + E's new download list** (15 candidates: 10 from D + 5 from E)

## v6.1 edits — Risk R4 refinement from Sub-task E

### Edit v6.1-R4.1 (P0 — CORE SUBSTANTIVE REFINEMENT)

- **Action type:** REFRAME + ADD
- **Target:** Risk R4 opening paragraph in `docs/DECISION_20260413_mvp_direction.md` v6
- **Rationale:** Sub-task E confirmed that **no published work validates the exact FinMem 3-bloc decomposition**, and modern construct-validity literature (Cronbach & Meehl 1955, Xiao et al. 2023, Freiesleben 2026, Kearns 2026) explicitly treats correlation structure as insufficient for construct interpretation. The current Risk R4 language implicitly presents the 3-bloc decomposition as authoritative; it should be downgraded to "descriptive working hypothesis."
- **Proposed text:** Replace the current Risk R4 opening:
  > The 12-factor shortlist may project onto a smaller number of latent constructs. The current three-bloc map is a **descriptive working hypothesis introduced by the cold reader's review, NOT a literature-validated latent structure**. The R4 literature sweep (Sub-task E, 2026-04-15) searched for published empirical validation of similar decompositions in financial NLP, memorization benchmarks, and general LLM benchmark factor analysis, and found none. Adjacent literatures (Burnell et al. 2023 arxiv 2306.10062, Petrova & Burden 2026 arxiv 2602.20813, Kearns 2026 arxiv 2602.15532) provide alternative decompositions (3-factor with different content, 1-factor collapse, structured capabilities model) but none validate our specific repetition/prominence/institutional-stage story. **Published construct-validity work in LLM evaluation (Cronbach & Meehl 1955, Xiao et al. 2023 EMNLP, Freiesleben 2026 arxiv 2603.15121) explicitly treats correlation structure as suggestive but insufficient evidence for construct interpretation on its own.**

### Edit v6.1-R4.2 (P0 — 4-BLOC REFINEMENT)

- **Action type:** ADD
- **Target:** Risk R4 bloc structure (currently 3 blocs) in v6
- **Rationale:** Sub-task E's strongest literature-backed refinement is to separate `Cutoff Exposure` as its own bloc. This matches what the cold reader implicitly did (Cutoff Exposure is already outside all 3 blocs) and is directly supported by Glasserman & Lin 2024 (separates look-ahead bias from distraction) and Kong et al. 2026 (treats look-ahead bias as one of five distinct structural biases).
- **Proposed text:** ADD a new bloc at the top of the numbered list:
  > 0. **Temporal exposure / cutoff overlap** (added v6.1): Cutoff Exposure. Separated from the other three blocs because (a) it is case×model not pure case; (b) finance-LLM validity literature explicitly treats look-ahead bias as distinct from prominence/distraction/source mechanisms (Glasserman & Lin 2024 arxiv 2309.17322, Kong et al. 2026 arxiv 2602.14233); (c) the current 3-bloc decomposition already implicitly leaves Cutoff Exposure outside — this edit makes that separation explicit.

  Renumber the current 3 blocs as 1, 2, 3 becoming 2, 3, 4 and re-reference them in any downstream text.

### Edit v6.1-R4.3 (P0 — MITIGATION STRENGTHENING)

- **Action type:** STRENGTHEN
- **Target:** Risk R4 mitigation bullet list in v6
- **Rationale:** Current mitigation says "Bloc-level summary as a secondary analysis" without framing the status. E's literature search confirms bloc-level summaries should be descriptive robustness, not construct-validation evidence.
- **Proposed text:** Replace the current "Bloc-level summary" mitigation bullet with:
  > **Bloc-level summaries are secondary DESCRIPTIVE robustness analyses only.** They are reported to show whether coarse latent-structure summaries explain per-factor patterns, NOT to establish construct validity by themselves. Alternative decompositions are stress-tested alongside the primary 4-bloc summary: at minimum a one-factor collapse check (following Petrova & Burden 2026's finding that apparent category diversity can collapse to a single general factor) and a temporal-split four-bloc check. **Construct-validity interpretation rests on theory-led mechanism claims, convergent/divergent diagnostics per MTMM-style checks (Xiao et al. 2023 EMNLP), and negative-control checks — not on correlation structure alone.**

### Edit v6.1-R4.4 (P1 — INTERNAL BLOC SPLIT FOR PROMINENCE)

- **Action type:** CAVEAT
- **Target:** Risk R4 Bloc 2 (prominence — Entity Salience, Target Scope, Tradability Tier)
- **Rationale:** Boukes & Vliegenthart 2020 separate `eliteness` from `influence/relevance`; Glasserman & Lin 2024 separate general firm knowledge from sentiment; Nakagawa et al. 2024 measure company-specific bias as distinct. These support not collapsing entity fame + market liquidity into a single prominence construct.
- **Proposed text:** Add as a sub-bullet under the Prominence bloc description:
  > **Internal split caveat**: `Entity Salience (target part)` and `Tradability Tier` should not be assumed to measure the same prominence subconstruct even if they correlate. The economic-news literature (Boukes & Vliegenthart 2020) separates `eliteness` from `influence/relevance`. Joint modeling should allow these to load on distinct latent factors unless the data rules it out.

### Edit v6.1-R4.5 (P1 — SOURCE BLOC CAVEAT)

- **Action type:** CAVEAT
- **Target:** Risk R4 Bloc 4 (institutional stage — Structured Event Type, Disclosure Regime, Event Phase, Session Timing)
- **Rationale:** Economic-news literature treats these as partly distinct newsroom routines, not redundant measurements. Their correlation may reflect domain structure, not construct collapse.
- **Proposed text:** Add as a sub-bullet under the Institutional stage bloc description:
  > **Source-bloc interpretation caveat**: correlations among `Structured Event Type`, `Disclosure Regime`, `Event Phase`, and `Session Timing` should be interpreted cautiously because in financial news they may reflect **genuine domain structure and newsroom routines** (news production, outlet ecology, regulatory timing) rather than redundant measurement of one latent variable. Boukes & Vliegenthart 2020 treat `continuity`, `eliteness`, `influence/relevance`, and outlet-type differences as partly distinct.

### Edit v6.1-R4.6 (P1 — PRINCIPLE P4 FRAMING)

- **Action type:** CAVEAT
- **Target:** Principle P4 (Pre-registered interaction menu)
- **Rationale:** The interaction menu is a pre-registered heterogeneity menu, not a latent-structure validation device. This distinction should be explicit to avoid over-interpretation of interaction results.
- **Proposed text:** Add a framing sentence before the menu rules:
  > **P4 is NOT a latent-structure validation device**; it is a pre-registered heterogeneity menu. Latent-structure checks (bloc-level summaries, factor-independence tests) are reported separately under Risk R4's mitigation framework. Interaction pairs are prioritized when they help separate plausible latent blocs — especially temporal-vs-prominence and repetition-vs-prominence confounds. If a pre-registered interaction is motivated by bloc-separation rather than substantive moderation, the paper labels it a **diagnostic interaction** and interprets null/non-null results accordingly.

### Edit v6.1-R4.7 (P2 — REVIEWER-FACING METHODS LANGUAGE)

- **Action type:** ADD
- **Target:** Methods / related-work discussion (when the paper is written — anchor as a note in Decision 1 framing)
- **Rationale:** Pre-emptively framing the construct-validity stance in the paper's methods section neutralizes reviewer critiques of the bloc story.
- **Proposed text:** Note for paper writer:
  > Methods section should include a sentence along the lines of: "Following construct-validity guidance from Cronbach & Meehl (1955) and recent LLM benchmark methodology (Xiao et al. 2023 EMNLP, Freiesleben 2026), we treat factor correlations as **evidence to be explained**, not as self-interpreting proof of a latent structure. Accordingly, FinMem-Bench reports theory-led per-factor results, bloc-level descriptive summaries, and alternative decomposition stress tests, while avoiding claims that the 4-bloc structure has itself been empirically validated in prior literature."

### Edit v6.1-R4.8 (P2 — BENCHBENCH REFERENCE)

- **Action type:** CITATION
- **Target:** Risk R4 mitigation language
- **Rationale:** Perlitz et al. 2024 BenchBench (arxiv 2407.13696) shows benchmark correlation is highly unstable to reference choice / model subset / metric — directly applicable to FinMem's factor correlation robustness analysis.
- **Proposed text:** Add as an additional citation next to the bloc-level summary caveat:
  > (Perlitz et al. 2024 "BenchBench" arxiv 2407.13696 shows that within-benchmark agreement is method-sensitive; high factor correlation in FinMem should not be treated as self-validating evidence of latent collapse.)

## v6.1 candidate-new-factor queue additions (SURFACED ONLY, not recommended)

From Sub-task E, two weak candidates surfaced per the user's instruction to queue new factor concepts without silently absorbing them:

### Queue item Q.3 — Influence / Relevance

- **Source:** Boukes & Vliegenthart 2020, `A general pattern in the construction of economic newsworthiness?`
- **Concept:** news-factor concept distinct from `eliteness/prominence`; relates to market impact or broad significance.
- **Evidence tier:** weak — journalism content analysis, not memorization benchmark
- **Overlap:** partial with Entity Salience and Tradability Tier (and the already-queued Q.1 Coverage Breadth)
- **Recommendation:** **DROP** — too close to existing factors + Q.1 Coverage Breadth; weak mechanism link to memorization

### Queue item Q.4 — Geographical Proximity

- **Source:** Boukes & Vliegenthart 2020
- **Concept:** standard news-factor concept of whether the event is geographically close to the reader
- **Evidence tier:** very weak — memorization relevance is indirect
- **Overlap:** none with existing factors, but mechanism to memorization is unclear
- **Recommendation:** **DROP** — no credible memorization mechanism

## PDF download list — Session 2 (15 candidates, cap is 10)

### From Sub-task D (10 candidates, exactly at cap)

| # | Paper | Arxiv/URL | Why |
|---|---|---|---|
| D1 | Membership Inference Attacks Against Machine Learning Models | arxiv 1610.05820 | Shokri 2017. Foundational MIA paper, 5056 citations, library gap |
| D2 | Membership Inference Attacks From First Principles | arxiv 2112.03570 | Carlini 2022. Strongest post-Shokri MIA baseline, 1026 citations, MemGuard explicitly builds on it |
| D3 | Min-K%++ | arxiv 2404.02936 | Zhang 2024. Direct detector follow-up to library's Min-K%; MemGuard core MIA component |
| D4 | Inherent Challenges of Post-Hoc MIA for LLMs | arxiv 2406.17975 | Meeus 2024. Skepticism paper on the MIA family MemGuard operationalizes |
| D5 | Time Machine GPT | arxiv 2404.18543 | Drinkall 2024. Already verified public HF by Sub-task C. Chrono-control precedent |
| D6 | Lookahead Bias in Pretrained LMs | SSRN 4754678 | Sarkar & Vafa 2024. Direct conceptual predecessor to chrono finance evaluation; cited by ChronoBERT + MemGuard |
| D7 | Caution Ahead | SSRN 5082861 | Levy 2025. Finance look-ahead follow-up on numerical reasoning |
| D8 | How Much Do LMs Copy From Training Data? (RAVEN) | TACL 2023 | McCoy 2021. Bridges memorization ↔ output novelty; cited by Carlini + Kandpal |
| D9 | Memorization Without Overfitting | arxiv 2205.10770 | Tirumala 2022. Theory framing for training dynamics of memorization |
| D10 | RealTime QA | arxiv 2207.13332 | Kasai 2022. Temporal-QA benchmark predecessor for Cutoff Exposure story |

### From Sub-task E (5 candidates)

| # | Paper | Arxiv/URL | Why |
|---|---|---|---|
| E1 | Quantifying construct validity in LLM evaluations | arxiv 2602.15532 | Kearns 2026. Strongest modern paper on misidentified constructs in latent factor models |
| E2 | Establishing Construct Validity in LLM Capability Benchmarks | arxiv 2603.15121 | Freiesleben 2026. Clearest statement of how LLM benchmark construct validity should be argued |
| E3 | Evaluating Evaluation Metrics: Framework using Measurement Theory | aclanthology.org/2023.emnlp-main.676 | Xiao et al. 2023. Strongest NLP-native MTMM/factor-analysis precedent |
| E4 | Revealing the structure of language model capabilities | arxiv 2306.10062 | Burnell 2023. Direct empirical factor-analysis precedent |
| E5 | Do These LLM Benchmarks Agree? BenchBench | arxiv 2407.13696 | Perlitz 2024. Benchmark correlation stability analysis |

### Download cap decision

Total Session 2 candidates: **15**, cap is 10. The user must decide:

- **(A) All 15** — exceeds cap by 5. Recommended if you want the full construct-validity methodology foundation in the library.
- **(B) 10 from D + 0 from E** — methodology papers from D only, Risk R4 refinement cited but not in library. NOT RECOMMENDED because E's v6.1 edits cite all 5 E papers and they should be readable.
- **(C) 10 selected across D+E** — my recommended trim below.
- **(D) All 15** — user extends cap (recommended).

**Orchestrator's recommended trim to exactly 10 (option C):**
- From D: D1 (Shokri), D2 (Carlini First Principles), D3 (Min-K%++), D5 (Time Machine GPT), D6 (Sarkar-Vafa Lookahead Bias), D9 (Tirumala Memorization Without Overfitting) — **6 papers**, the most factor-relevant
- From E: E1 (Kearns), E2 (Freiesleben), E3 (Xiao EMNLP), E5 (Perlitz BenchBench) — **4 papers**, the ones cited most heavily in the v6.1 edits
- **Dropped from trim**: D4 (SoK/Inherent Challenges — R5 territory), D7 (Caution Ahead — niche), D8 (RAVEN — moderate relevance), D10 (RealTime QA — temporal-QA tangent), E4 (Burnell 2023 — cited in edits but not as centrally as E1/E2/E3/E5)

Better: option (A) all 15 — the cap is a soft recommendation, the library can absorb 5 extra papers without issue, and the whole point of the sweep is completeness before R5 opens.

