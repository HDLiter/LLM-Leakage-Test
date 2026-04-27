---
title: WS1 Cloud Execution Plan — P_logprob on AutoDL RTX PRO 6000
stage: Phase 7 / WS1
date: 2026-04-26
last_amended: 2026-04-27
status: APPROVED — Stage 0 in progress; revised for fleet expansion + GPU upgrade
authority: plans/phase7-pilot-implementation.md §5.2 (WS1 spec)
related_decisions:
  - docs/DECISION_20260426_phase7_interfaces.md (WS0 sign-off)
  - docs/DECISION_20260427_pcsg_redefinition.md (PCSG redefinition + fleet expansion + Path E + WS6 conditional)
gpu_decision: RTX PRO 6000 (Blackwell, 96 GB) single-card on AutoDL
quantization_decision:
  qwen2_5_family: AWQ-INT4 (5 sizes — official Qwen AWQ)
  qwen3_family:   AWQ-INT4 (4 sizes — official Qwen AWQ; 1.7B not available officially, skipped)
  glm_family:     fp16 (no official GLM-4-9B AWQ)
budget_cap_usd: 30  # raised from 20 to accommodate 10-model + Path E run
---

# WS1 Cloud Execution Plan

## 1. Goal

Produce token-level `LogProbTrace` parquet artifacts for all **10 white-box
fleet members** (post-2026-04-27 expansion) on the Phase 7 pilot articles
(baseline only, no perturbation), then derive:

- `E_CTS` per model (absolute familiarity)
- `E_PCSG` on the **cross-version Qwen pair** `(qwen2.5-7B, qwen3-8B)`
  (primary confirmatory temporal contrast — see
  `docs/DECISION_20260427_pcsg_redefinition.md`)
- `E_PCSG_capacity_curve` (exploratory) on Qwen2.5 `[1.5, 3, 7, 14, 32]B`
  and Qwen3 `[4, 8, 14, 32]B` capacity members

WS1 also runs the **Path-E empirical cutoff probe** in the same cloud
session, on the same instance, to localize `cutoff_observed` for each
white-box model.

