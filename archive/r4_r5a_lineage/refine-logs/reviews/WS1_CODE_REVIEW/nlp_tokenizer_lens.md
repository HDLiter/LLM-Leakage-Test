# NLP / Tokenizer Lens Review

**Verdict**: `block`. The current cloud image pin is very likely unable to serve the two Qwen3 AWQ models, and GLM scoring semantics are not aligned between vLLM and `offline_hf`.

**Critical Findings**

| file:line | issue | why | fix |
|---|---|---|---|
| [scripts/ws1_provision_autodl.sh](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_provision_autodl.sh:26) | Pins `vllm/vllm-openai:v0.7.0`, but Qwen3 AWQ configs use `Qwen3ForCausalLM`. | vLLM v0.7.0 registry has Qwen2, not Qwen3; Qwen3 appears by v0.8.5. The Qwen3 rows in [plans/ws1-cloud-execution.md](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:102) will likely fail at model load. | Move to a tested vLLM image with `Qwen3ForCausalLM` support, e.g. `>=0.8.5`, pin digest, then rerun all echo/tokenize smoke checks. Sources: [v0.7.0 registry](https://github.com/vllm-project/vllm/blob/v0.7.0/vllm/model_executor/models/registry.py), [v0.8.5 registry](https://github.com/vllm-project/vllm/blob/v0.8.5/vllm/model_executor/models/registry.py#L104-L107), [Qwen3 config](https://huggingface.co/Qwen/Qwen3-8B-AWQ/raw/main/config.json). |
| [src/r5a/backends/offline_hf.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/offline_hf.py:95) + [src/r5a/backends/vllm_logprob.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/vllm_logprob.py:199) | GLM vLLM and HF fallback score different token streams. | vLLM completion/tokenize default `add_special_tokens=True`; GLM tokenizer prepends `[gMASK], <sop>`. Offline fallback uses `add_special_tokens=False`, so GLM fallback scores raw article without the model-native prefix. | Choose one policy and make both backends explicit. Recommended: feed model-native special tokens for GLM, but exclude GLM prefix tokens from the saved article trace. Source: [GLM tokenizer prefix](https://huggingface.co/THUDM/glm-4-9b-chat/blob/main/tokenization_chatglm.py#L123-L161). |

**High Findings**

| file:line | issue | why | fix |
|---|---|---|---|
| [src/r5a/backends/vllm_logprob.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/vllm_logprob.py:124) | Drops any `None`, not just the first prompt token. | vLLM v0.7.0 deliberately prepends `None` only for token index 0. Interior `None` means an API/logprob assembly problem and should not be silently removed. | Require `token_logprobs[0] is None` and all later positions non-null after any declared prefix policy. Source: [vLLM first-token behavior](https://github.com/vllm-project/vllm/blob/v0.7.0/vllm/engine/output_processor/single_step.py#L34-L42). |
| [src/r5a/backends/vllm_logprob.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/vllm_logprob.py:145) | ±1 count tolerance plus `head_drop` can silently misalign IDs. | If `/tokenize` is longer than completion, `head_drop=0` and IDs shift. `-1` placeholders at [line 164](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/vllm_logprob.py:164) can survive into CTS/PCSG. | Tokenize once, then pass integer token IDs as the completion `prompt`; require exact length equality. Never emit `-1`; fail the trace. |
| [scripts/ws1_provision_autodl.sh](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_provision_autodl.sh:120) | GLM vLLM launch path lacks `--trust-remote-code`. | GLM-4-9B-Chat uses a custom `ChatGLM4Tokenizer`; offline HF sets `trust_remote_code=True`, vLLM launch does not. | Add a GLM-specific launch command with `--trust-remote-code`; if vLLM still fails, use `offline_hf` with the corrected special-token policy. |

**Medium Findings**

| file:line | issue | why | fix |
|---|---|---|---|
| [src/r5a/contracts.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/contracts.py:226) | `LogProbTrace` lacks `quant_scheme` / precision. | A standalone Parquet cannot distinguish AWQ INT4 from fp16; runbook says quant is only in manifest. | Add `quant_scheme`, `weight_dtype`, and vLLM image digest or launch hash to trace rows. |
| [config/fleet/r5a_fleet.yaml](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:61) | Qwen3 says `append_no_think_sentinel`, but completion scoring must not append `/no_think`. | Qwen3 `enable_thinking` is chat-template behavior. Raw `/v1/completions` does not apply that template; appending a sentinel would change the scored article. | Change fleet wording for P_logprob to `completion_no_chat_template`; keep `thinking_mode="off"` as a recorded adapter state. Source: [Qwen3 thinking docs](https://huggingface.co/Qwen/Qwen3-8B-AWQ/blob/main/README.md#switching-between-thinking-and-non-thinking-mode). |
| [config/fleet/r5a_fleet.yaml](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:24) | `tokenizer_sha: <TBD>` has no resolver glue. | [src/r5a/fleet.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/fleet.py:94) hashes YAML after loading, but nothing computes tokenizer hashes or writes them back. | After download, compute `tokenizer.json` git-blob SHA and SHA256, write YAML, reload fleet, record `raw_yaml_sha256`. |
| [scripts/ws1_provision_autodl.sh](D:/GitRepos/LLM-Leakage-Test/scripts/ws1_provision_autodl.sh:28) | HF mirror exact-revision availability is unverified. | With `<pinned-sha>` still TBD, no one can know whether `hf-mirror.com` has all exact commits/LFS blobs. | Try mirror first; on failure use direct HF via proxy or pre-download locally and `rsync/scp`. Always verify local file hashes and resolved HF commit SHA. |
| [config/runtime/r5a_runtime.yaml](D:/GitRepos/LLM-Leakage-Test/config/runtime/r5a_runtime.yaml:23) | `max_concurrency=16` is probably correct, but not a reproducibility proof. | Prompt logprobs are deterministic semantically, but batching/AWQ kernels can move low-order floats. KV eviction should not change the target distribution. | Smoke duplicate 5 articles at concurrency 1 and 16; require exact token IDs and bounded `max_abs_logprob_delta`. |

**Low / Info**

- [src/r5a/backends/vllm_logprob.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/vllm_logprob.py:207): `echo=True, max_tokens=0` is valid for vLLM v0.7.0. vLLM internally maps no-generation echo to one engine token, but returns only prompt text/logprobs. Source: [vLLM completion path](https://github.com/vllm-project/vllm/blob/v0.7.0/vllm/entrypoints/openai/protocol.py#L809-L845), [response branch](https://github.com/vllm-project/vllm/blob/v0.7.0/vllm/entrypoints/openai/serving_completion.py#L410-L444).
- [src/r5a/backends/vllm_logprob.py](D:/GitRepos/LLM-Leakage-Test/src/r5a/backends/vllm_logprob.py:199): `/v1/tokenize` and `/v1/completions` both default `add_special_tokens=True` in v0.7.0, so Qwen count agreement is expected; GLM agreement can still hide synthetic-prefix contamination.
- [data/pilot/fixtures/smoke_30.json](D:/GitRepos/LLM-Leakage-Test/data/pilot/fixtures/smoke_30.json:1): 24/6 pre/post and host coverage are fine for sampling, but add rare-token cases: mixed tickers, URLs, full-width numbers, Greek/drug names, `<think>`, `[gMASK]`, `<|im_start|>`, and long numeric tables.

**Per-Model Risk Table**

| model | risk | top concrete concern | smoke-day check |
|---|---:|---|---|
| qwen2.5-7b | Low | No BOS expected; AWQ logprobs should align. | `/tokenize` IDs equal HF `add_special_tokens=True/False`; first logprob only is `None`. |
| qwen2.5-14b | Medium | Pair validity depends on exact tokenizer hash with 7B. | Same article raw IDs equal 7B after first-token drop. |
| qwen3-8b | High | vLLM v0.7.0 likely cannot load `Qwen3ForCausalLM`. | `/v1/models` starts; echo text equals article; no `<think>` tokens in echoed prompt. |
| qwen3-14b | High | Same Qwen3 support issue plus larger AWQ memory. | Same as 8B, plus concurrency 1 vs 16 duplicate delta check. |
| glm-4-9b | High | `[gMASK]<sop>` prefix and remote tokenizer can skew/fail traces. | Compare vLLM and HF token IDs under the chosen special-token policy; saved trace excludes prefix tokens. |

**vLLM-Version Gotchas To Document**

- v0.7.0 supports `max_tokens=0` echo, but internally sets engine `max_tokens=1`; ignore `completion_tokens` for this path.
- First prompt-token logprob is `None`; any later `None` is a failure.
- `/v1/tokenize` and completion default to `add_special_tokens=True`; set this explicitly in both requests.
- Qwen3 requires a vLLM version with `Qwen3ForCausalLM` registered.
- GLM needs `--trust-remote-code` and an explicit prefix policy.
- After any vLLM image bump, rerun the 30-case smoke before pilot traces.
