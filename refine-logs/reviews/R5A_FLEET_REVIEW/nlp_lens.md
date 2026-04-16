---
role: NLP / methodology
session: R5A Fleet Review
thread_id: 019d9416-f410-7e23-939d-fca70d6b3e93
model_reasoning_effort: xhigh
generated: 2026-04-15
---

**Verdict**

From the NLP/methodology lens, the main problem is measurement non-equivalence, not just raw model strength. For logprob detectors on Chinese text, cross-tokenizer comparisons are a bigger threat than a 7B vs 14B size gap. I would make the fleet do two jobs explicitly: a **controlled white-box pair** for temporal identification, and a **broader black-box layer** for external validity. Primary temporal claims should come from the controlled pair; full-fleet CMMD should be reported as secondary coverage evidence.

API cost estimates below assume `3,200` cases, about `1k input + 150 output tokens/case`, and **no reasoning tokens**.

**1. White-box capability ladder / tokenizer mismatch**

Diagnosis: real. For CMMD-style answer disagreement, capability/size differences are a major confound. For Min-K++ / PCSG, tokenizer mismatch is even worse, because the unit of surprise changes. In a small local probe on 5 Chinese finance strings, `Qwen2.5-7B` and `Qwen3` tokenized identically; `GLM-4-9B` uses a different `tokenizer.model` stack.

Recommended action: replace `Qwen3-14B` with `Qwen3-8B`. Use `Qwen2.5-7B` vs `Qwen3-8B` as the **primary white-box pair**, both in BF16. Keep `GLM-4-9B-0414` as a midpoint **sensitivity** model, not the primary late-minus-early PCSG comparator. Add model-pair fixed effects for CMMD; I would not rely on propensity-score "capability matching."

Model candidate: `Qwen/Qwen3-8B`, cutoff `~2025-01` at the Qwen3 family level (inference from current Qwen3 usage), `8.2B`, white-box, API cost `n/a`.

Trade-off: slightly less raw capability than 14B, but much cleaner tokenization and size matching.

**2. Thinking mode**

Diagnosis: real and first-order. If `Qwen3` thinks while the others do not, CMMD/PCSG disagreement is not interpretable as cutoff-linked memorization.

Recommended action: **disable thinking in the core fleet**. If you want robustness, run thinking ON/OFF only as a preregistered sensitivity on a small stratified subset, not as separate fleet members. Apply the same rule to other reasoning-capable black-box models: `reasoning.effort=none` for `GPT-5.1`, and no extended/adaptive thinking on Claude.

Model candidate: none beyond the Qwen3 replacement; for Qwen3 use `enable_thinking=False`.

Trade-off: some loss in peak benchmark accuracy, large gain in interpretability and cost control.

**3. No OpenAI model**

Diagnosis: real for paper positioning, but not because GPT is weak in Chinese. The official evidence points the other way: `GPT-4o` has better Chinese token compression and better Mainland-China medical QA than `GPT-4T`; `GPT-5` reports strong Simplified Chinese MMLU. The real questions are cutoff placement and inference-mode cleanliness.

Recommended action: add **exactly one** OpenAI model as a black-box reference, via the **native OpenAI API** rather than a routed alias. My preference is `gpt-5.1-2025-11-13` with `reasoning.effort=none`. If you want the cleanest non-thinking alternative, use `gpt-4.1-2025-04-14`. I would not pick `GPT-4o` unless reviewer optics matter more than chronological diversity.

Model candidates:
- `gpt-5.1-2025-11-13`, cutoff `2024-09-30`, params undisclosed, black-box, about `$8.8`
- Fallback `gpt-4.1-2025-04-14`, cutoff `2024-06-01`, params undisclosed, black-box, about `$10.2`
- Not recommended as primary add: `gpt-4o-2024-11-20`, cutoff `2023-10-01`, about `$12.8`; strongest explicit Chinese evidence, but mostly adds vendor diversity rather than a new temporal anchor

Trade-off: better external validity and reviewer acceptance, but more vendor heterogeneity. Snapshot pinning makes reproducibility much better than the old mutable-GPT-alias setup.

**4. SOTA timeliness / Claude 4.7**

Diagnosis: do not optimize around speculative releases. As of **April 15, 2026**, Anthropic's official release notes show `Claude Opus 4.6` launched on **February 5, 2026** and `Claude Sonnet 4.6` on **February 17, 2026**. I did **not** find an official `Claude 4.7` release.

