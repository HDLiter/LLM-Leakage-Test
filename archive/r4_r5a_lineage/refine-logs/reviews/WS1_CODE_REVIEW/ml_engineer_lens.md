# ML Engineer Lens Review

## 1. **Verdict**

**block**. Stage-0 unit tests pass, but this is not ready for the AutoDL cloud run: `--pilot` cannot run, mid-run failures lose all completed traces, and the vLLM alignment path can silently emit corrupted token IDs/logprob rows.

Verification run locally:
`22 passed` for WS1 metric/serialization tests, and `scripts/smoke_phase7.py --check-config` validates the 5+4 fleet split and runtime caps.

## 2. **Critical Findings**

| file:line | issue | why it matters | fix |
|---|---|---|---|
| `scripts/ws1_run_logprob.py:141-152` | `--pilot` mode is a hard stub that always exits. | The cloud plan calls this CLI for the 100-case pilot; the first real pilot command will fail before any model call. | Implement manifest loading before cloud run. Add an article source argument, load `PilotManifest`, join by `case_id`, verify `sha256(text) == PilotCase.article_hash`, then return `ArticleRecord`s. |
| `scripts/ws1_run_logprob.py:216-230` | The runner computes all traces in memory and writes Parquet only after full success. | One failed request discards all successful traces from that model; no resume hook or request-item lineage is used despite the plan requiring checkpointed resume. | Replace the all-at-once write with per-case or chunked persistence plus skip-existing behavior. Minimum: write `case_id`-scoped temp chunks and merge at close; better: integrate `runstate_db` with `success/retryable/terminal_skipped`. |
| `src/r5a/backends/vllm_logprob.py:124-164` + `src/r5a/contracts.py:226-241` | vLLM drops every `None` logprob and inserts `-1` token IDs for alignment misses; the contract does not reject either. | Interior `None`s or BOS/EOS mismatches can silently produce traces whose token IDs no longer represent the scored text. That corrupts E_CTS/E_PCSG inputs. | Only allow `None` at the first position; raise on interior `None`. Remove the `-1` placeholder path. Add a `LogProbTrace` `model_validator` enforcing `article_token_count == len(raw_token_ids) == len(token_logprobs)`, finite logprobs, and non-negative token IDs. |

## 3. **High Findings**

| file:line | issue | why it matters | fix |
|---|---|---|---|
| `src/r5a/contracts.py:226-241`, `src/r5a/backends/vllm_logprob.py:121-132`, `src/r5a/operators/p_logprob.py:126-149` | `top_logprobs` are requested conceptually but discarded and not persisted. | `compute_mink_pp` exists but cannot be computed from saved traces; schema drift later would require rerunning models. | Add `top_logprobs` to `LogProbTrace` and Parquet, aligned to kept token positions. Store vLLM `top_logprobs` as `list[dict[str, float]]` or a JSON column with a schema version. |
| `src/r5a/operators/p_logprob.py:90-100`, `scripts/ws1_run_logprob.py:216-222` | `asyncio.gather` propagates the first exception while sibling tasks can keep running; the CLI then closes the shared `AsyncClient`. | A single failing article can leave in-flight calls racing against client shutdown, creating noisy secondary failures and uncertain vLLM load. | Use `asyncio.TaskGroup` or explicit task cancellation/await-on-error before closing the backend. |
| `scripts/ws1_run_logprob.py:155-175`, `config/fleet/r5a_fleet.yaml:94-99` | The runner does not resolve `p_logprob.echo_supported`, `fallback`, or `thinking_control` from fleet config. | GLM is configured as `echo_supported: false` with `offline_hf_scorer`, but the default CLI still tries vLLM unless the operator remembers flags manually. | Make backend selection config-driven, with explicit `--force-vllm` only for smoke experiments. Enforce thinking-control validation in backend construction. |
| `scripts/ws1_run_logprob.py:168-175`, `config/runtime/r5a_runtime.yaml:11-26` | Runtime `retry_max` and `timeout_seconds` are not passed into `VLLMLogprobBackend`. | Cloud behavior can diverge from the frozen runtime config. | Pass `timeout_seconds=runtime.runtime.timeout_seconds` and `max_retries=runtime.runtime.retry_max` when constructing the backend. |
| `src/r5a/backends/offline_hf.py:81-91`, `scripts/ws1_run_logprob.py:218-222` | `OfflineHFBackend` has no `close()`/GPU cleanup path, and the CLI only calls `aclose`. | GLM fallback can retain model memory until process exit; brittle if the runner later handles multiple models in one process. | Add `close()` deleting model/tokenizer, `gc.collect()`, and `torch.cuda.empty_cache()` when CUDA is available; call either `aclose()` or `close()` in the CLI `finally`. |
| `src/r5a/backends/vllm_logprob.py:218-240` | Retry policy retries all HTTP status errors, including permanent 400/422 request-shape failures; it also sleeps after the last failed attempt. | Bad request contracts waste cloud time and hide actionable response bodies. | Retry only transport errors, timeouts, 408/409/425/429, and 5xx. Fail fast on other 4xx with response text included in `VLLMBackendError`. |
| `src/r5a/contracts.py:304-323`, `scripts/ws1_provision_autodl.sh:101-104` | `RunManifest` has no fields for tokenizer SHAs, vLLM image digest, quantization, GPU dtype, launch args, or environment hash. | The provisioner records a digest file, but the typed manifest cannot cite the full white-box provenance required by plan §10. | Extend `RunManifest` with `white_box_tokenizer_shas`, `vllm_image_digests`, `white_box_quantization`, `gpu`, and `launch_args_hashes`; have the runner ingest `/data/vllm_image_digest.txt`. |
| `requirements.txt:1-12` | `pyarrow` and `pyyaml` are missing from the repo requirements. | Fresh local or CI installs can fail importing `p_logprob`, `fleet`, or `runtime`, even though AutoDL provisioning installs them manually. | Add `pyarrow>=14` and `pyyaml>=6` to `requirements.txt`. |
| `scripts/ws1_provision_autodl.sh:50-52`, `scripts/ws1_provision_autodl.sh:125-127` | Provisioning creates `/data/repo` but never clones or syncs the repo, then next steps `cd /data/repo`. | A fresh AutoDL instance following this script will not have runnable code. | Add `REPO_URL`/`REPO_REF` clone logic, or make the script fail with a clear “rsync repo first” guard if `/data/repo/scripts/ws1_run_logprob.py` is absent. |

