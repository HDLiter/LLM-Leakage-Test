---
role: Quant / alpha-bridge
session: R5A Fleet Review
thread_id: 019d9416-c79e-78c3-9018-d8ee113d124b
model_reasoning_effort: xhigh
generated: 2026-04-15
---

Quant view: the current v6.2 fleet is close for CMMD, but not clean enough for the stronger claim you actually care about, namely that memorization contaminates alpha-relevant behavior rather than just correlating with model quality. The fix is not a bigger zoo. It is a cleaner white-box causal core, plus one current GPT reference.

1. **Concern 1: white-box capability ladder mismatch**
- Diagnosis: real, and high-severity for `PCSG`; moderate for `CMMD`. `7B -> 9B -> 14B`, mixed families, and mixed quantization make the current late-minus-early gap too easy to read as capability drift.
- Recommended action: redesign the white-box core around one matched same-family pair. My first choice is `Qwen2.5-14B-Instruct (~2023-10, estimated)` vs `Qwen3-14B (~2025-01, estimated)`, with `GLM-4-9B-0414 (2024-06-30)` kept as the orthogonal middle control.
- Model candidates: replace `Qwen2.5-7B-Instruct` with `Qwen2.5-14B-Instruct`; keep `Qwen3-14B`; keep `GLM-4-9B-0414`. Primary `PCSG` pair should be `Qwen2.5-14B` vs `Qwen3-14B`; any GLM pair is robustness, not primary identification.
- Trade-offs: you give up "already deployed locally" convenience, but you buy a much cleaner cutoff-control argument. Statistical controls should still be used, but they should rescue residual noise, not a bad fleet design.

2. **Concern 2: reasoning mode not unified**
- Diagnosis: real. Qwen3's hybrid thinking mode is a different inference regime, not a nuisance detail. For memorization work, that is a serious confound.
- Recommended action: primary runs should disable thinking everywhere configurable. For Qwen3, run `enable_thinking=False`. For GPT-5.4, use `reasoning_effort=none`. For Claude 4.6, do not enable extended/adaptive thinking in the primary run.
- Trade-offs: primary analysis becomes slightly less "production-like," but much more interpretable. Run a smaller sensitivity branch with thinking on after the main result is locked.

3. **Concern 3: no OpenAI model**
- Diagnosis: real. This does not kill detector validity, but it does weaken reviewer credibility and the alpha-bridge story. A fleet without GPT is easy to dismiss as "Chinese open models plus Claude."
- Recommended action: add exactly one OpenAI model.
- Recommended GPT: `gpt-5.4-2026-03-05`, knowledge cutoff `2025-08-31`, black-box, direct OpenAI API preferred. At your current workload assumption of `3,200` cases with about `300` input and `50` output tokens, cost is about **$4.80** per run.
- Cheaper fallback: `gpt-4.1-2025-04-14`, knowledge cutoff `2024-06-01`, about **$3.20** per run. This is cleaner as a non-reasoning model, but it adds mostly vendor diversity, not much new cutoff coverage.
- Not my primary pick: `gpt-4o-2024-11-20`, knowledge cutoff `2023-10-01`, about **$4.00** per run. It is high-profile, but cutoff-redundant with the Qwen2.5 anchor.
- Trade-offs: the incremental cost of `GPT-5.4` over `GPT-4.1` is only about **$1.60** per 3,200-case pass. That saving is too small to justify losing the "we tested a current frontier GPT" line.

4. **Concern 4: SOTA timeliness**
- Diagnosis: real, but the right rule is "latest official model at freeze date," not "chase rumors." As of **April 15, 2026**, Anthropic's official docs and release notes show **Claude Sonnet 4.6** as the current balanced Claude model. I found no official Claude 4.7 release.
- Recommended action: update the Claude slot from `Claude Sonnet 4.5` to `Claude Sonnet 4.6` now. Do not wait for a rumored `4.7`.
- Specific model: `claude-sonnet-4-6`, reliable knowledge cutoff `Aug 2025`, training data cutoff `Jan 2026`, pricing unchanged at about **$5.28** per 3,200-case pass under the same token assumption.
- Trade-offs: relevance improves materially. Reproducibility is still weaker than OpenAI snapshots because Anthropic exposes `claude-sonnet-4-6` as an alias-style model ID, so for this slot I would prefer first-party Anthropic or Bedrock regional routing over OpenRouter if possible.

