---
title: PCSG Redefinition + Fleet Expansion + Path-E Cutoff Probe + WS6 Conditional
date: 2026-04-27
phase: Phase 7
authority: supersedes R5A_FROZEN_SHORTLIST.md §1 PCSG definition; extends fleet roster
related_docs:
  - refine-logs/reviews/WS1_CODE_REVIEW/stats_lens.md (origin of M1 issue)
  - refine-logs/reviews/PCSG_PAIR_HUNT/open_source_landscape.md (fleet candidate scan)
  - plans/ws1-cloud-execution.md
  - plans/phase7-pilot-implementation.md
status: SIGNED — implementation in progress
---

# Decision Memo — PCSG Redefinition, Fleet Expansion, Path-E + WS6

## 1. Problem statement (M1)

The Stats lens of the WS0+WS1 code review surfaced a methodology defect:
**within-pair cutoff is identical** for both R5A `tokenizer-matched temporal pairs` —
`(qwen2.5-7b, qwen2.5-14b)` both at `2023-10-31`, and
`(qwen3-8b, qwen3-14b)` both at `2025-01-31`.

The plan §8.1A model coefficient `β₁ · cutoff_pair_exposure` is therefore
identified only at the article level (article date relative to the
shared cutoff), not at the model level. The literal "late-vs-early
model" reading from R5A_FROZEN_SHORTLIST §1 is unsupported by the
fleet's actual cutoff structure.

A subsequent open-source landscape scan (see related_docs above)
established that:

- **No vendor in the OSS ecosystem provides a within-family pair that
  is simultaneously (i) same-tokenizer, (ii) same-density, (iii) same-paradigm,
  (iv) different-cutoff, and (v) reasonably-Chinese-capable** — except
  Llama-3-8B vs Llama-3.1-8B, which fails on (v) and (iv-Chinese-relevance).
- **Qwen2.5 and Qwen3 share the `Qwen2Tokenizer` class** with byte-identical
  vocab IDs `0..151664`. Qwen3 adds 4 extension tokens at IDs
  `151665..151668` (`<tool_response>`, `</tool_response>`, `<think>`,
  `</think>`).
- **Most "cutoff dates" we previously took as ground truth are
  operator-asserted, not vendor-stated.** Including all the Qwen entries
  in our existing fleet.

## 2. Decisions

### 2.1 PCSG redefinition (replaces R5A_FROZEN_SHORTLIST §1 line for E_PCSG)

**E_PCSG (primary, confirmatory)** is now computed on the **temporal
pair** `(qwen2.5-7B, qwen3-8B)`:

- Score: `mean(logprob(qwen3-8B) - logprob(qwen2.5-7B))` over matched tokens
- Eligibility: every probe article's `raw_token_ids` must satisfy
  `max(token_id) <= 151664` so that both models' tokenizations align
  byte-for-byte. Articles tokenizing to any ID in `[151665, 151668]`
  are excluded from E_PCSG (but remain eligible for E_CTS, E_CMMD,
  E_FO, E_NoOp).
- Tokenizer compat label: `qwen2_class`. Backend MUST verify both
  members report this label before computing PCSG.

**E_PCSG_capacity_curve (exploratory, new)** is computed on
**capacity pairs** with cutoff held fixed:

- Qwen2.5 series: `[1.5B, 3B, 7B, 14B, 32B]`
- Qwen3 series: `[4B, 8B, 14B, 32B]`
- Score: per-article logprob, regressed on `log₂(params)`
- Interpretation: capacity-mediated memorization (Carlini 2021/2022
  scaling). Cutoff_exposure factor stratifies the regression.

The two analyses use **the same `LogProbTrace` artifacts** — no extra
cloud GPU spend.

### 2.2 Fleet expansion (5 → 10 white-box)

| Family | Sizes | Quant | Status |
|---|---|---|---|
| Qwen2.5 | 1.5B, 3B, 7B, 14B, 32B | AWQ-INT4 | all 5 official Alibaba AWQ; 3 new entries |
| Qwen3 | 4B, 8B, 14B, 32B | AWQ-INT4 | all 4 official Alibaba AWQ; 2 new entries |
| GLM | GLM-4-9B | fp16 | unchanged (no official AWQ) |
| Black-box | DeepSeek/GPT-4.1/GPT-5.1/Claude | n/a | unchanged |

