---
title: Phase 7 WS0 Interface Sign-off
date: 2026-04-26
phase: Phase 7 — Pilot
workstream: WS0
status: SIGNED — interfaces frozen for WS1/WS2/WS3 implementation; partly superseded by 0427 + 0429 (see banner below)
authority: plans/phase7-pilot-implementation.md §5.1
supersedes: none
superseded_in_part_by:
  - docs/DECISION_20260427_pcsg_redefinition.md (fleet roster: 5 white-box → 10 white-box; PCSG pair definition: same-tokenizer same-cutoff pairs → cross-version Qwen pair on common-vocab subset; RunManifest additions: cutoff_observed, quant_scheme, pcsg_pair_registry_hash)
  - docs/DECISION_20260429_gate_removal.md (E_FO/E_NoOp gate removal; Stage 2 family states collapsed to S20; WS6 unconditional; BL2 n_post 20→350; RunManifest additions: hidden_state_subset_hash, quality_gate_thresholds)
---

> **Supersession banner (added 2026-04-29).** This memo is preserved for
> historical record and for the parts that remain in force (R5A namespace
> layout, runtime schema, Pydantic contract names, smoke harness wiring).
> The fleet roster table in §2.1, the PCSG temporal-pair definition, and
> the RunManifest field set listed in §3 are **partly superseded** by the
> two memos linked above. For the current authoritative state consult:
> - **Fleet roster + PCSG pairs**: `config/fleet/r5a_fleet.yaml`
> - **RunManifest field set**: `plans/phase7-pilot-implementation.md` §10.4
>   (full enumerated list, including 2026-04-27 + 2026-04-29 additions)
> - **E_FO / E_NoOp gate status**: removed; see DECISION_20260429
> - **WS6 trigger**: unconditional; see DECISION_20260429 §2.4
>
> Do not rewrite the historical content below. New facts go in the two
> superseding memos.


# Phase 7 WS0 — Interface Sign-off

## Purpose

Per plan §5.1 exit criteria, this memo signs off the contract names,
config schemas, and manifest fields that downstream workstreams
(WS1 P_logprob, WS2 P_predict, WS3 perturbations + audit, WS4 pilot
execution, WS5 statistics) commit to. After this date, changes to
these surfaces require either a new decision memo or rework that
documents why the WS0 freeze did not hold.

This is **interface freeze**, not implementation freeze. Backend
adapters, operator bodies, perturbation generators, audit UI, and
analysis modules are still empty; WS1/WS2/WS3 fill them.

## What is signed

### 1. R5A namespace and module layout

```
src/r5a/
  __init__.py          version banner
  contracts.py         typed Pydantic records (this memo §3)
  fleet.py             FleetConfig + ModelConfig loader
  runtime.py           RuntimeConfig + ProviderRuntime loader
  backends/            stub — WS1 adds vllm_completion + offline_hf;
                              WS2 adds openai_compatible / openai_native /
                              anthropic_native
  operators/           stub — WS1/WS2 add p_logprob.py, p_predict.py
  perturbations/       stub — WS3 adds c_fo.py, c_noop.py, shared.py
  estimands/           stub — WS5 adds confirmatory.py
  audit/               stub — WS3 adds audit app + merge logic
  analysis/            stub — WS5 adds pilot_effects, correlation,
                              baselines, power
```

The legacy single-model code (`src/news_loader.py`, `src/llm_client.py`,
`src/pilot.py`, `src/metrics.py`, `src/masking.py`, `src/prompts.py`,
`src/prompt_loader.py`, `src/models.py`, `src/experiment.py`,
`src/display_utils.py`) was archived to `archive/pre_r5a_src/src/` on
this date. The legacy `tests/smoke_test_prompts.py`,
`tests/test_failure_isolation.py`, and the three `scripts/run_diagnostic_*`
/ `scripts/rescore_fo_flip.py` files that imported from old `src.*` were
moved to the same archive. New R5A code must not import from
`archive.pre_r5a_src.*`.

### 2. Config files

```
config/fleet/r5a_fleet.yaml
config/runtime/r5a_runtime.yaml
config/pilot_sampling.yaml
```

`config/perturbations/c_fo_rules.yaml` and
`config/perturbations/c_noop_clause_bank.yaml` are **not** part of the
WS0 freeze; they belong to WS3.

#### 2.1 Fleet schema (frozen)

`config/fleet/r5a_fleet.yaml` is the single source of truth for
per-model and per-operator behavior, per plan §10.1 / §14.2 (`A05`).
Adapters must read these fields rather than re-deriving them in code.
Frozen surface:

```yaml
fleet_version: <string>
models:
  <model_id>:
    family: <string>
    access: white_box | black_box
    provider: vllm | deepseek | openai | anthropic
    cutoff_date: <iso date>
    api_model_name: <string>            # black-box only; pinned at run time
    tokenizer_family: <string>          # white-box only
    tokenizer_sha: <string>             # white-box only; <TBD> until pinned
    hf_commit_sha: <string>             # white-box only; <TBD> until pinned
    p_logprob:                          # white-box only
      thinking_control: default_off | system_message_toggle |
                        append_no_think_sentinel
      prompt_overlay_policy: none
      route_lock_required: hf_commit_sha
      echo_supported: bool
      fallback: offline_hf_scorer | null
    p_predict:                          # all models
      thinking_control: default_deployed | extended_thinking_off
      prompt_overlay_policy: baseline_only
      route_lock_required: hf_commit_sha | provider_model_id | null
```

Frozen fleet members (5 white-box + 4 black-box = 9):

