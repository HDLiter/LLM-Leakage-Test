---
role: NLP / methodology
session: R5A Fleet Review Round 2
thread_id: 019d944c-89e0-7813-9aa0-68cfd4fb62fd
model_reasoning_effort: xhigh
generated: 2026-04-15
based_on:
  - FLEET_REVIEW_SYNTHESIS.md
  - FLEET_REVIEW_R2_BRIEF.md
---

# NLP view: revise to a 9-model core, and treat Qwen3.5 as shadow evaluation

## Verdict

Round 2 changes the NLP answer materially. The main issue is no longer just "do we have a decent Chinese-capable Qwen pair?" It is now:

1. whether the fleet distinguishes **tokenizer-family control** from **exact tokenizer control**,
2. whether Chinese financial generation is being measured in a comparable **reasoning regime**,
3. and whether architecture and size are handled as real moderators rather than as background noise.

My recommendation is:

- adopt **option (c)** for reasoning mode, with a small appendix ablation,
- move to a **9-model confirmatory core**,
- and keep **Qwen3.5 out of the confirmatory core**.

Qwen3.5 is worth evaluating, but not as a silent replacement for `Qwen3-8B`. It changes too many things at once: architecture, modality, tokenizer artifact, context length, and default reasoning behavior.

## 0. Tokenizer findings that change the design

The strongest new NLP result from this round is that the Qwen tokenizer story is more subtle than Round 1 assumed.

- `Qwen2.5-7B-Instruct` and `Qwen2.5-14B-Instruct` share the exact same published `tokenizer.json`.
- `Qwen3-8B`, `Qwen3-14B`, `Qwen3-30B-A3B`, `Qwen3-32B`, and `Qwen3-235B-A22B` share the exact same published `tokenizer.json`.
- `Qwen3.5-9B`, `Qwen3.5-27B`, `Qwen3.5-35B-A3B`, `Qwen3.5-122B-A10B`, and `Qwen3.5-397B-A17B` share the exact same published `tokenizer.json`.
- But the `Qwen2.5`, `Qwen3`, and `Qwen3.5` tokenizer artifacts are **not identical across generations**, even though all expose `Qwen2Tokenizer`.

Methodological implication:

- `Qwen2.5` vs `Qwen3` is **same tokenizer family**, not fully exact-tokenizer controlled.
- `Qwen3` dense vs `Qwen3` MoE is **exact-tokenizer controlled**.
- `Qwen3.5` dense vs `Qwen3.5` MoE is **exact-tokenizer controlled**.

For `PCSG` / `Min-K++`, that distinction matters. The cleanest exact-tokenizer architecture falsification pair is therefore **within Qwen3**, not `Qwen2.5` vs `Qwen3`.

## 1. Evaluation of Principles A-D

### Principle A — reasoning mode is fleet-wide

- Importance: **very high**
- Feasibility: **high** if split by detector family
- Minimum fleet change needed: **protocol change**, not a fleet doubling

### NLP recommendation: **option (c)**, with a narrow appendix overlay

- `PCSG` and `Min-K++`: reasoning/thinking **OFF** wherever a real switch exists.
- Behavioral detectors (`CMMD`, `SR/FO`, `NoOp`, `EAD`, extraction, `ADG`): run in the model's **default deployed mode**.
- Add a small ON/OFF appendix sensitivity on a stratified subset for `Qwen3-14B`, `GPT-5.1`, and `Claude Sonnet 4.6`.

Why:

- For logprob detectors, reasoning mode changes the token stream too aggressively to preserve comparability.
- For behavioral detectors, suppressing reasoning everywhere makes the benchmark less representative of how modern systems are actually used.

### Chinese financial text quality under reasoning mode

This effect is family-specific:

- **Qwen3 / Qwen3.5**: thinking mode usually improves structure, hedging discipline, and multi-step financial synthesis in Chinese, but it also lengthens answers and increases the risk of style drift. Qwen's own guidance uses different sampling settings for thinking vs non-thinking, and the Qwen3.5 card explicitly warns that higher presence penalties can induce **language mixing** and slightly reduce performance. That is a real Chinese-generation comparability risk.
- **GPT-5.1**: reasoning effort is cleaner as an API variable than Qwen's inline thinking tags, but higher effort still changes answer style, verbosity, and cost. For generation-quality evaluation this is useful; for detector comparability it is a confound.
- **Claude Sonnet 4.6**: extended/adaptive thinking tends to improve synthesis quality, but it also pushes responses toward longer, more discursive answer forms. That can inflate `CMMD` disagreement for reasons unrelated to memorization.
- **DeepSeek**: reasoning is now a family-level capability in current API docs, but it is not a clean ON/OFF switch on the pinned `DeepSeek-V3-0324` snapshot. That makes DeepSeek reasoning a poor confirmatory variable for this round.

