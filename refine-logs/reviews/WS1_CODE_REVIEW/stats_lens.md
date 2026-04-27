# Stats / Measurement Lens Review

**Verdict**: `block`

Do not run WS1 cloud yet. The raw Min-K% and PCSG arithmetic are mostly directionally coherent, but the trace contract cannot support confirmatory Min-K%++ recomputation, and the current PCSG pairing story does not yet guarantee a true late-vs-early temporal contrast.

## Critical findings

| file:line | issue | why it matters | fix |
|---|---|---|---|
| [src/r5a/contracts.py:231](D:/GitRepos/LLM-Leakage-Test/src/r5a/contracts.py:231), [src/r5a/operators/p_logprob.py:126](D:/GitRepos/LLM-Leakage-Test/src/r5a/operators/p_logprob.py:126), [plans/phase7-pilot-implementation.md:235](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:235) | `LogProbTrace` persists realized `token_logprobs` only; `top_logprobs` are requested by spec but dropped. | `E_CTS` is specified as Min-K++ in plan §8.1A, and Min-K++ needs per-position distribution statistics. Once cloud traces are written, this cannot be reconstructed without rerunning GPU. | Add persisted per-position `top_logprobs`, or better: store full-vocab-derived `minkpp_mu`, `minkpp_sigma`, realized rank, and `top_logprobs_requested`. |
| [src/r5a/analysis/logprob_metrics.py:98](D:/GitRepos/LLM-Leakage-Test/src/r5a/analysis/logprob_metrics.py:98) | `compute_mink_pp` uses an unweighted arithmetic mean/std over returned top-K logprobs. | Zhang et al. define μ and σ as probability-weighted moments over the full vocabulary distribution, not an equal-weight sample of top tokens. This changes the estimand, not just precision. | Compute μ/σ from full logits in the backend and persist them. If forced to use top-K, renormalize by probabilities and label it exploratory approximation. |
| [plans/phase7-pilot-implementation.md:704](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:704), [config/fleet/r5a_fleet.yaml:22](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:22), [config/fleet/r5a_fleet.yaml:39](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:39) | PCSG requires `late - early`, but same-tokenizer Qwen2.5 pair entries have the same cutoff date; Qwen3 pair entries also share one cutoff. | A same-cutoff pair estimates size/capability drift, not cutoff exposure. That invalidates `E_PCSG` as a temporal memorization estimand if these are the only pairs. | Freeze an explicit pair registry with `early_model`, `late_model`, cutoff dates, tokenizer SHA, and quant scheme. If no true tokenizer-matched temporal pair exists, demote PCSG or redefine it before prereg. |
| [plans/ws1-cloud-execution.md:46](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:46), [src/r5a/contracts.py:231](D:/GitRepos/LLM-Leakage-Test/src/r5a/contracts.py:231) | Quantization scheme is discussed in the cloud plan but absent from trace rows. | AWQ-Qwen vs fp16-GLM absolute logprob/CTS comparisons are confounded by inference regime. PCSG within identical AWQ pairs is less affected, but E_CTS pooling is not. | Persist `quant_scheme`, `dtype`, backend version, launch config/run_manifest_id. Analyze E_CTS with per-model or per-quant normalization; do not read raw cross-model CTS as absolute familiarity. |

## High findings

| file:line | issue | recommendation |
|---|---|---|
| [src/r5a/analysis/logprob_metrics.py:68](D:/GitRepos/LLM-Leakage-Test/src/r5a/analysis/logprob_metrics.py:68), [plans/phase7-pilot-implementation.md:703](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:703) | Top-5 Min-K++ is not confirmatory-quality. Top-K truncates the low-probability tail and usually underestimates σ; for low-ranked realized tokens this inflates negative z-scores and affects bottom-K selection. | Request more if staying with vLLM API. `K=20` is the current low-friction floor; `50/100` helps but still is not the Zhang estimand. Best fix is full-logit μ/σ summaries. |
| [src/r5a/analysis/logprob_metrics.py:101](D:/GitRepos/LLM-Leakage-Test/src/r5a/analysis/logprob_metrics.py:101) | Skipping σ=0 positions silently changes the target population. | With full vocab, σ=0 is essentially impossible; with top-K it is an artifact. Count and report degenerate positions; do not silently drop them in confirmatory scoring. |
| [src/r5a/analysis/logprob_metrics.py:172](D:/GitRepos/LLM-Leakage-Test/src/r5a/analysis/logprob_metrics.py:172), [refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:164](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md:164) | PCSG mean-over-all-tokens is consistent with plan §8.1A, but the framework doc also says PCSG is computed from E_CTS values. | Lock prereg wording: PCSG = mean token logprob delta over identical token sequence, not bottom-K and not CTS delta. Bottom-K PCSG would be a different estimand. |
| [src/r5a/analysis/logprob_metrics.py:123](D:/GitRepos/LLM-Leakage-Test/src/r5a/analysis/logprob_metrics.py:123) | `dict[int, float]` CTS interface only supports token-unigram baselines. | That is acceptable only if prereg locks CTS as per-tokenizer unigram calibration. Character n-gram or LM-derived priors need a richer scorer interface. |

