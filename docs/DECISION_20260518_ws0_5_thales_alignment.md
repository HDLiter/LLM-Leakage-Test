---
title: WS0.5 Thales Alignment — Reuse-vs-Rebuild Decision, Auto-Tune Loop, and Factor Pipeline Spec
date: 2026-05-18
revision: v0.2
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
status: DRAFT v0.2 — pending Codex round-1 re-review
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
context_gate ∈ {0,1,2}   # text-side veto
static_reach ∈ {1,2,3}   # metadata-side main signal

ordinal = 
    1 (low)    if context_gate == 0
    3 (high)   if static_reach == 3 and context_gate ≥ 1
    2 (medium) if static_reach == 2 and context_gate ≥ 1
    1 (low)    otherwise
```

`static_reach` mapping by target family:

| Family | static_reach=3 | static_reach=2 | static_reach=1 |
|---|---|---|---|
| Company | SSE50 / CSI300 / top-cap 国民级 | 普通 listed / CSI500 / 大型未上市 | 小盘 / unlisted / 地方 |
| Index/ETF | 宽基指数 / 全市场 ETF | 行业 / 主题 ETF | 窄基金 |
| Sector | 主流正式行业 / 主导主题 | 申万/CSRC 行业 / 商品 | 窄产品 / 业务段 |

**Class 1 (security) vs class 2 (sector) sub-division** intentionally NOT defined
in v0.2 — defer to pilot results + Codex v0.2 review.

#### 3.3.3 Construct validity & non-redundancy

- Target Salience proxies **cross-corpus training exposure** (market reach / institutional scope), not in-article text salience
- Text-local signals (title presence, mention count) are only the `context_gate`; they cannot promote ordinal alone
- Tradability Tier and Target Scope are absorbed into `static_reach`, not separate confirmatory factors
- Discriminant rule: no historical CLS mention count / no event_type / no month encoded in Target Salience (those belong to Historical Family Recurrence §5)
- Pre-manifest discriminant check: Spearman correlation between Target Salience and Historical Family Recurrence: `|ρ| < 0.50` desired, `0.50-0.65` inspect, `> 0.65` resample. VIF `< 3` in pilot mixed-model

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
  train_visible       60%   (1800 items) — proposers see errors here
  inner_dev           20%   ( 600 items) — candidate ranking; semi-transparent
  acceptance_holdout  10%   ( 300 items) — Ladder gate; returns ONLY pass/fail + rounded delta to proposers
  final_holdout       10%   ( 300 items) — sealed from T0; touched once at end

rotation:
  K = 5 rounds per rotation
  rotate: train + inner_dev (active sampling recipe below)
  do NOT rotate: acceptance_holdout, final_holdout

active sampling recipe (per rotation):
  40% stratified random (unbiased base)
  25% Claude/Codex/current-prompt 3-way disagreement (boundary cases)
  20% current-prompt high-confidence error (hotspot)
  15% embedding-cluster diversity + rare-label coverage

candidates per round (4):
  candidate_1 = Claude_free_form_patch(train_errors, current_prompt)
  candidate_2 = Codex_free_form_patch(train_errors, current_prompt)
  candidate_3 = ProTeGi_style_patch(train_minibatch_errors, current_prompt)
              # Required: explicit diagnose step before fix step
  candidate_4 = minimal_edit_patch(train_errors, current_prompt)
              # 1-2 line baseline; prevents over-mutation

selection pipeline (per round):
  4 candidates → train minibatch filter (drop schema-breaking / clearly worse)
  → top 2-3 ranked on inner_dev (per-example metric)
  → 1 finalist submitted to acceptance_holdout

acceptance gate (Ladder-style limited-exposure):
  paired test (per metric type):
    pass/fail per-example (e.g., topic top-1 acc): McNemar exact + binomial matched-pair
    F1-style aggregate (e.g., entity recall):     paired bootstrap diff CI + paired permutation test
  
  alpha spending:
    total alpha = 0.05
    max acceptance looks pre-registered = 30 (global across all rounds × candidates)
    per-look alpha = Bonferroni 0.05/30 ≈ 0.00167
  
  delta_min (pre-registered, per factor):
    topic_classification: 0.02 (primary_accuracy points)
    entity_extraction:    0.02 (core-entity F1)
    signal_profile:       0.02 (modality top-1)
  
  acceptance condition:
    candidate's paired metric vs incumbent on acceptance_holdout passes BOTH:
      (i)  practical effect: observed delta ≥ delta_min
      (ii) statistical:      paired test p < per-look alpha
  
  output to proposers:
    pass OR fail
    rounded delta to 0.01 (NOT exact metric)
    NO per-example breakdowns from acceptance_holdout

termination:
  threshold_converged: acceptance metric ≥ target_threshold per §3.1/§3.2/§3.4
  plateau: 2 consecutive rotations without accepted candidate
  global cap: 30 acceptance looks OR 4 rotations
  
post-termination:
  Evaluate winning prompt once on final_holdout
  Report final_holdout metric as the official threshold result
  If final_holdout metric < target_threshold by > delta_min: documented limitation, not blocker
```