Net: reasoning mode should be part of the **behavioral** story, not the **logprob identification** story.

### Principle B — same-cutoff different-architecture falsification pairs

- Importance: **very high**
- Feasibility: **moderate**
- Minimum fleet change needed: **one same-cutoff falsification pair in the core**

There are two distinct classes of same-cutoff falsification pairs:

#### Best tokenizer-controlled architecture pair

- `Qwen3-32B` vs `Qwen3-30B-A3B`
- Same release window: Qwen3 official release on **2025-04-29**
- Exact tokenizer control: yes
- Architecture contrast: dense vs MoE
- Size matching: close in total parameters

This is the cleanest NLP pair for "architecture noise, not cutoff." The problem is fleet size, not methodology.

#### Best tokenizer-uncontrolled core pair

- `GLM-4-9B-0414` vs `GPT-4.1-2025-04-14`
- Cutoff band: around **June 2024**
- Exact tokenizer control: no
- Architecture/vendor contrast: yes
- Size matching: imperfect because GPT parameters are undisclosed

This is good enough for a **behavioral falsification baseline** and should be in the confirmatory core. It is not clean enough to anchor `PCSG`.

### Principle C — architecture coverage is a design dimension

- Importance: **high**
- Feasibility: **high** if the family list is capped
- Minimum fleet change needed: keep the fleet to **Qwen / GLM / DeepSeek / OpenAI / Anthropic**

Recommended coverage:

- **Qwen dense**: primary Chinese-first temporal and size backbone
- **GLM dense**: Chinese-bilingual cross-family control
- **DeepSeek MoE**: Chinese-first MoE family
- **OpenAI**: closed frontier reference and same-cutoff control via `GPT-4.1`
- **Anthropic**: closed frontier reference with distinct generation style

I would **not** add `Yi`, `Llama`, or `Mistral` to the confirmatory core. They add vendor count faster than they add identification.

### Principle D — multiple size tiers with internal matching

- Importance: **very high**
- Feasibility: **high** at two white-box tiers plus one hosted tier
- Minimum fleet change needed: add `Qwen2.5-14B-Instruct` and `Qwen3-14B`

Recommended tier structure:

- **Small white-box tier**: `Qwen2.5-7B`, `Qwen3-8B`, `GLM-4-9B`
- **Medium white-box tier**: `Qwen2.5-14B`, `Qwen3-14B`
- **Large hosted tier**: `DeepSeek-V3-0324`, `GPT-5.1`, `Claude Sonnet 4.6`

This is the minimum tier structure that can say something defensible about whether memorization-sensitive behavior scales with model size.

## 2. Revised fleet table

Cutoff note:

- For `GPT-4.1`, `GPT-5.1`, and `Claude Sonnet 4.6`, the dates below are official published knowledge cutoffs.
- For `Qwen2.5`, `Qwen3`, and `Qwen3.5`, I did **not** find official model-card knowledge cutoff dates in the checked sources. Where the project already uses `2023-10` or `2025-01`, those should be treated as **project design anchors**, not audited vendor-published cutoffs.
- For `GLM-4-9B-0414`, I did not independently verify an official vendor-published knowledge cutoff in the checked sources, so I retain the project's existing **`2024-06-30` design anchor**.

### Confirmatory core (9)

| # | Model | Tier | Family / architecture | Cutoff date | Reasoning mode availability | Access | Design role |
|---|---|---|---|---|---|---|---|
| 1 | `Qwen/Qwen2.5-7B-Instruct` | small | Qwen dense | `2023-10` project anchor | no dual-mode switch | white-box | early small temporal anchor |
| 2 | `THUDM/GLM-4-9B-0414` | small | GLM dense | `2024-06-30` project anchor | no clean dual-mode switch | white-box | Chinese-bilingual architecture control |
| 3 | `Qwen/Qwen3-8B` | small | Qwen dense | `2025-01` project anchor | `enable_thinking` | white-box | late small temporal anchor |
| 4 | `Qwen/Qwen2.5-14B-Instruct` | medium | Qwen dense | `2023-10` project anchor | no dual-mode switch | white-box | early medium temporal anchor |
| 5 | `Qwen/Qwen3-14B` | medium | Qwen dense | `2025-01` project anchor | `enable_thinking` | white-box | late medium temporal anchor |
| 6 | `deepseek-ai/DeepSeek-V3-0324` | large | DeepSeek MoE | `2024-07` project anchor | current DeepSeek family supports reasoning, but not as a clean pinned `V3-0324` toggle | hosted / black-box | Chinese-first MoE coverage |
| 7 | `gpt-4.1-2025-04-14` | large | OpenAI non-reasoning | `2024-06-01` official | no reasoning step | black-box | same-cutoff falsification with GLM |
| 8 | `gpt-5.1-2025-11-13` | large | OpenAI reasoning-capable | `2024-09-30` official | `reasoning.effort` | black-box | late OpenAI temporal anchor |
| 9 | `claude-sonnet-4-6` | large | Anthropic reasoning-capable | `2025-08` reliable knowledge cutoff | extended / adaptive `thinking` | black-box | latest frontier anchor |

