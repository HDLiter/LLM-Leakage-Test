---
title: Llama-3 / Llama-3.1 Addition as Supplemental Vendor-Cutoff PCSG Anchor (P_logprob-only)
date: 2026-04-29
phase: Phase 7
authority: |
  Adds two Llama models to the R5A fleet as P_logprob-only members;
  introduces split-tier fleet (full-operator vs P_logprob-only);
  adds second confirmatory PCSG pair (`temporal_llama_cross_version`);
  assigns Llama as Path E knee-detector sanity-check anchor;
  enables AWQ-vs-fp16 calibration audit (Qwen2.5-7B bf16 rerun).
related_docs:
  - docs/DECISION_20260427_pcsg_redefinition.md (PCSG cross-version definition + Path E + pcsg_pairs registry)
  - docs/DECISION_20260429_gate_removal.md (strict-majority denominator rule + "fleet expansion alone does not require shortlist amendment" — invoked here)
  - refine-logs/reviews/PCSG_PAIR_HUNT/llama_family_verification_20260429.md (Codex MCP verification of all Llama family claims)
  - refine-logs/reviews/PCSG_PAIR_HUNT/open_source_landscape.md (original 2026-04-26 OSS landscape scan, §3.8 Llama family + §7.1 Recommendation B)
  - refine-logs/reviews/R5A_DESIGN_REVIEW_20260427/SYNTHESIS.md (C2 second PCSG pair as Tier-1 remediation; A4 cutoff provenance attack; A2 Path E knee artifact attack; A3 AWQ-vs-fp16 pooling attack)
status: SIGNED — implementation deferred to the next Tier-0 batch
---

# Decision Memo — Llama Addition (Hybrid D, P_logprob-only)

## 1. Problem statement

The R5A_DESIGN_REVIEW_20260427 SYNTHESIS surfaced three convergent
issues that a single design move can address:

1. **C2 (Construct + Adversarial A1)**: the cross-version Qwen PCSG
   pair conflates "cutoff exposure" with "Qwen2.5 → Qwen3 recipe
   drift". Tier-1 remediation called for a second PCSG pair, ideally
   with vendor-stated cutoffs.
2. **A4 (Adversarial)**: 13/14 fleet cutoffs are
   `community_paraphrase` or `operator_inferred`. Path E "validates"
   our own guesses with our own probe — circular.
3. **A2 (Adversarial)**: Path E knee detection cannot distinguish
   "training cutoff" from "Chinese financial-news regime shift" with
   any current control.
4. **A3 (Adversarial)**: cross-family E_CTS pooling (Qwen-AWQ vs
   GLM-fp16) inherits AWQ-vs-fp16 logprob distortion; the
   `quant_scheme` field labels but does not remove the bias.

A 2026-04-29 Codex MCP verification of the Llama family
(`refine-logs/reviews/PCSG_PAIR_HUNT/llama_family_verification_20260429.md`)
confirmed that **Llama-3-8B-Instruct + Llama-3.1-8B-Instruct** is the
only open-weight pair in the OSS landscape that simultaneously
satisfies: vendor-stated cutoff differential (~9 months: March 2023
vs December 2023), same-tokenizer family (128256 tiktoken core), same
size (8B / 8B), same density (dense autoregressive), same paradigm
(both Instruct).

The verification also revealed three constraints that shape the
addition:

- **No clean same-maintainer AWQ pair**: hugging-quants ships only
  Llama-3.1; Llama-3 community AWQ comes from different uploaders
  (casperhansen / bartowski / study-hjt / solidrust) with
  un-aligned calibration recipes. → Must run bf16, not AWQ.
- **Chinese-finance performance gap**: Llama-3.1-8B trails
  Qwen2.5-7B by 17-21 points on CFinBench, 24-26 points on C-Eval,
  22-28 points on CMMLU. → Llama is not a primary Chinese
  comprehension model and must not be tasked with `P_predict`-based
  estimands at confirmatory weight.
- **Tokenizer special-token map differs slightly**: 128256 core
  shared, but 3.1 reuses high IDs that 3.0 left as reserved
  (`<|finetune_right_pad_id|>`, `<|eom_id|>`, `<|python_tag|>`).
  Ordinary article text is alignable; tool/code-template tokens
  must be excluded.

## 2. Decisions

### 2.1 Add two Llama models to the white-box fleet

