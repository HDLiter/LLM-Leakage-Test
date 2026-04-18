---
title: Phase 7 Pilot Implementation Plan / Phase 7 试运行实施计划
stage: Phase 7
date: 2026-04-17
revision: v2.2
revision_date: 2026-04-18
revision_basis: refine-logs/reviews/PHASE7_PILOT/SYNTHESIS.md + WS0.5 scope deferral (A09 softened)
status: FINAL for scope the plan actually commits to; pending items tracked in root `PENDING.md`
open_decisions_resolved:
  - "OPEN 1: B (Phase 7b contingency)"
  - "OPEN 2: A (zero-shot baseline)"
  - "OPEN 3: A (C_NoOp placebo exploratory)"
deferred_items_tracked_in_PENDING_md:
  - "OPEN 4: audit staffing"
  - "WS0.5: Thales alignment design (T1/T2/T3 verification + reuse-vs-rebuild decision)"
status: DRAFT
depends_on:
  - refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md
  - refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md
  - refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_REVIEW_R2_SYNTHESIS.md
  - config/prompts/R5A_OPERATOR_SCHEMA.md
supersedes: none
owner: ML research engineering + statistics working draft
---

# Phase 7 Pilot Implementation Plan

## 1. Purpose and Operating Position

Phase 7 is the first implementation phase after the R5A conceptual freeze on 2026-04-16. The pilot is a **Stage 1 execution** in a two-stage adaptive pre-registration workflow. Its job is to prove that the frozen measurement stack can be executed, audited, and analyzed on real Chinese financial news at controlled scale. Its outputs are:

- runnable operator and perturbation pipelines;
- adjudicated quality-gate evidence for `C_FO` and `C_NoOp`;
- pilot effect-size estimates and covariance structure;
- a power model for the 2,560-case main run;
- a constrained Stage 2 decision surface that is frozen before Phase 8.

Phase 7 is **not** the main benchmark and not a license to revise the frozen shortlist ad hoc. It exists to estimate operational variance, effect magnitudes, and gate failures under a pre-specified protocol. Because the current `src/` tree still reflects earlier single-model work, Phase 7 should build a parallel `src/r5a/` namespace instead of mutating the legacy pipeline into the new shape.

## 2. Scope

### 2.1 In scope

| Area | Included in Phase 7 |
|---|---|
| Confirmatory operators | `P_logprob` on 5 white-box models and `P_predict` on all 9 fleet models |
| Confirmatory perturbations | `C_FO` and `C_NoOp`, including generation metadata, human audit, and quality gates |
| Pilot execution | One default `N=100` pilot manifest from CLS-source Chinese financial news |
| Analysis | Pilot effect sizes, confirmatory-estimand correlation matrix, baseline-confidence sensitivity, post-cutoff negative control, simple baseline predictors, Stage 2 power simulation |
| Reproducibility | model/version pinning, API fingerprint logging, seed/cache policy, manifest hashing, per-provider concurrency caps |
| Documentation | Stage 1 pre-registration, Stage 2 pre-registration skeleton, decision memos required by pilot triggers |

### 2.2 Out of scope

| Area | Explicitly not covered in Phase 7 |
|---|---|
| Main run | No 2,560-case execution in this phase |
| Full exploratory stack | `E_SR`, `E_EAD_t`, `E_EAD_nt`, `E_ADG`, `E_extract`, and `E_schema_cont` do not get full production runs unless a pre-specified trigger forces promotion work after the core pilot is already green |
| English expansion | No bilingual or English corpus work |
| Non-financial negative control | `BL3` is stretch only; it is not a Phase 8 gate unless a low-cost corpus is already available |
| Large UI product work | No bespoke labeling platform beyond a lightweight local review app and audit export tools |
| Model-fleet changes | No changes to the frozen 9-model fleet unless a provider becomes unavailable and a separate `DECISION_20260417_*` memo is approved |

### 2.3 Why the default pilot size is 100

`N=100` is the default arbitration point because it balances four constraints at once:

1. It is large enough to estimate variance and cross-estimand correlation rather than only surfacing obvious bugs.
2. It keeps full `C_FO` and `C_NoOp` human audit feasible, including double review and adjudication, within one sprint.
3. It limits black-box API spend and rerun overhead while still covering the 9-model fleet and both perturbations.
4. It can satisfy the pilot effective sample-size requirement `min cell >= 15` after pre-specified bin collapsing for each confirmatory estimand × factor × model check.

If the candidate pool cannot satisfy the sample-size matrix at `N=100`, the first remedy is **not** to expand to 150 automatically. The first remedy is to rebalance the pilot manifest while preserving the total size. Only if rebalancing fails should the team open a decision memo on pilot expansion.

## 3. Implementation Principles

### 3.1 Build the R5A stack in a new namespace

Phase 7 should add a parallel namespace:

```text
src/r5a/
  contracts.py
  fleet.py
  runtime.py
  backends/
  operators/
  perturbations/
  estimands/
  audit/
  analysis/
```

Legacy files such as `src/pilot.py` and `src/llm_client.py` may be reused as reference code, but they should not remain the authoritative implementation once the R5A namespace exists.

### 3.2 Freeze semantics, not deployment adapters

The semantic layer is defined by `config/prompts/R5A_OPERATOR_SCHEMA.md`. Per-model provider adapters may differ in JSON formatting support, seed support, and fingerprint fields, but the measurement semantics must not vary by model family.

### 3.3 Use manifests, not ad hoc run state

Every run should be determined by a case manifest, fleet manifest, runtime config, prompt/version manifest, perturbation manifest, and run manifest. Pilot outputs may update only the Stage 2 fields allowed by the two-stage protocol: effect-size priors, power calculations, quality-gate outcomes, redundancy regrouping, and reserve promotions under frozen triggers.

## 4. Workstream Map

| WS | Goal | Primary outputs | Depends on | Parallelizable |
|---|---|---|---|---|
| WS0 | R5A scaffolding and manifests | `src/r5a/` skeleton, fleet/runtime configs, contracts, smoke-test harness | none | starts immediately |
| WS0.5 | Thales alignment and factor pipelines (scope TBD; see Section 5.1A and `PENDING.md`) | decision memo + factor values deterministically computable; specifics deferred | WS0 contracts freeze | parallel with WS1/WS2/WS3; must close before WS4 |
| WS1 | `P_logprob` pipeline | white-box logprob traces, `E_CTS`, `E_PCSG` tables | WS0 | parallel with WS0.5/WS2/WS3 after contracts freeze |
| WS2 | `P_predict` pipeline | 9-model prediction records, parser, cache/fingerprint layer | WS0 | parallel with WS0.5/WS1/WS3 |
| WS3 | `C_FO` + `C_NoOp` generation and audit | perturbation artifacts, audit app, adjudicated pass-rate tables | WS0; reads event-type labels from WS0.5 before C_FO rule schema freeze | parallel with WS0.5/WS1/WS2 |
| WS4 | `N=100` pilot execution | frozen manifest, operator outputs, estimand tables, QC report | WS0.5, WS1, WS2, WS3 | limited; run orchestration depends on all four |
| WS5 | Pilot statistics and pre-registration | power simulation, baseline ablations, Stage 1 sign-in, Stage 2 skeleton | WS4 data complete | mostly sequential |

The intended critical path is:

`WS0 -> (WS0.5 + WS1 + WS2 + WS3) -> WS4 -> WS5`

The ML Engineer feasibility gate should occur twice:

- after WS0 contracts/config freeze, before deep implementation starts;
- after smoke tests in WS1-WS3, before the full 100-case pilot is launched.

## 5. Workstream Details

## 5.1 WS0: R5A scaffolding, manifests, and contracts

### Deliverables

| Type | Path | Purpose |
|---|---|---|
| code | `src/r5a/contracts.py`, `src/r5a/fleet.py`, `src/r5a/runtime.py` | typed contracts plus shared fleet/runtime loaders |
| config | `config/fleet/r5a_fleet.yaml`, `config/runtime/r5a_runtime.yaml`, `config/pilot_sampling.yaml` | authoritative model/runtime/sampling registry |
| doc | `docs/DECISION_20260417_phase7_interfaces.md` | signs off interface names and manifest fields before feature work |

### Steps and decision points

1. Create `src/r5a/` and define data contracts before implementing any operator.
2. Encode the frozen fleet in `config/fleet/r5a_fleet.yaml`, including fields: `model_id`, `family`, `access`, `provider`, `cutoff_date`, `thinking_policy`, `supports_logprob`, `tokenizer_family`, `api_model_name`, and `route_lock_required`.
3. Treat `config/fleet/r5a_fleet.yaml` as the only source of truth for per-model and per-operator behavior. Thinking controls, prompt overlay policy, route locks, echo support, and offline fallbacks must be resolved from this file rather than duplicated in prose or adapter-specific constants.
4. Encode runtime defaults in `config/runtime/r5a_runtime.yaml`. This must include:
   - `deepseek.max_concurrency: 20`
   - `vllm.max_concurrency: 16`
   - conservative starting caps for OpenAI and Anthropic
   - `trust_env: false`
   - `proxy: none`
   - cache mode and seed policy.
5. Freeze the manifest schema with hashable fields. A run manifest must include prompt versions, config hashes, model fingerprints, Docker image digests for white-box endpoints, and git commit SHA of the repository.
6. Add a smoke-test harness `scripts/smoke_phase7.py` that validates the fleet manifest, loads the runtime config, and checks one request path per provider.
7. Before WS2 deep implementation is considered open, run a minimal nine-model `P_predict` feasibility smoke with the frozen zero-shot baseline prompt. The WS0 feasibility gate requires all 9 models to achieve strict-JSON parse success `>= 95%` on a 20-case smoke set, using adapter hardening only and no semantic prompt edits.

