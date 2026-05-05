# WS1 AutoDL Ops Log — 2026-05-05

Purpose: preserve a sanitized operational record for WS1 AutoDL bring-up,
runtime debugging, and later audit. This file records command outcomes,
artifact paths, commits, and known operational issues. It intentionally omits
secrets, `.env` contents, API keys, HF tokens, raw CLS data, full signed
download URLs, large model weights, and trace parquet contents.

Related docs:

- `plans/ws1-cloud-execution.md`
- `docs/DECISION_20260504_autodl_nondocker_runtime.md`
- `PENDING.md`

## Instance

- SSH target: `connect.westd.seetacloud.com:10349` as `root`
- Hostname observed: `autodl-container-lalbr7shzx-3c1c85a0`
- GPU: `NVIDIA RTX PRO 6000 Blackwell Server Edition`
- VRAM: 97,887 MiB
- Driver: `595.58.03`
- NVIDIA driver CUDA capability reported by `nvidia-smi`: `13.2`
- Data disk: `/root/autodl-tmp`, 550 GB on `/dev/md0`
- `/data`: symlink to `/root/autodl-tmp/data`
- Repo path: `/data/repo`
- Model path: `/data/models`
- Trace/log path: `/data/traces`

## Local Baseline

Initial local checks on `main`:

- `git status --short --branch`: `## main...origin/main`, plus pre-existing
  untracked `.scratch/`
- `git pull --ff-only`: already up to date
- `python scripts/smoke_phase7.py --check-config`: passed
- `pytest tests/r5a -q`: passed
- Fleet cardinality preserved: 14 `P_predict`, 12 `P_logprob`, 2 PCSG
  temporal pairs
- Fleet version: `r5a-v2.3-2026-05-03`

The local ignored Path E fixture existed and was copied to AutoDL:

- `data/pilot/exposure_horizon/probe_set_monthly60_36mo.json`
- SHA-256: `c71740dca092bd2da41e11bc3fe9cec35bd683c402aa07d225847f9a963c0939`

## Repo Sync And Secrets Handling

Cloud repo was staged under `/data/repo`. Early sync used tar/archive; later
updates used git bundles because the cloud repo initially had no ordinary
`origin/main` refspec.

Secrets handling:

- `.env` was copied to `/data/repo/.env` with mode `0600`
- HF cache permissions were tightened with `chmod -R go-rwx`
- `.env`, HF token, API keys, raw CLS data, model weights, and trace parquet
  were not committed
- One early HF CLI/header traceback wrote sensitive material into
  `/data/provision_ws1.log`; that log was redacted and checked for long HF
  token patterns before continuing

## Commit Timeline

Local commits created during bring-up and pushed to `origin/main`:

- `1d95e07 Record WS1 AutoDL bring-up blocker`
- `e54d6be Support AutoDL non-Docker vLLM runtime`
- `9843736 Place AutoDL vLLM runtime under data disk`
- `f378d86 Keep AutoDL vLLM temp files on data disk`
- `a09f557 Clarify AutoDL runtime migration semantics`
- `81629be Document Blackwell vLLM runtime candidates`
- `8e3aa63 Validate Blackwell vLLM Qwen smoke`
- `60f7426 Document AutoDL WS1 operator notes`

Final synchronized state after this log entry:

- Local `main`: `60f7426`
- `origin/main`: `60f7426`
- AutoDL `/data/repo`: `60f7426`, clean working tree

## Stage 1 Docker Blocker

The original WS1 plan assumed Docker/vLLM image execution. AutoDL container
instances exposed the GPU and data disk but had no usable nested Docker path:

- No Docker CLI/daemon/socket available
- AutoDL docs indicate ordinary container instances do not support Docker
  inside the instance; Docker requires bare-metal rental

This led to the non-Docker runtime decision:

- vLLM runs directly in the AutoDL Python environment
- `vllm_image_digest` schema field remains unchanged for compatibility
- On AutoDL, `vllm_image_digest` stores a `sha256:<64-hex>` digest of
  `/data/vllm_runtime_provenance.json`

## First Non-Docker Runtime Attempt

Initial non-Docker provision installed vLLM in an isolated venv:

- Venv: `/data/venvs/ws1`
- vLLM: `0.10.0`
- Torch resolved to: `2.7.1+cu126`
- Runtime digest:
  `sha256:a5f57079381be329fa35e18101b52027f5feaea01098dbef4040fe6d10b102dd`

