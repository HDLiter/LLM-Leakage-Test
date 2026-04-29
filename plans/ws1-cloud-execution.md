---
title: WS1 Cloud Execution Plan — P_logprob on AutoDL RTX PRO 6000
stage: Phase 7 / WS1
date: 2026-04-26
last_amended: 2026-04-29
status: APPROVED — Stage 0 in progress; revised for fleet expansion + GPU upgrade + Stage 2.7 (WS6 Path C eager pre-compute) + Llama integration (DECISION_20260429_llama_addition)
authority: plans/phase7-pilot-implementation.md §5.2 (WS1 spec)
related_decisions:
  - docs/DECISION_20260426_phase7_interfaces.md (WS0 sign-off; partly superseded by 0427+0429)
  - docs/DECISION_20260427_pcsg_redefinition.md (PCSG redefinition + fleet expansion + Path E)
  - docs/DECISION_20260429_gate_removal.md (gate removal + WS6 unconditional via Stage 2.7 Path C eager pre-compute + BL2 n_post 350)
  - docs/DECISION_20260429_llama_addition.md (Llama-3 + Llama-3.1 P_logprob-only addition; second confirmatory PCSG pair; AWQ-vs-fp16 calibration audit)
gpu_decision: RTX PRO 6000 (Blackwell, 96 GB) single-card on AutoDL
quantization_decision:
  qwen2_5_family: AWQ-INT4 (5 sizes — official Qwen AWQ)
  qwen3_family:   AWQ-INT4 (4 sizes — official Qwen AWQ; 1.7B not available officially, skipped)
  glm_family:     fp16 (no official GLM-4-9B AWQ)
  llama3_family:  bf16 (no clean same-maintainer AWQ pair for Llama-3 + 3.1; verification §3 of refine-logs/reviews/PCSG_PAIR_HUNT/llama_family_verification_20260429.md)
budget_cap_usd: 45  # raised 2026-04-29 from 35 -> 45 to accommodate Llama (2 models × 1.5 hr Stage 2 + Path E + hidden-state ≈ 6 hr) and Stage 2.8 AWQ-vs-fp16 audit (Qwen2.5-7B bf16 × 430 cases ≈ 3 hr); ~$9 extra
---

# WS1 Cloud Execution Plan

## 1. Goal

Produce token-level `LogProbTrace` parquet artifacts for all **12
P_logprob-eligible white-box fleet members** (post-2026-04-29
split-tier: 10 full-operator + 2 Llama P_logprob-only per
`docs/DECISION_20260429_llama_addition.md`) on the Phase 7 pilot
articles (baseline only, no perturbation), then derive:

- `E_CTS` per model (absolute familiarity)
- `E_PCSG` on **two confirmatory cross-version pairs**:
  * `temporal_qwen_cross_version` `(qwen2.5-7B, qwen3-8B)` — operator-asserted cutoff
  * `temporal_llama_cross_version` `(llama-3-8B, llama-3.1-8B)` — vendor-stated cutoff
  (see `docs/DECISION_20260427_pcsg_redefinition.md` and `docs/DECISION_20260429_llama_addition.md` §2.3)
- `E_PCSG_capacity_curve` (exploratory) on Qwen2.5 `[1.5, 3, 7, 14, 32]B`
  and Qwen3 `[4, 8, 14, 32]B` capacity members

WS1 also runs the **Path-E empirical cutoff probe** in the same cloud
session, on the same instance, to localize `cutoff_observed` for each
P_logprob-eligible white-box model. The Llama probes serve as the
load-bearing **knee-detector calibration** anchor (single-point
absolute calibration + 9-month differential calibration per
`docs/DECISION_20260429_llama_addition.md` §2.4).

WS1 also runs a new **Stage 2.8 AWQ-vs-fp16 calibration audit** on
the same instance (Qwen2.5-7B in bf16 over the 430 pilot cases)
per `docs/DECISION_20260429_llama_addition.md` §2.5; this closes
Adversarial A3 (cross-precision E_CTS pooling).

