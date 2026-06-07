---
title: Active Document Review — Orchestrator Synthesis
stage: post-R5A-freeze cleanup
date: 2026-04-16
inputs:
  - ACTIVE_DOC_REVIEW_QUANT.md
  - ACTIVE_DOC_REVIEW_NLP.md
  - ACTIVE_DOC_REVIEW_STATS.md
  - ACTIVE_DOC_REVIEW_EDITOR.md
ground_truth:
  - R5A_FROZEN_SHORTLIST.md
  - MEASUREMENT_FRAMEWORK.md
purpose: Unified action list merging 4-lens reviews of active documents post-freeze
---

# Active Document Review — Orchestrator Synthesis

After R5A freeze (2026-04-16), 4 Codex agents (Quant / NLP / Stats / Editor) independently audited 29 active project documents against the frozen shortlist + four-layer measurement framework. This document merges their findings into a unified action list.

---

## 1. Convergence at a glance

| Verdict | 4/4 lenses | 3/4 lenses | 2/4 lenses | Conflict |
|---|---|---|---|---|
| **Update needed** | DECISION_20260413, CMMD_MODEL_FLEET_SURVEY, LITERATURE_SWEEP_2026_04, FACTOR_LITERATURE_PROVENANCE, config/prompts/README | TIMELINE, PAPER_INDEX, THALES_SIGNAL_PROFILE_REVIEW, MEDIA_COVERAGE_FEASIBILITY | BENCHMARK_PROPOSAL (others say archive) | — |
| **Archive** | All BENCHMARK_R4*, BENCHMARK_R5_KICKOFF, all R5A_STEP1+STEP2_SYNTHESIS, R5A_TEMPORAL_CUE, FLEET_REVIEW (Round 1), all LIT_SWEEP raw outputs + V6_EDIT_PROPOSALS, plans/phase5-qwen-positive-control | BENCHMARK_PROPOSAL | DECISION_20260413 (Stats+Editor), CMMD_MODEL_FLEET_SURVEY (Stats+Editor) | — |
| **No change** | FLEET_SELECTION_LITERATURE | FLEET_REVIEW_R2_SYNTHESIS, R5A_FROZEN_SHORTLIST, MEASUREMENT_FRAMEWORK | TIMELINE (Quant), THALES (Quant), MEDIA_COVERAGE (NLP) | — |

The agreement on what to **archive** is striking: 16 documents have unanimous archive recommendations from all 4 lenses. The remaining live document set should shrink dramatically.

---

## 2. Unified action list — sorted by priority

### Priority A — Critical contradictions that block downstream work

These will cause concrete pilot/implementation errors if not fixed before Phase 7.

| # | Action | Affected documents | Rationale |
|---|---|---|---|
| **A1** | **Resolve thinking-mode policy** in fleet documentation | `CMMD_MODEL_FLEET_SURVEY.md`, `FLEET_REVIEW_SYNTHESIS.md`, `FLEET_REVIEW_R2_SYNTHESIS.md` | Frozen policy: `P_logprob` requires thinking OFF on all 5 white-box; `P_predict`/`P_extract` use each model's default mode. Old fleet docs say "all confirmatory fleet thinking OFF". A pilot following the wrong doc produces irreversible data quality issues. |
| **A2** | **Lock single fleet authority** at 9-model core (5 white-box + 4 black-box) | `CMMD_MODEL_FLEET_SURVEY.md` (6-model), `DECISION_20260413_mvp_direction.md` (6-model), `BENCHMARK_R5_KICKOFF.md` (6-model), `LITERATURE_SWEEP_2026_04.md` (6-model), `R5A_TEMPORAL_CUE_SYNTHESIS.md` (6-model) | Repository currently contains 6/7/8/9-model versions. Cost estimates, power analysis, and operator coverage all depend on this number. |
| **A3** | **Lock single sample size**: 3,200 gross / 2,560 scorable | `DECISION_20260413_mvp_direction.md`, `MEDIA_COVERAGE_FEASIBILITY.md`, `CMMD_MODEL_FLEET_SURVEY.md` cost tables | Multiple docs treat "3,200" as the analysis target. Frozen target is 2,560 scorable from 3,200 gross (≈80% verification yield). |
| **A4** | **Replace `config/prompts/README.md` with R5A operator prompt schema** | `config/prompts/README.md` | Live prompt pointer is still Phase 0-4 `E1-E6`/`direct_prediction`/`decomposed_*` schema. Frozen shortlist references `config/prompts/` as live but no `P_predict`/`P_logprob`/`P_extract`/`P_schema` prompt schema exists yet. This is the single largest gap between methodology and implementation. |
| **A5** | **Mark `DECISION_20260413_mvp_direction.md` as superseded** | `DECISION_20260413_mvp_direction.md` + `TIMELINE.md` index | Currently labeled "权威文档" in TIMELINE but its statistical layer (12-factor, 6-model, P1-P5, N=3200) is pre-freeze. New agents entering the project may follow the wrong authority chain. Add superseded banner; downgrade in TIMELINE to "background / decision history". |

