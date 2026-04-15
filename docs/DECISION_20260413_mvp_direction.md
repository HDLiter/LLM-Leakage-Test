# DECISION: FinMem-Bench MVP Direction (v5.2)

**Date:** 2026-04-13
**Version:** 5.2 (post-R4 cold-reader review + Reprint drop + Thales/CMMD investigation integration)
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

**R3 refinements:**
- **Canonical selection rule** is deferred to the **Thales-joint track** (T1). v1 said "annotator picks earliest OR most representative with reasoning"; NLP + Stats both flagged this as too discretionary. The Thales project has parallel canonical-selection + entity-extraction needs, so this will be designed jointly.
- **Placeholder selection rule for R4 purposes only**: assume a deterministic rule will exist (most likely `earliest article in cluster`, with tie-breakers on length and source authority). R4 factors should not depend on the exact rule.
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

**Status:** Confirmed direction. Selection rule → Thales-joint track.

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

**Unchanged from v1.** Clustering pipeline + entity extraction will be designed jointly with Thales in a separate session after user prepares Thales materials. Canonical doc selection rule (T1 from R3) joins this track.

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
| **Thales-joint design** | Clustering pipeline + entity extraction + canonical doc selection rule (T1) | Thales materials from user | Production annotation start |
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

R4 ran four sub-rounds in one day: Step 1 brainstorm (4 Codex agents, 30 factor proposals total), Step 1 orchestrator synthesis, Step 2 review of the integrated 12-factor shortlist (4 Codex agents, 10/10/6/2 GO counts), Challenger cross-model check (Claude sub-agent, 3 IMPORTANT amendments), and a cold-reader pass that triggered v5. Final outputs:

1. **The 12-factor shortlist** organized by Editor's narrative hierarchy (4 spine + 4 secondary + 2 auxiliary + 1 control + 1 sampling-design factor + 4 reserve items + 4 dropped candidates). Each spine and secondary factor has a concept definition, a construct caveat (per cold-reader feedback — see "Construct caveats" notes within each factor block), a Decision-10 justification, an operationalization sketch (algorithmic details deferred to Thales-joint session for clustering- and entity-dependent factors), a predicted effect direction, and a hierarchy assignment.
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
   - **Robustness companion** (v4, post-Challenger): every case also gets a `surface_template_recurrence` score with two variants stored side by side — (a) **cluster-aware variant**: char-5gram TF-IDF cosine similarity vs prior-365-day cluster canonicals, matching Challenger's original proposal; (b) **cluster-free variant**: char-5gram TF-IDF cosine similarity vs ALL prior-365-day CLS articles with no clustering step at all (computed via global inverted index, top-k nearest neighbors, user-proposed extension of Challenger's idea). Primary analysis uses the cluster-aware variant; the cluster-free variant is (i) a fallback if clustering quality proves unstable and (ii) an independent robustness check that directly answers "is the effect an artifact of the clustering pipeline." If both variants agree on the direction of the Propagation Intensity effect, Risk R1 (shared annotation dependence) is substantially mitigated.
2. **Cutoff Exposure** — signed `cutoff_gap_days`, stored continuous. Primary binary split at 0. **Gray band around cutoff (±K days) excluded** to avoid cutoff imprecision contamination. K to be determined empirically from cutoff uncertainty estimates per model.
   - **Construct caveat (v5)**: the operational measurement is **case×model cutoff timing**, not "exposure" in the latent-inclusion-probability sense. Pre-cutoff position is a necessary but not sufficient condition for the model to have been exposed to the article. The factor is reported under the operational name "Cutoff Exposure" for brevity, but the paper's methodology section must explicitly state that what is measured is timing, not actual exposure.
   - **Source class**: case×model (NOT pure case factor) — the value depends on which model is being evaluated.
3. **Anchor Strength** — operationalization TBD via pre-registered comparison experiment, see Principle P3 below for full protocol.
   - **Construct caveat (v5)**: the experiment selects the **most reliable** of three candidate rubrics, not necessarily the one that best measures anchorability in any deep linguistic sense. P3 is a reliability screen with a face-validity sanity check, not a full construct validation study. Reports of Anchor Strength results must include this caveat.
