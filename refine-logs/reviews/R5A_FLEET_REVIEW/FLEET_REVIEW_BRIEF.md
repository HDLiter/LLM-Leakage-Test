---
title: R5A Fleet Review — Agent Brief
stage: R5A Round 3
date: 2026-04-15
status: INPUT DOCUMENT for 4-lens Codex discussion
scope: CMMD fleet composition, capability matching, SOTA timeliness, hardware constraints
context_files:
  - docs/DECISION_20260413_mvp_direction.md (v6.2, CMMD fleet section)
  - docs/CMMD_MODEL_FLEET_SURVEY.md
  - refine-logs/reviews/R5A_STEP1/R5A_DEFAULTS.md
  - refine-logs/reviews/R5A_TEMPORAL_CUE/R5A_TEMPORAL_CUE_SYNTHESIS.md
---

# R5A Fleet Review — Agent Brief

## Purpose

The v6.2 CMMD 6-model fleet was locked during R4 as a "strong reference for R5, NOT a default starting point" (per v5.3 user clarification). The R4 literature sweep found no chronologically-controlled model family that clears the fleet-add gates. However, user discussion on 2026-04-15 raised 5 specific concerns that warrant a fleet review before R5A Step 2 convergence.

This session does NOT have the authority to lock the fleet — it produces a **revised fleet proposal** that feeds into Step 2 alongside the detector defaults and temporal-cue synthesis. Step 2 agents then make the final fleet recommendation.

## Current fleet (v6.2 reference)

| # | Model | Location | Cutoff | Access | Params | Notes |
|---|---|---|---|---|---|---|
| 1 | Qwen 2.5-7B-Instruct | local vLLM | 2023-10 | white-box | 7B | fp16 fits 16GB |
| 2 | DeepSeek-V2.5 | OpenRouter | ~2024-03 | black-box | MoE ~236B | |
| 3 | GLM-4-9B-0414 | local vLLM | 2024-06-30 | white-box | 9B | may need quantization on 16GB |
| 4 | DeepSeek-V3-0324 | OpenRouter | 2024-07 | black-box | MoE ~671B | |
| 5 | Qwen3-14B | local vLLM | 2025-01 | white-box | 14B | needs Q4 on 16GB; has thinking mode |
| 6 | Claude Sonnet 4.5 | OpenRouter | 2025-01/07 | black-box | unknown | `claude-sonnet-4-5-20250929` |

Fleet span: 2023-10 → 2025-07 (21 months). White-box: 3 local. Black-box: 3 hosted.
Pre-commit requirement: pin to dated checkpoints and lock OpenRouter provider routing.

## User concerns (2026-04-15)

### Concern 1 — Capability ladder mismatch among white-box models

The 3 local white-box models differ substantially in parameter count: 7B → 9B → 14B. This is a near-2× jump between the smallest and largest. When CMMD or PCSG attributes disagreement to cutoff differences, the signal is confounded by:
- Raw capability differences (14B models are generally more capable than 7B models on instruction-following, reasoning, Chinese financial comprehension)
- Architecture differences (Qwen2.5, GLM-4, Qwen3 are different model families)
- Training data mix differences beyond cutoff (each family has different pretraining corpora)

The confound is especially problematic for PCSG (D2), which takes a within-case late-minus-early surprise gap — if the "late" model is also twice the size, the gap reflects both cutoff and capability.

**Open question**: Should the white-box fleet be redesigned for better capability matching? Options include:
- (a) Use same-family different-cutoff pairs (e.g., Qwen2.5-7B vs Qwen3-8B, or Qwen2.5-7B vs Qwen2.5-14B if available)
- (b) Use same-size different-cutoff pairs (e.g., two 7B models with different cutoffs)
- (c) Keep current fleet but add statistical capability controls (model-pair fixed effects, capability-matching propensity scores)
- (d) Rent cloud GPU to run larger models without quantization artifacts

### Concern 2 — Reasoning mode not unified

Qwen3-14B has a "thinking mode" (extended reasoning / chain-of-thought before responding). The other two white-box models (Qwen2.5-7B, GLM-4-9B) do not have this mode. If Qwen3 runs in thinking mode, it is using a fundamentally different inference regime — more careful, slower, and potentially less susceptible to memorization-based shortcuts (because it "reasons through" rather than pattern-matching from memory).

This creates a confound: if CMMD or PCSG shows that Qwen3-14B disagrees with the other two, is it because (a) Qwen3 saw the event in training (memorization signal), (b) Qwen3 is larger and more capable, or (c) Qwen3 is using thinking mode which changes its behavior?

**Open question**: How should thinking mode be handled?
- (a) Disable thinking mode on Qwen3 (use standard decoding) to unify inference regime
- (b) Run both modes (thinking ON + thinking OFF) and report as a sensitivity analysis
- (c) Accept as a confound and control statistically
- (d) Replace Qwen3-14B with a non-thinking model of similar cutoff

### Concern 3 — No OpenAI model in the fleet

The current fleet has zero OpenAI models. For a benchmark paper claiming to measure memorization across "widely adopted" LLMs, the absence of GPT-4 / GPT-4o / GPT-5 family is conspicuous. Reviewers will ask "what about GPT?"

