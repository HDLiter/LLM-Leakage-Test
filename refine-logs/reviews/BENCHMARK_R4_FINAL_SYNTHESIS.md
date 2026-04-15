# BENCHMARK R4 Final Synthesis — Factor Investigation Closure

**Date:** 2026-04-13 (R4 opened and closed within one day)
**Orchestrator:** Claude Code
**Scope:** R4 = factor investigation (what dimensions to measure per case, with what operationalization and what statistical structure)
**Output:** this synthesis + `docs/DECISION_20260413_mvp_direction.md` v4 + BENCHMARK_R4A/R4B/R4_CHALLENGER review files

---

## R4 process summary

R4 ran as four sequential sub-rounds over one day:

| Sub-round | Participants | Purpose | Output files |
|---|---|---|---|
| **R4 Step 1** (brainstorm) | 4 Codex domain agents (Quant / NLP / Stats / Editor), parallel, no cross-visibility | Independently propose candidate factors from each lens | BENCHMARK_R4A_{QUANT,NLP,STATS,EDITOR}.md |
| **R4 Step 1 synthesis** | Orchestrator | Aggregate the 30 proposed factors into a convergence map, identify divergences | BENCHMARK_R4A_SYNTHESIS.md |
| **R4 Step 2** (review) | 4 Codex domain agents, independent reviews of the 12-factor shortlist the user integrated from Step 1 | Evaluate the integrated draft, respond to user methodology inputs, answer detail questions | BENCHMARK_R4B_{QUANT,NLP,STATS,EDITOR}.md |
| **R4 Challenger** | Claude cross-model sub-agent (non-Codex, for model-family diversity) | Surface blind spots shared across the 4 Codex agents | BENCHMARK_R4_CHALLENGER.md |
| **User integration** | User + Orchestrator | Fold R4 Step 2 and Challenger findings into decisions, update decision document to v4 | `docs/DECISION_20260413_mvp_direction.md` v4 |

Total factor proposals generated: 30 (Step 1) → reviewed and integrated into a 12-factor shortlist (Step 2) → refined by 3 Challenger-addressed amendments → final v4.

---

## Convergence and divergence across 4 rounds (R1 → R4)

R4 sits at the end of a 4-round escalation from "this proposal has 3 papers stapled together" (R1 Editor) through "MVP pivot is the right move" (R2 consensus) through "R3 decision check — 3 critical blockers" (all resolved or routed) to "R4 factor investigation closes with no blockers." Convergence arc:

| Round | Central question | Convergence level |
|---|---|---|
| R1 | Is the original benchmark proposal defensible as-is? | No. 4 different verdict severities. |
| R2 | Is the narrower MVP pivot defensible? | Yes, unanimous GO with conditions. |
| R3 | Are the specific MVP decisions operationally sound? | 4 of 6 open decisions needed rework; B1/B2/B3 critical; all resolved or routed. |
| R4 Step 1 | What factors should the benchmark measure? | Brainstorm only, no convergence requirement. |
| R4 Step 2 | Does the integrated 12-factor shortlist hold up? | 10/10/6/2 GO counts (Quant/NLP/Stats/Editor); Editor raised 2 venue-drift blocks that user accepted as narrative-hierarchy reshuffle rather than factor removal. |
| R4 Challenger | Any shared blind spots across 4 Codex agents? | No BLOCKING issues; 3 IMPORTANT amendments applied to v4. |

**Net**: from a fractured R1 to a converged R4, without loss of project ambition. The 12-factor shortlist preserves Quant's alpha-bridge (via the auxiliary tier), NLP's literature-backed factors (as the spine), Stats' power discipline (via Editor's hierarchy + expanded N + principles P3/P4), and Editor's venue discipline (via the spine/secondary/auxiliary structure). All four agents have substantive representation in the final shortlist.

---

## R4 final outputs (by reference to v4)

R4 produces **no new content beyond what is captured in `docs/DECISION_20260413_mvp_direction.md` v4**. The decision doc is the authoritative artifact; this synthesis is an index into it. The v4 sections that R4 is responsible for:

1. **§ "R4 Step 1 + Step 2 outcome: 12-factor shortlist"** — the 12 factors organized by Editor's hierarchy: 4 spine + 4 secondary + 2 auxiliary + 1 control + 1 sampling-design factor (Event Phase), plus 4 reserve items and 4 dropped items.