| `model_id` | HF repo | Quant | Role |
|---|---|---|---|
| `llama-3-8b-instruct` | `meta-llama/Meta-Llama-3-8B-Instruct` | **bf16** | P_logprob-only |
| `llama-3.1-8b-instruct` | `meta-llama/Meta-Llama-3.1-8B-Instruct` | **bf16** | P_logprob-only |

`cutoff_source = vendor_stated` for both. The vendor_stated fraction
of the fleet rises from 1/14 (Claude only) to 3/16. This is the
direct payload against Adversarial A4.

### 2.2 Introduce split-tier fleet design

The fleet is now **two access tiers** rather than uniform full-operator
coverage:

| Tier | Members | Operators they participate in |
|---|---|---|
| **Full operator coverage** | 10 white-box (5 Qwen2.5 + 4 Qwen3 + 1 GLM) + 4 black-box (DeepSeek + GPT-4.1 + GPT-5.1 + Claude) = **14 models** | P_logprob (white-box only), P_predict (all 14), P_extract (all 14) |
| **P_logprob-only** | 2 white-box (Llama-3-8B-Instruct + Llama-3.1-8B-Instruct) = **2 models** | P_logprob ONLY. Excluded from P_predict, E_CMMD, E_FO, E_NoOp, E_extract. |

Reason: Llama-3.x's Chinese-finance instruction-following is not
adequate for confirmatory P_predict estimands (verification §6).
Including Llama in P_predict would risk dragging eligible coverage
down on the wrong models without compensating signal.

Total fleet: **12 white-box + 4 black-box = 16 models**;
P_predict-eligible fleet remains **14**; P_logprob-eligible fleet is
**12**.

The `ModelConfig` Pydantic schema must allow `p_predict` to be `None`
(unset) to express the P_logprob-only role; this is part of the
RunManifest closure work in the next Tier-0 implementation batch
(SYNTHESIS §5 item 1).

### 2.3 Add second confirmatory PCSG pair: `temporal_llama_cross_version`

The `pcsg_pairs` registry in `config/fleet/r5a_fleet.yaml` adds:

```yaml
- id: temporal_llama_cross_version
  role: temporal
  early: llama-3-8b-instruct       # vendor-stated cutoff 2023-03
  late:  llama-3.1-8b-instruct     # vendor-stated cutoff 2023-12
  tokenizer_compat: llama3_class
  max_token_id_inclusive: 128255   # excludes 3.1's added high-ID special tokens (3.0 reserved them)
```

R5A confirmatory PCSG now has **two temporal pairs**:

- `temporal_qwen_cross_version` (Qwen2.5-7B vs Qwen3-8B) — operator-asserted cutoff
- `temporal_llama_cross_version` (Llama-3-8B vs Llama-3.1-8B) — vendor-stated cutoff

§8.2 mixed model includes a fixed effect for `pair_id` to control for
between-pair offsets (different vendors, different tokenizers). The
primary cutoff coefficient is estimated **across both pairs**, gaining
~1.4× SE improvement over the single-pair design (Statistical lens §5
SE-inflation calibration applied in reverse). Per-pair coefficients
are reported as supplementary breakdown.

This directly addresses Construct C2 / Adversarial A1: a same-vendor
recipe-drift critique cannot apply to a Meta vendor pair, so any PCSG
signal that replicates across both Qwen and Llama pairs cannot be
attributed to vendor-recipe drift.

### 2.4 Path E knee-detector sanity-check role

Llama-3-8B and Llama-3.1-8B are added to the Path E month-stratified
probe (60 articles/month × 36 months × 2 models = ~4,320 extra
inferences ≈ 1-2 hr GPU on RTX PRO 6000).

Two sanity checks become possible:

- **Single-point calibration**: `cutoff_observed(llama-3-8b)` should
  fall near 2023-03 (the vendor-stated date), modulo Chinese-coverage
  smear. Deviation quantifies the knee detector's absolute bias.
- **Differential calibration**: `cutoff_observed(llama-3.1-8b) − cutoff_observed(llama-3-8b)` should be ~9 months. This is the
  load-bearing test for PCSG, because PCSG depends on the algorithm's
  ability to detect cutoff differentials, not absolute cutoffs.

This dual sanity check converts Adversarial A4 (cutoff circularity)
into a quantified-uncertainty statement the paper can defensibly
publish: "Path E recovers cutoff differential within ±X months on the
Llama vendor-stated case; for community-paraphrased cutoffs (Qwen),
`cutoff_observed` is reported as empirical horizon, not vendor cutoff
recovery."

