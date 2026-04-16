---
role: Quant / alpha-bridge
session: R5A Fleet Review Round 2
thread_id: 019d944c-8500-7332-8037-b78e2474a627
model_reasoning_effort: xhigh
generated: 2026-04-15
based_on:
  - FLEET_REVIEW_SYNTHESIS.md
  - FLEET_REVIEW_R2_BRIEF.md
---

# Quant view: revise to an 8-model, 3-tier fleet

Short version: Round 1 still underfit the identification problem. The main miss was not treating architecture and reasoning mode as design dimensions. The fix is not a 12-model zoo. It is an **8-model core** with:

- two matched white-box Qwen tiers for temporal and size identification,
- one explicit same-cutoff large-model falsification pair,
- one DeepSeek MoE slot for architecture coverage,
- and one current GPT plus one current Claude for alpha credibility.

My recommended core fleet is:

1. `Qwen/Qwen2.5-7B-Instruct`
2. `THUDM/GLM-4-9B-0414`
3. `Qwen/Qwen3-8B`
4. `Qwen/Qwen2.5-14B-Instruct`
5. `Qwen/Qwen3-14B`
6. `deepseek-ai/DeepSeek-V3-0324`
7. `gpt-5.4-2026-03-05`
8. `claude-sonnet-4-6`

Optional 9th model only if the paper can absorb it:

9. `gpt-4.1-2025-04-14`

The model to drop from the Round 1 baseline is `DeepSeek-V2.5`. Its marginal value is lower than the value of a second Qwen size tier or an explicit same-cutoff falsification control.

## 1. Evaluation of Principles A-D

### Principle A - reasoning mode is fleet-wide, not Qwen-only

- Importance: high.
- Feasibility: high if handled by detector type, low if treated as a full crossed factor.
- Minimum change needed: stop using one fleet-wide rule for every detector.

**Recommendation: option (c)**.

- `PCSG` and `Min-K++` should use thinking/reasoning **OFF** wherever a switch exists, because reasoning changes the token stream and breaks comparability for logprob-style detectors.
- Behavioral detectors (`CMMD`, `SR/FO`, `NoOp`, `EAD`, extraction, `ADG`) should use the model's **default deployed mode**, which for frontier models now usually means reasoning/thinking is available and often on by default or one flag away.
- Add a **small sensitivity branch**, not a full factorial expansion: run ON/OFF only for `Qwen3-14B`, `gpt-5.4-2026-03-05`, and `claude-sonnet-4-6` on a 10-15% stratified subset.

Quant rationale: Thales cares about what deployed systems actually do. If reasoning mode causes a model to explicitly retrieve or suppress memorized event facts, that is a real operational phenomenon, not just nuisance variance. But for logprob detectors, reasoning mode is too destructive to identification to leave on.

### Principle B - same-cutoff different-architecture falsification pairs

- Importance: very high.
- Feasibility: moderate.
- Minimum change needed: add at least **one** same-cutoff falsification pair that is not just same-family size matching.

Round 1 did not have a clean architecture-noise baseline. The core falsification pair I recommend is:

- `gpt-5.4-2026-03-05` vs `claude-sonnet-4-6`
  - OpenAI published cutoff: **2025-08-31**
  - Anthropic reliable knowledge cutoff: **2025-08**
  - Role: large-tier, same-cutoff, different-vendor/different-architecture falsification pair
  - Limitation: this is a **same-tier** control, not a truly parameter-matched control, because neither vendor discloses parameter counts

If those two disagree materially on `CMMD` or extraction despite essentially the same cutoff band, that disagreement is architecture/vendor noise, not temporal memorization signal.

Optional secondary falsification pair if a 9th slot is allowed:

- `THUDM/GLM-4-9B-0414` vs `gpt-4.1-2025-04-14`
  - GLM official release date proxy: **2024-06-18**
  - GPT-4.1 knowledge cutoff: **2024-06-01**
  - Role: mid-2024 same-cutoff control