2. **§ "Methodology principles (captured from R4 Step 2)"** — principles P1 through P5:
   - **P1** Extra-corpus signal principle (at least 2 extra-corpus factors always in the shortlist)
   - **P2** Event Phase two-stage sampling (replaces canonical selection rule)
   - **P3** Anchor Strength outcome-blind experiment, n=150, with bootstrap CI reporting and escape hatch
   - **P4** Pre-registered interaction menu, 5-7 cross-factor 2×2 pairs, including 2 cross-agent pairs added in v4
   - **P5** Detector-dependent factors are R5 territory

3. **§ "R4 Step 2 convergent risks (captured for pre-commit documentation)"** — risks R1/R2/R3:
   - **R1** Shared annotation dependence across 4 factors; mitigated by the v4 dual robustness companion on Propagation Intensity (cluster-aware + cluster-free variants)
   - **R2** Major-entity prominence correlation bloc; mitigated by joint modeling mandate and the v4 tail-entity diagnostic interaction pair
   - **R3** Anchor outcome-blind discipline; mitigated by Principle P3

4. **§ "Target N and sampling strategy"** — initial target N = 3,200 gross clusters, with explicit stopping conditions for adaptive resampling. User will scale up if balance requirements are not met.

5. **§ "R4 Challenger outcome (v4)"** — 3 IMPORTANT findings from the cross-model check, all addressed.

6. **§ "Open considerations for downstream tracks"** — items routed to dedicated downstream sessions rather than deferred indefinitely:
   - Spine factor dependency on the Thales-joint pipeline (handoff note for R5)
   - Chinese-specific data quality flags (for the Thales-joint algorithm session)
   - Cognitive-science ad-hoc consultation (parked until post-pilot interpretation)
   - MemGuard-Alpha (Roy & Roy 2026) as direct prior art (substrate framing + CMMD technique + cutoff exposure validation)
   - GSM-Symbolic (Mirzadeh et al. 2024) as methodological precedent for counterfactual probes (legitimizes SR/FO family, suggests FinMem-NoOp probe variant)

---

## What is new in R4 relative to prior rounds

R4 contributed these items that did not exist in R1-R3:

### New factor definitions (12, integrated from 30 brainstorm proposals)
- Propagation Intensity as a composite (cluster_size + prior_family_count_365d), with a dual robustness companion (cluster-aware + cluster-free surface_template_recurrence)
- Cutoff Exposure with an explicit gray-band exclusion zone
- Anchor Strength as a to-be-chosen rubric via pre-registered outcome-blind experiment (not a single fixed operationalization)
- Entity Salience as a dual field (target_salience + max_non_target_entity_salience)
- Target Scope as an explicit narrative stratifier
- Tradability Tier as a company-subset-conditional factor
- Structured Event Type as a Thales-aligned fine-grained taxonomy (not the 3-class Stats compression)
- Disclosure Regime as institutionally-defined, distinct from Structured Event Type
- Template Rigidity as char-5gram TF-IDF nearest-neighbor similarity
- Event Phase with two-stage random-type-then-earliest sampling
- Session Timing with explicit trading-session buckets
- Text Length as a mandatory control

### New methodology principles (5, none existed before R4)
- **P1** Extra-corpus signal principle emerged from a R4 Step 2 meta-insight that CLS-internal statistics are proxies for CLS properties, not LLM-training-set properties. This is a new design philosophy that influences every future factor proposal.
- **P2** Two-stage random-type-then-earliest sampling replaces the earlier discretionary canonical-selection rule. It is simultaneously a sampling strategy and the operationalization of Event Phase.
- **P3** Outcome-blind rubric selection via pre-registered experiment with bootstrap CI reporting and mechanical escape hatch. This is a new construct-validity safeguard.
- **P4** Pre-registered interaction menu framework — resolves the tension between Stats' strict "no confirmatory alpha on interactions" and the user's desire for combinatorial analysis. Compromise allows freely-analyzable but pre-committed interactions outside the confirmatory family.
- **P5** Detector-dependent factors are R5 territory. Sets boundary for R4 and R5.

### New narrative structure (Editor's hierarchy)
The spine / secondary / auxiliary / control / reserve structure is new in R4. It was Editor's response to the 12-factor shortlist and was accepted by the user as narrative-level (not data-collection-level) organization. This structure solves the alpha-bridge vs venue-drift tension without removing any factor.

### New prior art identifications (2 papers added to library)
- **MemGuard-Alpha (Roy & Roy 2026)** — arxiv 2603.26797 — closest direct competitor to FinMem-Bench. Positions our benchmark as a substrate for methods like theirs. Introduces CMMD (Cross-Model Memorization Disagreement) as a detector technique we had not considered.
- **GSM-Symbolic (Mirzadeh et al. 2024)** — arxiv 2410.05229 — top-venue methodological precedent for surface-invariant controlled perturbation as a memorization-vs-reasoning diagnostic. Legitimizes our counterfactual probe family and suggests a FinMem-NoOp variant analogous to GSM-NoOp.

