---
title: WS0.5 Thales Alignment — Reuse-vs-Rebuild Decision, Auto-Tune Loop, and Factor Pipeline Spec
date: 2026-05-18
revision: v0.4
revision_date: 2026-05-20
revision_basis: |
  v0.1 (2026-05-18): initial draft — recorded T1/T2/T3 findings and Scheme A reuse posture; received Codex round-0 review (`temp/ws0_5_alignment_review.md`) flagging MAJOR-REVISIONS-NEEDED on 4 blockers + 4 majors + 1 minor.
  v0.2 (2026-05-19): applies 9 issue decisions made in interactive review with user.
    Issue #1: topic taxonomy corrected to Thales V3 13-class + Scheme A 5-super-type collapse.
    Issue #2: Target Salience full construct (selection + ordinal scoring + non-redundancy rules).
    Issue #3: auto-tune Scheme Y (4-layer split, limited-exposure acceptance, paired tests, active fixture).
    Issue #4: determinism redefined as replay-from-cache + provenance.
    Issue #5: closure quota gates (factor_schema.yaml, quota_report.json, check_pilot_cells.py).
    Issue #6: signal_profile starting prompt deferred to smoke comparison (V2 combined vs v5.5 two-pass).
    Issue #7: Historical Family Recurrence contract (24mo window, within-super_type percentile, 3-step entity matching, no dedup).
    Issue #8: budget cap → token accounting + safety rails.
    Issue #9: Authority status clarified as covariate, not confirmatory.
  v0.3 (2026-05-19): applies round-1 review patches from 3 parallel Codex reviewers (ML engineer / statistician / measurement) — all 3 verdict MAJOR-REVISIONS-NEEDED, no cross-role conflict. Patches:
    E-1/S-1: §4.1 MDE preflight + split `delta_min_practical` (0.02 floor) from `delta_detectable_planning` (task-specific MDE under acceptance_n + alpha schedule).
    E-2/S-7: §4.1 proposer-isolation rule (API-only, sanitized train payload); binary predicates only to proposers (drop rounded-delta surface).
    E-3: §4.1 candidate contract (candidate.yaml + diagnosis.json + minimal-edit diff validator).
    E-4: §4.1 manifest lock + max-look exhaustion stop rule.
    E-5: §5.1 recurrence applicability rule — post-cutoff 350 controls get `null + missing_reason="not_applicable_post_cutoff"`.
    E-6: §5.3 R4 rule-based ambiguity override + versioned cache key.
    E-7/S-5: §5.2 full-frame ranks + tie rule + bin-stability report; primary renamed to `pre_case_cls_family_recurrence`.
    E-8: §6.1/§6.4 storage tiers (pilot per-case JSON, full-CLS sharded JSONL.zst with shard index).
    E-9: §6.3 canonical row-hash verification + hard-fail on missing cache.
    E-10: §7.1/§7.2 dry-run token estimator + buffered ledger writer + `run_state` checkpoint + `--resume` contract.
    S-2: §4.2 `alpha_family_scope` + per-task allocation + look-counting rule.
    S-3: §4.1 F1 gate disambiguation — paired permutation = primary, cluster bootstrap CI = descriptive; micro-F1 article-cluster unit.
    S-4: §4.1 active/random fixture separation — `train_visible` + `challenge_dev` active; `random_inner_dev` + `acceptance_holdout` + `final_holdout` + `anchor_dev` stratified random.
    S-6: §3.3.3 expand to all 6 confirmatory pairs, partial correlations, GVIF + condition number, mixed-model singularity diagnostics.
    S-8: §11 R-W05-1 stale "bootstrap CI gate" → "paired acceptance gate".
    C-1: §3.3 narrow construct claim ("selected-market-target reach composite"); `context_gate=0` becomes `target_validity_low` flag, not pure-low exposure; preserve raw components.
    C-2: §5.1/§5.2 add `recurrence_count_visible_to_model` (model-cutoff-censored sensitivity); rename primary case-date count to `pre_case_cls_family_recurrence`.
    C-3: §5.2 `log1p(recurrence_count)` retained as construct-nearer sensitivity; percentile framed as relative recurrence within event family.
    C-4: §5.2 clustered/deduped sensitivity + duplicate-ratio field for no-dedup primary measure.
    C-5: §3.4 v5.5 Authority conditioning caveat.
  v0.3 round-2 verdicts (2026-05-19, 3 parallel Codex reviewers):
    Measurement: APPROVE (clean — `temp/ws0_5_round2_measurement_review.md`)
    ML Engineer: APPROVE-WITH-MINOR-PATCHES — 2 narrow text patches (`temp/ws0_5_round2_ml_engineer_review.md`):
      E-1 follow-up: MDE preflight cannot estimate paired discordance q from incumbent alone; use pre-registered q-grid {0.05,0.10,0.20} or prior candidate evidence; report post-allocation per_look_alpha ≈ 0.000556. Applied in-place to §4.1 MDE preflight block.
      E-6 follow-up: R4 cache lookup key must be computable before any provider call; remove `response_id` from lookup key (kept as provenance). Applied in-place to §5.2 Phase R4 Step 4c.
    Statistician: APPROVE-WITH-MINOR-PATCHES — same S-1 wording patch as ML-engineer's E-1 (`temp/ws0_5_round2_statistician_review.md`); resolved by the E-1 patch above.
  Per runbook §5: 1× APPROVE + 2× APPROVE-WITH-MINOR-PATCHES → minor patches applied in-place to v0.3, no round-3 re-review.
  v0.4 (2026-05-20): user-directed simplification of §4 only. Replaced the heavy "Scheme Y" auto-tune framework (limited-exposure Ladder gate, paired McNemar / permutation tests, cross-task alpha spending, MDE preflight, 7-way fixture split, manifest lock, run-state resume) with a plain train/dev/test split: tune on `train`, rank candidates on `dev`, evaluate the final prompt once on a sealed `test` split. Rationale: a prompt is a measurement instrument; the per-round accept decision is an optimization step, not a confirmatory statistical claim, so it needs no hypothesis test. The sealed-test-set protection — the only necessary overfitting defense — is kept. v0.4 supersedes round-1 issues E-1/E-2/E-3/E-4/S-1/S-2/S-3/S-4/S-7 (all §4-machinery). Non-§4 round-1/2 issues remain in force. Downstream cleanup: §7.1 budget config rename, §7.4 trimmed to lightweight checkpoint, §8 deliverables (removed `ws0_5_mde_preflight.py`, `manifest.lock.yaml`, `mde_report.json`, `run_state.json`; `*_autotune_manifest.yaml` → `*_autotune_config.yaml`), §9 closure condition #5 simplified, §10 schedule, §11 risks R-W05-1/3/7. Not Codex-re-reviewed (removes machinery, adds no claim).
  v0.4 cont. (2026-05-20, continued review session — still v0.4): user is reviewing the 14 non-§4 round-1/2 issues (C-1..C-5, E-5..E-10, S-5/S-6/S-8). C-1 reopened and redesigned §3.3 — the case-admissibility test (a central, tradable target) is promoted to a GLOBAL sampling pre-filter (§3.3.1) applied to every case and every factor; Target Salience (§3.3.2) becomes a pure scorer, `log1p` of the target's CLS mention count. Removes the v0.3 `context_gate` veto + `target_validity_low` flag (collapsed into the pre-filter's centrality test — the same text-local signal was used twice), the `static_reach` 1/2/3 ordinal + family mapping table, and the market-metadata snapshot dependency (§3.3.4 deleted; `r5a_market_metadata_snapshot.json` + `build_market_metadata_snapshot.py` dropped from §8; §10 S1 trimmed; §12 Target-Salience class-1/2 open item closed). Rationale: market cap / index membership measures firm size, not fame, and misclassifies small-but-heavily-covered targets; a corpus mention count is the direct quantitative prominence proxy and reuses the §5 recurrence pipeline at near-zero cost. Supersedes the v0.3 C-1 patch. C-2 + user review then replaced the per-case recurrence window `[T−24mo, T)` with a fixed pre-cutoff window `[corpus_start, earliest_model_cutoff)`, shared by both Recurrence (§5) and Target Salience (§3.3.2) — the two factors now differ only by the event-family filter. This dissolves C-2 (model-visibility — `recurrence_count_visible_to_model` removed) and E-5 (recurrence now computable for all 430 cases incl. post-cutoff controls — no `not_applicable_post_cutoff`), and renames the primary recurrence variable `pre_case_cls_family_recurrence` → `cls_family_recurrence`. C-3: the recurrence confirmatory variable becomes the continuous `log1p_recurrence_count` — the within-super_type percentile, the median-split binary, the 4-way interpretation rules, and the `absolute_high_recurrence` parallel field are all removed; magnitude is the construct, and the event-family base-rate confound is handled by within-super_type stratified sampling plus super_type as a regression covariate, not by a percentile transform. A non-confirmatory within-super_type sampling bin remains for the plan §6.4 n_eff design. This also dissolves E-7/S-5 (the confirmatory variable has no bin → no bin-flip; the LOO/bootstrap bin-stability machinery and `ws0_5_bin_stability.py` are removed). C-4: an empirical probe (`scripts/cls_dup_probe.py`, 1.2M CLS items) found only 0.48% intra-day duplication — mostly legitimate rolling tickers — so the no-dedup recurrence count is used directly and all v0.3 C-4 dedup sensitivity fields (`recurrence_count_clustered`, `recurrence_count_first_per_day`, `duplicate_ratio`) are dropped. C-5: the §3.4 signal_profile smoke comparison gains a third arm — an independent two-pass (Authority predicted without conditioning on Modality, ported from Thales v5 Split-Independent); if it is selected, Authority is an independent measurement and the conditioning caveat is dropped (the caveat is now contingent on the smoke outcome). E-6: a Codex methods review (`temp/entity_disambig_methods_20260520.md`) found the LLM-on-critical-path entity pipeline both over- and under-engineered; §5.2 Phase R2-R4 are redesigned to a deterministic master-data pipeline — Phase R2 builds a tiered alias table from AKShare securities master data (codes / official names / former names with effective dates), Phase R4 resolves matches by deterministic evidence tiers, risk is rule-scored against a broader collision universe. The LLM alias-gen + LLM per-match-confirm steps leave the main path (the v0.3 E-6 ambiguity-override rules + versioned cache key are moot); §5.3 becomes a one-off user-reviewed smoke testing whether LLM alias generation / disambiguation adds enough recall to be admitted as a human-reviewed tier-3. E-8: the replay cache is consolidated from the v0.3 three-tier sharded-JSONL + `shard_index.parquet` + `run_state.json` scheme into two objects — a committed ~5 MB `pilot_raw_responses.jsonl` (Tier A, normal git) and a single git-ignored SQLite DB `data/cache/ws0_5_response_cache.sqlite` (Tier B, full-CLS + auto-tune, which natively serves as cache + key index + resume state); no Git LFS anywhere; the `ws0_5_storage_preflight.py` LFS preflight is dropped; the SQLite is backed up to a private Kaggle dataset (sha in `factor_provenance.json`). E-9: replay reproducibility keeps the `canonical_table_hash` content check and the hard-fail-on-missing/corrupt-cache rule, but drops the pyarrow-version-pinning + `replay_environment.lock.json` gold-plating (the content hash is already the reproducibility guarantee; byte-identical parquet is an unneeded stricter goal). E-10: the budget subsystem collapses into one metered DeepSeek client (`src/`) — it meters tokens/cost per call, so the per-task token estimate falls out of the smokes + auto-tune runs that precede the heavy S4 phase (no separate `ws0_5_token_estimator.py` dry-run), the live total drives the 2×/5× safety rails, and the run-end dump is the budget report; the separate `budget_ledger_*.jsonl` + buffered writer + §7.2 `LedgerEntry` schema and the pricing daily-refresh/epoch machinery are removed; resume was already covered by the v0.4 §7.3 checkpoint + the E-8 SQLite. S-6: a Codex literature review (`temp/collinearity_diagnostics_20260520.md`) confirms the v0.3 five-diagnostic discriminant suite is over-built by 2-3 items; §3.3.3 is cut to the field-standard minimum — VIF on the four confirmatory factors + a 4×4 Pearson correlation matrix, empirical max-VIF thresholds (≤5 / 5-10 / ≥10); condition number, partial/residual correlations, and the GVIF apparatus are dropped, and mixed-model singular-fit/convergence is reclassified as a separate analysis-stage model-fit check. S-8: confirmed already resolved — v0.4's §4 rewrite had already replaced the stale "bootstrap CI gate" wording in §11 R-W05-1/3/7. **All 14 round-1/2 issues are now resolved**: 10 produced memo edits (C-1..C-5, E-6, E-8, E-9, E-10, S-6); 3 dissolved as byproducts (E-5 via the C-2 window change, E-7 & S-5 via the C-3 continuous-variable change); 1 confirmed already-resolved (S-8). The review's consistent direction was simplification — each reviewer-driven heavyweight mechanism was cut to a minimal correct form. Awaiting user sign-off.
