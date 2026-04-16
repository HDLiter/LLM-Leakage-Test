---
title: R5A Fleet Review — Orchestrator synthesis
stage: R5A Round 3 close
date: 2026-04-15
inputs: quant_lens.md, nlp_lens.md, stats_lens.md, editor_lens.md
codex_threads:
  quant:  019d9416-c79e-78c3-9018-d8ee113d124b
  nlp:    019d9416-f410-7e23-939d-fca70d6b3e93
  stats:  019d9417-0c05-7780-bd35-PENDING
  editor: 019d9417-4472-72c0-8693-d0e2a1f53659
---

# R5A Fleet Review — Synthesis

4 Codex (xhigh) lens passes on 5 fleet concerns. 3 concerns reached full consensus; 2 have genuine tensions requiring user input.

---

## Unanimous consensus (3 of 5 concerns)

### Concern 2 — Thinking mode: DISABLE for confirmatory runs

**4/4 unanimous**: Thinking mode (Qwen3's enable_thinking, GPT extended reasoning, Claude extended thinking) must be **disabled** across the entire fleet for all confirmatory detector runs. Thinking ON vs OFF is a pre-registered sensitivity analysis only, run on a small subset. Rationale: thinking mode changes the inference regime fundamentally — more deliberate reasoning, potentially less memorization-based shortcutting — and this confound is not separable from cutoff/capability effects without a prohibitively large design.

### Concern 4 — SOTA: Upgrade Claude to Sonnet 4.6, don't chase 4.7

**4/4 unanimous**: Replace `claude-sonnet-4-5-20250929` with **Claude Sonnet 4.6** (already released, has a pinnable checkpoint). Do NOT wait for the rumored Claude 4.7 — it has no confirmed cutoff date, no pinnable checkpoint, and chasing unreleased models risks delaying the entire fleet freeze.

Principle: **"Latest official model at freeze date"** — track what is released and documented, not what is rumored.

### Concern 5 — Quantization: RENT CLOUD GPU, no mixed precision

**4/4 unanimous**: Mixed fp16 vs Q4 quantization across the white-box fleet is **unacceptable** for confirmatory logprob-based detectors (Min-K++/PCSG). Stats's argument is decisive: Q4 quantization shifts tail-token logprob distributions by an amount plausibly comparable to moderate cutoff effects near the decision boundary. This would invalidate PCSG's paired-contrast identification.

**Action**: Rent cloud A100/H100 GPU time for all white-box model runs. Run everything in bf16/fp16. Quant estimates total cloud cost at ~$15-25 for the full 3,200-case run across all white-box models — trivial relative to the project budget.

The user's local 4060 Ti 16GB remains useful for pilot runs, prototyping, and non-logprob detectors (CMMD text generation, SR/FO, NoOp, EAD, extraction), but confirmatory logprob detectors must run on uniform-precision cloud hardware.

**Fallback** (Stats): If cloud rental is temporarily unavailable, require a quantization equivalence gate before using mixed-precision results: correlation ≥ 0.98, mean shift < 0.1 SD, top-decile overlap > 0.9 between fp16 and quantized logprob distributions on a 200-case calibration set.

---

## Tensions requiring resolution (2 of 5 concerns)

### Concern 1 — White-box fleet composition

All 4 lenses agree the current 7B/9B/14B three-family design is problematic for PCSG identification, but they propose **3 different solutions**:

| Lens | Proposal | Fleet size impact | Core argument |
|---|---|---|---|
| **NLP** | Swap Qwen3-14B → **Qwen3-8B** | 6 → 6 (no change) | Same tokenizer as Qwen2.5-7B; similar size (7B vs 8B); creates clean same-tokenizer matched pair for primary PCSG. GLM-4-9B stays but only for sensitivity. |
| **Editor** | Swap Qwen3-14B → **Qwen3-8B** | 6 → 6 | Cleaner 7B/8B/9B ladder within Editor's 7-model ceiling. |
| **Quant** | Upgrade Qwen2.5-7B → **Qwen2.5-14B** | 6 → 6 | Creates Qwen2.5-14B vs Qwen3-14B same-size same-era pair for PCSG. |
| **Stats** | Add **both** Qwen2.5-14B AND Qwen3-8B | 6 → 8 | Two matched pairs: (Qwen2.5-7B, Qwen3-8B) for small-model PCSG + (Qwen2.5-14B, Qwen3-14B) for large-model PCSG. Size falsification controls via within-family same-cutoff pairs. |

**Analysis**:

- **NLP + Editor agree** (2/4): Swap Qwen3-14B → Qwen3-8B. This is the simplest change, keeps fleet at 6, and NLP's tokenizer argument is strong (Qwen2.5 and Qwen3 share the same tokenizer; GLM-4-9B uses a different one — tokenizer differences are a bigger confound for logprob-based detectors than parameter size).
- **Stats wants 8 models** — the most thorough confound control, but Editor's ceiling is 7. Stats would need to argue 8 is not a model zoo.
- **Quant goes the other direction** — upgrade to larger models rather than downgrading. Quant's concern is that 7B/8B models may lack sufficient Chinese financial capability for alpha-relevant memorization detection.

**Orchestrator recommendation for user decision**: NLP + Editor's "swap Qwen3-14B → Qwen3-8B" is the most conservative change. If the user wants stronger confound control AND is willing to accept 7-8 models, Stats's proposal to also add Qwen2.5-14B is the upgrade path. Quant's "upgrade Qwen2.5-7B → 14B" conflicts with the other proposals and would lose the small-model data point.

**Proposed resolution**: **NLP/Editor baseline** (swap Qwen3-14B → Qwen3-8B) + **Stats optional add** (Qwen2.5-14B as 7th white-box model, only if 8-model fleet is acceptable). This gives:
- Primary PCSG pair: Qwen2.5-7B (cutoff 2023-10) vs Qwen3-8B (cutoff 2025-01) — same tokenizer family, similar size, 15-month cutoff gap
- Optional secondary PCSG pair: Qwen2.5-14B (cutoff 2023-10) vs Qwen3-14B (cutoff 2025-01) — size falsification check
- GLM-4-9B as cross-family sensitivity

### Concern 3 — Which OpenAI model to add

All 4 lenses agree an OpenAI model should be added. They recommend **3 different GPT versions**:

| Lens | Model | Cutoff | Rationale |
|---|---|---|---|
| **NLP + Editor** | GPT-5.1 (`gpt-5.1-2025-11-13`) | 2024-09-30 | Pinnable checkpoint, fills temporal gap between GLM-4 (2024-06) and Qwen3 (2025-01), good Chinese capability |
| **Quant** | GPT-5.4 (`gpt-5.4-2026-03-05`) | 2025-08-31 | Most recent, extends fleet temporal span, maximizes reviewer SOTA impact |
| **Stats** | GPT-4.1 | ~2024-06 | Near-same-cutoff control for GLM-4-9B, enables within-cutoff-band disagreement baseline |

**Analysis**:

- **NLP + Editor agree on GPT-5.1** (2/4): It has a known cutoff (2024-09-30) that fills a gap in the temporal staircase, a pinnable dated checkpoint, and confirmed Chinese capability.
- **Quant's GPT-5.4** extends the fleet's temporal span further (cutoff 2025-08-31) — useful for alpha-bridge but partially redundant with Claude Sonnet 4.6 which also covers late-2025.
- **Stats's GPT-4.1** prioritizes identification (same-cutoff control) over brand impact — methodologically sound but loses the "we tested GPT-5" headline.

**Orchestrator recommendation**: **GPT-5.1** (NLP + Editor consensus). It balances temporal gap-filling, reproducibility (pinnable checkpoint), and reviewer impact. If budget allows a second OpenAI model, GPT-4.1 as a same-cutoff control for GLM-4-9B is Stats's upgrade path.

---

## Entity masking taxonomy (Round 2 delta question)

**3/4 consensus** (NLP, Stats, Quant; Editor silent on specifics):

**Category-preserving masking should use sector/role level ONLY, not prominence level.**

- ✅ "某互联网公司"（sector）
- ✅ "某证券公司高管"（sector + role）
- ❌ "某**著名**互联网巨头"（prominence adjective reintroduces Entity Salience confound）

NLP's argument is cleanest: prominence cues like "著名" or "巨头" narrow the candidate set and reintroduce quasi-identification — a reader (or model) can guess "著名互联网巨头" = one of ~5 companies (Alibaba, Tencent, ByteDance, Meituan, JD). That defeats the purpose of anonymization.

Both masking depths (full-anon "公司A" and sector-preserving "某互联网公司") should be retained as the two levels of the target/competitor × full-anon/category-preserving 2×2 taxonomy already locked in R5A_DEFAULTS.md.

---

## Proposed revised fleet

Based on the consensus items + orchestrator recommendations on the two tensions:

### Baseline proposal (7 models — NLP/Editor path)

| # | Model | Location | Cutoff | Access | Params | Role |
|---|---|---|---|---|---|---|
| 1 | Qwen 2.5-7B-Instruct | cloud bf16 | 2023-10 | white-box | 7B | Earliest cutoff anchor; PCSG pair A (early) |
| 2 | DeepSeek-V2.5 | OpenRouter | ~2024-03 | black-box | MoE | Mid-early cutoff |
| 3 | GLM-4-9B-0414 | cloud bf16 | 2024-06-30 | white-box | 9B | Cross-family sensitivity; mid cutoff |
| 4 | DeepSeek-V3-0324 | OpenRouter | 2024-07 | black-box | MoE | Mid cutoff |
| 5 | **GPT-5.1-2025-11-13** | OpenAI API | **2024-09-30** | **black-box** | unknown | **NEW: fills temporal gap; vendor diversity** |
| 6 | **Qwen3-8B** (thinking OFF) | cloud bf16 | **2025-01** | **white-box** | **8B** | **REPLACES Qwen3-14B; PCSG pair A (late)** |
| 7 | **Claude Sonnet 4.6** | OpenRouter | **~2025-08** | **black-box** | unknown | **UPGRADED from 4.5; latest cutoff anchor** |

Changes from v6.2: +GPT-5.1, swap Qwen3-14B→8B, upgrade Claude 4.5→4.6. Net: 6→7 models.

Fleet span: 2023-10 → ~2025-08 (22 months, +1 month vs v6.2).
White-box: 3 (Qwen2.5-7B, GLM-4-9B, Qwen3-8B) — all on cloud bf16.
Black-box: 4 (DeepSeek-V2.5, DeepSeek-V3, GPT-5.1, Claude Sonnet 4.6).

PCSG primary pair: Qwen2.5-7B (2023-10) ↔ Qwen3-8B (2025-01) — same tokenizer, similar size, 15-month gap.

### Upgrade proposal (8 models — Stats path)

Add **Qwen2.5-14B-Instruct** (cloud bf16, cutoff 2023-10, white-box, 14B) as model #8.

This enables:
- PCSG pair A (small): Qwen2.5-7B vs Qwen3-8B (7B vs 8B, same tokenizer)
- PCSG pair B (large): Qwen2.5-14B vs Qwen3-14B* (14B vs 14B, same tokenizer)
- Size falsification: Qwen2.5-7B vs Qwen2.5-14B (same family, same cutoff, different size — any PCSG gap here is pure capability confound)

*If Stats upgrade is adopted, Qwen3-14B returns to the fleet alongside Qwen3-8B.

### Cost estimate

| Component | Baseline (7) | Upgrade (8) |
|---|---|---|
| Cloud GPU (white-box bf16) | ~$20-30 | ~$35-50 |
| OpenRouter (DeepSeek×2 + Claude) | ~$8-12 | ~$8-12 |
| OpenAI API (GPT-5.1) | ~$5-15 | ~$5-15 |
| **Total per full-fleet detector run** | **~$35-55** | **~$50-75** |

At 7-9 detectors, total fleet cost is roughly $250-500 (baseline) to $400-650 (upgrade) for the main experiment. Well within the user's stated budget flexibility.

---

## Fleet design principles (distilled from 4 lenses)

1. **Same-tokenizer matched pairs for PCSG**: The primary temporal contrast must compare models that share a tokenizer to avoid logprob-distribution confounds. Qwen2.5 ↔ Qwen3 pairs satisfy this.
2. **Uniform precision**: All white-box models run in bf16/fp16 on cloud GPU. No quantization for confirmatory logprob detectors.
3. **Thinking mode OFF for confirmatory**: Extended reasoning / thinking modes disabled fleet-wide. Thinking ON is a pre-registered sensitivity analysis.
4. **Pin to dated checkpoints**: Every model in the fleet must have a version-locked checkpoint ID before pre-commit. OpenRouter provider routing must be locked.
5. **Vendor diversity is secondary to temporal coverage**: Add models primarily for cutoff diversity, secondarily for vendor diversity. A GPT model at the right cutoff > a GPT model at a redundant cutoff.
6. **7-model ceiling for main text** (Editor): 8 is the hard maximum. Beyond 8, model-specific results move to supplementary materials.

---

## Open items for Step 2

1. **User decision: 7-model baseline or 8-model Stats upgrade?** This is a budget + paper-structure call.
2. **Verify GPT-5.1 cutoff date and checkpoint pinning** before fleet freeze.
3. **Verify Claude Sonnet 4.6 cutoff date** — estimated ~2025-08 but needs confirmation.
4. **Verify Qwen3-8B availability** on HuggingFace with a specific commit SHA.
5. **If Stats upgrade: verify Qwen2.5-14B-Instruct** availability and compatibility with vLLM.
6. **Cloud GPU provider selection** for white-box runs (Vast.ai / Modal / RunPod / Lambda).

---

## Artifacts

- `quant_lens.md` — thread `019d9416-c79e-78c3-9018-d8ee113d124b`
- `nlp_lens.md` — thread `019d9416-f410-7e23-939d-fca70d6b3e93`
- `stats_lens.md` — thread pending
- `editor_lens.md` — thread `019d9417-4472-72c0-8693-d0e2a1f53659`
- `FLEET_REVIEW_BRIEF.md` — input brief
- `FLEET_REVIEW_SYNTHESIS.md` — this file