## Medium findings

- Min-K% implementation is faithful to Shi et al. on sign and aggregation: bottom K% realized token logprobs, averaged; higher/less negative means more familiar. The `ceil` rule is defensible but must be preregistered. Very short articles should be excluded or flagged because 20% of `<5` scored tokens is one token.

- Raw Min-K% is a valid Shi 2024 anchor, but current literature favors Min-K%++ normalization for this role. Use raw Min-K% only as fallback/sanity, not as the confirmatory `E_CTS` if the plan says Min-K++.

- `compute_mink_pp` lacks `k_pct` validation and finite-value checks. Add the same guards as `compute_mink_pct`.

- Strict `tokenizer_sha` + `raw_token_ids` equality is appropriate for confirmatory PCSG. It may block harmless tokenizer metadata bumps, but that is preferable to silent drift. Waivers should require all pilot token IDs to match, not just matching vocab names.

## Low / Info

- `compute_cts(..., frequency_table=None)` deferral is statistically correct. Do not build a quick seed-corpus table before WS3 just to fill the function; that would create a moving calibration target.

- Do not store `exp(logprob)` as a primary trace field. It is deterministic and risks duplicated sign/orientation confusion. Store derived probabilities only in analysis outputs if needed.

- Chinese tokenization granularity matters for E_CTS. Each tokenizer needs its own frequency table and within-model/tokenizer standardization; GLM should not be directly compared to Qwen on raw token-level CTS.

## Recommendations for the trace contract

Add before cloud execution:

- `top_logprobs`: per position alternatives with token id/text/logprob/rank, or full-logit summaries `minkpp_mu`, `minkpp_sigma`, `realized_rank`.
- `top_logprobs_requested`, `top_logprobs_returned`, and possibly top-K probability mass.
- `quant_scheme`, `dtype`, `vllm_version`, image digest, launch args/run manifest id.
- `cutoff_date` or frozen pair-role metadata available to PCSG derivation.
- Tokenization diagnostics: encoded token count, scored token count, dropped positions, BOS/EOS policy.
- Frequency-table metadata when CTS is computed: tokenizer SHA, smoothing rule, source corpus hash, coverage.

## Pre-registration implications

Lock these in `PREREG_STAGE1` before pilot inference:

- E_CTS primary definition: true full-vocab Min-K%++ or explicitly demoted top-K approximation.
- `K=20%`, `ceil` rounding, minimum token-count eligibility, and score orientation.
- CTS baseline: per-tokenizer unigram table with smoothing and coverage rules; alternatives exploratory only.
- PCSG pair registry, sign convention `late - early`, and full-token mean aggregator.
- Quantization handling: PCSG only within identical quant schemes; E_CTS normalized or stratified by model/quant scheme.
- Trace schema freeze before cloud; no confirmatory metric that requires fields not persisted.

Literature anchors: Shi et al. define Min-K% as selecting lowest-probability tokens and averaging log likelihood, with `k=20` used in experiments and performance improving with text length. Zhang et al. define Min-K%++ as full-vocabulary z-scoring of token logprob, then the same bottom-K aggregation. vLLM docs indicate logprob count controls returned alternatives and full prompt logprobs can be requested at engine level, but response-size cost scales with tokens × returned alternatives. Sources: [Shi 2024 ICLR](https://proceedings.iclr.cc/paper_files/paper/2024/file/e32ad85fa27be4a9868d55703f01323e-Paper-Conference.pdf), [Zhang 2025 ICLR](https://arxiv.org/pdf/2404.02936), [vLLM SamplingParams](https://docs.vllm.ai/en/latest/api/vllm/sampling_params/).