status: v0.4 — 14-issue round-1/2 review complete (§3.3 / §3.4 / §5 / §6 / §7 revised, all net-simplified); awaiting user sign-off + WS0.5 closure
authority: |
  Resolves the WS0.5 scope-TBD placeholder in plans/phase7-pilot-implementation.md §5.1A
  (revisions v2.2 / v2.3 / v2.4) and the matching open item in PENDING.md (line 37-48).
  Answers the T1 / T2 / T3 verification questions recorded in plan §5.1A.
  Locks the factor-pipeline implementation strategy that WS4 pilot manifest freeze
  (Section 6) and the §14.4 sign-off checklist depend on.
related_docs:
  - plans/phase7-pilot-implementation.md (master plan; §5.1A, §6, §11.1, §12 R11/R12, §13, §14.4)
  - PENDING.md (open item "WS0.5 — Thales alignment design")
  - docs/THALES_SIGNAL_PROFILE_REVIEW.md (background review of Thales Modality/Authority/EventType — note: written 2026-04-13, predates Thales v3 EventType refactor and v5.5 two-pass signal_profile refactor)
  - refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md (the 4 confirmatory factors + Bloc 3 factor inventory)
  - refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md (factor definitions L1)
  - D:\GitRepos\Thales\contracts\news\_annotation.py (EventType v3 13-class enum — current production)
  - D:\GitRepos\Thales\prompts\news_processing\topic_classification.py (V3 13-class prompt — 578 lines)
  - D:\GitRepos\Thales\prompts\news_processing\signal_profile.py (v5.5 two-pass — 736 lines)
  - D:\GitRepos\Thales\experiments\prompts\news_summary\fixtures\labeling_prompt_entity.md (dual-agent entity labeling — 629 lines)
  - temp/ws0_5_alignment_review.md (Codex round-0 review)
  - temp/ws0_5_supertype_analysis.md (Codex super-type Scheme A analysis)
  - temp/ws0_5_target_salience_construct.md (Codex Target Salience construct design)
  - temp/ws0_5_autotune_sota_search.md (Codex auto-tune SOTA literature search)
  - temp/entity_disambig_methods_20260520.md (Codex E-6 entity-disambiguation methods review)
  - temp/collinearity_diagnostics_20260520.md (Codex S-6 collinearity-diagnostics methods review)
---

# Decision Memo — WS0.5 Thales Alignment & Auto-Tune Loop

## 1. Problem statement

WS0.5 has been a scope-deferred placeholder in `plans/phase7-pilot-implementation.md` §5.1A
across revisions v2.2 → v2.4. WS0.5 blocks:

- WS4 pilot manifest freeze (plan §6.3 factor quotas depend on a frozen factor schema)
- §14.4 sign-off checklist (gates §13 exit conditions)
- WS3 `C_FO` rule schema freeze (per plan §4: "reads event-type labels from WS0.5 before C_FO rule schema freeze")

WS0.5 closure requires answering three verification questions and producing a decision
memo that locks reuse-vs-rebuild for the four confirmatory factors and Bloc 3 factors.

| ID | Question (from plan §5.1A) |
|---|---|
| T1 | Has Thales's topic-classification pipeline (EventType taxonomy) already been executed against CLS v3, or does it need to be run on the R5A sample? |
| T2 | Does Thales provide (or can it easily derive) an `(entity, event_type, date_window)` frequency index suitable for `historical_family_recurrence`? |
| T3 | Does CLS raw data preserve publisher metadata at meaningful coverage, such that Bloc 3 Authority can be operationalized as a genuinely extra-corpus factor instead of text inference? |

## 2. Findings from 2026-05-18/19 investigation

### 2.1 T1 — Topic classification (Thales V3 13-class prompt)

**Status of the asset.** `D:\GitRepos\Thales\prompts\news_processing\topic_classification.py`
holds a 578-line `NewsTopicClassificationPrompt` v2.2.0. The production enum
`EventType` in `D:\GitRepos\Thales\contracts\news\_annotation.py` is the **V3 13-class
taxonomy**: POLICY, ENFORCEMENT, LEGAL, INDICATOR, EARNINGS, CORPORATE, PRODUCT,
PERSONNEL, TRADING, OWNERSHIP, INDUSTRY, GEOPOLITICS, OTHER. The earlier V6 10-class
result in the topic experiment log (`primary_accuracy=0.738` on a fresh 367-item
fixture, 2026-03-30) is **historical calibration evidence on a now-superseded
taxonomy**, not the schema to freeze for R5A.

> v0.1 mis-stated the production enum as 10-class V6. Corrected in v0.2 per Codex
> round-0 Issue #1 and direct repository inspection.

**Status against CLS.** Thales has run topic classification only against ~5000-item
quality universes and ~370-item fixtures, not against the full CLS corpus. Answer
to T1: **Thales has a battle-tested 13-class V3 prompt and calibrated fixtures, but
no persisted full-corpus EventType labels.** WS0.5 must run inference against the
R5A pilot cases plus a fixed pre-cutoff recurrence reference window — and as decided in
Issue #7, against the full CLS mirror.

**Test fixtures available for V4 Pro calibration:**
- `experiments/prompts/news_topic_classification/fixtures/quality_uniform.json` (~370 items, balanced ~25/type)
- `experiments/prompts/news_topic_classification/fixtures/quality_natural.json` (~600 items, natural distribution; held blind, will be re-sampled if any auto-tune patch touches it)
- `experiments/prompts/news_topic_classification/fixtures/boundary_decision_trees.md`

### 2.2 T2 — Entity extraction (Thales summary dual-agent labeling)

**Status of the asset.** The user's earlier Story 9.15 v2 R1 work built a dual-agent
entity labeling pipeline as part of the summary experiment:

- `D:\GitRepos\Thales\experiments\prompts\news_summary\fixtures\labeling_prompt_entity.md` (629-line 4-stage pipeline)
- `D:\GitRepos\Thales\experiments\prompts\news_summary\fixtures\quality_summary_pilot.json` (80-item adjudicated fixture)
- raw labels `raw_labels_claude_code_entity_batch*.json` and `raw_labels_codex_mcp_entity_batch*.json` (dual-agent independent labels)
- `validate_raw_labels.py` validator

**Output schema.** `RawSalienceLabel` carries per-entity `value` / `type` (closed
enum: person, institution, region, company, ...) / `salience` (`core | supporting`)
/ `reason`. The `salience` tier is reused as a *candidate signal* for Target
Salience (see §3.2), but **does not by itself define the factor**.

**Production entity-disambiguation pipeline.** Thales `pipeline/news_processing/entity_disambig.py`
is in active rework by the user; ETA incompatible with WS0.5 critical path. WS0.5
will reuse the summary-experiment dual-agent labeling prompt as the entity-extraction
starting point — not the production pipeline.

### 2.3 T3 — Authority + Modality (Thales signal_profile v5.5 two-pass)

**Status of the asset.** Current `D:\GitRepos\Thales\prompts\news_processing\signal_profile.py`
is a **v5.5 two-pass** design:

- `NewsSignalProfileModalityPrompt` (modality pass)
- `NewsSignalProfileAuthorityPrompt` (authority pass, conditioned on predicted modality)

