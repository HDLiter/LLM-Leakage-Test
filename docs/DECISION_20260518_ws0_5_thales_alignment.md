---
title: WS0.5 Thales Alignment — Reuse-vs-Rebuild Decision, Auto-Tune Loop, and Factor Pipeline Spec
date: 2026-05-18
revision: v0.3
revision_date: 2026-05-19
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
status: v0.3 — APPROVED after round-2 (minor in-place patches applied); awaiting user sign-off + WS0.5 closure
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
R5A pilot cases plus a 24-month recurrence reference window — and as decided in
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
| Target Salience | 2 (prominence) | case-level ordinal | target selection + ordinal salience score | **T2** for target selection; market metadata for ordinal |
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
| Target threshold | `primary_accuracy ≥ 0.78` on final_holdout (V6 SLM 0.738; V4 Pro expected exceed) |
| Tune scope | Boundary-rule additions and few-shot examples only; no taxonomy changes |
| Scheme B fallback (4 super-types) | Trigger: `sector_industry` cannot reach 12 verified+slotable C_FO cases OR `issuer_quant` < 12 after sampling. Bridge: `reported_numbers` [EARNINGS+INDICATOR+INDUSTRY], `market_security` [TRADING+OWNERSHIP] with class-conditional host bridge |

### 3.2 T2 — Entity extraction: REUSE Thales summary entity prompt, V4 Pro auto-tune

| Item | Decision |
|---|---|
| Prompt template | Reuse `labeling_prompt_entity.md` 4-stage pipeline verbatim |
| Output schema | `RawSalienceLabel` with `value` / `type` / `salience` / `reason` |
| Consumed downstream | `(value, type)` for recurrence (§5); `salience=core` as candidate target signal for §3.3 selection rule |
| Calibration fixture | `quality_summary_pilot.json` (80 adjudicated items) as starting fixture; expand to 3000 via Scheme Y active fixture growth (§4) |
| Target thresholds | core-entity precision ≥ 0.85, recall ≥ 0.85 |

### 3.3 Bloc 2 — Target Salience construct (NEW, Issue #2)

Target is a **manifest INPUT** to `P_predict`, not LLM-inferred at operator time
(per `R5A_OPERATOR_SCHEMA.md` line 81). WS0.5 must produce a deterministic target
selection rule + ordinal salience score at sampling/manifest-freeze time.

**Construct claim (narrowed in v0.3 per measurement reviewer C-1).** Target
Salience is operationalized as a **selected-market-target reach composite**. It
proxies expected pretraining exposure to the *forecastable* target, not pure
cross-corpus fame independent of tradability, scope, or target-selection
validity. `context_gate` is a **target-validity safeguard**: cases with weak
target validity are flagged (`target_validity_low=true`) and gated, but the
ordinal score itself reflects market-reach magnitude. Raw component fields
(`listed_flag`, `index_membership`, `market_cap_bucket`, `scope_class`,
`target_family`) used to derive `static_reach` are retained on the factor table
for sensitivity checks (see §8 `factor_schema.yaml` deliverables).

#### 3.3.1 Target selection rule

```python
def select_target(article, salient_entities, market_metadata):
    # 1. Build candidate pool
    candidates = []
    for e in salient_entities:
        if e.salience != "core":                     continue   # only core
        if e.type not in {"company", "sector",
                          "index", "ETF", "commodity"}: continue # tradable types only
        if is_source_only_attribution(e):            continue   # 中信建投: → drop
        if is_pure_person_without_org(e):            continue   # CEO standalone → drop
        if is_one_char_region_alias(e):              continue   # 中/俄 if full alias exists
        candidates.append(e)
    
    if not candidates:
        return NullTarget("no_eligible_tradable_target")   # case sampling rejected
    
    # 2. Within candidate pool — centrality-first selection (Issue #2 user override of Codex class-first)
    selected = max(candidates, key=lambda c: (
        c.in_headline,
        c.is_core,
        -c.first_offset,
        c.mention_count,
        len(c.value),  # longer alias preferred for disambiguation
    ))
    
    return Target(
        target=selected.display_name,
        target_type=map_target_type(selected),  # ∈ {company, sector, index}
        target_ticker=selected.metadata.get("ticker"),  # sidecar for listed companies
        target_source_entity=selected.value,
        target_selection_confidence=confidence(selected, candidates),
    )
```

**Macro / policy cases with no tradable target are REJECTED at sampling stage**
(`null_no_eligible_tradable_target`), not retained with target_type=macro. Plan
§6.3 host quota (`policy` ≥ 15, `macro` ≥ 15) is filled by sector/index targets
under macro-themed articles, not by macro-target cases.

#### 3.3.2 Ordinal salience scoring (3-level)

```
context_gate ∈ {0,1,2}   # target-validity gate (v0.3: flag, not score driver)
static_reach ∈ {1,2,3}   # market-reach magnitude (ordinal categories, NOT interval dose)

# v0.3 semantics (measurement reviewer C-1 patch):
target_validity_low = (context_gate == 0)     # case is flagged; analysis treats
                                              # it as low-confidence target, not as
                                              # low-exposure target
ordinal_admitted =                            # ordinal computed only for admitted cases
    3 (high)   if static_reach == 3
    2 (medium) if static_reach == 2
    1 (low)    if static_reach == 1
ordinal_reported = ordinal_admitted if not target_validity_low else NA   # main analysis
```

`static_reach` is an **ordinal category, not an interval-scale dose**. The 2/3
boundary is well-anchored (SSE50/CSI300/top-cap vs ordinary listed). The 1/2
boundary is heterogeneous (small-cap listed, unlisted local, narrow products,
local institutions). The factor table retains raw components so that paper
sensitivity analyses can recompute alternative reach scores without re-labeling.

`static_reach` mapping by target family:

| Family | static_reach=3 | static_reach=2 | static_reach=1 |
|---|---|---|---|
| Company | SSE50 / CSI300 / top-cap 国民级 | 普通 listed / CSI500 / 大型未上市 | 小盘 / unlisted / 地方 |
| Index/ETF | 宽基指数 / 全市场 ETF | 行业 / 主题 ETF | 窄基金 |
| Sector | 主流正式行业 / 主导主题 | 申万/CSRC 行业 / 商品 | 窄产品 / 业务段 |

**Class 1 (security) vs class 2 (sector) sub-division** intentionally NOT defined
in v0.2 — defer to pilot results + Codex v0.2 review.

#### 3.3.3 Construct validity & non-redundancy

- Target Salience proxies **expected pretraining exposure to the selected forecastable target**, not in-article text salience or pure fame independent of tradability/scope
- Text-local signals (title presence, mention count) are only the `context_gate` (target-validity flag); they cannot promote ordinal alone, and `context_gate=0` triggers `target_validity_low=true` (flag), not automatic low ordinal (per C-1)
- Tradability Tier and Target Scope are absorbed into `static_reach`, not separate confirmatory factors; their raw components are retained for sensitivity (per C-1)
- Discriminant rule: no historical CLS mention count / no event_type / no month encoded in Target Salience (those belong to Historical Family Recurrence §5)

**Discriminant-diagnostics report (v0.3 expansion per statistician reviewer S-6).**
The pre-manifest-freeze discriminant check is **not** a single marginal Spearman
between Target Salience and Recurrence. WS0.5 emits a full report over **all six
confirmatory pairs** among Cutoff Exposure, Historical Family Recurrence, Target
Salience, and Template Rigidity:

