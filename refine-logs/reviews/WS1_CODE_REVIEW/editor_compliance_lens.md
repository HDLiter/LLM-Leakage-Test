# Editor / Plan Compliance Lens Review

## 1. Verdict

**fix-then-ship**. The WS0/WS1 stage-0 implementation is broadly in scope and local checks pass, but several freeze-level contract/doc hygiene issues need correction before treating this as preregistration-stable:

- `LogProbTrace` omits `token` / `top_logprobs` despite plan §5.2 requiring them (`plans/phase7-pilot-implementation.md:235-236`, `src/r5a/contracts.py:231-241`).
- `RunManifest` lacks Docker/vLLM image digest fields required by WS0 step 5 / §10.1 (`plans/phase7-pilot-implementation.md:149`, `:963`; `src/r5a/contracts.py:307-322`).
- `RunStateRow` does not expose the seed triplet as required schema fields (`plans/phase7-pilot-implementation.md:441-443`; `src/r5a/contracts.py:286-296`).
- Plan/memo path drift: master plan expects `docs/DECISION_20260417_phase7_interfaces.md`; delivered file is `docs/DECISION_20260426_phase7_interfaces.md`.

Local verification run:
- `python scripts/smoke_phase7.py --check-config` passed.
- `python -m pytest tests/r5a/test_logprob_metrics.py tests/r5a/test_p_logprob_serialization.py` passed: 22 tests.
- `--operator p_predict --variant baseline --smoke-cases 20` exits `2` as an intentional WS0/WS2 stub.

## 2. Plan §5.1 WS0 Row-By-Row Checklist

| Deliverable | Status | File or stub | Notes |
|---|---:|---|---|
| `src/r5a/contracts.py`, `fleet.py`, `runtime.py` | partial | `src/r5a/contracts.py:87`, `src/r5a/fleet.py:24`, `src/r5a/runtime.py:17` | Imports/config validation work. Contract gaps remain for runstate seed fields, Docker digests, and typed perturbation metadata. |
| `config/fleet/r5a_fleet.yaml`, `runtime`, `pilot_sampling` | partial | `config/fleet/r5a_fleet.yaml:18`, `config/runtime/r5a_runtime.yaml:9`, `config/pilot_sampling.yaml:10` | 9 fleet entries present. `<TBD>` placeholders acceptable pre-run but need PENDING tracking. Fleet follows §14.2 shape more than §5.1 step-2 field list. |
| decision memo | partial | `docs/DECISION_20260426_phase7_interfaces.md:11` | Naming-compliant, signed, but plan cites `20260417` at `plans/phase7-pilot-implementation.md:135` and `:161`. Memo does not freeze manifest fields field-by-field. |
| smoke harness | partial | `scripts/smoke_phase7.py:31-123` | `--check-config` works. Provider handshakes and 20-case `P_predict` parse gate are stubbed (`scripts/smoke_phase7.py:114-123`). |

WS0 steps / exit:
- Steps 1-4: mostly done; runtime/fleet validate.
- Step 5: **gap**. Manifest schema is named, not fully frozen; missing Docker digest.
- Step 6: config validation done; provider handshake not done.
- Step 7: CLI stub only; no `>=95%` parse result yet.
- Exit criteria at `plans/phase7-pilot-implementation.md:157-161`: only first two are locally satisfied.

## 3. Plan §5.2 WS1 Row-By-Row Checklist

| Deliverable | Status | File or stub | Notes |
|---|---:|---|---|
| operator/backend/metrics code | partial | `src/r5a/operators/p_logprob.py:54`, `src/r5a/backends/vllm_logprob.py:45`, `src/r5a/analysis/logprob_metrics.py:123` | In scope, but `PLogprobOperator.compute` is async and lacks planned `model_id` / `batch_size` args (`plans/...:220-225`; `p_logprob.py:72-77`). |
| `config/models/*.yaml` | missing | none | Required by `plans/...:211`. Fleet has SHA placeholders instead (`config/fleet/r5a_fleet.yaml:24-25`). |
| `data/pilot/logprob_traces/*.parquet` | cloud-deferred | writer at `src/r5a/operators/p_logprob.py:212-236` | Path layout matches §5.2 / §14.1. No actual traces yet. |