### 4.2 Pre-registration manifest

Before any loop runs, commit `config/factors/<task>_autotune_manifest.yaml`:

```yaml
factor_task: topic_classification     # or entity_extraction, signal_profile
fixture_seed: <pinned>
fixture_total: 3000
split_ratios: {train: 0.6, inner_dev: 0.2, acceptance: 0.1, final: 0.1}
K_rotation: 5
candidates_per_round: 4
candidate_sources: [claude, codex, protegi_style, minimal_edit]
metric:
  primary: primary_accuracy
  paired_test: mcnemar_exact
  delta_min: 0.02
target_threshold: 0.78
alpha_total: 0.05
max_acceptance_looks: 30
per_look_alpha: 0.00167
plateau_rule: "2 consecutive rotations without acceptance"
global_cap: {acceptance_looks: 30, rotations: 4}
active_sampling_recipe: {stratified: 0.4, disagreement: 0.25, hotspot: 0.2, diversity: 0.15}
```

Git SHA of this manifest is logged in every tuning log entry. Mutations to the
manifest after a single run round constitute a separate decision memo.

### 4.3 Fixture build cost

Per task: 3000 items × dual-agent (Claude + Codex) labels + user adjudication on
disagreements. Per active rotation: ~500 additional items appended via active
sampling recipe + dual-agent label.

Total auto-tune fixture spend ≤ ~$50 V4 Pro per task (3 tasks → ~$150).

## 5. Historical Family Recurrence — data contract (Issue #7)

### 5.1 Construct

For each pilot case (T, target, super_type), `historical_family_recurrence` is the
count of CLS articles in `[T − 24 months, T)` that match `(target ∨ target aliases,
super_type's constituent V3 event_types)` after entity disambiguation.

**Construct interpretation**: proxy for "how often the model probably saw similar
patterns during training". High raw count = high media coverage density during
training = high memorization likelihood. **No deduplication** is applied (Issue #7
user rationale): if a story is reposted N times in CLS, that itself signals
training exposure intensity.

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

Phase R4: Entity match confirmation (high-ambiguity only)
  For each candidate matched ONLY via high-ambiguity-risk aliases:
    Run DeepSeek V4 Pro confirmation prompt (pre-specified, smoke-validated, ancillary)
    Input: (article text, target name, matched_alias)
    Output: is_same_entity ∈ {yes, no, unsure}
  Cache: keyed (article_hash, target_id) → result; reusable across pilot reruns
  Cost: ~10-30K calls × $0.0004 ≈ $4-12

Phase R5: Count compute
  recurrence_count[case_id] = COUNT(confirmed_matches)
  recurrence_pct_within_super_type[case_id] = percentile_rank of count within
                                              same-super_type pilot cases
  
  Binary primary factor (CONFIRMATORY):
    high_recurrence = (recurrence_pct_within_super_type >= 0.50)
  
  Sensitivity reference (NOT confirmatory, stored only):
    absolute_high_recurrence = (recurrence_count >= median across all 80 pilot cases)
```

### 5.3 Ancillary prompts spec (Phase R2, R4)

Both alias-gen and entity-confirm are simple V4 Pro tasks. v0.2 path:

- Pre-specified prompt (drafted in S1 / S2 session)
- Smoke validate on 20 cases × 2 reviewers → require ≥ 95% precision
- If smoke passes: lock and use directly
- If smoke fails: escalate to a short auto-tune (Scheme Y with smaller fixture ~200)

### 5.4 Non-redundancy

- Within-super_type percentile is decorrelated from super_type by construction (resolves multicollinearity worry)
- Absolute count stored as sensitivity for paper appendix
- Pre-manifest discriminant check: Spearman correlation between Historical Family Recurrence (primary) and other factors; same rules as §3.3.3

### 5.5 Provisional designation

Within-super_type percentile vs absolute count as the primary confirmatory binarization
is **provisional in v0.2**. Codex v0.2 re-review may suggest alternate operationalization;
final lock at S4 (compute pilot factor values).

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

```
data/factors/raw_llm_responses/
  topic_classification_v4pro/
    <case_or_cls_item_id>.json       # full V4 Pro response + provenance
  entity_extraction_v4pro/
    <case_id>.json
  signal_profile_v4pro/
    <case_id>.json

each <id>.json contains:
  {
    "case_id_or_cls_id": "...",
    "prompt_sent": "<full prompt text>",
    "response_text": "<full V4 Pro response>",
    "response_id": "<provider response id>",
    "model_snapshot": "deepseek-v4-pro-<date>",
    "decoding_params": {"temperature": 0.0, "top_p": 1.0, "seed": 42 if supported},
    "request_timestamp": "ISO8601",
    "tokens_in": <int>,
    "tokens_out": <int>
  }