4. **Entity Salience** — DUAL field: `(target_salience, max_non_target_entity_salience)`. First tracks direct target prominence (Zipf); second tracks Glasserman & Lin 2024 distraction effect from non-target entities in the same article. Both stored, analyzed jointly with target_scope.
   - **Construct caveat (v5)**: this is a **bundled label for two distinct mechanisms** — target prominence (the target's parametric trace density in CLS) and competing-entity distraction (non-target entities in the article steering the model toward stored priors). The cold reader correctly notes these are not the same thing. They are stored as two separate fields and **must be analyzed and reported as two distinct effects**, not summed into a single "Entity Salience" score. The label "Entity Salience" is retained for organizational brevity, but in the paper they should be referred to by their specific names: `Target Prominence` and `Competing-Entity Prominence`.

**Secondary (4 factors — validation / differentiation)**:
5. **Target Scope** — binary (company vs non-company); stratifier + control, rarely a headline hypothesis
   - **Construct caveat (v5)**: this is a coarse entity-class label, not a memorization mechanism by itself. Its hypothesized effect on memorization runs through prominence, tradability, and disclosure norms (all elsewhere in the shortlist). Treat as stratifier, not as an independent explanatory variable. Bloc 2 (prominence/attention).
6. **Structured Event Type** — Thales-aligned fine-grained taxonomy. User explicitly rejected Stats' 3-category simplification in favor of finer taxonomy; willing to expand dataset N to support it. Coupled with Propagation Intensity's historical term.
   - **v5.2 taxonomy update**: Thales signal profile review (see `docs/THALES_SIGNAL_PROFILE_REVIEW.md`) reveals that Thales already has a 13-type EventType taxonomy (POLICY, ENFORCEMENT, LEGAL, INDICATOR, EARNINGS, CORPORATE, PRODUCT, PERSONNEL, TRADING, OWNERSHIP, INDUSTRY, GEOPOLITICS, OTHER) which is FINER than our 7-cat draft. User notes that Thales's CORPORATE category itself bundles several business templates and was kept coarse in Thales because its small annotation model couldn't handle finer distinctions; FinMem-Bench uses high-capacity agents (Claude + Codex) and can afford to subdivide further. The FinMem-Bench MVP will therefore use a **fine taxonomy (15-20 types, refining Thales's 13 + splitting CORPORATE into sub-templates)** as the **primary label**, with a **coarse secondary label (5-7 types, roughly Thales's high-level groups)** stored alongside. This hierarchical labeling satisfies the user's desire for fine-grained analysis AND Stats' power constraints: primary fine labels are reported descriptively (they are not powered for confirmatory claims at MVP N), secondary coarse labels are reported as confirmatory stratifications (power-safe at 3-5 bins). Exact taxonomy subdivision of CORPORATE and secondary grouping rules are deferred to the Thales dedicated session.
   - **Construct caveat (v5)**: as written, this is a **taxonomy, not a factor with a directional hypothesis**. Different categories may show different memorization profiles, but no a priori prediction of which categories show stronger or weaker memorization exists. Treat as stratifier; report category-by-category effects descriptively, not as a confirmatory main effect. Bloc 3 (institutional stage / source).
7. **Disclosure Regime** — binary (formal disclosure vs commentary/secondary), institutionally-defined not rhetorically
   - **Construct caveat (v5)**: the operational measurement captures **source provenance + institutional writing style**, which overlaps materially with Event Type and Event Phase. Treat as a third bloc-3 (institutional stage / source) variable; do not claim it as independent evidence in joint analyses with Event Type or Event Phase. Bloc 3.
   - **v5.2 open question**: Thales has a richer 7-value `Modality` enum (OFFICIAL_ANNOUNCEMENT / REGULATORY_FILING / DATA_RELEASE / PRESS_RELEASE / ANALYSIS / RUMOR / OTHER) which **strictly dominates** Disclosure Regime's binary split. A potential revision would be to **replace Disclosure Regime with Thales Modality**. The Thales review recommends "refine + reuse": reuse the enum and the CLS marker rules, simplify to single-label primary modality, drop Thales's dense 1-5 scoring. **Deferral**: this swap is NOT applied in v5.2. Pre-commit is still in draft state; the swap will be re-evaluated in the Thales dedicated session + detailed design session along with data availability, computational difficulty, and annotation accuracy concerns. For now, the MVP factor list retains Disclosure Regime as a placeholder.
8. **Template Rigidity** — char-5gram TF-IDF to cross-cluster nearest neighbors. Pure NLP, no event/entity dependence, fully specifiable now.
   - **Construct caveat (v5)**: the operational measurement is **char-5gram surface similarity to other CLS texts**, NOT "template rigidity" in any deep linguistic sense. The operational name is shorthand for "surface similarity to prior CLS texts." High values may be driven by outlet boilerplate, repeated named entities, or standard finance phrasing — not necessarily by deep template structure. The factor still has memorization signal value (surface reuse → memorization), but its mechanistic interpretation is constrained to surface reuse. Bloc 1 (repetition / surface reuse).

**Auxiliary / Conditional (2 factors — domain audit, not main claim)**:
9. **Tradability Tier** — ADV20 percentile at `first_seen_time - 1`. **Conditional factor**: defined ONLY for `target_type=company`. Subject is the FORECAST TARGET, not an extracted primary entity from text. Preserves alpha-bridge narrative for Thales downstream; kept out of main claim to prevent EMNLP venue drift.
   - **Construct caveat (v5)**: the path from market tradability to LLM memorization is indirect — it runs through "tradable names get more coverage" → "more coverage means more training-data exposure" → "more exposure means more memorization." Each link is plausible but unproven. Treat as a proxy for prominence, not a direct memorization driver. Bloc 2 (prominence/attention).
10. **Session Timing** — pre_open / intraday / post_close / non_trading_day. CLS timestamps are second-precision so feasible; kept as auxiliary to prevent venue drift.
    - **Construct caveat (v5)**: the mechanism for memorization differences across trading sessions is weak. Session timing clearly matters for markets, but it is NOT yet convincing that it matters for memorization except indirectly through urgency, disclosure regime, or propagation. Treat as exploratory; if it shows an effect, the interpretation is contingent on disentangling from disclosure regime and propagation. Bloc 3 (institutional stage / source).

**Control (1 factor)**:
11. **Text Length** — frozen tokenizer token count. Never a primary hypothesis.

**Sampling design factor (overlap with Event Phase sampling rule)**:
12. **Event Phase** — {rumor, official, clarification, recap}. Uses user's two-stage sampling rule: **randomly assign a target phase per cluster, then pick the earliest article of that phase within the cluster**. Replaces the earlier "earliest OR most representative" canonical selection rule. Avoids the degenerate "all canonicals = earliest rumor" problem.
    - **Construct caveat (v5)**: this is partly **a sampling-design choice imposed by the benchmark, not a property measured from the world**. The realized phase distribution is uniform by construction (because of the random assignment), so analyses of "phase effect on memorization" are conditional on the sampling design and cannot be re-weighted to the natural population without additional assumptions. Bloc 3 (institutional stage / source).

### Reserve (3 items)

13. **Exact-Span Rarity** — conditional on large-scale trigram annotation subproject (see below). Pre-committed in the plan but not guaranteed to execute.
14. **Cluster Temporal Span / Repost Persistence** — deferred pending Thales event-annotation decisions. Has standalone value but operationalization depends on the clustering pipeline.
15. **Pre-registered interaction menu** — see Principle P4 below.

### Dropped in v5.1

- **Reprint Status** — dropped. Reasoning (user observation, late 2026-04-13): CLS 财联社 is predominantly an aggregator; essentially all CLS content is in some sense reprinted from other sources (public announcements, exchange disclosures, other media). The only CLS-original content is a small subset of market commentary (`盘面点评`). A binary `is_reprint` factor would therefore have extreme class imbalance (>90% positive) and no meaningful discriminative signal — it would degenerate to "looks obviously reprinted vs obscure source" which is annotation noise, not memorization signal. Drop. **P1 implication**: the only pure extra-corpus factor remaining in the shortlist is Tradability Tier (plus Cutoff Exposure which is case×model, not corpus-class). P1 is now at minimum satisfaction.

### v5.2 P1 restoration attempt (DEFERRED)

The Thales review identified **Authority** (8-value ordinal enum: OFFICIAL=6 → SELF_MEDIA=0, UNKNOWN=-1) as a candidate factor that could restore P1 headroom IF re-operationalized as extra-corpus (publisher metadata lookup instead of Thales's text-inference).

**Blocker**: the user confirms that the **CLS raw schema does NOT have a publisher / source field** (the required metadata is not present, or schema is incomplete). This was already explored in Thales experiments and is a known fact.

**What the user has available**:
- Thales experiment logs under `D:\GitRepos\Thales` (topic classification experiments + signal_profile experiments containing modality and authority exploration)
- Agent-labeled fixture prompts from Thales that can be partially reused for FinMem-Bench annotation

**Resolution for v5.2**: **DO NOT launch a sub-agent to read Thales experiment logs now**. Per user instruction, the Thales materials need curation first, and a **dedicated Thales sync session** is planned for later. When that session opens, a sub-agent can read:
- `D:\GitRepos\Thales\...\experiments\...\topic_classification\*` — for topic taxonomy refinement
- `D:\GitRepos\Thales\...\experiments\...\signal_profile\*` — for Modality + Authority exploration logs
- Thales fixture prompts — for annotation reuse

Until then, **P1 remains tightly met with only Tradability Tier as the pure extra-corpus factor in the active shortlist**. This is acknowledged as a known weakness, not silently glossed. Authority factor addition is deferred to the Thales dedicated session.

### Dropped

- **Outcome Label Quality** — not a factor, a sampling filter. Only high-quality cases are sampled.
- **Standardized Surprise Magnitude** — depends on deferred outcome function
- **Outcome Materialization Lag** — depends on deferred outcome function
- **Outcome Horizon** — Editor self-flagged as venue drift, dropped

---

## Methodology principles (captured from R4 Step 2)

### Principle P1 — Extra-corpus signal principle

CLS-internal statistics (cluster_size, CLS-based entity salience, CLS-based reprint rate) are proxies for CLS corpus properties, NOT LLM training-set properties. The CLS corpus is small relative to any LLM's actual pretraining corpus; distributions in CLS may diverge from distributions in pretraining. Factors that leverage **extra-corpus signals** (market-based Tradability, multi-media Reprint coverage as proxy for external dissemination, historical event-family frequency) have **independent diagnostic value** precisely because they do NOT rely on CLS-internal counts.

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
| Reprint Status (reserve) | **extra-corpus** | No | Whether the article matches a public-domain source — independent of CLS |

**Extra-corpus count**: 2 in the active shortlist (Tradability Tier + Reprint Status if promoted from reserve) + 1 case×model variable (Cutoff Exposure) that is also pipeline-independent. **Principle P1 is minimally satisfied** but tightly. If Reprint Status is not promoted, only Tradability Tier remains as a pure extra-corpus factor — and Tradability is auxiliary in the hierarchy. **R5 should consider promoting at least one detector-derived signal that is also pipeline-independent** to give P1 more headroom.

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

The cold reader's biggest single-risk finding. The 12-factor shortlist looks broad but actually collapses into **3 latent constructs**, not 12:

1. **Repetition / surface reuse**: Propagation Intensity, Template Rigidity, Reprint Status, surface_template_recurrence robustness companion
2. **Prominence / attention**: Entity Salience (target part), Target Scope, Tradability Tier
3. **Institutional stage / source provenance**: Structured Event Type, Disclosure Regime, Event Phase, Session Timing

If the eventual analysis "shows" memorization is stronger for high-propagation, salient, tradable, templated cases and presents this as **converging multi-factor evidence**, the conclusion may be substantively wrong: those four factors all manifest the same latent construct (high-profile, repeatedly-worded coverage of major firms). The benchmark could end up validating sensitivity to **prominence + boilerplate + corpus reuse** rather than memorization per se. This produces a clean-looking story that is wrong.

**Mitigation**:
- **Joint modeling mandate**: never report independent univariate effects for any factor in the same latent bloc; always condition on bloc-mates
- **Tail-entity diagnostic** (interaction menu pair `target_salience × propagation_intensity | target_salience=low`): directly tests whether Propagation Intensity has any effect on the low-prominence subset. If yes, repetition is a genuine driver independent of prominence; if no, the bloc is one variable
- **Cluster-free robustness companion** to Propagation Intensity: independent of clustering pipeline AND of prominence (it's pure char-5gram surface reuse)
- **Construct caveats per factor block**: each factor block now states what the operational measurement actually captures vs what the operational name might suggest, making the bloc structure visible to readers
- **Pre-commit explicitly labels the 3 latent blocs as a known confound**, so reviewers see the team confronted the issue rather than discovered it post-hoc
- **Bloc-level summary as a secondary analysis**: in the paper, report bloc-level effects (averaged or PCA'd within bloc) alongside per-factor effects, so readers can see whether the bloc story explains the factor stories

---

## Target N and sampling strategy

**Initial target N = 3,200 gross clusters** (Stats-computed reference), ≈ 2,560 scorable after 20% verification loss. This is an ESTIMATE, not a hard requirement.

**Real sampling rule (user-directed)**: design stopping conditions on a set of balance requirements; sample adaptively until stopping conditions are met.

**Stopping conditions (captured from Stats + user)**:
- All confirmatory binary factor minority shares ≥ 25%
- Company share ≥ 70% (for Tradability subset)
- Tradability binary minority within company subset ≥ 25%
- Event Phase all 4 types have ≥ 200 cases each (for two-stage sampling to work)
- Event Type: each of the 7+ categories has ≥ minimum cell (to be set in R6)

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

**Research-grade chronologically-controlled alternatives to investigate in R4 literature sweep**:
- **DatedGPT** (Yan et al. 2026, `related papers/DatedGPT Preventing Lookahead Bias.pdf`): **family of 12 × 1.3B-parameter models trained from scratch on ~100B tokens with strict annual cutoffs spanning 2013-2024**. This is the single strongest chronologically-controlled baseline in the memorization literature because it controls model architecture and training algorithm exactly while varying only the temporal cutoff year by year. **Drawback**: 1.3B is small, Chinese capability uncertain, accessibility uncertain.
- **ChronoBERT / ChronoGPT** (He et al. 2025, `related papers/Chronologically Consistent Large Language Models.pdf`): also trained only on text available at each point in time; different architecture family from DatedGPT. Same drawbacks re: scale and Chinese capability.
- **Action**: the R4 literature sweep (see `refine-logs/reviews/BENCHMARK_R4_LIT_SWEEP_KICKOFF.md`) should specifically investigate these two papers for (a) whether the models are publicly downloadable, (b) whether they handle Chinese financial news at usable quality, (c) whether they should enter the CMMD fleet as a "controlled baseline" 7th/8th member. Even if they cannot enter the fleet operationally, their methodology supports FinMem-Bench's CMMD narrative.

**Fleet status**: the 6-model recommendation is accepted as the v5.2 reference fleet. It is NOT yet frozen into R5 pre-commit because R5 hasn't started. Final freezing happens in R5 Step 2 or equivalent.

### GSM-Symbolic (Mirzadeh et al. 2024) as methodological precedent for counterfactual probes

`related papers/GSM-Symbolic Understanding Reasoning Limits.pdf` (arxiv 2410.05229) is not about finance or memorization directly, but provides a top-venue methodological precedent for **surface-invariant controlled perturbation as a memorization-vs-reasoning diagnostic**. GSM-Symbolic parameterizes GSM8K problems so surface tokens (names, numbers, entities) can be swapped while keeping logical structure fixed, then measures accuracy variance across equivalent instantiations. The **GSM-NoOp** variant adds one irrelevant-but-plausible clause and observes accuracy drops up to 65%. **Implication for R5**: this directly legitimizes our counterfactual / semantic-reversal / evidence-intrusion probe family — we can cite GSM-Symbolic as ACL-family precedent for "controlled perturbation reveals pattern-matching behind apparent reasoning," which is the same construct we test with SR/FO probes. Also suggests adding a **distractor-clause variant** (a CLS article with an inserted plausible-but-irrelevant sentence about an unrelated ticker) as a candidate R5 probe type, analogous to GSM-NoOp.
