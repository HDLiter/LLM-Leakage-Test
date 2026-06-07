# WS0.5 Thales Alignment Memo — Codex Round 0 Review

**Reviewer**: GPT-5.4 xhigh via Codex CLI
**Date**: 2026-05-18
**Memo under review**: docs/DECISION_20260518_ws0_5_thales_alignment.md

## TL;DR

**Verdict: MAJOR-REVISIONS-NEEDED.** The memo's high-level reuse posture is reasonable, but it cannot be signed as written: the Thales topic/signal assets are mis-versioned, Target Salience is not construct-valid from `salience=core` alone, and the auto-tune loop reuses holdouts in a way that would not survive reviewer/statistical scrutiny.

The highest-risk downstream bugs are: freezing a 10-class EventType schema when Thales current production code is 13-class; producing `pilot_factor_values.parquet` without a reproducible LLM-output manifest; and closing WS0.5 without a factor-quota / `n_eff >= 15` checker tied to plan §6.3.

## 1. Files actually read

- `docs/DECISION_20260518_ws0_5_thales_alignment.md` — Memo proposes reuse of Thales topic/entity/signal prompts plus an autonomous Claude+Codex auto-tune loop; key claims are in §2-§6.
- `plans/phase7-pilot-implementation.md` — WS0.5 closure must make factor values deterministically computable before WS4; §6.3 requires frozen factor schema, event-type quotas, factor-bin quotas, and perturbation eligibility funnels.
- `PENDING.md` — WS0.5 open item requires T1/T2/T3 answers, reuse-vs-rebuild scope, adapter/validation plan, and effort estimate before WS4.
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md` — Confirms the 4 confirmatory factors and S20 = 5 estimands x 4 factors; Bloc 3 baseline coverage in §8 lists Event Type / Modality / Event Phase / Session Timing, not Authority.
- `refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md` — L1 factors are case labels; `Entity Salience: target` is ordinal, not just target-entity extraction.
- `docs/THALES_SIGNAL_PROFILE_REVIEW.md` — Confirms Thales Modality and Authority are CLS-text-derived, not extra-corpus; flags collinearity with Event Type/Modality.
- `D:\GitRepos\Thales\prompts\news_processing\topic_classification.py` — Current file defines `NewsTopicClassificationPrompt` v2.2.0 but with V3 13 action-based EventType taxonomy.
- `D:\GitRepos\Thales\contracts\news\_annotation.py` — Current `EventType` enum has 13 values: POLICY, ENFORCEMENT, LEGAL, INDICATOR, EARNINGS, CORPORATE, PRODUCT, PERSONNEL, TRADING, OWNERSHIP, INDUSTRY, GEOPOLITICS, OTHER.
- `D:\GitRepos\Thales\prompts\news_processing\signal_profile.py` — Current file is two-pass v5.5.0 (`NewsSignalProfileModalityPrompt`, `NewsSignalProfileAuthorityPrompt`), not a single V2 combined `NewsSignalProfilePrompt`.
- `D:\GitRepos\Thales\experiments\prompts\news_summary\fixtures\labeling_prompt_entity.md` — Entity pass is dual-agent, self-contained, and uses 4-stage Filter/Tier/Type/Normalize with `salience = core|supporting`.
- `D:\GitRepos\Thales\experiments\prompts\news_summary\fixtures\quality_summary_pilot.json` — 80-item fixture exists with `items[]` and `salient_entities[]`; first rows confirm `value/type/salience`, but not the R16+ per-entity `reason` raw-label schema.
- `D:\GitRepos\Thales\experiments\prompts\news_topic_classification\experiment-log.md` — Contains the V6 0.738 fresh result, then later V3 13-type redesign and deepseek-chat 0.8142 / 0.8374 evidence.
- `D:\GitRepos\Thales\experiments\prompts\news_signal_profile\experiment-log.md` — Contains the V2 0.815/0.760 deepseek result, but later logs show v5/v5.5, fresh holdout, canon drift, and repeat aggregation.
- `data/cls_telegraph_raw/2026-05-01.json` — 4-item spot check confirms `author` exists; 2/4 first items have non-empty author and `source` is fixed `api_csw`.
- DeepSeek official pricing page, `https://api-docs.deepseek.com/quick_start/pricing/` — Checked because V4 Pro pricing is time-sensitive; current page lists discounted `deepseek-v4-pro` prices through 2026-05-31 15:59 UTC.

## 2. Claim verification

### 2.1 Thales 资产现状 (Claim 类 A)