### New N estimate and sampling strategy
- Initial target N upgraded from 1,500 (R3) to 3,200 (R4 Step 2 Stats recalc). This reflects (a) the user's decision to expand the factor list from 4 confirmatory to 6-7 confirmatory, (b) the user's willingness to purchase additional annotation capacity, and (c) conditional factor overhead from Tradability being company-only.
- Sampling strategy is now stopping-rule driven rather than fixed-N. User will adaptively resample until all balance requirements are met.

---

## What is deferred out of R4

These items are deliberately NOT resolved in R4 and are routed to the correct downstream session:

- **Detector list** → R5 (factors say what to measure; detectors say how to measure memorization on top of those factors)
- **Exact algorithmic specifications** for clustering-dependent and entity-dependent factors → Thales-joint factor-algorithm session (user will open a dedicated conversation with Thales materials)
- **Chinese-specific data quality flags schema** → Thales-joint session, specific sub-section
- **Point-in-time market mechanics fields** (for Tradability, Session Timing, Outcome function) → dedicated point-in-time analysis track
- **LLM annotation protocol** (Claude + Codex cross-validation, IAA thresholds, human QA budget, prompt design) → dedicated annotation protocol track
- **Pre-registration specific wording** → R6 (after R5 detector list is locked)
- **Cognitive-science interpretation lens** → post-pilot one-shot ad-hoc consultation (not a permanent agent)
- **Exact-Span Rarity subproject go/no-go** → decided when trigram annotation infrastructure is ready; pre-committed in the plan but not guaranteed to execute
- **Timeline commitment** (May 25 vs August 3 ARR) → user decision, with Editor's R4 Step 2 estimate being August 3 realistic
- **Venue-drift audit** → after R4 factor list + R5 detector list both lock; depends on what detectors get added

---

## R4 → R5 handoff

R5 is **detector investigation**. The inputs R5 must take from R4:

### Frozen inputs (R5 must not relitigate)

1. The 12-factor shortlist is locked. R5 does not add or remove factors.
2. Methodology principles P1-P5 are binding on R5.
3. Risks R1-R3 are documented and must be carried forward.
4. Target N = 3,200 (initial reference) + stopping conditions; R5 must respect this.
5. Case text for measurement = CLS text (Decision 5 from v2/v3, still binding).
6. Pre-commit granularity = 档位 2 偏 1 (Decision 9).
7. Editor's narrative hierarchy (spine/secondary/auxiliary/control/reserve) — affects how R5 presents detector choices.

### Known R5 inputs from R4 (new information to seed R5)

1. **MemGuard-Alpha's 5-MIA ensemble** — R5 must evaluate whether to select a single MIA method or an ensemble.
2. **MemGuard-Alpha's CMMD** (Cross-Model Memorization Disagreement) — R5 must include this as a detector candidate. R5 orchestrator should also survey which Chinese LLMs with different cutoffs are available for CMMD (Qwen 2.5 / Qwen 2 / DeepSeek / ChatGLM / Baichuan / Yi etc.).
3. **GSM-Symbolic's NoOp intervention** — R5 must evaluate a FinMem-NoOp probe variant: insert a plausible but irrelevant clause into CLS text and observe prediction change. This is distinct from SR (changes fact) and FO (substitutes false outcome).
4. **Cutoff exposure is empirically validated** by MemGuard-Alpha's Cohen's d jump when adding temporal proximity features — R5 should prioritize detectors that are time-aware.
5. **Shared annotation dependence (Risk R1)** affects R5 as well — any detector that uses cluster / entity / event-type features inherits the dependency. R5 should also prefer detectors that run directly on raw text (Min-K%, MIA, perplexity, extraction) as a robustness layer.

### Detector family candidates for R5 to evaluate (seeded from R4 findings)