WS1 steps:
| Step | Status | Anchor |
|---|---:|---|
| 1 completion endpoint, not chat | done | `src/r5a/backends/vllm_logprob.py:207-216` |
| 2 resolve behavior from fleet | partial | CLI reads fleet, but backend fallback is user-selected, not resolved from `p_logprob.echo_supported` (`scripts/ws1_run_logprob.py:155-190`). |
| 3 tokenizer/checkpoint pinning | partial/deferred | YAML fields exist but `<TBD>`; `config/models/*.yaml` absent. |
| 4 thinking-off backend enforcement | partial | traces force `thinking_mode="off"` (`vllm_logprob.py:192`), but Qwen3 explicit backend control is not implemented. |
| 5 Parquet traces | done locally | `p_logprob.py:126-149`, `:212-236` |
| 6 CTS/PCSG from saved traces | partial | `compute_pcsg` done; `compute_cts` requires later frequency table (`logprob_metrics.py:140-144`). No table CLI. |
| 7 30-case smoke | partial | fixture exists and validates as 30 records; cloud model execution pending. |

WS1 exit criteria:
- Cloud-only: all 5 models returning logprobs; `<1%` failure rate.
- Locally checkable and tested: Parquet roundtrip (`tests/r5a/test_p_logprob_serialization.py:49-86`), PCSG checks (`tests/r5a/test_logprob_metrics.py:142-171`), CTS function with supplied table (`:179-198`).
- Not yet tested locally: token-count tolerance against tokenizer, end-to-end E_CTS/E_PCSG table generation, real thinking-off trace audit.

## 4. Contract Field Audit

Perturbation metadata §5.4A:

| Plan field | `contracts.py` field | Match? |
|---|---|---:|
| `verified_outcome` | metadata comment only `:169-172` | partial |
| `fo_slotable` | metadata comment only | partial |
| `fo_slot_topology` | enum exists `:64-67`, metadata comment | partial |
| `slot_span` | metadata comment; no typed span object | partial |
| `ineligible_reason` | metadata comment only | partial |
| `host_category` | enum `:57-61`; metadata comment | partial |
| `noop_bank_id` | metadata comment only | partial |
| `noop_eligibility_rule_id` | metadata comment only | partial |
| `placebo_variant` | `PerturbationVariant` has `c_noop_placebo`; no metadata enum `none/c_noop/c_noop_placebo` | partial |

Runstate §5.5A:

| Plan field | `contracts.py` field | Match? |
|---|---|---:|
| `request_id`, `case_id`, `model_id`, `operator`, `perturbation_variant`, `status`, `retry_count` | `:286-292` | yes |
| `fingerprint` | `:293` | yes |
| `seed_requested`, `seed_supported`, `seed_effective` | only inside `RequestFingerprint` `:198-200` | **no** |
| `response_id`, `ts_start`, `ts_end` | `:294-296` | yes |

Fingerprint §10.3:

| Plan field | `contracts.py` field | Match? |
|---|---|---:|
| `provider`, `model_id`, `system_fingerprint`, `response_id`, `route_hint`, `ts` | `:192-197` | yes |
| seed triplet | extra in fingerprint `:198-200` | extra/misplaced |

Run manifest §10.4 plus WS0 step 5:

| Plan field | `contracts.py` field | Match? |
|---|---|---:|
| git commit SHA | `git_commit_sha` `:309` | yes |
| config hashes | split into `fleet/runtime/sampling_config_hash` `:310-312` | yes |
| prompt versions | `prompt_versions` `:313` | yes |
| model fingerprints | `model_fingerprints` `:314` | yes |
| white-box checkpoint SHAs | `white_box_checkpoint_shas` `:315` | yes |
| Docker/vLLM image digest | missing | **no** |
| runtime caps, seed policy | `:316-317` | yes |
| runstate path/hash | `:318-319` | yes |
| article/perturbation/audit hashes | `:320-322` | yes |

## 5. YAML Audit

| File | Status | Notes |
|---|---:|---|
| fleet | partial | All 9 entries present. Per-model nested operator fields are present. `qwen3-* tokenizer_family: qwen3` (`config/fleet/r5a_fleet.yaml:57`, `:74`) differs from master §14.2 example `qwen` (`plans/...:1218`, `:1234`); DECISION agrees with YAML (`docs/...:107-116`). |
| fleet placeholders | acceptable but track | `<TBD>` tokenizer/model SHAs for 5 white-box models and API names for `gpt-5.1` / `claude-sonnet-4.6` (`config/fleet/...:24-25`, `:132`, `:143`). Acceptable before confirmatory run per `config/fleet/...:8-10`, but not tracked in `PENDING.md`. |
| runtime | pass | Matches §14.2 and §10.2 caps: seed/retry/cache/runstate and provider caps (`config/runtime/r5a_runtime.yaml:9-32`). |
| pilot sampling | pass with deferred field | Numeric §6.2/§6.3/§6.4 values represented: 100, 60/20/20, 20/30/30/20 windows, 15/12/15/20/15 quotas, `n_eff` 20/15 (`config/pilot_sampling.yaml:10-44`). `factor_schema_path` defer is documented and matches `PENDING.md:23-34`. |