```

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
configs + factor_schema.yaml; outputs identical `pilot_factor_values.parquet` and
`factor_provenance.json` **without re-calling V4 Pro**. Anyone with the LFS-tracked
raw cache + git checkout reproduces bit-identical artifacts.

### 6.4 Storage

Estimated 12000 raw response JSONs × ~3 KB ≈ **35-60 MB**. Tracked via **Git LFS**:

```
.gitattributes:
data/factors/raw_llm_responses/**/*.json filter=lfs diff=lfs merge=lfs -text
```

## 7. Budget accounting + safety rails (Issue #8)

v0.1's "$5/factor cap" is replaced with token-and-USD accounting + safety rails
(not hard caps).

### 7.1 Per-task budget ledger

```yaml
# config/factors/<task>_autotune_manifest.yaml inherits:
budget:
  pre_registered_estimates:
    expected_input_tokens_per_item: 3000
    expected_output_tokens_per_item: 800
    expected_items_total:
      auto_tune_loop: 50_000
      pilot_factor_inference: 430
      reference_window_topic_class: 500_000   # topic task only
      entity_step_C_disambig: 20_000          # entity task only
  
  live_tracking:
    output_file: data/factors/budget_ledger_<task>.jsonl
    aggregate_dashboard: scripts/budget_summary.py
  
  safety_rails:
    soft_limit_factor: 2.0   # 2× expected_USD → warning + concurrency throttle
    hard_limit_factor: 5.0   # 5× expected_USD → halt, require user resume
  
  pricing_pin:
    fetch_at_run_start: deepseek_v4_pro_official_pricing_page
    snapshot_in_ledger_header: True
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
  ws0_5_auto_tune_loop.py                       # Scheme Y driver
  replay_factor_values.py                       # raw_responses → parquet (no API calls)
  budget_summary.py                             # ledger → markdown report
  check_pilot_cells.py                          # WS0.5 stub; WS4 full implementation
  ws0_5_compute_pilot_factors.py                # orchestrator: pilot 430-case factor inference

data/factors/
  pilot_factor_values.parquet                   # final factor table for WS4/WS5
  factor_provenance.json                        # per-cell audit trail
  ws0_5_quota_report.json                       # plan §6.3 + §6.4 quota check report
  
  raw_llm_responses/                            # Git LFS tracked; replay source-of-truth
    topic_classification_v4pro/
    entity_extraction_v4pro/
    signal_profile_v4pro/
  
  cls_event_type_index.parquet                  # full-CLS event_type labels
  target_aliases.json                           # pilot target alias bank
  tuning_logs/
    <task>_tuning_log.jsonl                     # per-round Scheme Y log + alpha-spent ledger
  budget_ledger_<task>.jsonl                    # token + USD live tracking
  budget_summary_report.md                      # aggregate budget report

related papers/
  (Codex S0 round 0 references batch-fetched per Issue #11; index updated in PAPER_INDEX.md)
```

## 9. Closure conditions for WS0.5

WS0.5 closes when **ALL** of:

1. This memo signed (v0.2 → Codex round-1 re-review → v0.3 → user approval)
2. Three frozen prompt configs committed (T1 topic, T2 entity, T3 signal_profile)
3. Two ancillary prompt configs committed (alias-gen, entity-confirm)
4. T3 Track B coverage report committed; mapping table OR documented abandonment
5. Auto-tune logs show termination = `threshold_converged` OR `plateau` for each factor + alpha-spent ledgers
6. **`pilot_factor_values.parquet` reproducible from `raw_llm_responses/` cache + frozen code SHAs** (Issue #4)
7. **`factor_schema.yaml` committed** — factor names, dtypes, binning/collapse rules, EventType → super_type mapping, missing-value policy, perturbation-eligibility fields (Issue #5)
8. **`data/factors/ws0_5_quota_report.json` committed** — plan §6.3 quotas + §6.4 n_eff target/min counts + C_FO funnel + C_NoOp host coverage + post-cutoff mix preservation (Issue #5)
9. **`scripts/check_pilot_cells.py` committed at spec+stub level** — function signature + IO schema + check-logic pseudocode in docstring; WS4 implements (Issue #5)
10. Plan §5.1A WS0.5 section updated from "scope TBD" to one-paragraph pointer at this memo + factor_schema.yaml path
11. Budget ledgers committed; `budget_summary_report.md` shows actual spend vs pre-registered estimate

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
| R-W05-1 | V4 Pro behavior diverges materially from deepseek-chat → starting prompts regress | Scheme Y bootstrap CI gate catches; if 50% baseline drop in round 1, halt and reconsider |
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

- Author: Claude Code orchestrator, 2026-05-18 (v0.1) / 2026-05-19 (v0.2), interactive session with user
- v0.1 review: Codex round-0, MAJOR-REVISIONS-NEEDED, 9 issues identified
- v0.2 status: 9 issues resolved per user-Claude interactive decision; awaiting Codex round-1 re-review
- User sign-off: pending after round-1 review
- Plan §5.1A update: pending S5