| Claim | Verdict | Evidence |
|---|---|---|
| A1: Thales V6 topic prompt exists and is a 10-class enum | contradicted | `topic_classification.py` exists, but current prompt text says "Event Type Taxonomy (V3)" and lists 13 types. `_annotation.py` also defines 13 enum values. The 10-class V6 result exists historically in the log, but it is not the current production enum. |
| A2: Thales summary entity prompt has dual-agent + salience tier output | partially-confirmed | `labeling_prompt_entity.md` explicitly says the other session labels in parallel and outputs `salient_entities[]` with `value/type/salience/reason`. `quality_summary_pilot.json` confirms 80 adjudicated items with `salient_entities[].salience`; however the fixture schema shown lacks per-entity `reason`, so it is not identical to the current raw-label schema. |
| A3: Thales signal_profile V2 on deepseek-chat reached modality 0.815 / authority 0.760 | partially-confirmed | The signal experiment log §3.6 records V2 A+B combined on deepseek-chat at 81.5% modality and 76.0% authority. But current `signal_profile.py` is v5.5 two-pass, and later logs show newer holdout/repeat evidence; using V2 as the current asset metric is stale. |
| A4: CLS raw `author` field exists but is severely incomplete | partially-confirmed | `data/cls_telegraph_raw/2026-05-01.json` first 4 items all have `author`; first two are `央视新闻` / `新华社`, next two are empty strings, and `source` is always `api_csw`. This confirms incompleteness in the 4-item sample, but "severely" still needs the full coverage probe. |

### 2.2 Factor mapping (Claim 类 B)

| Claim | Verdict | Evidence |
|---|---|---|
| B1: 2/4 confirmatory factors do not depend on Thales | confirmed | Frozen shortlist §1 defines Cutoff Exposure as temporal case x model and Template Rigidity as text-template repetition. Neither requires Thales topic/entity/signal labels, although both still need deterministic implementation. |
| B2: Thales `salience=core` can directly serve Target Salience target-identification | partially-confirmed | Thales salience can identify summary-core entities, so it is useful for candidate target extraction. It does not by itself implement R5A's `Entity Salience: target` ordinal factor: core entities may be officials, countries, concepts, or multiple entities, and the R5A target/entity-prominence rule is not specified. |
| B3: Text-inferred Thales Authority is CLS-internal and does not restore P1 | partially-confirmed | Correct for Track A: THALES_SIGNAL_PROFILE_REVIEW §4/§6 says authority is inferred from CLS text markers, not publisher metadata/KG/web lookup. Caveat: Authority's status as a Bloc 3 factor is inconsistent across docs; plan §5.1A mentions it, but the frozen shortlist/framework baseline Bloc 3 inventory does not include Authority. |

### 2.3 Auto-tune loop (Claim 类 C)

| Claim | Verdict | Evidence |
|---|---|---|
| C1: Monotone-improvement gate prevents Claude/Codex patch ping-pong | contradicted | The 20% holdout gate can block obvious regressions, but both agents see the same error set and repeatedly compete on the same reused holdout. That prevents only local score decreases, not specialization to the holdout or oscillation between equivalent narrow patches. |
| C2: Fixture rotation every K=5, size 80->200 is enough to detect overfitting | contradicted | With 80 items, a 20% holdout is only 16 items; precision/recall deltas are too noisy for entity extraction and type-specific errors. K=5 allows several accepted patches before fresh validation; this is especially weak when two patch proposals are tested per round. |
| C3: 3 no-improvement rounds as plateau exit | partially-confirmed | A plateau rule is useful operationally, but with nondeterministic LLM scoring and small fixtures, 3 rounds can stop early because of metric noise. It needs confidence intervals / repeated scoring or a minimum fresh-validation pass before accepting plateau. |
| C4: `$5/factor x 20 rounds` is reasonable and complete | contradicted | Official DeepSeek pricing currently discounts `deepseek-v4-pro` to $0.435 / 1M cache-miss input tokens and $0.87 / 1M output tokens until 2026-05-31, with list prices higher after discount. The long entity prompt plus 80-200 item scoring, two candidate patches per round, and dual-agent fixture refresh can exceed $5/factor; labeling refresh cost is not included. |
| C5: Multi-prompt patch scoring on holdout creates multiplicity / holdout contamination | confirmed | Each round tests Claude and Codex patches on the same holdout, then repeats across rounds. Without a never-touched final holdout or nested CV, the reported threshold/plateau metric is optimistically biased. |

### 2.4 Closure 完整性 (Claim 类 D)

