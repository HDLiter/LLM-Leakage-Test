# Plan: Stratified Dataset Expansion + Multi-Dimensional Annotation

## Context

Current diagnostic results (192 cases) cannot support memorization claims because key cells in the (period × anchor_level) stratification are too small:

- **Post-cutoff Level 3** (uniquely identifiable events): only **6 cases**
- **Post-cutoff Level 0** (no anchor): only **4 cases**
- The "significant" CPT temporal effect (impact Fisher p=0.042) is driven by these tiny cells
- Pre-cutoff anchor pattern is counterintuitive (Level 1 has 0% flips, Level 3 has 6.5%) — undermining the memorization-signal interpretation

To make any temporal/memorization claim defensible, we need:
1. A **larger, balanced sample** (target 400+ cases, iterate up to 700 if cells are short)
2. **Three new annotation dimensions** with proper methodology:
   - **anchor_level** (0-3): from a fixed written rubric (current `anchor_analysis.json` is hand-coded Python, not Codex)
   - **frequency_class** (high/med/low): from a real retrieval index over CLS corpus
   - **reversibility** (high/med/low): post-hoc, comparing original + counterfactual via Codex
3. **All 192 existing cases re-annotated** with Codex for consistency
4. **Case-level concurrency** in D2 (current 1.5h → ~30min target)

## Critical findings from exploration

These corrections shape the plan:

1. **`anchor_analysis.json` is hand-coded Python** (`scripts/generate_anchor_analysis.py` has `LEVELS = {"tc_001": 3, ...}`), NOT Codex-generated. Re-doing with Codex + a written rubric is a quality improvement.

2. **`anchor_level` is not wired into `run_diagnostic_2.py` strata** — only `period`, `rarity_estimate`, `memorization_likelihood`. Current stratified analysis joins anchor data post-hoc. New schema must surface anchor in `bundle.metadata` and `aggregate_by_field`.

3. **The real concurrency bottleneck is `prepare_conditions()` in `src/pilot.py`** — 4 sync `client.chat()` CF generation calls per case. For 175 cases that's ~700 serial calls. The `max_concurrency=20` flag only helps the *task* phase. Fixing this requires flat multi-phase batching at the driver level (3 API phases + 1 CPU scoring phase, see Phase C1 below).

4. **`LLMClient.batch_chat_concurrent()` already enforces `Semaphore(20)`** — no need for a custom queue. The fix is to flatten ALL CF calls across all cases into one batch, all outcome-negation calls into another, and all task calls into a third.

5. **`memorization_likelihood` becomes redundant** once `anchor_level` + `frequency_class` exist. Drop it (do not preserve as legacy).

## Phase 0 — Dependencies (NEW, addresses Round 2 HIGH)

Before any phase below runs, install required packages into `rag_finance` conda env. Prefer conda channels for things that have them, then `python -m pip` for the rest:

```bash
conda install -n rag_finance -c conda-forge jieba statsmodels
conda run -n rag_finance python -m pip install rank_bm25 firthlogist
```

If `firthlogist` install fails on Windows: fall back to `rpy2` + R `logistf` package, OR document Firth as future work and use `statsmodels.discrete.discrete_model.Logit` with regularization (`fit_regularized`) as a weaker substitute. Verify all imports succeed before starting Phase A.

## Codex review changes (incorporated below)

The Plan agent's draft was reviewed by Codex (xhigh, two rounds) and revised in these places:

1. **Sampling funnel split**: v2 strict filter rejects roundups/commentary — exactly the Level 0/1 content we need. B1 now has TWO separate funnels: high-anchor and low-anchor.
2. **Power target rewritten around expected `fo_flip` events**, not raw case counts. 50 per cell is insufficient if base flip rate is single-digit; collapse to binary anchor early if needed.
3. **Batch refactor preserves correctness contracts**: per-prompt retry, `bypass_cache` on retry, `target_echo` validation, per-prompt exception capture. Two-pass design (full batch → mini-batch for failures only).
4. **`generate_false_outcome_cpt` LLM negation must be in the batch plan** — added as a third batch phase (CF generation → outcome negation → task execution). **Pre-cutoff uses LLM only — no regex/generic fallback** (would mix probe modalities and create a worse confound). On failure, mark `llm_failed` and exclude from CPT analysis with missingness footnote.
5. **Reversibility demoted from regression covariate to sensitivity slice** — it's downstream of SR generation, so primary adjustment use is methodologically weak. Use Firth/penalized logistic for rare events.
6. **Frequency thresholds use a fixed corpus-level reference**, not sample terciles. Dedupe near-duplicate hits. Compute hits only on pre-article date window (true exposure proxy).
7. **Weighted Cohen's κ for ordinal labels**, plus a small human-reviewed gold slice.
8. **Event-level dedup**: normalized title + entity + date window, not just title prefix.
9. **A2 (BM25 build) and C (concurrency refactor) run in parallel with A1/B1.**
10. **10-20 case end-to-end smoke run before D1.**