This secondary pair is not size-matched as cleanly as I would like, so it is a bonus control, not core identification.

### Principle C - architecture coverage should be systematic

- Importance: high.
- Feasibility: high if capped at 5 families.
- Minimum change needed: ensure the fleet covers at least Qwen, GLM, DeepSeek, OpenAI, and Anthropic.

Recommended architecture coverage:

- **Qwen dense**: `Qwen2.5-7B`, `Qwen3-8B`, `Qwen2.5-14B`, `Qwen3-14B`
- **GLM dense**: `GLM-4-9B-0414`
- **DeepSeek MoE**: `DeepSeek-V3-0324`
- **OpenAI frontier**: `gpt-5.4-2026-03-05`
- **Anthropic frontier**: `claude-sonnet-4-6`

What I would **not** add to the confirmatory core:

- `Qwen3.5`: too disruptive for the core design. The current `Qwen3.5-9B` card describes a **hybrid architecture** with a vision encoder plus Gated DeltaNet and sparse MoE. That makes it a new family, not a clean successor to dense `Qwen3-8B/14B`. It belongs in an exploratory appendix, not the confirmatory fleet.
- `Llama`, `Mistral`, `Yi`: all are plausible appendix candidates, but none beat the marginal value of the medium Qwen tier or `GPT-4.1` for the main paper. `Yi` is the only one I would consider if the project later decides it wants a second Chinese small-tier family.

### Principle D - multiple size tiers with internal matching

- Importance: very high for this project.
- Feasibility: high at **2 white-box tiers + 1 hosted SOTA tier**.
- Minimum change needed: add `Qwen2.5-14B-Instruct` and restore `Qwen3-14B`.

Recommended tier structure:

- **Small white-box tier**: `Qwen2.5-7B`, `Qwen3-8B`, `GLM-4-9B`
- **Medium white-box tier**: `Qwen2.5-14B`, `Qwen3-14B`
- **Large hosted tier**: `DeepSeek-V3-0324`, `gpt-5.4-2026-03-05`, `claude-sonnet-4-6`

This is enough to answer the question Thales should actually care about:

- Do smaller local models surface memorized market or issuer facts more directly than medium models?
- Do medium open models close that gap?
- Do frontier hosted models suppress, reframe, or amplify that same signal under reasoning mode?

My answer on value for Thales is **yes**: a credible result that "small models memorize differently from larger models" is operationally useful because it maps directly to deployment routing. It tells a buyer whether a cheap on-prem 7B/8B model and a 14B model should be governed as the same risk class. That is more valuable than adding a sixth vendor family.

## 2. Revised fleet table

Cutoff note:

- For `GPT-5.4`, `GPT-4.1`, and `Claude Sonnet 4.6`, the dates below are official published knowledge cutoffs.
- For `Qwen2.5`, `Qwen3`, and `DeepSeek-V3-0324`, the vendors do not publish a comparable reliable knowledge cutoff in the model cards I checked. I therefore keep the project's existing Qwen cutoff anchors and use explicit proxies where needed. These should be read as **design anchors**, not audited training-cutoff facts.
- For `GLM-4-9B-0414`, I use the official release date from the Transformers docs as a proxy because I did not find an official knowledge cutoff.