| Diagnostic | What it computes | Trigger |
|---|---|---|
| Marginal Spearman ρ | per pair, ordinal/continuous as appropriate | report all; `|ρ| > 0.65` triggers resample-or-rebin |
| Partial / residual correlation | per pair, controlling for super_type, host category, event-date window (where applicable) | `|partial ρ| > 0.50` triggers inspect; `> 0.65` → resample |
| Scaled fixed-effect design VIF / GVIF | on the scaled mixed-model design matrix (NOT OLS-only) | `GVIF^(1/(2·df)) > 2` triggers inspect |
| Condition number | of centered/scaled fixed-effect design matrix | `> 30` triggers inspect |
| Mixed-model singularity / convergence | random-effect singularity, BLUP shrinkage, REML convergence | any singular / non-converged stratum triggers redesign signal |

**Timing** (clarified per S-6): the check runs **after candidate sampling AND
after factor-value computation** (S4), **before pilot manifest freeze** and
before any main analysis. Cutoff Exposure correlations are must-report; if high,
trigger date-stratified rebalance or explicit model adjustment rather than
silent resampling (Cutoff is non-modifiable at sampling time once dates are
fixed).

Same-level modifiable factor pairs (Target Salience × Recurrence, Target Salience
× Template Rigidity, Recurrence × Template Rigidity) follow `> 0.65` →
resample-or-rebin. The discriminant report is committed at
`data/factors/ws0_5_discriminant_report.json`; failures must be signed-off with
a v0.3-addendum decision memo before sampling proceeds.

#### 3.3.4 Market metadata snapshot dependency

Scheme A `static_reach` requires market metadata (market cap bucket, index membership,
institution registry). Deliverable: `config/factors/r5a_market_metadata_snapshot.json`
+ `scripts/build_market_metadata_snapshot.py`. Data source: user-built (not Thales
quant engine), Tushare/AKShare/CSRC official lists, frozen pre-pilot. Implementation
deferred to S1 session.

**Scheme B fallback (text-only)**: if metadata snapshot blocks manifest freeze or
> 20% of company targets are metadata-missing, switch to text-only Scheme B
(weaker construct, accepted as documented limitation).

### 3.4 Bloc 3 — Disclosure Regime/Modality + Authority (T3 Track A — Issue #6 smoke comparison)

Because v0.1's "V2 single-pass / 0.815 modality" claim is stale (Issue #6), v0.2
does **not** prematurely lock a single starting prompt. Instead:

**Stage 1 (smoke comparison)**: On a 100-case stratified subset of the 3000-case
auto-tune fixture, run both architectures × 1 V4 Pro round:
- `signal_profile_v2_combined.yaml` (archived V2 single-pass, ported from Thales archive)
- `signal_profile_v55_twopass.yaml` (current Thales v5.5 two-pass — modality prompt + authority prompt)

**Decision rule**:
- If `modality_acc_A ≥ modality_acc_B - 0.02` → pick V2 combined (modality occupies confirmatory factor; single-pass is cheaper)
- Otherwise → pick v5.5 two-pass

**Stage 2 (auto-tune)**: Winner enters Scheme Y loop with threshold `modality_top_1 ≥ 0.82` on final_holdout.