### Architecture appendix upgrade (+2)

| Model | Tier | Why add it |
|---|---|---|
| `Qwen/Qwen3-30B-A3B` | upper-medium | exact-tokenizer-controlled Qwen MoE |
| `Qwen/Qwen3-32B` | upper-medium | exact-tokenizer-controlled Qwen dense |

These two models turn architecture falsification from a tokenizer-uncontrolled proxy into a clean within-family controlled test.

## 3. Pairing table

| Pair | Purpose | Tokenizer status | What it identifies |
|---|---|---|---|
| `Qwen2.5-7B` vs `Qwen3-8B` | small-tier temporal pair | same tokenizer family, not exact-tokenizer guaranteed | primary small-tier temporal contrast |
| `Qwen2.5-14B` vs `Qwen3-14B` | medium-tier temporal pair | same tokenizer family, not exact-tokenizer guaranteed | primary medium-tier temporal contrast |
| `Qwen2.5-7B` vs `Qwen2.5-14B` | early size control | exact-tokenizer controlled | size effect at early anchor |
| `Qwen3-8B` vs `Qwen3-14B` | late size control | exact-tokenizer controlled within Qwen3 | size effect at late anchor |
| `GLM-4-9B-0414` vs `GPT-4.1` | core same-cutoff falsification pair | tokenizer uncontrolled | architecture/vendor noise baseline for behavioral detectors |
| `DeepSeek-V3-0324` vs `GPT-5.1` | late hosted family contrast | tokenizer uncontrolled | whether Chinese-first MoE behaves differently from OpenAI on a nearby temporal band |
| `GPT-5.1` vs `Claude Sonnet 4.6` | hosted frontier contrast | tokenizer uncontrolled | whether late closed models disagree because of family/style rather than benchmark content |
| `Qwen3-32B` vs `Qwen3-30B-A3B` | appendix architecture falsification | exact-tokenizer controlled | clean dense-vs-MoE architecture effect at fixed release window |
| `Qwen3.5-27B` vs `Qwen3.5-35B-A3B` | shadow architecture pair | exact-tokenizer controlled | exploratory Qwen3.5 dense-vs-MoE test after freeze |

## 4. Fleet size recommendation

- **Minimum that satisfies A-D in the core paper**: **9**
- **Ideal fleet**: **11**
- **Maximum before it becomes a model zoo**: **11 in supplement, 9 in main analysis**

Interpretation:

- `9` is the smallest fleet that gives you two white-box size tiers, one same-cutoff falsification pair, and all five architecture families.
- `11` is the size where the NLP story becomes strongest, because you can add the clean Qwen3 dense-vs-MoE tokenizer-controlled pair.
- Beyond `11`, Qwen3.5, Yi, Llama, and similar additions should be treated as exploratory extras, not core evidence.

## 5. Thinking-mode answer

**Answer: option (c)**.

Operationally:

- logprob detectors: reasoning OFF
- behavioral detectors: default deployed mode
- appendix sensitivity: ON/OFF for `Qwen3-14B`, `GPT-5.1`, `Claude Sonnet 4.6`

This is the only option that preserves both:

- logprob identification,
- and realistic Chinese financial generation behavior.

## 6. Cost estimate

Working assumption:

- `3,200` cases
- roughly `1,000` input + `150` output tokens per case for black-box runs
- white-box models served in `bf16/fp16` on rented cloud GPUs

### API-side cost per full-fleet detector pass

- `GPT-4.1`: about **$10.2**
- `GPT-5.1`: about **$8.8**
- `Claude Sonnet 4.6`: about **$16.8**
- `DeepSeek` API-equivalent pricing at current `deepseek-chat` rates would be roughly **$1.4** without cache hits, but this is only a rough ceiling because `DeepSeek-V3-0324` is a pinned hosted/open-weight design slot rather than the current `DeepSeek-V3.2` API alias