| model_id            | provider  | cutoff_date | tokenizer_family |
|---------------------|-----------|-------------|------------------|
| qwen2.5-7b          | vllm      | 2023-10-31  | qwen             |
| qwen2.5-14b         | vllm      | 2023-10-31  | qwen             |
| qwen3-8b            | vllm      | 2025-01-31  | qwen3            |
| qwen3-14b           | vllm      | 2025-01-31  | qwen3            |
| glm-4-9b            | vllm      | 2024-06-30  | glm4             |
| deepseek-v3-0324    | deepseek  | 2024-07-31  | —                |
| gpt-4.1             | openai    | 2024-06-30  | —                |
| gpt-5.1             | openai    | 2024-09-30  | —                |
| claude-sonnet-4.6   | anthropic | 2025-08-31  | —                |

Tokenizer-matched temporal pairs for E_PCSG: `(qwen2.5-7b, qwen2.5-14b)`
on the qwen tokenizer; `(qwen3-8b, qwen3-14b)` on the qwen3 tokenizer
(R5A_FROZEN_SHORTLIST.md §1, operator schema §4.5). `glm-4-9b` is
white-box but standalone for paired contrasts.

#### 2.2 Runtime schema (frozen)

```yaml
runtime:
  seed: <int>                # 20260417
  retry_max: <int>
  timeout_seconds: <int>
  cache_enabled: <bool>
  runstate_db: data/pilot/runstate.db
providers:
  deepseek:  { max_concurrency: 20, trust_env: false, proxy: none }
  vllm:      { max_concurrency: 16, trust_env: false, proxy: none }
  openai:    { max_concurrency: 8 }
  anthropic: { max_concurrency: 8 }
```

The `trust_env=false` / `proxy=none` defaults for DeepSeek and vLLM
are load-bearing per CLAUDE.md and project memory `feedback_concurrency.md`
(local proxy interferes with both, default 50 overruns capacity).

#### 2.3 Pilot sampling schema (frozen surface, values pilot-iterable)

The bucket counts (60/20/20), date-window targets, category quotas,
and `n_eff` thresholds (target 20 / minimum 15) match plan §6 verbatim.
The `factor_schema_path` is intentionally `<TBD-WS0.5>` — the WS0.5
follow-up session sets the schema location and content. WS4 must not
build the manifest until that path is non-TBD.

### 3. Pydantic contracts (frozen)

Defined in `src/r5a/contracts.py`. Downstream code imports from there;
no parallel record definitions are allowed.

| Contract              | Origin in plan / schema                   |
|-----------------------|-------------------------------------------|
| `ArticleRecord`       | plan §5.2/5.3 input, schema §3.2/§4.2     |
| `PilotCase`           | plan §6 sampling output                   |
| `PilotManifest`       | plan §10.4 article manifest               |
| `PerturbationArtifact`| plan §5.4 + §5.4A reserved metadata keys  |
| `SpanEdit`            | plan §5.4 edit metadata                   |
| `PredictRecord`       | plan §5.3 + schema §3.4                   |
| `LogProbTrace`        | plan §5.2 + schema §4.4                   |
| `EvidenceQuote`       | schema §3.4                               |
| `RequestFingerprint`  | plan §10.3 normalized schema              |
| `AuditRecord`         | plan §9.2 + §9.3 cue-fail expansion       |
| `CueFailFlags`        | plan §9.3 six classes                     |
| `RunStateRow`         | plan §5.5A request-item lineage           |
| `RunManifest`         | plan §10.4                                |

Enums: `AccessTier`, `OperatorId`, `PerturbationVariant`,
`RequestStatus`, `HostCategory`, `FOSlotTopology`, `SeedSupport`,
`Direction`.

### 4. Smoke harness

`scripts/smoke_phase7.py` validates fleet and runtime YAMLs in
`--check-config` mode. The `--operator p_predict` 9-model 20-case
feasibility gate (plan §5.1 step 7) is wired to its CLI surface but
returns a stub exit code until WS2 lands the adapters; WS2 is the
first workstream allowed to flip that gate to a real check.

## What is NOT signed

- backend adapter implementations (WS1, WS2);
- operator bodies (WS1, WS2);
- perturbation generators or rule files (WS3);
- audit Streamlit app and merge logic (WS3);
- pilot orchestration scripts (WS4);
- estimand / power / pre-registration tooling (WS5);
- WS0.5 Thales-alignment scope (deferred per `PENDING.md`).

## Open items remaining

| Tracker        | Item                                  | Blocks       |
|----------------|---------------------------------------|--------------|
| `PENDING.md`   | OPEN 4 audit staffing                 | WS4 launch   |
| `PENDING.md`   | WS0.5 Thales-alignment scope          | Manifest freeze + sign-off §14.4 |

## Verification done before signing

```text
$ conda run -n rag_finance python scripts/smoke_phase7.py --check-config
== fleet ==
fleet_version: r5a-v1.0-2026-04-26
white_box (5): qwen2.5-7b, qwen2.5-14b, qwen3-8b, qwen3-14b, glm-4-9b
black_box (4): deepseek-v3-0324, gpt-4.1, gpt-5.1, claude-sonnet-4.6
== runtime ==
providers.deepseek: max_concurrency=20 trust_env=False proxy=none
providers.vllm:     max_concurrency=16 trust_env=False proxy=none
providers.openai:   max_concurrency=8
providers.anthropic:max_concurrency=8
```

Fleet 5+4 split matches the frozen shortlist; concurrency caps match
plan §10.2; pydantic `extra="forbid"` rejects unknown fields on every
contract.