- **Min-K% family** (multiple variants: Min-K%, Min-K%++, PatentMIA)
- **MIA family** (multiple variants; at least 3-4 based on MemGuard-Alpha's ensemble approach)
- **Extraction attacks** (Carlini style — canaries, verbatim recall)
- **Counterfactual probes** — SR (Semantic Reversal, already in-project), FO (False Outcome, already in-project), FinMem-NoOp (new, from GSM-Symbolic)
- **CMMD** — Cross-Model Memorization Disagreement (new, from MemGuard-Alpha)
- **Contamination detection** — PaCoST, CLEAN-EVAL, VarBench, LastingBench (already in library)
- **Perplexity-based** — zlib-ratio, reference-ratio

R5 is not committed to all of these; it is a starting set for R5 Step 1 brainstorm.

### Open questions R5 must explicitly address

1. **Ensemble vs single-detector strategy** — MemGuard-Alpha uses 5 MIA methods + logistic regression. Should FinMem-Bench detector layer also be an ensemble, or a set of independent detectors reported side-by-side?
2. **Black-box vs white-box split** — DeepSeek has broken logprobs, so white-box detectors (Min-K%, MIA) can only run on Qwen / Llama / Baichuan etc. Does R5 commit to white-box primary / black-box secondary, or vice versa?
3. **CMMD feasibility** — can we assemble 3-4 Chinese LLMs with genuinely different training cutoffs for CMMD? If not, CMMD has to be deferred or dropped.
4. **FinMem-NoOp design** — what counts as an "irrelevant but plausible" clause in CLS? How is it generated? Is it LLM-generated (introducing a new annotation dependency) or rule-based?
5. **Detector-dependent factors** (Principle P5) — each detector may contribute 1-2 stratification fields. What are they for each detector in the shortlist?
6. **Integration with factor shortlist** — which detectors are most informative on which factors? E.g., Min-K% is most informative on Propagation Intensity and Duplicate Cluster Size; CMMD is most informative on Cutoff Exposure.

---

## R4 status: CONCEPTUALLY CLOSED — execution gates remain

R4 is **conceptually closed**: all 4 Codex domain agents + Challenger + Cold-Reader have produced reviews, all user decisions are captured in `docs/DECISION_20260413_mvp_direction.md` v5, the 12-factor shortlist + 5 methodology principles + 4 risks + per-factor construct caveats are in place. Items discussed within R4 but requiring downstream operationalization are explicitly routed to their correct downstream sessions, NOT silently deferred.

**Execution gates that remain before R4 outputs become operational**:

1. **Thales-joint factor algorithm session** must produce: cluster algorithm, entity normalization rules, event-type taxonomy frozen, Chinese-specific data quality flag schema. Until then, the 4 Thales-dependent factors (Propagation Intensity composite, Entity Salience, Structured Event Type, parts of Disclosure Regime) cannot be computed.
2. **Point-in-time analysis track** must produce: market mechanics field list, intraday vs daily-close decision, outcome function `O_i(H)` parameters. Until then, Tradability Tier and Cutoff Exposure cannot be fully realized.
3. **LLM annotation protocol track** must produce: prompt design, IAA targets, human QA budget, agreement-bucket audit rules. Until then, no annotation can begin at scale.
4. **Anchor Strength 150-case experiment** must run before any memorization detector touches the main corpus. This is a hard gate per Principle P3.

**R4 is conceptually closed but operationally pending** the above 4 gates. The benchmark's data collection cannot start until at least gates 1, 2, and 4 are resolved. Gate 3 can begin in parallel with the others.

Next up: R5 detector investigation (to be started in a new session). A separate R5 kickoff document is provided at `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md`.

---

## v5 cold-reader cleanup pass

After this synthesis was first written, a cold-reader Codex review (`BENCHMARK_R4_FINAL_REVIEW.md`) caught 11 specific issues:
- Stale "What R4 should produce / can assume" sections (still pre-R4 language)
- D13 / D14 in the locked decisions table contradicting Principles P3 / P4 (interaction count, anchor experiment N)
- Decision 3 / Decision 6 / Open Tracks contradicting Principle P2 on canonical selection
- Construct collapse risk (3 latent blocs masquerading as 12 independent factors) not explicitly captured
- Per-factor construct caveats missing (factor names overclaim what is actually measured)
- P1 not auditable from prose alone (no per-factor source-class table)
- P2 operationally incomplete (no-match handling, tie-breakers, distribution all under-specified)
- P3 statistical rule too loose (independent CIs instead of paired bootstrap)
- R4 closure language too triumphant ("no blockers" while execution gates remain)

All 11 issues were applied to produce decision doc v5. The cold reader's biggest finding — **construct collapse risk** — is now Risk R4 in the v5 risks section, with a 3-bloc structure explicitly documented and a mitigation plan that includes the tail-entity diagnostic interaction pair, joint modeling mandate, bloc-level summary as a secondary analysis, and the cluster-free robustness companion to Propagation Intensity.

This synthesis itself was minimally updated (this section + closure language softening); the substantive changes all live in v5 of the decision document.