| Claim | Verdict | Evidence |
|---|---|---|
| D1: §6 closure covers plan §14.4 sign-off + §6.3 factor quota dependencies | partially-confirmed | Memo §6 covers signed memo, prompt configs, coverage report, tuning logs, factor parquet, and plan pointer. It does not require a factor-bin schema accepted by the sampler, quota report, `n_eff` checker, event super-type collapse, or perturbation eligibility fields required by plan §6.3/§6.4/§14.4. |
| D2: There are hard constraints in plan/shortlist missing from memo §6 | confirmed | Missing hard gates include plan §6.3 category/event-type quotas, both sides of each factor split retaining counts, C_FO `verified_outcome` and `fo_slotable` funnel, C_NoOp host category coverage, §6.4 target/minimum `n_eff`, and §13 `min cell >= 15` on 80 pre-cutoff cases. |
| D3: `pilot_factor_values.parquet` deterministic definition is sufficient | contradicted | "Deterministic given frozen prompts" is not enough for black-box LLM factor generation. Closure must pin model slug/snapshot, decoding params, prompt/config SHA, input hashes, parser version, raw response cache, fixture hashes, and factor-bin code; otherwise rerunning the API can produce drift. |

## 3. Critical issues found

### Issue #1 — Topic taxonomy/version is wrong (severity: blocker)

**问题**: The memo repeatedly says Thales topic classification is a 10-class V6 enum and proposes freezing that taxonomy. Current Thales code and contracts are 13-class V3. The V6 0.738 evidence is historical and belongs to the pre-V3 / V2 10-class phase. If WS0.5 signs the 10-class schema, WS3 `C_FO` event-type rules and §6.3 quota sampling can be built on a taxonomy Thales no longer implements.

**建议修改**: Replace the 10-class claim with the current 13-class production taxonomy. Treat the V6 0.738 result as historical lower-bound evidence only, and set calibration targets/fixtures against the current 13-class V3 prompt and boundary trees. Also define the collapse from 13 classes into the plan §6.3 "4 or 5 super-types" before closure.

**可 paste 文本**:
```markdown
**Corrected T1 asset status.** Current Thales production topic classification uses the V3 13-class `EventType` enum in `contracts/news/_annotation.py`: POLICY, ENFORCEMENT, LEGAL, INDICATOR, EARNINGS, CORPORATE, PRODUCT, PERSONNEL, TRADING, OWNERSHIP, INDUSTRY, GEOPOLITICS, OTHER. The earlier V6 10-class result (`primary_accuracy=0.738` on a fresh 367-item fixture) is historical calibration evidence, not the schema to freeze for R5A. WS0.5 will reuse the current 13-class prompt/contract and will additionally define a deterministic 13-class -> pilot super-type collapse for plan §6.3 quota checking and WS3 `C_FO` rule design.
```

### Issue #2 — `salience=core` does not close Target Salience (severity: blocker)

**问题**: The memo alternates between "salience directly answers Target Salience" and "answers the target-identification half." The latter is closer but still under-specified. R5A Target Salience is an ordinal case-level factor; Thales salience is a summary-entity tier. A news item can have several `core` entities, including countries, regulators, people, concepts, and non-tradable institutions. Without a target-selection and ordinal construction rule, this factor will be construct-invalid and hard to defend in the paper.

**建议修改**: Make Thales salience a candidate extraction input, not the factor itself. Add an explicit target selection rule, nullability rule, and ordinal binning rule. Validate target extraction separately from entity extraction.

**可 paste 文本**:
```markdown
**Target Salience construct rule.** Thales `salience=core` is reused only as a candidate target-entity signal. It does not by itself define the R5A Target Salience factor. WS0.5 must freeze: (1) a target-selection rule that chooses the financially material target entity among core entities, preferring tradable company/instrument entities when present; (2) a null rule for articles with no eligible target; (3) an ordinal salience/prominence binning rule using the selected target's role plus allowed metadata; and (4) validation metrics for target-span precision/recall and ordinal-bin agreement. The factor is closed only when this target rule is implemented and recorded in `factor_schema.yaml`.
```

### Issue #3 — Auto-tune validation leaks through reused holdouts (severity: blocker)

**问题**: The loop tests two patch proposals per round on the same 20% holdout and repeats this across up to 20 rounds. This is multiple comparison and adaptive holdout reuse. The monotone gate will select patches that fit the holdout's quirks, especially with N=80 entity fixtures. A reviewer can fairly ask: "What data were untouched by prompt search?"

