---
title: R5A Fleet Review Round 2 — Agent Brief
stage: R5A Round 3b (revision of Round 3a fleet review)
date: 2026-04-15
status: INPUT DOCUMENT for 4-lens Codex discussion
baseline: FLEET_REVIEW_SYNTHESIS.md (Round 1 output)
---

# R5A Fleet Review Round 2 — Agent Brief

## Why a Round 2

Round 1 produced a 7-model baseline fleet proposal that addressed the original 5 user concerns (capability ladder, thinking mode, no OpenAI, SOTA timeliness, quantization). However, the user identified 4 additional design principles that Round 1 did not consider. These principles are significant enough to require a full re-evaluation of fleet composition.

**Each agent should read `FLEET_REVIEW_SYNTHESIS.md` (Round 1 output) first as the baseline**, then revise their fleet proposal in light of the new principles below.

## Round 1 baseline fleet (for reference)

| # | Model | Cutoff | Access | Params | Architecture |
|---|---|---|---|---|---|
| 1 | Qwen 2.5-7B-Instruct | 2023-10 | white-box | 7B | Qwen dense |
| 2 | DeepSeek-V2.5 | ~2024-03 | black-box | MoE ~236B | DeepSeek MoE |
| 3 | GLM-4-9B-0414 | 2024-06-30 | white-box | 9B | GLM dense |
| 4 | DeepSeek-V3-0324 | 2024-07 | black-box | MoE ~671B | DeepSeek MoE |
| 5 | GPT-5.1-2025-11-13 | 2024-09-30 | black-box | unknown | OpenAI |
| 6 | Qwen3-8B (thinking OFF) | 2025-01 | white-box | 8B | Qwen dense |
| 7 | Claude Sonnet 4.6 | ~2025-08 | black-box | unknown | Anthropic |

Round 1 locked consensus: uniform bf16 on cloud GPU for white-box; thinking OFF for confirmatory; Claude upgraded to 4.6; GPT-5.1 added.

## 4 new design principles from user (2026-04-15)

### New Principle A — Thinking/reasoning mode is a FLEET-WIDE variable, not just a Qwen issue

Round 1 treated thinking mode as a Qwen3-specific confound and recommended disabling it. But virtually every modern model family has a reasoning mode switch:
- Qwen3/3.5: `enable_thinking`
- Claude: extended thinking
- GPT-5.x: reasoning effort settings
- DeepSeek: thinking mode

"Disable thinking across the fleet" means testing models in a non-default, potentially degraded state that does not reflect real-world deployment. The user's counter-argument: thinking mode may REVEAL different forms of memorization (e.g., explicit event recall in chain-of-thought) and suppressing it may hide signal rather than reduce confounds.