## 6. Citation Drift List

| Reference | Problem | Fix |
|---|---|---|
| `plans/phase7-pilot-implementation.md:135`, `:161` | Points to `docs/DECISION_20260417_phase7_interfaces.md`; actual signed memo is `20260426`. | Update plan path or create an explicit supersession note. |
| `src/r5a/backends/offline_hf.py:4` | "plan §5.2 R2 risk" does not resolve; §5.2 has an unlabeled risk table. | Cite `plans/phase7-pilot-implementation.md:251` or `:263-266`. |
| `scripts/ws1_run_logprob.py:14-15` | Cites §14.3 for CLI shape, but §14.3 does not document `ws1_run_logprob.py`. | Cite `plans/ws1-cloud-execution.md:108-129` or add WS1 CLI to §14.3. |
| `docs/DECISION_20260426_phase7_interfaces.md:161` | Claims `LogProbTrace` follows operator schema §4.4; current model omits schema score fields and plan-required `top_logprobs`. | Either revise the contract or narrow the memo claim. |
| `plans/ws1-cloud-execution.md:137` vs `:177` | Says E_CTS is calculable end-to-end on smoke, but frequency-table construction is deferred. | Change smoke gate to "Min-K%/PCSG local derivation; CTS after frequency table." |

Spot-checked valid refs include plan §5.1, §5.2, §5.4A, §5.5A, §6, §10.2, §10.3, §10.4, §14.2, §14.3; `R5A_FROZEN_SHORTLIST.md` §1 and §5; `R5A_OPERATOR_SCHEMA.md` §3.2, §3.4, §4.4, §4.5, §7.

## 7. PENDING.md Updates Needed

- Update `PENDING.md:9` last-updated date to `2026-04-26`.
- Add active item: **WS1 model/tokenizer provenance pinning**. Blocks WS1 cloud pilot and Phase 7 §13 item 3. Track 5 HF commit SHAs, 5 tokenizer SHAs, vLLM image digest, quant scheme.
- Add active item: **WS1 trace contract closure**. Blocks prereg-stable `LogProbTrace`; decide whether to persist `token` / `top_logprobs` or amend plan/operator schema.
- Add active item: **WS2 black-box route/API name pinning**. Blocks 9-model `P_predict` smoke; `gpt-5.1` and `claude-sonnet-4.6` still `<TBD>`.
- No current active item appears resolved; keep `Recently closed` empty.

## 8. Recommended Doc Patches

```diff
# plans/phase7-pilot-implementation.md
- docs/DECISION_20260417_phase7_interfaces.md
+ docs/DECISION_20260426_phase7_interfaces.md

# §14.2, qwen3 entries: either align to delivered DECISION/YAML
- tokenizer_family: qwen
+ tokenizer_family: qwen3
```

```diff
# docs/DECISION_20260426_phase7_interfaces.md
+ RunManifest frozen fields include:
+ - git_commit_sha
+ - fleet/runtime/sampling config hashes
+ - prompt_versions
+ - model_fingerprints
+ - white_box_checkpoint_shas
+ - vllm_image_digests / docker_image_digests
+ - runtime_caps, seed_policy
+ - runstate_db_path/hash
+ - article/perturbation/audit manifest hashes
```

```diff
# docs/DECISION_20260426_phase7_interfaces.md
- `LogProbTrace`        | plan §5.2 + schema §4.4
+ `LogProbTrace`        | plan §5.2 trace provenance fields; score fields are derived downstream
+ NOTE: if Min-K%++ remains in scope, persisted trace rows must include `top_logprobs`.
```

```diff
# PENDING.md
- Last updated: 2026-04-18
+ Last updated: 2026-04-26

+ ### WS1 provenance pinning — checkpoint/tokenizer/image digests
+ ### WS1 trace contract closure — top_logprobs/token persistence decision
+ ### WS2 route/API pinning — black-box `api_model_name` placeholders
```