**Authority handling (Issue #9)**:
- Authority is NOT a confirmatory factor; it is a Bloc 3 candidate adjunct/covariate
- Authority metric reported but does not gate auto-tune termination
- Opportunistic tuning: after modality auto-tune converges, if session time permits, run a short Authority-only auto-tune; otherwise ship Authority as-is (V2 baseline 0.76, expected V4 Pro improvement modest)

**v5.5 conditioning caveat (v0.3 per measurement reviewer C-5).** If the
Stage-1 smoke comparison selects v5.5 two-pass, **Authority is measured
conditional on predicted Modality**, not as an independently observed case
attribute. Paper language must therefore treat Authority as a descriptive
covariate/adjunct under v5.5, not as a separately measured Bloc 3 dimension.
Any future elevation of Authority to a confirmatory or interaction role
requires an **independent** authority operationalization (independent text
inference, publisher metadata via Track B, or KG/Wikipedia lookup deferred to
P1-expansion). The smoke-comparison report records which architecture was
selected and the resulting independence-status of Authority.

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

## 4. Auto-Tune Loop — Scheme Y (Issue #3)

Per `temp/ws0_5_autotune_sota_search.md`, v0.1's Claude+Codex 2-patch + bootstrap-CI-
non-overlap gate is statistically incorrect (paired data ignored), reuses holdouts
adaptively, and accumulates type-I error across rounds. v0.2 adopts **Scheme Y —
limited-exposure acceptance gate + multi-source candidate pool + paired statistical
tests + alpha spending + active fixture growth**.

### 4.1 Loop algorithm

```
inputs:
  initial_prompt          ← Thales prompt verbatim (per §3.1 / §3.2 / §3.4 winner)
  fixture_total = 3000    ← Codex + Claude dual-agent labeled, user-adjudicated on disagreements

fixture splits (random seed pinned in manifest):
  train_visible       50%   (1500 items) — proposers see errors here       — active-sampled
  challenge_dev       10%   ( 300 items) — boundary/hotspot diagnostic     — active-sampled
  random_inner_dev    10%   ( 300 items) — unbiased ranking sample         — stratified random
  acceptance_holdout  10%   ( 300 items) — Ladder gate                     — stratified random, sealed
  final_holdout       10%   ( 300 items) — touched once at end             — stratified random, sealed
  anchor_dev           5%   ( 150 items) — fixed cross-rotation monitor    — stratified random, NEVER tuned-against
  reserve              5%   ( 150 items) — for active-sampling refill into train/challenge — stratified random

(v0.3 per S-4 + E-2: active-sampling is restricted to `train_visible` and
`challenge_dev`. Population-estimator pools — `random_inner_dev`,
`acceptance_holdout`, `final_holdout`, `anchor_dev` — are independently
stratified random samples from the target evaluation distribution. The driver
maintains a split manifest with immutable `item_id`, `input_sha256`, `split`
fields; every active-sampling refill MUST assert no overlap with any sealed pool
or with prior sealed rows.)

rotation:
  K = 5 rounds per rotation
  rotate: train_visible + challenge_dev only (active sampling recipe below)
  do NOT rotate: random_inner_dev, acceptance_holdout, final_holdout, anchor_dev

active sampling recipe (per rotation, applied to train_visible + challenge_dev):
  40% stratified random (unbiased base, drawn from reserve)
  25% Claude/Codex/current-prompt 3-way disagreement (boundary cases)
  20% current-prompt high-confidence error (hotspot)
  15% embedding-cluster diversity + rare-label coverage

proposer isolation rule (v0.3 per E-2):
  Scheme Y proposers are API-only calls with sanitized train payloads. They
  receive: (a) error summaries from `train_visible` and (b) the current prompt.
  They DO NOT receive: any item from `random_inner_dev`, `challenge_dev`,
  `acceptance_holdout`, `final_holdout`, or `anchor_dev`; nor any scored
  metric except the binary predicates defined below; nor any per-example
  per-look breakdown. Workspace-aware sub-agent proposers are forbidden;
  proposer payload SHA is logged per candidate.

candidates per round (4) — candidate contract (v0.3 per E-3):
  Each candidate writes `candidate.yaml` with:
    {source, base_prompt_sha, changed_sections, diff_sha,
     rationale, payload_sha}

  candidate_1 = Claude_free_form_patch(train_errors, current_prompt)
  candidate_2 = Codex_free_form_patch(train_errors, current_prompt)
  candidate_3 = ProTeGi_style_patch(train_minibatch_errors, current_prompt)
              # Two-artifact flow: emit `diagnosis.json` (errors → root
              # causes) on the train minibatch FIRST, then emit `patch.diff`
              # conditioned only on the diagnosis + allowed prompt sections.
  candidate_4 = minimal_edit_patch(train_errors, current_prompt)
              # Enforced by diff validator: ≤ 2 changed semantic prompt
              # lines, ≤ 1 added few-shot example, no schema/output-key
              # changes. Reject-before-scoring on violation.

selection pipeline (per round):
  4 candidates → train minibatch guardrail filter (cheap, NOT a ranker)
                   - drops only schema-breaking / parse-failing / grossly
                     regressing candidates
                   - fixed stratified minibatch size; no aggressive ranking
  → 2-3 ranked on `random_inner_dev` (unbiased estimator);
     `challenge_dev` reported as secondary diagnostic; weighting rule
     recorded in manifest
  → 1 finalist submitted to acceptance_holdout

acceptance gate (Ladder-style limited-exposure):
  paired test (per metric type):
    top-1 accuracy (topic / modality): exact McNemar on discordant pairs,
      one-sided superiority (candidate > incumbent), pre-registered direction
    F1-style aggregate (entity recall / F1):
      PRIMARY (the gate)   = paired permutation/randomization test on the
                             pre-registered primary metric, resampling at the
                             article-fixture-cluster unit, one-sided
      DESCRIPTIVE (reported, not a gate) = paired article-cluster bootstrap
                             difference CI
      averaging: micro-F1 over core entities is primary unless the manifest
                 explicitly declares a macro-F1 and verifies minimum
                 per-stratum counts (rare-stratum macro is diagnostic only)

  effect-size calibration (v0.3 per E-1 + S-1 + MDE preflight):
    delta_min_practical (per task) = minimum practical effect floor:
      topic_classification: 0.02 primary_accuracy points
      entity_extraction:    0.02 core-entity F1
      signal_profile:       0.02 modality top-1
    delta_detectable_planning (per task) = MDE under acceptance_holdout_n
      and per-task alpha schedule; computed at run start (see preflight
      below). v0.3 does NOT claim that 0.02 is detectable at n=300 +
      alpha=0.00167; it is a practical floor, not a statistical claim.

  MDE preflight (v0.3 per E-1 + S-1; clarified per round-2 minor patch) —
  runs before any acceptance query:
    1. For paired tests (McNemar for top-1, paired permutation for F1),
       discordance `q = b + c` (or paired SD for F1) is a candidate-vs-
       incumbent quantity. It is NOT identifiable from the incumbent
       prompt alone. The preflight therefore uses a pre-registered
       grid OR, when available, prior candidate-vs-incumbent evidence:
         - Default top-1 q-grid: q ∈ {0.05, 0.10, 0.20}
         - Default F1 paired-SD grid: pre-registered task-specific 3-point grid
         - Refinement: after first acceptance look (or from smoke
           candidates on `random_inner_dev`), append observed
           candidate-vs-incumbent q / paired-SD as empirical estimates
       The run-start go/no-go verdict is based on the pre-registered
       grid. `mde_report.json` must NEVER label the incumbent-only error
       rate as paired candidate-vs-incumbent discordance.
    2. Compute MDE at each grid point for the planned
       (acceptance_holdout_n, per_look_alpha, 80% power). The
       per_look_alpha used here is the POST-ALLOCATION value after S-2
       cross-task allocation (≈ 0.000556 = 0.0167 / 30 per task under
       `alpha_family_scope: all_ws0_5_prompt_tuning_tasks`), NOT
       v0.2's task-local 0.00167. For top-1:
         MDE ≈ (z_α + z_0.80) · √(q / n)
       evaluated at each grid q.
    3. Write `data/factors/tuning_runs/<run_id>/mde_report.json` with
       the planning method (grid / prior / empirical), per_look_alpha
       used, per-grid-point MDE, and a go/no-go verdict.
    4. If `MDE > delta_min_practical` at the lower-q grid point: the
       run may PROCEED but records the gate as conservative (real
       0.02-0.05 improvements may fail acceptance — plateau is then a
       power issue, not a true no-improvement signal). Escalation
       options: (i) enlarge acceptance_holdout (re-split required,
       manifest revision); (ii) raise delta_min to MDE; (iii) document
       gate as conservative.
    5. If `MDE > 0.10` at all grid points: the run STOPS. The design
       cannot detect any reasonable improvement and a new manifest is
       required.

  acceptance condition (per look):
    candidate's paired metric vs incumbent on acceptance_holdout passes BOTH:
      (i)  practical effect: observed delta ≥ delta_min_practical
      (ii) statistical:      paired test p < per_look_alpha
                             (one-sided superiority)

  output to proposers — BINARY PREDICATES ONLY (v0.3 per E-2 + S-7):
    Proposers see one of:
      "fail"
      "pass_delta_min"
      "pass_above_target_threshold"
    Exact metrics, rounded deltas, and per-example breakdowns are written
    to the private tuning log for audit only. Proposers receive no
    numeric scalar feedback. The driver dedupes candidates by
    `candidate_sha`; near-duplicate resubmissions of failed candidates
    are rejected.

termination:
  threshold_converged: incumbent on acceptance_holdout passes
                       "pass_above_target_threshold" per §3.1/§3.2/§3.4
  plateau: 2 consecutive rotations with zero accepted candidates
           (failed acceptance queries still spend alpha looks)
  global cap: max_acceptance_looks per task (see §4.2) OR 4 rotations

max-look exhaustion stop rule (v0.3 per E-4):
  If max_acceptance_looks is reached without convergence, the run STOPS.
  Continuing under the same manifest is invalid. The next action must be
  one of:
    (a) ship incumbent with documented plateau in `mde_report.json`
        and `tuning_log.jsonl`; or
    (b) open a new decision memo + new manifest + new sealed holdouts
        (no reuse of the exhausted acceptance_holdout); or
    (c) re-build the fixture with new sealed holdouts via re-labeling
        + re-split.

manifest lock (v0.3 per E-4):
  At run start, `ws0_5_auto_tune_loop.py`:
    1. requires the source manifest to have NO uncommitted changes;
    2. copies it to `data/factors/tuning_runs/<run_id>/manifest.lock.yaml`;
    3. records `manifest_sha256` + `manifest_git_commit`;
    4. aborts if the on-disk manifest hash changes during the run.
  All tuning log rows carry the same `run_id` + `manifest_sha256` +
  `manifest_git_commit`; CI verifies this invariant.

post-termination:
  Evaluate winning prompt once on final_holdout
  Report final_holdout metric as the official threshold result (one-time CI)
  anchor_dev metric reported alongside as a trend reference (never tuned-against)
  If final_holdout metric < target_threshold by > delta_min_practical:
    documented limitation, not blocker
```

### 4.2 Pre-registration manifest

Before any loop runs, commit `config/factors/<task>_autotune_manifest.yaml`.
v0.3 (per statistician reviewer S-2) makes alpha-family scope explicit across
the three tasks:

```yaml
factor_task: topic_classification     # or entity_extraction, signal_profile
fixture_seed: <pinned>
fixture_total: 3000
split_ratios:
  train_visible:    0.50
  challenge_dev:    0.10
  random_inner_dev: 0.10
  acceptance_holdout: 0.10
  final_holdout:    0.10
  anchor_dev:       0.05
  reserve:          0.05
K_rotation: 5
candidates_per_round: 4
candidate_sources: [claude, codex, protegi_style, minimal_edit]
candidate_contract_required: true     # candidate.yaml + diagnosis.json (ProTeGi) + diff validator (minimal_edit)

metric:
  primary: primary_accuracy            # or core_entity_f1_micro, or modality_top1
  paired_test:
    top1: mcnemar_exact_one_sided
    f1:   paired_permutation_cluster   # PRIMARY gate
    f1_descriptive: paired_cluster_bootstrap_ci   # reported, not gate
  averaging: micro                     # F1 unit; macro requires manifest declaration + min stratum counts
  cluster_unit: article_fixture_id     # for F1 paired permutation / bootstrap
  delta_min_practical: 0.02            # task-specific floor; NOT a detectability claim
  delta_detectable_planning: null      # populated by MDE preflight at run start
target_threshold: 0.78                 # or 0.85 for entity, 0.82 for modality

# alpha family — across all 3 ws0_5 prompt-tuning tasks (v0.3 per S-2)
alpha_family_scope: all_ws0_5_prompt_tuning_tasks
alpha_total_family: 0.05
task_alpha_allocation:
  topic_classification: 0.0167
  entity_extraction:    0.0167
  signal_profile:       0.0166
max_acceptance_looks_by_task:
  topic_classification: 30
  entity_extraction:    30
  signal_profile:       30
per_look_alpha_rule: "task_alpha / max_acceptance_looks_by_task[task]"
# resulting per_look_alpha per task ≈ 0.000556  (Bonferroni within task,
# family alpha 0.05 across all 3 tasks)
look_counting_rule: |
  every acceptance_holdout query (the finalist submitted at the end of a
  round) spends one look, pass or fail. Candidates dropped by the train
  minibatch guardrail filter or by random_inner_dev ranking do not spend
  alpha. A rotation with zero submitted finalists counts toward operational
  plateau but spends no alpha.

plateau_rule: "2 consecutive rotations with zero accepted candidates"
global_cap: {acceptance_looks_by_task: see_above, rotations: 4}

active_sampling_recipe:
  applies_to: [train_visible, challenge_dev]
  stratified: 0.4
  disagreement: 0.25
  hotspot: 0.2
  diversity: 0.15

# v0.3 mechanical sealing per E-2
proposer_isolation:
  proposer_kind: api_only
  proposer_workspace_access: forbidden
  allowed_inputs_to_proposers:
    - train_visible_error_summaries
    - current_prompt_full_text
  forbidden_inputs_to_proposers:
    - random_inner_dev_items
    - challenge_dev_items
    - acceptance_holdout_items
    - final_holdout_items
    - anchor_dev_items
    - exact_metric_scalars
    - rounded_delta_scalars
    - per_example_per_look_breakdowns
  proposer_output_predicate_only:
    - fail
    - pass_delta_min
    - pass_above_target_threshold
  payload_sha_logged_per_candidate: true

# v0.3 manifest lock per E-4
manifest_lock:
  require_clean_git: true
  copy_to: data/factors/tuning_runs/<run_id>/manifest.lock.yaml
  abort_on_hash_change: true
  log_invariants: [run_id, manifest_sha256, manifest_git_commit]
```

Git SHA + content SHA256 of this manifest is logged in every tuning log row.
Mutations to the manifest after a single run round constitute a separate
decision memo + new `run_id` (per E-4).

### 4.3 Fixture build cost

Per task: 3000 items × dual-agent (Claude + Codex) labels + user adjudication on
disagreements. Per active rotation: ~500 additional items appended via active
sampling recipe + dual-agent label.

Total auto-tune fixture spend ≤ ~$50 V4 Pro per task (3 tasks → ~$150).

## 5. Historical Family Recurrence — data contract (Issue #7)

### 5.1 Construct

**Primary confirmatory variable** (renamed in v0.3 per measurement reviewer C-2):
`pre_case_cls_family_recurrence`. For each pilot case `(T, target, super_type)`,
it is the count of CLS articles in `[T − 24 months, T)` that match
`(target ∨ target aliases, super_type's constituent V3 event_types)` after entity
disambiguation.

**Construct interpretation (narrowed in v0.3 per C-2).** `pre_case_cls_family_recurrence`
is a **CLS recurrence density** measure, **proxying** model training-exposure
intensity. It is **not** identical to model-visible training recurrence: case
date `T` may exceed an older model's training cutoff, so the `[T − 24mo, T)`
window can include CLS items the model could not have seen. Paper language must
therefore refer to this variable as "pre-case CLS family recurrence density,
proxying training exposure," not as a directly observed training count.

**Model-cutoff-censored sensitivity (v0.3 per C-2).** Alongside the primary
case-level count, the factor table also stores, per (case × model):

```
recurrence_count_visible_to_model[case_id, model_id] =
    COUNT(matched_articles where date ∈ [T − 24mo, min(T, model_cutoff[model_id])))
```

This is reported as a sensitivity check for cutoff-sensitive estimands; the main
confirmatory analysis uses the case-level `pre_case_cls_family_recurrence` (so
that the factor remains case-level, not case×model), but the appendix reports
results recomputed with the model-visible variant.

**Recurrence applicability for negative controls (v0.3 per ML-engineer reviewer
E-5).** The 350 post-cutoff negative-control cases get
`pre_case_cls_family_recurrence = null` with
`missing_reason = "not_applicable_post_cutoff"`, and are **excluded** from
recurrence factor-bin quotas (plan §6.3 recurrence high/low quota counts apply
to the 80 pre-cutoff cases only). Rationale: for post-cutoff cases, the 24mo
window extends beyond all model training cutoffs by construction, so the same
measure does not proxy the same construct.

**No deduplication on the primary (Issue #7) — with v0.3 sensitivity (C-4).**
The primary measure is no-dedup (repeated CLS items contribute, as media repost
density is itself an exposure-density signal). v0.3 adds clustered/deduped
sensitivity fields to allow paper readers to distinguish broad recurrence from
within-CLS feed-level duplication:

```
recurrence_count_clustered[case_id]       # same matches, collapsed by event-cluster
recurrence_count_first_per_day[case_id]   # first match per calendar day
duplicate_ratio[case_id] = 1 - (recurrence_count_clustered / pre_case_cls_family_recurrence)
log1p_recurrence_count[case_id]            # construct-nearer continuous (C-3)
```

The paper interprets the primary as **CLS recurrence density** (within-CLS,
no-dedup). Cross-source / cross-corpus duplication is explicitly out of scope
for WS0.5; the deduped sensitivity exposes the magnitude of CLS-internal
repetition for any reviewer asking whether the measure indexes editorial feed
mechanics rather than corpus exposure.

### 5.2 Pipeline

```
Phase R1: Topic classification on FULL CLS mirror
  Input: data/cls_telegraph_raw/ (local, sha256-locked, 2317 daily files, 2020-now)
  Tool: frozen topic_classification_v4pro.yaml (output of Phase 1 auto-tune)
  Output: data/factors/cls_event_type_index.parquet
          (each CLS item → raw_event_type, super_type, host_category)
  Cost:   ~500K-1M items × $0.0004 ≈ $200-400

Phase R2: Entity alias generation for pilot targets
  Input: 80 pilot target entities (target, target_ticker)
  Tool: DeepSeek V4 Pro alias-gen prompt (pre-specified, smoke-validated, ancillary)
  Output: data/factors/target_aliases.json
          {target_id: [alias_str], each alias tagged ambiguity_risk: high|low}
  Cost: 80 × $0.0004 ≈ $0.03

Phase R3: Reference window candidate filter
  For each pilot case (T, target):
    Filter cls_event_type_index for:
      date ∈ [T − 24mo, T)
      super_type == case.super_type
      ANY salient_entities[].value ∈ target_aliases[target_id]
    → candidate_pool[target_id, super_type]
  No LLM cost. Rule-based.

Phase R4: Entity match confirmation (high-ambiguity only) — v0.3 per E-6
  Step 4a — rule-based ambiguity override:
    The alias-gen LLM emits `ambiguity_risk ∈ {high, low}`. The driver
    overrides to `high` (forcing Step 4b confirm) whenever ANY of:
      - alias length < 3 Chinese chars OR < 4 ASCII chars
      - one-char region alias (中, 美, 日, ...) when full alias exists
      - common surname or single-char person token
      - market/index acronym in shared-acronym registry
      - alias overlap with > 1 target in target_aliases.json
      - alias-gen ambiguity_risk missing or low-confidence tag
    Only aliases tagged `low` after override go to Step 4c without confirm.

  Step 4b — V4 Pro confirm (high-ambiguity matches only):
    Run DeepSeek V4 Pro confirmation prompt (pre-specified, smoke-validated,
    ancillary). Input: (article text, target name, matched_alias, target_id).
    Output: is_same_entity ∈ {yes, no, unsure}; unsure rejects the match.

  Step 4c — versioned cache key (v0.3 per E-6; corrected per round-2
  minor patch — lookup key must be computable BEFORE any provider call,
  so `response_id` cannot be part of the lookup key):
    cache_lookup_key = sha256(
      normalized_article_sha256, raw_article_sha256, target_id,
      matched_alias_norm, target_alias_bank_sha, confirm_prompt_sha,
      requested_model_slug, decoding_params_sha,
      provider_snapshot_if_available_else_pricing_epoch_id
    )
    # Stored as PROVENANCE fields on the cache record (NOT in lookup
    # key): response_id, provider_headers, request_timestamp,
    # model_snapshot_observed, full ledger entry.
    Cache invalidates when alias bank, confirm prompt, decoding params,
    requested model slug, or provider snapshot/pricing epoch changes.
    Per-call record stores the lookup key + result + provenance;
    re-runs read the cache and never silently reuse stale aliases.
  Cost: ~10-30K calls × $0.0004 ≈ $4-12

Phase R5: Count compute — v0.3 per E-7 + S-5 + C-2 + C-3
  Per pilot case (pre-cutoff cases only — post-cutoff controls get
  null + not_applicable_post_cutoff per §5.1):
    pre_case_cls_family_recurrence[case_id]      = COUNT(confirmed_matches)
    recurrence_count_clustered[case_id]          = collapsed by event-cluster
    recurrence_count_first_per_day[case_id]      = first match per calendar day
    duplicate_ratio[case_id]                     = 1 - clustered / primary
    log1p_recurrence_count[case_id]              = log1p(primary)

  Per pilot case × model (sensitivity, C-2):
    recurrence_count_visible_to_model[case_id, model_id] =
      COUNT(matched_articles where date ∈
        [T − 24mo, min(T, model_cutoff[model_id])))

  Within-super_type relative recurrence (v0.3 per E-7 + S-5):
    Compute ranks/cutpoints on the FULL eligible pre-cutoff sampling
    frame (not only on the final 80 cases), then freeze cutpoints
    before final manifest selection:
      recurrence_rank_method     = "average"   # ties handled by mean rank
      recurrence_tie_break       = "secondary order: log1p_count desc"
      recurrence_pct_within_super_type[case_id] = full_frame_percentile

  Primary binary CONFIRMATORY label (v0.3 framed as relative recurrence,
  per C-3):
    relative_recurrence_within_super_type_high[case_id] =
      (recurrence_pct_within_super_type >= 0.50)
    # construct interpretation: unusually recurrent for this event family,
    # NOT absolute exposure dose

  Bin stability diagnostic (v0.3 per E-7 + S-5):
    For each super_type, compute leave-one-out bin-flip rate AND
    bootstrap bin-flip rate on counts. Cases flagged as "unstable
    near 0.50 cutpoint" are reported in
    `data/factors/ws0_5_quota_report.json`. Sampler preferentially
    selects stable high/low cases while preserving §6.3/§6.4 quota
    rules; if instability is high (>15% bin-flip), manifest freeze
    requires an explicit signed note (no silent acceptance).

  Sensitivity reference (NOT confirmatory, always stored — closer to
  the latent "times seen" construct per C-3):
    log1p_recurrence_count[case_id]
    absolute_high_recurrence = (pre_case_cls_family_recurrence >=
                                median(all_80_pre_cutoff_cases))

  Pre-registered interpretation rules (v0.3 per S-statistician section 5.2):
    - both within-type and absolute significant, same sign → robust
      recurrence/exposure evidence
    - within-type significant, absolute not → conditional within-family
      repetition only, not broad exposure density
    - absolute significant, within-type not → exposure density dominated
      by event-type / base-rate differences
    - signs disagree or one is unstable → treat recurrence evidence as
      unresolved; emphasize sensitivity in the paper
    Pre-registration prevents post-hoc primary-swap.
```

### 5.3 Ancillary prompts spec (Phase R2, R4)

Both alias-gen and entity-confirm are simple V4 Pro tasks. v0.2 path:

- Pre-specified prompt (drafted in S1 / S2 session)
- Smoke validate on 20 cases × 2 reviewers → require ≥ 95% precision
- If smoke passes: lock and use directly
- If smoke fails: escalate to a short auto-tune (Scheme Y with smaller fixture ~200)

### 5.4 Non-redundancy

- Within-super_type percentile is decorrelated from super_type by construction in expectation; with ties and unequal stratum sizes, full-frame ranks are used (per §5.2 v0.3 patch) so that small-sample bin-flips do not dominate
- Absolute count + `log1p(count)` + clustered/deduped counts stored as construct-nearer sensitivity (per C-3 + C-4)
- Pre-manifest discriminant check is governed by §3.3.3 v0.3 expansion: all 6 confirmatory pairs, marginal + partial / residual correlations controlling for super_type / host / date, scaled GVIF, condition number, mixed-model singularity. `relative_recurrence_within_super_type_high` × Target Salience and × Template Rigidity are the modifiable same-level pairs subject to resample-or-rebin on `|partial ρ| > 0.65`

### 5.5 Provisional designation

The choice of `relative_recurrence_within_super_type_high` as the primary
binary confirmatory factor remains provisional. v0.3 sharpens the semantics
(per C-3): the primary measure is **relative recurrence within event family**;
absolute / log / clustered counts are stored alongside as construct-nearer
sensitivity, and the §5.2 pre-registered interpretation rules govern how
within-type vs absolute findings are read. The final lock occurs at S4 after
pilot factor values are computed and the §3.3.3 discriminant report is
emitted; if `relative_recurrence_within_super_type_high` proves unstable
(>15% bin-flip per §5.2) or strongly correlated with another modifiable
factor (`|partial ρ| > 0.65`), the swap to absolute/log count is mechanical
and recorded in a v0.3-addendum decision.

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
deterministic post-processing (parse → collapse → bin) over the cache.

**Storage tiers (v0.3 per ML-engineer reviewer E-8).** The per-case JSON layout
in v0.2 was inconsistent with §5 Phase R1 (full-CLS topic classification,
500K-1M calls); a single 35-60 MB Git-LFS estimate would expand to multiple GB
and hundreds of thousands of tiny LFS pointers under Windows. v0.3 splits the
cache by volume:

```
data/factors/raw_llm_responses/
  # Tier A — pilot-scale, per-case JSON (430 cases × 3 tasks ≈ 1290 files):
  pilot/
    topic_classification_v4pro/<case_id>.json
    entity_extraction_v4pro/<case_id>.json
    signal_profile_v4pro/<case_id>.json

  # Tier B — full-CLS R1 topic classification (~500K-1M items),
  # compressed sharded JSONL.zst (E-8):
  full_cls/
    topic_classification_v4pro/
      shard_0001.jsonl.zst
      shard_0002.jsonl.zst
      ...
      shard_index.parquet      # cls_item_id → (shard_path, byte_offset, raw_sha256)

  # Tier C — auto-tune raw responses (per task, sharded):
  auto_tune/
    topic_classification_v4pro/<run_id>/shard_*.jsonl.zst + shard_index.parquet
    entity_extraction_v4pro/<run_id>/shard_*.jsonl.zst + shard_index.parquet
    signal_profile_v4pro/<run_id>/shard_*.jsonl.zst + shard_index.parquet

each tier-A JSON contains (full prompt text retained, pilot scale only):
  {
    "case_id_or_cls_id": "...",
    "prompt_sent": "<full prompt text>",
    "response_text": "<full V4 Pro response>",
    "response_id": "<provider response id>",
    "model_snapshot": "deepseek-v4-pro-<date> | null if unavailable",
    "model_snapshot_unavailable": false,
    "requested_model_slug": "deepseek-v4-pro",
    "provider_headers": {...},
    "decoding_params": {"temperature": 0.0, "top_p": 1.0, "seed": 42 if supported},
    "request_timestamp": "ISO8601",
    "tokens_in": <int>,
    "tokens_out": <int>
  }

each tier-B / tier-C JSONL.zst record stores:
  {
    "cls_item_id_or_case_id": "...",
    "prompt_sha": "<sha256 of rendered prompt>",     # full text stored ONCE in templates
    "prompt_template_path": "config/factors/.../v4pro.yaml",
    "prompt_template_git_sha": "...",
    "input_sha256": "<sha256 of canonical input fields>",
    "rendered_prompt_sha256": "...",
    "response_text": "<full V4 Pro response>",
    "response_id": "<provider response id>",
    "model_snapshot": "deepseek-v4-pro-<date> | null",
    "model_snapshot_unavailable": false,
    "requested_model_slug": "deepseek-v4-pro",
    "decoding_params": {...},
    "request_timestamp": "ISO8601",
    "tokens_in": <int>,
    "tokens_out": <int>
  }
# full rendered prompt text is NOT stored per record in tier B/C;
# it is recoverable by re-rendering with template + canonical input fields,
# verified against rendered_prompt_sha256.
```

**`model_snapshot` nullability (v0.3 per E-8).** Before S1, run a provider
smoke test to determine whether DeepSeek V4 Pro exposes a stable
snapshot/fingerprint. If not, store `model_snapshot=null` +
`model_snapshot_unavailable=true` and rely on `response_id` + provider headers
+ request timestamp for traceability. Replay determinism is then defined as
"same `response_text` returned given same cache key," not "same snapshot
across runs."

### 6.2 factor_provenance.json (audit trail)

For each cell in `pilot_factor_values.parquet`:

```json
{
  "<case_id>": {
    "<factor_name>": {
      "value": "<computed value>",
      "source_raw_response": "raw_llm_responses/<task>/<id>.json",
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

`scripts/replay_factor_values.py` — reads `raw_llm_responses/` + frozen prompt
configs + factor_schema.yaml; outputs `pilot_factor_values.parquet` and
`factor_provenance.json` **without re-calling V4 Pro**.

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
`factor_provenance.json`; reproducibility is verified by hash equality, not
parquet byte-identity. If bit-level parquet identity is additionally desired
for archival reasons, the script pins `pyarrow` version and writer options
explicitly (recorded in `data/factors/replay_environment.lock.json`).

**Missing-cache policy (v0.3 per E-9).** Confirmatory replay **hard-fails** on
any missing, corrupt, duplicate, or hash-mismatched raw response. A separate
diagnostic mode `replay_factor_values.py --allow-missing` may write incomplete
artifacts for triage, but it **cannot overwrite** the committed
`pilot_factor_values.parquet`; it writes to `pilot_factor_values.partial.parquet`
with a separate provenance file.

### 6.4 Storage

**Pilot tier (tier A) — committed via Git LFS**:

```
.gitattributes:
data/factors/raw_llm_responses/pilot/**/*.json filter=lfs diff=lfs merge=lfs -text
data/factors/raw_llm_responses/full_cls/**/*.jsonl.zst filter=lfs diff=lfs merge=lfs -text
data/factors/raw_llm_responses/full_cls/**/shard_index.parquet filter=lfs diff=lfs merge=lfs -text
data/factors/raw_llm_responses/auto_tune/**/*.jsonl.zst filter=lfs diff=lfs merge=lfs -text
data/factors/raw_llm_responses/auto_tune/**/shard_index.parquet filter=lfs diff=lfs merge=lfs -text
```

Pilot tier estimate: 1290 JSONs × ~3 KB ≈ **4-6 MB** (revised from v0.2's
35-60 MB which conflated pilot and full-CLS).

**Full-CLS tier (tier B) — revised estimate (v0.3 per E-8).** 500K-1M records
× ~1.5 KB compressed JSONL ≈ **0.7-1.5 GB** compressed. Sharded into
~100 MB shards (5-15 shards). LFS preflight required (per E-8):

```
ws0_5_storage_preflight.py:
  - git lfs env / quota check
  - dry-run 1K-call sample of topic_classification_v4pro
  - compute observed compressed bytes/record
  - extrapolate to full-CLS size estimate
  - if estimate > LFS quota OR file count > Windows comfort:
      switch to external artifact path:
        store shards outside Git LFS as a checksum-locked archive
        (e.g., on the local CLS data drive)
      treat `cls_event_type_index.parquet` as the committed
      source-of-truth (always Git LFS), and raw shards as an
      auxiliary reproducibility artifact with SHA recorded in
      factor_provenance.json
```

**Auto-tune tier (tier C)** is per-run; storage is freed/compressed once the
winning prompt is locked, except for the winning candidate's responses (which
become the prompt's reproducibility cache and are retained).

The storage preflight runs before the first heavy phase (R1 full-CLS topic
classification at S4) and writes `data/factors/storage_preflight_report.json`.

## 7. Budget accounting + safety rails (Issue #8)

v0.1's "$5/factor cap" is replaced with token-and-USD accounting + safety rails
(not hard caps).

### 7.1 Per-task budget ledger

```yaml
# config/factors/<task>_autotune_manifest.yaml inherits:
budget:
  # v0.3 per E-10 — per-task dry-run token estimator (not uniform 3000)
  token_estimator_dry_run:
    sample_n: 100                          # representative items per task
    sample_strategy: stratified_random     # from train_visible
    record_p50_p95: true
    output: config/factors/<task>_token_estimate.json
    run_before: manifest_commit

  pre_registered_estimates:
    # Populated from token_estimator_dry_run output, NOT uniform across tasks.
    # Typical post-estimator values (record in manifest):
    expected_input_tokens_p50_per_item: <task-specific>
    expected_input_tokens_p95_per_item: <task-specific>
    expected_output_tokens_p50_per_item: <task-specific>
    expected_output_tokens_p95_per_item: <task-specific>
    expected_items_total:
      auto_tune_loop: <formula>           # = K_rotation × candidates_per_round × candidate_eval_n
                                          #   + max_acceptance_looks × acceptance_holdout_n
                                          #   + 1 × final_holdout_n
      pilot_factor_inference: <430 or 80 per task>
      reference_window_topic_class: 500_000   # topic task only
      entity_step_C_disambig:        ~20_000  # entity task only; from R4 high-ambiguity rate

  live_tracking:
    output_file: data/factors/budget_ledger_<task>.jsonl
    aggregate_dashboard: scripts/budget_summary.py
    writer_kind: buffered_queue          # v0.3 per E-10 — NOT fsync-per-row
    flush_every_n_rows: 100
    flush_every_seconds: 5
    flush_on_checkpoint: true
    flush_on_clean_shutdown: true

  safety_rails:
    soft_limit_factor: 2.0   # 2× expected_USD (p50) → warning + concurrency throttle
    hard_limit_factor: 5.0   # 5× expected_USD (p50) → halt, require user resume
    estimate_basis: p50      # p95 also computed for early-warning at 1.5× p95

  pricing_pin:
    fetch_at_run_start: deepseek_v4_pro_official_pricing_page
    refresh_at_most: daily              # v0.3 per E-10 — NOT per-call
    snapshot_in_ledger_header: True
    new_epoch_on_pricing_change: True   # ledger records pricing_epoch_id
    cost_compute_basis: actual_tokens_returned_by_api
```

### 7.2 LedgerEntry schema

```json
{
  "timestamp": "ISO8601",
  "factor_task": "topic_classification | entity_extraction | signal_profile",
  "phase": "auto_tune_round_3 | pilot_inference | reference_window | step_C_confirm",
  "prompt_sha": "...",
  "model_snapshot": "...",
  "tokens_in": 2856,
  "tokens_out": 412,
  "input_rate_USD_per_M": 0.435,
  "output_rate_USD_per_M": 0.87,
  "USD_at_call_time": 0.00159,
  "promotional_pricing_period_active": true
}
```

### 7.3 Aggregate report

`scripts/budget_summary.py` — outputs per-task and overall USD/tokens, breakdown by
phase, comparison to pre-registered estimates. Markdown report at
`data/factors/budget_summary_report.md`.

### 7.4 Run-state checkpoint + resume contract (v0.3 per E-10)

The "halt on hard limit, require user resume" rule of v0.2 needs a concrete
resume state. The driver maintains `data/factors/tuning_runs/<run_id>/run_state.json`
(or sqlite) with at minimum:

```json
{
  "run_id": "...",
  "manifest_sha256": "...",
  "manifest_git_commit": "...",
  "phase": "auto_tune | pilot_inference | reference_window | step_c_confirm",
  "rotation_idx": <int>,
  "round_idx": <int>,
  "look_idx": <int>,
  "accepted_prompt_sha": "<sha of current incumbent>",
  "alpha_spent": <float>,
  "alpha_remaining": <float>,
  "looks_spent": <int>,
  "looks_remaining": <int>,
  "raw_cache_shard_cursor": {"shard": "shard_0007", "byte_offset": 12345678},
  "in_flight_request_ids": ["resp_id_1", "resp_id_2"],
  "budget_totals_USD": <float>,
  "budget_totals_tokens": {"in": <int>, "out": <int>},
  "last_checkpoint_at": "ISO8601"
}
```

On hard-limit halt, the driver:
1. cancels in-flight requests OR awaits clean completion (configurable);
2. flushes the ledger queue + raw-cache shard writer;
3. writes a final checkpoint.

Resumption requires `python ws0_5_auto_tune_loop.py --resume <run_id>` and:
- verifies the on-disk manifest still matches `manifest.lock.yaml` SHA;
- verifies the prompt git commit still matches `manifest_git_commit`;
- aborts on any drift, requiring an explicit new `run_id`.

This makes "user resume" implementable; without it the v0.2 rail is paper-only.

## 8. Deliverables

```
docs/
  DECISION_20260518_ws0_5_thales_alignment.md   # this memo

config/factors/
  topic_classification_v4pro.yaml               # T1 frozen prompt + collapse_map + thresholds
  entity_extraction_v4pro.yaml                  # T2 frozen prompt + thresholds
  signal_profile_v4pro.yaml                     # T3 frozen (V2 combined OR v5.5 two-pass, decided post-smoke)
  ancillary/
    target_alias_gen_prompt.yaml                # Phase R2 (ancillary, smoke-validated)
    entity_confirm_prompt.yaml                  # Phase R4 (ancillary, smoke-validated)
  
  factor_schema.yaml                            # all factor names, dtypes, binning, collapse maps
  r5a_market_metadata_snapshot.json             # market cap / index members / institution registry (built S1)
  author_authority_mapping.json                 # T3 Track B (if author coverage ≥ 80%; else documented absence)
  
  topic_classification_autotune_manifest.yaml   # Scheme Y pre-reg
  entity_extraction_autotune_manifest.yaml
  signal_profile_autotune_manifest.yaml

scripts/
  build_market_metadata_snapshot.py             # S1
  ws0_5_cls_author_coverage.py                  # T3 Track B coverage probe
  ws0_5_auto_tune_loop.py                       # Scheme Y driver (manifest lock + resume per E-4/E-10)
  ws0_5_mde_preflight.py                        # v0.3 per E-1/S-1; runs before any acceptance query
  ws0_5_token_estimator.py                      # v0.3 per E-10; per-task dry-run p50/p95 token sampler
  ws0_5_storage_preflight.py                    # v0.3 per E-8; LFS quota + dry-run shard-size probe
  ws0_5_discriminant_report.py                  # v0.3 per S-6; 6-pair partial/GVIF/condition diagnostics
  ws0_5_bin_stability.py                        # v0.3 per E-7/S-5; LOO + bootstrap bin-flip per super_type
  replay_factor_values.py                       # raw_responses → parquet (no API calls); canonical row-hash + hard-fail-on-missing per E-9
  budget_summary.py                             # ledger → markdown report
  check_pilot_cells.py                          # WS0.5 stub; WS4 full implementation
  ws0_5_compute_pilot_factors.py                # orchestrator: pilot 430-case factor inference

data/factors/
  pilot_factor_values.parquet                   # final factor table for WS4/WS5
  factor_provenance.json                        # per-cell audit trail + canonical_table_hash (v0.3 per E-9)
  replay_environment.lock.json                  # v0.3 per E-9; pyarrow/python version pins for archival parquet identity
  ws0_5_quota_report.json                       # plan §6.3 + §6.4 quota check report + bin-stability block (v0.3 per E-7/S-5)
  ws0_5_discriminant_report.json                # v0.3 per S-6; 6-pair partial / GVIF / condition / mixed-model singularity
  storage_preflight_report.json                 # v0.3 per E-8
  
  raw_llm_responses/                            # Git LFS tracked; replay source-of-truth (v0.3 tiered per E-8)
    pilot/
      topic_classification_v4pro/<case_id>.json
      entity_extraction_v4pro/<case_id>.json
      signal_profile_v4pro/<case_id>.json
    full_cls/
      topic_classification_v4pro/shard_*.jsonl.zst + shard_index.parquet
    auto_tune/
      <task>/<run_id>/shard_*.jsonl.zst + shard_index.parquet
  
  cls_event_type_index.parquet                  # full-CLS event_type labels
  target_aliases.json                           # pilot target alias bank (versioned alias_bank_sha)
  tuning_logs/
    <task>_tuning_log.jsonl                     # per-round Scheme Y log + alpha-spent ledger
  tuning_runs/<run_id>/                         # v0.3 per E-4/E-10
    manifest.lock.yaml                          # hash-locked manifest copy
    mde_report.json                             # MDE preflight verdict
    run_state.json                              # checkpoint state for --resume
  budget_ledger_<task>.jsonl                    # token + USD live tracking (buffered writer per E-10)
  budget_summary_report.md                      # aggregate budget report

related papers/
  (Codex S0 round 0 references batch-fetched per Issue #11; index updated in PAPER_INDEX.md)
```

## 9. Closure conditions for WS0.5

WS0.5 closes when **ALL** of:

1. This memo signed (v0.2 → Codex round-1 → v0.3 → Codex round-2 → user approval)
2. Three frozen prompt configs committed (T1 topic, T2 entity, T3 signal_profile)
3. Two ancillary prompt configs committed (alias-gen, entity-confirm)
4. T3 Track B coverage report committed; mapping table OR documented abandonment
5. Auto-tune logs show termination = `threshold_converged` OR `plateau` for each factor + alpha-spent ledgers; **per-run `manifest.lock.yaml` + `mde_report.json` + `run_state.json` committed in `data/factors/tuning_runs/<run_id>/`** (v0.3 per E-1/E-4/E-10/S-1)
6. **`pilot_factor_values.parquet` reproducible from `raw_llm_responses/` cache + frozen code SHAs** (Issue #4); reproducibility verified via `canonical_table_hash` (v0.3 per E-9); confirmatory replay hard-fails on missing/corrupt cache
7. **`factor_schema.yaml` committed** — factor names, dtypes, binning/collapse rules, EventType → super_type mapping, missing-value policy (incl. `not_applicable_post_cutoff` for recurrence on 350 controls per v0.3 E-5), perturbation-eligibility fields, Target Salience raw-component fields (per v0.3 C-1), recurrence sensitivity fields (`recurrence_count_visible_to_model`, `log1p_recurrence_count`, `recurrence_count_clustered`, `duplicate_ratio` per v0.3 C-2/C-3/C-4), rank/tie/bin-stability policy (per v0.3 E-7/S-5) (Issue #5 + v0.3 patches)
8. **`data/factors/ws0_5_quota_report.json` committed** — plan §6.3 quotas + §6.4 n_eff target/min counts + C_FO funnel + C_NoOp host coverage + post-cutoff mix preservation + **bin-stability block per super_type** (v0.3 per E-7/S-5) (Issue #5)
9. **`scripts/check_pilot_cells.py` committed at spec+stub level** — function signature + IO schema + check-logic pseudocode in docstring; WS4 implements (Issue #5)
10. **`data/factors/ws0_5_discriminant_report.json` committed** — 6-pair marginal + partial correlations, scaled GVIF, condition number, mixed-model singularity, per-pair go/inspect/resample verdict (v0.3 per S-6)
11. **`data/factors/storage_preflight_report.json` committed** — LFS quota probe + per-shard size estimate; declares whether full-CLS raw cache is Git-LFS-tracked or external-archive (v0.3 per E-8)
12. Plan §5.1A WS0.5 section updated from "scope TBD" to one-paragraph pointer at this memo + factor_schema.yaml path
13. Budget ledgers committed; `budget_summary_report.md` shows actual spend vs pre-registered estimate; pricing-pin epoch records snapshotted in ledger header (v0.3 per E-10)
14. PENDING.md "WS0.5 — Thales alignment design" moved to Recently closed; plan §14.4 sign-off checklist WS0.5 row ticked ✓

## 10. Schedule

| Session | Deliverables |
|---|---|
| **S0 (2026-05-18/19)** | v0.1 → Codex round-0 → 9-issue interactive review → **v0.2 (this revision)** → Codex round-1 re-review (S0 closes when round-1 verdict ≥ APPROVE-WITH-REVISIONS) |
| **S1** | T3 Track B author-coverage probe; market metadata snapshot builder + run; T1 topic_classification auto-tune (Scheme Y) |
| **S2** | T2 entity_extraction auto-tune (Scheme Y); ancillary alias-gen + entity-confirm smoke validation |
| **S3** | T3 Track A signal_profile: smoke comparison (V2 combined vs v5.5 two-pass) → winner → auto-tune; opportunistic Authority tuning if session time |
| **S4** | Phase R1-R5 recurrence pipeline (full-CLS topic class + entity matching + count compute); pilot 430-case factor inference; replay → parquet + provenance |
| **S5** | Plan §5.1A update + sign-off + §14.4 checklist tick + commit |

S1-S3 can overlap with V4 Pro concurrency parallelism. S4 strictly sequential
after S1-S3 prompts frozen.

## 11. Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-W05-1 | V4 Pro behavior diverges materially from deepseek-chat → starting prompts regress | Scheme Y paired acceptance gate (one-sided exact McNemar / paired permutation per §4.1) + train/inner_dev diagnostics catch; if 50% baseline drop in round 1 (incumbent under target_threshold by > 0.10 on random_inner_dev), halt and reconsider |
| R-W05-2 | Salience-tier output from heavy entity prompt fragile under V4 Pro | MVP entity output (value, type) sufficient; salience as bonus that fails open |
| R-W05-3 | Adaptive holdout reuse degrades reported metric | Scheme Y's 4-layer split + limited-exposure acceptance + alpha spending; final_holdout sealed |
| R-W05-4 | sector_industry < 12 verified+slotable for C_FO | Hard quota oversample at sampling; trigger Scheme B 4-super_type fallback if persists |
| R-W05-5 | Author coverage < 80% → Track B abandoned | Track A alone covers Authority operationalization; abandonment is documented limitation, not closure blocker |
| R-W05-6 | Recurrence reference window topic-classification cost overrun | Full-CLS cost ~$200-400 within token plan; soft 2× / hard 5× safety rail catches accidents |
| R-W05-7 | Thales summary entity fixture too small (80) for V4 Pro calibration | Scheme Y active fixture growth to 3000 via dual-agent labeling |
| R-W05-8 | Codex v0.2 re-review challenges within-super_type recurrence binarization | Pre-stored absolute count; alternate operationalization swap is mechanical |
| R-W05-9 | Smoke comparison (V2 vs v5.5) tie within ±2% modality | Decision rule deterministic; document tie-breaking choice in memo addendum if triggered |
| R-W05-10 | Signal profile two-pass nominally selected but Authority post-tune doesn't gain | Authority opportunistic-tune; not a closure gate |

## 12. Open items / future-session pointers

- KG-lookup / Wikipedia Authority for true extra-corpus operationalization → P1-expansion track, separate memo
- Bloc 3 Event Phase / Session Timing operationalization → WS0.5 closure addendum after S4
- Production entity-pipeline rework integration → re-evaluate prompt swap for main run (NOT pilot)
- Class 1 vs class 2 sub-division for Target Salience → pilot data review + Codex v0.2 review
- Recurrence primary binarization (within-super_type percentile vs absolute count) → Codex v0.2 review

## 13. Sign-off

- Author: Claude Code orchestrator, 2026-05-18 (v0.1) / 2026-05-19 (v0.2 + v0.3), interactive + autonomous review session with user
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
- User sign-off: pending
- Plan §5.1A update: pending S5