WS1 hands these to WS5 for confirmatory analysis. Successful WS1 closes
plan §13 exit-gate item 3 ("`P_logprob` succeeds on all 10 white-box
models with pinned tokenizer/checkpoint provenance, and Path-E
`cutoff_observed` published").

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
| GPU | **RTX PRO 6000 (Blackwell, 96 GB) single card** on AutoDL | AutoDL availability check 2026-04-27 showed RTX PRO 6000 with 225/1580 free instances (highest availability; A6000 unavailable, 4090 zeroed). 96 GB lets us load Qwen2.5-32B / Qwen3-32B AWQ comfortably alongside hidden-state extraction headroom for WS6 prep. |
| Qwen2.5 quant | AWQ-INT4 (5 sizes: 1.5B, 3B, 7B, 14B, 32B; all Alibaba-official) | HF verified 2026-04-27 |
| Qwen3 quant | AWQ-INT4 (4 sizes: 4B, 8B, 14B, 32B; all Alibaba-official). **Qwen3-1.7B-AWQ does not exist as Alibaba-official; skipped** to avoid mixing precision within-family | HF verified 2026-04-27 |
| GLM quant | fp16 (no official AWQ) | Same as before |

**E_PCSG (cross-version) validity**: relies on the `Qwen2Tokenizer`
class being shared between Qwen2.5 and Qwen3 with byte-identical core
vocab IDs `0..151664`. AWQ-INT4 is identical across both families. Probe
articles tokenizing to IDs in `[151665, 151668]` (the Qwen3 extension
tokens) are excluded from PCSG (kept for E_CTS).

**E_PCSG_capacity_curve validity**: each capacity pair holds tokenizer
+ cutoff + paradigm fixed, varies only parameter count. Qwen2.5 family
gives 5 log-spaced points; Qwen3 gives 4. Both run as a single
within-family OLS regression of paired logprob delta on `log₂(params)`.

## 4. Cost projection

| Component | Estimate |
|---|---|
| RTX PRO 6000 @ ~¥8/hr × 12 hr (10 models pilot + Path E + smoke + provisioning) | ~¥96 (~$13) |
| 100 GB persistent data disk × 36 hr (extra room for 10 model checkpoints + Path E artifacts) | ~¥18 (~$2.5) |
| **Expected total** | **~$15** |
| **Hard stop budget** | **$30** |

Stop and review if 80% of budget is consumed before all 10 models close
their pilot loop. Path E shares the same instance — if budget is tight,
defer Path E to a separate later run.

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

### Stage 2 — Per-model loop (~9-10 hr, sequential)

Same flow per model, in this order (low-risk first, batch by family for warm checkpoint cache):

1. `qwen2.5-7b` — already verified on local Thales container; **smoke** + **pilot** (ground-truth anchor)
2. `qwen2.5-3b` — same family, smaller; smoke + pilot
3. `qwen2.5-1.5b` — same family, smallest Qwen2.5 capacity-curve point; smoke + pilot
4. `qwen2.5-14b` — same family, larger; smoke + pilot
5. `qwen2.5-32b` — same family, largest Qwen2.5; smoke + pilot
6. `qwen3-8b` — first verification of `enable_thinking=False` (irrelevant for completion endpoint, recorded as constant in trace); smoke + pilot
7. `qwen3-4b` — same family, smaller; smoke + pilot
8. `qwen3-14b` — same family, larger; smoke + pilot
9. `qwen3-32b` — same family, largest Qwen3; smoke + pilot
10. `glm-4-9b` — first verification of vLLM `echo=True` support; if it fails, fall back to `offline_hf` backend with the same checkpoint SHA

**Hidden-state extraction (WS6 prep)**: for each white-box model, additionally save
per-layer hidden states for a **30-article subset** of the pilot manifest. This
adds ~5 minutes per model (30 articles × layer-count × hidden-dim, fp16) and
~2 GB disk per model. Total ~20 GB extra, well within 100 GB persistent disk.

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

### Stage 2.5 — Path E empirical cutoff probe (~2 hr, same instance)

Runs after the main per-model pilot loop, before instance teardown.
2,160 articles (60/month × 36 months 2023-01..2025-12). Local pipeline
verification 2026-04-27 produced the fixture in ~7 s.

```bash
# 1. build the fixture (run once, ideally locally before scp-ing the
#    JSON up to the cloud — avoids needing the full CLS corpus on cloud)
python scripts/build_cutoff_probe_set.py \
  --source D:\GitRepos\Thales\datasets\cls_telegraph_raw \
  --start 2023-01 --end 2025-12 \
  --per-month 60 \
  --output data/pilot/cutoff_probe/probe_set_monthly60_36mo.json

# 2. score with the same operator already used for the main pilot —
#    just point --fixture at the probe set and write to a separate
#    output dir so the main pilot traces stay clean
python scripts/ws1_run_logprob.py \
  --model qwen2.5-7b \
  --smoke \
  --fixture data/pilot/cutoff_probe/probe_set_monthly60_36mo.json \
  --vllm-url http://localhost:8000 \
  --output-dir data/pilot/cutoff_probe/traces

# (repeat for each of the 10 white-box models)

# 3. knee detect locally back home
python scripts/run_cutoff_probe_analysis.py \
  --probe-set data/pilot/cutoff_probe/probe_set_monthly60_36mo.json \
  --traces-dir data/pilot/cutoff_probe/traces \
  --output data/pilot/cutoff_probe/cutoff_observed.json
```

Reuses the same vLLM container per model; sequentially swaps through all
10 white-box. Min-K% computed locally from saved traces (no second GPU pass).

### Stage 3 — Local re-derivation (no GPU; 2 hr)

After all 10 traces and Path E artifacts are downloaded:

```bash
python scripts/ws1_compute_metrics.py \
  --traces data/pilot/logprob_traces \
  --output data/pilot/analysis

python scripts/ws1_compute_cutoff_observed.py \
  --probe data/pilot/cutoff_probe/month_stratified_scores.parquet \
  --output data/pilot/cutoff_probe/cutoff_observed.json
```

Produces:
- `data/pilot/analysis/e_cts.parquet` — per (case, model) Min-K% scores
- `data/pilot/analysis/e_pcsg_temporal.parquet` — per case, cross-version pair paired logprob delta
- `data/pilot/analysis/e_pcsg_capacity_curve.parquet` — per (case, family, params) capacity-curve regression input
- `data/pilot/cutoff_probe/cutoff_observed.json` — per-model empirical cutoff date + knee width

Plan §5.2 exit: <1% un-recovered trace failures across the 10 models +
`cutoff_observed` populated for every white-box model.

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
