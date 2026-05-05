# WS1 AutoDL Stage 2 Smoke Report - 2026-05-05

Purpose: record the post-pinning Stage 2 smoke start attempt after the
white-box fleet was pinned at commit `3a8c051`. This report is sanitized:
it omits passwords, tokens, `.env` contents, signed URLs, raw CLS data, model
weights, and trace parquet contents.

Related docs:

- `docs/WS1_AUTODL_OPS_LOG_20260505.md`
- `plans/ws1-cloud-execution.md`
- `docs/DECISION_20260504_autodl_nondocker_runtime.md`

## Scope

Approved next step:

1. Fast-forward AutoDL `/data/repo` from the prior clean state to `3a8c051`.
2. Run runtime and pinned-fleet config checks on AutoDL.
3. Run bounded Stage 2 smoke probes only.
4. Keep full pilot, long Path E, Stage 2.7, and Stage 2.8 out of scope unless
   separately confirmed.
5. Stop any probe vLLM server after each smoke so GPU memory and port 8000
   remain free.

## Local Baseline

Local checks completed before cloud work:

```text
git status --short --branch
## main...origin/main
?? .scratch/

git pull --ff-only
Already up to date.

git rev-parse HEAD
3a8c0517b691ddec5988994b5f30c2fe01b43e64

git rev-parse origin/main
3a8c0517b691ddec5988994b5f30c2fe01b43e64
```

Config and unit checks:

```text
python scripts/smoke_phase7.py --check-config
passed
fleet_version: r5a-v2.3-2026-05-03+pinned-whitebox-20260505
white_box: 12
black_box: 4
p_predict_eligible: 14
p_logprob_eligible: 12
pcsg.temporal_pairs: 2

pytest tests/r5a -q
145 passed in 3.77s
```

## Cloud Execution

SSH target:

```text
ssh -p 10349 root@connect.westd.seetacloud.com
```

Non-interactive SSH probe:

```text
ssh -o BatchMode=yes -o ConnectTimeout=20 \
  -o ServerAliveInterval=10 -o ServerAliveCountMax=2 \
  -p 10349 root@connect.westd.seetacloud.com \
  "echo AUTODL_OK && hostname && pwd"
```

Result:

```text
Permission denied (publickey,password).
```

Interpretation: the SSH gateway was reachable, but this local session did not
have a usable non-interactive authentication path. No cloud repository sync,
runtime check, model load, vLLM server launch, smoke trace, or GPU operation
was performed in this attempt.

The user then provided a password out-of-band in the chat. It was saved only
as `AUTODL_SSH_PASSWORD` in ignored `.env`; the value is not reproduced here.
A temporary `.scratch/` askpass helper read that variable for SSH/SCP. The
helper contains no password literal.

AutoDL `/data/repo` could not use `git pull --ff-only` directly because its
`origin` still pointed at an older local bundle rather than a GitHub remote:

```text
origin /root/autodl-tmp/ws1_uploads/ws1_runtime_f378d86.bundle
fatal: couldn't find remote ref main
```

Resolution: local `main` was bundled and copied to AutoDL, then `/data/repo`
was fast-forwarded from `a37d373` to `3a8c051`.

```text
Updating a37d373..3a8c051
Fast-forward
after:
3a8c0517b691ddec5988994b5f30c2fe01b43e64
## main
```

Runtime and config checks after sync:

```text
runtime_digest:
sha256:75e40429893cdcad6cdf69a765ae252716aeff05b80f5ccec7d7d2029c8a8d2e

torch=2.8.0+cu128 cuda=12.8
gpu=NVIDIA RTX PRO 6000 Blackwell Server Edition
capability=(12, 0)
arch_list includes sm_120
vllm=0.10.2

python scripts/smoke_phase7.py --check-config
passed
```

Operational note: when uploading bash scripts from Windows, CRLF line endings
made one `--check-config` argument arrive with a hidden carriage return. Remote
scripts were normalized with `perl -pi -e 's/\r$//'` before execution.

## Stage 2 Bounded Smoke Results

These were smoke probes only. No full pilot, long Path E, Stage 2.7, or
Stage 2.8 run was started.