It also provides the strongest available rebuttal to Adversarial A2:
if the knee detector finds the Llama-3 / 3.1 knees ~9 months apart
on the same Chinese news corpus, that 9-month gap cannot be explained
by Chinese news regime shifts (which are common to both models) and
must reflect actual training data exposure differential.

### 2.5 AWQ-vs-fp16 calibration audit (Adversarial A3 closure)

Llama is bf16. Adding it to the fleet requires a bf16 backend on the
cloud instance regardless. This makes the AWQ-vs-fp16 audit (which
SYNTHESIS Tier-1 #13 had recommended as a separate effort) cheap to
fold into the same WS1 cloud session:

- Run **Qwen2.5-7B in bf16** on the full pilot manifest (430 cases)
  using the same bf16 backend already loaded for Llama. Estimated +3
  hr GPU = +24 RMB.
- Output: `data/pilot/analysis/quant_calibration_qwen2.5_7b.parquet`
  containing per-article `Min-K%++(AWQ)` and `Min-K%++(bf16)`.
- Compute `delta_quant = Min-K%++(AWQ) − Min-K%++(bf16)` per article;
  publish summary statistics.
- If `|mean(delta_quant)| < 0.05 nats`: report as caveat only; no
  correction applied to Qwen-AWQ Min-K% scores.
- If `|mean(delta_quant)| ≥ 0.05 nats`: subtract `delta_quant` from
  Qwen-AWQ Min-K% scores before pooling with GLM-fp16 / Llama-bf16
  in fleet-level E_CTS.

Note: bf16 vs fp16 differences in logprob computation (~1e-3 nats) are
negligible compared to the AWQ-vs-fp16 effect size (~1e-2 to 1e-1
nats). Treating bf16 as the fp16 reference for calibration purposes is
sound; using bf16 backend (already required for Llama) avoids spinning
up a separate fp16 backend.

### 2.6 No frozen-shortlist amendment required

Per `docs/DECISION_20260429_gate_removal.md` §2.6:
> Fleet expansions (e.g., adding Llama-3 white-box pair) automatically
> re-derive K from the new N at run time; **fleet expansion alone no
> longer triggers a frozen-shortlist amendment** as long as the
> formulas are honored.

This memo is the authoritative record of the addition. The frozen
shortlist (`R5A_FROZEN_SHORTLIST.md`) is not edited.

The strict-majority quality-gate denominators rescale automatically:

- Behavioral E_FO / E_NoOp gate (over P_predict eligible N): N = 14 →
  `⌊14/2⌋+1 = 8/14`. Llama is excluded from P_predict, so N stays 14.
- WS6 mechanistic trigger (over white-box N): N = 12 →
  `⌊12/2⌋+1 = 7/12`. Was 6/10 before Llama; now 7/12 because Llama
  contributes hidden states. (See §3.4 below.)
- E_extract reserve promotion (over P_predict eligible N): unchanged
  at 5/14 main-text and 8/14 confirmatory.

## 3. Effects downstream

### 3.1 Pre-registration

`PREREG_STAGE1` (still pending pilot) must:

- Reference both `pcsg_pairs.temporal_qwen_cross_version` and
  `pcsg_pairs.temporal_llama_cross_version` as confirmatory.
- State the §8.2 mixed-model includes `pair_id` fixed effect; primary
  cutoff coefficient is across-pair.
- Reference Llama as Path E knee-detector calibration anchor; state
  the deviation-tolerance band for Llama-3 single-point and Llama-3.1
  / Llama-3 differential checks.
- State `quant_calibration_qwen2.5_7b.parquet` is published alongside
  pilot results; describe the conditional correction rule.
- State Llama is excluded from `P_predict` and therefore from E_CMMD,
  E_FO, E_NoOp; vendor-mix discussion in paper limitations notes the
  asymmetry.

### 3.2 RunManifest schema

The next Tier-0 implementation batch (SYNTHESIS §5 item 1) extends
`RunManifest` to support split-tier fleet:

- `fleet_white_box: list[str]` — currently 12 (was 10)
- `fleet_p_predict_eligible: list[str]` — 14 (Llama excluded)
- `pcsg_pair_registry_hash` — covers both temporal pairs

`ModelConfig.p_predict` becomes `Optional[PPredictConfig]`; `None`
encodes "this model does not participate in P_predict".

### 3.3 WS1 cloud execution plan

`plans/ws1-cloud-execution.md` Stage 2 per-model loop adds
Llama-3-8B-Instruct + Llama-3.1-8B-Instruct between
`qwen3-32b` and `glm-4-9b`. Stage 2.5 Path E adds Llama probes.
Stage 2.7 hidden-state extraction extends to 12 white-box (was 10)
unless WS6 explicitly opts to exclude Llama for cross-vendor
mechanism comparison parity (decision deferred to WS6 design).

A new Stage 2.8 — **AWQ-vs-fp16 calibration audit** — runs
Qwen2.5-7B in bf16 on the 430 pilot cases. Estimated +3 hr GPU =
+24 RMB.

Budget cap: $35 → **$45** to accommodate Llama (2 models × 1.5 hr +
Path E 1-2 hr + bf16 audit 3 hr = ~8 hr extra ≈ 64 RMB ≈ $9).

### 3.4 WS6 hidden-state extraction extends to Llama

Per Q-Llama-4 user decision (2026-04-29), WS6 30-case subset extracts
hidden states for 12 white-box models including Llama. Storage budget:
30 cases × 2 Llama models × 32 layers × 4096 hidden_dim × bf16 ≈ 4 GB
extra; total Stage 2.7 storage 30-65 GB (within 100 GB persistent disk).

This enables cross-vendor mechanism comparison: do override / no-override
decisions in Llama-3 vs Llama-3.1 happen at the same relative-layer
positions as in Qwen2.5 vs Qwen3? A positive answer strengthens the
mechanism story's generality; a negative answer becomes its own
finding (vendor-specific override pathways).

### 3.5 Operational pre-flight

Meta repos are gated. Before WS1 cloud spend:

- User must accept `meta-llama/Meta-Llama-3-8B-Instruct` license at
  `https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct`.
- User must accept `meta-llama/Meta-Llama-3.1-8B-Instruct` license at
  `https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct`.
- HF fine-grained read-only token must include access to gated Meta
  repos (verified via `huggingface-cli whoami` after acceptance).
- `hf-mirror.com` does NOT bypass Meta gating (verified 2026-04-29);
  authenticated `huggingface-cli download` is required.

This is tracked as a PENDING.md operational item alongside the
existing CLS post-cutoff extraction reminder.

### 3.6 Documents updated in the implementation batch (NOT in this commit)

This commit is **decision-only**. The implementation batch (next
session) will update:

- `config/fleet/r5a_fleet.yaml` — 2 Llama entries + new pcsg_pairs entry
- `src/r5a/contracts.py` — ModelConfig.p_predict optional + RunManifest
  split-tier fields
- `src/r5a/fleet.py` + `tests/r5a/test_fleet_config.py` — pcsg_pairs
  validator + P_logprob-only fleet member support
- `plans/phase7-pilot-implementation.md` §1 / §5.2 / §10.4 / §11.2 /
  §13 — fleet count sweep, P_predict tier callout
- `plans/ws1-cloud-execution.md` — Stage 2 Llama insertion, Stage 2.5
  Llama probes, Stage 2.7 Llama hidden states, Stage 2.8 calibration
  audit, budget cap $35 → $45
- `PENDING.md` — HF Meta license click-through pre-flight item

## 4. What this memo does NOT change

- **Westfall-Young multiplicity** — still over 20 confirmatory
  coefficients (5 estimands × 4 factors). Adding a second PCSG pair
  does NOT increase family size; it improves identification of
  existing E_PCSG coefficients.
- **Strict-majority denominator rule** — unchanged; auto-rescales.
- **Gate removal** — unchanged; E_FO / E_NoOp remain unconditional
  confirmatory; Llama just isn't in their fleet.
- **PCSG common-vocab restriction principle** — same approach as Qwen
  pair; Llama gets `max_token_id_inclusive: 128255` to exclude 3.1's
  added high-ID special tokens.
- **English follow-up scope** — Llama-3.2 1B / 3B + Llama-3.1-70B
  capacity curve and any Llama-4 work remain reserved for a later
  English-version benchmark, NOT folded into Phase 7 / Phase 8.

## 5. Sign-off

This memo is committed as a decision-only record alongside no
implementation changes. The next Tier-0 implementation batch
(SYNTHESIS §5 items 1-6 + 10) absorbs the Llama integration into its
scope; on completion of that batch the implementation will be
verified end-to-end and the cloud spend gate (no `<TBD>` in fleet
YAML; RunManifest contract closed; Path E joiner runnable; pcsg_pairs
validator green; Meta license accepted) will close.
