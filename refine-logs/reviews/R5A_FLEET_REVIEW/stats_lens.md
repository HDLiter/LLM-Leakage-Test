---
role: Stats / power and identification
session: R5A Fleet Review
thread_id: 019d9417-2d19-7783-ac60-9f2428ab4187
model_reasoning_effort: xhigh
generated: 2026-04-15
---

**Bottom Line**
From the stats lens, the current 6-model reference is acceptable for exploratory `CMMD`, but it is not clean enough for confirmatory `PCSG`. The biggest real threats are `Concern 1` and `Concern 5`: the current white-box trio confounds cutoff with size/family/inference regime, and mixed `Q4` vs `fp16` is not safe for `Min-K++/PCSG`.

**1. Concern 1: White-box capability ladder mismatch**
- This concern is real, and it is first-order for `PCSG`.
- For `CMMD`, mismatch mostly inflates noise. For `PCSG`, it breaks identification because `late - early` is currently also `bigger - smaller`, `Qwen - GLM`, and possibly `thinking - non-thinking`.
- Same-family matched pairs are not strictly required for `CMMD`, but they are effectively required for confirmatory `PCSG`. Without at least one same-family close-size pair, `PCSG` should be exploratory only.
- I would redesign the white-box core to: `Qwen2.5-7B`, `Qwen2.5-14B`, `GLM-4-9B-0414`, `Qwen3-8B`, `Qwen3-14B`.
- Pre-register these contrasts:
  1. Primary `PCSG`: `Qwen2.5-14B` vs `Qwen3-14B`.
  2. Secondary `PCSG`: `Qwen2.5-7B` vs `Qwen3-8B`.
  3. Size falsification control: `Qwen2.5-14B` vs `Qwen2.5-7B`.
  4. Size falsification control: `Qwen3-14B` vs `Qwen3-8B`.
  5. `CMMD` within-band control: `GLM-4-9B-0414` vs `GPT-4.1`.
- Use pair-standardized gaps, not raw gaps: `G_{i,p} = (S_late - S_early - mean_placebo_p) / sd_placebo_p`.
- Then estimate factor effects on `G_{i,p}` with pair fixed effects. This removes baseline pair difficulty and ability differences.
- I would not use propensity scores here. Fleet size is too small for model-level propensity methods to be credible; design-stage matching is much stronger.

**2. Concern 2: Thinking mode**
- Real confound.
- For confirmatory runs, set `Qwen3` to `thinking OFF`. Same rule for any configurable reasoning mode on hosted models: use the non-extended/default regime.
- Run thinking `ON` only as a sensitivity analysis on a stratified subset. It should not define a separate fleet member.
- If `thinking ON` materially changes `PCSG` direction on placebo cases, that is evidence the detector is inference-regime sensitive, not cutoff-identified.

**3. Concern 3: No OpenAI model**
- Add exactly one OpenAI model.
- My stats pick is `gpt-4.1-2025-04-14`, not `GPT-5`, because its official `2024-06-01` knowledge cutoff creates a near-same-cutoff control with `GLM-4-9B-0414` (`2024-06-30`). That is statistically more valuable than simply adding another frontier brand.
- Estimated cost at `3,200` cases with `300` input + `50` output tokens is about `$3.2` for one detector pass.
- If reviewer optics dominate identification, `GPT-5` is the appendix alternative, not my core pick.

**4. Concern 4: SOTA timeliness**
- The brief's date premise is already stale: as of **April 15, 2026**, Anthropic has already released **Claude Sonnet 4.6** on **February 17, 2026**.
- Anthropic's current docs list `claude-sonnet-4-6` as active with **Aug 2025 reliable knowledge cutoff** and **Jan 2026 training data cutoff**.
- From a stats perspective, this is a genuinely useful late anchor.
- My recommendation is: include `Claude Sonnet 4.6` in the fleet, but treat it as a black-box reference anchor and archive raw responses, resolved provider metadata, and hashes. If Step 2 insists on immutable dated snapshots only, fall back to `claude-sonnet-4-5-20250929` in the confirmatory core and move `4.6` to appendix.

