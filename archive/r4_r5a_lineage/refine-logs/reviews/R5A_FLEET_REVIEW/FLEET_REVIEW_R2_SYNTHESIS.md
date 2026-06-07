---
title: R5A Fleet Review Round 2 — Synthesis
stage: R5A Round 3b close
date: 2026-04-15
inputs: quant_lens_r2.md, nlp_lens_r2.md, stats_lens_r2.md, editor_lens_r2.md
codex_threads:
  quant:  019d944c-8500-7332-8037-b78e2474a627
  nlp:    019d944c-89e0-7813-9aa0-68cfd4fb62fd
  stats:  019d944c-c761-7ce1-8480-a26d2f4dc7ec
  editor: 019d944c-f972-7a00-842d-531f31f60ff4
---

> **Status (2026-04-16, post-R5A-freeze)**: Authoritative for the frozen 9-model core fleet. The "GPT-5.4 optional 10th" discussion is historical pre-freeze context; the freeze locks the 9-model core. Operator policy (per `MEASUREMENT_FRAMEWORK.md`): `P_logprob` requires thinking OFF on all 5 white-box models; `P_predict` and `P_extract` use each model's default deployed mode. References to "logprob detectors" and "behavioral detectors" map to `P_logprob` and `P_predict`/`P_extract` operators respectively.

# R5A Fleet Review Round 2 — Synthesis

Round 2 incorporated 4 new user-proposed design principles (thinking mode fleet-wide, same-cutoff falsification pairs, architecture coverage, multi-tier size matching). Consensus is high; the main remaining tension is GPT version choice.

---

## 1. Consensus on the 4 new principles

### Principle A — Thinking mode: Option (c) with targeted crossover (4/4 converge)

All 4 lenses converge on a hybrid of options (c) and (e):

- **Logprob detectors (PCSG, Min-K++)**: thinking OFF across the fleet. Thinking mode changes token probability distributions in ways that confound tail-surprise scores.
- **Behavioral detectors (CMMD, SR/FO, NoOp, EAD, extraction, ADG)**: use each model's **default deployed mode** (thinking ON where that is the standard). This reflects real-world usage and may reveal memorization patterns that non-thinking mode suppresses.
- **Targeted ON/OFF crossover**: Run on a 400-800 case subset for 3-4 models with clean toggles (Qwen3-8B or Qwen3-14B, GPT-5.x, Claude Sonnet 4.6). Reported in appendix as sensitivity analysis.
- **Fleet-wide doubling rejected** (Stats): Doubling every model to ON+OFF halves per-mode N and worsens minimum detectable effect by ~√2 with no gain for architecture/tier main effects.

### Principle B — Same-cutoff falsification pairs: GPT-4.1 ↔ GLM-4-9B (3/4 agree)

Strong consensus on one primary falsification pair:

- **GLM-4-9B-0414** (cutoff 2024-06-30) ↔ **GPT-4.1** (cutoff ~2024-06)
- Different architecture families (GLM dense vs OpenAI), similar cutoff, different size but both "medium-small"
- Any CMMD/PCSG disagreement between these two is architecture noise, not cutoff signal — this is the falsification baseline

Quant additionally proposes a late-period falsification pair: **GPT-5.4** (cutoff ~2025-08) ↔ **Claude Sonnet 4.6** (cutoff ~2025-08). Valid but requires GPT-5.4 instead of GPT-5.1 — see §2 tension.

### Principle C — Architecture coverage: 5 families confirmed

All lenses agree the fleet should cover at minimum:

| Family | Representative(s) | Architecture type |
|---|---|---|
| Qwen | Qwen2.5-7B/14B, Qwen3-8B/14B | Dense, Chinese-first |
| GLM | GLM-4-9B-0414 | Dense, Chinese-bilingual |
| DeepSeek | DeepSeek-V3-0324 | MoE, Chinese-first |
| OpenAI | GPT-4.1 / GPT-5.x | Unknown, English-first |
| Anthropic | Claude Sonnet 4.6 | Unknown, English-first |

NLP notes an interesting additional option: **Qwen3-32B (dense) vs Qwen3-30B-A3B (MoE)** as an exact-tokenizer architecture test (dense vs MoE within the same model family). This is an appendix-level upgrade, not core fleet.

### Principle D — Two size tiers with internal matching (4/4 agree)

All lenses endorse a 2-tier white-box design:

