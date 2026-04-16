---
role: Editor / narrative and venue-fit
session: R5A Fleet Review Round 2
thread_id: 019d944c-f972-7a00-842d-531f31f60ff4
model_reasoning_effort: xhigh
generated: 2026-04-15
---

**Verdict**

A 9-page EMNLP paper cannot carry a 10-15 model fleet as first-class evidence. It can carry a **6-model confirmatory core in main text** and a **9-10 model full fleet in supplement**.  
"Memorization varies by architecture and model size" is **paper-strengthening only as a secondary moderation result**; it becomes scope creep if it competes with the main thesis that FinMem-Bench enables cleaner, factor-controlled memorization detection.

**Principles And Recommendation**

- **A. Thinking mode:** important, but not worth a full fleet-wide 2x expansion. My recommendation is **option (e)**: standardize the **confirmatory core in non-thinking/base mode**, then run a **3-anchor appendix sensitivity** in default reasoning mode (`Qwen3`, `GPT-5.1`, `Claude 4.6`) on a stratified subset. If forced into the menu, this is closest to **(c)**, but narrower.
- **B. Same-cutoff falsification pairs:** essential. Without at least one near-same-cutoff architecture control, reviewers can always say "you found family noise." Minimum change: add **`gpt-4.1-2025-04-14`** against **`GLM-4-9B-0414`**.
- **C. Architecture coverage:** useful, but only as coverage. Cap it at **Qwen / GLM / DeepSeek / OpenAI / Anthropic**. Do **not** add Yi/Llama/Mistral unless one of them fills a specific pairing hole.
- **D. Multiple size tiers:** worth it if you keep to **two real matched white-box tiers**. Minimum change: add **`Qwen2.5-14B-Instruct`** and restore **`Qwen3-14B`**.

**Fleet Size**
- **Minimum that satisfies A-D:** **8**
- **Ideal full fleet:** **10**
- **Absolute max for main text:** **8 named models**, with only **6 actively interpreted**
- **Practical max with supplement:** **12**
- **10-15** is only viable if the paper explicitly treats most of the fleet as **supplementary robustness**, not co-equal story elements.

**Ideal Full Fleet (10)**

| Set | Model | Tier | Family | Cutoff | Reasoning mode | Access | Design role |
|---|---|---|---|---|---|---|---|
| Core | Qwen2.5-7B-Instruct | Small | Qwen dense | 2023-10 | none public | WB | Small early temporal anchor |
| Core | Qwen3-8B | Small | Qwen dense | 2025-01 | `enable_thinking` | WB | Small late temporal anchor |
| Core | GLM-4-9B-0414 | Small | GLM dense | 2024-06-30 | none public | WB | Architecture control |
| Core | Qwen2.5-14B-Instruct | Medium | Qwen dense | 2023-10 | none public | WB | Medium early temporal anchor |
| Core | Qwen3-14B | Medium | Qwen dense | 2025-01 | `enable_thinking` | WB | Medium late temporal anchor |
| Core | GPT-4.1-2025-04-14 | Hosted | OpenAI | 2024-06-01 | non-reasoning | BB | Same-cutoff falsification with GLM |
| Coverage | DeepSeek-V2.5 | Hosted | DeepSeek MoE | ~2024-03–05 | family split (`chat`/`reasoner`) | BB | Mid-cutoff MoE coverage |
| Coverage | DeepSeek-V3-0324 | Hosted | DeepSeek MoE | 2024-07 | family split (`chat`/`reasoner`) | BB | Later MoE coverage |
| Coverage | GPT-5.1-2025-11-13 | Hosted | OpenAI | 2024-09-30 | `reasoning.effort` | BB | Late OpenAI temporal anchor |
| Coverage | Claude Sonnet 4.6 | Hosted | Anthropic | 2025-08 reliable | extended/adaptive thinking | BB | Latest frontier anchor |

**Pairings**

| Purpose | Pair / set |
|---|---|
| Small temporal pair | `Qwen2.5-7B` vs `Qwen3-8B` |
| Medium temporal pair | `Qwen2.5-14B` vs `Qwen3-14B` |
| Early size control | `Qwen2.5-7B` vs `Qwen2.5-14B` |
| Late size control | `Qwen3-8B` vs `Qwen3-14B` |
| Same-cutoff architecture falsification | `GLM-4-9B-0414` vs `GPT-4.1` |
| External-validity robustness | `DeepSeek-V2.5`, `DeepSeek-V3`, `GPT-5.1`, `Claude 4.6` |

`Qwen3.5` should stay **out of the confirmatory core**: its official model card presents it as a **multimodal, hybrid architecture** with **thinking on by default**, so it is not a clean replacement for the Qwen temporal pair. `GPT-5.4` is also not a core pick here because its **August 31, 2025** cutoff is too redundant with Claude Sonnet 4.6's **August 2025 reliable cutoff**.

**Paper Strategy**

- Main text should be organized by **contrasts**, not by vendors.
- Show only **three result blocks** in main text:
  1. Small-tier temporal pair
  2. Medium-tier temporal pair
  3. Same-cutoff falsification pair
- Put the rest of the fleet into a **robustness layer**: one pooled figure/table plus full per-model results in supplement.
- Use one compact fleet-design figure: **cutoff × size tier × family × role**.
- Never give every model its own paragraph. Every model must earn one non-overlapping role.

**Editor Answers**

- **Absolute max in a 9-page main text:** **8**, but **6-7** is the healthy range.
- **With supplement:** **10** is clean, **12** is still defensible, **15** is too many unless the paper becomes appendix-heavy and stops pretending the fleet is all main-text evidence.
- **Does architecture/size heterogeneity strengthen the paper?** Yes, if framed as: "the benchmark's signal is not a one-family artifact." No, if framed as: "we also discovered a general scaling law of memorization."
- **Cost estimate:**  
  - **8-model minimum:** about **$45-60** per full-detector fleet pass  
  - **10-model ideal:** about **$55-75** per pass  
  - At **7-9 detectors**, roughly **$315-675** total, plus about **10-15%** for the 3-model reasoning appendix

**Two-Sentence Pitch**

Matched temporal pairs show that memorization-sensitive detector signals survive controlled cutoff comparisons, but their magnitude is systematically modulated by model family and scale. This turns architecture and size from nuisance confounds into boundary conditions: FinMem-Bench is not just detecting memorization, but showing where that memorization expresses more strongly or more weakly across model classes.

**Sources checked**

- OpenAI GPT-4.1: https://developers.openai.com/api/docs/models/gpt-4.1
- OpenAI GPT-5.1: https://developers.openai.com/api/docs/models/gpt-5.1
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic Sonnet 4.6 announcement: https://www.anthropic.com/news/claude-sonnet-4-6
- Qwen3 blog: https://qwenlm.github.io/blog/qwen3/
- Qwen3.5 model card: https://huggingface.co/Qwen/Qwen3.5-9B
- DeepSeek API docs: https://api-docs.deepseek.com/