| model | backend | status | trace output | tokenizer/checkpoint | token counts |
|---|---|---:|---|---|---|
| `qwen2.5-7b` | vLLM AWQ | 30/30 | `/data/traces/ws1_stage2_smoke_20260505T120823Z/qwen2.5-7b__smoke.parquet` | matched pinned fleet | min 55 / max 726 / mean 174.97 |
| `qwen3-8b` | vLLM AWQ | 30/30 | `/data/traces/ws1_stage2_sentinel_smoke_20260505T121057Z/qwen3-8b__smoke.parquet` | matched pinned fleet | min 55 / max 726 / mean 174.97 |
| `llama-3-8b-instruct` | vLLM bf16 | 30/30 | `/data/traces/ws1_stage2_sentinel_smoke_20260505T121057Z/llama-3-8b-instruct__smoke.parquet` | matched pinned fleet | min 69 / max 850 / mean 212.87 |
| `glm-4-9b` | offline_hf fp16 | 30/30 | `/data/traces/ws1_stage2_glm_offline_smoke_20260505T121615Z/glm-4-9b__smoke.parquet` | matched pinned fleet | min 52 / max 663 / mean 162.70 |

All four summaries reported `thinking_off_pct: 100.0`.

vLLM readiness and cleanup:

- `qwen2.5-7b`: ready after 56 s; model dir 5.2 GB.
- `qwen3-8b`: ready after 76 s; model dir 5.7 GB.
- `llama-3-8b-instruct`: ready after 52 s; model dir 30 GB.
- Each vLLM probe exposed `allow_logprobs=true` and was stopped after smoke.
- Final check: no vLLM server process, port 8000 closed, GPU memory 0 MiB.

## Runtime Dependency Adjustment

The first GLM `offline_hf` attempt failed before scoring because
Transformers requires `accelerate` when loading with `device_map="cuda"`:

```text
ValueError: Using a `device_map` ... requires `accelerate`.
```

Fix applied on AutoDL:

```text
python -m pip install 'accelerate>=0.30'
installed accelerate-1.13.0
```

The runtime provenance was recaptured after this dependency change:

```text
sha256:ba5b8d6150af7f5943f7e52a5b40ab0463066317303a02af25c32f58aa523fc5
torch=2.8.0+cu128
vllm=0.10.2
accelerate=1.13.0
sm_120 present
```

GLM smoke used the new digest. Earlier Qwen/Llama smoke traces used the
pre-`accelerate` digest. For future confirmatory or pilot artifacts, use the
current recaptured digest unless the runtime changes again.

## Current Stage 1 Acceptance State

Completed:

- `config/fleet/r5a_fleet.yaml` carries pinned `hf_commit_sha` and
  `tokenizer_sha` values for all 12 white-box `P_logprob` models.
- Fleet version is
  `r5a-v2.3-2026-05-03+pinned-whitebox-20260505`.
- Fleet cardinality remains 14 `P_predict`, 12 `P_logprob`, and 2 temporal
  PCSG pairs.
- GLM remains documented as a custom slow-tokenizer case. Its
  `tokenizer_sha` is the SHA-256 of the backend-loaded tokenizer-materials
  canonical manifest, not a synthetic `tokenizer.json`.
- Local config smoke and `tests/r5a` are green.

No current blocker is known for starting bounded Stage 2 smoke after SSH
authentication is available. Confirmatory finalization still depends on later
artifacts: 12 pilot trace parquets, Path E exposure-horizon analyzer JSON,
WS6 hidden-state subset, launch env, gpu dtype, runstate DB clean gate, and
trace row-count/contract checks.

## Resume Plan

For the next cloud session, resume with:

1. Ensure `/data` exists:

   ```bash
   [ -e /data ] || ln -s /root/autodl-tmp/data /data
   ```

2. Verify `/data/repo` remains at `3a8c051` and clean.

3. Verify the current runtime digest and pinned config:

   ```bash
   source /data/venvs/ws1-cu128/bin/activate
   python - <<'PY'
   import torch, vllm
   print(torch.__version__, torch.version.cuda)
   print(torch.cuda.get_device_name(0))
   print(torch.cuda.get_device_capability(0))
   print(torch.cuda.get_arch_list())
   print(vllm.__version__)
   assert torch.cuda.get_device_capability(0) == (12, 0)
   assert "sm_120" in torch.cuda.get_arch_list()
   PY

   python scripts/smoke_phase7.py --check-config
   ```

4. If moving into broader Stage 2, continue with per-model smoke before any
   pilot run. Use the recaptured runtime digest above. GLM should use the
   `offline_hf` fallback unless a separate vLLM echo/logprobs diagnostic is
   explicitly requested.

5. After every vLLM probe:

   ```bash
   kill "$(cat /data/traces/<model>.vllm.pid)" 2>/dev/null || true
   rm -f /data/traces/<model>.vllm.pid
   ```

## Explicit Non-Actions

- No push.
- No full pilot.
- No long Path E.
- No Stage 2.7 hidden-state extraction.
- No Stage 2.8 AWQ-vs-fp16 audit.
- No black-box fleet changes.
- No change to experiment design or confirmatory contracts.