**5. Concern 5: Hardware, budget, quantization**
- Real for `Min-K++/PCSG`; much less serious for output-only detectors like `CMMD`.
- Strong `4-bit` methods can keep average perplexity drift small, but that is not enough. `Min-K++` and `PCSG` depend on tail-token logprobs, and low-bit errors are input-sensitive.
- My bound is: `Q4` is probably smaller than a large cutoff effect on obvious memorized cases, but it is plausibly the same order as the moderate effects you actually need to estimate near the decision boundary. So mixed `fp16` vs `Q4` across pair members is not acceptable for confirmatory `PCSG`.
- Recommendation: rent cloud GPU and run all white-box `Min-K++/PCSG` models in the same `bf16/fp16` regime.
- If quantization is unavoidable, all compared models must use the same scheme and pass an equivalence gate on about `200` calibration cases:
  - score correlation `>= 0.98`
  - mean shift `< 0.1` pooled SD
  - top-decile overlap `> 0.9`
  - placebo-vs-leakage separation changes by `< 10%`
- If that gate fails, the model can still stay in `CMMD`, but not in confirmatory `Min-K++/PCSG`.

**Power**
- The proposed `8`-model fleet gives `28` pairwise model contrasts versus `15` now. Under an independence upper bound that is about a `27%` SE reduction for pairwise-summary CMMD-style quantities; the real gain is smaller, but the important improvement is structural: you gain three within-band controls.
- The proposed `5` white-box models give `10` white-box pairs versus `3` now, and more importantly move you from effectively `0-1` usable `PCSG` pairs to `2` clean pre-registerable pairs.

**Revised Fleet Proposal**
| Model | Cutoff | Access | Stats role |
|---|---|---|---|
| `Qwen2.5-7B-Instruct` | `2023-10` | white-box, `bf16/fp16` | early small anchor |
| `Qwen2.5-14B-Instruct` | `2023-10` | white-box, `bf16/fp16` | same-cutoff size control |
| `GLM-4-9B-0414` | `2024-06-30` | white-box, `bf16/fp16` | official mid-cutoff anchor |
| `gpt-4.1-2025-04-14` | `2024-06-01` | black-box | same-cutoff cross-vendor control, OpenAI coverage |
| `deepseek-chat-v3-0324` | `2024-07` | black-box | Chinese late-2024 anchor |
| `Qwen3-8B` | `~2025-01` | white-box, `bf16/fp16`, thinking off | matched late small pair |
| `Qwen3-14B` | `~2025-01` | white-box, `bf16/fp16`, thinking off | matched late large pair |
| `claude-sonnet-4-6` | `Aug 2025 reliable / Jan 2026 training` | black-box | late frontier anchor |

If you need a leaner fallback, drop `Qwen3-8B` first and keep the rest.

**Masking Taxonomy**
- Statistically, prefer `Option C`, not `A` or `B` alone.
- `raw - category-preserving` estimates identity-specific signal.
- `category-preserving - full-anon` estimates semantic information-loss from masking itself.
- For category-preserving masks, preserve only coarse type or sector, not prominence cues. `某互联网平台公司` is safer than `某著名互联网巨头`, because prominence is itself a salience confound.

**Fleet Design Principles**
- Optimize for identifiable contrasts, not maximal date coverage.
- Allow purposeful cutoff redundancy if it creates a within-band control or a matched pair.
- For logprob detectors, all white-box comparisons must share inference mode and numeric precision.
- Require at least one same-family matched cutoff pair for confirmatory `PCSG`.
- Add exactly one OpenAI model and one Anthropic model, but choose them for design leverage, not brand completeness.

Sources: project brief plus [OpenAI GPT-4.1 docs](https://developers.openai.com/api/docs/models/gpt-4.1), [OpenAI GPT-5 docs](https://developers.openai.com/api/docs/models/gpt-5), [Anthropic Claude models overview](https://platform.claude.com/docs/en/about-claude/models/overview), [Anthropic Claude 4.6 release notes](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6), [QQQ: Quality Quantization for LLMs](https://arxiv.org/abs/2406.09904), [Why Do Some Inputs Break Low-Bit LLM Quantization?](https://arxiv.org/abs/2506.12044), [Quantization Meets Reasoning](https://arxiv.org/abs/2501.03035).