> v0.1 mis-stated the production prompt as `NewsSignalProfilePrompt v3.0.0` (a single
> combined pass). Corrected in v0.2 per Codex round-0 Issue #6 and direct inspection.

**Calibration history.** The 2026-04-11 experiment log records on deepseek-chat
(N=200 training fixture):

| Architecture | Parse | Modality top-1 | Authority top-1 |
|---|---|---|---|
| Combined V2 (single-pass, retired) | 100% | **81.5%** | 76.0% |
| v5 Split-Independent (two-pass, no conditioning) | 100% | 79.5% | 72.5% |
| v5 Split-Conditioned (two-pass with modality→authority) | 100% | 80.5% | **79.0%** |

On Qwen 7B (SLM), split-conditioned is +23 percentage-points stronger on authority
than independent. On deepseek-chat (LLM closer to V4 Pro), the split-conditioned
advantage on authority is +3pp; combined V2 actually wins on modality by +1pp.
Thales chose v5.5 two-pass as production because it was the **global optimum across
both SLM and LLM**, not because single-pass was eliminated for LLMs.

**P1 implication.** Text-inferred Authority via either architecture is
**CLS-internal**, not extra-corpus. P1 (extra-corpus signal headroom) is **not**
restored by this WS0.5 closure regardless of which Authority architecture wins.

**CLS publisher metadata (Track B).** A 4-item spot check on `data/cls_telegraph_raw/2026-05-01.json`
shows each item carries an `author` field, but 2/4 are empty strings in the sample;
user has independently confirmed publisher metadata is "severely incomplete". A
formal coverage quantification is deferred to S1 (see §10 schedule).