**Open question for agents**: Should thinking/reasoning mode be:
- (a) Disabled fleet-wide for ALL analyses (Round 1 recommendation) — cleanest confound control but least realistic
- (b) Enabled fleet-wide as the PRIMARY analysis, with thinking-OFF as sensitivity — most realistic but introduces reasoning-mode confounds across families
- (c) Split by detector type: logprob detectors (PCSG, Min-K++) use thinking OFF (because thinking changes token distributions); behavioral detectors (CMMD, SR/FO, NoOp, EAD, extraction, ADG) use thinking ON (because they care about the model's real-world response)
- (d) Treated as a RESEARCH VARIABLE: run every model in both modes, report the difference as a finding ("reasoning mode modulates memorization expression")
- (e) Something else?

Consider that option (d) doubles the fleet's effective size for compute purposes. Is it worth it?

### New Principle B — Same-cutoff different-architecture pairs for falsification

Round 1 focused on different-cutoff pairs (for measuring temporal effects) but did NOT include same-cutoff different-architecture pairs. The user points out this is a critical gap:

> If two models share the same cutoff but have different architectures, any CMMD/PCSG disagreement between them CANNOT be attributed to cutoff — it must come from architecture/capability differences. This directly gives an "architecture confound baseline."

Without same-cutoff pairs, you cannot distinguish "this disagreement is because of cutoff" from "this disagreement is because Qwen and GLM are different model families." Same-cutoff pairs are **falsification controls** that Round 1 missed.

**Open question for agents**: Identify specific model pairs where:
- Cutoff dates are within ~2 months of each other
- Architectures are different (different model families)
- Parameter counts are similar (within the same size tier)
These pairs serve as "if CMMD/PCSG shows a gap here, it's architecture noise, not memorization signal."

### New Principle C — Architecture coverage as a systematic design dimension

Instead of treating architecture differences as confounds to minimize, treat them as a dimension to COVER. The fleet should intentionally include models from different architecture families (dense transformer, MoE, different training paradigms) so that the benchmark can report whether memorization detection patterns are architecture-dependent or universal.

This is analogous to the reasoning-mode-as-variable idea: architecture diversity is not just noise — "memorization detection sensitivity varies across architecture families" is itself a publishable finding.

**Open question for agents**: What architecture families should the fleet cover? At minimum:
- Qwen family (dense, Chinese-first)
- GLM family (dense, Chinese-bilingual)
- DeepSeek family (MoE, Chinese-first)
- OpenAI family (unknown architecture, English-first with Chinese capability)
- Anthropic family (unknown architecture, English-first with Chinese capability)
Are there other families worth including (e.g., Llama/Meta, Mistral, Yi)?

### New Principle D — Multiple size tiers with internal matching

Round 1 focused on one size tier (~7-9B for white-box models). The user proposes having MULTIPLE size tiers where within each tier models are parameter-matched, enabling cross-tier comparison of "does model size affect memorization detection?"

Example structure:
- **Small tier (~7-8B)**: Qwen2.5-7B, Qwen3-8B, GLM-4-9B — internally matched, test cutoff+architecture
- **Medium tier (~14B)**: Qwen2.5-14B, Qwen3-14B, [other 14B?] — internally matched, same tests
- **Large tier (hosted, parameter-unknown)**: GPT-5.x, Claude, DeepSeek-V3 — black-box, cannot match exactly but represent SOTA

Cross-tier comparison: if a memorization signal is visible in the small tier but not the medium tier (or vice versa), that is evidence about capability × memorization interaction.

**Open question for agents**: Is the multi-tier design worth the fleet expansion? How many tiers are needed (2? 3?)? What is the minimum number of models per tier for the within-tier contrasts to be meaningful?

## Additional model candidates to consider

Round 1 did not evaluate these. Round 2 agents should consider:

- **Qwen3.5** (recently released) — what is its cutoff? Does it supersede Qwen3-8B from Round 1? What sizes are available?
- **Qwen2.5-14B-Instruct** — Stats Round 1 proposed this for size falsification
- **Qwen3-14B** — was in v6.2 fleet, removed in Round 1 but may return in a multi-tier design
- **GPT-4.1** — Stats Round 1 proposed for same-cutoff control with GLM-4-9B
- **GPT-5.4** — Quant Round 1 proposed for latest SOTA
- **DeepSeek-V3-0324 thinking mode** — does DeepSeek V3 have a reasoning mode?
- **Yi / Llama / Mistral** — are there Chinese-capable models from these families at relevant cutoff dates?
- Any other models the agents are aware of that the project has not considered

## What this session should produce

Each agent should:

1. **Evaluate each of the 4 new principles (A-D)**: Is it important? Is it feasible within a reasonable fleet size? What is the minimum fleet change needed to satisfy it?

2. **Propose a revised fleet table** that incorporates the new principles. The table should annotate each model with:
   - Size tier (small / medium / large)
   - Architecture family
   - Cutoff date
   - Reasoning mode availability (yes/no, and what it's called)
   - Access type (white-box / black-box)
   - Role in the design: temporal pair / same-cutoff falsification pair / architecture coverage / size-tier anchor

3. **Propose fleet design pairings**: Which specific model pairs serve which design purpose? Format as a pairing table.

4. **Give a fleet size recommendation**: What is the minimum fleet that satisfies all 4 principles? What is the ideal fleet? What is the maximum before it becomes unmanageable?

5. **Address the thinking mode question (Principle A)** with a concrete recommendation: option (a), (b), (c), (d), or (e).

6. **Cost estimate** for the proposed fleet at 3,200 cases × K detectors.

## Lens-specific angles

- **Quant**: Which models matter for alpha-bridge credibility? Is multi-tier comparison useful for Thales (e.g., "smaller models memorize differently than larger ones")?
- **NLP**: Tokenizer families across the fleet. Chinese financial capability across tiers. Reasoning mode effects on Chinese text generation quality.
- **Stats**: Factorial design structure. How many models per cell are needed for the pairwise contrasts to have power? Is the multi-tier design statistically identified or over-parameterized?
- **Editor**: Fleet size ceiling for a 9-page paper. Can a 10+ model fleet be presented without becoming a model zoo? Is "memorization varies by architecture" a compelling sub-finding or scope creep?

## What is NOT open

Round 1 locked consensus items carry forward:
- Uniform bf16/fp16 precision on cloud GPU for all white-box models
- Claude upgraded to Sonnet 4.6
- At least one OpenAI model in the fleet
- Pin to dated checkpoints; lock OpenRouter provider routing
- Category-preserving masking = sector/role level, no prominence adjectives