WS1 hands these to WS5 for confirmatory analysis. Successful WS1 closes
plan §13 exit-gate item 3 ("`P_logprob` succeeds on all 12
P_logprob-eligible white-box models with pinned tokenizer/checkpoint
provenance, and Path-E `cutoff_observed` (or rejected-with-CI)
published").

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
| Llama-3 / 3.1 quant | bf16 (no clean same-maintainer AWQ pair for 3.0 vs 3.1; mixing community AWQs would confound calibration) | Verification 2026-04-29 — `refine-logs/reviews/PCSG_PAIR_HUNT/llama_family_verification_20260429.md` §3 |

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
| RTX PRO 6000 @ ~¥8/hr × 14 hr (12 models pilot + Path E + smoke + provisioning; +2 Llama bf16 ≈ +3 hr) | ~¥112 (~$15.5) |
| **Stage 2.7 hidden-state extraction (~6 hr offline_hf, 12 models × 30 cases)** | **~¥48 (~$6.6)** |
| **Stage 2.8 AWQ-vs-fp16 calibration audit (~3 hr Qwen2.5-7B bf16 × 430 cases)** | **~¥24 (~$3.3)** |
| 100 GB persistent data disk × 40 hr (12 checkpoints + Path E + 30-65 GB hidden states + bf16 audit) | ~¥20 (~$2.8) |
| **Expected total** | **~$28** |
| **Hard stop budget** | **$45** |

Stop and review if 80% of budget is consumed before all 12 models close
their pilot loop. Path E, Stage 2.7, and Stage 2.8 share the same instance — if
budget is tight, defer in order of: Stage 2.8 (AWQ audit, ~$3.3) → Stage 2.7
(hidden-state extraction, ~$6.6) → Path E. Path E is a hard exit-gate item
per plan §13 #3 and the Llama probes within it are the load-bearing
sanity check; do not skip.

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

### Stage 2 — Per-model loop (~11-13 hr, sequential)

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
10. `llama-3-8b-instruct` — first bf16 backend bring-up; gated repo (verify HF token has Meta access); smoke + pilot. **No P_predict** (P_logprob-only role per `docs/DECISION_20260429_llama_addition.md` §2.2). Added 2026-04-29.
11. `llama-3.1-8b-instruct` — same backend reuse; smoke + pilot. P_logprob-only. Added 2026-04-29.
12. `glm-4-9b` — first verification of vLLM `echo=True` support; if it fails, fall back to `offline_hf` backend with the same checkpoint SHA

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

### Stage 2.7 — Hidden-state extraction for WS6 (~5 hr, same instance)

Added 2026-04-29 per `docs/DECISION_20260429_gate_removal.md` §3.2.
WS6 (mechanistic memorization localization, Wang et al. 2025-style
DS / KL / activation patching) is now an **unconditional** exploratory
follow-up. Hidden states are eagerly pre-computed in this stage so
WS6 has its data regardless of behavioral E_FO outcomes.

**Subset selection** (run locally before cloud, commit to manifest):

```bash
# Build the 30-case subset from the pilot manifest:
#   - eligibility: fo_slotable=true (so the same articles support
#     WS6 false-outcome mechanism analysis)
#   - stratification: equal allocation across the pilot event-type
#     taxonomy (e.g. 5 super-types × 6 articles, or 4 × 7-8)
#   - cross-model alignment: same 30 case_ids for ALL 10 white-box
#     models so activation-patching can compare layer representations
#     across cases
python scripts/ws1_select_hidden_state_subset.py \
  --pilot-manifest data/pilot/manifests/pilot_430_cases.json \
  --output data/pilot/manifests/hidden_state_subset_30.json
```

**Per-model loop** (after Stage 2 vLLM is fully done, before Stage 2.5
Path E starts; model checkpoints already on local disk so reload is fast):

```bash
for model_id in \
    qwen2.5-{1.5b,3b,7b,14b,32b} \
    qwen3-{4b,8b,14b,32b} \
    llama-3-8b-instruct llama-3.1-8b-instruct \
    glm-4-9b; do
  docker stop $(docker ps -q --filter ancestor=vllm/vllm-openai) 2>/dev/null || true
  python scripts/ws1_run_logprob.py \
    --model "$model_id" \
    --backend offline_hf \
    --hidden-states-subset data/pilot/manifests/hidden_state_subset_30.json \
    --output-dir data/pilot/hidden_states
done
```

**Pack and transfer** (compressed shipment back to local for analysis):

```bash
bash scripts/ws1_pack_hidden_states.sh \
  --input-dir data/pilot/hidden_states \
  --output data/pilot/hidden_states.tar.zst
# Estimated 30-65 GB raw -> 35-55 GB compressed (12 white-box, +2 Llama bf16 vs prior 10);
# ~45-70 min download at AutoDL 100 Mbps
```

**Disk budget**: 30-65 GB on the 100 GB persistent disk. Within capacity.

**Smoke gate**: each per-(model, case) `.safetensors` must contain
`layer_0..layer_N` keys with shapes consistent with model card metadata
(layer count and hidden dim verified against `config.json`). The
`hidden_state_subset_hash` from the manifest must match.

### Stage 2.5 — Path E empirical cutoff probe (~2.5 hr, same instance)

Runs after the main per-model pilot loop, before instance teardown.
2,160 articles (60/month × 36 months 2023-01..2025-12). Local pipeline
verification 2026-04-27 produced the fixture in ~7 s.

The Llama probes added 2026-04-29 carry the load-bearing
**knee-detector calibration** check per
`docs/DECISION_20260429_llama_addition.md` §2.4: `cutoff_observed(llama-3-8b)`
should fall near 2023-03 (vendor-stated, modulo Chinese-coverage smear),
and the `cutoff_observed(llama-3.1-8b) − cutoff_observed(llama-3-8b)`
differential should be ~9 months. This converts Adversarial A4 (cutoff
circularity) and A2 (regime-shift artifact) into quantified-uncertainty
statements with a same-corpus control.

```bash
# 1. build the fixture (run once, ideally locally before scp-ing the
#    JSON up to the cloud — avoids needing the full CLS corpus on cloud)
python scripts/build_cutoff_probe_set.py \
  --source D:\GitRepos\Thales\datasets\cls_telegraph_raw \
  --start 2023-01 --end 2025-12 \
  --per-month 60 \
  --output data/pilot/cutoff_probe/probe_set_monthly60_36mo.json

# 2. score with the same operator already used for the main pilot —
#    use the dedicated --cutoff-probe mode so traces land in a
#    distinct output directory (Tier-0 #5 fix; was --smoke previously)
python scripts/ws1_run_logprob.py \
  --model qwen2.5-7b \
  --cutoff-probe \
  --vllm-url http://localhost:8000 \
  --vllm-image-digest sha256:...

# (repeat for each of the 12 P_logprob-eligible white-box models;
#  Llama-3 / 3.1 probes are the load-bearing calibration anchors)

# 3. knee detect locally back home (piecewise WLS + bootstrap CI;
#    Tier-0 #3 replaces the legacy threshold detector)
python scripts/run_cutoff_probe_analysis.py \
  --probe-set data/pilot/cutoff_probe/probe_set_monthly60_36mo.json \
  --traces-dir data/pilot/cutoff_probe/traces \
  --output data/pilot/cutoff_probe/cutoff_observed.json \
  --n-bootstrap 2000 \
  --max-ci-width-months 3
```

Reuses the same vLLM container per model; sequentially swaps through all
12 P_logprob-eligible white-box models. Min-K% computed locally from
saved traces (no second GPU pass).

### Stage 2.8 — AWQ-vs-fp16 calibration audit (~3 hr, same instance)

Added 2026-04-29 per `docs/DECISION_20260429_llama_addition.md` §2.5
to close Adversarial A3 (cross-precision E_CTS pooling). Llama is bf16,
which means a bf16 backend is already loaded on the same instance for
Stage 2 / 2.5 / 2.7; we reuse it to score Qwen2.5-7B in bf16 over the
full 430-case pilot manifest.

```bash
# Reload Qwen2.5-7B in bf16 (no AWQ) on the same instance:
docker stop $(docker ps -q --filter ancestor=vllm/vllm-openai) 2>/dev/null || true
docker run -d --gpus all --rm \
  -v /data/models/qwen2.5-7b-bf16:/model \
  -p 8000:8000 \
  vllm/vllm-openai@sha256:<digest> \
  --model /model --served-model-name qwen2.5-7b-bf16 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.9

python scripts/ws1_run_logprob.py \
  --model qwen2.5-7b \
  --pilot \
  --pilot-articles data/pilot/manifests/pilot_430_articles.json \
  --vllm-url http://localhost:8000 \
  --served-model-name qwen2.5-7b-bf16 \
  --output-dir data/pilot/quant_calibration \
  --vllm-image-digest sha256:...
```

**Local analysis** (after traces download):

```bash
python scripts/ws1_quant_calibration_audit.py \
  --awq data/pilot/logprob_traces/qwen2.5-7b__pilot.parquet \
  --bf16 data/pilot/quant_calibration/qwen2.5-7b__pilot.parquet \
  --output data/pilot/analysis/quant_calibration_qwen2.5_7b.parquet
```

**Decision rule** (encoded in the audit script + reported in paper):

- `|mean(delta_quant)| < 0.05 nats` → caveat-only; no correction applied
  to Qwen-AWQ Min-K% scores.
- `|mean(delta_quant)| ≥ 0.05 nats` → subtract `delta_quant` from
  Qwen-AWQ Min-K% scores before pooling with GLM-fp16 / Llama-bf16
  in fleet-level E_CTS.

Note (`docs/DECISION_20260429_llama_addition.md` §2.5): bf16 vs fp16
differences in logprob computation (~1e-3 nats) are negligible
compared to the AWQ-vs-fp16 effect size (~1e-2 to 1e-1 nats), so
treating bf16 as the fp16 reference for calibration purposes is sound.

### Stage 3 — Local re-derivation (no GPU; 2 hr)

After all 12 trace files (10 full-operator + 2 Llama bf16) and Path E
artifacts are downloaded:

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

Plan §5.2 exit: <1% un-recovered trace failures across the 12
P_logprob-eligible models + `cutoff_observed` (or rejected-with-CI)
populated for every P_logprob-eligible white-box model. Llama probes
must additionally pass the differential calibration check
(|differential − 9 months| within the bootstrap CI; if violated, open a
decision memo before publishing PCSG results).

### Stage 4 — Teardown

- Stop instance, delete data disk (unless WS5 needs traces re-derived
  on cloud, which it doesn't — traces come back to local).
- Run `scripts/ws1_pin_fleet.py` to write back tokenizer / hf_commit
  SHAs and bump fleet_version (Tier-0 #2).
- Run `scripts/ws1_finalize_run_manifest.py` to join the pinned fleet
  with traces + Path E output + pcsg_pairs hash + Docker digest +
  hidden-state subset hash + quality-gate thresholds (Tier-0 #4).
- Verify the resulting RunManifest carries all 6 new fields per plan
  §10.4 + DECISION_20260429_gate_removal §2.6 +
  DECISION_20260429_llama_addition §3.2.

## 6. Risk register (extends plan §5.2 risks)

| ID | Risk | Trigger | Response |
|---|---|---|---|
| W1 | GLM `echo=True` broken in vLLM | smoke fails on glm-4-9b | switch to `offline_hf` backend with same checkpoint SHA; record `backend=offline_hf` in trace |
| W2 | AutoDL HF mirror flaky | model download stalls | fall back to `https://hf.co` directly with proxy, or pre-download to local disk and `scp` up |
| W3 | A6000 unavailable in cheaper region | rental queue empty | accept ~30% premium for next region or wait off-hours |
| W4 | Tokenizer SHA mismatch within Qwen2.5 pair | E_PCSG cannot be paired | rerun whichever model loaded the wrong tokenizer; PCSG pair invalid until resolved |
| W5 | Qwen3 thinking tokens leak into trace | thinking_mode field non-`off` somewhere | enforce in operator: any non-`off` value -> reject and rerun |

## 7. What is NOT in WS1

- WS2 P_predict (14 P_predict-eligible models): runs locally without a GPU; OpenRouter is the right answer there
- WS3 perturbation generation and audit: independent track, can run in parallel during WS1 stage 0
- C_temporal logprob exploration (parallel white-box validation for E_TDR per shortlist §5): explicitly reserve, not in WS1
- Frequency-table construction needed for full CTS computation: deferred until pilot manifest is built (depends on WS0.5 + WS3)

## 8. Sign-off checklist

- [x] AWQ availability for 4 Qwen models confirmed (HF, 2026-04-26)
- [x] GLM AWQ unavailable → fp16 path locked
- [x] RTX PRO 6000 chosen, budget approved (raised to $45 on 2026-04-29)
- [x] HF fine-grained read-only token created (user, 2026-04-26)
- [ ] **HF Meta license click-through complete for both Llama-3-8B-Instruct and Llama-3.1-8B-Instruct** (user; tracked in PENDING.md as "Llama fleet addition — Meta HF gating pre-flight"). Verify with `huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct --include "*.json"` test pull. Required before Stage 1.
- [ ] Stage 0 modules + tests merged
- [ ] Stage 0 smoke fixture committed
- [ ] AutoDL account ready
- [ ] Stage 1 instance reserved
- [ ] **`scripts/ws1_pin_fleet.py` run**: fleet YAML carries no `<TBD>` for any of the 12 white-box `tokenizer_sha` / `hf_commit_sha` (Tier-0 #2)
- [ ] Run manifest fields populated for each of the **12 P_logprob-eligible white-box models + 4 black-box** (incl. `cutoff_observed`, `quant_scheme`, `pcsg_pair_registry_hash`, `hidden_state_subset_hash`, `quality_gate_thresholds` per plan §10.4)
- [ ] Trace failure rate < 1% across the **12 P_logprob-eligible white-box models**
- [ ] Stage 2.7 hidden-state extraction complete (30 cases × 12 models, packed and downloaded)
- [ ] Stage 2.8 AWQ-vs-fp16 calibration audit complete (`quant_calibration_qwen2.5_7b.parquet` published)
- [ ] Path E `cutoff_observed.json` produced and joined into RunManifest via `scripts/ws1_finalize_run_manifest.py` (Tier-0 #4)
- [ ] Llama differential calibration check passes (`cutoff_observed(llama-3.1) - cutoff_observed(llama-3) ≈ 9 months` within bootstrap CI; per `docs/DECISION_20260429_llama_addition.md` §2.4)
- [ ] Instance + data disk torn down