**Authority status clarification (Issue #9).** Authority is handled in WS0.5
because plan §5.1A asks T3 explicitly, but it is **not** one of the four
confirmatory factors and is **not** listed in `R5A_FROZEN_SHORTLIST.md §8`
baseline Bloc 3 interaction menu. In this memo, **Authority is a candidate
Bloc 3 adjunct/covariate**, not a new confirmatory factor.

### 2.4 Mapping the 4 confirmatory factors to T1 / T2 / T3 dependencies

| Factor | Bloc | Type | Inputs needed | T1 / T2 / T3 dependency |
|---|---|---|---|---|
| Cutoff Exposure | 0 (temporal) | case × model continuous | `event_date` per case + `model_cutoff` | none — text-date + manifest |
| Historical Family Recurrence | 1 (repetition) | case-level continuous | recurrence count from CLS reference window | **T1 + T2** both required; see §5 contract |
| Target Salience | 2 (prominence) | case-level continuous | central tradable target (global pre-filter §3.3.1) + pre-cutoff CLS mention count | **T1 + T2** — reuses §5 recurrence pipeline; no market metadata |
| Template Rigidity | 1 (repetition) | case-level continuous | text-only boilerplate measure (shingling / template-bank overlap) | none — pure text feature |

**Bloc 3 factors covered by this memo (Disclosure Regime/Modality + candidate Authority):**
- Structured Event Type = T1 output (13-class) + Scheme A 5-super_type collapse
- Disclosure Regime / Modality = T3 modality output (confirmatory Bloc 3)
- Authority = T3 authority output (candidate adjunct/covariate, NOT confirmatory)
- Event Phase / Session Timing = pure timestamp features (deferred to closure addendum)

## 3. Reuse-vs-Rebuild Decisions

### 3.1 T1 — Topic classification: REUSE Thales V3 13-class prompt + Scheme A collapse

| Item | Decision |
|---|---|
| Prompt template | Reuse `NewsTopicClassificationPrompt` v2.2 (13-class V3) verbatim as V4 Pro starting point |
| Raw taxonomy | 13-class V3 enum from `_annotation.py` |
| **Super-type collapse (Scheme A, Codex-recommended)** | 5 active super-types per `temp/ws0_5_supertype_analysis.md`: `authority_decision` [POLICY+ENFORCEMENT+LEGAL+GEOPOLITICS], `issuer_catalyst` [CORPORATE+PRODUCT+PERSONNEL], `issuer_quant` [EARNINGS+OWNERSHIP], `market_macro_print` [INDICATOR+TRADING], `sector_industry` [INDUSTRY]; OTHER → `exclude_from_pilot=true` |
| Host category collapse (4-class for C_NoOp) | `authority_decision → policy`, `issuer_catalyst → corporate`, `issuer_quant → corporate`, `market_macro_print → macro`, `sector_industry → industry` |
| Calibration target | DeepSeek V4 Pro |
| Calibration fixtures | `quality_uniform.json` (~370) for tuning; `quality_natural.json` (~600) blind validation (re-sample if any patch touches it) |
| Target threshold | `primary_accuracy ≥ 0.78` on the sealed `test` split (§4) (V6 SLM 0.738; V4 Pro expected exceed) |
| Tune scope | Boundary-rule additions and few-shot examples only; no taxonomy changes |
| Scheme B fallback (4 super-types) | Trigger: `sector_industry` cannot reach 12 verified+slotable C_FO cases OR `issuer_quant` < 12 after sampling. Bridge: `reported_numbers` [EARNINGS+INDICATOR+INDUSTRY], `market_security` [TRADING+OWNERSHIP] with class-conditional host bridge |

### 3.2 T2 — Entity extraction: REUSE Thales summary entity prompt, V4 Pro auto-tune

| Item | Decision |
|---|---|
| Prompt template | Reuse `labeling_prompt_entity.md` 4-stage pipeline verbatim |
| Output schema | `RawSalienceLabel` with `value` / `type` / `salience` / `reason` |
| Consumed downstream | `(value, type)` for recurrence (§5) and Target Salience (§3.3.2); `salience=core` as the candidate pool for the §3.3.1 admissibility pre-filter |
| Calibration fixture | `quality_summary_pilot.json` (80 adjudicated items) as starting fixture; expand to ~2000 via Claude+Codex dual-agent labeling (§4) |
| Target thresholds | core-entity precision ≥ 0.85, recall ≥ 0.85 |

### 3.3 Bloc 2 — Target Salience + Case Admissibility Pre-filter (Issue #2; §3.3 redesigned per C-1)

Target is a **manifest INPUT** to `P_predict`, not LLM-inferred at operator time
(per `R5A_OPERATOR_SCHEMA.md` line 81). WS0.5 must produce, at
sampling/manifest-freeze time, (a) a deterministic rule that admits a case and
fixes its target entity, and (b) a Target Salience score for that target.

> **§3.3 redesign (per C-1 + user review).** v0.2-v0.3 conflated a *filter*
> (is there a tradable entity this article is genuinely about?) with a *scorer*
> (how prominent is that target?). This redesign separates them. The admissibility test
> becomes a **global sampling pre-filter** (§3.3.1) applied to every case and
> every factor — not a Target-Salience-internal step. Target Salience (§3.3.2)
> then becomes a **pure scorer** over an already-clean population. The v0.3
> `context_gate` veto, the `static_reach` 1/2/3 ordinal, and the market-metadata
> snapshot are removed: `context_gate` collapsed into the pre-filter's
> centrality test (the same text-local signal was being used twice), and
> `static_reach` is replaced by a direct quantitative metric.

**Construct claim.** Target Salience is operationalized as the
**log corpus footprint of the target**: `log1p` of the count of CLS articles
mentioning the target before the earliest model cutoff, across all event types. It proxies
the target's general prominence — how much text about this target the model
plausibly saw during pretraining. Market capitalization / index membership are
explicitly **not** used: they measure firm size, not fame, and would
systematically misclassify small-but-heavily-covered targets (妖股, hot new
issues, scandal stocks) as low-salience. A corpus mention count, by contrast,
rises with actual news coverage regardless of market cap.

#### 3.3.1 Case Admissibility Pre-filter (GLOBAL — applies to every sampled case)

This filter runs at sampling time on every candidate case — all four
confirmatory factors and the negative controls alike. A case is admitted only
if the article has a **central, tradable** target entity; otherwise it is
rejected before any factor is computed. The filter also outputs the single
target entity consumed by every downstream factor.

```python
def admit_case(article, salient_entities):
    # 1. Tradable candidate pool
    candidates = []
    for e in salient_entities:
        if e.salience != "core":                       continue  # core entities only
        if e.type not in {"company", "sector",
                          "index", "ETF", "commodity"}: continue  # tradable types only
        if e.type == "company" and not has_listed_ticker(e):
            continue                                             # unlisted firm: no price to predict
        if is_source_only_attribution(e):              continue  # 中信建投: (byline) → drop
        if is_pure_person_without_org(e):              continue  # standalone CEO → drop
        if is_one_char_region_alias(e):                continue  # 中/俄 if full alias exists
        candidates.append(e)

    if not candidates:
        return Reject("no_eligible_tradable_target")

    # 2. Pick the most central candidate
    selected = max(candidates, key=lambda c: (
        c.in_headline, -c.first_offset, c.mention_count, len(c.value),
    ))

    # 3. Centrality gate (absorbs the old context_gate): the article must
    #    actually be about the selected target.
    if not (selected.in_headline or selected.mention_count >= 2):
        return Reject("target_not_central_enough")

    return Target(
        target=selected.display_name,
        target_type=map_target_type(selected),          # ∈ {company, sector, index}
        target_ticker=selected.metadata.get("ticker"),  # listed company / tradable index
        target_source_entity=selected.value,
    )
```

The two rejection reasons are applied at sampling stage and never carried into
the factor table:

- `no_eligible_tradable_target` — no core entity has a tradable price. An
  unlisted company has no direction/alpha label to predict, so it is dropped
  here (the v0.2-v0.4 design wrongly let unlisted firms through and scored them
  `static_reach=1`). Macro/policy articles survive only when a tradable
  sector/index target is central; plan §6.3 host quota (`policy` ≥ 15,
  `macro` ≥ 15) is filled by sector/index targets under macro-themed articles,
  not by macro-target cases.
- `target_not_central_enough` — the most central tradable candidate is still
  only weakly present (not in the headline and mentioned at most once), so
  target assignment would be arbitrary. This replaces the v0.3
  `context_gate=0 → target_validity_low → NA` path: such a case is simply not
  sampled, so there is no validity flag and no NA value to carry downstream.

The exact centrality threshold (default: in-headline OR `mention_count ≥ 2`) is
finalized at S1 against pilot text and recorded in `factor_schema.yaml`.

#### 3.3.2 Target Salience metric

Target Salience is a property of the case's `target`:

```
target_salience[target_id] = log1p(cls_target_mention_count)

cls_target_mention_count =
    COUNT( CLS articles dated in [corpus_start, earliest_model_cutoff)
           whose confirmed salient entities include any alias in
           target_aliases[target_id] )
```

`earliest_model_cutoff` is the earliest training cutoff across the WS2 model
panel, so the window lies entirely inside every model's training data — the
count is a model-visible exposure proxy for all models. The window does **not**
follow the case date `T`: a target's pretraining footprint is fixed by the
training corpus, not by when a particular pilot case happened. (This mildly
*understates* exposure for later-cutoff models — a conservative, accepted
trade-off that keeps the factor a single case-level value, not case×model.)

Target Salience is a **continuous, target-level** factor, computed once per
target across **all event types**.

**Computed off the §5 recurrence pipeline — no new infrastructure.** Phase R1
already classifies the full CLS mirror; Phase R2 builds the pilot-target alias
table; Phase R3/R4 match and resolve those aliases against CLS articles. Target
Salience is the **same alias-match count with the `super_type` filter removed**
(all event types instead of one family). The master-data alias table
(`target_aliases.json`, §5.2 Phase R2) and the deterministic Phase-R4
disambiguation are reused unchanged. No market-metadata snapshot is needed.

**Relation to Historical Family Recurrence.** Target Salience and Historical
Family Recurrence (§5) use the **identical window** `[corpus_start,
earliest_model_cutoff)`. Their **only** difference is the event-family filter:
Target Salience counts all event types; Recurrence counts only the case's
`super_type`. Recurrence is thus the same-family slice of Target Salience —
correlated by construction (Recurrence's raw count is a sub-count of Target
Salience's). The pair is monitored in the §3.3.3 discriminant report (VIF +
correlation matrix). If their VIF / correlation exceeds the §3.3.3 threshold,
the registered fallback is either (i) redefining
Target Salience on the *complement* family-set (target mentions in event
families other than the case's `super_type`, making the two counts disjoint by
construction), or (ii) substituting a non-CLS prominence proxy (Baidu Baike
entry length). The choice is recorded in a v0.4-addendum decision.

#### 3.3.3 Construct validity & non-redundancy

- Target Salience proxies the target's **general corpus prominence** (plausible pretraining exposure to the target), measured directly as a log CLS mention count — not firm size, and not in-article centrality (centrality is the §3.3.1 pre-filter, not part of the score)
- Admissibility (a central, tradable target) is enforced once, globally, by the §3.3.1 pre-filter; Target Salience itself carries no gating, no validity flag, and no NA values
- Target Salience and Historical Family Recurrence both derive from CLS mention counts and are expected to correlate; they are kept distinct by measurement slice (§3.3.2) and their correlation is monitored — not assumed away — by the discriminant report below. This reverses the v0.2-v0.4 rule that forbade any CLS mention count in Target Salience; that rule dodged the overlap by substituting a worse proxy (market cap / index membership)
- Discriminant rule: no event_type and no month is encoded in Target Salience (those belong to Historical Family Recurrence §5)

**Discriminant check (v0.4 per S-6 — Codex literature review,
`temp/collinearity_diagnostics_20260520.md`).** The pre-manifest-freeze
non-redundancy check is the field-standard minimal pair, not a five-diagnostic
suite:

1. **VIF** on the four confirmatory factors as they enter the analysis (the
   fixed-effect design matrix). GVIF is not needed — all four are 1-df
   continuous terms, for which GVIF = VIF.
2. A **4×4 Pearson correlation matrix** of the same model-entered (transformed)
   covariates — descriptive transparency on which pair overlaps. (Pearson, not
   Spearman: collinearity is a linear design-matrix property.)

Triggers are empirical guides, **not** significance tests:

| max VIF | reading | action |
|---|---|---|
| ≤ 5 | no severe fixed-effect collinearity | proceed |
| 5-10 | moderate collinearity | keep all four factors; pre-register a sensitivity analysis |
| ≥ 10, or rank deficiency, or pairwise `|r| ≥ 0.90` | the pilot cannot separate the four effects | revise the sampling support, or combine/redefine the colliding factors (e.g. the §3.3.2 Recurrence × Target Salience fallback), before the confirmatory analysis |

Dropped from the v0.3 suite (per S-6): condition number (a redundant global
collinearity measure once VIF is reported), partial/residual correlations (they
share VIF's information source), and the GVIF apparatus. Mixed-model
singular-fit / convergence is **not** a factor-non-redundancy diagnostic — it
is a model-fit / random-effects-structure check, reported separately at the
analysis stage, not in this discriminant report.

**Remedy discipline (per S-6).** A high VIF is not a licence to mechanically
drop a confirmatory factor. The continuous factors are not dichotomized
(settled in C-3) and are not residualized against each other (residualization
changes the estimand and depends on entry order). For an unfrozen pilot the
clean fix is design-side — adjust the sampling support without inspecting
outcomes; Cutoff Exposure is the special case (fixed by event dates, so its
remedy is date-stratified rebalancing, not free resampling).

**Timing.** The check runs after candidate sampling AND after factor-value
computation (S4), before pilot manifest freeze and before any main analysis.
The discriminant report is committed at `data/factors/ws0_5_discriminant_report.json`;
a `5-10` or `≥ 10` outcome is signed off in a v0.4-addendum decision before
sampling proceeds.

### 3.4 Bloc 3 — Disclosure Regime/Modality + Authority (T3 Track A — Issue #6 smoke comparison)

Because v0.1's "V2 single-pass / 0.815 modality" claim is stale (Issue #6), v0.2
does **not** prematurely lock a single starting prompt. Instead:

**Stage 1 (smoke comparison)**: On a 100-case stratified subset of the 2000-case
auto-tune fixture, run three architectures × 1 V4 Pro round:
- `signal_profile_v2_combined.yaml` (archived V2 single-pass, ported from Thales archive)
- `signal_profile_v55_twopass.yaml` (Thales v5.5 two-pass — modality pass, then authority pass *conditioned* on predicted modality)
- `signal_profile_independent_twopass.yaml` (two-pass — modality pass + authority pass predicted *independently* from the article, no conditioning; ported from Thales v5 Split-Independent; added per C-5 user review)

> **Why the independent arm (C-5).** Thales calibration shows the authority
> benefit of conditioning shrinks sharply as the model gets stronger: +23pp on
> Qwen 7B (SLM), only +6.5pp on deepseek-chat (LLM). V4 Pro is stronger still,
> so the independent variant may now be close. If it is, it is preferred — an
> independently-predicted Authority is a genuinely independent measurement,
> which removes the C-5 caveat entirely rather than documenting around it. The
> extra arm costs ~100 V4 Pro calls.

**Decision rule** (two steps, both simple):
- **Modality** (the confirmatory factor): if `modality_acc(v2_combined) ≥ modality_acc(two_pass) − 0.02` → pick V2 combined (single-pass is cheaper); otherwise pick the two-pass modality pass.
- **Authority** (only when a two-pass architecture was chosen for modality): default to the **independent** authority pass; fall back to the **conditioned** pass only if independent authority accuracy is materially worse (default margin 3pp). Authority is a non-confirmatory covariate, so a few points of accuracy is a worthwhile price for measurement independence.

**Stage 2 (auto-tune)**: Winner enters the §4 auto-tune loop with threshold `modality_top_1 ≥ 0.82` on the sealed `test` split.

**Authority handling (Issue #9)**:
- Authority is NOT a confirmatory factor; it is a Bloc 3 candidate adjunct/covariate
- Authority metric reported but does not gate auto-tune termination
- Opportunistic tuning: after modality auto-tune converges, if session time permits, run a short Authority-only auto-tune; otherwise ship Authority as-is (V2 baseline 0.76, expected V4 Pro improvement modest)

**Authority independence — contingent on the Stage-1 outcome (C-5).** The
smoke-comparison report records the selected architecture and Authority's
resulting independence status:
- **Independent two-pass selected** → Authority is predicted from the article
  alone, not from predicted Modality. It is a genuinely independent
  measurement; no conditioning caveat is needed, and Authority could later be
  elevated beyond a covariate without remeasurement.
- **v5.5 conditioned two-pass, or V2 combined, selected** → Authority is
  measured conditional on (or jointly with) Modality, not as an independently
  observed attribute. Paper language must then treat Authority as a descriptive
  covariate/adjunct, not a separately measured Bloc 3 dimension; any future
  elevation to a confirmatory or interaction role requires an independent
  operationalization (independent text inference, publisher metadata via
  Track B, or KG/Wikipedia lookup deferred to P1-expansion).

**Track B (publisher metadata)**: After S1 author-coverage probe, if non-empty rate ≥ 80% on post-2024 CLS slice, build `config/factors/author_authority_mapping.json` as partial extra-corpus cross-check. If < 80%, abandon Track B as documented limitation (does NOT block closure). P1 is not restored either way.

### 3.5 What we explicitly do NOT do in WS0.5

| Excluded | Reason |
|---|---|
| Wait for entity-pipeline rework | User time pressure; summary-experiment dual-agent prompt sufficient |
| KG-lookup / Wikipedia Authority (genuine extra-corpus) | Out of scope; deferred to P1-expansion track separately |
| Rewrite any of the three Thales prompts from scratch | All have calibration history; rewriting forfeits the trail |
| Build a new EventType taxonomy | V3 13-class is sufficient and battle-tested |
| Use FinMem 7-class collapse | Strictly worse; loses real V3 distinctions |
| Run any inference at the operator runtime with the OTHER class | OTHER → `exclude_from_pilot=true` per Codex Issue #1 |

## 4. Auto-Tune Loop — train / dev / test split (Issue #3)

WS0.5 adapts three Thales prompts (topic classification, entity extraction,
signal_profile) to DeepSeek V4 Pro. Each prompt is a **measurement instrument**,
not a research result. The per-round decision "is this candidate prompt better
than the current one" is an optimization step, not a scientific claim — it does
not need a formal hypothesis test.

The one thing that genuinely needs protecting is the **final reported accuracy**
of each frozen prompt. That is protected by a single sealed test set, evaluated
exactly once. Everything else is a plain "is the number bigger" comparison.

> Design history. v0.1 used a bootstrap-CI-non-overlap gate that is
> statistically wrong for paired data (Codex round-0). v0.2 / v0.3
> over-corrected with a heavy limited-exposure + alpha-spending + MDE-preflight
> framework ("Scheme Y"). v0.4 (user decision, 2026-05-20) removes that
> framework: it defended the per-round accept decision as if it were a
> confirmatory statistical test, which a measurement-instrument prompt does
> not require. The sealed-test-set protection — the only part that actually
> matters — is kept. v0.4 supersedes round-1 issues E-1, E-2, E-3, E-4, S-1,
> S-2, S-3, S-4, S-7, all of which patched machinery that no longer exists.

### 4.1 Loop algorithm

```
inputs:
  initial_prompt   ← Thales prompt verbatim (per §3.1 / §3.2 / §3.4 winner)
  fixture          ← per task, Claude + Codex dual-agent labeled,
                     user-adjudicated on the disagreements

fixture split (random seed pinned in §4.2 config; fixed once, never rotated):
  train   70%   — proposers see its errors
  dev     15%   — used each round to rank candidates and pick the incumbent
  test    15%   — SEALED; evaluated exactly once, at the very end

  All three splits are stratified random samples from the labeled fixture.
  If tuning reveals weak spots, label MORE items and append them to `train`
  only. `dev` and `test` are frozen at run start and never change.

per round:
  1. Claude and Codex each read the current prompt + a summary of its
     errors on `train`, and each propose one improved prompt. (Optionally a
     third "minimal-edit" candidate — a 1-2 line conservative tweak — as an
     anti-over-mutation baseline.)
  2. Score every candidate AND the current incumbent on `dev`.
  3. If the best candidate beats the incumbent on `dev` by at least
     `min_improvement` (default 0.01), it becomes the new incumbent.
     Otherwise the incumbent is kept.
  4. Log the round (candidate prompts, their dev scores, incumbent dev
     score, which was accepted)
     → `data/factors/tuning_logs/<task>_tuning_log.jsonl`.

stop when ANY of:
  - incumbent dev score ≥ target_threshold (§3.1 / §3.2 / §3.4), OR
  - dev score has not improved for `stop_on_plateau` rounds (default 2), OR
  - `max_rounds` reached (default 10).

final evaluation (exactly once):
  Run the final incumbent prompt on `test`.
  Report the test score + a simple standard error
  ( SE = sqrt(p·(1−p)/n_test) for an accuracy metric ).
  THIS test score is the official threshold result quoted downstream.
  If it falls short of target_threshold by a meaningful margin:
  documented limitation, not a closure blocker.

the one rule (anti-overfitting):
  `test` is never seen — not by a proposer, not by the dev-ranking step,
  not by the operator — until the single final evaluation. The stopping
  rule is committed in the §4.2 config BEFORE the loop starts, so there is
  no "just one more round" after a peek.
```

Why reusing `dev` across rounds is fine: the final incumbent will be mildly
overfit to `dev`, because it was chosen to win there. That is exactly why
`test` exists and stays sealed — `test` played no part in choosing the
prompt, so the `test` number is honest.

### 4.2 Pre-registration config

Before the loop runs, commit a short `config/factors/<task>_autotune_config.yaml`:

```yaml
factor_task: topic_classification     # or entity_extraction, signal_profile
fixture_seed: <pinned>
fixture_total: 2000                   # ≥ 2000 keeps test ≥ 300 for a usable SE
split: {train: 0.70, dev: 0.15, test: 0.15}
metric: primary_accuracy              # or core_entity_f1_micro, or modality_top1
target_threshold: 0.78                # 0.78 topic / 0.85 entity / 0.82 modality
min_improvement: 0.01                 # dev-set margin required to swap incumbent
max_rounds: 10
stop_on_plateau: 2                    # rounds without dev improvement → stop
proposers: [claude, codex]            # + optional minimal_edit
```

The git SHA of this config is recorded in the tuning log. The config is
committed before the loop and not edited mid-run; a needed change means a new
config file + a fresh run, not an in-place edit.

### 4.3 Fixture build cost

Per task: ~2000 items, dual-agent (Claude + Codex) labeled, user adjudicates
only the disagreements. Roughly ~$30-40 V4 Pro per task → ~$100-120 for the
three tasks. (Down from v0.3's 3000-item 7-way split — the simple 3-way split
needs less labeled data because there are no extra holdout layers.)

## 5. Historical Family Recurrence — data contract (Issue #7)

### 5.1 Construct

**Primary confirmatory variable.** `cls_family_recurrence`. For each pilot case
`(target, super_type)`, it is the count of CLS articles in the **fixed
pre-cutoff window** `[corpus_start, earliest_model_cutoff)` that match
`(target ∨ target aliases, super_type's constituent V3 event_types)` after
entity disambiguation. `earliest_model_cutoff` is the earliest training cutoff
across the WS2 model panel.

> **v0.4 window change (per C-2 + user review).** v0.2-v0.3 used a per-case
> window `[T − 24mo, T)` that followed each event. That was a construct error:
> a model's exposure to a `(target × event-family)` pattern is fixed by its
> training corpus and does not depend on when a particular pilot case happened.
> The window is now **fixed** and anchored before the earliest model cutoff, so
> it lies entirely inside every model's training data. This dissolves two
> round-1 issues at the source: C-2 (the censored `recurrence_count_visible_to_model`
> field is removed — the whole window is model-visible by construction) and E-5
> (recurrence is now computable for post-cutoff cases too — see below). Cost:
> the fixed window mildly *understates* exposure for later-cutoff models —
> accepted, conservative, and it keeps the factor a single case-level value
> rather than case×model. Target Salience (§3.3.2) uses the same fixed window.

**Construct interpretation.** `cls_family_recurrence` is a **CLS recurrence
density** measure, **proxying** model training-exposure intensity to the
`(target × event-family)` pattern. The fixed pre-cutoff window guarantees every
counted article was inside the training data of every model, so the C-2
"window includes items the model could not have seen" concern no longer
applies. It remains a *CLS-corpus* proxy, not the true pretraining corpus, so
paper language refers to it as "pre-cutoff CLS family recurrence density,
proxying training exposure," not as a directly observed training count.

**Recurrence for negative controls (E-5 — dissolved by the window change).**
Because the window no longer depends on the case date `T`, recurrence **is
computed for all 430 pilot cases**, post-cutoff negative controls included —
there is no `null` / `not_applicable_post_cutoff` value. For a post-cutoff
control, `cls_family_recurrence` measures the model's training-time familiarity
with that `(target × event-family)`; it is a covariate and a **placebo check**
(recurrence should not predict the outcome for events the model could not have
seen). The recurrence factor's confirmatory role and its plan §6.3 quota
remain scoped to the pre-cutoff cases (where leakage is possible); the
post-cutoff value is non-confirmatory.

**No deduplication — empirically justified (C-4).** The recurrence count is
no-dedup: every matched CLS item contributes one count. C-4 worried this could
be inflated by 财联社 intra-day repost-spam (the same flash re-issued by the
feed). This was tested, not assumed: `scripts/cls_dup_probe.py` scanned the
full 1.2M-item CLS archive (2316 daily files) for intra-day exact + near
(≥ 0.85 similarity) duplicates. Result (2026-05-20): **0.48%** of all items
(0.13% exact, 0.36% near) — and the near matches are mostly legitimate
intra-day rolling tickers (e.g. southbound-flow updates whose amount genuinely
changes), so true repost-spam is even lower; per-year rate 0.22%-1.07%.
Duplication is negligible, so the no-dedup count is used directly and **no
dedup sensitivity fields are kept** (the v0.3 `recurrence_count_clustered`,
`recurrence_count_first_per_day`, `duplicate_ratio` are dropped). The probe
result is the documented answer to any reviewer asking whether the measure
indexes editorial feed mechanics. Cross-source / cross-corpus duplication
remains out of scope for WS0.5.

### 5.2 Pipeline

```
Phase R1: Topic classification on FULL CLS mirror
  Input: data/cls_telegraph_raw/ (local, sha256-locked, 2317 daily files, 2020-now)
  Tool: frozen topic_classification_v4pro.yaml (output of Phase 1 auto-tune)
  Output: data/factors/cls_event_type_index.parquet
          (each CLS item → raw_event_type, super_type, host_category)
  Cost:   ~500K-1M items × $0.0004 ≈ $200-400

Phase R2: Build the target alias table — from AKShare master data (per E-6)
  Source: AKShare securities master data (free, reproducible — chosen over
  Tushare for zero-credit access):
    - A-share list: official short name, full name, securities code
    - historical former names: stock_info_change_name (Sina) +
      stock_info_sz_change_name (SZSE), each carrying its effective date range
    - index / SW-industry master data for index & sector targets
  The pulled data is snapshotted to data/factors/akshare_master_snapshot/
  with a pull-date stamp, so the alias table is fully reproducible.

  Output: data/factors/target_aliases.json — a TIERED alias table; per alias
  {alias, entity_id, type, tier, source, effective_start, effective_end, risk}:
    tier 0  code aliases          600519 / 600519.SH / SH600519
    tier 1  official names        current short name, full name, cnspell
    tier 2  deterministic-derived ST/*ST variants, legal-suffix-stripped
            forms (only when the result stays unique), small hand-kept
            index-name whitelist (沪深300 / 上证综指 / 创业板指 / ...)
    tier 3  LLM-suggested         admitted ONLY if the §5.3 smoke earns it,
                                  and only after per-alias user review

  risk is rule-computed (NOT an LLM tag), against a BROADER universe — all
  A-shares + major indices + common group names, not just the 80-430 targets:
    low   exact code; or an official name unique in the broader universe
    high  alias collides with >1 entity in the broader universe; a 1-2-char
          generic token; a common group / place / surname / industry word
  High-risk aliases never auto-count — they require Phase R4 evidence.
  Cost: $0 (deterministic; no LLM).

Phase R3: Fixed-window candidate filter (+ type & date compatibility, per E-6)
  Window is FIXED — [corpus_start, earliest_model_cutoff) — and does NOT
  follow the case date T (per the §5.1 window change).
  For each pilot target:
    Filter cls_event_type_index for:
      date ∈ [corpus_start, earliest_model_cutoff)
      a salient entity whose normalized surface matches a target alias
        (the §5.2 Phase R2 table)
      type compatibility: a company alias matches only company mentions,
        index↔index, sector↔sector
      effective-date check: a former name matched outside its alias
        effective range is downgraded to high-risk (needs R4 evidence)
    Optional recall booster: deterministic scan of raw CLS title/body for
      the target's securities code (catches mentions the entity extractor
      missed).
    Then split by event family:
      super_type == case.super_type  → candidate_pool[target, super_type]  (recurrence, §5)
      all event types                → candidate_pool[target]              (Target Salience, §3.3.2)
  No LLM cost. Rule-based.

Phase R4: Deterministic disambiguation (per E-6 — no LLM in the count path)
  Each candidate match is resolved by evidence tier, strongest first:
    1. exact securities / index code present in the article    → count
    2. official full name present                              → count
    3. low-risk alias, unique in the broader universe          → count
    4. high-risk alias + a disambiguating cue in the SAME       → count
       article (a matching code / full name, or type-consistent
       industry context for the intended entity)
    5. otherwise                                               → unresolved
                                                                 (NOT counted)
  Unresolved matches are logged (article_id, surface, candidate_ids, reason)
  for the §5.3 error audit. For a confirmatory factor a missed count is safer
  than a false count, so the rule is deliberately precision-first.
  No provider calls → no confirm-cache and no versioned-cache-key machinery
  (the v0.3 E-6 cache key is moot — there is nothing to cache).
  Cost: $0 (deterministic; no LLM).

Phase R5: Count compute — per C-3 + C-4 (C-2 dissolved by the §5.1 window change;
          E-7/S-5 dissolved — the C-3 continuous variable has no bin, hence no bin-flip)
  Per pilot case (ALL 430 cases — the fixed window makes recurrence
  computable for post-cutoff controls too, per §5.1):
    cls_family_recurrence[case_id]               = COUNT(confirmed_matches)
    log1p_recurrence_count[case_id]              = log1p(cls_family_recurrence)

  CONFIRMATORY analysis variable (v0.4 per C-3 — continuous log count,
  no percentile, no binary):
    log1p_recurrence_count[case_id]   # = log1p(cls_family_recurrence)
    # This is THE recurrence factor entering the analysis. It keeps the
    # absolute magnitude (the construct = "times the pattern was seen"),
    # on a diminishing-returns scale. The event-family base-rate confound
    # is handled by super_type already being a covariate in the analysis
    # model — no pre-residualizing percentile is needed.

  Sampling / n_eff bin (NOT confirmatory — v0.4 per C-3):
    recurrence_bin_within_supertype[case_id] =
      "high" if cls_family_recurrence >= median(cls_family_recurrence
               over cases of the SAME super_type in the eligible frame)
      else "low"
    # Used only for the plan §6.4 n_eff cell design and to drive
    # within-super_type stratified sampling: each super_type contributes
    # both high and low recurrence cases, so the sampled recurrence
    # variable is decorrelated from event type and the analysis can
    # cleanly separate the recurrence effect from the event-type effect.
    # A case flipping bins near the cutpoint only perturbs an n_eff cell
    # count by ±1; it does not touch the continuous confirmatory variable.
```

### 5.3 Smoke test — does LLM augmentation earn its place? (E-6 user review)

Phase R2-R4 above are fully deterministic. Before the main run a one-off smoke
checks whether an LLM still adds value, on a sample the user reviews by hand:

- **LLM alias generation.** On a stratified sample of ~30-50 targets, run an
  LLM alias-gen pass. The user manually reviews each LLM-proposed alias for
  correctness. Measure the **incremental recall** — how many additional true
  CLS mentions the LLM aliases catch over the master-data alias table — and the
  precision of those extra aliases.
- **LLM disambiguation.** On a sample of high-risk ambiguous matches, run an
  LLM yes/no pass alongside the deterministic Phase-R4 resolution. The user
  reviews ground truth; compare precision / recall.

**Decision rule.**
- If LLM aliases add material recall at acceptable precision → admit them as a
  human-reviewed **tier-3** in the alias table; each LLM alias is accepted only
  after user review (`source=llm_suggested_user_accepted`). Otherwise the
  master-data table is used alone and the LLM alias-gen prompt is not run in
  the main pipeline.
- Likewise, LLM disambiguation enters the main path only if it beats the
  deterministic Phase-R4 rule on the reviewed sample.

The smoke prompts (`ancillary/target_alias_gen_prompt.yaml`,
`ancillary/entity_confirm_prompt.yaml`) exist for this smoke only. The smoke
result + the decision are recorded in the WS0.5 closure notes.

### 5.4 Non-redundancy

- The confirmatory recurrence variable is `log1p_recurrence_count` (continuous, §5.2). Decorrelation from event type is handled two ways — within-super_type stratified sampling (the sampled recurrence variable is balanced within each super_type) and super_type as a covariate in the analysis model — not by pre-transforming recurrence into a percentile (per C-3)
- The no-dedup count is used directly; C-4 added no dedup sensitivity fields — an empirical probe found 0.48% intra-day CLS duplication (§5.1)
- Pre-manifest discriminant check is governed by §3.3.3 (per S-6): VIF on the four confirmatory factors + a 4×4 Pearson correlation matrix. `log1p_recurrence_count` × Target Salience is the pair most at risk (both are CLS counts of the target); a `max VIF ≥ 10` or `|r| ≥ 0.90` there triggers the §3.3.2 fallback

### 5.5 S4 discriminant check

The recurrence operationalization is settled: the confirmatory variable is the
continuous `log1p_recurrence_count` (per C-3). What remains for S4 is the
§3.3.3 discriminant report, run after pilot factor values are computed — it
checks `log1p_recurrence_count` against the other confirmatory factors. If
recurrence is too collinear with Target Salience (both are CLS counts of the
target; see §3.3.2), the registered §3.3.2 fallback applies (recompute Target
Salience on the complement family-set, or substitute a non-CLS proxy), recorded
in a v0.4-addendum decision.

### 5.6 CLS mirror provenance

```
cls_mirror_path: data/cls_telegraph_raw/  (this project, NOT D:\GitRepos\Thales\datasets\...)
cls_mirror_sha256: <computed from sorted-path concat of per-file sha256>
cls_mirror_snapshot_date: 2026-05-03 (per project memory)
cls_mirror_file_count: 2317
cls_mirror_size_bytes: 939_000_000 (approx; exact recorded at sha-compute time)
```

Locked in `factor_provenance.json` (§6).

## 6. Determinism via replay-from-cache (Issue #4)

`pilot_factor_values.parquet` is **NOT** assumed bit-stable across fresh V4 Pro
calls. v0.1's "deterministic given frozen prompts" is incorrect for closed-API
LLMs.

### 6.1 Replay-from-cache definition

Determinism is achieved by **caching every raw LLM response** and replaying the
deterministic post-processing (parse → collapse → count) over the cache.

**Two storage objects (v0.4 per E-8 + user review).** v0.2 estimated 12K
responses / 35-60 MB; but §5 Phase R1 runs topic classification over the full
CLS mirror (500K-1M calls). v0.3 sharded that into compressed JSONL plus a
separate `shard_index.parquet`, and leaned on E-10's `run_state.json` for
resume — three mechanisms doing one job. v0.4 collapses them into a single
**SQLite** database, which natively *is* the cache, the key index, and the
resume state:

```
data/factors/pilot_raw_responses.jsonl     # Tier A — committed (normal git)
data/cache/ws0_5_response_cache.sqlite     # Tier B — git-ignored, private Kaggle backup
```

- **Tier A — pilot raw responses** (`pilot_raw_responses.jsonl`): the 430
  pilot cases × 3 tasks ≈ 1290 records, ~5 MB. One JSONL, committed to
  **normal git** — not Git LFS (LFS is for large files; KB-scale records gain
  nothing from it). Committing it keeps `pilot_factor_values.parquet`
  independently replayable by anyone with the repo.
- **Tier B — full-CLS + auto-tune response cache**
  (`ws0_5_response_cache.sqlite`): 500K-1M+ records, ~1.5-5 GB. A SQLite DB
  (Python-stdlib `sqlite3` — no server, no dependency). The table *is* the
  cache; the primary key (`cls_item_id` / `case_id`) *is* the lookup index
  (no `shard_index.parquet`); a `SELECT` of completed ids *is* the resume
  state (a re-run does insert-or-ignore — no separate checkpoint file); WAL
  mode gives crash-safety. `data/cache/` is already git-ignored (the
  project's regenerable-API-cache directory) — no new ignore rule needed.

Per-record fields (same content in either store): `id`, `task`,
`prompt_template_path` + `prompt_template_git_sha`, `input_sha256`,
`rendered_prompt_sha256`, `response_text`, `response_id`, `model_snapshot`
(nullable — see below), `requested_model_slug`, `decoding_params`,
`request_timestamp`, `tokens_in`, `tokens_out`. Tier A additionally keeps the
full `prompt_sent` (pilot scale only); for Tier B the prompt is recovered by
re-rendering the template against the canonical input fields and verified
against `rendered_prompt_sha256`.

**`model_snapshot` nullability (per E-8).** Before S1, a provider smoke test
checks whether DeepSeek V4 Pro exposes a stable snapshot/fingerprint. If not,
`model_snapshot=null` + `model_snapshot_unavailable=true`, and traceability
relies on `response_id` + provider headers + request timestamp. Replay
determinism is then "same `response_text` for the same cache key," not "same
snapshot across runs."

### 6.2 factor_provenance.json (audit trail)

For each cell in `pilot_factor_values.parquet`:

```json
{
  "<case_id>": {
    "<factor_name>": {
      "value": "<computed value>",
      "source_raw_response": "pilot_raw_responses.jsonl#<id> | ws0_5_response_cache.sqlite:<id> | derived (for count-based factors)",
      "prompt_sha": "<git SHA of config/factors/*_v4pro.yaml>",
      "parser_version": "v1.0",
      "model_snapshot": "deepseek-v4-pro-<date>",
      "derived_from": "<upstream factor if any>",
      "transformation_sha": "<git SHA of collapse_map / scoring code>"
    }
  }
}
```

### 6.3 Replay script

`scripts/replay_factor_values.py` — reads the Tier-A pilot JSONL + the Tier-B
SQLite cache + frozen prompt configs + factor_schema.yaml; outputs
`pilot_factor_values.parquet` and `factor_provenance.json` **without re-calling
V4 Pro**.

**Reproducibility check (v0.3 per ML-engineer reviewer E-9).** Bit-identical
parquet across machines is fragile (pyarrow/pandas/compression library version
differences). v0.3 uses a **canonical row-content hash** as the primary
reproducibility check:

```python
canonical_table_hash = sha256(
    sort_rows(table, by=("case_id", "factor_name")),
    schema=frozen_schema,
    nulls_normalized=True,
    float_serialization="canonical"  # decimal repr, fixed precision
)
```

`scripts/replay_factor_values.py` writes `canonical_table_hash` into
`factor_provenance.json`; reproducibility is verified by hash equality. The
`canonical_table_hash` **is** the reproducibility guarantee — parquet
byte-identity is not pursued (it would only add a brittle library-version pin
for no analytical benefit).

**Missing-cache policy (v0.3 per E-9).** Confirmatory replay **hard-fails** on
any missing, corrupt, or hash-mismatched raw response (a duplicate is
structurally impossible — the Tier-B SQLite primary key prevents it). A
separate diagnostic mode `replay_factor_values.py --allow-missing` may write
incomplete artifacts for triage, but it **cannot overwrite** the committed
`pilot_factor_values.parquet`; it writes to `pilot_factor_values.partial.parquet`
with a separate provenance file.

### 6.4 Storage & backup

- **Tier A** (`data/factors/pilot_raw_responses.jsonl`, ~5 MB) — committed to
  normal git. Small, so no Git LFS (LFS is for large files, not KB-scale
  records).
- **Tier B** (`data/cache/ws0_5_response_cache.sqlite`, ~1.5-5 GB) —
  git-ignored (the existing `data/cache/` rule already covers it). It is a
  regenerable cache, so it does not travel with the repo; reproducibility
  travels through the committed artifacts (`cls_event_type_index.parquet`,
  `pilot_factor_values.parquet`, `factor_provenance.json`) plus sha-locks.
  An uncompressed SQLite of ~1M text records is ~3-5 GB; either store
  `response_text` as a per-row zstd blob (~1.5 GB) or accept the larger
  file — a local choice, not load-bearing.
- **Backup.** Re-running the full-CLS phase costs ~$200-400, so the Tier-B
  SQLite is backed up to a **private** Kaggle dataset (the free tier
  comfortably holds a 1.5-5 GB private dataset; `kaggle datasets version`
  for updates). The backup must stay **private** — the cache embeds
  财联社 article text, which is copyrighted. The backup's sha256 + upload
  date are recorded in `factor_provenance.json`.

No Git LFS is used anywhere in WS0.5: Tier A is small → normal git; Tier B is
git-ignored → private external backup. The v0.3 `ws0_5_storage_preflight.py`
LFS-quota preflight is **dropped** — there is no LFS quota to preflight.

## 7. Budget accounting + safety rails (Issue #8)

v0.1's "$5/factor cap" is replaced with token-and-USD accounting + safety rails
(not hard caps).

### 7.1 Metered DeepSeek client (per E-10 — replaces estimator + ledger)

Every WS0.5 V4 Pro call goes through one **metered client** in `src/` (a thin
wrapper over the existing DeepSeek client). On each call it reads `tokens_in` /
`tokens_out` from the API response and updates an in-process **meter** keyed by
`(task, phase)`, costing tokens at a pricing snapshot pinned once at run start.
This single object replaces the v0.3 dry-run estimator, the per-task JSONL
ledger, and the buffered ledger writer.

- **Estimation — no separate dry-run.** The smokes (§3.4, §5.3) and the
  auto-tune loops run at S1-S3, before the heavy S4 full-CLS phase; their
  metered calls *are* the real per-task token profile. The S4 full-CLS
  topic-classification budget is read straight off the T1 auto-tune meter
  (same frozen `topic_classification_v4pro.yaml`, same kind of CLS-item
  input — representative).
- **Safety rails.** The driver checks the meter's live running total against
  the expected spend:
  - `soft_limit_factor: 2.0` — 2× expected USD → warning + concurrency throttle
  - `hard_limit_factor: 5.0` — 5× expected USD → halt, require user resume
- **Pricing.** Snapshotted once at run start (DeepSeek V4 Pro official
  pricing); the snapshot date + the input/output rates go in the budget
  report header. No daily refresh, no pricing-epoch machinery — a WS0.5 run
  is days, not long enough for pricing to move.
- Cost is always computed from `actual_tokens_returned_by_api`, never from
  the pre-run estimate.

The §6.1 SQLite response cache independently stores `tokens_in` / `tokens_out`
on every record, so a post-hoc audit can cross-check the meter — but the meter,
not the cache, is the primary budget mechanism.

### 7.2 Budget report

`scripts/budget_summary.py` dumps the meter at run end: per-task and overall
USD / tokens, breakdown by phase, and comparison to the expected spend.
Markdown report at `data/factors/budget_summary_report.md` — committed, as the
closure record of actual WS0.5 spend.

### 7.3 Lightweight checkpoint

The auto-tune loop (§4) is short — at most `max_rounds` (default 10) rounds,
each a handful of API calls plus a `dev` evaluation — so it does not need a
sophisticated resume protocol. After each round the driver writes a small
checkpoint `data/factors/tuning_logs/<task>_checkpoint.json`:

```json
{
  "task": "topic_classification",
  "config_sha": "<git sha of <task>_autotune_config.yaml>",
  "round_idx": <int>,
  "incumbent_prompt_sha": "<sha of current best prompt>",
  "incumbent_dev_score": <float>,
  "budget_totals_USD": <float>,
  "last_checkpoint_at": "ISO8601"
}
```

If the loop is interrupted (crash or hard budget-rail halt), restarting
re-reads the checkpoint and resumes from the next round; at most one round is
lost, and the meter restarts from `budget_totals_USD`. The heavy
`pilot_factor_inference` / full-CLS phases need no checkpoint of their own —
the §6.1 SQLite cache is itself the resume state (a re-run skips ids already
present).

## 8. Deliverables

```
docs/
  DECISION_20260518_ws0_5_thales_alignment.md   # this memo

config/factors/
  topic_classification_v4pro.yaml               # T1 frozen prompt + collapse_map + thresholds
  entity_extraction_v4pro.yaml                  # T2 frozen prompt + thresholds
  signal_profile_v4pro.yaml                     # T3 frozen (V2 combined OR v5.5 two-pass, decided post-smoke)
  ancillary/
    target_alias_gen_prompt.yaml                # §5.3 smoke only — NOT in the deterministic main pipeline
    entity_confirm_prompt.yaml                  # §5.3 smoke only — NOT in the deterministic main pipeline
  
  factor_schema.yaml                            # all factor names, dtypes, binning, collapse maps
  author_authority_mapping.json                 # T3 Track B (if author coverage ≥ 80%; else documented absence)
  
  topic_classification_autotune_config.yaml     # §4 auto-tune pre-reg config
  entity_extraction_autotune_config.yaml
  signal_profile_autotune_config.yaml

scripts/
  ws0_5_cls_author_coverage.py                  # T3 Track B coverage probe
  build_target_alias_table.py                   # E-6; AKShare master data → tiered target_aliases.json
  ws0_5_auto_tune_loop.py                       # §4 train/dev/test auto-tune driver
  ws0_5_discriminant_report.py                  # S-6; VIF (4 factors) + 4×4 Pearson correlation matrix
  replay_factor_values.py                       # raw_responses → parquet (no API calls); canonical row-hash + hard-fail-on-missing per E-9
  budget_summary.py                             # E-10; dumps the §7.1 meter → markdown report
  check_pilot_cells.py                          # WS0.5 stub; WS4 full implementation
  ws0_5_compute_pilot_factors.py                # orchestrator: pilot 430-case factor inference

data/factors/
  pilot_factor_values.parquet                   # final factor table for WS4/WS5
  factor_provenance.json                        # per-cell audit trail + canonical_table_hash (v0.3 per E-9)
  ws0_5_quota_report.json                       # plan §6.3 + §6.4 quota check report
  ws0_5_discriminant_report.json                # S-6; VIF (4 factors) + 4×4 Pearson correlation matrix + verdict
  pilot_raw_responses.jsonl                     # E-8; Tier-A pilot raw responses (~5 MB, normal git)
  # Tier-B response cache lives OUTSIDE data/factors, git-ignored:
  #   data/cache/ws0_5_response_cache.sqlite — full-CLS + auto-tune raw responses
  #   (~1.5-5 GB; SQLite; private Kaggle dataset backup; sha in factor_provenance.json)
  
  cls_event_type_index.parquet                  # full-CLS event_type labels
  akshare_master_snapshot/                      # E-6; pull-date-stamped AKShare master data (alias-table source)
  target_aliases.json                           # E-6; tiered alias table built from AKShare master data (§5.2 R2)
  tuning_logs/
    <task>_tuning_log.jsonl                     # per-round auto-tune log (candidate prompts + dev scores + final test score)
    <task>_checkpoint.json                      # lightweight per-round checkpoint (§7.3)
  budget_summary_report.md                      # E-10; budget report dumped from the §7.1 meter

related papers/
  INDEX.md                                      # tracked paper index; per-direction synthesis notes in notes/
```

## 9. Closure conditions for WS0.5

WS0.5 closes when **ALL** of:

1. This memo signed (v0.2 → Codex round-1 → v0.3 → Codex round-2 → v0.4 §4 simplification → 14-issue round-1/2 review → user sign-off)
2. Three frozen prompt configs committed (T1 topic, T2 entity, T3 signal_profile)
3. Target alias table (`target_aliases.json`) built from the AKShare master snapshot committed; §5.3 LLM-augmentation smoke run and its admit/reject decision recorded
4. T3 Track B coverage report committed; mapping table OR documented abandonment
5. For each of the 3 tasks: `<task>_autotune_config.yaml` committed; `<task>_tuning_log.jsonl` shows the loop terminated (dev score reached `target_threshold`, or plateau, or `max_rounds`); the final sealed-`test` score is recorded as the official threshold result (§4)
6. **`pilot_factor_values.parquet` reproducible from the Tier-A pilot JSONL + Tier-B SQLite cache + frozen code SHAs** (Issue #4); reproducibility verified via `canonical_table_hash` (v0.3 per E-9); confirmatory replay hard-fails on missing/corrupt cache
7. **`factor_schema.yaml` committed** — factor names, dtypes, binning/collapse rules, EventType → super_type mapping, missing-value policy, perturbation-eligibility fields, the Target Salience field (`target_salience` = `log1p` of pre-cutoff all-event-type CLS mention count, §3.3.2) + the §3.3.1 centrality-gate threshold, the recurrence confirmatory variable `log1p_recurrence_count` + its non-confirmatory within-super_type sampling bin (§5.2) (Issue #5 + v0.3 patches)
8. **`data/factors/ws0_5_quota_report.json` committed** — plan §6.3 quotas + §6.4 n_eff target/min counts + C_FO funnel + C_NoOp host coverage + post-cutoff mix preservation (Issue #5)
9. **`scripts/check_pilot_cells.py` committed at spec+stub level** — function signature + IO schema + check-logic pseudocode in docstring; WS4 implements (Issue #5)
10. **`data/factors/ws0_5_discriminant_report.json` committed** — VIF on the four confirmatory factors + a 4×4 Pearson correlation matrix + the max-VIF go / sensitivity / revise verdict (per S-6)
11. **Tier-B response cache (`data/cache/ws0_5_response_cache.sqlite`) built and backed up** to a private Kaggle dataset; its sha256 + the backup upload date recorded in `factor_provenance.json` (per E-8)
12. Plan §5.1A WS0.5 section updated from "scope TBD" to one-paragraph pointer at this memo + factor_schema.yaml path
13. `budget_summary_report.md` committed — actual WS0.5 spend (dumped from the §7.1 meter), per task/phase, vs the expected spend; pricing snapshot date + rates in the report header (per E-10)
14. PENDING.md "WS0.5 — Thales alignment design" moved to Recently closed; plan §14.4 sign-off checklist WS0.5 row ticked ✓

## 10. Schedule

| Session | Deliverables |
|---|---|
| **S0 (2026-05-18/20)** | v0.1 → Codex round-0 → 9-issue interactive review → v0.2 → Codex round-1 → v0.3 → Codex round-2 → **v0.4 (user simplification of §4)** |
| **S1** | T3 Track B author-coverage probe; T1 topic_classification auto-tune (§4 train/dev/test loop) |
| **S2** | T2 entity_extraction auto-tune (§4 loop) |
| **S3** | T3 Track A signal_profile: 3-arm smoke comparison (V2 combined / v5.5 conditioned / independent two-pass) → winner → auto-tune; opportunistic Authority tuning if session time |
| **S4** | Phase R1-R5 recurrence pipeline (full-CLS topic class + AKShare alias table + §5.3 LLM-augmentation smoke + entity matching + count compute); pilot 430-case factor inference; replay → parquet + provenance |
| **S5** | Plan §5.1A update + sign-off + §14.4 checklist tick + commit |

S1-S3 can overlap with V4 Pro concurrency parallelism. S4 strictly sequential
after S1-S3 prompts frozen.

## 11. Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-W05-1 | V4 Pro behavior diverges materially from deepseek-chat → starting prompts regress | §4 auto-tune `dev`-set scoring catches it each round; if the round-1 `dev` score is far below `target_threshold`, halt and reconsider the starting prompt |
| R-W05-2 | Salience-tier output from heavy entity prompt fragile under V4 Pro | MVP entity output (value, type) sufficient; salience as bonus that fails open |
| R-W05-3 | Tuning overfits to the evaluation data → reported metric is inflated | §4 sealed `test` split, evaluated exactly once at the end; `dev` reuse only affects which prompt is chosen, never the reported number; stopping rule pre-committed in `<task>_autotune_config.yaml` |
| R-W05-4 | sector_industry < 12 verified+slotable for C_FO | Hard quota oversample at sampling; trigger Scheme B 4-super_type fallback if persists |
| R-W05-5 | Author coverage < 80% → Track B abandoned | Track A alone covers Authority operationalization; abandonment is documented limitation, not closure blocker |
| R-W05-6 | Recurrence reference window topic-classification cost overrun | Full-CLS cost ~$200-400 within token plan; soft 2× / hard 5× safety rail catches accidents |
| R-W05-7 | Thales summary entity fixture too small (80) for V4 Pro calibration | Grow to ~2000 via Claude+Codex dual-agent labeling before the §4 loop runs |
| R-W05-8 | Recurrence operationalization (percentile-binary vs continuous count) contested | Resolved per C-3 — the confirmatory variable is the continuous `log1p_recurrence_count`; there is no binarization left to challenge |
| R-W05-9 | 3-arm signal_profile smoke (§3.4) ties within ±2% modality | Decision rule deterministic; document tie-breaking choice in memo addendum if triggered |
| R-W05-10 | Signal profile two-pass nominally selected but Authority post-tune doesn't gain | Authority opportunistic-tune; not a closure gate |

## 12. Open items / future-session pointers

- KG-lookup / Wikipedia Authority for true extra-corpus operationalization → P1-expansion track, separate memo
- Bloc 3 Event Phase / Session Timing operationalization → WS0.5 closure addendum after S4
- Production entity-pipeline rework integration → re-evaluate prompt swap for main run (NOT pilot)

## 13. Sign-off

- Author: Claude Code orchestrator, 2026-05-18 (v0.1) / 2026-05-19 (v0.2 + v0.3) / 2026-05-20 (v0.4 + 14-issue review), interactive review session with user
- v0.1 review: Codex round-0, MAJOR-REVISIONS-NEEDED, 9 issues identified
- v0.2 status: 9 round-0 issues resolved per user-Claude interactive decision
- v0.2 review: Codex round-1 (3 parallel reviewers, 2026-05-19) — ALL three returned MAJOR-REVISIONS-NEEDED:
  - ML Engineer (`temp/ws0_5_round1_ml_engineer_review.md`, 10 critical issues E-1 to E-10)
  - Statistician (`temp/ws0_5_round1_statistician_review.md`, 8 critical issues S-1 to S-8)
  - Measurement / Construct Validity (`temp/ws0_5_round1_measurement_review.md`, 5 critical issues C-1 to C-5)
  - No cross-role conflict; patches complementary
- v0.3 status: all 23 round-1 critical issues patched (see frontmatter revision_basis); round-2 re-review completed 2026-05-19
- v0.3 review: Codex round-2 (3 parallel reviewers, 2026-05-19):
  - Measurement: APPROVE (clean)
  - ML Engineer: APPROVE-WITH-MINOR-PATCHES (2 narrow text patches — applied in-place: §4.1 MDE q-grid wording, §5.2 R4 cache lookup key)
  - Statistician: APPROVE-WITH-MINOR-PATCHES (1 patch, same root concern as ML-engineer's E-1 — resolved by the same in-place patch)
  - Per runbook §5: ≥2 APPROVE-WITH-MINOR-PATCHES → minor patches applied to v0.3, no round-3 needed
- v0.4 (2026-05-20): user-directed simplification of §4. The Codex reviewers (round-0 → round-2) progressively built a heavy "Scheme Y" auto-tune framework (limited-exposure Ladder gate, paired McNemar / permutation tests, cross-task alpha spending, MDE preflight, 7-way fixture split, manifest lock, run-state resume). The user judged this over-engineered: a prompt is a measurement instrument, and the per-round accept decision is an optimization step, not a confirmatory statistical claim. v0.4 replaces §4 with a plain train/dev/test split — tune on `train`, rank candidates on `dev`, evaluate the final prompt once on a sealed `test` split. This keeps the only protection that matters (sealed test set, used once) and drops the rest. v0.4 supersedes round-1 issues E-1, E-2, E-3, E-4, S-1, S-2, S-3, S-4, S-7 (all §4-machinery patches now moot). Round-1/round-2 issues outside §4 (recurrence pipeline, replay cache, budget, Target Salience / recurrence construct) are unaffected and remain in force.
- v0.4 NOT Codex-re-reviewed: the change removes machinery and adds no new claim; a train/dev/test split has minimal failure surface. User is the decision authority here.
- v0.4 continued review (2026-05-20): the 14 non-§4 round-1/2 issues (C-1..C-5, E-5..E-10, S-5/S-6/S-8) were reviewed with the user issue-by-issue. All 14 resolved — 10 produced memo edits (C-1..C-5, E-6, E-8, E-9, E-10, S-6), 3 dissolved as byproducts of the C-2/C-3 changes (E-5, E-7, S-5), 1 confirmed already-resolved (S-8). Two Codex literature reviews were commissioned (E-6 entity disambiguation, S-6 collinearity diagnostics; reports in `temp/`, papers in `related papers/`). Every issue was confirmed or net-simplified — no reviewer-driven heavyweight mechanism survived. NOT Codex-re-reviewed: the review removed machinery and tightened construct claims, adding no new statistical claim. Per-issue detail in frontmatter `revision_basis` 'v0.4 cont.'.
- User sign-off: pending
- Plan §5.1A update: pending S5