| # | Model | Tier | Family / architecture | Cutoff date | Reasoning mode availability | Access | Design role |
|---|---|---|---|---|---|---|---|
| 1 | `Qwen/Qwen2.5-7B-Instruct` | small | Qwen dense | `2023-10` project anchor | No dual-mode switch | white-box | early small-tier temporal anchor |
| 2 | `THUDM/GLM-4-9B-0414` | small | GLM dense | `2024-06-18` release-date proxy | No dual-mode switch in this checkpoint | white-box | cross-family small-tier sensitivity |
| 3 | `Qwen/Qwen3-8B` | small | Qwen dense | `2025-01` project anchor | Yes: `enable_thinking` | white-box | late small-tier temporal anchor |
| 4 | `Qwen/Qwen2.5-14B-Instruct` | medium | Qwen dense | `2023-10` project anchor | No dual-mode switch | white-box | early medium-tier temporal anchor |
| 5 | `Qwen/Qwen3-14B` | medium | Qwen dense | `2025-01` project anchor | Yes: `enable_thinking` | white-box | late medium-tier temporal anchor |
| 6 | `deepseek-ai/DeepSeek-V3-0324` | large | DeepSeek MoE | `2024-07` project anchor | Pinned 0324 snapshot has no clean documented ON/OFF toggle; later DeepSeek API exposes `thinking` / `deepseek-reasoner` | black-box or hosted open-weight | large-tier MoE architecture coverage |
| 7 | `gpt-5.4-2026-03-05` | large | OpenAI frontier | `2025-08-31` official | Yes: `reasoning_effort` / reasoning token support | black-box | large-tier SOTA anchor; same-cutoff falsification pair A |
| 8 | `claude-sonnet-4-6` | large | Anthropic frontier | `2025-08` reliable knowledge cutoff | Yes: adaptive / extended `thinking` | black-box | large-tier SOTA anchor; same-cutoff falsification pair A |
| 9 | `gpt-4.1-2025-04-14` | large | OpenAI non-reasoning | `2024-06-01` official | No reasoning step | black-box | optional same-cutoff falsification pair B with GLM |

## 3. Pairing table

| Pair | Design purpose | Why it matters |
|---|---|---|
| `Qwen2.5-7B` vs `Qwen3-8B` | small-tier temporal pair | primary white-box temporal contrast with near-matched size and shared family |
| `Qwen2.5-14B` vs `Qwen3-14B` | medium-tier temporal pair | same test at a higher capability tier |
| `Qwen2.5-7B` vs `Qwen2.5-14B` | size falsification at early cutoff | separates capability/size effects from cutoff effects |
| `Qwen3-8B` vs `Qwen3-14B` | size falsification at late cutoff | same as above for the later-era family |
| `gpt-5.4-2026-03-05` vs `claude-sonnet-4-6` | primary same-cutoff falsification pair | large-tier architecture/vendor noise baseline around Aug 2025 |
| `GLM-4-9B-0414` vs `gpt-4.1` | optional secondary same-cutoff falsification pair | mid-2024 control; useful if the paper can absorb a 9th model |
| `GLM-4-9B-0414` vs `Qwen2.5-7B` | cross-family small-tier sensitivity | tells you whether small-tier detector behavior generalizes beyond Qwen |
| `GLM-4-9B-0414` vs `Qwen3-8B` | cross-family late-vs-mid sensitivity | helps bound how much of the small-tier gap is family-specific |
| `DeepSeek-V3-0324` vs `gpt-5.4` / `claude-sonnet-4-6` | architecture coverage contrast | tests whether MoE behavior looks materially different from dense/closed frontier behavior |

## 4. Fleet size recommendation

- **Minimum fleet that satisfies A-D**: **8 models**
  - `Qwen2.5-7B`, `GLM-4-9B-0414`, `Qwen3-8B`, `Qwen2.5-14B`, `Qwen3-14B`, `DeepSeek-V3-0324`, `gpt-5.4-2026-03-05`, `claude-sonnet-4-6`
- **Ideal fleet**: **9 models**
  - add `gpt-4.1-2025-04-14`
- **Maximum before it becomes unmanageable**: **9 in the main paper**

Why I stop at 9:

- The 8-model core already identifies the main temporal, size, and architecture questions.
- The 9th slot buys one useful extra falsification control.
- The 10th slot is where this starts to look like a model survey instead of a benchmark with a design.

## 5. Thinking-mode answer

**Choose option (c)**.

Operational rule:

- `PCSG`, `Min-K++`: thinking OFF where possible.
- Behavioral detectors: default deployed mode.
- Sensitivity branch: ON/OFF on a small stratified subset for `Qwen3-14B`, `gpt-5.4-2026-03-05`, and `claude-sonnet-4-6`.

Why not the alternatives:

- Not `(a)`: too clean to be useful for deployed-system risk.
- Not `(b)`: ruins the logprob story.
- Not `(d)`: doubles compute and doubles exposition burden for too little incremental identification.

## 6. Cost estimate

Working assumption for API cost arithmetic:

- `3,200` cases
- roughly `300` input tokens and `50` output tokens per case
- cloud `A100/H100` for white-box `bf16/fp16`

Per full-detector pass:

- **8-model core**
  - white-box GPU (`5` models): about **$35-$55**
  - `gpt-5.4-2026-03-05`: about **$4.8**
  - `claude-sonnet-4-6`: about **$5.3**
  - `DeepSeek-V3` family slot: roughly **<$1** direct API pricing, but allow **$1-$3** if routed via a third party
  - total: about **$46-$66** per detector pass
- **9-model ideal**
  - add `gpt-4.1`: about **$3.2**
  - total: about **$49-$69** per detector pass

Portfolio-level budget:

- `K = 8` detectors, 8-model core: about **$368-$528**
- `K = 8` detectors, 9-model ideal: about **$392-$552**

Important caveat:

- If `gpt-5.4` or `claude-sonnet-4-6` run with reasoning/adaptive-thinking on behavioral detectors, actual billed output can rise materially because reasoning tokens are charged. I would budget a **25-75% uplift** on those two slots for the behavioral branch.

## Specific model calls

### Keep

- `Qwen2.5-7B-Instruct`
- `GLM-4-9B-0414`
- `Qwen3-8B`
- `Claude Sonnet 4.6`

### Add or restore

- `Qwen2.5-14B-Instruct`
- `Qwen3-14B`
- `gpt-5.4-2026-03-05`

### Drop

- `DeepSeek-V2.5`

### Hold out of the confirmatory core

- `Qwen3.5`
- `Yi`
- `Llama`
- `Mistral`

## Source-grounded notes

- `gpt-5.4-2026-03-05` is currently the strongest OpenAI credibility slot because OpenAI publishes an explicit **Aug 31, 2025** knowledge cutoff, reasoning-token support, and a pinned snapshot.
- `GPT-4.1` remains the cleanest extra falsification control because OpenAI publishes a **Jun 01, 2024** cutoff and exposes a pinned snapshot `gpt-4.1-2025-04-14`.
- Anthropic's model overview explicitly lists `claude-sonnet-4-6`, a reliable knowledge cutoff of **Aug 2025**, training data cutoff **Jan 2026**, and support for **extended/adaptive thinking**.
- Qwen's `Qwen3-8B` model card explicitly documents the `enable_thinking` switch and says the default is `True`.
- DeepSeek's current docs show that the API family now supports thinking mode through `deepseek-reasoner` or a `thinking` parameter, but that is not the same as having a pinned ON/OFF toggle on the dated `DeepSeek-V3-0324` snapshot. For confirmatory work, I would keep the pinned dated snapshot and treat DeepSeek thinking as exploratory unless a stable pinned interface is available.

## Sources

- OpenAI GPT-5.4 model docs: https://developers.openai.com/api/docs/models/gpt-5.4
- OpenAI GPT-4.1 model docs: https://developers.openai.com/api/docs/models/gpt-4.1
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic Sonnet 4.6 announcement: https://www.anthropic.com/news/claude-sonnet-4-6
- Anthropic extended thinking docs: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
- Qwen3-8B model card: https://huggingface.co/Qwen/Qwen3-8B
- Qwen3 blog: https://qwenlm.github.io/blog/qwen3/
- Qwen3.5-9B model card: https://huggingface.co/Qwen/Qwen3.5-9B
- Transformers GLM-4 docs: https://huggingface.co/docs/transformers/en/model_doc/glm4
- DeepSeek models and pricing: https://api-docs.deepseek.com/quick_start/pricing
- DeepSeek V2.5 release note: https://api-docs.deepseek.com/news/news0905
- DeepSeek-V3-0324 model card: https://huggingface.co/deepseek-ai/DeepSeek-V3-0324