This imported, but Torch warned that the RTX PRO 6000 Blackwell device reports
CUDA capability `sm_120` while the wheel supported only through `sm_90`.

Root cause found later: the AutoDL base image was correct, but the isolated
venv had installed the wrong Torch wheel.

## Validated Blackwell Runtime

After switching/checking the AutoDL image, base Python was:

- Python path: `/root/miniconda3/bin/python`
- Torch: `2.8.0+cu128`
- `torch.version.cuda`: `12.8`
- Device capability: `(12, 0)`
- `torch.cuda.get_arch_list()` included `sm_120`

Validated WS1 runtime:

- Venv: `/data/venvs/ws1-cu128`
- Venv mode: `--system-site-packages`
- Reason: inherit the AutoDL base image's Blackwell-compatible Torch
- vLLM: `0.10.2`
- Transformers: `4.57.6`
- `huggingface_hub`: `0.36.2`
- Runtime digest:
  `sha256:75e40429893cdcad6cdf69a765ae252716aeff05b80f5ccec7d7d2029c8a8d2e`

Acceptance check:

```bash
python - <<'PY'
import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.get_device_name(0))
print(torch.cuda.get_device_capability(0))
print(torch.cuda.get_arch_list())
assert torch.cuda.get_device_capability(0) == (12, 0)
assert "sm_120" in torch.cuda.get_arch_list()
PY
```

The old venv was later removed:

- Removed: `/data/venvs/ws1`
- Kept: `/data/venvs/ws1-cu128`
- Approximate space recovered: 8.3 GB

## Qwen2.5-7B Compatibility Probe

Model:

- HF repo: `Qwen/Qwen2.5-7B-Instruct-AWQ`
- Local dir: `/data/models/qwen2.5-7b`
- Files completed:
  - `model-00001-of-00002.safetensors` — 3,996,422,976 bytes
  - `model-00002-of-00002.safetensors` — 1,574,406,784 bytes
  - tokenizer/config files

Download behavior:

- Small files completed quickly
- One large Xet/CAS-backed shard timed out, then resumed successfully
- A second retry process was briefly started and waited on the first process's
  HF lock; the retry process was stopped, and the original process completed

vLLM launch:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model /data/models/qwen2.5-7b \
  --served-model-name qwen2.5-7b \
  --host 127.0.0.1 \
  --port 8000 \
  --gpu-memory-utilization 0.55 \
  --max-model-len 4096 \
  --quantization awq_marlin
```

Readiness probe:

- `/v1/models`: passed
- Model exposed `allow_logprobs=true`

Direct logprob probe:

- `/tokenize`: passed
- `/v1/completions` with pre-tokenized IDs, `echo=true`, `max_tokens=0`,
  `temperature=0`, `logprobs=5`: passed
- Response length matched tokenized prompt length
- First token logprob was `None`
- Interior token logprobs were non-null

Project backend probe:

- Initial failure: backend used `/v1/tokenize`, but vLLM 0.10.2 exposed
  `/tokenize`
- Fix: fallback from `/v1/tokenize` to `/tokenize` only on 404
- Second failure: vLLM sometimes returned K+1 top-logprob entries for
  `logprobs=5`
- Fix: producer trims top-logprob lists to the declared K instead of relaxing
  the `LogProbTrace` contract
- Final single-sample backend probe passed:
  - `trace_ok=True`
  - `article_token_count=12`
  - `top_logprobs_k=5`
  - `max_top_len=5`

30-case smoke:

```bash
python scripts/ws1_run_logprob.py \
  --model qwen2.5-7b \
  --smoke \
  --vllm-url http://127.0.0.1:8000 \
  --vllm-image-digest "$(cat /data/vllm_runtime_digest.txt)" \
  --output-dir /data/traces/qwen2.5-7b-smoke-probe \
  --max-concurrency 4