**建议修改**: Split validation into train/dev/final. Use dev for patch selection, refresh/rotate training data, and keep a final holdout sealed until the end. For small fixtures, require bootstrap/McNemar uncertainty and repeated scoring for accepted improvements.

**可 paste 文本**:
```markdown
**Validation split discipline.** The auto-tune loop uses three partitions: `train` for error analysis, `dev` for patch selection, and `final_holdout` for one-time post-convergence reporting. Claude/Codex patches may compete on `dev`, but `final_holdout` is never shown in error sets and is evaluated only once after threshold/plateau termination. A patch is accepted only if it improves the dev metric by more than a pre-specified uncertainty margin (bootstrap CI for precision/recall, McNemar/binomial test for top-1 accuracy). The signed threshold metric is the final-holdout result, not the adaptive dev score.
```

### Issue #4 — Determinism/reproducibility is under-defined (severity: blocker)

**问题**: Memo §6 says `pilot_factor_values.parquet` is deterministic given frozen prompts. For API LLM factor generation, frozen prompt text is insufficient. DeepSeek/OpenAI/Anthropic class APIs can drift by model snapshot, decoding defaults, hidden system behavior, retry paths, and parser changes. If `pilot_factor_values.parquet` changes on rerun, WS4 manifest freeze becomes non-reproducible.

**建议修改**: Define determinism as replayability from cached raw LLM outputs plus full run metadata, not as fresh API determinism. The closure artifact must include hashes and model fingerprints.

**可 paste 文本**:
```markdown
**Determinism definition.** `pilot_factor_values.parquet` is deterministic by replay, not by assuming fresh API calls are bit-stable. WS0.5 closure requires: prompt SHA, config SHA, parser version, input case hash, model provider slug, model version/snapshot where exposed, decoding params (`temperature`, `top_p`, seed if supported), request timestamp, response id/fingerprint, raw response cache URI, and factor-bin code hash. The parquet must be reproducible from the frozen input manifest plus cached raw outputs without re-calling the LLM.
```

### Issue #5 — Closure misses plan §6.3/§6.4 quota gates (severity: major)

**问题**: Memo §6 does not require evidence that factor bins and event-type labels satisfy the pilot sampling and effective-sample constraints. Plan §6.3 requires category/event-type quotas, both sides of each factor split, C_FO feasibility funnel, C_NoOp host-category coverage, and post-cutoff mix preservation. Plan §6.4/§13 require `n_eff >= 15`. A frozen parquet without a quota report is not enough for WS4.

**建议修改**: Add a closure criterion for `factor_schema.yaml` plus a generated quota/cell report consumed by the sampler.

**可 paste 文本**:
```markdown
7. `factor_schema.yaml` committed with factor names, dtypes, binning/collapse rules, EventType -> pilot super-type mapping, missing-value policy, and perturbation-eligibility fields.
8. `data/factors/ws0_5_quota_report.json` committed and produced by the same checker WS4 will run. The report must show plan §6.3 quotas, plan §6.4 `n_eff` target/minimum counts, C_FO `verified_outcome` and `fo_slotable` counts, C_NoOp host-category coverage, and post-cutoff category-mix preservation.
```

### Issue #6 — Signal profile starting point is stale/misidentified (severity: major)

**问题**: Memo §2.3/§3.3 says `signal_profile.py` implements single-call `NewsSignalProfilePrompt v3.0.0` and proposes reusing V2 A+B combined. Current file is v5.5 two-pass modality/authority. The experiment log after V2 contains holdout failures, canon drift, v5/v5.5 comparisons, and repeat aggregation. The cited 0.815/0.760 is real but not the current best evidence.

**建议修改**: Rewrite T3 Track A around the current two-pass prompt and latest validation standard. Decide whether WS0.5 starts from current production v5.5 or an archived V2 prompt pack; do not call V2 "current" unless the exact archived prompt file is named and checked in.

**可 paste 文本**:
```markdown
**Corrected T3 Track A starting point.** Current Thales signal profile code is a two-pass v5.5 prompt pair: `NewsSignalProfileModalityPrompt` and `NewsSignalProfileAuthorityPrompt`. The 2026-04-11 V2 A+B combined deepseek result (modality 0.815, authority 0.760) is retained as historical evidence, but WS0.5 starts from the current two-pass prompt unless an archived V2 prompt pack is explicitly copied into `config/factors/` and justified. T3 validation must use the latest canon-aligned fixture/holdout protocol and must report parse rate, modality top-1, authority top-1, rank metric, and persistent error clusters.
```

### Issue #7 — Historical Family Recurrence is not operationalized tightly enough (severity: major)