5. **Concern 5: hardware and budget**
- Diagnosis: real, but cheap to fix. On a 4060 Ti, quantization is not a convenience issue for logprob detectors; it is an identification issue.
- Recommended action: rent cloud GPU for all white-box runs and keep the 4060 Ti for smoke tests only. Use `A100 80GB` as the default; use `H100 80GB` only if throughput becomes the bottleneck.
- Cost: current official pricing is roughly `A100 80GB` at **$1.35/hr** on Hyperstack and from **$1.64/hr** on Runpod; `H100 80GB` is about **$1.90/hr** on Hyperstack. A three-model white-box pass in this size range is roughly a **$15-$25** problem, not a budget problem.
- Trade-offs: the correct use of cloud budget here is cleaner inference, not adding 32B/70B models. Spend the money on removing `Q4 vs fp16` and `thinking vs non-thinking` confounds first.

**Revised fleet proposal**
| # | Model | Cutoff | Access | Quant-lens role |
|---|---|---|---|---|
| 1 | Qwen2.5-14B-Instruct | `~2023-10` estimated | white-box, cloud BF16/FP16 | early matched-size Qwen anchor |
| 2 | GLM-4-9B-0414 | `2024-06-30` | white-box, cloud BF16/FP16 | official mid-cutoff Chinese control |
| 3 | Qwen3-14B, thinking `OFF` | `~2025-01` estimated | white-box, cloud BF16/FP16 | late matched-size Qwen anchor |
| 4 | DeepSeek-V2.5 | `~2024-03/05` estimated | black-box | cheap Chinese mid-cutoff reference |
| 5 | DeepSeek-V3-0324 | `2024-07` | black-box | strong Chinese financial reference |
| 6 | GPT-5.4 `gpt-5.4-2026-03-05` | `2025-08-31` | black-box, direct OpenAI | GPT flagship credibility slot |
| 7 | Claude Sonnet 4.6 | reliable `2025-08`, training `2026-01` | black-box, direct Anthropic/Bedrock preferred | current Claude reference |

If Step 2 insists on staying at **6** models, the first cut should be `DeepSeek-V2.5`, not the GPT slot and not the updated Claude slot.

**Fleet design principles**
- One matched white-box cutoff pair is mandatory; diversity comes after identification.
- Primary inference regime must be standardized: no mixed thinking modes, no mixed quantization regimes.
- Include one current GPT and one current Claude for reviewer credibility and real-world alpha-filter relevance.
- Spend cloud budget on cleaner execution before adding more models.
- Pin exact snapshots where possible; where vendor APIs expose only aliases, archive provider metadata and use conservative cutoff coding.

**Entity masking note**
Use both variants, but define "category-preserving" narrowly: preserve economic role or sector, not prominence. `某互联网平台公司` is good; `某著名互联网巨头` leaks salience back in.

**Sources**
- OpenAI GPT-5.4 model docs: https://developers.openai.com/api/docs/models/gpt-5.4
- OpenAI GPT-4.1 model docs: https://developers.openai.com/api/docs/models/gpt-4.1
- OpenAI GPT-4o model docs: https://developers.openai.com/api/docs/models/gpt-4o
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic Sonnet 4.6 release note: https://www.anthropic.com/news/claude-sonnet-4-6
- Anthropic release notes: https://platform.claude.com/docs/en/release-notes/overview
- Qwen2.5 blog: https://qwenlm.github.io/blog/qwen2.5/
- Qwen3 blog: https://qwenlm.github.io/blog/qwen3/
- Hyperstack GPU pricing: https://www.hyperstack.cloud/gpu-pricing
- Runpod GPU pricing: https://www.runpod.io/gpu-pricing
