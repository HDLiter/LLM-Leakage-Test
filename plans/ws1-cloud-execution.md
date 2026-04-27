---
title: WS1 Cloud Execution Plan — P_logprob on AutoDL A6000
stage: Phase 7 / WS1
date: 2026-04-26
status: APPROVED — local Stage 0 implementation in progress
authority: plans/phase7-pilot-implementation.md §5.2 (WS1 spec)
related_decisions:
  - docs/DECISION_20260426_phase7_interfaces.md (WS0 sign-off)
gpu_decision: A6000 48GB single-card on AutoDL
quantization_decision:
  qwen_family: AWQ-INT4 (official Qwen AWQ checkpoints)
  glm_family:  fp16 (no official GLM-4-9B AWQ; AWQ run aborted)
budget_cap_usd: 20
---

# WS1 Cloud Execution Plan

## 1. Goal

Produce token-level `LogProbTrace` parquet artifacts for all 5 white-box
fleet members on the Phase 7 pilot articles (baseline only, no
perturbation), then derive `E_CTS` per-model and `E_PCSG` on the two
tokenizer-matched temporal pairs. WS1 hands these to WS5 for confirmatory
analysis. Successful WS1 closes plan §13 exit-gate item 3 ("`P_logprob`
succeeds on all 5 white-box models with pinned tokenizer/checkpoint
provenance").

## 2. Platform

**AutoDL** (Chinese GPU rental). SSH supported, mirror market includes
official vLLM image, HF downloads via `hf-mirror.com`. OpenRouter and
similar API gateways are *not* viable for WS1 because every hosted API
has stripped prompt-side `echo=True` logprobs (project memory
`infra_capabilities.md` confirms DeepSeek explicitly forbids the
`echo+logprobs` combo; OpenAI chat API removed echo years ago;
Anthropic exposes no logprobs). P_logprob requires direct vLLM access.

## 3. GPU and quantization

| Decision | Value | Reason |
|---|---|---|
| GPU | A6000 48 GB single card | GLM-4-9B fp16 ≈ 18 GB weights + KV/activation overhead; 4090 24 GB is the OOM-risk knife edge. Differential cost is ~$1.5; not worth the swap-mid-pilot risk |
| Qwen2.5/3 quant | AWQ-INT4 (official `Qwen/*-AWQ` checkpoints) | All four AWQ repos verified existent (2026-04-26 web check) |
| GLM quant | fp16 (no official AWQ) | Search 2026-04-26 returned only GGUF and unofficial community AWQs; not worth the risk for a model that anchors no E_PCSG pair |

**E_PCSG validity**: only matters that *within* a tokenizer pair, both
models share the same quant scheme. Qwen2.5-7B and Qwen2.5-14B are both
AWQ; Qwen3-8B and Qwen3-14B are both AWQ. GLM-4-9B is not part of any
pair (different tokenizer family). E_CTS is per-model self-scaled, so
mixed precision across the fleet is acceptable as long as quantization
is recorded in the run manifest.

## 4. Cost projection

| Component | Estimate |
|---|---|
| A6000 instance @ ~¥3.5/hr × 7 hr | ~¥24.5 (~$3.5) |
| 50 GB persistent data disk × 24 hr | ~¥12 (~$1.7) |
| **Expected total** | **~$5** |
| **Hard stop budget** | **$20** |

Stop and review if 80% of budget is consumed before all 5 models close
their pilot loop. Same posture as plan §11.3.

## 5. Stages

### Stage 0 — Local implementation (no GPU; 1-1.5 days)

Deliverables:

| Path | Purpose |
|---|---|
| `src/r5a/analysis/logprob_metrics.py` | Min-K%, PCSG, CTS stub |
| `src/r5a/backends/vllm_logprob.py` | async httpx client to `/v1/completions` |
| `src/r5a/backends/offline_hf.py` | HF forward fallback for GLM if echo unsupported |
| `src/r5a/operators/p_logprob.py` | Operator + trace persistence (Parquet) |
| `scripts/ws1_run_logprob.py` | CLI: `--smoke` / `--pilot`, `--model`, `--vllm-url` |
| `scripts/ws1_build_smoke_fixture.py` | Builds `data/pilot/fixtures/smoke_30.json` from seed |
| `scripts/ws1_provision_autodl.sh` | AutoDL bring-up (HF mirror, model SHA pull, vLLM start) |
| `tests/r5a/test_logprob_metrics.py` | Min-K% / PCSG correctness |
| `tests/r5a/test_p_logprob_serialization.py` | Parquet roundtrip |

Stage 0 exit: pytest green; smoke fixture produces 30 valid records.

### Stage 1 — AutoDL bring-up (1 hr)

1. Reserve A6000 48 GB + 50 GB disk; record region and host (latency
   matters for HF mirror).
2. SSH in. Run `ws1_provision_autodl.sh`:
   - export `HF_ENDPOINT=https://hf-mirror.com`
   - `huggingface-cli login` with the user's fine-grained read-only token
   - mkdir `/data/{models,traces,repo}`
   - `docker pull vllm/vllm-openai:<version>` and capture digest
   - `git clone` or `rsync` repo into `/data/repo`
3. Sanity: `nvidia-smi` confirms A6000; `vllm --version` matches the
   pinned image.

### Stage 2 — Per-model loop (5-6 hr, sequential)

Same flow per model, in this order (low-risk first):

1. `qwen2.5-7b` — already verified on local Thales container; confidence baseline
2. `qwen2.5-14b` — same family, larger
3. `qwen3-8b` — first verification of `enable_thinking=False` (irrelevant for completion endpoint, recorded as constant in trace)
4. `qwen3-14b` — same as 3, larger
5. `glm-4-9b` — first verification of vLLM `echo=True` support; if it fails, fall back to `offline_hf` backend with the same checkpoint SHA

Per-model script:

```bash
huggingface-cli download Qwen/Qwen2.5-7B-Instruct-AWQ \
  --revision <pinned-sha> \
  --local-dir /data/models/qwen2.5-7b
docker run -d --gpus all --rm \
  -v /data/models/qwen2.5-7b:/model \
  -p 8000:8000 \
  vllm/vllm-openai@sha256:<digest> \
  --model /model --served-model-name qwen2.5-7b \
  --gpu-memory-utilization 0.9
# health
curl -s http://localhost:8000/v1/models
# smoke
python scripts/ws1_run_logprob.py --model qwen2.5-7b --smoke \
  --vllm-url http://localhost:8000 \
  --fixture data/pilot/fixtures/smoke_30.json
# pilot (only after smoke passes)
python scripts/ws1_run_logprob.py --model qwen2.5-7b --pilot \
  --vllm-url http://localhost:8000 \
  --manifest data/pilot/manifests/pilot_100_cases.json
docker stop $(docker ps -q --filter ancestor=vllm/vllm-openai)
```

Smoke gate per model:
- `article_token_count == tokenizer.encode(text).length` within ≤1 (BOS/EOS allowed; rule logged)
- 30/30 cases return non-empty token logprobs of equal length to token IDs
- `thinking_mode == "off"` written on every record
- E_CTS, E_PCSG calculable end-to-end on the smoke set

### Stage 3 — Local re-derivation (no GPU; 1 hr)

After all 5 traces are downloaded:

```bash
python scripts/ws1_compute_metrics.py \
  --traces data/pilot/logprob_traces \
  --output data/pilot/analysis
```

Produces:
- `data/pilot/analysis/e_cts.parquet` — per (case, model) Min-K% scores
- `data/pilot/analysis/e_pcsg.parquet` — per (case, qwen pair) paired logprob gap

Plan §5.2 exit: <1% un-recovered trace failures across the 5 models.

### Stage 4 — Teardown

- Stop instance, delete data disk (unless WS5 needs traces re-derived
  on cloud, which it doesn't — traces come back to local).
- Update run manifest with: vLLM image digest, 5 × HF commit SHA, 5 ×
  tokenizer SHA, GPU model, quant scheme per model.

## 6. Risk register (extends plan §5.2 risks)

| ID | Risk | Trigger | Response |
|---|---|---|---|
| W1 | GLM `echo=True` broken in vLLM | smoke fails on glm-4-9b | switch to `offline_hf` backend with same checkpoint SHA; record `backend=offline_hf` in trace |
| W2 | AutoDL HF mirror flaky | model download stalls | fall back to `https://hf.co` directly with proxy, or pre-download to local disk and `scp` up |
| W3 | A6000 unavailable in cheaper region | rental queue empty | accept ~30% premium for next region or wait off-hours |
| W4 | Tokenizer SHA mismatch within Qwen2.5 pair | E_PCSG cannot be paired | rerun whichever model loaded the wrong tokenizer; PCSG pair invalid until resolved |
| W5 | Qwen3 thinking tokens leak into trace | thinking_mode field non-`off` somewhere | enforce in operator: any non-`off` value -> reject and rerun |

## 7. What is NOT in WS1

- WS2 P_predict (9-model API fleet): runs locally without a GPU; OpenRouter is the right answer there
- WS3 perturbation generation and audit: independent track, can run in parallel during WS1 stage 0
- C_temporal logprob exploration (parallel white-box validation for E_TDR per shortlist §5): explicitly reserve, not in WS1
- Frequency-table construction needed for full CTS computation: deferred until pilot manifest is built (depends on WS0.5 + WS3)

## 8. Sign-off checklist

- [x] AWQ availability for 4 Qwen models confirmed (HF, 2026-04-26)
- [x] GLM AWQ unavailable → fp16 path locked
- [x] A6000 chosen, budget approved
- [x] HF fine-grained read-only token created (user, 2026-04-26)
- [ ] Stage 0 modules + tests merged
- [ ] Stage 0 smoke fixture committed
- [ ] AutoDL account ready
- [ ] Stage 1 instance reserved
- [ ] Run manifest fields populated for each model
- [ ] Trace failure rate < 1% across the 5 models
- [ ] Instance + data disk torn down