| Tier | Models | Cutoff span | Internal pair purpose |
|---|---|---|---|
| **Small (~7-9B)** | Qwen2.5-7B, Qwen3-8B, GLM-4-9B | 2023-10 → 2025-01 | Primary PCSG temporal pair + cross-family sensitivity |
| **Medium (~14B)** | Qwen2.5-14B, Qwen3-14B | 2023-10 → 2025-01 | Secondary PCSG temporal pair + size falsification vs small tier |

Cross-tier comparison: If temporal effects appear in both small AND medium tiers with consistent direction, the finding is robust to model scale. If they appear only in one tier, scale is a boundary condition — itself a finding worth reporting.

**Size falsification control** (Stats): Qwen2.5-7B vs Qwen2.5-14B (same family, same cutoff, different size). Any PCSG gap here is pure capability confound, not cutoff signal.

### Qwen3.5 — Do NOT include (NLP definitive)

NLP evaluated Qwen3.5 in detail and recommends against inclusion:
- No official published cutoff date
- Different tokenizer artifact from Qwen3 (despite same tokenizer class)
- Multimodal hybrid architecture
- Thinking-on-by-default with different control semantics
- Available as shadow evaluation model only, not in confirmatory fleet

### DeepSeek-V2.5 — DROP (Quant + Stats implicit)

Replaced by GPT-4.1 which fills the same ~mid-2024 cutoff slot with more utility (same-cutoff falsification partner for GLM-4-9B + vendor diversity). DeepSeek is still represented by DeepSeek-V3.

---

## 2. Remaining tension — GPT version

| Lens | Primary GPT | Secondary GPT | Rationale |
|---|---|---|---|
| **NLP + Editor** | GPT-5.1 (cutoff 2024-09-30) | GPT-4.1 (cutoff ~2024-06) | GPT-5.1 fills temporal gap; GPT-4.1 for falsification |
| **Quant** | GPT-5.4 (cutoff 2025-08-31) | GPT-4.1 optional | GPT-5.4 extends fleet span; same-cutoff pair with Claude 4.6 |
| **Stats** | GPT-4.1 (cutoff ~2024-06) | GPT-5.1 (cutoff 2024-09-30) | GPT-4.1 for falsification is the priority; GPT-5.1 adds temporal coverage |

**Analysis**: GPT-4.1 is consensus as the **falsification model** (3/4 lenses). The disagreement is whether the second OpenAI slot goes to GPT-5.1 (temporal gap) or GPT-5.4 (SOTA + late-period falsification with Claude).

**Orchestrator recommendation**: Include **both GPT-4.1 AND GPT-5.1** in the 9-model core:
- GPT-4.1 serves the falsification role (same-cutoff pair with GLM-4-9B)
- GPT-5.1 fills the temporal gap (2024-09-30, between DeepSeek-V3's 2024-07 and Qwen3's 2025-01)
- GPT-5.4 as optional 10th model if user wants the late-period falsification pair with Claude

---

## 3. Proposed revised fleet

### Core fleet (9 models)

| # | Model | Cutoff | Access | Params | Tier | Family | Design role |
|---|---|---|---|---|---|---|---|
| 1 | Qwen2.5-7B-Instruct | 2023-10 | white-box | 7B | small | Qwen | Temporal pair A (early); size falsification anchor |
| 2 | Qwen2.5-14B-Instruct | 2023-10 | white-box | 14B | medium | Qwen | Temporal pair B (early); size falsification vs #1 |
| 3 | GLM-4-9B-0414 | 2024-06-30 | white-box | 9B | small | GLM | Cross-family sensitivity; falsification pair with #7 |
| 4 | DeepSeek-V3-0324 | 2024-07 | black-box | MoE | large | DeepSeek | MoE architecture coverage |
| 5 | **GPT-4.1** | **~2024-06** | **black-box** | unknown | large | **OpenAI** | **Same-cutoff falsification pair with #3** |
| 6 | **GPT-5.1-2025-11-13** | **2024-09-30** | **black-box** | unknown | large | **OpenAI** | **Temporal gap filler** |
| 7 | Qwen3-8B (thinking varies) | 2025-01 | white-box | 8B | small | Qwen | Temporal pair A (late) |
| 8 | Qwen3-14B (thinking varies) | 2025-01 | white-box | 14B | medium | Qwen | Temporal pair B (late) |
| 9 | Claude Sonnet 4.6 | ~2025-08 | black-box | unknown | large | Anthropic | Latest cutoff anchor |

### Optional 10th model