Recommended action: do not plan a core-fleet swap to unreleased `Claude 4.7`. Keep a stable pinned Sonnet checkpoint in the core fleet. If a newer Anthropic model becomes officially released and immutably pinnable before freeze, run it as a **shadow appendix model**, not as a last-minute replacement.

Model candidate: optional shadow `claude-sonnet-4-6` only if Anthropic exposes a stable immutable ID you accept for preregistration; listed price is `$3/$15` per MTok, so roughly `$16.8` under the above token assumption.

Trade-off: you lose "latest-week" optics, but the GPT addition already answers the most obvious reviewer question.

**5. Hardware / budget**

Diagnosis: real. Mixed-precision or quantized white-box comparisons are not acceptable as the primary setup for Min-K++ / PCSG; the probability tails are exactly what quantization perturbs.

Recommended action: spend cloud budget on **precision parity** before spending it on extra models. Run all white-box models used for logprob detectors on the same cloud stack, BF16 preferred, same serving stack/version. If budget is tight, a clean Qwen pair plus GLM sensitivity is methodologically better than a larger mixed-precision fleet.

Model candidate: none; this is an execution-policy change.

Trade-off: higher infra cost and less "runs on a 4060 Ti" convenience, but much better detector validity.

**Revised Fleet**

| Model | Role | Cutoff | Access | Params | Note |
|---|---|---:|---|---:|---|
| Qwen2.5-7B-Instruct | Primary white-box early anchor | 2023-10 | white-box | 7.61B | BF16 |
| Qwen3-8B | Primary white-box late anchor | ~2025-01 | white-box | 8.2B | `enable_thinking=False`; cutoff is a family-level inference |
| GLM-4-9B-0414 | White-box midpoint sensitivity | 2024-06-30 | white-box | 9B | BF16; separate tokenizer family |
| DeepSeek-V2.5 | Black-box mid anchor | ~2024-03 | black-box | MoE ~236B | keep |
| DeepSeek-V3-0324 | Black-box late-2024 anchor | 2024-07 | black-box | MoE ~671B | keep |
| GPT-5.1-2025-11-13 | Black-box GPT anchor | 2024-09-30 | black-box | undisclosed | `reasoning.effort=none` |
| Claude Sonnet 4.5 `claude-sonnet-4-5-20250929` | Black-box stable frontier anchor | Jan 2025 reliable cutoff | black-box | undisclosed | no extended thinking |

**Design Principles**
- Separate clean identification from broad coverage: primary temporal claims should come from controlled same-tokenizer white-box pairs; full-fleet CMMD is secondary/external-validity evidence.
- For logprob detectors in Chinese, tokenizer equivalence matters more than parameter matching. For response-disagreement detectors, capability matching matters more.
- The core fleet should run in one inference regime: no thinking, no adaptive reasoning, no mixed quantization.
- Spend budget first on BF16 precision parity and immutable checkpoints, only then on extra fleet members.
- Use conservative reliable knowledge cutoffs for chronology; treat late SOTA arrivals as shadow runs unless fully pinnable before freeze.

**Entity Masking**
`Category-preserving` should mean **sector/role-level only**, e.g. `某互联网公司`, `某券商`, `某新能源车企`. I would **not** preserve prominence-level cues like `某著名互联网巨头` in the main taxonomy, because they sharply narrow the candidate set and reintroduce quasi-entity identification. If you want prominence, make it a later ablation, not the default EAD condition.

Sources: [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B), [Qwen3-14B-FP8](https://huggingface.co/Qwen/Qwen3-14B-FP8), [GLM-4-9B-Chat](https://huggingface.co/zai-org/glm-4-9b-chat), [OpenAI models overview](https://developers.openai.com/api/docs/models), [GPT-4o model](https://developers.openai.com/api/docs/models/gpt-4o), [GPT-4.1 model](https://developers.openai.com/api/docs/models/gpt-4.1), [GPT-5.1 model](https://developers.openai.com/api/docs/models/gpt-5.1), [GPT-4o system card](https://cdn.openai.com/gpt-4o-system-card.pdf), [GPT-5 system card](https://cdn.openai.com/gpt-5-system-card.pdf), [Anthropic models overview](https://platform.claude.com/docs/en/docs/models-overview), [Anthropic release notes](https://platform.claude.com/docs/en/release-notes/overview).
