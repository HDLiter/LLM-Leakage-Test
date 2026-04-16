---
role: Stats / power and identification
session: R5A Fleet Review Round 2
thread_id: 019d944c-c761-7ce1-8480-a26d2f4dc7ec
model_reasoning_effort: xhigh
generated: 2026-04-15
---

# Stats Lens — Round 2

**Bottom line**

Round 2 turns this from a simple model ladder into a sparse design problem. A full `architecture × size tier × cutoff × thinking-mode` factorial is not statistically identified at 8-9 models, even with `3,200` cases per model. The right move is a **planned-contrast lattice**: two within-family temporal pairs, two within-family size controls, one same-cutoff cross-architecture falsification pair, and a small frontier stratum treated as external-validity anchors rather than core factorial cells.

---

## 1. Answers to Principles A-D

### Principle A — Thinking mode

- Important, but only as a **targeted crossover variable**, not a fleet-wide doubling.
- My recommendation is **option (e)**: operationally, this is **option (c)** for the main experiment plus a small **option (d)** subset.
- For confirmatory logprob detectors (`PCSG`, `Min-K++`), use **non-thinking / non-extended reasoning mode** only. The token distribution is the object of inference.
- For behavioral detectors (`CMMD`, extraction, `SR/FO`, `NoOp`, `EAD`, `ADG`), use the model's standard deployed mode only when that mode is snapshot-stable and comparable.
- Run an ON/OFF crossover only on models with a true within-checkpoint toggle: `Qwen3-8B`, `Qwen3-14B`, `GPT-5.1`, `Claude Sonnet 4.6`.
- Do **not** try to force `DeepSeek-V3-0324` into this factor. Current DeepSeek API docs expose a `thinking` switch on `deepseek-chat`, but the pinned `V3-0324` checkpoint is not a clean fleet-wide ON/OFF member.

### Principle B — Same-cutoff different-architecture falsification

- Essential. Round 1 was missing this.
- Minimum viable falsification pair: `GLM-4-9B-0414` vs `GPT-4.1`.
- Their official knowledge cutoffs are **June 30, 2024** and **June 1, 2024**. That is the cleanest same-cutoff pair currently available in the candidate set.
- If this pair shows a detector gap, that gap is architecture/vendor noise, not cutoff.
- There is no equally clean `~14B` same-cutoff Chinese-capable pair today. Do not pretend one exists.

### Principle C — Architecture coverage

- Important, but not every covered family needs to enter the confirmatory core symmetrically.
- Minimum worthwhile set remains the 5 families named in the brief:
  - `Qwen`
  - `GLM`
  - `DeepSeek`
  - `OpenAI`
  - `Anthropic`
- Extra families like `Yi`, `Llama`, or `Mistral` mostly create singleton cells with no matched role. From a stats lens, they worsen identification faster than they improve generality.

### Principle D — Multiple size tiers

- Worth it if limited to **2 white-box tiers** plus **1 descriptive frontier tier**.
- Small and medium tiers are statistically useful because they let you compare the temporal effect at two capacities.
- The large hosted tier should be treated as an **external-validity stratum**, not as part of the confirmatory factorial.
- Minimum internally useful white-box structure is 4 Qwen models across 2 tiers plus 2 small-tier non-Qwen controls.

---

## 2. Factorial Structure and Identification

### 2.1 Notional full factorial

If the user's principles are taken literally, the design is:

`architecture family (5) × size tier (3) × cutoff band (3) × thinking mode (2) = 90 cells`

With an 8- or 9-model fleet, occupancy is only `8/90` or `9/90`. That is not a factorial experiment. It is a set of singleton cells.

### 2.2 What is actually identified

At `N = 3,200` cases per model, the statistical units are **cases**, not models. Therefore:

- Pairwise model contrasts can have high precision even with 1 model per cell.
- Architecture/tier/cutoff main effects across cells do **not** become identified, because there is no model-level replication.

So the identifiable design is a **contrast design**, not a cell-means ANOVA.

### 2.3 Minimum replication rule

- For a single pre-registered pairwise contrast: **2 models are enough**, because cases supply the power.
- For a factor claim like "the temporal effect survives size tier": you need at least **2 independent contrasts** carrying that factor.
- For a true cell-based factorial claim: you need at least **2 models per occupied cell**, preferably **3**. At 90 cells, that would require dozens of models, not 8-9.

### 2.4 Power for pairwise contrasts

For a paired standardized detector score with `N=3,200` cases:

- If cross-model case-level correlation is `rho=0.5`, `SE ≈ 0.0177`
- 80% power, two-sided `alpha=.05`: MDE `≈ 0.050 SD`
- 80% power, Bonferroni over 6 confirmatory contrasts: MDE `≈ 0.062 SD`

If you split the same compute budget into ON/OFF halves (`N=1,600` per mode):

- Bonferroni MDE inflates to `≈ 0.087 SD` at `rho=0.5`

Conclusion: pairwise contrasts are well-powered. The bottleneck is **model design**, not case count.

---

## 3. Is the Multi-Tier Design Identified?

Yes, but only under a restricted claim set.

**Identified**

- Small-tier temporal effect: `Qwen2.5-7B -> Qwen3-8B`
- Medium-tier temporal effect: `Qwen2.5-14B -> Qwen3-14B`
- Size effect at early cutoff: `Qwen2.5-7B vs Qwen2.5-14B`
- Size effect at late cutoff: `Qwen3-8B vs Qwen3-14B`
- Same-cutoff architecture noise baseline: `GLM-4-9B-0414 vs GPT-4.1`

**Not identified**

- A general architecture main effect pooled across all families
- Architecture × tier interaction across all families
- Thinking × architecture × tier interaction
- Any "average cutoff effect" pooled across hosted frontier models

So the multi-tier design does **not** collapse with 2 models in the medium tier as long as you only use that tier for temporal and size contrasts. It **does** collapse if you try to estimate medium-tier architecture effects.

---

## 4. Revised Stats Fleet Recommendation

### 4.1 Minimum full fleet satisfying B + C + D: 8 models

This is the smallest fleet that gives:

- 2 size tiers
- 1 same-cutoff falsification pair
- the 5 architecture families named in the brief

| Model | Tier | Family | Cutoff | Reasoning mode | Access | Stats role |
|---|---|---|---|---|---|---|
| `Qwen2.5-7B-Instruct` | small | Qwen dense | `2023-10` project prior | no exposed toggle | white-box | early small anchor |
| `Qwen3-8B` | small | Qwen dense | `2025-01` project prior | `enable_thinking` | white-box | late small anchor |
| `Qwen2.5-14B-Instruct` | medium | Qwen dense | `2023-10` project prior | no exposed toggle | white-box | early medium anchor |
| `Qwen3-14B` | medium | Qwen dense | `2025-01` project prior | `enable_thinking` | white-box | late medium anchor |
| `GLM-4-9B-0414` | small | GLM dense | `2024-06-30` | no clean within-checkpoint toggle | white-box | same-cutoff architecture control A |
| `gpt-4.1-2025-04-14` | small/control | OpenAI | `2024-06-01` | non-reasoning model | black-box | same-cutoff architecture control B |
| `DeepSeek-V3-0324` | large | DeepSeek MoE | `2024-07` project prior | pinned checkpoint not a clean ON/OFF factor | black-box | MoE architecture anchor |
| `claude-sonnet-4-6` | large | Anthropic | reliable `Aug 2025`, training `Jan 2026` | extended/adaptive thinking | black-box | latest hosted anchor |

### 4.2 Ideal fleet: 9 models

Add `gpt-5.1-2025-11-13`.

Why:

- Adds a snapshot-able late OpenAI anchor
- Adds a true reasoning-effort control for the thinking-mode subset
- Lets `GPT-4.1` keep its same-cutoff falsification role instead of forcing one OpenAI slot to do two jobs

### 4.3 Maximum before it becomes unmanageable: 10 models

A 10th slot is only justified if it closes an existing contrast.

- Best use: `DeepSeek-V2.5` as an earlier MoE anchor
- Bad use: a singleton `Yi` / `Llama` / `Mistral` / `Qwen3.5` slot with no matched role

Past 10, this becomes a model zoo rather than an identified fleet.

---

## 5. Pairing Table

| Pair | Design purpose | Cleanly controlled factors | Residual confounds |
|---|---|---|---|
| `Qwen2.5-7B` vs `Qwen3-8B` | small-tier temporal effect | family/tokenizer, near size tier | `7B` vs `8B` not exact |
| `Qwen2.5-14B` vs `Qwen3-14B` | medium-tier temporal effect | family/tokenizer, exact nominal size | none beyond generation regime |
| `Qwen2.5-7B` vs `Qwen2.5-14B` | early size falsification | family, cutoff | size only |
| `Qwen3-8B` vs `Qwen3-14B` | late size falsification | family, cutoff | size only |
| `GLM-4-9B-0414` vs `GPT-4.1` | same-cutoff architecture falsification | cutoff band, approximate small-tier role | opaque parameter count on GPT |
| `DeepSeek-V3-0324` vs `Claude 4.6` | late hosted external validity | late hosted tier | cutoff mismatch, vendor, hidden architecture |
| `GPT-4.1` vs `GPT-5.1` | within-vendor temporal bridge, ideal 9-model fleet only | vendor | hidden size/architecture |