| 10 | GPT-5.4-2026-03-05 | ~2025-08 | black-box | unknown | large | OpenAI | Late-period falsification pair with Claude; extends SOTA |

### Design pairing table

| Pair type | Model A | Model B | What it tests |
|---|---|---|---|
| **Temporal pair A (small)** | Qwen2.5-7B (2023-10) | Qwen3-8B (2025-01) | Cutoff effect at ~8B scale, same tokenizer family |
| **Temporal pair B (medium)** | Qwen2.5-14B (2023-10) | Qwen3-14B (2025-01) | Cutoff effect at ~14B scale, same tokenizer family |
| **Same-cutoff falsification (mid)** | GLM-4-9B (2024-06) | GPT-4.1 (~2024-06) | Architecture noise baseline at mid-2024 cutoff |
| **Same-cutoff falsification (late)** | Claude 4.6 (~2025-08) | GPT-5.4 (~2025-08) | Architecture noise at late-2025 (optional, requires 10th model) |
| **Size falsification** | Qwen2.5-7B (2023-10) | Qwen2.5-14B (2023-10) | Capability confound at fixed cutoff |
| **Cross-tier temporal** | Small tier (avg) | Medium tier (avg) | Scale × memorization interaction |

### Fleet properties

- **Temporal span**: 2023-10 → ~2025-08 (22 months)
- **Architecture families**: 5 (Qwen, GLM, DeepSeek, OpenAI, Anthropic)
- **Size tiers**: 2 white-box (small ~7-9B, medium ~14B) + hosted (large, size unknown)
- **White-box models**: 5 (all bf16 on cloud GPU)
- **Black-box models**: 4
- **Thinking mode**: OFF for logprob detectors; default deployed mode for behavioral detectors; ON/OFF crossover on subset for appendix

### Cost estimate

| Configuration | Per-detector-run cost | Total at K=8 detectors |
|---|---|---|
| 9-model core | ~$45-65 | ~$360-520 |
| 10-model with GPT-5.4 | ~$55-75 | ~$440-600 |
| + thinking crossover subset | +~$30-50 | +~$30-50 |
| Cloud GPU (white-box bf16) | ~$25-40 flat | ~$25-40 flat |
| **Grand total (9-model)** | | **~$415-610** |
| **Grand total (10-model)** | | **~$495-690** |

---

## 4. Fleet design principles (consolidated from Round 1 + Round 2)

1. **Same-tokenizer temporal pairs for PCSG**: Primary temporal contrast within same tokenizer family (Qwen2.5 ↔ Qwen3).
2. **Same-cutoff different-architecture pairs for falsification**: At least one pair where cutoffs match but families differ (GLM ↔ GPT-4.1). Disagreement in this pair = architecture noise, not memorization.
3. **Multiple size tiers with internal matching**: At least 2 tiers (small ~8B, medium ~14B) with matched temporal pairs in each. Cross-tier comparison tests whether memorization detection is scale-dependent.
4. **Uniform precision**: All white-box models bf16/fp16 on cloud GPU. No quantization for confirmatory detectors.
5. **Thinking mode split by detector type**: Logprob detectors (PCSG, Min-K++) use thinking OFF. Behavioral detectors use default deployed mode. Targeted ON/OFF crossover on subset for appendix.
6. **Pin to dated checkpoints**: Every model has a version-locked checkpoint before pre-commit. OpenRouter provider routing locked.
7. **5-family architecture coverage**: Qwen + GLM + DeepSeek + OpenAI + Anthropic minimum.
8. **Paper presentation**: Main text organized by contrast blocks (temporal pair, falsification pair, cross-tier), not by individual model. Full per-model results in supplement.

---

## 5. Verification checklist before fleet freeze

- [ ] GPT-4.1 cutoff date confirmed (~2024-06 is estimated)
- [ ] GPT-5.1 checkpoint ID and cutoff confirmed (2024-09-30 from NLP/Editor)
- [ ] Claude Sonnet 4.6 cutoff date confirmed (~2025-08 estimated)
- [ ] Qwen2.5-14B-Instruct HuggingFace commit SHA locked
- [ ] Qwen3-8B HuggingFace commit SHA locked
- [ ] Qwen3-14B HuggingFace commit SHA locked
- [ ] GLM-4-9B-0414 commit SHA locked
- [ ] Cloud GPU provider selected (Vast.ai / Modal / RunPod)
- [ ] Thinking mode toggle syntax verified for each model
- [ ] If 10-model: GPT-5.4 checkpoint and cutoff confirmed