### White-box cost

Using Modal's current list price for an `A100 80GB` at about **$2.50/hour**, a 5-model white-box core remains roughly in the same budget class as Round 1:

- **9-model core**: about **$55-$75** per detector pass total
- **11-model ideal**: about **$80-$110** per detector pass total

At `K = 8` detectors:

- **9-model core**: about **$440-$600**
- **11-model ideal**: about **$640-$880**

Reasoning-mode appendix uplift:

- budget an extra **20-60%** on the `GPT-5.1` and `Claude Sonnet 4.6` behavioral branch, because reasoning tokens and longer outputs can increase billed output materially

## Qwen3.5 evaluation

### What sizes are available?

From the current official Qwen Hugging Face listing, the open Qwen3.5 family currently includes:

- dense-like sizes: `0.8B`, `2B`, `4B`, `9B`, `27B`
- MoE sizes: `35B-A3B`, `122B-A10B`, `397B-A17B`

### What is the cutoff?

I did **not** find an official vendor-published knowledge cutoff date for Qwen3.5 in the checked model cards or documentation.

What is official:

- Qwen's site lists **Qwen3.5** as open-sourced on **2026-02-15**
- the model card citation places it in **February 2026**

Methodological consequence:

- Qwen3.5 is fine as a **release-date-anchored shadow model**
- it is **not** fine as a clean replacement for `Qwen3-8B` in a temporal-identification core unless you are willing to use a release-date proxy instead of a real cutoff

### Does it share Qwen3's tokenizer?

- It shares the **tokenizer class** (`Qwen2Tokenizer`)
- it does **not** share Qwen3's exact published tokenizer artifact
- within the Qwen3.5 family, the tokenizer artifact is internally consistent across checked sizes

So the answer is:

- **same tokenizer family**: yes
- **same exact tokenizer artifact as Qwen3**: no

### Should it replace `Qwen3-8B`?

**No, not in the confirmatory fleet.**

Reasons:

- no official audited cutoff found
- different tokenizer artifact from `Qwen3`
- multimodal vision-language model card, not a clean text-only successor
- hybrid architecture rather than the simpler Qwen3 dense setup
- thinking on by default, with different control semantics from Qwen3

### What should be done with it instead?

Use `Qwen3.5-9B` as a **shadow evaluation model** after the confirmatory fleet is frozen.

Best use:

- run behavioral detectors on the same Chinese finance subset used for the reasoning appendix
- compare it to `Qwen3-8B` and `Qwen3-14B` as a "what changes when the Qwen line becomes multimodal-hybrid?" stress test
- do **not** merge it into the main temporal ladder

## Bottom line

- Round 2 should move the NLP recommendation from a 7-model baseline to a **9-model core**.
- The most important methodological correction is to distinguish **same tokenizer family** from **exact tokenizer control**.
- The cleanest exact-tokenizer architecture pair is inside **Qwen3**, not across `Qwen2.5` and `Qwen3`.
- `Qwen3.5` is worth running, but as a **shadow model**, not as the replacement for `Qwen3-8B`.

## Sources

- Qwen3 blog: https://qwenlm.github.io/blog/qwen3/
- Qwen3-8B model card: https://huggingface.co/Qwen/Qwen3-8B
- Qwen3-14B model card: https://huggingface.co/Qwen/Qwen3-14B
- Qwen2.5-7B-Instruct model card: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- Qwen2.5-14B-Instruct model card: https://huggingface.co/Qwen/Qwen2.5-14B-Instruct
- Qwen3.5-9B model card: https://huggingface.co/Qwen/Qwen3.5-9B
- Qwen3.5 docs in Transformers: https://huggingface.co/docs/transformers/en/model_doc/qwen3_5
- GLM-4-9B-0414 model card: https://huggingface.co/THUDM/GLM-4-9B-0414
- DeepSeek models and pricing: https://api-docs.deepseek.com/quick_start/pricing
- DeepSeek-V2.5 release note: https://api-docs.deepseek.com/news/news0905
- OpenAI GPT-4.1 docs: https://developers.openai.com/api/docs/models/gpt-4.1
- OpenAI GPT-5.1 docs: https://developers.openai.com/api/docs/models/gpt-5.1
- Anthropic pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic release notes: https://platform.claude.com/docs/en/release-notes/overview
- Modal pricing: https://modal.com/pricing