### Priority B — Terminology alignment (4-layer framework)

Apply the old→new crosswalk consistently across remaining live documents.

| Old term | New term | Affected docs (sample) |
|---|---|---|
| detector / detector pool / detector slot | estimand / operator / perturbation (per layer) | DECISION, LITERATURE_SWEEP, FACTOR_LITERATURE_PROVENANCE |
| D1 / CMMD | E_CMMD (P_predict) | LITERATURE_SWEEP, R5A_STEP*_SYNTHESIS |
| D2 / PCSG | E_PCSG (P_logprob) | LITERATURE_SWEEP, R5A_STEP*_SYNTHESIS |
| D3 / Min-K%++ / CTS | E_CTS (P_logprob) | LITERATURE_SWEEP, R5A_STEP*_SYNTHESIS |
| D4a / ADG conflict | E_ADG_conflict (C_ADG, diagnostic only) | R5A_TEMPORAL_CUE_SYNTHESIS |
| D4b / ADG misdirection | E_ADG (C_ADG + C_temporal, reserve) | R5A_TEMPORAL_CUE_SYNTHESIS |
| D5-SR / Semantic Reversal | E_SR (C_SR), exploratory | DECISION, BENCHMARK_PROPOSAL |
| D5-FO / False Outcome | E_FO (C_FO), confirmatory + quality gate | DECISION, BENCHMARK_PROPOSAL |
| D6 / FinMem-NoOp | E_NoOp (C_NoOp), confirmatory + quality gate | DECISION, R5A_STEP2_SYNTHESIS |
| D7 / EAD | E_EAD_t / E_EAD_nt (C_anon target/non-target), exploratory | LITERATURE_SWEEP, V6_EDIT_PROPOSALS |
| D8 / Extraction | E_extract (P_extract), reserve with 2-tier promotion | DECISION, R5A_STEP2_SYNTHESIS |
| D9 / RAVEN | **DROPPED** — must not appear as active anywhere | (audit all) |
| D10 / Debias Delta | **DROPPED** — must not appear as active anywhere | (audit all) |
| D11 / TDR / Temporal Dose-Response | E_TDR — **interaction term β₃ = cutoff×dose, NOT standalone** | R5A_TEMPORAL_CUE_SYNTHESIS, LITERATURE_SWEEP |
| D12 / Schema-Completion | P_schema (operator candidate) → E_schema_cont (continuation reserve only); Cloze + QA = DEFER | R5A_STEP2_SYNTHESIS |
| Anonymization (binary mask/no-mask) | C_anon multi-level dose-response (L0-L4 gradient) | LITERATURE_SWEEP, V6_EDIT_PROPOSALS |
| 12-factor shortlist (spine/secondary/auxiliary) | 4 core confirmatory factors + Bloc 0-3 inventory | DECISION, FACTOR_LITERATURE_PROVENANCE |
| ~60-65 coefficients / detector slots | 5 estimands × 4 factors = 20 coefficients (Westfall-Young max-T) | R5A_STEP2_SYNTHESIS, DECISION |

### Priority C — Document index hygiene

| # | Action | Document | Rationale |
|---|---|---|---|
| **C1** | Re-classify in TIMELINE: archive vs active | `TIMELINE.md` | Document index still lists `BENCHMARK_PROPOSAL`, `CMMD_MODEL_FLEET_SURVEY`, `phase5-qwen-positive-control` as active. Mark with historical/archived tags. Compress "权威文档" section to just `R5A_FROZEN_SHORTLIST` + `MEASUREMENT_FRAMEWORK`. |
| **C2** | Refresh PAPER_INDEX.md | `PAPER_INDEX.md` | Last sync 2026-04-06; missing 27+ papers added during R4 sweep + fleet review. Add categories: memorization/MIA foundations, chronological controls, construct validity, finance look-ahead, fleet selection. |
| **C3** | Reframe MEDIA_COVERAGE_FEASIBILITY as reserve-factor memo | `MEDIA_COVERAGE_FEASIBILITY.md` | Drop "13th active factor" framing; clarify it does NOT enter the frozen 20-coefficient confirmatory family. Sync N to "3,200 gross / 2,560 scorable". |
| **C4** | Light context note on FACTOR_LITERATURE_PROVENANCE | `FACTOR_LITERATURE_PROVENANCE.md` | Document is provenance background; add header noting "pre-freeze 15+2 audit; not current active factor map" + crosswalk to 4 core factors. Keep evidence body intact. |
| **C5** | Light context note on THALES_SIGNAL_PROFILE_REVIEW | `THALES_SIGNAL_PROFILE_REVIEW.md` | Add header: "informs Bloc 3 operationalization only; does not change confirmatory family". Update Event Type comparison from "7-cat draft" to current hierarchical 15-20 + 5-7. |
| **C6** | Reframe LITERATURE_SWEEP_2026_04 as historical sweep | `docs/LITERATURE_SWEEP_2026_04.md` | Add "historical sweep feeding v6.x; not current spec" header. Change "current conclusions" to "supports frozen shortlist". Mark fleet conclusion as superseded by FLEET_REVIEW_R2_SYNTHESIS. |