**Context**: OpenAI models are black-box only (no logprob access for Min-K%++ or PCSG, but usable for CMMD, SR/FO, NoOp, EAD, extraction, ADG). Adding an OpenAI model would increase the black-box fleet to 4 and the total fleet to 7+.

**Open question**: Should one or more OpenAI models be added?
- If yes: which model and version? What is its cutoff date? Does it add cutoff diversity (a date not already covered by the fleet) or just vendor diversity?
- Cost implication: OpenAI API calls are generally more expensive than DeepSeek/Claude on OpenRouter. At 3,200 cases per detector, each additional model adds meaningful cost.
- Reproducibility: OpenAI model versioning has historically been less transparent than Anthropic's dated checkpoints. Is this a risk for pre-commit reproducibility?

### Concern 4 — SOTA timeliness

Claude 4.7 is expected to release within days (around 2026-04-18). The current fleet pins to Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`). Should the fleet update to Claude 4.7 when it becomes available?

More broadly: should the fleet aim for SOTA at the time of running experiments (maximizing relevance and reviewer impact) or for stability/reproducibility (minimizing the risk that model updates break results)?

**Trade-off**:
- Updating to Claude 4.7: more relevant at publication time, but cutoff date is unknown until release, and the model may not have a pinnable dated checkpoint immediately.
- Staying on Claude Sonnet 4.5: cutoff is known (2025-01 reliable / 2025-07 extended), checkpoint is pinnable, reproducibility is high.
- Running BOTH: adds cost but hedges both concerns.

**User's stated principle**: "用那些高影响力的在业界被广泛采用的模型来作为参照物是更重要的" — using high-influence, widely-adopted models as reference points matters more. This argues for including SOTA models even at reproducibility cost.

### Concern 5 — Hardware and budget constraints

**Local hardware**: NVIDIA GeForce RTX 4060 Ti with 16GB VRAM.
- 7B models (Qwen2.5-7B): comfortable in fp16 (~14GB)
- 9B models (GLM-4-9B): tight in fp16 (~18GB), needs at minimum Q8 quantization (~9-10GB) or offloading
- 14B models (Qwen3-14B): requires Q4 quantization (~8GB) or cloud deployment

**Quantization confound**: If Qwen2.5-7B runs in fp16 but Qwen3-14B runs in Q4, the comparison is not just "7B vs 14B" or "2023-10 cutoff vs 2025-01 cutoff" — it is also "fp16 vs Q4 quantization", which affects logprob distributions and potentially Min-K%++ / PCSG scores.

**Cloud budget**: User has indicated willingness to rent cloud GPU for experiments. Cost can be traded for experimental quality. This means:
- All local white-box models could potentially run in fp16 on a rented A100/H100
- Additional larger models (e.g., 70B) could potentially be added to the fleet if the identification argument justifies it
- The 4060 Ti 16GB constraint is a default, not a hard limit

## Fleet-add gates (from v6.2, for reference)

The v6.2 fleet survey applied 4 gates:
1. **Downloadable**: weights publicly available for local deployment
2. **Non-redundant cutoff**: cutoff date falls in the [2023-10, 2025-07] window and is not within ~2 months of an existing fleet member
3. **Chinese capability**: usable performance on Chinese financial text
4. **Compute-fit**: runnable within the project's compute budget

These gates are a reference, not a hard constraint. This session may revise or relax them.

## What this session should produce

For each of the 5 concerns, each lens should produce:
1. **Diagnosis**: Is this concern real or overstated? How much does it actually threaten CMMD / PCSG / other detector validity?
2. **Recommended action**: What specific fleet change (if any) addresses the concern?
3. **Model candidates** (if adding): Specific model name, version/checkpoint, cutoff date, parameter count, access type, estimated cost for 3,200-case run.
4. **Trade-offs**: What does the recommended action cost in terms of budget, complexity, or reproducibility?

After addressing all 5 concerns, each lens should produce a **revised fleet proposal** (complete table of recommended models) and a **fleet design principles** section (3-5 principles that guide fleet composition, e.g., "at least 2 same-family different-cutoff pairs for capability control").

## Additional context: Entity masking taxonomy question

A minor design question deferred from earlier discussion: when category-preserving entity masking is applied (as part of D7 EAD's 2×2 taxonomy), what level of category information should be preserved?

- Option A — "公司A" (full anonymization): removes ALL entity information including category
- Option B — "某著名互联网巨头" (category-preserving): keeps sector + prominence tier
- Option C — both, as two sub-variants

The temporal cue session locked EAD at 2×2 (target/competitor × full-anon/category-preserving). This question asks what "category-preserving" concretely means. If the lens has a view, include it in the cross-concern synthesis. Otherwise, note it as deferred to implementation.

## What is NOT open in this session

1. The 7 Step 1 consensus items (independent reporting, deviate from MemGuard-Alpha, etc.)
2. The temporal-cue session outcomes (Factor 13, D4 split, D11 reshape, time-handling defaults)
3. The detector pool composition (7 definite + D4 pending + D11/D12 candidates)
4. The factor shortlist (12 active + Factor 13 Temporal Anchor Recoverability)