**问题**: The memo says recurrence needs `(entity, event_type, date_window)` frequency but does not define the reference set. This can leak future information, double-count wire duplicates, or build recurrence around noisy raw entity strings. It also says "pilot 430 cases + recurrence reference window" without specifying whether the post-event article itself or later follow-ups are excluded.

**建议修改**: Add a recurrence data contract: entity normalization, event-type source, lookback window, exclusion of same-day/post-event/future items, duplicate handling, and sparse-subset construction.

**可 paste 文本**:
```markdown
**Historical Family Recurrence contract.** For each pilot case, recurrence is computed only from CLS items strictly before the pilot case timestamp within the frozen lookback window. The reference table keys are `(normalized_entity_id_or_surface, EventType, month)` and must record the normalization method, duplicate/wire-cluster dedup policy, and exclusion rule for the pilot item and post-event follow-ups. The computation must be reproducible from a frozen CLS mirror hash and must not use future articles relative to the case timestamp.
```

### Issue #8 — Budget cap is token-unstable and omits fixture refresh labeling (severity: major)

**问题**: `$5/factor x 20 rounds` is too concrete for a price surface that changes and a loop whose token use is prompt-size dominated. The entity prompt is very long; each patch scoring round evaluates current/Claude/Codex prompts over train/dev slices, and fixture refresh uses dual-agent labeling. The official DeepSeek page also says the current V4 Pro discount expires on 2026-05-31 15:59 UTC.

**建议修改**: Replace fixed dollar cap with token-accounting cap plus live stop rules. Include fixture-refresh labeling in the estimate.

**可 paste 文本**:
```markdown
**Budget accounting.** The loop budget is tracked in tokens and USD at run time, not as a fixed prose estimate. Each factor config must declare expected input/output tokens per item, number of current/patch evaluations per round, fixture-refresh labeling calls, and cache-hit assumptions. The driver emits live token and USD totals and stops for review if spend exceeds either the token cap or the USD cap under the current provider price table. DeepSeek V4 Pro pricing must be read from the official pricing page on run day because the 75% discount is time-limited.
```

### Issue #9 — Authority's Bloc 3 status is document-inconsistent (severity: minor)

**问题**: Plan §5.1A and PENDING include Authority in the WS0.5 question set, but the frozen shortlist §8 and measurement framework §2 do not list Authority in the baseline Bloc 3 inventory. The memo treats "Bloc 3 Authority" as if it is already a frozen factor. That is a paper/reviewer risk because the factor inventory appears to drift silently.

**建议修改**: State Authority's status precisely: a WS0.5 open item / optional Bloc 3 adjunct requested by plan §5.1A, not one of the four confirmatory factors and not currently restoring P1.

**可 paste 文本**:
```markdown
**Authority status.** Authority is handled in WS0.5 because plan §5.1A/PENDING ask T3 explicitly, but it is not one of the four confirmatory factors and it is not listed in the frozen shortlist's baseline Bloc 3 interaction menu. In this memo, Authority is treated as a candidate Bloc 3 adjunct/covariate for pilot metadata, not as a new confirmatory factor. Text-inferred Authority remains CLS-internal and does not restore P1.
```

## 4. Strengths worth preserving

- The memo correctly refuses to wait for the in-rework Thales production entity pipeline; that is pragmatic under WS4 timing pressure.
- It correctly distinguishes text-inferred Authority from genuine extra-corpus Authority and avoids pretending P1 is restored.
- The T3 Track B author-coverage probe is the right first empirical check before spending time on publisher-authority mapping.
- The deliverable layout under `config/factors/`, `scripts/`, and `data/factors/` is close to what WS4 needs, once schema/quota/replay artifacts are added.
- The auto-tune section correctly recognizes static-fixture overfitting as a risk; it just needs a stricter validation design.

## 5. Final verdict

**Verdict**: MAJOR-REVISIONS-NEEDED

**修订后需 re-review 的 section**: §2.1, §2.3, §2.4, §3.1, §3.2, §3.3, §4.2-§4.5, §5, §6, §8.

**建议下一步**:

- Claude should first patch the factual asset errors: topic taxonomy to current 13-class V3, signal profile to current v5.5 two-pass, and quality fixture schema caveat.
- Then patch construct/validation gates: Target Salience target rule, recurrence contract, train/dev/final-holdout auto-tune design, deterministic replay definition, and §6 quota closure criteria.
- Run a second Codex review focused only on the revised sections above. Do not sign WS0.5 until the taxonomy/schema/closure gate changes are in the memo.