```

Smoke result:

- 30/30 traces written
- Chunks:
  - `/data/traces/qwen2.5-7b-smoke-probe/qwen2.5-7b__smoke__chunks/chunk-0000.parquet`
  - `/data/traces/qwen2.5-7b-smoke-probe/qwen2.5-7b__smoke__chunks/chunk-0001.parquet`
  - `/data/traces/qwen2.5-7b-smoke-probe/qwen2.5-7b__smoke__chunks/chunk-0002.parquet`
- Consolidated:
  `/data/traces/qwen2.5-7b-smoke-probe/qwen2.5-7b__smoke.parquet`
- Summary:
  `/data/traces/qwen2.5-7b-smoke-probe/qwen2.5-7b__smoke.summary.json`
- Summary values:
  - `n=30`
  - `thinking_off_pct=100.0`
  - token min: 55
  - token max: 726
  - token mean: 174.96666666666667

The probe vLLM server was stopped after smoke. GPU returned to idle.

## Fleet Pinning Progress

Qwen2.5 family snapshot/tokenizer pinning completed on AutoDL:

- Download root: `/data/models`
- Pin source: explicit HF `main` resolutions from `huggingface_hub` API, then
  `huggingface-cli download --revision <commit> --local-dir /data/models/<id>`
- Runtime digest recorded in the local pinning log:
  `sha256:75e40429893cdcad6cdf69a765ae252716aeff05b80f5ccec7d7d2029c8a8d2e`
- Local fleet version after this milestone:
  `r5a-v2.3-2026-05-03+pinned-qwen25-20260505`

Pinned Qwen2.5 entries:

| model_id | hf_commit_sha | tokenizer_sha |
|---|---|---|
| `qwen2.5-1.5b` | `3ecffa0ceb27851800f45519bab9c457a04405e1` | `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539` |
| `qwen2.5-3b` | `3559b226e8ce77211e2c1bd7ddfb7686fec4d6dd` | `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539` |
| `qwen2.5-7b` | `b25037543e9394b818fdfca67ab2a00ecc7dd641` | `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539` |
| `qwen2.5-14b` | `539535859b135b0244c91f3e59816150c8056698` | `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539` |
| `qwen2.5-32b` | `5c7cb76a268fc6cfbb9c4777eb24ba6e27f9ee6c` | `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539` |

Operational note: the `qwen2.5-32b` download hit one Xet/CAS read timeout and
resumed successfully in the same `huggingface-cli` process. The raw AutoDL log
contains a signed CAS URL and must not be committed without sanitization.

## Validation

Local validation after the runtime/backend fixes:

- `pytest tests/r5a -q`: `145 passed`
- `python scripts/smoke_phase7.py --check-config`: passed
- `git diff --check`: passed

Cloud validation after syncing `60f7426`:

- `/data/repo` clean
- Runtime check:
  - `torch 2.8.0+cu128`
  - `sm_120=True`
  - `vllm 0.10.2`
- Runtime digest:
  `sha256:75e40429893cdcad6cdf69a765ae252716aeff05b80f5ccec7d7d2029c8a8d2e`

## Raw Cloud Logs And Artifacts

These files remain on AutoDL for detailed debugging:

- `/data/provision_ws1.log`
- `/data/provision_ws1_nondocker.log`
- `/data/traces/ws1_vllm_0102_install.log`
- `/data/traces/ws1_project_deps_install.log`
- `/data/traces/ws1_cu128_config_smoke.log`
- `/data/traces/ws1_post_8e3aa63_config_smoke.log`
- `/data/traces/qwen2.5-7b.download.log`
- `/data/traces/qwen2.5-7b.vllm.log`
- `/data/traces/qwen2.5-7b-smoke-probe.log`
- `/data/traces/qwen2.5-7b.models.json`
- `/data/traces/qwen2.5-7b.openapi.json`
- `/data/vllm_runtime_provenance.json`
- `/data/vllm_runtime_digest.txt`
- `/data/traces/qwen2.5-7b-smoke-probe/`

Do not commit raw logs blindly. Check them for secrets or signed URLs before
copying into the repo.

## Operational Lessons

- AutoDL SSH can transiently fail after TCP connect with
  `Error reading SSH protocol banner`; wait and retry before changing
  credentials.
- AutoDL image/container switches can remove `/data` even when the backing
  data disk persists. Recreate `/data -> /root/autodl-tmp/data` before running
  WS1 commands.
- Avoid isolated venvs on Blackwell AutoDL images unless the Torch wheel index
  is pinned. Prefer `--system-site-packages` so the validated base Torch wheel
  is preserved.
- Do not run concurrent HF downloads into the same `--local-dir`.
- Stop probe vLLM servers after tests so later failures are not caused by
  occupied GPU memory or port 8000.
- The next WS1 blocker is fleet pinning for the remaining white-box models,
  not Blackwell runtime compatibility.