### Priority D — Bulk archive (move to `archive/` directory)

These 16 documents have unanimous (4/4) or near-unanimous (3/4) archive recommendations. Move them to a new `archive/r4_r5a_lineage/` (or similar) and leave pointer stubs in original locations if needed.

**R4 lineage (5 docs):**
- `refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md`
- `refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md`
- `refine-logs/reviews/BENCHMARK_R4_CHALLENGER.md`
- `refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md`
- `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md`

**R5A pre-freeze lineage (4 docs):**
- `refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md`
- `refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md`
- `refine-logs/reviews/R5A_STEP2/R5A_STEP2_SYNTHESIS.md`
- `refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md`

**Fleet review Round 1 (1 doc):**
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md` (superseded by R2)

**Literature sweep raw outputs (6 docs):**
- `refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md`
- `refine-logs/reviews/LIT_SWEEP_B_BROAD_SWEEP.md`
- `refine-logs/reviews/LIT_SWEEP_C_CHRONO_BASELINES.md`
- `refine-logs/reviews/LIT_SWEEP_D_CITED_BUT_UNREAD.md`
- `refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md`
- `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md`

**Phase 5 plan (1 doc):**
- `plans/phase5-qwen-positive-control.md` (extract Qwen CPT causal anchor concept first)

**Mixed verdicts — user decides whether to archive or update:**
- `docs/BENCHMARK_PROPOSAL.md` (3/4 archive, NLP says rewrite or archive)
- `docs/DECISION_20260413_mvp_direction.md` (Stats+Editor archive; Quant+NLP say update with superseded banner)
- `docs/CMMD_MODEL_FLEET_SURVEY.md` (Stats+Editor archive; Quant+NLP say update to 9-model)

**Recommendation**: archive all three with pointer stubs. The information is captured in `R5A_FROZEN_SHORTLIST.md` + `FLEET_REVIEW_R2_SYNTHESIS.md`. Continued maintenance burden outweighs benefit.

---

## 3. Cross-document contradictions — consolidated

The 4 lenses surfaced 11 distinct contradictions; deduplicated below.

| # | Contradiction | Severity | Resolution |
|---|---|---|---|
| 1 | **Fleet size**: 6 / 7 / 8 / 9 models | HIGH | Lock 9-model core (5 WB + 4 BB). Update or archive all 6-model docs. |
| 2 | **Thinking-mode policy**: all-OFF vs P_logprob-only-OFF | HIGH | Lock per frozen framework: P_logprob OFF only. Pilot blocker if wrong. |
| 3 | **Authority chain**: DECISION + R5_KICKOFF claim authority alongside frozen shortlist | HIGH | Single authority is `R5A_FROZEN_SHORTLIST.md` + `MEASUREMENT_FRAMEWORK.md`. Update TIMELINE index. |
| 4 | **Confirmatory family**: detector slots vs 5 estimands × 4 factors = 20 coefficients with quality gates | HIGH | Lock per frozen shortlist. Old EAD-as-confirmatory and NoOp-auto-extension contradict the gate mechanism. |
| 5 | **E_TDR definition**: standalone detector / sensitivity protocol vs mixed-model interaction term | HIGH | Lock as `β₃ = cutoff × dose` interaction. Not standalone. |
| 6 | **Factor hierarchy**: 12-factor spine/secondary/auxiliary + 3-bloc vs 4 core + 4-bloc inventory + Temporal Anchor Recoverability | MEDIUM | Lock 4-bloc + 4 core confirmatory. |
| 7 | **D9 RAVEN / D10 Debias Delta**: still appearing in some docs | MEDIUM | DROPPED. Audit and remove all live references. |
| 8 | **C_anon design**: binary mask vs L0-L4 dose-response | MEDIUM | Lock L0-L4 gradient (pilot uses L0 vs L4 binary). |
| 9 | **P_schema status**: open / candidate vs Continuation reserve / Cloze+QA defer | MEDIUM | Lock per §6 of frozen shortlist. |
| 10 | **Sample size**: N=3,200 vs 2,560 | MEDIUM | Lock 3,200 gross / 2,560 scorable. Update cost tables. |
| 11 | **Tradability Tier role**: alpha-bridge / auxiliary / extra-corpus pillar vs Bloc 2 ordinal stratifier | LOW | Lock as Bloc 2 ordinal; not driving confirmatory narrative. |
| 12 | **Implementation gap**: `config/prompts/` is legacy E1-E6 schema, not P_predict/P_logprob/P_extract operators | HIGH | Build R5A operator prompt schema before Phase 7 pilot. |

---

## 4. Recommended execution sequence

**Stage 1 — Authority chain repair (low cost, high leverage):**
1. Add superseded banner + crosswalk to `DECISION_20260413_mvp_direction.md` (or archive it)
2. Update `TIMELINE.md` document index: archive markers + tighten "权威文档" section
3. Refresh `PAPER_INDEX.md`

**Stage 2 — Bulk archive sweep:**
4. Move 16 unanimous-archive docs to `archive/r4_r5a_lineage/`
5. Leave a one-line README.md in each archived directory pointing to current authoritative doc
6. Decide on the 3 mixed-verdict docs (BENCHMARK_PROPOSAL, DECISION, CMMD_FLEET_SURVEY). Default: archive.

**Stage 3 — Light context notes (preserve existing content, add headers):**
7. `FACTOR_LITERATURE_PROVENANCE.md` — pre-freeze audit notice + crosswalk
8. `THALES_SIGNAL_PROFILE_REVIEW.md` — Bloc 3 operationalization scope notice
9. `LITERATURE_SWEEP_2026_04.md` — historical sweep notice
10. `MEDIA_COVERAGE_FEASIBILITY.md` — reserve-factor reframe + N sync

**Stage 4 — Implementation gap (blocker for Phase 7):**
11. Write R5A operator prompt schema as a new doc (e.g., `config/prompts/R5A_OPERATOR_SCHEMA.md`)
12. Mark current `config/prompts/README.md` as legacy Phase 0-4 schema
13. Define prompts for P_predict, P_logprob, P_extract; note P_schema as candidate

**Stage 5 — FLEET_REVIEW_R2_SYNTHESIS light update:**
14. Add freeze note: 9-model core authoritative; GPT-5.4 historical only
15. Map "logprob/behavioral detectors" terms to "P_logprob/P_predict"

---

## 5. Documents that need NO change (post-freeze)

These are clean per all 4 lenses and should be left alone:

- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` (the authority itself)
- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` (the framework definitions)
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md` (external lit review, valid as-is)