---

## 6. Thinking-Mode Recommendation

My recommendation is **option (e)**:

- `PCSG` / `Min-K++`: non-thinking or non-extended reasoning mode only
- Behavioral detectors: standard deployed mode, but **not** full ON/OFF doubling
- Add a preregistered ON/OFF crossover subset on:
  - `Qwen3-8B`
  - `Qwen3-14B`
  - `GPT-5.1`
  - `Claude Sonnet 4.6`
- Subset size can be `400-800` stratified cases rather than the full `3,200`

Why **not** option `(d)` fleet-wide ON/OFF?

- If budget is fixed, per-mode `N` halves and primary MDE worsens by about `sqrt(2)`
- If budget doubles, you gain power only for **within-model mode effects**, not for architecture/tier main effects
- `DeepSeek-V3-0324` is not a clean within-checkpoint ON/OFF member, so the factor is not harmonized across the fleet

---

## 7. Candidate-Specific Calls

- `Qwen3.5`: do **not** use it in the core fleet. The official Qwen site currently presents the first Qwen3.5 open-weight release as `Qwen3.5-397B-A17B`, i.e. a new flagship cell rather than a clean `8B/14B` replacement. It expands the design; it does not strengthen an existing contrast.
- `GPT-4.1`: yes, because it creates the best same-cutoff falsification pair in the entire candidate set.
- `GPT-5.4`: appendix/SOTA only. It improves headline recency, not identification.
- `DeepSeek-V3-0324` thinking mode: current DeepSeek API exposes a `thinking` switch on `deepseek-chat`, but the pinned `V3-0324` checkpoint is not a clean fleet-wide ON/OFF factor. Do not use it in the reasoning crossover.
- `Yi / Llama / Mistral`: no core slot unless one becomes a matched same-cutoff control.

---

## 8. Cost at `3,200 × K detectors`

For the 8-model minimum fleet, a reasonable per-detector-pass estimate is:

- White-box cloud `bf16/fp16` (`Qwen2.5-7B`, `Qwen2.5-14B`, `Qwen3-8B`, `Qwen3-14B`, `GLM-4-9B`): about `$35-50`
- Hosted/API models (`GPT-4.1`, `DeepSeek-V3-0324`, `Claude 4.6`): about `$9-12`
- Total: about **`$45-62 per detector`**

For the 9-model ideal fleet, adding `GPT-5.1` increases a full pass by about **`$2.8`** under the `300 input + 50 output` token assumption:

- Total: about **`$48-65 per detector`**

At `7-9` detectors, that is roughly:

- **Minimum 8-model fleet:** `~$315-560`
- **Ideal 9-model fleet:** `~$340-585`

That remains well below the cost of a genuinely balanced factorial.

---

## 9. Final Stats Recommendation

- Minimum identified full fleet: **8 models**
- Ideal fleet: **9 models**
- Confirmatory analysis unit: **planned pair contrasts**, not omnibus factorial coefficients
- Hard no: a full `architecture × tier × cutoff × thinking` model fit
- Thinking mode: **targeted crossover**, not fleet-wide doubling
- Large hosted tier: **external-validity stratum**, not the main identification engine

Sources:

- Internal project survey: `docs/CMMD_MODEL_FLEET_SURVEY.md`
- OpenAI GPT-5.1 model docs: https://developers.openai.com/api/docs/models/gpt-5.1
- OpenAI GPT-5.4 model docs: https://developers.openai.com/api/docs/models/gpt-5.4
- OpenAI GPT-4.1 model docs: https://developers.openai.com/api/docs/models/gpt-4.1
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic release notes: https://platform.claude.com/docs/en/release-notes/overview
- DeepSeek create chat completion: https://api-docs.deepseek.com/api/create-chat-completion
- DeepSeek-V3-0324 release note: https://api-docs.deepseek.com/zh-cn/news/news250325
- Qwen3-8B model card: https://huggingface.co/Qwen/Qwen3-8B
- Qwen3-14B model card: https://huggingface.co/Qwen/Qwen3-14B
- Qwen2.5-14B-Instruct model card: https://huggingface.co/Qwen/Qwen2.5-14B-Instruct
- Qwen official site: https://qwen.ai/