## 4. **Medium Findings**

| file:line | issue | fix |
|---|---|---|
| `src/r5a/operators/p_logprob.py:103-118` | Sync HF work is sent through `asyncio.to_thread`; cancellation will not stop the GPU forward pass and can leave cleanup timing unclear. | For the sync backend, call `self.backend.trace(...)` directly in the sequential path, or add an explicit executor lifecycle and cancellation note. |
| `src/r5a/operators/p_logprob.py:70-80` | Async detection via `inspect.iscoroutinefunction(backend.trace)` is brittle for decorated callables or sync functions returning awaitables. | Normalize the return value: call `trace(...)`, then `await` it if `inspect.isawaitable(result)`. |
| `src/r5a/runtime.py:20-22`, `config/runtime/r5a_runtime.yaml:20-26` | YAML `proxy: none` loads as string `"none"`, not Python `None`. | Add a Pydantic validator converting `"none"`/`"null"`/`""` to `None`; adapters should pass the normalized value. |
| `src/r5a/backends/vllm_logprob.py:199-205`, `src/r5a/backends/vllm_logprob.py:230-231` | Malformed JSON or malformed token payloads are not consistently wrapped in backend-specific errors. | Catch `ValueError` from `resp.json()` and token coercion; raise `VLLMBackendError` with path, status, and trimmed body. |
| `src/r5a/operators/p_logprob.py:126-149` | Parquet schema is manually flattened with no `schema_version`; added trace fields will be silently omitted unless every mapping is updated. | Add `schema_version`, and add a unit test asserting every persisted `LogProbTrace` field is represented intentionally. |
| `scripts/ws1_run_logprob.py:126-132` | `<TBD>` SHAs only warn. | Keep warning for `--smoke`, but make `--pilot` fail if tokenizer or checkpoint SHAs remain `<TBD>`. |
| `tests/r5a/test_logprob_metrics.py:24-198`, `tests/r5a/test_p_logprob_serialization.py:49-86` | Tests cover pure metrics and Parquet roundtrip, but not vLLM HTTP behavior, async cancellation, retries, or resume. | Add mocked `httpx` tests for 400/429/5xx, malformed payloads, token mismatch, interior `None`, and operator sibling cancellation. |

## 5. **Low / Info**

| file:line | note |
|---|---|
| `scripts/smoke_phase7.py:114-123` | The operator smoke gate is still a stub. This matches the WS0 memo, but it should not be treated as the WS2 9-model gate. |
| `src/r5a/backends/vllm_logprob.py:106-111` | `list_models()` exists but the CLI does not call it to verify `served_model_name` before the run. Add a preflight check. |
| `src/r5a/operators/p_logprob.py:273-278` | Summary JSON writes are non-atomic. Use the same temp-and-replace pattern as Parquet. |
| `scripts/ws1_provision_autodl.sh:94-96` | HF token is not echoed or written to `.bashrc`, good. It is still passed as a process argument briefly; prefer a token file/stdin flow if available, then `unset HF_TOKEN`. |
| `scripts/ws1_provision_autodl.sh:55-66` | `.bashrc` patch is idempotent only for first values. If `DATA_ROOT` or `HF_ENDPOINT` changes, the old block remains. |

## 6. **What’s Already Good**

- `offline_hf` lazy-imports `torch`/`transformers` only at backend construction, preserving the local `rag_finance` constraint: `src/r5a/backends/offline_hf.py:55-64`.
- vLLM uses a single long-lived `httpx.AsyncClient` with `trust_env=False` and `proxy=None`: `src/r5a/backends/vllm_logprob.py:86-92`.
- The vLLM backend uses `/v1/completions`, not chat wrapping: `src/r5a/backends/vllm_logprob.py:207-216`.
- The CLI closes async backends in a `finally`: `scripts/ws1_run_logprob.py:216-222`.
- Pydantic `extra="forbid"` is consistently applied across contracts/config loaders.
- Parquet uses temp-file then replace for the main trace artifact: `src/r5a/operators/p_logprob.py:223-229`.
- Current pure tests pass and are useful guardrails for metrics and serialization.

## 7. **Cloud-Execution Readiness Checklist**

- Implement `--pilot` manifest-to-article loading with article hash verification.
- Add per-case/chunk checkpointing and resume; do not run the 100-case pilot with one final write.
- Add trace validators and remove `-1` token ID fallback before any cloud trace is accepted.
- Persist `top_logprobs` or remove Min-K%++ from WS1 claims until the field exists.
- Enforce no `<TBD>` tokenizer/checkpoint SHAs for `--pilot`.
- Pass runtime timeout/retry settings into the backend.
- Add mocked vLLM tests for retries, 4xx fail-fast, malformed JSON, token mismatch, and cancellation.
- Confirm GLM fallback path with `--with-torch`, then verify `close()` releases GPU memory.
- Record vLLM digest, quantization, launch args, GPU model, tokenizer SHAs, and HF SHAs into a typed run manifest.
- Ensure `/data/repo` is actually populated by clone/rsync before following the provisioner’s next steps.