---

## 6. Notes on lens disagreements

- **Quant** is alone in marking `MEDIA_COVERAGE_FEASIBILITY` as needing update via cross-doc reference (NLP says no change). Recommendation: light reframe per Editor + Stats convergence.
- **Quant** is alone in marking `TIMELINE` as no-change (others want index hygiene). Recommendation: light index hygiene per 3-lens majority.
- **NLP** is alone in marking `MEDIA_COVERAGE_FEASIBILITY` as no-change. Recommendation: light reframe per Editor + Stats convergence.
- **Stats + Editor** want full archive of `DECISION_20260413` and `CMMD_FLEET_SURVEY`; **Quant + NLP** want updates with superseded banner. Recommendation: archive, since the 9-model fleet is captured in FLEET_REVIEW_R2_SYNTHESIS and the frozen scope is in R5A_FROZEN_SHORTLIST. Maintenance burden of keeping a "v6.3 update" of DECISION outweighs the value.

---

## 7. Estimated effort

| Stage | Effort | Risk if skipped |
|---|---|---|
| Stage 1 (authority chain) | ~30 min | New agents follow wrong authority |
| Stage 2 (bulk archive) | ~30 min | Term confusion, accidental relitigation |
| Stage 3 (context notes) | ~30 min | Misreading provenance docs as current spec |
| Stage 4 (operator prompts) | ~2-4 hrs (substantive) | **BLOCKS Phase 7 pilot** |
| Stage 5 (fleet review notes) | ~10 min | Minor terminology drift |

Stage 4 is the only substantive work — everything else is documentation hygiene.

---

## 8. Output artifacts (for user review)

- 4 lens reports: `ACTIVE_DOC_REVIEW_{QUANT,NLP,STATS,EDITOR}.md` in this directory
- This synthesis: `ACTIVE_DOC_REVIEW_SYNTHESIS.md`

User should review this synthesis and confirm execution order before any document edits or archive moves are applied.