**Total: 10 white-box + 4 black-box = 14 models.**

**Why not Qwen3-1.7B**: Alibaba did not publish an official AWQ for
sizes < 4B in the Qwen3 family. Including 1.7B would force fp16,
mixing precision within-family and confounding the capacity curve with
quantization regime.

**Why not Qwen2.5-72B**: A6000 / RTX PRO 6000 96GB VRAM is sufficient
to load 72B AWQ (~40GB), but pilot ROI is low. Add only if the
4-point Qwen2.5 curve shows curvature that warrants extension. Not
in default pilot.

### 2.3 Cutoff-source provenance

Every fleet entry now carries `cutoff_source ∈ {vendor_stated,
community_paraphrase, operator_inferred}` per the open-source
landscape scan. Today's status:

| Model | cutoff_date | source |
|---|---|---|
| Qwen2.5-* | 2023-10-31 | community_paraphrase (HaoooWang) |
| Qwen3-* | 2025-01-31 | operator_inferred |
| GLM-4-9B | 2024-06-30 | operator_inferred |
| DeepSeek-V3-0324 | 2024-07-31 | community_paraphrase |
| GPT-4.1 | 2024-06-30 | community_paraphrase |
| GPT-5.1 | 2024-09-30 | operator_inferred |
| Claude Sonnet 4.6 | 2025-08-31 | vendor_stated |

**No confirmatory analysis may rely on a `community_paraphrase` or
`operator_inferred` cutoff without a corroborating empirical probe.**
Hence Path E.

### 2.4 Path E — empirical cutoff probe

Build a temporally-stratified dataset from CLS source corpus
(`D:\GitRepos\Thales\datasets\cls_telegraph_raw`):

- 60 articles per month × 24 months from 2023-Q1 to 2025-Q4
- Total ~1,440 articles
- For each article, run **P_logprob** on all 10 white-box models +
  **P_extract** masked-span completion (we already have this operator
  in the legacy pipeline; lift the prompt verbatim, score on hit rate)
- Output: month-stratified Min-K% (per model) and P_extract hit rate
  (per model)

The "knee" of the month-vs-score curve gives an empirical
`cutoff_observed` per model. The run manifest stores both
`cutoff_date_yaml` (declared) and `cutoff_observed` (empirical) for
every white-box model. The `cutoff_exposure` factor in the §8.2
mixed model uses `cutoff_observed` as the primary covariate, with
`cutoff_date_yaml` as a robustness check.

Path E is **technique reuse**, not technique novelty: we use
Min-K% Prob (Shi et al. ICLR 2024) and the temporal-stratification
protocol of Roberts et al. (NAACL Findings 2023). The contribution
is application to Chinese financial news with minute-resolution
timestamps.

**Implementation**:
- `scripts/build_cutoff_probe_set.py` — sample 1,440 articles
- `scripts/run_cutoff_probe.py` — call P_logprob and P_extract
- `data/pilot/cutoff_probe/month_stratified_scores.parquet` — output
- `src/r5a/analysis/cutoff_probe.py` — knee detection on the curve

Path E runs alongside the main WS1 pilot on the same cloud instance;
estimated +1.5h GPU time, +1 day engineering.

### 2.5 WS6 conditional — mechanistic memorization localization

Adapted from Wang et al. 2025 "When Truth Is Overridden" (arxiv
2508.02087). The sycophancy paper's methodology — Decision Score
via logit-lens, layer-wise KL divergence, activation patching — maps
directly to our `C_FO` setup: when the article contains a fake
outcome that contradicts the model's memorized real outcome, where
in the network does the override happen?

**Conditional trigger**: WS6 is opened only if behavioral E_FO
(plan §1 confirmatory) shows resistance signal in pilot — concretely,
`mean |delta| > 0` on `>= 5/9` models per the frozen quality gate
(plan §13 item 6). If not, mechanism analysis is moot.

**Pre-pilot prep (must do now to avoid GPU rerun)**:
- `src/r5a/backends/offline_hf.py` adds optional `return_hidden_states=True`
- `src/r5a/contracts.py` `LogProbTrace` adds `hidden_states_uri: str | None`
  pointing to a `.safetensors` file containing per-layer hidden states