## Phases

### Phase A — Annotation infrastructure

**A1. Write `docs/ANCHOR_RUBRIC.md`**
- Decision-tree rubric (4 ordered yes/no questions, no Likert scale)
- 2 examples per level (one prototypical, one edge case) with 1-line rationale
- Forbidden shortcuts section ("do NOT use publish_time alone")
- Header field `rubric_version: 1.0`
- Target ~600 tokens, embedded verbatim in every Codex annotation prompt

**A2. Build BM25 frequency index**
- New script: `scripts/build_frequency_index.py`
- Tokenize titles + content from `D:\GitRepos\Thales\datasets\cls_telegraph_raw\*.json` with `jieba.cut_for_search`
- Use `rank_bm25.BM25Okapi`
- Pickle to `data/cache/cls_bm25_index.pkl` with `{index, doc_ids, doc_dates, tokenizer_version, build_timestamp}`
- Sanity check: print top-5 hits for "央行降准", "证监会", "宁德时代"
- Reasoning: BM25 over jieba is reproducible and interpretable; semantic embeddings would over-merge distinct events

**A3. Compute frequency_class** (revised per Codex, tightened for Round 2)
- New script: `scripts/compute_frequency.py`
- Per case: query = `title + " " + " ".join(key_entities)`, get top-N BM25 hits
- **Restrict hit window to dates BEFORE the case's `publish_time`** — frequency must be a true exposure proxy, not include the article itself
- **Dedupe near-duplicate hits** (tightened): cluster requires ALL of:
  - Normalized title cosine similarity > 0.7 (jieba tokens, set-based)
  - At least one shared key entity (from the case's `key_entities`)
  - Same date or ±3 days
  - This prevents over-merging distinct events that happen to share a date or template
- Count clusters, not raw hits
- **Use fixed corpus-level reference thresholds**, calibrated once on a 50-case calibration set, then frozen
- Output: `data/seed/frequency_analysis.json` with `{case_id, cluster_count, top_clusters: [{title, entity, date}], frequency_class, threshold_used, threshold_basis: "calibration_set_v1"}`

### Phase B — Sampling + annotation

**B1. Two-funnel sampling: `scripts/sample_cls_v3.py`** (revised per Codex)

The v2 strict filter rejects roundups/commentary, which is exactly the Level 0/1 content we need. B1 must have TWO independent funnels:

- **High-anchor funnel** (target Level 2-3): inherit v2 strict filter, add positive boosts for date/document patterns
- **Low-anchor funnel** (target Level 0-1): RELAX v2 filter to allow:
  - Sector commentary, market roundups (without specific entities)
  - ETF/strategy marketing copy
  - Generic trend summaries
  - Scheduled template content (earnings calendar, etc.)
- Both funnels: apply event-level dedup (normalized title + entity + date window ±3 days), NOT just title prefix
- Both funnels: log rejection counts per filter rule
- Targets: 250 high-anchor + 250 low-anchor, evenly split pre/post-cutoff (so ~125 per cell of high/low × pre/post)
- Output: `data/seed/expansion_candidates_v3.json` with `funnel: "high_anchor"|"low_anchor"` field

**B2. Codex annotation: `scripts/annotate_v3_batch.py`** (revised per Codex)
- Reads rubric from `docs/ANCHOR_RUBRIC.md` as text, injects into Codex system prompt
- Batch size 40 candidates per Codex call
- Output schema: standard v2 fields + `anchor_level` + `anchor_cues` + `anchor_rationale` + `rubric_version`
- **Re-annotates all 192 existing cases** for consistency (input from `test_cases_expanded.json`)
- Final merge to `data/seed/test_cases_v3.json`
- **Reliability protocol** (replaces simple κ check, sized for Round 2 precision concern):
  - **50 cases double-annotated** (up from 30) with `bypass_cache=True` and a different seed
  - Use **weighted Cohen's κ** (linear weights for ordinal labels), NOT plain κ
  - Target κ_w ≥ 0.65 with 95% CI lower bound > 0.55 (bootstrap CI on the 50-pair sample)
  - Plus a **30-case human-reviewed gold slice** (PI manually labels, used as ground truth for accuracy estimate)
  - Report both κ_w (with bootstrap CI) and accuracy-vs-gold (with Wilson CI); if either fails or its CI is too wide, refine rubric and re-annotate
  - Note: 50+30 is still small for tight precision but is a sane minimum given Codex annotation cost; document the limitation in PILOT_RESULTS.md

**B3. Run frequency computation**
- Run `compute_frequency.py` on `test_cases_v3.json`

**B4. Power-aware cell check: `scripts/check_strata.py`** (revised per Codex)
- Cross-tab `period × anchor_level`
- **Power calculation**: target effect OR=2.5 at α=0.05, 80% power, given expected baseline `fo_flip` rate ~5-10%
  - Per-cell case count needed: ~80-150 if base rate is 5%, ~50-80 if base rate is 10%
  - Decision: if pilot's 7-10% flip rate holds, target **80 cases per cell** (320 pre + 320 post = 640 total)
- **If sample budget (700 cap) cannot satisfy 80/cell across all 4 anchor levels**:
  - **Collapse to binary anchor early**: `weakly_anchored` (Level 0+1) vs `strongly_anchored` (Level 2+3)
  - This gives 2 cells × 2 periods = 4 cells, easily reachable with 200 per cell at 800 total
  - Document decision in PILOT_RESULTS.md as a power-driven design choice
- **Report expected number of `fo_flip` events per cell**, not just case count
- Print full distribution + power analysis before committing to D2
- **Canonical analysis field** (addresses Round 2 MEDIUM): write the binary collapse decision to `data/seed/strata_config.json` with key `analysis_anchor_field`, value either `"anchor_level"` (4-level) or `"anchor_binary"` (2-level). E1 and E2 BOTH read this file and use the same field — no hardcoding `C(anchor_level)` in regression scripts.

**B5. Targeted re-sampling (iterative)**
- For under-filled cells, write a targeted filter (e.g., for post-cutoff Level 3: must have `\d{4}年\d{1,2}月\d{1,2}日` OR `《[^》]{6,}》` + named institution + direction-bearing verb)
- Apply to CLS post-cutoff files
- **Apply the SAME event-level dedup as B1** (normalized title + entity + date window ±3 days), NOT just title prefix — this addresses Round 2 partial-fix flag
- Re-run B2-B4 on the new candidates
- Hard cap: 700 total cases
- If post-cutoff Level 3 still short after targeted sampling, document as data limitation and collapse to binary `weakly_anchored / strongly_anchored` for Mantel-Haenszel (keep 4-level for descriptive tables)

### Phase C — Pipeline concurrency upgrade (revised per Codex)

**C0. Pre-requisite: harden `LLMClient.batch_chat_concurrent` for per-prompt failure isolation**
- Currently `asyncio.gather` raises on first exception, killing the whole batch
- Change to `asyncio.gather(..., return_exceptions=True)` and surface per-prompt failures with stable indices
- Add a `failure_isolated=True` flag for backward compat

**C1. Refactor `src/pilot.py` for THREE-phase batching** (not two — LLM negation in `generate_false_outcome_cpt` is a third phase)
- Split `_generate_cf_safe()` into prompt builder + response parser
- **Preserve all existing correctness contracts**:
  - Per-prompt retry on failure (3 attempts) with `bypass_cache=True` on retry
  - `target_echo` validation
  - JSON schema validation
- **Phase 1 — CF generation**: `prepare_cf_batch(client, loader, test_cases) -> dict[(case_id, cf_type), cf_payload]`
  - Builds 3 prompt pairs per case (semantic_reversal_direction, semantic_reversal_fund_impact, neutral_paraphrase)
  - Single `client.batch_chat_concurrent(prompts, max_concurrency=20, failure_isolated=True)`
  - **Mini-batch retry pass**: collect failed/invalid prompts, retry with `bypass_cache=True`, up to 2 retry passes
  - Parse + validate responses
- **Phase 2 — Outcome negation**: `prepare_fo_cpt_batch(client, test_cases) -> dict[case_id, fo_article | None]`
  - For pre-cutoff cases with `known_outcome`, builds outcome-negation prompts (LLM-based path only)
  - Same batched + retry pattern as Phase 1
  - **Pre-cutoff cases: LLM-only, no fallback.** If LLM negation exhausts retries (3 attempts with `bypass_cache=True`), set `fo_article = None`, `cpt_mode = "llm_failed"`, emit a warning to logs. Do NOT fall back to regex `_negate_outcome()` or generic templates. Reason: mixing CPT probe modalities (LLM-negated vs regex-swapped vs generic-template) within one analysis introduces a confound that's worse than missing data.
  - **Post-cutoff cases**: still use the generic template path (no API call) since they have no `known_outcome` to negate. This is a separate, clearly labeled probe type (`cpt_mode = "generic_post_cutoff"`).
  - In E1/E2, **only cases with `cpt_mode = "llm_negated"` are used for the pre-cutoff CPT analysis**; `llm_failed` cases are excluded with a missingness footnote. Post-cutoff cases use a separate analysis arm (or are dropped from temporal comparison if homogeneity matters more).
  - Track and report `n_llm_failed` per period in the D2 stratified output. If >5% of pre-cutoff cases hit `llm_failed`, investigate prompt or rate-limit issues before E1.
- **Phase 3 — Task execution**: `run_tasks_batch(client, loader, test_cases, conditions_map) -> dict[case_id, task_results]`
  - Builds (task × condition) prompt pairs across all cases
  - Same batched + retry pattern
- **Phase 4 — Scoring** (CPU-only): per-case CFLS scoring after batches complete
- Keep existing `prepare_conditions` and `run_single_case` for backward compat with `src/pilot.py::run_pilot`
- **Per-case error tracking**: if a case fails any phase, mark in `errors[]` with stage and reason; never silently drop

**C2. Update `scripts/run_diagnostic_2.py`**
- New chunked driver: 50 cases per chunk, Phase1 (CF gen) → Phase2 (FO negation) → Phase3 (task exec) → Phase4 (CPU scoring) → checkpoint
- Bump `PIPELINE_VERSION = 3`
- Update `CaseBundle.metadata` to include `anchor_level`, `frequency_class`, `reversibility` (initially `None`)
- Update `adapt_case()` to read new fields from `test_cases_v3.json`
- Drop `memorization_likelihood` from strata (replaced by anchor + frequency)
- Add to `aggregate_by_field` calls: `by_anchor_level`, `by_frequency_class`, `by_period_x_anchor_level` (joint key)
- Change `DEFAULT_CASES_PATH` to `data/seed/test_cases_v3.json`
- Estimated wall time: ~25 min for 400-500 cases (8-10 chunks × ~3 min)

### Phase D — Run + post-hoc reversibility (revised per Codex)

**D0. Smoke test before full run**
- Run D2 on a 10-20 case sample first (`--n-cases 15`)
- Verify: phase 1/2/3/4 all execute, output JSON parses, strata are populated correctly
- Compare CFLS values for 5 of these cases against the v2 results — should be identical (modulo cache hits)

**D1. Run D2 from scratch on full dataset**
- Delete `data/results/diagnostic_2_results.json` first (schema change)
- Command: `conda run -n rag_finance python scripts/run_diagnostic_2.py`

**D2. Post-hoc reversibility annotation: `scripts/annotate_reversibility.py`**
- Load D2 results
- Per case: extract `original` article + `semantic_reversal` SR text from `tasks.direct_prediction.base.responses`
- Codex prompt structure:
  - Show: original_article, sr_rewritten_article, known_outcome (do NOT show expected_direction to avoid anchoring)
  - Ask: `reversibility ∈ {high, medium, low}` + 1-sentence rationale
  - Definitions:
    - **high**: both versions read as natural real-world news (e.g., "stock rose 5%" ↔ "stock fell 5%")
    - **medium**: counterfactual is grammatical and locally coherent but unusual for that entity/event type
    - **low**: counterfactual is internally contradictory or inverts non-reversible public-record facts
- Write back into both `test_cases_v3.json` (`reversibility` field) and D2 results (case metadata)
- Spot-check 10 labels manually before relying on them

### Phase E — Stratified re-analysis (revised per Codex)

**E1. Update `scripts/quick_stats.py`**
- Add Mantel-Haenszel via `statsmodels.stats.contingency_tables.StratifiedTable`
- **Read `data/seed/strata_config.json` to get `analysis_anchor_field`** — primary stratum is whatever field that key names (`anchor_level` if 4-level survives, `anchor_binary` if collapsed). Never hardcode the field name.
- Per-stratum Fisher + pooled MH OR + Breslow-Day homogeneity test
- Sanity check: pooled MH OR should sit within range of stratum-level ORs
- **`reversibility` and `frequency_class` are NOT primary strata** — they are sensitivity slices (see E2)

**E2. Sensitivity analysis: `scripts/sensitivity_analysis.py`** (replaces conditional_logit, addresses Round 2 MEDIUM)
- **Primary inference is MH from E1**, not regression
- **Read `data/seed/strata_config.json` to get `analysis_anchor_field`** — never hardcode `anchor_level` or `anchor_binary`
- Sensitivity slices (compute MH within each subset, do NOT pool):
  - Within `reversibility=high` only
  - Within `frequency_class=low` only
  - Within `frequency_class=high` only
- **For regression supplement**, use **Firth's penalized logistic** (`firthlogist` package, fall back to `rpy2` + R `logistf`, last resort `statsmodels.fit_regularized`)
  - Plain logit is fragile under rare events / quasi-separation, which is exactly our regime
  - Model: `fo_flip ~ period + C({analysis_anchor_field})` only — DO NOT include reversibility/frequency as primary covariates (they are post-hoc / downstream of generation)
  - The anchor field name comes from `strata_config.json`, not a hardcoded string
- Output: `data/results/sensitivity_analysis.json`

**E3. Update `docs/PILOT_RESULTS.md`**
- Full MH table per task
- κ for anchor_level reliability
- Frequency distribution histogram
- Sample-size rationale and any collapsed cells documented
- Updated answers to Q1/Q2/Q3 (the three diagnostic questions)

## Critical files

- **New:** `docs/ANCHOR_RUBRIC.md`, `data/cache/cls_bm25_index.pkl`, `data/seed/expansion_candidates_v3.json`, `data/seed/test_cases_v3.json`, `data/seed/frequency_analysis.json`
- **New scripts:** `scripts/build_frequency_index.py`, `scripts/compute_frequency.py`, `scripts/sample_cls_v3.py`, `scripts/annotate_v3_batch.py`, `scripts/check_strata.py`, `scripts/annotate_reversibility.py`, `scripts/sensitivity_analysis.py`
- **Refactored:** `src/pilot.py` (add batch functions), `src/masking.py` (**remove regex/generic fallback for pre-cutoff in `generate_false_outcome_cpt` — LLM only for pre-cutoff, raise/return None on failure**), `src/llm_client.py` (add `failure_isolated=True` mode), `scripts/run_diagnostic_2.py` (chunked driver, pipeline_version=3, new strata, new default cases path), `scripts/quick_stats.py` (add MH)

## Reused infrastructure

- `src/llm_client.py::LLMClient.batch_chat_concurrent()` — already has `Semaphore(20)`, no change needed
- `src/masking.py::generate_false_outcome_cpt()` — LLM-based negation already landed (pipeline v2)
- `src/metrics.py::cfls_per_case()`, `_detect_fo_flip()` — no changes
- `scripts/sample_cls_v2.py` filter rules — copy as base for v3 with logging added
- `scripts/quick_stats.py` existing tests — extend, don't replace

## Verification (revised per Codex)

- **A2:** BM25 sanity check returns plausible top-5 for known queries; index file <1.5 GB
- **A3:** Frequency distribution is right-skewed; if uniform, tokenizer is broken; threshold basis recorded
- **B2:** Weighted κ ≥ 0.65 + ≥80% accuracy vs human gold slice
- **B4:** Print cell counts AND power analysis (expected `fo_flip` events per cell) before committing to D2
- **C0:** Unit test for per-prompt failure isolation in `batch_chat_concurrent`
- **C1:** Equivalence test on **15-20 cases** (not 2): `prepare_cf_batch` + `prepare_fo_cpt_batch` + `run_tasks_batch` produce per-case conditions and CFLS values byte-identical to legacy `prepare_conditions` + `run_single_case` (modulo cache hits and dict ordering)
- **D0:** 10-20 case smoke test passes before D1
- **D1:** Wall clock <30 min for 400-500 cases (vs 90 min current); per-case errors logged with stage; `n_llm_failed` for pre-cutoff CPT < 5% of pre-cutoff cases
- **D2:** Spot-check 10 reversibility labels manually; check that labels are NOT perfectly correlated with `expected_direction`
- **E1:** Pooled MH OR sits within stratum-level OR range; report Breslow-Day p
- **E2:** Firth logit converges; sensitivity slices show direction consistent with main MH
- **E3:** PILOT_RESULTS.md has full MH table + weighted κ + accuracy-vs-gold + frequency histogram + collapsed-cell rationale + power analysis

## Risks and mitigations (revised per Codex)

1. **Codex rubric drift between batches** → embed rubric text verbatim in every Codex prompt, never edit mid-run, version-tag with `rubric_version`
2. **Post-cutoff Level 3/0 still short after targeted re-sampling** → collapse to binary anchor at B4 (power-driven), keep 4-level for descriptive tables, document as data limitation
3. **Weighted κ <0.65 OR gold accuracy <80%** → refine rubric, re-annotate, do NOT proceed with low-reliability data
4. **Cache poisoning when re-annotating** → `LLMClient` cache key includes prompt hash; new rubric → new hash → automatic re-query. Only `bypass_cache=True` for κ double-annotation
5. **Schema break for resumed D2** → delete `diagnostic_2_results.json` before D1, do not rely on `--resume`
6. **Reversibility labels correlate perfectly with `expected_direction`** → check at E2; if found, exclude from sensitivity analysis
7. **One bad prompt poisons a batch** (C0) → `failure_isolated=True` mode + per-prompt retry + stage-tagged errors
8. **`generate_false_outcome_cpt` LLM negation overlooked in batching** → explicit Phase 2 batch (C1 revised)
9. **Frequency thresholds drift across iterations** → calibrate ONCE on 50-case set, freeze (A3 revised)
10. **Mantel-Haenszel underpowered if base flip rate is single-digit** → power-driven binary collapse (B4 revised)
11. **Firth logit unavailable** → Phase 0 dependency check; fall back to `rpy2` + R `logistf` or `statsmodels.fit_regularized` and document
12. **Sequencing bottleneck**: A1/B1 wait for rubric → run A2 (BM25 build) and C0/C1 (concurrency refactor) in parallel
13. **Phase 2 LLM negation failure** → mark `cpt_mode = llm_failed`, emit warning, exclude from CPT analysis with missingness footnote. NO fallback to regex/generic for pre-cutoff cases (mixing probe modalities is a worse confound than missing data). Investigate if `n_llm_failed > 5%`.
14. **Binary collapse not propagating to E2** → canonical `strata_config.json` field, read by both E1 and E2
15. **Frequency cluster over-merging distinct events** → tightened cluster rule (entity match required)

## Out of scope

- Vector DB (sentence-transformer embeddings) — BM25 sufficient for this study; vector DB is future work
- Multi-model replication (Qwen, etc.) — separate experiment
- Paper draft updates beyond `PILOT_RESULTS.md` — deferred until results stabilize
- `memorization_likelihood` field migration in old data — drop entirely, don't preserve

## Effort estimate (revised per Codex)

| Phase | Work | Wall time |
|-------|------|-----------|
| A1 | Write rubric | 0.5 day |
| A2 | BM25 index build (parallel with A1) | 0.5 day |
| A3 | Frequency computation | 0.5 day |
| B1 | Two-funnel sampling | 0.5 day |
| B2 | Codex annotation (~600 cases) + κ + gold slice | 1.5 days |
| B3-B5 | Frequency + cell check + iterative re-sampling | 1 day |
| C0-C1 | Concurrency refactor + per-prompt failure isolation (parallel with A/B) | 1.5 days |
| C2 | D2 driver update | 0.5 day |
| D0-D1 | Smoke test + full run | 0.5 day |
| D2 | Reversibility annotation | 0.5 day |
| E1-E3 | Re-analysis + doc update | 1 day |
| **Total** | | **~7-8 days** with parallelism, **9-10 days** sequential |
