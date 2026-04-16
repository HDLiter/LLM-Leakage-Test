# DECISION: FinMem-Bench MVP Direction (v6.2)

**Date:** 2026-04-13
**Version:** v6.2 (post-R4 literature sweep Session 2 user decisions on candidate queue)
**Based on:** BENCHMARK_R1 + R2 + R3 + R4 Step 1 + R4 Step 2 + R4 Challenger + R4 Cold-Reader review + CMMD model fleet survey + Thales signal profile review
**Supersedes:** v4 (same-day late evening)
**Next rounds:**
- R5 — detector investigation (next session)
- R6 — final pre-registration integration → `docs/PREREGISTRATION_MVP.md`

## Dependent variable (one-sentence definition)

FinMem-Bench evaluates whether memorization detectors assign systematically different memorization scores to CLS Chinese financial event-cluster cases as a function of pre-specified case-level and case×model factors. The unit of analysis is one canonical CLS article per event cluster; the dependent variable is detector score; the experimental contrasts are the 12 factors in the shortlist below.

---

## Version history

- **v1** (2026-04-13 morning): initial 10 decisions post-R2
- **v2** (2026-04-13 afternoon): post-R3 decision check. B1 resolved cleanly; B2/B3/T1/T2 routed to dedicated tracks; T3 accepted; target N refined.
- **v3** (2026-04-13 evening): post-R4 Step 2 integration. Added 12-factor shortlist with Editor hierarchy, target N=3,200 reference with stopping-rule sampling, pre-registered interaction menu framework, 3 convergent shared-annotation risks captured. Factor operationalization details stay deferred to Thales-joint algorithm session.
- **v4** (2026-04-13 late evening): post-R4 Challenger cross-model check. Propagation Intensity gets a dual robustness companion (cluster-aware primary + cluster-free fallback); Anchor experiment upgraded to n=150 with escape hatch and bootstrap CI reporting; interaction menu gets 2 cross-agent pairs (template×cutoff, tail-entity diagnostic); Chinese-specific data quality flags and cognitive-science ad-hoc consultation added to Open Considerations; MemGuard-Alpha (Roy & Roy 2026) noted as direct prior art.
- **v5** (2026-04-13 late evening): post-cold-reader review (`refine-logs/reviews/BENCHMARK_R4_FINAL_REVIEW.md`). Cleanup pass: stale "What R4 should produce / can assume" sections rewritten; D13 / D14 values reconciled with Principles P3 / P4; Decision 3 / Decision 6 / Open Tracks reconciled with Principle P2 (P2 now binding for canonical selection, Thales-joint session only handles operational details); construct collapse risk explicitly captured as Risk R4 (the cold reader's biggest single-risk finding); P1 audit table added; P2 algorithm details added (no-match handling, tie-breakers, distribution); P3 statistical rule refined to paired-bootstrap differences; per-factor construct caveats added (factors are NOT renamed but each factor block now states what it actually measures vs what its name might suggest). R4 closure language softened from "no blockers" to "conceptually closed; execution gates remain."
- **v5.1** (2026-04-13 night, small amendment): Reprint Status dropped from the reserve list per user observation that CLS is predominantly an aggregator (≥90% reprinted content) so `is_reprint` has extreme class imbalance and no discriminative signal. P1 noted as "tightly met" with only Tradability Tier remaining as the sole extra-corpus factor in the active shortlist.
- **v5.2** (2026-04-13 night, CMMD + Thales investigation integration): (a) CMMD 6-model fleet recommendation captured (see `docs/CMMD_MODEL_FLEET_SURVEY.md`), with DatedGPT (Yan et al. 2026, 12×1.3B models with strict annual cutoffs 2013-2024) and ChronoBERT/ChronoGPT (He et al. 2025) flagged as research-grade chronologically-controlled baselines for the upcoming R4 literature sweep; (b) Thales signal profile review captured (see `docs/THALES_SIGNAL_PROFILE_REVIEW.md`) — Thales has 13-type EventType taxonomy which is actually FINER than our 7-cat draft, not coarser; Modality 7-enum (CLS-internal) strictly dominates Disclosure Regime; Authority 8-enum (currently CLS-internal in Thales) could become extra-corpus if re-operationalized via publisher metadata lookup; (c) Structured Event Type factor updated with hierarchical labeling note (fine primary + coarse secondary) to satisfy user's desire for finer taxonomy while keeping Stats' power constraints manageable; (d) Modality/Disclosure Regime swap DEFERRED to detailed design session (not applied in v5.2) because pre-commit is still in draft state; (e) Authority factor DEFERRED to Thales dedicated session (per user, CLS raw schema lacks publisher field but Thales has experiment logs for Authority exploration); (f) "Thales dedicated session" added to Open Considerations as a specific future session, distinct from the Thales-joint factor algorithm session — user will curate Thales materials first before this session opens.
- **v5.2.1** (2026-04-13 night, integration review cleanup): applied 10 post-integration-review fixes — P1 prose/audit table sync, Risk R4 bloc 1 sync, "3 reserve + 5 dropped" count fix, Decisions 3/6 canonical-selection wording reconciled with Principle P2, Event Type stopping rule updated for hierarchical labeling, P3 randomized rubric order added, R5 kickoff v5→v5.2 sync, R4 lit sweep kickoff scope boundary clarified, R4 final synthesis stale references fixed.
- **v5.3** (2026-04-13 late night, user clarifications on 5 open questions): (1) R4 literature sweep confirmed as HARD prerequisite to R5; (2) Disclosure Regime confirmed as placeholder (NOT frozen), with known computational difficulty — may be refined or replaced by Modality later; (3) Event Type balance-gating clarified — **coarse 5-7 bins MUST be balanced** (strict), **fine 15-20 primary labels get best-effort minimum balance only if severely imbalanced during sampling** (soft safeguard, not strict gate); (4) CMMD 6-model fleet downgraded from "default starting point" to "strong reference" — R5 agents should explore more freely; (5) **CLS publisher field fact corrected** — the field DOES exist in the raw schema but is incomplete and unreliable (not "does not exist" as v5.2 claimed), so metadata-based Authority is NOT viable but **LLM-based semantic Authority annotation is simple and viable**. This means Authority can be a CLS-internal factor (not extra-corpus), which does NOT restore P1 headroom but IS a cheap addition to the shortlist if desired.
- **v6** (2026-04-14, post-R4 literature sweep Session 1 integration): applied approved edits from `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md`. The sweep (3 fresh-persona Codex calls covering factor provenance, broad 2024-2026 discovery, chronologically-controlled baselines) produced no P0 direct-competitor discoveries; FinMem-Bench novelty claim holds. Novelty distribution across 15 factors: 5 STRONG_PRIOR_ART, 8 PARTIAL_PRIOR_ART, 2 NOVEL (Disclosure Regime — already placeholder — and Session Timing). Cutoff Exposure ±K gray-band confirmed to have no published precedent; labeled as benchmark-specific design choice. v5.2 6-model CMMD fleet stands unchanged; DatedGPT (arxiv 2603.11838) and ChronoBERT/ChronoGPT (arxiv 2502.21206) added as cited methodological precedents. R5 reading queue seeded with 8 new P1 papers from broad sweep. Entity-Anonymization Sensitivity routed to R5 as detector-level stratification field under Principle P5. Coverage Breadth / Media Coverage candidate new factor gated on `docs/MEDIA_COVERAGE_FEASIBILITY.md` (produced in parallel). Sub-tasks D (cited-but-unread) and E (3-bloc construct-collapse validation) deferred to Session 2.
- **v6.1** (2026-04-15, post-R4 literature sweep Session 2 integration — Risk R4 refinement): Session 2 completed Sub-tasks D (cited-but-unread) and E (3-bloc construct-collapse validation). **Key finding**: no published work validates the exact cold-reader 3-bloc decomposition. The construct-validity literature (Cronbach & Meehl 1955, Xiao et al. 2023 EMNLP, Freiesleben 2026 arxiv 2603.15121, Kearns 2026 arxiv 2602.15532, Perlitz et al. 2024 "BenchBench" arxiv 2407.13696, Bean et al. 2025 arxiv 2511.04703) explicitly treats correlation structure as insufficient for construct interpretation. **Risk R4 is refactored**: (a) 3-bloc downgraded from "literature-validated latent structure" to "descriptive working hypothesis"; (b) `Cutoff Exposure` separated as its own Bloc 0 ("temporal exposure") per Glasserman & Lin 2024 and Kong et al. 2026 — refinement from 3-bloc to **4-bloc**; (c) bloc-level summaries framed as descriptive robustness only, not validity proof; (d) prominence bloc internal split caveat added (Entity Salience target vs Tradability Tier); (e) institutional-source bloc interpretation caveat added (correlations may reflect domain structure). Principle P4 gains a framing sentence distinguishing interaction menu from latent-structure validation. Methods-section reviewer-facing language noted for paper writer. Session 2 also surfaced 15 new PDF download candidates (10 from D + 5 from E) handled by a parallel session, plus 2 weak candidate factors (Influence/Relevance, Geographical Proximity) flagged for DROP in the sweep report — user decision on these was pending at v6.1 apply time and is resolved in v6.2 below.
- **v6.2** (2026-04-15, user decisions on Sub-task E candidate queue + Caution Ahead PDF resolved): User-reviewed the 2 weak candidate factors surfaced by Sub-task E. **Decisions**: (1) **Influence / Relevance** added to Reserve list as item 16 (overriding orchestrator drop recommendation) — user reasoning: LLM-agent semantic annotation is cheap (no external data needed, common-sense judgement only), so reserve cost is low and the factor can be re-evaluated after R5 results. (2) **Eliteness** also added to Reserve list as item 17 (newly distinguished from Influence/Relevance per user instruction "影响力和精英性可以看一下") — same low-cost-annotation reasoning. (3) **Geographical Proximity DROPPED** per user reasoning: LLM pretraining corpora are global and English-heavy, so news geographical distance does not straightforwardly translate to training-data frequency differences. Reserve list now has 5 items (was 3). Also resolved: Caution Ahead PDF (Levy 2025, SSRN 5082861) was Cloudflare-blocked for automated fetch in v6.1, now archived from user-supplied PDF in Downloads folder; library entry status updated from MANUAL_REQUIRED to SUCCESS. **Note**: optional Session-3 extensions (CNKI Chinese-academic-index sweep, ChronoGPT-Instruct Chinese smoke test) declined by user as not needed.

---

## R3 outcome summary

4 R3 reviews (Quant/NLP/Stats/Editor) produced a verdict matrix with 4 of 6 open decisions flagged NEEDS-REWORK:

| Decision | Issues raised | User response |
|---|---|---|
| D1 Framing | OK-with-concerns | Confirmed deferral, pre-commit as sufficient risk management |
| D2 Point-in-time fields | **NEEDS-REWORK** (Quant) — baostock 15-min unreliable; missing fields | Deferred to dedicated analysis track |
| D3 Cluster sampling | OK-with-concerns (selection rule too discretionary) | Confirmed direction; selection rule → Thales-joint track |
| D4 Outcome function `O_i(H)` | **NEEDS-REWORK** (Quant) — coupled with D2 | Deferred until D2 resolved |
| D5 Pilot via reprint detection | **NEEDS-REWORK** (NLP + Editor) — text replacement breaks memorization measurement | **Resolved cleanly** — rewritten in v2 |
| D7 Agent-based annotation | **NEEDS-REWORK** (NLP + Editor) — LLM agreement ≠ ground truth | Deferred to dedicated protocol track |

Critical finding from NLP R3 (B1): **memorization detection methods are surface-form sensitive**. Replacing CLS text with public-domain originals for release but using the replacement text for measurement would measure the model's response to text it never saw. The measurement text must be the same text the model most plausibly saw during pretraining.

Critical finding from Quant R3 (B2): baostock's 15-minute CSI 300 historical data is not reliable. The user's implicit "intraday anchoring via baostock" assumption does not hold as specified.

---

## Decisions (v2)

### Decision 1 — Framing is deferred [CONFIRMED]

**Decision (unchanged from v1):** Do not commit to "audit substrate" vs "factor-taxonomy-driven benchmark" framing now. Revisit post-experiment.

**R3 refinement:** Editor asked for a paper shell freeze date; NLP asked for factor provenance fields in the schema. User accepted pre-commit granularity (Decision 9) as sufficient risk management for deferred framing.

**Required for R4:** Factor list output should record, per factor, (a) literature provenance or mechanism-based justification, (b) which framing it supports (substrate, taxonomy, or both).

Paper related-work section must cite MemGuard-Alpha (Roy & Roy 2026), Profit Mirage (Li et al. 2025, arxiv 2510.07920), and Look-Ahead-Bench (Benhenda 2026, arxiv 2601.13770) alongside the DatedGPT/ChronoBERT chronological-control precedents.

**Status:** Confirmed deferred.

---

### Decision 2 — Point-in-time market mechanics fields [DEFERRED TO DEDICATED TRACK]

**v1 direction:** Use akshare + baostock (with 15-min intraday bars); candidate field list.

**R3 finding:** Quant live-probed both sources and found baostock's 15-min CSI 300 data unreliable. Additional critical fields missing (fixed return legs, finer session buckets, identity fields, benchmark_id, corporate actions, survivorship, timestamp_quality_flag).

**User decision (v2):** Defer the full point-in-time schema design to a dedicated analysis session (separate conversation). Record the open problems below; do not force a decision in this document.

**Open problems parked for dedicated track:**
1. Intraday vs daily-close as the primary anchoring strategy (Quant + Stats flagged D2↔D4 coupling)
2. Alternative intraday data source selection (baostock not viable as assumed)
3. Complete field list: `ar_1d/5d/22d`, `c2o`, `o2c`, `o2o_1d/3d`, `timestamp_quality_flag`, session buckets (`pre_open_auction / intraday / close_auction / post_close`), identity fields (`ticker`, `exchange`, `target_scope`), `benchmark_id`, corporate-action flags (split/dividend/rights/rename), survivorship flag
4. CSI 300 vs target-type-specific benchmarks
5. Neutral band formula (horizon-matched, 0.5σ vs regime-adaptive)
6. IPO / insufficient-history rule
7. Rename `confidence` → `label_quality` (Stats suggestion)

**R4 can assume:** outcome computation will eventually produce a verified direction + magnitude + horizon label per case, but specific fields are TBD. Factors must not depend on specific outcome field names.

**Status:** Deferred to dedicated point-in-time analysis track.

---

### Decision 3 — Event-cluster sampling, one case per cluster [CONFIRMED with refinements]

**Decision:** Sampling unit = event cluster, not article. One canonical case per cluster.

**R3 refinements (superseded by Principle P2 in v5.2)**:
- **Canonical selection rule is now fixed by Principle P2** (two-stage Event Phase sampling: random phase assignment → earliest article of that phase within cluster, with full algorithm specified in P2 including no-match handling, tie-breakers, seeds). Earlier drafts said this was deferred to the Thales-joint track; that is **no longer true** as of v5/v5.2. **The Thales-joint session only operationalizes phase labeling rules, tie-breakers, QC, clustering, and entity extraction — it does NOT decide canonical selection**. The canonical-selection rule is a fixed v5.2 commitment.
- **Cluster membership**: the schema will store full cluster member IDs even though only the canonical case is annotated, so downstream frequency analysis can reference it (NLP R3).

**Updated target N (Stats R3 recalc):**
- Previous R2 target: ~1,500 (based on DEFF ≈ 1.5 from within-cluster duplication)
- With true one-per-cluster: DEFF ≈ 1.0–1.1
- **New base target**: ~1,000–1,100 sampled clusters for 80% power on a single clean partition contrast at OR=1.95
- **Scope/loss margin**: 1,300–1,500 justified only as verification-loss buffer
- **Pilot size**: 150 doubly-annotated clusters (up from 50–100 in v1) for bootstrap CI on IAA

**R4 can assume:**
- ~1,000–1,500 curated cases, each is a cluster canonical
- Pilot annotation set = 150 cases, doubly annotated
- Factors will be computed on the canonical text, but cluster-level statistics (size, first-seen time) are available as factor inputs

**Status:** Confirmed direction. **Canonical selection rule is fixed by Principle P2**, NOT deferred to Thales-joint session. The Thales-joint session owns clustering algorithm, entity extraction, and phase-labeling operational details only.

---

### Decision 4 — Verified outcome function `O_i(H)` [DEFERRED WITH D2]

**v1 direction:** Outcome is a function of point-in-time fields, not a frozen label. H=5d primary, CSI 300 benchmark, 0.5σ neutral band.

**R3 finding:** Directly coupled with D2 (B3 hidden-coupling). Stats added missing spec items (exact τ_i, horizon-matched band, target-type benchmark map, IPO rule, rename `confidence`→`label_quality`).

**User decision (v2):** Blocked on D2. Defer together to the dedicated point-in-time analysis track.

**R4 can assume:** Each case will eventually have a triplet `(direction ∈ {up, down, neutral}, magnitude, label_quality)` for each horizon, but exact parameters are TBD. Factors can be defined on `(direction, horizon)` pairs abstractly.

**Status:** Deferred with D2.

---

### Decision 5 — Measurement text vs release text [RESOLVED, REWRITTEN from v1]

**v1 direction (superseded):** Annotate CLS text, detect reprints, replace CLS text with public-domain source for release.

**R3 critical finding (NLP):** If Qwen saw the CLS version during pretraining and we feed the benchmark the SSE announcement version, memorization detectors measure the wrong construct. Surface-form sensitivity is central to Min-K% / MIA / extraction.

**User decision (v2) — CLEAN RESOLUTION:**

1. **Measurement text is always CLS text.** This is the text the target model most plausibly saw during pretraining. All memorization measurements run on CLS text.
2. **`is_reprint` flag** is stored as a stratification field (per Quant's R3 requirement) — boolean plus `reprint_similarity_score` plus `public_source_type` (SSE/SZSE/gov/other-media/none).
3. **Do NOT pre-store the public-domain version** in the main dataset. If a case is flagged `is_reprint = True`, only the flag and source type are stored.
4. **Main experiments run on the CLS corpus.** Full stop.
5. **Public release set is a separate future deliverable.** If/when CLS licensing becomes a blocker for publication, we will construct a SEPARATE public-only set:
   - Pull the original public-domain text from the source at that time (using the stored flag)
   - Re-annotate or partially reuse factor annotations (decided later based on how much is content-independent)
   - Release the public set as its own product
   - Public set and CLS set are **two separate deliverables**, not "CLS set with substituted text"
6. **No claim of "text substitution preserves metrics."** Metrics measured on CLS text are CLS-text metrics; metrics measured on the public set are public-set metrics. They are not comparable without explicit re-measurement.

**Rationale:** This resolves B1 cleanly. It matches the convergent fix from NLP + Editor + Quant R3. It also drops the v1 implicit assumption of licensing-friendly release for MVP — that assumption is replaced by "main experiments are for research; public set is a future deliverable if needed."

**Status:** Resolved. No further discussion needed.

---

### Decision 6 — Event clustering + Thales integration [DEFERRED, with Thales]

**Unchanged from v1 for the clustering/entity extraction parts.** Clustering pipeline + entity extraction will be designed jointly with Thales in a separate session after user prepares Thales materials. **Canonical doc selection rule is NO LONGER in this track** — v5 moved it to Principle P2 as a fixed rule. The Thales-joint session only handles clustering algorithm, entity extraction, phase-labeling classifier rules, and QC.

**R4 can assume:** Clustering produces `duplicate_cluster_id`, `duplicate_cluster_size`, `first_seen_time`, `canonical_doc_id`, and a list of cluster member article IDs. Entity extraction produces `key_entities` per case.

**Status:** Deferred (Thales-joint).

---

### Decision 7 — LLM annotation protocol [DEFERRED TO DEDICATED PROTOCOL TRACK]

**v1 direction:** Claude Code + Codex cross-validation → human review of disagreements → small pilot first.

**R3 finding (NLP + Editor + Stats convergent):** Current workflow is insufficient for EMNLP-level defensibility:
- "Two LLMs agreeing" is triage, not ground truth (shared systematic biases)
- Need human audit of the agreement bucket too (random ~20%)
- Per-field IAA targets: κ ≥ 0.80 (categorical), ICC ≥ 0.75 (continuous), span F1 (entities)
- Few-shot prompts from held-out calibration set, never from production cases
- **Outcome labels must NOT be LLM-annotated** — they are computed mechanically from market data; LLMs only annotate text-grounded factor fields
- Pilot size upgrade: 150 cases (up from 50–100)

**Stats R3 positive finding (must be preserved):** If outcome labels are computed mechanically from market data, and the target model (Qwen) is disjoint from the annotator LLMs (Claude/Codex), the **LLM-annotator endogeneity concern is structurally resolved**. This is the cleanest positive finding from R3.

**User decision (v2):** Defer the full protocol to a dedicated iterative optimization track. The R3 requirements above are recorded as minimum bars that the eventual protocol must meet.

**R4 can assume:**
- Factor fields will be LLM-annotated (Claude + Codex) with human QA
- Outcome labels will be computed mechanically from market data (not LLM-annotated)
- Pilot = 150 doubly-annotated cases with per-field IAA measurement

**Status:** Deferred to dedicated annotation protocol track.

---

### Decision 8 — (Same as Decision 1)

Covered by Decision 1.

---

### Decision 9 — Pre-commit granularity: 档位 2 偏 1 [CONFIRMED]

**Unchanged from v1.** Stats R3 confirmed this will survive reviewer critique IF cutpoints and contrast lists are frozen before any confirmatory detector run.

**Status:** Confirmed.

---

### Decision 10 — Plan B philosophy: factors must have economic / linguistic / statistical meaning [CONFIRMED]

**Unchanged from v1.** R4 agents will be explicitly instructed to justify each candidate factor under this rule.

**Status:** Confirmed. Load-bearing for R4.

---

## Open tracks (deferred, each needs its own session)

These are NOT "problems pushed aside" — each has a dedicated working track. They don't block R4 factor investigation because R4 defines WHAT to measure, while these tracks define HOW to compute or annotate.

| Track | Scope | Depends on | Blocks |
|---|---|---|---|
| **Point-in-time analysis** | D2 fields + D4 outcome function + intraday vs daily-close decision | fresh session | R5/R6 detector choice (partially) |
| **Thales-joint design** | Clustering pipeline + entity extraction + phase labeling rules + QC (canonical SELECTION is already fixed by Principle P2; not in Thales-joint scope) | Thales materials from user | Production annotation start |
| **LLM annotation protocol** | Full workflow spec, prompt design, IAA thresholds, human QA budget (T2) | Pilot data | Production annotation start |

---

## Open items (still not decided)

1. **Timeline commitment**: May 25 vs August 3 ARR. Editor R3 was direct: May 25 is NOT realistic as base plan; only survivable if B1 + paper shell + pilot all freeze by April 19–20. User has NOT yet committed.
2. **Venue-drift check**: Editor + Quant both flagged that the schema direction is tilting quant-flavored, possibly drifting from EMNLP NLP audience toward a finance venue. To be reassessed after R4 factor list is locked.
3. **Paper shell freeze date**: Editor T3 concern. To be decided after R4.

---

## What R4 can assume (frozen inputs for factor investigation)

R4 agents should treat the following as given and NOT relitigate:

1. **Case text for memorization measurement = CLS text.** Not the reprint source, not a paraphrase, not a masked variant. CLS exact tokens.
2. **Sampling unit = event cluster.** Initial target N = 3,200 gross clusters (Stats reference, see `Target N and sampling strategy` section below); ~150 doubly-annotated for the Anchor Strength pilot experiment.
3. **Outcome will produce (direction, magnitude, label_quality) per horizon.** Specific horizons (likely ≥2 of {1d, 5d, 22d}) and exact field names are TBD. Factors should define themselves on abstract `outcome.direction` and `outcome.horizon`.
4. **Cluster metadata available**: `duplicate_cluster_id`, `duplicate_cluster_size`, `first_seen_time`, `canonical_doc_id`, full cluster member list.
5. **Entity extraction available**: `key_entities` per case (from Thales-joint pipeline).
6. **Pre-commit granularity = 档位 2 偏 1**: factor list locked + operationalization function locked + bin-edge RULE locked + bin-edge VALUE computed post-hoc from empirical distribution.
7. **Plan B philosophy**: each factor must justify itself via economic / linguistic / statistical meaning. Vague factors (importance, complexity, memorability, hotness) will be rejected.
8. **Target models for eventual experiments**: Qwen 2.5 7B (white-box via vLLM, logprobs available) primary; DeepSeek (black-box) secondary. Some detectors (Min-K%, MIA) will only run on Qwen.
9. **Framing is deferred**: factors must support both "audit substrate" and "factor-taxonomy-driven" framings.

---

## What R4 produced (post-closure)

R4 ran four sub-rounds in one day: Step 1 brainstorm (4 Codex agents, 30 factor proposals total), Step 1 orchestrator synthesis, Step 2 review of the integrated 12-factor shortlist (4 Codex agents, 10/10/6/2 GO counts), Challenger cross-model check (Claude sub-agent, 3 IMPORTANT amendments), and a cold-reader pass that triggered v5. A post-v5 integration review then drove v5.1 (Reprint Status drop) and v5.2 (CMMD + Thales integration + hierarchical Event Type + per-factor construct caveats). Final outputs:

1. **The 12-factor shortlist** organized by Editor's narrative hierarchy (4 spine + 4 secondary + 2 auxiliary + 1 control + 1 sampling-design factor + **3 reserve items + 5 dropped candidates** after v5.1 Reprint drop). Each spine and secondary factor has a concept definition, a construct caveat (per cold-reader feedback — see "Construct caveats" notes within each factor block), a Decision-10 justification, an operationalization sketch (algorithmic details deferred to Thales-joint session for clustering- and entity-dependent factors), a predicted effect direction, and a hierarchy assignment.
2. **Methodology principles P1-P5** (extra-corpus signal principle, Event Phase two-stage sampling rule, Anchor outcome-blind selection protocol, pre-registered interaction menu framework, R5-vs-R4 boundary).
3. **Convergent risks R1-R4** (shared annotation dependence, major-entity prominence correlation bloc, anchor outcome-blind discipline, construct collapse — R4 added in v5 from cold-reader feedback).
4. **Initial target N = 3,200** gross clusters with stopping-rule adaptive sampling; user has indicated willingness to scale up if balance requirements are not met.
5. **R4 → R5 handoff** with seeded detector candidates (Min-K%, MIA, extraction, SR, FO, FinMem-NoOp, CMMD, contamination, perplexity-based) and 6 explicit open questions for R5 to address.

R4 status: **conceptually closed; execution gates remain** for Thales clustering algorithm, model cutoff metadata, point-in-time field design, and LLM annotation protocol — all routed to dedicated downstream tracks rather than left ambiguous.

---

## R4 scope constraints

**In scope:**
- Factor brainstorming + literature review + new-factor proposals
- Cross-agent debate + Challenger cross-model check
- Operationalization rules for shortlisted factors

**Out of scope:**
- Detector choice (R5)
- Pre-registration wording (R6)
- Clustering implementation (Thales-joint track)
- Annotation protocol details (dedicated track)
- Point-in-time field list (dedicated track)
- Timeline commitment (user decision)

---

## R4 Step 1 + Step 2 outcome: 12-factor shortlist (v3 integration)

R4 Step 1 produced 30 factor proposals (8 Quant + 7 NLP + 9 Stats + 6 Editor). The user integrated these into a 12-factor shortlist draft. R4 Step 2 reviewed the draft with 10/10/6/2 per-agent GO verdicts (Quant/NLP/Stats/Editor). Editor raised 2 factor-level BLOCKs on venue-drift grounds and proposed a narrative hierarchy (spine/secondary/auxiliary) that is compatible with the other 3 agents' positions without changing data collection.

**User accepted** Editor's hierarchy at narrative level. Data collection covers all 12 factors uniformly; narrative structure orders them by centrality.

### Factor hierarchy (user-accepted, narrative-level only)

**Spine (4 factors — main claim)**:
1. **Propagation Intensity** — composite: `log(1+cluster_size) + log(1+prior_family_count_365d)`. Quant's Repetition Load version, rejecting NLP's pure cluster_size. Rationale: single-event burst is shallower than historical template recurrence; the second term is the quantitative dual of Structured Event Type and must be reported jointly with it.
    - **Construct caveat (v5)**: the composite **bundles two distinct constructs**: (a) `cluster_size` measures **same-event burst duplication** (how many CLS articles describe the SAME event), and (b) `prior_family_count_365d` measures **historical template recurrence** (how often events of the same type happen in the prior year). These are not the same thing — the first is a within-event repetition signal, the second is a cross-event template signal. **Both must be stored as separate fields** (`event_burst` and `historical_family_recurrence`), analyzed independently in primary analyses, and only summarized as the composite as a secondary convenience. The "Propagation Intensity" label is retained for organizational brevity but the analysis must respect the two-construct structure.
    - **Literature provenance (v6 addition):** Propagation Intensity has strong direct memorization precedent in duplication/frequency work; Ishihara & Takahashi 2024 (arxiv 2404.17143) provides the strongest non-English news-domain replication and is especially relevant to FinMem-Bench's Chinese CLS setting.
    - **Robustness companion** (v4, post-Challenger): every case also gets a `surface_template_recurrence` score with two variants stored side by side — (a) **cluster-aware variant**: char-5gram TF-IDF cosine similarity vs prior-365-day cluster canonicals, matching Challenger's original proposal; (b) **cluster-free variant**: char-5gram TF-IDF cosine similarity vs ALL prior-365-day CLS articles with no clustering step at all (computed via global inverted index, top-k nearest neighbors, user-proposed extension of Challenger's idea). Primary analysis uses the cluster-aware variant; the cluster-free variant is (i) a fallback if clustering quality proves unstable and (ii) an independent robustness check that directly answers "is the effect an artifact of the clustering pipeline." If both variants agree on the direction of the Propagation Intensity effect, Risk R1 (shared annotation dependence) is substantially mitigated.
2. **Cutoff Exposure** — signed `cutoff_gap_days`, stored continuous. Primary binary split at 0. **Gray band around cutoff (±K days) excluded** to avoid cutoff imprecision contamination. K to be determined empirically from cutoff uncertainty estimates per model.
    - **Construct caveat (v5)**: the operational measurement is **case×model cutoff timing**, not "exposure" in the latent-inclusion-probability sense. Pre-cutoff position is a necessary but not sufficient condition for the model to have been exposed to the article. The factor is reported under the operational name "Cutoff Exposure" for brevity, but the paper's methodology section must explicitly state that what is measured is timing, not actual exposure.
    - **Literature provenance (v6 addition):** The ±K gray-band exclusion is a benchmark-specific design choice to reduce misclassification around uncertain cutoffs. No verified published precedent exists for a symmetric gray-band exclusion zone as a factor-design convention. Document this in the pre-commit as a methodological choice, not a literature-standard convention.
    - **Source class**: case×model (NOT pure case factor) — the value depends on which model is being evaluated.
3. **Anchor Strength** — operationalization TBD via pre-registered comparison experiment, see Principle P3 below for full protocol.
    - **Construct caveat (v5)**: the experiment selects the **most reliable** of three candidate rubrics, not necessarily the one that best measures anchorability in any deep linguistic sense. P3 is a reliability screen with a face-validity sanity check, not a full construct validation study. Reports of Anchor Strength results must include this caveat.
    - **Literature provenance (v6 addition):** No published rubric matches our 3-way pre-registered comparison. Huet et al. 2025 (arxiv 2501.13121) provides the closest structured event representation, but not a benchmark-side scalar anchorability score. The Anchor Strength rubric chosen by P3 is therefore novel as an operational measure and should be described as "adapted from episodic-memory representation work" rather than "derived from prior literature."
4. **Entity Salience** — DUAL field: `(target_salience, max_non_target_entity_salience)`. First tracks direct target prominence (Zipf); second tracks Glasserman & Lin 2024 distraction effect from non-target entities in the same article. Both stored, analyzed jointly with target_scope.
    - **Construct caveat (v5)**: this is a **bundled label for two distinct mechanisms** — target prominence (the target's parametric trace density in CLS) and competing-entity distraction (non-target entities in the article steering the model toward stored priors). The cold reader correctly notes these are not the same thing. They are stored as two separate fields and **must be analyzed and reported as two distinct effects**, not summed into a single "Entity Salience" score. The label "Entity Salience" is retained for organizational brevity, but in the paper they should be referred to by their specific names: `Target Prominence` and `Competing-Entity Prominence`.
    - **Literature provenance (v6 addition):** The target-vs-competing split is directly motivated by Glasserman & Lin 2024 (arxiv 2309.17322), which reports that anonymized headlines outperform originals in-sample, with stronger effects for larger companies — evidence that competing-entity prominence drives distraction independently of target prominence. Nakagawa et al. 2024 (arxiv 2411.00420) and Wu et al. 2025 (arxiv 2511.15364) replicate the anonymization effect in financial sentiment.

**Secondary (4 factors — validation / differentiation)**:
5. **Target Scope** — binary (company vs non-company); stratifier + control, rarely a headline hypothesis
   - **Construct caveat (v5)**: this is a coarse entity-class label, not a memorization mechanism by itself. Its hypothesized effect on memorization runs through prominence, tradability, and disclosure norms (all elsewhere in the shortlist). Treat as stratifier, not as an independent explanatory variable. Bloc 2 (prominence/attention).
6. **Structured Event Type** — Thales-aligned fine-grained taxonomy. User explicitly rejected Stats' 3-category simplification in favor of finer taxonomy; willing to expand dataset N to support it. Coupled with Propagation Intensity's historical term.
   - **v5.2 taxonomy update**: Thales signal profile review (see `docs/THALES_SIGNAL_PROFILE_REVIEW.md`) reveals that Thales already has a 13-type EventType taxonomy (POLICY, ENFORCEMENT, LEGAL, INDICATOR, EARNINGS, CORPORATE, PRODUCT, PERSONNEL, TRADING, OWNERSHIP, INDUSTRY, GEOPOLITICS, OTHER) which is FINER than our 7-cat draft. User notes that Thales's CORPORATE category itself bundles several business templates and was kept coarse in Thales because its small annotation model couldn't handle finer distinctions; FinMem-Bench uses high-capacity agents (Claude + Codex) and can afford to subdivide further. The FinMem-Bench MVP will therefore use a **fine taxonomy (15-20 types, refining Thales's 13 + splitting CORPORATE into sub-templates)** as the **primary label**, with a **coarse secondary label (5-7 types, roughly Thales's high-level groups)** stored alongside. This hierarchical labeling satisfies the user's desire for fine-grained analysis AND Stats' power constraints: primary fine labels are reported descriptively (they are not powered for confirmatory claims at MVP N), secondary coarse labels are reported as confirmatory stratifications (power-safe at 3-5 bins). Exact taxonomy subdivision of CORPORATE and secondary grouping rules are deferred to the Thales dedicated session.
   - **Construct caveat (v5)**: as written, this is a **taxonomy, not a factor with a directional hypothesis**. Different categories may show different memorization profiles, but no a priori prediction of which categories show stronger or weaker memorization exists. Treat as stratifier; report category-by-category effects descriptively, not as a confirmatory main effect. Bloc 3 (institutional stage / source).
7. **Disclosure Regime** — binary (formal disclosure vs commentary/secondary), institutionally-defined not rhetorically
    - **Construct caveat (v5)**: the operational measurement captures **source provenance + institutional writing style**, which overlaps materially with Event Type and Event Phase. Treat as a third bloc-3 (institutional stage / source) variable; do not claim it as independent evidence in joint analyses with Event Type or Event Phase. Bloc 3.
    - **v5.3 status — PLACEHOLDER, NOT FROZEN**: Thales has a richer 7-value `Modality` enum (OFFICIAL_ANNOUNCEMENT / REGULATORY_FILING / DATA_RELEASE / PRESS_RELEASE / ANALYSIS / RUMOR / OTHER) which **strictly dominates** Disclosure Regime's binary split. A potential revision would be to **replace Disclosure Regime with Thales Modality**. The Thales review recommends "refine + reuse": reuse the enum and the CLS marker rules, simplify to single-label primary modality, drop Thales's dense 1-5 scoring. **Per user decision in v5.3**: Disclosure Regime is **explicitly a placeholder, not a frozen factor**. It has known computational difficulty (writing a reliable rule-based classifier over CLS text is non-trivial), and it may be refined or replaced by Modality after the Thales dedicated session has a chance to evaluate annotation feasibility. R5 detector design should treat this factor as "conditional" — detector-factor matchings that depend specifically on Disclosure Regime should also describe how they would work under a Modality replacement.
    - **Literature provenance (v6 addition):** The R4 literature sweep (2026-04-14) found no verified memorization/contamination benchmark that uses formal disclosure vs commentary/secondary coverage as a factor. Adjacent finance literature distinguishes official clarifications, regulatory filings, press releases, rumors, and commentary, but not as a memorization factor. This factor is therefore NOVEL in the memorization benchmark literature and must be justified mechanistically in the paper, not by citation. If retained through R5, its overlap with Modality, Authority, Event Phase, Template Rigidity, and Session Timing must be reported transparently.
8. **Template Rigidity** — char-5gram TF-IDF to cross-cluster nearest neighbors. Pure NLP, no event/entity dependence, fully specifiable now.
    - **Construct caveat (v5)**: the operational measurement is **char-5gram surface similarity to other CLS texts**, NOT "template rigidity" in any deep linguistic sense. The operational name is shorthand for "surface similarity to prior CLS texts." High values may be driven by outlet boilerplate, repeated named entities, or standard finance phrasing — not necessarily by deep template structure. The factor still has memorization signal value (surface reuse → memorization), but its mechanistic interpretation is constrained to surface reuse. Bloc 1 (repetition / surface reuse).
    - **Literature provenance (v6 addition):** Template Rigidity has strong surface-form precedent. Lee et al. 2021 (arxiv 2107.06499), *Deduplicating Training Data Makes Language Models Better*, is the foundational near-duplicate / repetitive-substring paper for this factor's surface-reuse logic.

**Auxiliary / Conditional (2 factors — domain audit, not main claim)**:
9. **Tradability Tier** — ADV20 percentile at `first_seen_time - 1`. **Conditional factor**: defined ONLY for `target_type=company`. Subject is the FORECAST TARGET, not an extracted primary entity from text. Preserves alpha-bridge narrative for Thales downstream; kept out of main claim to prevent EMNLP venue drift.
   - **Construct caveat (v5)**: the path from market tradability to LLM memorization is indirect — it runs through "tradable names get more coverage" → "more coverage means more training-data exposure" → "more exposure means more memorization." Each link is plausible but unproven. Treat as a proxy for prominence, not a direct memorization driver. Bloc 2 (prominence/attention).
10. **Session Timing** — pre_open / intraday / post_close / non_trading_day. CLS timestamps are second-precision so feasible; kept as auxiliary to prevent venue drift.
    - **Construct caveat (v5)**: the mechanism for memorization differences across trading sessions is weak. Session timing clearly matters for markets, but it is NOT yet convincing that it matters for memorization except indirectly through urgency, disclosure regime, or propagation. Treat as exploratory; if it shows an effect, the interpretation is contingent on disentangling from disclosure regime and propagation. Bloc 3 (institutional stage / source).
    - **Literature provenance (v6 addition):** The R4 literature sweep (2026-04-14) found no verified memorization/contamination paper that uses announcement timing as a factor. Finance literature supports DellaVigna & Pollet 2009 style investor-inattention effects at the market level, but not memorization effects at the model level. This factor is therefore NOVEL in the memorization benchmark literature and should be treated as a low-confidence auxiliary with a weak proposed mechanism.

**Control (1 factor)**:
11. **Text Length** — frozen tokenizer token count. Never a primary hypothesis.

**Sampling design factor (overlap with Event Phase sampling rule)**:
12. **Event Phase** — {rumor, official, clarification, recap}. Uses user's two-stage sampling rule: **randomly assign a target phase per cluster, then pick the earliest article of that phase within the cluster**. Replaces the earlier "earliest OR most representative" canonical selection rule. Avoids the degenerate "all canonicals = earliest rumor" problem.
    - **Construct caveat (v5)**: this is partly **a sampling-design choice imposed by the benchmark, not a property measured from the world**. The realized phase distribution is uniform by construction (because of the random assignment), so analyses of "phase effect on memorization" are conditional on the sampling design and cannot be re-weighted to the natural population without additional assumptions. Bloc 3 (institutional stage / source).
    - **Literature provenance (v6 addition):** Finance event-study literature distinguishes rumor / clarification / official-announcement phases, and rumor-detection work treats rumor vs non-rumor as meaningful (Information Transmission Through Rumors in Stock Markets, 2016; M&A rumours in China, 2020). No published work validates event phase as a memorization factor. Treat the direction of any observed phase effect as a first-observation finding, not a replication of a known effect.

### Reserve (5 items)

13. **Exact-Span Rarity** — conditional on large-scale trigram annotation subproject (see below). Pre-committed in the plan but not guaranteed to execute.
14. **Cluster Temporal Span / Repost Persistence** — deferred pending Thales event-annotation decisions. Has standalone value but operationalization depends on the clustering pipeline.
15. **Pre-registered interaction menu** — see Principle P4 below.
16. **Influence / Relevance** (added v6.2, 2026-04-15, from R4 literature sweep Sub-task E candidate-new-factor queue Q3) — news-factor concept for how broadly an event affects the reader/audience's life, decisions, or worldview, distinct from entity fame. Source: Boukes & Vliegenthart 2020 `A general pattern in the construction of economic newsworthiness?` (Sage Journalism, via Sub-task E domain-adjacent search). **Operationalization sketch**: LLM-agent semantic annotation over CLS text using common-sense judgement ("does this event affect a broad audience / narrow audience"). Annotation cost is low because no external data is needed and the judgement is coarse. **Why reserve not active**: heavy conceptual overlap with Tradability Tier, Entity Salience, and the already-queued Coverage Breadth feasibility candidate (Q1); link to memorization mechanism is indirect (influence → coverage volume → training-corpus frequency → memorization). Retain as reserve pending R5 detector results and Coverage Breadth feasibility pilot outcome. **User-approved reserve status 2026-04-15** — do not promote without a mechanism-specific justification that distinguishes it from existing prominence factors.
17. **Eliteness** (added v6.2, 2026-04-15, from R4 literature sweep Sub-task E candidate-new-factor queue Q5) — news-factor concept for semantic/ontological "how high in the institutional hierarchy is the actor/event" (e.g., State Council > central ministry > provincial regulator > listed firm > local enterprise). Distinct from Entity Salience (CLS-frequency Zipfian prominence) and Target Scope (binary company vs non-company). Source: same Boukes & Vliegenthart 2020. **Operationalization sketch**: LLM-agent semantic annotation with an ordinal 4-6 level hierarchy based on actor institutional tier. Annotation cost is low (agent common-sense judgement over article text). **Why reserve not active**: Eliteness is semantically close to Target Scope + Entity Salience + Authority and will likely correlate with several of them; joint-modeling value is uncertain. Retain as reserve pending R5 detector results. **User-approved reserve status 2026-04-15** — promotion decision gated on whether joint modeling with Target Scope / Entity Salience / Authority shows independent signal.

### Dropped in v6.2 (new dropped row after the literature sweep)

- **Geographical Proximity** — surfaced as candidate Q4 in R4 literature sweep Sub-task E from Boukes & Vliegenthart 2020 news-factor theory. **User decision 2026-04-15: DROP**. Reasoning: LLM pretraining corpora are global and English-heavy, so "near / far" news does not straightforwardly translate to training-data frequency differences. Additional reasons: (a) mechanism link to memorization runs purely through language/region pretraining prior, duplicating what Authority and Modality already capture; (b) in CLS (predominantly A-share Chinese telegraph), "proximity" degenerates into "is it mainland China or overseas", which reduces to a Target Scope refinement; (c) no clean ground-truth distance metric; (d) violates Decision 10 Plan B philosophy (vague hotness proxy, no independent economic/linguistic/statistical mechanism).

### Dropped in v5.1

- **Reprint Status** — dropped. Reasoning (user observation, late 2026-04-13): CLS 财联社 is predominantly an aggregator; essentially all CLS content is in some sense reprinted from other sources (public announcements, exchange disclosures, other media). The only CLS-original content is a small subset of market commentary (`盘面点评`). A binary `is_reprint` factor would therefore have extreme class imbalance (>90% positive) and no meaningful discriminative signal — it would degenerate to "looks obviously reprinted vs obscure source" which is annotation noise, not memorization signal. Drop. **P1 implication**: the only pure extra-corpus factor remaining in the shortlist is Tradability Tier (plus Cutoff Exposure which is case×model, not corpus-class). P1 is now at minimum satisfaction.

### v5.2 / v5.3 P1 restoration attempt (DEFERRED)

The Thales review identified **Authority** (8-value ordinal enum: OFFICIAL=6 → SELF_MEDIA=0, UNKNOWN=-1) as a candidate factor that could restore P1 headroom IF re-operationalized as extra-corpus (publisher metadata lookup instead of Thales's text-inference).

**v5.3 fact correction**: the user clarified in v5.3 that the CLS raw schema **DOES contain a publisher / source field**, but the field is **incomplete (missing for many records) and unreliable (correctness is questionable)**. This is different from what v5.2 claimed ("does not have a publisher field"). The practical consequence is the same: metadata-based Authority is NOT viable at production quality because the metadata cannot be trusted.

**BUT** the user also noted that **LLM-based semantic Authority annotation is simple**: an annotation agent can read the CLS article text and infer the original source's authority tier (e.g., from cue phrases like `据新华社` / `证监会宣布` / `根据财经媒体报道`) with good reliability. This is **CLS-internal** (text-inference), not extra-corpus (no external lookup). It therefore does NOT restore P1 extra-corpus headroom, but it DOES make Authority a cheap and feasible addition to the shortlist if desired.

**Status update for v5.3**:
- Authority remains **deferred to the Thales dedicated session** for final go/no-go and operationalization decision
- The Thales review's "do not reuse Thales's text-inference operationalization because it collapses on CLS" caveat may be OVER-conservative given user's clarification that semantic annotation is simple — the Thales dedicated session should re-evaluate this
- **P1 remains at minimum satisfaction** with only Tradability Tier as the pure extra-corpus active factor. Adding Authority as CLS-internal does not change this. Genuine P1 restoration would require either (a) an external knowledge-graph lookup for entity authority, or (b) detector-derived cross-model agreement score in R5, or (c) something surfaced by the R4 literature sweep. All three are deferred.

**What the user has available for the Thales dedicated session**:
- Thales experiment logs under `D:\GitRepos\Thales` (topic classification experiments + signal_profile experiments containing modality and authority exploration)
- Agent-labeled fixture prompts from Thales that can be partially reused for FinMem-Bench annotation

**Resolution for v5.3**: **DO NOT launch a sub-agent to read Thales experiment logs now**. Per user instruction, the Thales materials need curation first, and a **dedicated Thales sync session** is planned for later. When that session opens, a sub-agent can read:
- `D:\GitRepos\Thales\...\experiments\...\topic_classification\*` — for topic taxonomy refinement
- `D:\GitRepos\Thales\...\experiments\...\signal_profile\*` — for Modality + Authority exploration logs
- Thales fixture prompts — for annotation reuse

### Dropped

- **Outcome Label Quality** — not a factor, a sampling filter. Only high-quality cases are sampled.
- **Standardized Surprise Magnitude** — depends on deferred outcome function
- **Outcome Materialization Lag** — depends on deferred outcome function
- **Outcome Horizon** — Editor self-flagged as venue drift, dropped

### Factor literature provenance summary

The R4 literature sweep does NOT support treating the shortlist as uniformly literature-backed. Across the 15 audited active+reserve factors, the distribution is 5 STRONG_PRIOR_ART, 8 PARTIAL_PRIOR_ART, and 2 NOVEL. The two novel factors are `Disclosure Regime` and `Session Timing`. `Cutoff Exposure` has strong precedent, but the `±K` gray-band exclusion is a benchmark-specific design choice with no verified published precedent and should be labeled that way in the paper. The table below reproduces the sweep's per-factor verdict table, including `Modality` and `Authority` as under-investigation additions.

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

---

## Methodology principles (captured from R4 Step 2)

### Principle P1 — Extra-corpus signal principle

CLS-internal statistics (cluster_size, CLS-based entity salience, CLS-based template recurrence) are proxies for CLS corpus properties, NOT LLM training-set properties. The CLS corpus is small relative to any LLM's actual pretraining corpus; distributions in CLS may diverge from distributions in pretraining. Factors that leverage **extra-corpus signals** (market-based liquidity tiers, external knowledge-graph lookups, and — pending Thales sync — publisher-metadata-based authority) have **independent diagnostic value** precisely because they do NOT rely on CLS-internal counts.

**v5.1/v5.2 reality**: Reprint Status was dropped (CLS is aggregator-dominated, no discriminative signal), so the only pure extra-corpus active factor currently in the shortlist is **Tradability Tier**. Authority is a candidate but cannot be extra-corpus without publisher metadata (which the CLS raw schema does not contain). P1 is currently at **minimum satisfaction** and this is acknowledged as a known weakness; the upcoming Thales dedicated sync session and R4 literature sweep may surface a second extra-corpus factor to restore headroom.

**Practical rule**: whenever a factor is proposed, label it as "CLS-internal," "case×model" (depends on model-side metadata), or "extra-corpus" (independent of both CLS and the model). Keep at least 2 extra-corpus factors in the shortlist at all times.

**P1 audit table for the v5 shortlist** (added per cold-reader feedback):

| Factor | Source class | Thales-dependent? | Notes |
|---|---|---|---|
| Propagation Intensity (cluster_size term) | CLS-internal | Yes (clustering) | The dominant term |
| Propagation Intensity (prior_family_count_365d term) | CLS-internal | Yes (event type) | Conditional on event type taxonomy |
| Propagation Intensity (cluster-free robustness companion) | CLS-internal | No | The annotation-free fallback computed via global char-5gram TF-IDF; not extra-corpus but pipeline-independent |
| Cutoff Exposure | **case×model** | No | Requires model cutoff metadata, not CLS metadata; cold-reader correctly notes this is timing not exposure |
| Anchor Strength (final rubric TBD) | CLS-internal | Partial (entity normalization) | Pure text-based once tokenization is fixed |
| Entity Salience — target_salience | CLS-internal | Yes (entity normalization + cluster df) | Captures Zipf in CLS, not in LLM training |
| Entity Salience — competing-entity prominence | CLS-internal | Yes | Same caveat |
| Target Scope | CLS-internal (essentially zero-cost) | No | Determined at sampling time |
| Structured Event Type | CLS-internal (annotated label) | Yes | Inherits Risk R1 |
| Disclosure Regime | CLS-internal (rule-based) | No | Pure rule on text |
| Template Rigidity | CLS-internal | No | Char-5gram TF-IDF, no annotation |
| **Tradability Tier** | **extra-corpus** | No | Market data, independent of CLS |
| Session Timing | CLS-internal (timestamp) | No | Trivial from CLS metadata |
| Event Phase | CLS-internal (rule-based) | Partial | Phase labeling depends on rule quality |
| Text Length | CLS-internal | No | Trivial |

**Extra-corpus count (v5.2 reality)**: **1 pure extra-corpus factor** in the active shortlist (Tradability Tier) + 1 case×model variable (Cutoff Exposure) that is pipeline-independent but model-specific. Reprint Status was dropped in v5.1 as non-discriminative on CLS (see Dropped section below). **Principle P1 is currently tight**: a single extra-corpus factor that is also auxiliary (not in the spine) does not give the benchmark strong headroom against Risk R4 construct collapse. **Possible P1 restorations (all deferred)**: (a) Thales `Authority` re-operationalized via external publisher metadata, blocked by CLS schema lacking a publisher field; (b) R4 literature sweep may surface new extra-corpus candidates; (c) detector-derived CMMD agreement score in R5 could act as a quasi-extra-corpus signal; (d) **Coverage Breadth / Media Coverage** as an extra-corpus factor candidate surfaced by the R4 literature sweep. Finance attention literature (Fang & Peress 2009, Hirshleifer et al. 2023) and recent representation-bias work (Dimino et al. 2025, arxiv 2510.05702) suggest cross-publisher coverage breadth drives visibility effects in LLMs. Operationalization would require an extra-corpus coverage count per event cluster from publishers outside CLS. **Status: queued in the candidate-new-factor list for user decision, not promoted.** Status: acknowledged weakness, not yet repaired.

### Principle P2 — Event Phase two-stage sampling (supersedes prior canonical selection rule)

**This rule is binding and replaces all earlier canonical selection rules** (Decision 3 v1/v2, Decision 6 deferred-to-Thales canonical selection). The Thales-joint algorithm session inherits this rule and only specifies operational details (phase labeling rules, tie-breakers, QC), NOT the rule itself.

**Algorithm (post-cold-reader expansion in v5)**:

1. **Phase distribution**: random phase assignment is **uniform** over the four phases {rumor, official, clarification, recap}, independent of cluster.
2. **Phase labeling**: each article in a cluster receives a phase label from a pre-committed rule-based classifier (specific cue lists per phase, fixed in v5 per Quant R4 Step 1: `公告/披露/回复函/签署/审议通过` → official; `传闻/据悉/市场消息/或将/网传` → rumor; `澄清/辟谣/回应传闻` → clarification; otherwise `recap/follow_up`). Phase labeling happens BEFORE phase assignment.
3. **Within-cluster selection**: for each cluster, after a random phase is assigned, select the article matching the assigned phase with the **earliest publication timestamp**. Tie-break (multiple earliest): longest article first, then deterministic hash-based tiebreaker.
4. **No-match handling**: if the assigned phase has no matching article in the cluster, the cluster is **rejected from the sample**, NOT resampled with a different phase. This makes the realized sample frame "clusters that contain at least one article of the assigned phase," which is a non-uniform restriction over the frame of all clusters. **Selection bias mitigation**: for each rejected cluster, record the assigned phase, the cluster size, and the available phases. This metadata is published in the benchmark documentation so users can reweight if needed.
5. **Phase availability and cluster characteristics**: phase availability is correlated with cluster size (larger clusters have more diverse phase coverage). This means the realized sample over-represents large clusters slightly. **Mitigation**: report the realized sample's cluster size distribution alongside the gross cluster population's distribution; if needed, apply inverse-propensity weights when computing population-level statistics.
6. **Ambiguous articles**: articles matching multiple phase cues (e.g., a clarification that also contains official disclosure language) are labeled as the **first matching cue from a fixed precedence order**: clarification > official > rumor > recap (because a clarification of an existing rumor is the most informative phase to surface). This precedence is locked ex ante.
7. **Random seed**: the random phase assignment uses a fixed seed published in the benchmark release notes, so the sample is reproducible.
8. **Audit fields per case**: assigned_phase, available_phases_in_cluster, selected_article_id, selection_reason (= 'P2 earliest-of-phase'), labeling_confidence (from the rule-based classifier).

**Known limitations of P2** (acknowledged in pre-commit):
- Rule-based phase labeling will mislabel some articles (especially boundary cases). Phase label confidence is stored per case.
- The realized sample is NOT a uniform sample over all clusters; it is a uniform sample over (cluster × assigned_phase) crossed with availability. Statistical analyses must respect this.
- Smaller clusters with rare phase combinations contribute less, biasing the sample toward larger / more-diverse clusters.

**This rule fully specifies canonical selection for the MVP.** Decision 3 and Decision 6 are formally superseded by P2 for the canonical selection question; they remain in force only for their other content (event clustering algorithm details and Thales integration scope).

### Principle P3 — Anchor Strength outcome-blind selection (v4 revised)

Anchor Strength operationalization is decided via a pre-registered comparison experiment on 150 CLS cases (revised up from 50 in v3 — see Challenger Challenge 4):

**Sampling**: 150 CLS cases via stratified random over (pre/post cutoff × target type × text length tertile × propagation × event type).

**Annotators**: 3 independent raters — 2 model families (Claude, Codex) + 1 human — each applying ALL 3 rubrics (Quant density count / NLP triple specificity / Editor 0-3 rubric) to ALL 150 cases. Total = 450 annotations per rubric = 1,350 annotations.

**Randomized rubric order within each rater**: for each case, the order in which the 3 rubrics are applied is randomized per (rater × case) with a fixed seed. This prevents systematic carryover effects (e.g., a rater subconsciously anchoring later rubrics to their first rubric's score). The randomization order is published with the release so reviewers can verify.

**Primary reliability metric**: **ordinal Krippendorff's α** (see Concept Definitions below) computed per rubric, with **95% bootstrap confidence intervals** from 2,000 resamples. At n=150, the bootstrap CI half-width is expected to be approximately ±0.05 (compared to ±0.10 at n=50, which was too wide to support the decision rule).

**Auxiliary metrics**: quadratic-weighted Cohen's κ; Spearman correlation vs 3-rater consensus; annotation time per case.

**Face validity audit**: separate from the 150 main cases, 10 manually-curated "obvious high-anchor" cases (specific entity + specific date + specific discrete event) and 10 "obvious low-anchor" cases (vague commentary, no specific event) are scored by each rubric. Face validity = fraction of correct high-vs-low orderings.

**Decision rule** (locked in writing BEFORE the experiment runs, v5 refined per cold-reader Edit 9):

1. Compute each rubric's α and its 95% bootstrap CI from 2,000 bootstrap resamples.
2. **Compute paired-bootstrap differences** for each pair of rubrics: on each of the 2,000 bootstrap draws, compute α_A − α_B for the SAME resampled cases, building a distribution of paired differences. Take the 95% CI of the paired difference. This is statistically tighter than comparing two independent CIs because it accounts for the correlation across rubrics on shared cases.
3. **Decision**:
   - If a rubric has the highest α AND its paired-bootstrap difference vs both other rubrics has a 95% CI that excludes zero → that rubric is the primary.
   - **Escape hatch — if no rubric clearly dominates** (any paired-difference 95% CI includes zero): the 3 rubrics are statistically indistinguishable. Primary rubric defaults to **Editor's 0-3 count rubric** (simplest by definition complexity, and the choice is mechanical / cannot be retroactively rationalized). The other two rubrics are retained as robustness checks: each case is scored by all 3, primary analysis runs on the chosen primary, sensitivity analyses run on the other two.
4. Face validity is used **only** as a tiebreaker when the paired-bootstrap rule produces two co-leaders (both have CIs excluding zero against the third but not against each other). In that narrow window, the rubric with higher face-validity hit rate wins.

**Statistical caveat** (added v5 per cold-reader concern about over-claiming): the paired-bootstrap procedure is a **reliability screen**, not a construct validity proof. High α (or robust α-difference) means raters agree, not that the rubric measures anchorability correctly. The face validity audit (10 + 10 hand-curated obvious cases) is a thin construct validity layer; it is not a substitute for a full construct validation study. The rubric chosen by P3 is the **most reliable** of the three candidates; its construct validity is supported by face validity but not proven. The benchmark documentation must state this caveat explicitly when reporting Anchor Strength results.

**One-rater limitation**: the experiment includes 2 model raters + 1 human rater. The cold reader correctly notes that 1 human is thin if the experiment is meant to support construct validity claims. **Resolution**: P3 is explicitly labeled as a reliability screen, not a construct validity study. If construct validation is needed, R5 / R6 may add a follow-up multi-human-rater study; that is parked, not committed.

**Critical constraint**: the 150-case experiment must run BEFORE any memorization detector is executed on any CLS data. The rubric is chosen on agreement / validity metrics ONLY, never on what rubric produces "better" memorization effects. Violating this converts the selection into p-hacking.

**Release artifact**: all 150 main cases + 20 face-validity cases + 3-rubric scores from all 3 raters are released with the benchmark for independent verification.

**Concept definitions (for reviewers unfamiliar with the statistics)**:
- **Krippendorff's α** — a generalization of Cohen's κ that supports any number of raters, any measurement level (we use ordinal), and missing data. α = 1 means perfect inter-rater agreement; α ≥ 0.80 is "good reliability"; α in [0.67, 0.80] is "tentatively useful"; α < 0.67 is "unreliable." The ordinal variant uses ordered category distances, appropriate for 0-3 scales.
- **Bootstrap 95% confidence interval** — a resampling method for estimating uncertainty when analytical CIs do not exist. We repeatedly sample 150 cases with replacement, compute α on each resample, and take the 2.5% / 97.5% quantiles as the CI. At n=150, the typical half-width for a moderate-α rubric is ≈ 0.05.
- **Face validity** — a non-statistical sanity check: does the rubric correctly order cases that are *obviously* high-anchor vs obviously low-anchor? Needed as a complement to α because three raters can be consistently wrong in the same direction (high α, low validity).
- **Escape hatch** — methodology term for "what happens when the primary rule does not produce a unique answer." Our escape hatch (default to simplest rubric) is a fully mechanical fallback that does not require looking at the results.

### Principle P4 — Pre-registered interaction menu (user's Idea 4, Stats-REVISED form, Challenger-expanded)

The pre-registration includes a fixed menu of **5-7 2×2 interaction pairs** between DIFFERENT factors. v4 final menu (locked after Challenger, subject to minor R6 adjustment):
- `cutoff × propagation_intensity`
- `cutoff × anchor_strength`
- `entity_salience × tradability_tier` (within company subset)
- `disclosure_regime × event_type`
- `template_rigidity × exact_span_rarity` (if rarity subproject runs)
- **`template_rigidity × cutoff_exposure`** [v4, cross-agent NLP × Editor] — tests whether templated text memorization decays differently across the cutoff boundary than free-form text. If templated text shows smaller pre/post separation, it suggests the "memorization" of templated text is time-invariant structural priors rather than event-specific recall.
- **`target_salience × propagation_intensity | target_salience = low`** [v4, cross-agent NLP × Quant, **tail-entity diagnostic**] — tests the central correlation-bloc question: on the low-target-salience subset (tail entities that are NOT major listed firms), does Propagation Intensity still produce a memorization effect? If YES, Propagation is a genuine repetition-exposure driver independent of prominence; if NO, Propagation is likely a proxy for target-entity fame. This is a directed test that can falsify the "Propagation = prominence proxy" hypothesis and directly mitigates Risk R2 (major-entity prominence correlation bloc).

**P4 is NOT a latent-structure validation device**; it is a pre-registered heterogeneity menu. Latent-structure checks (bloc-level summaries, factor-independence tests) are reported separately under Risk R4's mitigation framework. Interaction pairs are prioritized when they help separate plausible latent blocs — especially temporal-vs-prominence and repetition-vs-prominence confounds. If a pre-registered interaction is motivated by bloc-separation rather than substantive moderation, the paper labels it a **diagnostic interaction** and interprets null/non-null results accordingly.

**Rules governing the menu**:
1. **Menu is locked ex ante**; no additions after data is seen
2. **Only cross-factor pairs** (no self-interactions)
3. **Analyzed freely without confirmatory alpha consumption** — these are pre-registered exploratory, not primary confirmatory
4. **All menu items MUST be reported in the paper**, even if null. Reporting depth can vary:
   - Strong effects: detailed analysis in results section
   - Weak / null effects: 1-sentence summary in a results table, nothing dropped
   - **Selective reporting of menu items triggers p-hacking suspicion; rule: if it's on the menu, it appears in the paper**
5. Any interaction found during analysis that is NOT on the menu is **post-hoc exploratory**, labeled as such, and goes in a clearly-marked exploratory section

This framework protects against selective reporting while preserving the user's desired flexibility to freely analyze pre-committed combinations.

**Methodological precedent (v6 addition):** This interaction-menu framework is closest to multiverse/specification-curve analysis for pre-committed exploratory analysis; see Ecker et al. 2023, *One Model Many Scores: Using Multiverse Analysis to Prevent Fairness Hacking and Evaluate the Influence of Model Design Decisions* (arxiv 2308.16681).

### Principle P5 — Detector-dependent factors are R5 territory

Factors coupled to specific detection methods (text reversibility for counterfactual probes, extractable span density for extraction attacks, logprob tail length for Min-K%, token-level perplexity variance for MIA) are NOT decided in R4. They co-emerge in R5 when the detector shortlist is finalized. Each detector may contribute its own 1-2 stratification fields.

---

## R4 Step 2 convergent risks (captured for pre-commit documentation)

### Risk R1 — Shared annotation dependence creates false convergence

4 factors depend on the same event/entity annotation backbone: **Structured Event Type, Propagation Intensity's historical term, Event Phase, Disclosure Regime**. If the upstream annotation has systematic bias, all 4 factors inherit it, creating the illusion of "multi-factor evidence convergence" when it is actually one bias counted 4 times.

**Mitigation (captured from Quant + NLP)**:
- Pre-commit publishes a **dependency graph** distinguishing primitive annotations from derived factors
- **Event Type ontology frozen BEFORE any historical frequency calculation**
- Sensitivity analyses must show primary findings hold under alternative event-type taxonomies or with event-type annotations replaced by cluster-free alternatives
- No single "multi-factor replication" claim without the dependency graph being transparent

### Risk R2 — "Major-entity prominence" correlation bloc

`Target Scope`, `Target Salience`, `Tradability Tier` all load on the latent variable "prominence of large listed firms." They look like three independent factors but project the same underlying signal.

Secondary concerns: Propagation × Template Rigidity (both measure repetition-like signals); Disclosure Regime × Structured Event Type (both categorical text labels with non-random joint distribution).

**Mitigation (captured from Stats)**:
- **No mechanical orthogonalization** (distorts interpretation)
- **Joint modeling** in the analysis — never an independent univariate claim for any factor in the bloc
- Pre-commit explicitly labels the bloc as a correlation hazard
- Interpretation of any single-factor result within the bloc is conditional on the others being held fixed

### Risk R3 — Anchor operationalization must be outcome-blind

Addressed by Principle P3. Duplicated here because it is the cleanest potential p-hacking channel in R4.

### Risk R4 — Construct collapse into a prominence/repetition proxy benchmark (added v5)

The 12-factor shortlist may project onto a smaller number of latent constructs. The current three-bloc map is a **descriptive working hypothesis introduced by the cold reader's review, NOT a literature-validated latent structure**. The R4 literature sweep (Sub-task E, 2026-04-15) searched for published empirical validation of similar decompositions in financial NLP, memorization benchmarks, and general LLM benchmark factor analysis, and found none. Adjacent literatures (Burnell et al. 2023 arxiv 2306.10062, Petrova & Burden 2026 arxiv 2602.20813, Kearns 2026 arxiv 2602.15532) provide alternative decompositions (3-factor with different content, 1-factor collapse, structured capabilities model) but none validate our specific repetition/prominence/institutional-stage story. **Published construct-validity work in LLM evaluation (Cronbach & Meehl 1955, Xiao et al. 2023 EMNLP, Freiesleben 2026 arxiv 2603.15121) explicitly treats correlation structure as suggestive but insufficient evidence for construct interpretation on its own.**

Note for paper writer:
Methods section should include a sentence along the lines of: "Following construct-validity guidance from Cronbach & Meehl (1955) and recent LLM benchmark methodology (Xiao et al. 2023 EMNLP, Freiesleben 2026), we treat factor correlations as **evidence to be explained**, not as self-interpreting proof of a latent structure. Accordingly, FinMem-Bench reports theory-led per-factor results, bloc-level descriptive summaries, and alternative decomposition stress tests, while avoiding claims that the 4-bloc structure has itself been empirically validated in prior literature."

0. **Temporal exposure / cutoff overlap** (added v6.1): Cutoff Exposure. Separated from the other three blocs because (a) it is case×model not pure case; (b) finance-LLM validity literature explicitly treats look-ahead bias as distinct from prominence/distraction/source mechanisms (Glasserman & Lin 2024 arxiv 2309.17322, Kong et al. 2026 arxiv 2602.14233); (c) the current 3-bloc decomposition already implicitly leaves Cutoff Exposure outside — this edit makes that separation explicit.
1. **Repetition / surface reuse**: Propagation Intensity (event_burst + historical_family_recurrence terms), Template Rigidity, surface_template_recurrence robustness companion (cluster-aware and cluster-free variants)
2. **Prominence / attention**: Entity Salience (target part), Target Scope, Tradability Tier
   - **Internal split caveat**: `Entity Salience (target part)` and `Tradability Tier` should not be assumed to measure the same prominence subconstruct even if they correlate. The economic-news literature (Boukes & Vliegenthart 2020) separates `eliteness` from `influence/relevance`. Joint modeling should allow these to load on distinct latent factors unless the data rules it out.
3. **Institutional stage / source provenance**: Structured Event Type, Disclosure Regime, Event Phase, Session Timing
   - **Source-bloc interpretation caveat**: correlations among `Structured Event Type`, `Disclosure Regime`, `Event Phase`, and `Session Timing` should be interpreted cautiously because in financial news they may reflect **genuine domain structure and newsroom routines** (news production, outlet ecology, regulatory timing) rather than redundant measurement of one latent variable. Boukes & Vliegenthart 2020 treat `continuity`, `eliteness`, `influence/relevance`, and outlet-type differences as partly distinct.

If the eventual analysis "shows" memorization is stronger for high-propagation, salient, tradable, templated cases and presents this as **converging multi-factor evidence**, the conclusion may be substantively wrong: those four factors all manifest the same latent construct (high-profile, repeatedly-worded coverage of major firms). The benchmark could end up validating sensitivity to **prominence + boilerplate + corpus reuse** rather than memorization per se. This produces a clean-looking story that is wrong.

**Mitigation**:
- **Joint modeling mandate**: never report independent univariate effects for any factor in the same latent bloc; always condition on bloc-mates
- **Tail-entity diagnostic** (interaction menu pair `target_salience × propagation_intensity | target_salience=low`): directly tests whether Propagation Intensity has any effect on the low-prominence subset. If yes, repetition is a genuine driver independent of prominence; if no, the bloc is one variable
- **Cluster-free robustness companion** to Propagation Intensity: independent of clustering pipeline AND of prominence (it's pure char-5gram surface reuse)
- **Construct caveats per factor block**: each factor block now states what the operational measurement actually captures vs what the operational name might suggest, making the bloc structure visible to readers
- **Pre-commit explicitly labels the 3 latent blocs as a known confound**, so reviewers see the team confronted the issue rather than discovered it post-hoc
- **Bloc-level summaries are secondary DESCRIPTIVE robustness analyses only.** They are reported to show whether coarse latent-structure summaries explain per-factor patterns, NOT to establish construct validity by themselves. Alternative decompositions are stress-tested alongside the primary 4-bloc summary: at minimum a one-factor collapse check (following Petrova & Burden 2026's finding that apparent category diversity can collapse to a single general factor) and a temporal-split four-bloc check. **Construct-validity interpretation rests on theory-led mechanism claims, convergent/divergent diagnostics per MTMM-style checks (Xiao et al. 2023 EMNLP), and negative-control checks — not on correlation structure alone.**
  (Perlitz et al. 2024 "BenchBench" arxiv 2407.13696 shows that within-benchmark agreement is method-sensitive; high factor correlation in FinMem should not be treated as self-validating evidence of latent collapse.)

---

## Target N and sampling strategy

**Initial target N = 3,200 gross clusters** (Stats-computed reference), ≈ 2,560 scorable after 20% verification loss. This is an ESTIMATE, not a hard requirement.

**Real sampling rule (user-directed)**: design stopping conditions on a set of balance requirements; sample adaptively until stopping conditions are met.

**Stopping conditions (captured from Stats + user)**:
- All confirmatory binary factor minority shares ≥ 25%
- Company share ≥ 70% (for Tradability subset)
- Tradability binary minority within company subset ≥ 25%
- Event Phase all 4 types have ≥ 200 cases each (for two-stage sampling to work)
- Event Type: **coarse confirmatory groups (5-7 bins, the secondary label layer) MUST meet minimum cell count per group** (strict balance-gate; to be set in R6); **fine primary labels (15-20 bins, after Thales 13-type subdivision) are descriptive by default and NOT strictly balance-gated**, BUT per v5.3 user clarification: **if during sampling a fine primary label is found to be severely imbalanced (e.g., some labels under ~20 cases), a best-effort minimum balance safeguard kicks in** (continue sampling with a bias toward under-represented fine labels until they reach a floor count). This is a soft safeguard, not a hard gate — it reduces pathological sparsity without blocking data collection.

If stopping conditions are not met at N=3,200, sampling continues. N may scale up to 3,500-4,500 in practice; user has indicated willingness to purchase additional annotation capacity.

**Optional scale-up trigger**: if Tradability Tier is promoted from auxiliary to confirmatory (a framing-level decision), initial target scales to 3,500. Currently Tradability is auxiliary per Editor's hierarchy.

---

## Decisions locked in v3 (new)

| Decision | Content | Status |
|---|---|---|
| D11 — Factor hierarchy | Editor's spine/secondary/auxiliary structure adopted at narrative level | Locked |
| D12 — Target N reference | 3,200 gross initial, stopping-rule driven thereafter | Locked |
| D13 — Interaction menu | Pre-registered 5-7 cross-factor 2×2 pairs (v5: menu expanded with 2 cross-agent pairs in v4); all reported; non-menu interactions are post-hoc | Locked |
| D14 — Anchor outcome-blind selection | 150-case experiment (v5: upgraded from 50 in v3) with locked decision rule, paired-bootstrap α comparison, escape hatch defaulting to Editor 0-3 rubric, run before outcome data | Locked |
| D15 — Extra-corpus signal principle | Mandatory principle: ≥ 2 extra-corpus factors at all times | Locked |

---

## Still open (to R5 / R6 / dedicated tracks)

- Detector list (R5)
- Pre-registration specific wording (R6)
- Exact factor algorithm specifications for clustering-dependent and entity-dependent factors (Thales-joint session)
- Point-in-time market mechanics fields (dedicated track)
- LLM annotation protocol (dedicated track)
- Timeline commitment (user decision — Editor's R4 Step 2 estimate is June-July 2026 internal draft / July-August 2026 submission / August 3 ARR realistic; May 25 ARR is NOT realistic)
- Exact-Span Rarity subproject go/no-go decision

---

## R4 Challenger outcome (v4)

The R4 Challenger (Claude cross-model check after 4 Codex agents) returned **no BLOCKING issues**. Verdict: the 12-factor shortlist with Editor's hierarchy is robust enough to close R4. 3 IMPORTANT findings were raised, all addressed in v4:

1. **Risk R1 mitigation was weaker than advertised** → v4 adds the dual robustness companion (cluster-aware + cluster-free `surface_template_recurrence`) to Propagation Intensity. The cluster-free variant is annotation-free in a stronger sense than Challenger's original proposal — it is computed via a global char-5gram TF-IDF index over the prior-365-day CLS corpus with NO clustering step at all, making it independent of both event-type annotation AND the clustering pipeline.

2. **Anchor 50-case experiment had insufficient statistical power** → v4 upgrades Principle P3 to n=150, adds an explicit bootstrap CI reporting requirement, and adds an escape hatch (default to Editor 0-3 rubric if α differences are within the noise band).

3. **Interaction menu was populated from same-agent pairs** → v4 adds two cross-agent pairs to Principle P4: `template_rigidity × cutoff_exposure` (NLP × Editor, time-decay of templated memorization) and `target_salience × propagation_intensity | target_salience=low` (NLP × Quant, tail-entity diagnostic that can directly falsify "Propagation is a prominence proxy").

Challenger also raised MINOR findings that are parked in the "Open considerations for downstream tracks" section below.

Full Challenger report at `refine-logs/reviews/BENCHMARK_R4_CHALLENGER.md`.

---

## Open considerations for downstream tracks

Items flagged during R4 as important but not resolvable within R4 scope. Each is routed to the correct downstream track rather than deferred indefinitely.

### Spine factor dependency on Thales-joint pipeline

Four spine / secondary factors (Propagation Intensity, Entity Salience, Target Scope, Structured Event Type) depend on the deferred Thales-joint clustering + entity extraction pipeline. R5 detector investigation should explicitly acknowledge this upstream dependency when selecting detectors — some detector families (Min-K% / MIA) can run on raw CLS text alone, while others (those that need frequency features computed per event family) cannot run until the Thales track produces cluster IDs and event type labels.

**Handoff note for R5**: mark each detector as (a) usable on raw CLS text immediately, (b) requires Thales pipeline outputs, or (c) can run degraded without Thales but gains from it. This determines R5 execution sequencing.

### Chinese-specific data quality flags (Thales-joint algorithm session)

Challenger Challenge 6 flagged 5 Chinese-NLP-specific issues that the 4 Codex agents (primarily trained on English literature) may have under-weighted:
1. **Simplified vs traditional variation** — same event reported in HK / Taiwan / mainland with different character encodings
2. **Regional newsroom style** — 财联社 vs 21 世纪经济报道 vs 每经 have different disclosure vocabularies and surface forms
3. **Regulator language conventions** — 证监会 / 银保监会 / 人民银行 / 发改委 use distinct formal-disclosure dialects
4. **Segmentation instability** — impacts any token-level factor (Locator Specificity, Exact-Span Rarity, Template Rigidity's char-5gram TF-IDF is robust here; others are not)
5. **Entity alias normalization** — 中信证券 / 中信 / 600030 / 中信证券股份有限公司 must map to one canonical ID
6. **Unit suffix rarity artifact** — `亿`, `万`, `千万` can inflate n-gram rarity spuriously in Exact-Span Rarity factor

**Handoff**: the Thales-joint factor-algorithm session will dedicate one sub-section to "Chinese-specific data quality flags," spec out detection + normalization rules, and produce a schema of QC fields to accompany each case.

### Cognitive-science ad-hoc consultation (parked)

Challenger Challenge 7 noted that the 4 Codex agents anchor primarily to the English memorization-benchmark literature (Kandpal, Carlini, Lee, Chang, Dated Data, AntiLeakBench) and do not draw on cognitive-science frameworks for episodic vs semantic vs procedural memory.

**Decision**: do NOT add a permanent 5th agent for cognitive science. The cognitive-memory framework (Tulving et al.) is more useful at the **post-experiment interpretation** stage than at the **factor-design** stage — the relevant question is "given the effects we observed, which cognitive-memory framework best explains them?", not "which factor should we measure?"

**Parked action**: after R5 completes and pilot experiments produce their first results, trigger a **one-shot ad-hoc cognitive-science consultation** (either a Codex call with strong role setting, or an independent Claude agent) whose input is (a) the pilot results, (b) `related papers/notes/memory_cognitive.md` contents, and (c) the Tulving / Memory GAPS / Tulving Test papers already in the library. Output is a 1-2 page interpretation memo that can feed into the paper's Discussion section.

### MemGuard-Alpha (Roy & Roy 2026) as direct prior art

`related papers/MemGuard-Alpha Memorization Financial Forecasting.pdf` (arxiv 2603.26797, Mar 2026) is the closest prior art to FinMem-Bench identified during R4. It proposes a two-stage filter (MCS combining 5 MIA methods with temporal proximity features + CMMD = Cross-Model Memorization Disagreement) and reports a 7× return gap between memorization-flagged "tainted" and "clean" LLM forecasting signals on S&P 100 constituents over Jan 2019 - Jun 2024. **Implications captured separately in R5 handoff notes**; the key one for this decision document is that FinMem-Bench should position itself as a **substrate benchmark on which methods like MemGuard-Alpha can be evaluated**, not as a competing method. MemGuard-Alpha is English / S&P 100; FinMem-Bench is Chinese / CLS — the cross-lingual gap is a novelty claim. MemGuard-Alpha's temporal proximity features directly validate the Cutoff Exposure spine factor; its 5-MIA-method ensemble is a strong hint for the R5 detector shortlist.

### Thales dedicated sync session (added v5.2)

A **separate future session** (distinct from the Thales-joint factor algorithm session and distinct from the Thales-joint clustering session) will handle direct synchronization with the Thales project:

**Scope**:
- Read Thales experiment logs for topic classification, modality, and authority exploration (paths under `D:\GitRepos\Thales\...\experiments\...`)
- Evaluate reuse of Thales agent-labeled fixture prompts for FinMem-Bench annotation
- Decide: (a) fine-grained subdivision of Thales's 13-type EventType (especially CORPORATE) for FinMem-Bench's higher-capacity annotation regime, (b) Modality vs Disclosure Regime swap decision, (c) Authority operationalization decision (given CLS schema lacks publisher field), (d) fixture prompt reuse extent
- Produce a written integration spec that feeds into R6 pre-registration and the Thales-joint factor algorithm session

**Prerequisite**: user will curate Thales materials (clean up, organize, point to relevant files) before this session opens. **Do NOT launch sub-agents against `D:\GitRepos\Thales` until the user signals readiness.**

### CMMD model fleet (R5 input from v5.2)

The R5 Cross-Model Memorization Disagreement detector requires a multi-model fleet with genuine cutoff diversity and Chinese capability. A dedicated survey (`docs/CMMD_MODEL_FLEET_SURVEY.md`) produced the following recommendation:

**Recommended fleet (6 models, 21-month cutoff span 2023-10 → 2025-07)**:
1. Qwen 2.5-7B-Instruct (local, cutoff 2023-10, white-box)
2. DeepSeek-V2.5 (OpenRouter, cutoff ~2024-03, black-box)
3. GLM-4-9B-0414 (local, cutoff 2024-06-30 — ONLY officially-documented cutoff, white-box)
4. DeepSeek-V3 `deepseek-chat-v3-0324` (OpenRouter, cutoff 2024-07, black-box)
5. Qwen3-14B (local, cutoff 2025-01, white-box)
6. Claude Sonnet 4.5 `claude-sonnet-4-5-20250929` (OpenRouter, cutoff 2025-01 reliable / 2025-07 extended, black-box, non-Chinese-vendor diversity)

**Critical landmine**: silent model updates under the same slug are the biggest reproducibility hazard. Pre-commit MUST pin to dated checkpoints (`-0324`, `-20250929`, HF commit SHAs) and lock OpenRouter provider routing.

**Cost**: ~$6 API + 8 GPU-hours at 3,200 cases × 6 models = 19,200 calls (Claude dominates at ~$5.76; 3 local white-box models are effectively free).

**Research-grade chronologically-controlled precedents (v6 update post-R4 literature sweep):**
- **DatedGPT** (Yan et al. 2026, arxiv 2603.11838): 12 × 1.3B annual-cutoff 2013-2024. **Not yet downloadable** (weights pending paper acceptance per author page). **English-only** — no Chinese training data reported. Verdict: METHOD_ONLY, cite prominently in methods section, do not enter fleet.
- **ChronoBERT / ChronoGPT / ChronoGPT-Instruct** (He et al. 2025, arxiv 2502.21206): public HF releases at `manelalab/chrono-*-v1-20241231` with verified commit SHAs. **English-only** per every verified model card. Verdict: METHOD_ONLY. Optional: Chinese smoke test on `chrono-gpt-instruct-v1-20241231` to confirm Chinese-capability concern.
- **Time Machine GPT** (Guo et al. 2024, arxiv 2404.18543, NAACL Findings): public HF (`Ti-Ma/TiMaGPT2-*`), 2011-2022, GPT-2 small, English-only. METHOD_ONLY, too early for CLS-era.
- Additional chronologically-controlled families discovered by the sweep but not relevant to CLS era: **StoriesLM** (1900-1963), **NoLBERT** (arxiv 2509.01110, 1976-1995, introduces the "lookaback bias" concept). Both METHOD_ONLY.
- **PiT-Inference** — vendor claim, no reproducible public release. REJECT.
- **"Bendemra 2024 Frontier Models"** — probably a citation error (confused with Benhenda's Look-Ahead-Bench). Do not cite as a separate model family.
- **FINSABER** (arxiv 2505.07078, KDD 2026): benchmarking framework, not a model. Cite as methodological precedent for PiT benchmark design.

**Fleet verdict:** the v5.2 6-model fleet should stand unchanged. No chronologically-controlled family clears all four fleet-add gates (downloadable + nonredundant cutoff in [2023-10, 2025-07] + usable Chinese capability + compute-fit).

**Fleet status (v5.3 update)**: the 6-model recommendation is a **strong reference for R5**, NOT a default starting point. Per user's v5.3 clarification, R5 agents should have freedom to explore model candidates more broadly — the fleet survey is one input among several, and the R4 literature sweep may surface additional chronologically-controlled candidates (DatedGPT, ChronoBERT/ChronoGPT, Time Machine GPT) that change the optimal fleet composition. R5 Step 2 or equivalent freezes the final fleet.

### GSM-Symbolic (Mirzadeh et al. 2024) as methodological precedent for counterfactual probes

`related papers/GSM-Symbolic Understanding Reasoning Limits.pdf` (arxiv 2410.05229) is not about finance or memorization directly, but provides a top-venue methodological precedent for **surface-invariant controlled perturbation as a memorization-vs-reasoning diagnostic**. GSM-Symbolic parameterizes GSM8K problems so surface tokens (names, numbers, entities) can be swapped while keeping logical structure fixed, then measures accuracy variance across equivalent instantiations. The **GSM-NoOp** variant adds one irrelevant-but-plausible clause and observes accuracy drops up to 65%. **Implication for R5**: this directly legitimizes our counterfactual / semantic-reversal / evidence-intrusion probe family — we can cite GSM-Symbolic as ACL-family precedent for "controlled perturbation reveals pattern-matching behind apparent reasoning," which is the same construct we test with SR/FO probes. Also suggests adding a **distractor-clause variant** (a CLS article with an inserted plausible-but-irrelevant sentence about an unrelated ticker) as a candidate R5 probe type, analogous to GSM-NoOp.

### R5 reading queue (new P1 papers from R4 literature sweep)

Sub-task B surfaced 8 new P1 papers that should be read before R5 detector decisions:

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

### Detector-level stratification fields seeded by the R4 literature sweep

NoLBERT (arxiv 2509.01110) is METHOD_ONLY for the CMMD fleet, but it introduces the "lookaback bias" concept. R5 should consider whether detector coverage needs to measure both look-ahead memorization and memorization of pre-cutoff content, rather than treating chronology only as a future-knowledge leakage problem.

- **Detector-level stratification field — Entity-Anonymization Sensitivity.** Magnitude of a detector's score change when entity names in the measurement text are replaced by anonymous placeholders. Direct literature support: Glasserman & Lin 2024 (arxiv 2309.17322, anonymized-headlines distraction effect), Nakagawa et al. 2024 (arxiv 2411.00420, company-specific bias in financial sentiment), Wu et al. 2025 (arxiv 2511.15364, anonymization information-loss tradeoff). This is a **detector-level probe** analogous to the counterfactual detector's "反事实显著程度" — the stratum is a property of how the detector responds, not a property of the article text. R5 Step 1 should evaluate whether to include it as a seeded detector-level stratification field and, if yes, which detector families it applies to (Min-K%, MIA, CMMD, SR/FO counterfactual probes, FinMem-NoOp).