- During WS1 cloud pilot, **subsample 30 articles** for hidden-state
  extraction across all 10 white-box models. The other 70 articles
  remain logprob-only (~25× cheaper in disk).

**Predicted layer windows** (scaled from Wang et al. results):

| Model | Total layers | DS shift (mid-late) | KL peak (final) |
|---|---|---|---|
| Qwen2.5-1.5B | 28 | 19-22 | 26-28 |
| Qwen2.5-3B | 36 | 24-28 | 32-36 |
| Qwen2.5-7B | 28 | 19-22 | 26-28 |
| Qwen2.5-14B | 48 | 32-38 | 44-48 |
| Qwen2.5-32B | 64 | 43-50 | 58-64 |
| Qwen3-4B | 36 | 24-28 | 32-36 |
| Qwen3-8B | 36 | 24-28 | 32-36 |
| Qwen3-14B | 40 | 27-32 | 36-40 |
| Qwen3-32B | 64 | 43-50 | 58-64 |
| GLM-4-9B | 40 | 27-32 | 36-40 |

**Pre-registered prediction** (PREREG_STAGE2 if WS6 fires): the
"memorization override" of fake outcome occurs in the final 25% of
layers in each model, with effect size scaling with parameter count
(Carlini-Wang composite hypothesis).

### 2.6 Tokenizer naming reconciliation

Plan §14.2 example shows Qwen entries with `tokenizer_family: qwen`
including Qwen3. Our fleet YAML retains `qwen` for Qwen2.5 and
`qwen3` for Qwen3 because the **vocabularies differ** (4 extension
tokens). The PCSG pair compatibility is now validated via an
explicit `tokenizer_compat: qwen2_class` label, not via
`tokenizer_family` equality. Plan §14.2 needs updating to match
this YAML; see plans/phase7-pilot-implementation.md update task.

## 3. What this changes downstream

### 3.1 Pre-registration

`PREREG_STAGE1` (still pending pilot) must:

- Define E_PCSG on the temporal pair, with `max_token_id_inclusive: 151664` rule
- List E_PCSG_capacity_curve as exploratory (one figure, no confirmatory alpha)
- Reference `cutoff_observed` (Path E output) as the primary covariate
- Reference WS6 layer predictions as exploratory (only fires conditional on
  behavioral E_FO)

### 3.2 Run manifest

`RunManifest` must add:

- `cutoff_observed: dict[str, date]` — per-model, from Path E
- `quant_scheme: dict[str, str]` — per-model, from fleet YAML
- `pcsg_pair_registry_hash: str` — hash of the `pcsg_pairs` block in fleet YAML

### 3.3 Plan §13 exit gate

Item 3 ("`P_logprob` succeeds on all 5 white-box models") changes to
"**all 10 white-box models**, with `<1%` un-recovered trace failures
and Path E `cutoff_observed` published".

### 3.4 PENDING.md additions

- Resolve OPEN: PCSG temporal-pair design (this memo)
- Add: WS1 fleet provenance pinning (10 white-box × tokenizer_sha + hf_commit_sha + Docker digest)
- Add: WS1 trace contract closure (top_logprobs, quant_scheme, hidden_states_uri)
- Add: Path E data sourcing (CLS 1M corpus access)
- Add: WS6 mechanistic conditional trigger evaluation (post-pilot)

## 4. Out of scope for this memo

- Phase 8 main run sample size (still 2,560)
- C_FO and C_NoOp generation rules (WS3)
- Audit staffing (PENDING OPEN 4)
- WS0.5 Thales factor pipeline (PENDING)
- 72B extreme-right capacity-curve point (deferred until 4-point curve shows curvature)

## 5. Sign-off

This memo is committed alongside the fleet YAML expansion, the
R5A_FROZEN_SHORTLIST §1/§3/§7 update, the WS1 cloud-execution plan
update, and the master Phase 7 plan update. Together they constitute
the methodology delta for the WS1 cloud run.

After commit, the next blocker is **the 6 P0-Critical findings from
the WS0+WS1 code review** (see `refine-logs/reviews/WS1_CODE_REVIEW/`)
which must be resolved before any cloud spend.
