# R4 / R5A Pre-Freeze Lineage Archive

**Date archived:** 2026-04-16

**Reason for archiving:** All documents in this directory have been superseded by the R5A freeze (2026-04-16). They are preserved here for historical and provenance purposes only. They MUST NOT be treated as current spec by any downstream agent or contributor.

## Authoritative current docs

The single source of truth for the project's current methodology is now:

- [`refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`](../../refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md) — frozen estimand / operator / factor / fleet shortlist
- [`refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md`](../../refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md) — four-layer measurement framework definitions

The orchestrator synthesis driving this bulk-archive decision is at [`refine-logs/reviews/R5A_STEP2/ACTIVE_DOC_REVIEW_SYNTHESIS.md`](../../refine-logs/reviews/R5A_STEP2/ACTIVE_DOC_REVIEW_SYNTHESIS.md). It was assembled from four independent Codex lens reviews (Quant / NLP / Stats / Editor) of all active project documents, with all 20 files below receiving an "archive" verdict from at least 3 of 4 lenses (16 unanimous, 3 mixed-verdict per Stats+Editor majority).

---

## Archived files by category

### R4 lineage (5 docs)

Superseded by the R5A freeze (frozen shortlist + measurement framework). These were the round-4 benchmark synthesis chain that fed into R5A; their contents are absorbed into the frozen docs.

- `refine-logs/reviews/BENCHMARK_R4A_SYNTHESIS.md`
- `refine-logs/reviews/BENCHMARK_R4_FINAL_SYNTHESIS.md`
- `refine-logs/reviews/BENCHMARK_R4_CHALLENGER.md`
- `refine-logs/reviews/BENCHMARK_R4_POST_V5_2_INTEGRATION_REVIEW.md`
- `refine-logs/reviews/BENCHMARK_R5_KICKOFF.md`

### R5A pre-freeze lineage (4 docs)

Superseded by the R5A freeze. These are the working syntheses from R5A Step 1, Step 2 (pre-freeze), and the temporal-cue side investigation; their conclusions are now consolidated into `R5A_FROZEN_SHORTLIST.md` and `MEASUREMENT_FRAMEWORK.md`.

- `refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md`
- `refine-logs/reviews/R5A_STEP1/R5A_STEP1_SYNTHESIS.md`
- `refine-logs/reviews/R5A_STEP2/R5A_STEP2_SYNTHESIS.md`
- `refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md`

### Fleet Review Round 1 (1 doc)

Superseded by `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md` (Round 2) and the 9-model core fleet locked in the frozen shortlist.

- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_SYNTHESIS.md`

### Literature sweep raw outputs (6 docs)

Raw per-axis lit sweep outputs and the V6 edit proposals. Superseded by the literature integration captured in the R5A frozen docs and `docs/LITERATURE_SWEEP_2026_04.md` (which itself is being reframed as a historical sweep memo).

- `refine-logs/reviews/LIT_SWEEP_A_FACTOR_PROVENANCE.md`
- `refine-logs/reviews/LIT_SWEEP_B_BROAD_SWEEP.md`
- `refine-logs/reviews/LIT_SWEEP_C_CHRONO_BASELINES.md`
- `refine-logs/reviews/LIT_SWEEP_D_CITED_BUT_UNREAD.md`
- `refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md`
- `refine-logs/reviews/LIT_SWEEP_V6_EDIT_PROPOSALS.md`

### Phase 5 plan (1 doc)

Superseded by the R5A frozen scope. The Qwen CPT positive-control concept is preserved in project memory (`feedback_*` notes) and absorbed into the broader confirmatory-factor design in the frozen shortlist.

- `plans/phase5-qwen-positive-control.md`

### Mixed-verdict docs (3 docs)

Per the orchestrator synthesis recommendation: archive (Stats + Editor majority). These docs carry pre-freeze fleet sizes (6-model), pre-freeze sample sizes (N=3,200 with no scorable distinction), and pre-freeze detector taxonomy (D1–D12 / RAVEN / Debias Delta). Their content is captured by `R5A_FROZEN_SHORTLIST.md` and `FLEET_REVIEW_R2_SYNTHESIS.md`; continued maintenance burden outweighs the value.

- `docs/BENCHMARK_PROPOSAL.md`
- `docs/DECISION_20260413_mvp_direction.md`
- `docs/CMMD_MODEL_FLEET_SURVEY.md`

---

## Total: 20 documents archived

Do NOT cite these documents as authoritative. Use the frozen shortlist + measurement framework instead.