Decision point: if the WS0 interface review reveals that `src/llm_client.py` cannot be safely wrapped without invasive edits, treat it as legacy code and build provider adapters directly under `src/r5a/backends/`.

### Exit criteria

- `src/r5a/` namespace exists and imports cleanly.
- Fleet and runtime manifests validate with no missing required fields.
- Smoke harness completes at least one provider handshake for local vLLM and one API provider.
- The WS0 feasibility gate records `>= 95%` strict-JSON parse success on the frozen zero-shot 20-case `P_predict` smoke set.
- `docs/DECISION_20260417_phase7_interfaces.md` is signed before WS1-WS3 full coding starts.

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| interface drift or legacy coupling | merge friction and hidden task leakage | freeze contracts first and keep new code under `src/r5a/` |
| provider config duplicated in code | poor reproducibility | centralize model/runtime settings in YAML and persist resolved config in every run manifest |

## 5.1A WS0.5: Thales alignment prerequisites (scope TBD)

### Status

**Scope deferred.** The four confirmatory factors (Cutoff Exposure, Historical Family Recurrence, Target Salience, Template Rigidity) and several Bloc 3 factors (Structured Event Type, Disclosure Regime / Modality, Authority) have potential reuse paths through the companion project at `D:\GitRepos\Thales\`, but the reuse-vs-rebuild decision, the deliverable list, the file layout, and the effort estimate are all **open and intentionally unspecified** in this revision of the plan.

WS0.5 is reserved as a named workstream so that downstream sections (Section 4 workstream map, Section 6.3 factor quotas, Section 11.1 time budget, Section 12 risks, Section 13 exit gate, Section 14.4 sign-off checklist) can reference "the factor-pipeline gate" without presupposing a specific implementation. The substantive design — what to reuse, what to rebuild, how to validate, and how much effort to budget — will be resolved in a separate working session and recorded in a dedicated decision memo before pilot manifest freeze.

### Verification questions to carry into that session

These three questions are the inputs the follow-up session needs. They are recorded here as a briefing note, not as a commitment to any particular resolution path.

| ID | Question |
|---|---|
| T1 | Has Thales's topic-classification pipeline (EventType taxonomy) already been executed against the CLS v3 raw corpus with outputs persisted on disk, or does it need to be run on the R5A sample? |
| T2 | Does Thales provide (or can it easily derive) an `(entity, event_type, date_window)` frequency index over CLS suitable for `historical_family_recurrence`? |
| T3 | Does CLS raw data preserve publisher metadata at meaningful coverage, such that Bloc 3 Authority can be operationalized as a genuinely extra-corpus factor instead of text inference? |

### What is intentionally not fixed here

- deliverable list, file paths, and scorer interfaces;
- whether factor schemas live in `config/factors/` or inside existing config directories;
- the effort estimate (the range is a function of the T1/T2/T3 answers);
- whether Authority is preserved as Bloc 3, demoted, or redefined;
- whether any part of WS0.5 runs before WS0 contracts freeze or only after.

### Open-item pointer

The live tracking entry for this workstream lives in `PENDING.md` at the repo root. That entry is authoritative for status. Do not treat this section as a prescription.

### Gate behavior

WS0.5 must close before pilot manifest freeze (Section 6) and before Section 14.4 sign-off can be completed. "Close" here means: a decision memo exists, the factor values the pilot depends on are deterministically computable, and the chosen path has passed whatever validation the follow-up session defines.

## 5.2 WS1: `P_logprob` white-box pipeline

### Deliverables

| Type | Path | Purpose |
|---|---|---|
| code | `src/r5a/operators/p_logprob.py`, `src/r5a/backends/vllm_logprob.py`, `src/r5a/analysis/logprob_metrics.py` | operator, backend, and `E_CTS`/`E_PCSG` calculations |
| config | `config/models/*.yaml` for the 5 white-box checkpoints | white-box checkpoint pinning |
| data | `data/pilot/logprob_traces/*.parquet` | token-level traces |

### Required implementation shape

`src/r5a/operators/p_logprob.py` should expose a contract close to:

```python
class PLogprobOperator:
    def compute(
        self,
        articles: list[ArticleRecord],
        model_id: str,
        batch_size: int,
    ) -> list[LogProbTrace]:
        ...
```

`LogProbTrace` must minimally store case/model IDs, tokenizer provenance, raw token IDs, token logprobs, token count, thinking mode, and request fingerprint.

All `P_logprob` request-time controls must be read from `config/fleet/r5a_fleet.yaml` `models.<model_id>.p_logprob`. The required prompt-logprob request/response contract is:

| Contract element | Required value |
|---|---|
| request | `echo=True`, `max_tokens=0`, `logprobs=True`, `top_logprobs=5` |
| response trace row | `token`, `logprob`, `top_logprobs` (list) |
| fallback | if `echo=True` is not supported by a given endpoint, use an offline HF scorer with the same checkpoint SHA and tokenizer SHA |

Known risk: some endpoints, especially `GLM-4-9B`, may not expose prompt-side `echo=True` cleanly through vLLM. That is an adapter/runtime issue, not a reason to change the operator semantics.

### Steps and decision points

1. Implement `VLLMLogprobBackend` against the **completion** endpoint rather than the chat endpoint. Do not rely on DeepSeek logprobs.
2. Resolve per-model `P_logprob` behavior from `config/fleet/r5a_fleet.yaml` `models.<model_id>.p_logprob`, including `thinking_control`, `route_lock_required`, `echo_supported`, and any fallback scorer.
3. Build tokenizer pinning into the model config. Each white-box model config should store both model checkpoint SHA and tokenizer SHA so paired comparisons can verify tokenizer identity rather than infer it from model family names.
4. Enforce thinking-off policy at the backend layer. For Qwen3 models this must be explicit; for other white-box models the run manifest should still store `thinking_mode: off`.
5. Persist traces in `Parquet`; the same trace must feed `E_CTS` and `E_PCSG`.
6. Implement `compute_cts(trace, frequency_table)` and `compute_pcsg(trace_late, trace_early)` from saved traces, not separate reruns.
7. Create a 30-case smoke benchmark covering both Qwen tokenizer families and GLM.

Decision point: if prompt-logprob extraction through vLLM is incomplete or misaligned for any white-box model by the end of the smoke test, switch that model to an offline HF forward scorer while keeping the same pinned checkpoint and tokenizer SHA. This fallback is acceptable for pilot as long as the run manifest records the backend change.

### Exit criteria

- All 5 white-box models return valid prompt-side token logprobs on the 30-case smoke set.
- `article_token_count` matches the tokenizer-encoded length within a deterministic tolerance of at most one BOS/EOS handling difference, and the difference rule is documented.
- Thinking mode is logged as `off` for 100% of traces.
- `E_CTS` and `E_PCSG` tables can be generated end-to-end for the smoke set with no missing pair rows on the two temporal Qwen pairs.
- Full pilot run later yields less than 1% un-recovered trace failures after retries.

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| backend or tokenizer mismatch | invalid or missing `P_logprob` traces | use completion endpoint first, validate tokenizer SHA equality, keep offline HF fallback |
| local GPU instability on 14B models | run failures or OOM | cap concurrency at 16, queue models separately, allow cloud fallback while preserving checkpoint SHA |

## 5.3 WS2: `P_predict` nine-model pipeline

### Deliverables

| Type | Path | Purpose |
|---|---|---|
| code | `src/r5a/operators/p_predict.py`, `src/r5a/parsers/p_predict.py` | prediction operator and strict parser |
| code | `src/r5a/backends/openai_compatible.py`, `src/r5a/backends/openai_native.py`, `src/r5a/backends/anthropic_native.py` | provider adapters with fingerprint capture |
| data | `data/pilot/predict/*.jsonl` | raw and parsed model outputs |

### Required implementation shape

`src/r5a/operators/p_predict.py` should expose:

```python
class PPredictOperator:
    def predict(
        self,
        article: ArticleRecord,
        model_id: str,
        prompt_version: str,
        variant_id: str = "baseline",
    ) -> PredictRecord:
        ...
```

`PredictRecord` must minimally store case/model/variant IDs, direction, confidence, both explicit-memory flags, evidence quotes, parse status, retry count, seed, request fingerprint, and cache key.

All `P_predict` defaults must be read from `config/fleet/r5a_fleet.yaml` `models.<model_id>.p_predict`. This includes `thinking_control`, prompt overlay policy, provider routing, and whether the baseline prompt is used without modifiers.

### 5.3A Baseline prompt freeze and zero-shot contract

The baseline `P_predict` template is frozen as **zero-shot**: task instruction plus a single article, with no few-shot examples. Output must satisfy the strict JSON schema in `config/prompts/R5A_OPERATOR_SCHEMA.md`.

`E_ADG` is not allowed to mutate the baseline template in place. It must be implemented as a separate prompt modifier or overlay layer that composes on top of the frozen zero-shot baseline contract and is versioned independently.

### Steps and decision points

1. Implement provider-specific adapters under `src/r5a/backends/` instead of forcing every provider through the existing `LLMClient`.
2. Resolve the thinking-mode policy by operator from `config/fleet/r5a_fleet.yaml`, not by ad hoc provider branches. `P_predict` uses each model’s default deployed mode, while `P_logprob` is always thinking off.
3. Implement strict JSON parsing using the frozen zero-shot `P_predict` schema in `R5A_OPERATOR_SCHEMA.md`. Allow one repair retry if JSON is malformed, but do not change prompt semantics, task description, or add few-shot examples.
4. Add Challenger `B3` support in two layers: the structured JSON field and a raw-response heuristic scan for phrases such as `我记得`, `训练数据`, `I recall`, and `from training`.
5. Implement seed and cache policy. The local cache key must include prompt version, model ID, provider route, variant ID, seed, and article hash. For providers that support request seeds, pass the seed explicitly. For providers that do not, record `seed_supported: false` in the fingerprint.
6. Mitigate Challenger `B4` by randomizing request order and forcing a small duplicate subset with local-cache bypass. The duplicate subset should be 5% of pilot requests or at least 10 requests per provider.
7. Log provider fingerprint fields. Capture model string, provider response ID, system fingerprint if available, created timestamp, route/provider name, and HTTP header metadata relevant to versioning.

Decision point: if any provider falls below 95% valid JSON rate on the 20-case zero-shot smoke test, add a deployment-layer adapter change only. Do not alter the semantic prompt body unless a separate decision memo is approved.

### Exit criteria

- All 9 models pass a 20-case zero-shot smoke test with at least 95% valid JSON on first pass and at least 99% after one repair/retry cycle.
- `explicit_memory_reference` or `explicit_memory_reference_heuristic` is populated for 100% of parsed records.
- Provider fingerprint coverage is 100% for all successful calls.
- DeepSeek concurrency is capped at 20 and vLLM at 16 in code and runtime config.
- No request path relies on proxy inheritance; adapters explicitly set `proxy=None` and `trust_env=False` where applicable.

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| schema drift or hidden server cache | parse failures or compressed deltas | keep semantic layer fixed, randomize order, use duplicate reruns with cache bypass |
| rate limits or API instability | pilot delays | provider semaphores, exponential backoff, run-level resume support |

## 5.4 WS3: `C_FO` and `C_NoOp` perturbation generation plus human audit

### Deliverables

| Type | Path | Purpose |
|---|---|---|
| code | `src/r5a/perturbations/c_fo.py`, `src/r5a/perturbations/c_noop.py`, `src/r5a/perturbations/shared.py` | generation logic and diff metadata |
| config | `config/perturbations/c_fo_rules.yaml`, `config/perturbations/c_noop_clause_bank.yaml` | rule tables and deterministic clause bank |
| code | `scripts/build_perturbation_audit_batch.py`, `scripts/merge_perturbation_audit.py`, `scripts/audit_app.py` | audit export, merge, and UI |
| data | `data/pilot/perturbations/*.jsonl`, `data/pilot/audit/*.jsonl` | artifacts and adjudicated labels |

### Required implementation shape

Each perturbation artifact should be represented as:

```python
class PerturbationArtifact(BaseModel):
    case_id: str
    perturbation_id: str
    event_type: str
    eligible: bool
    source_text: str
    perturbed_text: str
    edit_spans: list[SpanEdit]
    rationale: str
    metadata: dict[str, Any]
```

The generation functions should look like:

```python
def generate_false_outcome(article: ArticleRecord, rules: FORuleSet) -> PerturbationArtifact: ...
def generate_noop(article: ArticleRecord, bank: NoOpClauseBank) -> PerturbationArtifact: ...
```

### 5.4A Admissibility field contract

`PerturbationArtifact.metadata` is not free-form for gate-relevant fields. It must at least reserve the following keys:

| Field | Type | Applies to | Meaning |
|---|---|---|---|
| `verified_outcome` | bool | `C_FO` | whether the article contains a verified true outcome |
| `fo_slotable` | bool | `C_FO` | whether a clean, replaceable outcome slot exists |
| `fo_slot_topology` | enum | `C_FO` | one of `single-point`, `multi-point-linked`, `narrative-entailed` |
| `slot_span` | object | `C_FO` | character start/end span for the edited outcome slot |
| `ineligible_reason` | string | `C_FO` and `C_NoOp` | required whenever `eligible=false` or `fo_slotable=false` |
| `host_category` | enum | `C_NoOp` | one of `policy`, `corporate`, `industry`, `macro` |
| `noop_bank_id` | string | `C_NoOp` | clause-bank identifier used for the insertion |
| `noop_eligibility_rule_id` | string | `C_NoOp` | category-specific admissibility rule that was passed |
| `placebo_variant` | enum | `C_NoOp` | one of `none`, `c_noop`, `c_noop_placebo` |

`slot_span` should be stored as character offsets relative to `source_text`. For `multi-point-linked` and `narrative-entailed` slots, the primary span must still be recorded and any linked spans should be enumerated in `edit_spans`.

### 5.4B Host-aware `C_NoOp` library and exploratory placebo

`C_NoOp` should use a **host-aware insertion library** rather than one global clause bank. Maintain separate clause banks and eligibility rules for `policy`, `corporate`, `industry`, and `macro` hosts. The insertion rule for a case is valid only if the selected clause matches the article’s host category and preserves the local register of that category.

Add an exploratory-only variant `C_NoOp_placebo`: a length-matched null edit such as a neutral filler clause or repetition of a semantically empty short phrase already compatible with the article’s register. `C_NoOp_placebo` is used only for secondary robustness identification, does **not** enter the confirmatory family, and does **not** trigger the `E_NoOp` quality gate.

Throughout Phase 7, `E_NoOp` should be described as a **robustness / template-brittleness signal**, not as direct memorization evidence.

### Steps and decision points

1. Define the pilot event-type taxonomy before generating any perturbation and write any collapse rule to `docs/DECISION_20260417_pilot_event_taxonomy.md`.
2. Implement `C_FO` as rule-based slot editing only. The generator must record `verified_outcome` and `fo_slotable` separately, must replace only verified known outcomes, and must refuse generation when the slot cannot be localized cleanly.
3. Implement `C_NoOp` as deterministic insertion from a versioned, host-aware clause bank. Insertion should happen in a medial position only, should record the exact insertion index, and should log the category-specific bank and eligibility rule used.
4. Emit machine-readable diff metadata for every edit. This is required for the human audit UI and for debugging failure cases.
5. Audit **all** pilot-generated `C_FO` and primary `C_NoOp` variants rather than a subsample. `C_NoOp_placebo` is exploratory-only and should be generated only after the confirmatory `C_NoOp` artifacts are frozen.
6. Compute the frozen quality-gate thresholds from adjudicated labels and later pilot deltas. `C_NoOp_placebo` summaries must be reported separately and must not be folded into the confirmatory gate denominator.

Decision point: if the pool cannot yield at least 60 pre-cutoff cases with `verified_outcome=true` and enough `fo_slotable=true` cases for clean `C_FO` edits, rebalance the sample before reducing the perturbation. Do not weaken the edit rules to “make quota.”

### Exit criteria

- `C_FO` generator produces eligible artifacts for at least 60 pre-cutoff pilot cases and stores `verified_outcome`, `fo_slotable`, `fo_slot_topology`, `slot_span`, and `ineligible_reason`.
- `C_NoOp` generator produces eligible artifacts for at least 90 of 100 pilot cases, with the target goal being full coverage, and records `host_category`, `noop_bank_id`, and `noop_eligibility_rule_id`.
- Every perturbation artifact stores event type, edit span metadata, and generator version.
- Human audit labels exist for every generated pilot artifact.
- Cohen’s kappa on adjudication-free pass/fail labels is at least 0.70 overall for each perturbation, with dimension-level kappa not falling below 0.60. Lower agreement triggers rubric repair and re-audit before the gate can be evaluated.

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| ambiguous `C_FO` slots or cue-leaking `C_NoOp` clauses | low eligibility or false signal | separate `verified_outcome` from `fo_slotable`, use host-aware clause banks, reject ambiguous edits, and audit all confirmatory variants |
| reviewer disagreement | unreliable quality gate | double review all items, adjudicate formally, version the rubric |

## 5.5 WS4: `N=100` pilot execution

### Deliverables

| Type | Path | Purpose |
|---|---|---|
| code | `scripts/sample_phase7_pilot.py`, `scripts/check_pilot_cells.py`, `scripts/run_phase7_pilot.py` | sampling, cell checking, and orchestration |
| data | `data/pilot/manifests/pilot_100_cases.json`, `data/pilot/results/*.parquet` | frozen case manifest and outputs |
| data | `data/pilot/runstate.db` | request-item lineage, resume state, and retry bookkeeping |
| doc | `docs/DECISION_20260417_pilot_manifest.md`, `data/pilot/reports/pilot_qc_report.md` | signed manifest and QC summary |

### 5.5A Request-item lineage and resume state

Resume must operate at the **request-item** level rather than at the coarse run level. Every API call or white-box scoring request should receive a UUID `request_id` and a state drawn from:

- `pending`
- `success`
- `retryable`
- `terminal_skipped`

Persist this state in SQLite at `data/pilot/runstate.db`. The required schema includes:

```text
request_id, case_id, model_id, operator, perturbation_variant, status,
retry_count, fingerprint, seed_requested, seed_supported, seed_effective,
response_id, ts_start, ts_end
```

The orchestration layer should treat `baseline`, `C_FO`, `C_NoOp`, and `C_NoOp_placebo` requests as first-class request items under the same lineage model.

### Steps and decision points

1. Build the pilot manifest from CLS-source Chinese financial news using the sampling plan in Section 6.
2. Compute the effective sample-size matrix **before** any model run. If any confirmatory estimand × factor × model cell is below 15, rebalance the manifest and rerun the checker.
3. Freeze the pilot manifest by writing per-case hashes, publish dates, target strings, factor bins, and perturbation eligibility flags.
4. Initialize `data/pilot/runstate.db` and issue a UUID `request_id` for every planned baseline and perturbation request before launch.
5. Run `P_logprob` on the 5 white-box models for baseline articles only.
6. Run `P_predict` baseline on all 9 models.
7. Run `P_predict` on `C_FO` and `C_NoOp` variants after audit-approved artifacts are available. Run `C_NoOp_placebo` only after the confirmatory perturbation branch is frozen and only for secondary analysis.
8. Execute the duplicate-subset reruns for cache and seed diagnostics. The diagnostic subset must cover both baseline requests and matched baseline-plus-perturbation delta requests.
9. Assemble estimand tables under `src/r5a/estimands/confirmatory.py` or an equivalent module. The pilot must yield usable tables for `E_CMMD`, `E_PCSG`, `E_CTS`, `E_FO`, and `E_NoOp`.
10. Produce a QC report summarizing parse rates, trace success, missingness, audit gates, duplicate-rerun stability, and request-lineage completeness.

Decision point: if any confirmatory operator has unresolved missingness above threshold after retries, the pilot is not “done” and WS5 should not start.

### Exit criteria

- A 100-case manifest is frozen and signed.
- The effective sample-size checker reports `min cell >= 15` after approved bin-collapsing rules.
- End-to-end missingness is below 2% per operator × model cell after retries.
- `data/pilot/runstate.db` exists and every launched request has a terminal lineage state with no orphan `pending` rows at pilot closeout.
- Duplicate reruns show no provider-specific drift severe enough to invalidate delta interpretation. A practical threshold is absolute direction disagreement under 5% on duplicate baseline prompts for deterministic providers; any breach must be written up in the QC report.
- All five confirmatory estimands are materialized as analysis-ready tables, even if some later fail quality gates and become exploratory.

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| weak date-window coverage or provider failure | incomplete temporal contrasts or partial pilot | stratify by date window, checkpoint every chunk, and resume from request-item state in `runstate.db` |
| audit lags execution | invalid perturbation branch | do not launch perturbation scoring until adjudicated audit artifacts are frozen |

## 5.6 WS5: pilot statistics, power analysis, and two-stage pre-registration

### Deliverables

| Type | Path | Purpose |
|---|---|---|
| code | `src/r5a/analysis/pilot_effects.py`, `correlation.py`, `baselines.py`, `power.py` | effect-size estimation, redundancy checks, baselines, and power simulation |
| code | `scripts/simulate_phase8_power.py` | CLI wrapper for power analysis |
| data | `data/pilot/analysis/*.parquet` | coefficient tables, covariance matrices, simulated power outputs |
| doc | `docs/PREREG_STAGE1_PILOT.md`, `docs/PREREG_STAGE2_MAIN_SKELETON.md`, `docs/CAVEAT_model_capability.md` | preregistration and B1 caveat |

### Steps and decision points

1. Write `PREREG_STAGE1_PILOT.md` before the first full 100-case run.
2. Estimate pilot coefficients and standardized effect sizes for every confirmatory estimand × factor target.
3. Compute the pairwise correlation matrix over the 5 confirmatory estimands on the common eligible subset. If the frozen automatic regrouping rule in Section 8.4 fires, retain `E_PCSG` as confirmatory and demote `E_CTS` to corroborative without opening a memo.
4. Add Challenger `B1` by creating a `model_capability` covariate table sourced from pre-registered benchmark scores such as CFinBench or another explicitly documented Chinese-finance-capable benchmark. Store raw score, normalized score, source date, and any interpolation notes.
5. Add Challenger `C3` by defining a baseline-confidence covariate and a percentile-based mid-range sensitivity check. This is sensitivity-only and must not reparameterize the primary confirmatory family.
6. Run `BL1` simple baseline predictor models, the `BL2` post-cutoff negative control checks, and the exploratory `C_NoOp_placebo` robustness-identification summary. The placebo branch must be reported as secondary analysis only.
7. Simulate main-run power at `N=2560` under the legal Stage 2 family states using scenario-based priors, observed variance components, and empirical cross-estimand covariance under Westfall-Young stepdown max-T.
8. Populate the Stage 2 preregistration skeleton with only the fields the Stage 1 protocol allows to change.

Decision point: if pilot-implied power for the 2,560-case main run is too low for the retained confirmatory family under the scenario range, the team must either narrow the family under the frozen demotion rules or reopen sample-size planning. Phase 8 should not start on a single optimistic perturbation-rich point estimate.

### Exit criteria

- `PREREG_STAGE1_PILOT.md` is dated and signed before the full pilot run.
- Pilot effect-size and covariance tables are reproducibly generated from saved artifacts.
- Correlation matrix and regrouping trigger are evaluated and documented.
- `model_capability` covariate table exists with benchmark provenance and caveat text.
- Main-run power simulation for `N=2560` is complete and linked from the Stage 2 prereg skeleton, with scenario-based prior ranges, Monte Carlo error summaries, and realized missingness.
- The exploratory `C_NoOp_placebo` summary is published separately from the confirmatory family and excluded from gate and power calculations.

### Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| noisy pilot variance or incomplete capability benchmarks | unstable power or weak B1 covariate | use bootstrap intervals, scenario-based priors, and pre-register fallback benchmark sources |
| high confirmatory redundancy | wasted alpha in Phase 8 | regroup only through the frozen `r > 0.8` trigger |

## 6. Pilot Case Sampling Strategy (`N=100`)

### 6.1 Source and philosophy

The pilot should use Chinese CLS-style financial news as the primary source. Existing assets such as `data/seed/test_cases_v3.json` may be reused, but the pilot manifest must not be limited to them if that weakens date-window coverage or perturbation eligibility. Sampling should be handled by a new script:

```python
# scripts/sample_phase7_pilot.py
def build_pilot_manifest(config_path: str) -> list[PilotCase]:
    ...
```

The script should pull from:

- existing seed cases already in the repository;
- CLS raw archive if additional cases are needed for date windows, event-type quotas, or perturbation eligibility.

### 6.2 Proposed manifest composition

The default 100-case pilot manifest should target:

| Bucket | Count | Rationale |
|---|---|---|
| Pre-cutoff, verified-outcome, perturbation-rich | 60 | supports `C_FO` eligibility, `C_NoOp`, and main temporal analyses |
| Pre-cutoff, factor-coverage supplement | 20 | broadens factor range without forcing all cases into `C_FO` |
| Post-cutoff negative controls | 20 | supports `BL2` and sanity-checks false temporal signal |

Within the 80 pre-cutoff cases, date windows should be balanced as follows:

| Date window | Target count | Why it matters |
|---|---|---|
| `<= 2023-10-31` | 20 | before the earliest Qwen temporal-pair cutoff; low expected temporal advantage |
| `2023-11-01` to `2024-06-30` | 30 | between early Qwen2.5 and mid-2024 models; supports monotone exposure contrasts |
| `2024-07-01` to `2025-01-31` | 30 | between mid-2024 and Qwen3 cutoffs; critical for temporal-pair A/B |
| `>= 2026-02-01` | 20 | post-cutoff negative controls with at least a 6-month safety gap after the latest approximate core-fleet cutoff (`Claude Sonnet 4.6 ~ 2025-08`) |

These windows ensure enough “between-cutoff” cases for temporal contrasts, enough “before all” cases for low-signal anchors, and enough “after all” cases for negative controls.

### 6.3 Factor and event-type quotas

Factor values and event-type labels are produced by the WS0.5 factor pipeline (see Section 5.1A; scope TBD). The sampling script must consume a frozen factor schema from WS0.5 rather than hard-coding bin thresholds; the exact schema file and path are determined by the WS0.5 follow-up session. The sampling script should enforce four additional quota families:

1. Each top-level news category (`policy`, `corporate`, `industry`, `macro`) should appear at least 15 times.
2. The pilot event-type taxonomy used for `C_FO` should have at least 12 cases per super-type if five super-types are used, or at least 15 per super-type if collapsed to four.
3. For each core case-level factor after pilot binning, both sides of the binary split should retain at least 20 pre-cutoff cases overall and at least 15 `C_FO`-eligible cases where `E_FO` needs them.
4. `C_FO` feasibility must be tracked as a two-step funnel: `verified_outcome` counts and `fo_slotable` counts should both be reported before manifest freeze, rather than collapsing them into one eligibility number.
5. `C_NoOp` host-aware clause-bank eligibility should be tracked by category. The manifest should record the intended host category for every pre-cutoff case so each of `policy`, `corporate`, `industry`, and `macro` has auditable insertion coverage.
6. The post-cutoff bucket should preserve the same broad category mix as the pre-cutoff bucket as much as corpus availability allows.

### 6.4 Effective sample-size matrix (`B2`)

`scripts/check_pilot_cells.py` should compute:

```text
n_eff(estimand, factor_bin, analysis_unit)
```

using the actual eligibility mask and the estimand-specific analysis unit:

| Estimand | Analysis unit for `n_eff` | Eligibility mask |
|---|---|---|
| `E_CTS` | case × model | all 100 cases on the 5 white-box models |
| `E_PCSG` | case × tokenizer-matched pair | white-box same-tokenizer temporal pairs only |
| `E_CMMD` | case | all 100 cases after fleet aggregation |
| `E_FO` | case × model | `C_FO`-eligible subset |
| `E_NoOp` | case × model | `C_NoOp`-eligible subset |

For case × model estimands, `n_eff` counts eligible case-model rows after fixed model availability is applied. For `E_PCSG`, the unit is a tokenizer-matched temporal pair rather than an individual model. For `E_CMMD`, the unit is the fleet-aggregated case, so the checker should not fabricate a model dimension that the estimand no longer has.

The rule is:

- target pilot design: all factor bins support `n_eff >= 20`
- minimum acceptable design: all factor bins support `n_eff >= 15`
- if not, collapse the factor from tertiles to binary median split before increasing `N`

The `15` threshold is a lower-bound stability rule for pilot mixed-model estimation. It is not paper-grade precision; it is a guardrail against obviously underidentified cells.

## 7. Pre-registration Structure (Two-stage Adaptive)

### 7.1 Stage 1: pilot sign-in before execution

`docs/PREREG_STAGE1_PILOT.md` should be committed before the first full pilot run. It must include:

- frozen confirmatory family as inherited from `R5A_FROZEN_SHORTLIST.md`;
- pilot manifest policy and rebalancing rules;
- fleet and thinking-mode policy;
- quality-gate thresholds for `C_FO` and `C_NoOp`;
- seed, cache, fingerprint, and rerun policy;
- effective sample-size matrix rule;
- correlation-regrouping trigger (`r > 0.8`);
- reserve promotion rules exactly as frozen;
- allowed Stage 2 edits and forbidden edits.

Stage 1 should state plainly that the pilot does **not** answer the main paper question. It estimates effect size, operational stability, and admissibility.

The perturbation quality-gate language should quote the frozen shortlist conditions verbatim:

| Estimand | Condition 1 | Condition 2 | Condition 3 |
|---|---|---|---|
| `E_FO` | audit pass rate `>= 85%` overall, no event type `< 75%` | eligible case coverage `>= 60%` of pre-cutoff cases | baseline delta non-degeneracy: `mean |delta| > 0` on `>= 5/9` models |
| `E_NoOp` | audit pass rate `>= 85%` overall, no event type `< 75%` | eligible case coverage `>= 60%` of pre-cutoff cases | baseline delta non-degeneracy: `mean |delta| > 0` on `>= 5/9` models |

### 7.1A Stage 2 family-state table

Stage 1 should freeze the legal Stage 2 confirmatory family states as follows:

| state id | family size | trigger | alpha split |
|---|---|---|---|
| `S20` | 20 coefficients | `E_FO` and `E_NoOp` both pass quality gate | Westfall-Young family-wise `alpha = 0.05` over 20 |
| `S16a` | 16 coefficients | `E_FO` is demoted because the `C_FO` gate fails | Westfall-Young family-wise `alpha = 0.05` over 16 |
| `S16b` | 16 coefficients | `E_NoOp` is demoted because the `C_NoOp` gate fails | Westfall-Young family-wise `alpha = 0.05` over 16 |
| `S12` | 12 coefficients | `E_FO` and `E_NoOp` are both demoted | Westfall-Young family-wise `alpha = 0.05` over 12 |

Any state outside `S20`, `S16a`, `S16b`, and `S12` requires a new decision memo and is not part of the default preregistered path. Pilot cases **MUST** be excluded from all Stage 2 confirmatory analyses regardless of which legal family state is selected.

### 7.1B Evidence package

Stage 1 should contain an explicit evidence package block with the following fields:

| Field | Required content |
|---|---|
| signatories | reviewer and adjudicator names; until OPEN 4 closes use `[TBD pending OPEN 4]` placeholders |
| prereg commit SHA | the final 40-character git commit SHA before execution |
| external anchor | GPG-signed git tag `prereg/phase7-stage1-v1.0` or a third-party timestamp such as OpenTimestamps |
| pilot manifest hash | SHA256 of `data/pilot/manifests/pilot_100_cases.json` |
| audit manifest hash | SHA256 of the audit export JSONL after 100% labeling is complete |
| Phase 8 go/no-go backlink | path or identifier of the Phase 8 memo that cites this evidence package |

### 7.2 Stage 2: main-run preregistration after pilot

`docs/PREREG_STAGE2_MAIN_SKELETON.md` should be prepared in Phase 7 but only completed after the pilot. It may update only:

- which estimands remain confirmatory after quality gates under `S20`, `S16a`, `S16b`, or `S12`;
- whether any reserve estimand is promoted under its frozen trigger and the Phase 7b contingency memo;
- whether the automatic `E_PCSG` / `E_CTS` regrouping rule in Section 8.4 fired;
- pilot-informed power statements and any resulting sample-size or family-size decision;
- prompt adapter hardening only, such as JSON schema wrappers, formatting normalization, or failure-retry strategy;
- final model/version pins and route locks captured at run time.

It may not update:

- the four core factors;
- the meaning of any retained estimand;
- the fleet roster without a separate availability memo;
- semantic prompt wording, task description, or few-shot content;
- statistical tests beyond pre-specified choices.

Any other change path requires a new decision memo rather than a silent Stage 2 edit.

### 7.2A Phase 7b reserve-promotion contingency

Per OPEN 1 = B, reserve promotion is **not** pre-built into the default critical path. If a frozen reserve trigger in `R5A_FROZEN_SHORTLIST.md` Section 4 is hit, the team should open a new memo named `docs/DECISION_20260XXX_phase7b_reserve_*.md`.

The scope of Phase 7b is the minimum runnable implementation of the triggered reserve operator, typically `P_extract` or `P_schema`, and **not** full feature parity with the already-frozen core operators. Phase 7b is explicitly outside the default Phase 7 critical path and does not delay the normal Phase 8 exit-gate timing unless the new memo says otherwise.

### 7.3 Required pilot decision memos

Phase 7 should pre-plan these memo slots:

- `docs/DECISION_20260417_phase7_interfaces.md`
- `docs/DECISION_20260417_pilot_event_taxonomy.md`
- `docs/DECISION_20260417_pilot_manifest.md`
- `docs/DECISION_20260XXX_phase7b_reserve_*.md` if a frozen reserve-promotion trigger fires
- `docs/DECISION_20260417_estimand_regrouping.md` only if a non-default regrouping request is made outside the automatic Section 8.4 tie-break
- `docs/DECISION_20260417_phase8_go_no_go.md`

## 8. Pilot Statistical Analysis Plan

### 8.1 Analysis goals

The pilot analysis has five jobs:

1. estimate operationally relevant effect sizes;
2. determine whether `E_FO` and `E_NoOp` survive confirmatory quality gating;
3. quantify redundancy among confirmatory estimands;
4. test whether simple metadata baselines explain the same variation;
5. project main-run power under the frozen multiplicity procedure.

### 8.1A Estimand-specific analysis units and scalar scores

The confirmatory estimand contract should be frozen before any pilot inference:

| estimand | analysis unit | scalar score | eligibility mask |
|---|---|---|---|
| `E_CTS` | case × model | Min-K++ continuous score (bottom-`K%` average) | all 100 |
| `E_PCSG` | case × tokenizer-matched pair | `logprob(late) - logprob(early)` on matched tokens | white-box same-tokenizer pairs only |
| `E_CMMD` | case (fleet-aggregated) | cross-cutoff separation score across 9-model predictions | all 100 |
| `E_FO` | case × model (`FO`-eligible) | signed-score non-compliance to visible false outcome | `C_FO`-eligible subset |
| `E_NoOp` | case × model (`NoOp`-eligible) | `|signed_base - signed_noop|` absolute stability loss | `C_NoOp`-eligible subset |

For `P_predict`-derived scores, freeze:

```text
signed_score = sign(direction) * logit((confidence + 0.5) / 101)
```

where `confidence` is the parsed `0-100` confidence value from `P_predict`. `E_CMMD` should first map each model prediction to `signed_score`, then aggregate to a case-level cross-cutoff separation score before entering the confirmatory model. `E_NoOp` remains a robustness / template-brittleness signal rather than a direct memorization claim.

### 8.2 Mixed-model form

The confirmatory model family should be parameterized **per estimand**, not forced into one universal `Y_ijm` form. The common fixed-effect skeleton is the same across estimands, but the response notation and random-effect structure follow the analysis unit frozen in Section 8.1A.

For case × model estimands (`E_CTS`, `E_FO`, `E_NoOp`), fit:

```text
score_im^(j) = beta0^(j)
             + beta1^(j) * cutoff_exposure_im
             + beta2^(j) * factor_i
             + beta3^(j) * cutoff_exposure_im * factor_i
             + beta4^(j) * model_capability_m
             + u_i^(j) + v_m^(j) + e_im^(j)
```

For tokenizer-matched pair estimands (`E_PCSG`), fit:

```text
score_ip^(PCSG) = beta0
                + beta1 * cutoff_pair_exposure_ip
                + beta2 * factor_i
                + beta3 * cutoff_pair_exposure_ip * factor_i
                + u_i + v_p + e_ip
```

where `p` indexes a tokenizer-matched temporal pair rather than a model.

For the fleet-aggregated case-level estimand (`E_CMMD`), fit:

```text
score_i^(CMMD) = beta0
               + beta1 * fleet_cutoff_separation_i
               + beta2 * factor_i
               + beta3 * fleet_cutoff_separation_i * factor_i
               + e_i
```

with case-cluster bootstrap inference rather than a model random effect, because the fleet aggregation has already collapsed the model dimension.

Coefficient-of-interest rules:

- for the `Cutoff Exposure` factor, the primary coefficient is `beta1`;
- for the other three factors, the primary pilot coefficient is `beta3`, the interaction with cutoff exposure;
- `E_TDR` remains separate and is represented by its own `cutoff * dose` interaction in exploratory sensitivity models only.

`baseline_confidence` is intentionally excluded from the primary confirmatory parameterization. It enters only through the sensitivity analyses in Section 8.3.

### 8.3 Baseline-confidence covariate (`C3`)

`baseline_confidence` is a sensitivity-only covariate for the `P_predict` family (`E_CMMD`, `E_FO`, `E_NoOp`). It should not appear in the primary confirmatory models in Section 8.2 and should not change confirmatory family membership, quality gates, or power planning.

Within the sensitivity pass, `baseline_confidence_im` should be centered within model to absorb trivial ceiling/floor behavior in `P_predict` outputs. The mid-range sensitivity analysis should retain only observations whose baseline confidence lies between the model-specific 20th and 80th percentiles. Percentile-based bands are preferred over a hard 20-80 numeric threshold because confidence scales can drift by provider.

### 8.4 Confirmatory-estimand correlation matrix (`C1`)

The pilot should compute pairwise Pearson and Spearman correlations across the 5 confirmatory estimands on their common eligible subset after standardizing on the estimand’s own analysis unit. Use bootstrap resampling over cases to obtain stability intervals. The default Stage 1 regrouping rule is deterministic:

- `Pearson r > 0.80`, and
- the sign is stable in at least 90% of bootstrap resamples.

If both conditions hold for the `E_CTS` / `E_PCSG` pair, retain `E_PCSG` as confirmatory and demote `E_CTS` to corroborative automatically, with no memo required. This is the only automatic regrouping rule written into Stage 1. Any other regrouping request requires a new decision memo before Stage 2.

### 8.5 Simple baseline predictors (`BL1`)

The baseline ablation should fit metadata-only models that predict each estimand outcome from:

- cutoff exposure;
- historical family recurrence;
- target salience;
- template rigidity;
- structured event type;
- category and date-window indicators as nuisance controls.

Then fit an augmented model adding model-side covariates and, where relevant, perturbation eligibility. Compare out-of-fold `R^2` or classification loss. The point is to document how much variance is already explained by simple priors.

Add a second, low-cost **text-light challenger** using only the headline plus first sentence (lede), represented with TF-IDF features or a lexicon-based linear model. This challenger should predict either baseline sign or flip-risk, and its out-of-fold `R^2` or classification loss should be reported alongside the metadata-only BL1 model.

Grouped cross-validation must split on the **case** as the grouping unit, not on individual rows. All rows derived from the same article, including model rows and perturbation variants, must stay in the same fold to avoid leakage.

`C_NoOp_placebo` should be analyzed only as a secondary robustness-identification check. Report placebo stability loss next to `E_NoOp`, but keep it outside the confirmatory family, outside quality gates, and outside power planning.

### 8.6 Post-cutoff negative control (`BL2`)

For the 20 post-cutoff controls, rerun the same `E_CMMD` and `E_PCSG` analysis logic. The expected outcome is near-zero temporal signal because all relevant models should lack exposure. `BL2` should use a preregistered equivalence test rather than the old attenuation heuristic.

Use case-cluster bootstrap resampling with `n_boot = 2000` to estimate the post-cutoff effect interval on a standardized effect scale. Standardization should use the pre-cutoff pilot standard deviation of the corresponding estimand score so the post-cutoff and pre-cutoff magnitudes live on the same scale.

Freeze the equivalence rule as:

- SESOI (Smallest Effect Size Of Interest) `= 0.15` standardized effect units
- `BL2` passes only if the 95% post-cutoff bootstrap confidence interval lies fully inside `[-0.15, +0.15]`
- failure to establish equivalence blocks automatic Phase 8 GO and requires explicit design review

### 8.6A Same-cutoff early-warning ratio

Compute an architecture-noise early-warning ratio on the `E_CMMD` separation scale:

```text
ratio = |effect(GLM-4-9B <-> GPT-4.1 same-cutoff pair)|
        / |effect(Qwen2.5-7B <-> Qwen3-8B temporal pair)|
```

If `ratio > 0.5`, Phase 8 does not automatically fail, but the Phase 8 go/no-go memo must strengthen the architecture/capability caveat and cite the same-cutoff warning explicitly. If the denominator is near zero or not estimable, treat the ratio as warning-triggered rather than silently dropping the check.

### 8.7 Model capability covariate (`B1`)

Create `data/reference/model_capability_scores.csv` with:

- `model_id`
- `benchmark_name`
- `benchmark_date`
- `score_raw`
- `score_normalized`
- `source_url_or_doc`
- `notes`

This covariate is only a partial adjustment. `docs/CAVEAT_model_capability.md` should state that benchmark scores do not identify architecture, training data, or multilingual finance specialization cleanly.

### 8.8 Power analysis for the 2,560-case main run (`M2`)

The exact main-run multiplicity procedure is Westfall-Young stepdown max-T, so pilot power should be simulated rather than approximated by a univariate closed form. Power planning must be **scenario-based** and must not use a single perturbation-rich pilot point estimate as the Phase 8 planning prior.

Freeze at least three prior scenarios:

| Scenario | Prior construction | Use |
|---|---|---|
| `unweighted_pilot` | raw pilot point estimates and variance components | empirical anchor |
| `reweighted_phase8` | reweight coefficients to the expected Phase 8 `category × cutoff window` composition | planning prior for population shift |
| `shrinkage_0.5` | shrink pilot coefficients toward `0` by factor `0.5` | conservative stress test |

For each scenario, and for each legal family state (`S20`, `S16a`, `S16b`, `S12`):

1. Estimate the pilot coefficient vector `hat(beta)` and residual covariance `hat(Sigma)` for the retained confirmatory estimands.
2. Simulate `B = 2000` main-run datasets at `N_case = 2560`, `N_model = 9`, preserving:
   - case random-intercept variance where applicable;
   - model random-intercept variance where applicable;
   - observed missingness and eligibility masks by estimand;
   - cross-estimand covariance from the pilot;
   - the scenario-specific prior effect vector.
3. Refit the planned estimand-specific models on each synthetic dataset.
4. Apply Westfall-Young stepdown max-T across the confirmatory family in each replicate.
5. Estimate detection power for each primary coefficient as:

```text
power_j = (1 / B) * sum_{b=1}^B I[p_j^(WY, b) < alpha]
```

where `alpha = 0.05` family-wise.

For every reported power value, also report:

- Monte Carlo standard error `SE(power_j) = sqrt(power_j * (1 - power_j) / B)`
- a 95% Monte Carlo interval
- realized missingness under the scenario and family state

The planning output should therefore be a **range** over scenarios and legal family states, not a single optimistic number.

## 9. Human Audit Protocol for `C_FO` and `C_NoOp`

### 9.1 Review roles

The four domain agents should map to audit roles as follows:

> NOTE (OPEN 4 pending): default staffing assumes 2 reviewers + 1 adjudicator + 1 stats merge (roles may be held by the same person with time separation). If only a single reviewer is available, fall back to intra-rater test-retest, with a second pass at least 7 days after the first, and explicitly report this as a pilot staffing constraint in the Phase 8 paper methods.

| Role | Responsibility |
|---|---|
| Quant reviewer | economic consistency and target-local edit |
| NLP reviewer | natural CLS style and unintended cue detection |
| Editor reviewer | adjudicates style and target-local disagreements |
| Stats reviewer | adjudicates gate-boundary disputes and computes IAA/pass-rate summaries |

The ML Engineer agent is not an auditor. That role checks that the audit app, export format, and label merge logic are operational before the review starts.

### 9.2 Audit UI

Implement a lightweight local UI in `scripts/audit_app.py` using Streamlit. The UI should show:

- original text and perturbed text side by side;
- token/span diff highlights;
- case metadata (`case_id`, event type, date window, target);
- four rubric dimensions as `pass/fail/uncertain`;
- overall pass/fail toggle;
- short free-text comment box;
- reviewer ID and timestamp.

The UI should write JSONL records directly to `data/pilot/audit/raw/`.

### 9.3 Rubric

Every `C_FO` and `C_NoOp` item is judged on four frozen dimensions:

1. natural CLS style;
2. target-local edit;
3. economic consistency outside the edited slot;
4. no unintended cues.

Overall pass means all four dimensions pass. “Uncertain” is allowed during first-pass labeling but must be resolved during adjudication.

For `C_FO`, reviewers must verify that the stored `verified_outcome`, `fo_slotable`, `fo_slot_topology`, and `slot_span` metadata match the actual edit. For `C_NoOp`, reviewers must verify that the stored `host_category` and clause-bank choice match the article register.

Dimension 4, “no unintended cues,” should be expanded into the following six-class cue-fail checklist:

1. temporal cue (date or time-period hints accidentally introduced)
2. numeric-density mismatch (number density no longer matches the source article)
3. diction-register shift (lexical level or newsroom register changes abruptly)
4. entity-salience leak (another entity is added or made newly salient)
5. discourse-marker shift (connectors such as “此外” or “另外” are unnaturally abrupt)
6. style-boilerplate drift (the variant no longer reads like CLS-style copy)

### 9.4 Review flow

1. Quant and NLP reviewers independently review every generated perturbation.
2. Items with full agreement are accepted directly.
3. Any disagreement or uncertainty goes to Editor adjudication.
4. Stats reviewer runs the merge script, computes kappa or test-retest agreement as applicable, overall pass rates, per-dimension pass rates, cue-fail counts by class, and per-perturbation × event-type pass rates.
5. The adjudicated table is frozen before `P_predict` perturbation scoring.

### 9.5 IAA targets

IAA targets are:

- overall pass/fail Cohen’s kappa `>= 0.70` for each perturbation;
- dimension-level kappa `>= 0.60`;
- if either threshold is missed, revise rubric examples and rerun the affected batch before using the gate result.

These are pilot-grade reliability targets: high enough to make the gate credible without pretending the task is perfectly objective.

If the OPEN 4 fallback path is used and only one reviewer is available, replace inter-rater kappa with intra-rater test-retest agreement on the same thresholds after a second pass at least 7 days later.

### 9.6 Required audit outputs

The merge step must publish overall pass rate by perturbation, pass rate by perturbation × event type (`BL4`), per-dimension pass rate, disagreement counts, kappa or test-retest table, cue-fail counts by the six classes in Section 9.3, and adjudication notes for failed event types.

The final audit export JSONL should also preserve the gate-relevant artifact metadata used by later analysis and hashing: `verified_outcome`, `fo_slotable`, `fo_slot_topology`, `slot_span`, `host_category`, `noop_bank_id`, `noop_eligibility_rule_id`, and `ineligible_reason`.

## 10. Infrastructure and Reproducibility

### 10.1 Version pinning (`F4`)

`config/fleet/r5a_fleet.yaml` is the single source of truth for version pinning, operator-specific thinking controls, route locks, and fallback policy. The run manifest should record the resolved values from that file rather than a prose reconstruction.

White-box runs must pin:

- HF model repo and commit SHA;
- tokenizer repo and commit SHA;
- vLLM Docker image tag and digest;
- GPU dtype/quantization setting;
- launch command and environment variables.

Black-box runs must pin:

- provider name;
- model string exactly as called;
- provider route lock if OpenRouter or a similar gateway is used;
- runtime request parameters;
- response fingerprint fields returned by the provider.

### 10.2 Runtime policy

Required runtime defaults:

- DeepSeek concurrency `= 20`
- local vLLM concurrency `= 16`
- explicit `NO_PROXY` and `no_proxy` configuration for local vLLM and DeepSeek access paths
- `proxy=None`
- `trust_env=False`
- exponential backoff with checkpointed resume

Seed policy should be recorded as a triplet rather than a single field:

| Field | Meaning |
|---|---|
| `seed_requested` | the literal seed value sent in the request, if any |
| `seed_supported` | whether the provider claims deterministic or best-effort seed support |
| `seed_effective` | whether two identical `(model, prompt, seed_requested)` calls produced the same content hash |

The default provider interpretation should be:

| Provider path | `seed_supported` value |
|---|---|
| DeepSeek | `no` |
| OpenAI | `best-effort` |
| Anthropic | `no` |
| local vLLM / offline HF | `yes` |

### 10.3 Cache and fingerprint policy (`B4`)

The local cache should be enabled but never silent. Every cached record must store:

- full request hash inputs;
- raw response payload;
- parsed payload;
- provider fingerprint;
- creation timestamp;
- cache-hit flag.

Cache keys must include model ID, route ID, prompt version, seed, variant ID, and text hash. Duplicate-diagnostic reruns must set `bypass_local_cache=true`.

The normalized fingerprint schema should be:

```text
provider / model_id / system_fingerprint / response_id / route_hint / ts
```

Provider-specific handling rules:

- OpenRouter: populate `route_hint` from the `upstream_provider` field.
- DeepSeek: `system_fingerprint` may be empty; record `null` rather than throwing an error.
- local vLLM: encode the local git hash plus launch-arguments hash into the stored fingerprint fields.

Duplicate reruns must cover both baseline stability and perturbation-delta stability. That means rerunning both the baseline request and a matched perturbation request so that the delta itself can be checked for drift, rather than auditing only baseline duplicates.

### 10.4 Run manifest

Each pilot run should emit `data/pilot/manifests/run_{timestamp}.json` containing:

- git commit SHA;
- config hashes;
- prompt versions;
- model fingerprints;
- white-box checkpoint SHAs;
- runtime caps;
- seed policy;
- request-lineage database path and hash;
- article manifest hash;
- perturbation manifest hash;
- audit manifest hash.

### 10.5 Recommended repository additions

Phase 7 should add `data/pilot/` as the authoritative artifact root, `data/reference/` for external metadata, the new config subdirectories, `data/pilot/runstate.db` for request-level lineage, and a short runbook.

## 11. Compute and Time Budget

### 11.1 Engineering and review effort

| Workstream | Estimated elapsed time |
|---|---|
| WS0 | 1-2 working days |
| WS0.5 | scope TBD; not estimated until the follow-up Thales-alignment session closes (see `PENDING.md`) |
| WS1 | 2-3 working days |
| WS2 | 2-3 working days |
| WS3 | 3-4 working days including audit |
| WS4 | 1-2 working days |
| WS5 | 2-3 working days |

### 11.2 Expected wall-clock runtime

| Component | Approximate runtime | Notes |
|---|---|---|
| `P_logprob` smoke (30 cases x 5 models) | 30-90 minutes | depends on 14B throughput and batch size |
| `P_logprob` full pilot (100 cases x 5 models) | 2-4 hours | trace saving and per-model queuing included |
| `P_predict` smoke (20 cases x 9 models) | 30-90 minutes | includes repair/retry overhead |
| `P_predict` full pilot baseline + perturbations | 4-8 hours | depends on provider latency and retry rate |
| duplicate reruns | 30-60 minutes | 5% diagnostic subset |
| full human audit | 6-10 reviewer-hours | feasible within one day across four reviewers |
| pilot analysis + power simulation | 2-6 hours compute | mostly CPU, simulation scales with `B` |

### 11.3 API and token budget

For planning purposes, Phase 7 should budget roughly:

- baseline `P_predict`: `100 cases x 9 models = 900` calls;
- `C_FO`: approximately `60 eligible cases x 9 models = 540` calls;
- `C_NoOp`: approximately `90-100 eligible cases x 9 models = 810-900` calls;
- exploratory `C_NoOp_placebo`: approximately `100 eligible cases x 9 models = 900` calls;
- duplicate reruns: roughly `5%` overhead.

That implies roughly `3.2k-3.4k` model calls before retries. The exact USD cost is provider-price dependent and should be converted from token logs on run day rather than hard-coded in this plan. Because `C_NoOp_placebo` is exploratory-only, it should be the first branch dropped if token accounting threatens the confirmatory path. A practical planning rule is:

- set a hard pilot spend cap of `USD 300`;
- emit live token accounting during the run;
- stop and review if 80% of the cap is consumed before all confirmatory paths are complete.

This keeps the pilot bounded without pretending that current provider prices are stable.

## 12. Risk Register

| ID | Risk | Trigger | Response |
|---|---|---|---|
| R1 | both `C_FO` and `C_NoOp` fail quality gates | overall pass `<85%` or an event type `<75%` | demote both to exploratory, shrink confirmatory family, update Stage 2 prereg accordingly |
| R2 | `P_logprob` unavailable on one or more white-box models | prompt-logprob extraction fails smoke test | switch affected model to offline HF scorer with same checkpoint SHA |
| R3 | hidden provider caching compresses deltas | duplicate reruns are suspiciously identical or response IDs repeat in an implausible pattern | document provider behavior, widen rerun subset, downgrade provider-specific claims if needed |
| R4 | same-cutoff falsification pair shows large signal | Section 8.6A early-warning ratio `> 0.5` | flag architecture/capability confounding, strengthen caveat text, consider narrowing main-text claims |
| R5 | post-cutoff negative control does not establish equivalence | Section 8.6 post-cutoff CI is not fully inside `[-0.15, +0.15]` | block automatic Phase 8 GO until sampling, scoring, or cutoff coding is reviewed |
| R6 | confirmatory estimands are redundant | pilot correlation `r > 0.8` | apply the automatic Section 8.4 tie-break where pre-registered; require a memo only for non-default regrouping |
| R7 | model-capability covariate unavailable or too noisy | benchmark sources missing for some models | use a transparent fallback source, mark caveat, avoid overinterpreting adjusted coefficients |
| R8 | pilot power implies underpowered main run | simulated Phase 8 power too low at `N=2560` | pause Phase 8 and revisit sample size or confirmatory family under frozen rules |
| R9 | `BL2` equivalence pass is over-read as proof of zero effect | readers treat TOST passage as “no signal exists” rather than “signal is within SESOI” | write explicit equivalence-language caveat in the Phase 8 memo and paper methods |
| R10 | zero-shot parse failures exceed 5% on one or more models | 20-case smoke shows strict-JSON success `<95%` | delay Phase 7 launch, apply adapter hardening only, and do not change prompt semantics or add few-shot examples |
| R11 | WS0.5 factor pipeline not ready in time for pilot manifest freeze | Thales-alignment session does not close before WS4 prep | pause WS4 until the factor schema is deterministic; do not substitute ad-hoc factor labels |
| R12 | WS0.5 follow-up session reveals factor operationalization options the R5A frozen scope did not anticipate | Thales-alignment memo surfaces factor definitions that require scope-level adjustment | route changes through a new `DECISION_*` memo before pilot manifest freeze rather than absorbing them silently into this plan |

## 13. Exit Gate to Phase 8 (Main Run)

Phase 8 may start only if all of the following hold:

1. `src/r5a/` operator and perturbation pipelines run end-to-end on the frozen pilot manifest.
2. A signed Stage 1 preregistration exists and the Stage 2 skeleton is populated from pilot outputs only.
3. `P_logprob` succeeds on all 5 white-box models with pinned tokenizer/checkpoint provenance.
4. `P_predict` succeeds on all 9 models with fingerprint logging and acceptable parse rates.
5. The effective sample-size matrix passes `min cell >= 15`.
6. Quality-gate adjudication for `C_FO` and `C_NoOp` is complete and any demotions are explicitly carried into Stage 2, using the frozen three-condition thresholds: audit pass rate `>=85%` overall with no event type `<75%`, eligible case coverage `>=60%` of pre-cutoff cases, and baseline delta non-degeneracy `mean |delta| > 0` on `>=5/9` models.
7. `BL2` passes the Section 8.6 TOST equivalence rule and the Section 8.6A same-cutoff early-warning ratio is documented; if the ratio exceeds `0.5`, the go/no-go memo must adopt strengthened caveat language rather than ignoring the warning.
8. Correlation/regrouping trigger has been evaluated and documented.
9. Main-run power at `N=2560` is acceptable for the retained confirmatory family under the Section 8.8 scenario range. Automatic GO requires at least one temporal-route estimand (`E_CMMD` or `E_PCSG`) **and** one perturbation-route estimand (`E_FO` or `E_NoOp`) to simultaneously reach Westfall-Young-adjusted `80%` power for the primary cutoff-exposure coefficient; a single-channel success is insufficient.
10. `docs/DECISION_20260417_phase8_go_no_go.md` records the retained family, risks, and run-day operational caps.

The Phase 8 gate is about measurement readiness, not about obtaining a “positive” pilot. Null pilot findings are allowed; unidentified or unstable pilot findings are not.

## 14. Appendix

### 14.1 Key file paths

```text
config/fleet/r5a_fleet.yaml
config/runtime/r5a_runtime.yaml
config/perturbations/c_fo_rules.yaml
config/perturbations/c_noop_clause_bank.yaml
config/pilot_sampling.yaml
src/r5a/contracts.py
src/r5a/operators/p_predict.py
src/r5a/operators/p_logprob.py
src/r5a/perturbations/c_fo.py
src/r5a/perturbations/c_noop.py
src/r5a/analysis/power.py
scripts/sample_phase7_pilot.py
scripts/check_pilot_cells.py
scripts/init_runstate_db.py
scripts/build_perturbation_audit_batch.py
scripts/generate_noop_placebo.py
scripts/audit_app.py
scripts/run_phase7_pilot.py
scripts/simulate_phase8_power.py
data/pilot/
data/pilot/runstate.db
data/pilot/perturbations/c_noop_placebo.jsonl
data/reference/model_capability_scores.csv
```

### 14.2 Config keys that should exist

`config/fleet/r5a_fleet.yaml` should minimally define a per-model × per-operator matrix:

```yaml
models:
  qwen2.5-7b:
    family: qwen
    access: white_box
    provider: vllm
    cutoff_date: 2023-10-31
    tokenizer_family: qwen
    tokenizer_sha: <tokenizer-sha>
    hf_commit_sha: <model-sha>
    p_logprob:
      thinking_control: default_off
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: true
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
  qwen2.5-14b:
    family: qwen
    access: white_box
    provider: vllm
    cutoff_date: 2023-10-31
    tokenizer_family: qwen
    tokenizer_sha: <tokenizer-sha>
    hf_commit_sha: <model-sha>
    p_logprob:
      thinking_control: default_off
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: true
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
  glm-4-9b:
    family: glm
    access: white_box
    provider: vllm
    cutoff_date: 2024-06-30
    tokenizer_family: glm4
    tokenizer_sha: <tokenizer-sha>
    hf_commit_sha: <model-sha>
    p_logprob:
      thinking_control: system_message_toggle
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: false
      fallback: offline_hf_scorer
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
  qwen3-8b:
    family: qwen
    access: white_box
    provider: vllm
    cutoff_date: 2025-01-31
    tokenizer_family: qwen
    tokenizer_sha: <tokenizer-sha>
    hf_commit_sha: <model-sha>
    p_logprob:
      thinking_control: append_no_think_sentinel
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: true
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
  qwen3-14b:
    family: qwen
    access: white_box
    provider: vllm
    cutoff_date: 2025-01-31
    tokenizer_family: qwen
    tokenizer_sha: <tokenizer-sha>
    hf_commit_sha: <model-sha>
    p_logprob:
      thinking_control: append_no_think_sentinel
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: true
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
  deepseek-v3-0324:
    family: deepseek
    access: black_box
    provider: deepseek
    cutoff_date: 2024-07-31
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
      route_lock_required: provider_model_id
  gpt-4.1:
    family: openai
    access: black_box
    provider: openai
    cutoff_date: 2024-06-30
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
      route_lock_required: provider_model_id
  gpt-5.1:
    family: openai
    access: black_box
    provider: openai
    cutoff_date: 2024-09-30
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
      route_lock_required: provider_model_id
  claude-sonnet-4.6:
    family: anthropic
    access: black_box
    provider: anthropic
    cutoff_date: 2025-08-31
    p_predict:
      thinking_control: default_deployed
      prompt_overlay_policy: baseline_only
      route_lock_required: provider_model_id
```

`config/runtime/r5a_runtime.yaml` should minimally define:

```yaml
runtime:
  seed: 20260417
  retry_max: 5
  timeout_seconds: 120
  cache_enabled: true
  runstate_db: data/pilot/runstate.db
providers:
  deepseek:
    max_concurrency: 20
    trust_env: false
    proxy: none
  vllm:
    max_concurrency: 16
    trust_env: false
    proxy: none
  openai:
    max_concurrency: 8
  anthropic:
    max_concurrency: 8
```

### 14.3 Command snippets

```powershell
$env:NO_PROXY = "localhost,127.0.0.1,host.docker.internal"
$env:no_proxy = $env:NO_PROXY

conda run -n rag_finance python scripts/smoke_phase7.py `
  --fleet config/fleet/r5a_fleet.yaml `
  --runtime config/runtime/r5a_runtime.yaml `
  --operator p_predict `
  --variant baseline `
  --smoke-cases 20

conda run -n rag_finance python scripts/init_runstate_db.py `
  --db data/pilot/runstate.db

conda run -n rag_finance python scripts/sample_phase7_pilot.py `
  --config config/pilot_sampling.yaml `
  --output data/pilot/manifests/pilot_100_cases.json

conda run -n rag_finance python scripts/check_pilot_cells.py `
  --manifest data/pilot/manifests/pilot_100_cases.json `
  --fleet config/fleet/r5a_fleet.yaml

conda run -n rag_finance python scripts/build_perturbation_audit_batch.py `
  --manifest data/pilot/manifests/pilot_100_cases.json `
  --output-dir data/pilot/audit/batches

conda run -n rag_finance streamlit run scripts/audit_app.py -- `
  --batch-dir data/pilot/audit/batches

conda run -n rag_finance python scripts/generate_noop_placebo.py `
  --manifest data/pilot/manifests/pilot_100_cases.json `
  --audit-jsonl data/pilot/audit/exports/audit_manifest.jsonl `
  --output data/pilot/perturbations/c_noop_placebo.jsonl

conda run -n rag_finance python scripts/run_phase7_pilot.py `
  --manifest data/pilot/manifests/pilot_100_cases.json `
  --fleet config/fleet/r5a_fleet.yaml `
  --runtime config/runtime/r5a_runtime.yaml `
  --runstate-db data/pilot/runstate.db `
  --out-dir data/pilot/results

conda run -n rag_finance python scripts/simulate_phase8_power.py `
  --pilot-results data/pilot/analysis/pilot_effects.parquet `
  --family-states S20,S16a,S16b,S12 `
  --scenario unweighted_pilot `
  --scenario reweighted_phase8 `
  --scenario shrinkage_0.5 `
  --n-cases 2560 `
  --n-sims 2000

Get-FileHash data/pilot/manifests/pilot_100_cases.json -Algorithm SHA256
Get-FileHash data/pilot/audit/exports/audit_manifest.jsonl -Algorithm SHA256
git rev-parse HEAD
git tag -s prereg/phase7-stage1-v1.0 -m "Phase 7 Stage 1 prereg"
```

### 14.4 Minimal sign-off checklist

- interfaces signed
- WS0.5 Thales-alignment session closed, decision memo committed, factor schema frozen (exact file path set by that session)
- zero-shot 20-case smoke parse success `>=95%`
- `runstate.db` initialized and request lineage validated
- 100-case manifest signed
- pilot manifest hash recorded
- perturbation audit complete
- audit manifest hash recorded
- QC report complete
- Stage 1 prereg committed
- external anchor (signed tag or timestamp) created
- `BL2` equivalence test and same-cutoff warning ratio evaluated
- scenario-based power table written
- Phase 8 go/no-go memo written

## 15. Changelog

- `A01` froze the estimand contract by adding Section 8.1A, defining analysis units, scalar scores, and the `signed_score` mapping. Section 6.4 now computes `n_eff` on the estimand’s own analysis unit, and Section 8.2 now uses per-estimand parameterization rather than one shared `Y_ijm` form.
- `A02` replaced the old `BL2` attenuation heuristic with a preregistered TOST equivalence rule in Section 8.6 and moved the post-cutoff window in Section 6.2 to `>= 2026-02-01`. Section 8.6A now adds the same-cutoff early-warning ratio and Section 13 cites only these hard numerical checks.
- `A03` froze the legal Stage 2 family states in Section 7.1A and made the `E_CTS` / `E_PCSG` regrouping rule deterministic in Section 8.4. Section 7.2 now narrows allowed prompt edits to adapter hardening, and Section 13 item 9 now requires one temporal-route and one perturbation-route estimand to meet the automatic GO power target.
- `A04` hardened `C_FO` and `C_NoOp` admissibility by splitting `verified_outcome` from `fo_slotable`, adding slot-topology metadata, and converting `C_NoOp` to a host-aware clause-bank design. The plan also adds `C_NoOp_placebo` as exploratory-only and consistently narrows `E_NoOp` language to robustness / template-brittleness rather than direct memorization evidence.
- `A05` made `config/fleet/r5a_fleet.yaml` the operator/runtime source of truth across WS0, `P_logprob`, `P_predict`, and the reproducibility section. Appendix 14.2 now includes an explicit per-model × per-operator YAML example covering the full frozen 9-model fleet.
- `A06` replaced coarse resume semantics with request-item lineage via `data/pilot/runstate.db`, frozen request IDs, and status fields. Seed semantics and fingerprint logging are now normalized in Sections 10.2-10.4, and duplicate reruns now cover both baseline outputs and perturbation deltas.
- `A07` added the Stage 1 evidence package in Section 7.1B and a non-critical-path Phase 7b reserve-promotion contingency in Section 7.2A. The audit staffing table remains intact, but Section 9.1 now carries the OPEN 4 note and fallback path.
- `A08` hardened `BL1` and power planning by adding a text-light challenger, grouped-CV-by-case, and scenario-based power priors with Monte Carlo error reporting. Section 13 now explicitly forbids treating a single perturbation-rich pilot point estimate as the Phase 8 planning prior.
- `A09` reserved `WS0.5: Thales alignment prerequisites` as a named but intentionally-unspecified workstream in Section 5.1A. Scope, deliverables, file paths, and effort are all deferred to a separate follow-up session and tracked in root-level `PENDING.md`. Section 4 workstream map, Section 6.3 factor-quota note, Section 11.1 time budget, Section 12 risks `R11`/`R12`, and Section 14.4 sign-off checklist now point at the WS0.5 gate without prescribing its implementation. The T1/T2/T3 verification questions are preserved as a briefing note, not as a commitment to any specific resolution path.
