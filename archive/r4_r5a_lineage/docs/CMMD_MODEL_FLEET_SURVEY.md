# CMMD Model Fleet Survey — FinMem-Bench R5 Pre-commit

**Purpose.** Cross-Model Memorization Disagreement (CMMD; Roy & Roy 2026) requires a fleet of Chinese-capable LLMs with genuinely non-overlapping pre-training cutoffs. This document surveys candidates, recommends a 6-model final fleet, and flags reproducibility hazards for the R5 pre-commit.

**Task constraints.** Chinese financial news (CLS telegraph) sentiment / next-period label. Short dense text (50-300 Chinese chars), heavy domain jargon. Need genuine reading capability, not just token support.

**Date of survey.** 2026-04-13.

---

## 1. Executive Summary — Final Recommended Fleet (6 models)

| # | Model | Cutoff | Access | Rationale (one line) |
|---|---|---|---|---|
| 1 | **Qwen 2.5-7B-Instruct** | 2023-10 | Local vLLM (already deployed) + OpenRouter `qwen/qwen-2.5-7b-instruct` | Oldest anchor, white-box logprobs, native Chinese, already in project infra |
| 2 | **DeepSeek-V2.5** (chat-v2.5) | 2024-03–05 | OpenRouter `deepseek/deepseek-chat-v2.5` | Mid-2024 anchor, native Chinese, MoE white-box possible via HF |
| 3 | **GLM-4-9B-0414** (ZhipuAI) | 2024-06 | HF local vLLM + OpenRouter `thudm/glm-4-9b` | Third Chinese-native family, mid-2024, logprobs, diversifies beyond Qwen/DeepSeek |
| 4 | **DeepSeek-V3 (chat-v3-0324)** | 2024-07 | OpenRouter `deepseek/deepseek-chat-v3-0324` + DeepSeek API (user already has) | Late-2024 anchor, strong Chinese finance domain, project's baseline model |
| 5 | **Qwen3-14B** or **Qwen3-32B** | 2025-01 | OpenRouter `qwen/qwen3-14b` or `qwen/qwen3-32b` + HF local | Early-2025 anchor, newest stable Qwen, full open weights |
| 6 | **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) | 2025-01 (reliable) / 2025-07 (extended) | OpenRouter `anthropic/claude-sonnet-4.5` | Commercial diversity, non-Chinese-vendor perspective for CMMD agreement signal |

**Why this fleet:**
- **Cutoff span:** 2023-10 → 2025-07 ≈ **21 months of temporal spread** → CLS news from 2024-H2 is memorization-possible for some, impossible for others.
- **Chinese strength:** 5 of 6 are Chinese-native (Qwen, DeepSeek, GLM, DeepSeek, Qwen3); Claude 4.5 is the strongest non-Chinese-vendor on Chinese benchmarks.
- **White-box members:** Qwen 2.5-7B, GLM-4-9B, Qwen3-14B are fully open weights → logprobs available for parallel Min-K% / MIA runs, satisfying CMMD's "logprob-optional bonus."
- **Commercial/hosted members:** DeepSeek-V3 and Claude Sonnet 4.5 via OpenRouter → API diversity, cost-bounded.
- **Reproducibility:** Every slug is either a pinned `-0324` / `-0414` / `-20250929` checkpoint or a frozen open-weight HF repo. No `gpt-4o-latest`-style moving targets.

---

## 2. Cutoff Timeline Diagram

```
          2023-Q4  2024-Q1  2024-Q2  2024-Q3  2024-Q4  2025-Q1  2025-Q2  2025-Q3
          --------|--------|--------|--------|--------|--------|--------|-------
Qwen 2.5    [===]                                                               (Oct 2023)
GPT-4o      [===]                                                               (Oct 2023)
GLM-4-9B             [===================]                                      (~Jun 2024)
Claude 3.5s             [===]                                                   (Apr 2024)
DeepSeek-V2.5          [======]                                                 (~Mar–May 2024)
GPT-4.1                         [===]                                           (Jun 2024)
DeepSeek-V3                        [===]                                        (Jul 2024)
DeepSeek-R1                        [===]                                        (Jul 2024)
Claude 3.5h                        [===]                                        (Jul 2024)
InternLM3                                 [===]                                 (~Oct–Dec 2024)
Qwen3 14B/32B                                [===]                              (Jan 2025)
Gemini 2.5 Pro                               [===]                              (Jan 2025)
Claude Opus 4 / 4.5                              [===]                          (Mar 2025)
Claude Sonnet 4.5                                     [=============]           (Jan → Jul 2025)
```

**Usable CMMD contrast windows:**
- **Pre-2024 events** → memorization-possible for all 6 → CMMD signal is the "control" regime.
- **2024-Q1..Q2 events** → Qwen 2.5 *cannot* memorize (cutoff 2023-10). Other 5 can. Disagreement here isolates Qwen 2.5's non-memorized inference.
- **2024-Q3..Q4 events** → Qwen 2.5 and Claude 3.5 Sonnet cannot. GLM-4, DeepSeek-V3, and later models can. Richest contrast zone.
- **2025-Q1 events** → only Qwen3 and Claude 4.5 can memorize. Strongest temporal anchor.
- **Post-2025-Q3 events** → no model in fleet has seen them → CMMD acts as a pure reasoning check.

---

## 3. Full Survey Table (sorted by cutoff)

Legend: **C-cap** = Chinese capability (S=strong native, M=moderate multilingual, W=weak). **OR** = OpenRouter. **Conf** = cutoff confidence (H/M/L).

| Model | Family | Release | Cutoff | Conf | C-cap | OR slug | HF+vLLM | Logprob | Params | License | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-3.5-turbo | OpenAI | 2022-11 | 2021-09 | H | M | `openai/gpt-3.5-turbo` | No | No | ? | proprietary | Too old, but useful as pre-2023 anchor if needed |
| Qwen 1.5-7B | Alibaba | 2024-02 | ~2023-09 | M | S | `qwen/qwen-7b-chat` | Yes | Yes | 7B | Tongyi Qianwen | Superseded by 2.5, avoid |
| Yi-34B | 01.AI | 2023-11 | ~2023-06 | M | S | limited | Yes | Yes | 34B | Yi license | Good Chinese, but cutoff uncertain |
| **Qwen 2.5-7B-Instruct** | Alibaba | 2024-09 | **2023-10** | M (community) | S | `qwen/qwen-2.5-7b-instruct` | **Yes (project local)** | Yes | 7B | Apache 2.0 | **FLEET #1.** Native Chinese, 18+ trillion token pre-train |
| Qwen 2.5-72B-Instruct | Alibaba | 2024-09 | 2023-10 | M | S | `qwen/qwen-2.5-72b-instruct` | Yes (heavy) | Yes | 72B | Qwen license (commercial OK) | Same cutoff as 7B, redundant |
| GPT-4o (2024-05) | OpenAI | 2024-05 | 2023-10 | H | M–S | `openai/gpt-4o-2024-05-13` | No | No | ? | proprietary | Silent-update landmine — use pinned `-2024-05-13` |
| ChatGLM3-6B | THUDM | 2023-10 | ~2023-06 | M | S | none direct | Yes | Yes | 6B | ChatGLM license | Superseded, avoid |
| Claude 3.5 Sonnet (original) | Anthropic | 2024-06 | 2024-04 | H | M | `anthropic/claude-3.5-sonnet:beta` / `claude-3.5-sonnet-20240620` | No | No | ? | proprietary | Pinned checkpoint OK |
| Qwen2-7B | Alibaba | 2024-06 | ~2024-03 | L | S | `qwen/qwen-2-7b-instruct` | Yes | Yes | 7B | Apache 2.0 | Superseded by 2.5 |
| DeepSeek-V2.5 | DeepSeek | 2024-09 | ~2024-03–05 | M | S | `deepseek/deepseek-chat-v2.5` | Yes (236B MoE, heavy) | Yes if local | 236B (21B active) | DeepSeek LM license | **FLEET #2.** Strong finance Chinese |
| Claude 3.5 Haiku | Anthropic | 2024-11 | 2024-07 | H | M | `anthropic/claude-3.5-haiku` | No | No | ? | proprietary | Cheap alt, OK for commercial slot |
| Baichuan2-13B | Baichuan | 2023-09 | ~2023-06 | L | S | rare | Yes | Yes | 13B | Baichuan license | Old, Baichuan-M1 never open-sourced; skip |
| **GLM-4-9B-0414** | Zhipu/THUDM | 2025-04-25 | **2024-06-30** | H | S | `thudm/glm-4-9b` (original) | **Yes** | Yes | 9B | MIT (check) | **FLEET #3.** Official cutoff stated. The `0414` variant is a refresh — use exact HF snapshot |
| GPT-4.1 (2025-04-14) | OpenAI | 2025-04-14 | 2024-06 | H | M | `openai/gpt-4.1` | No | No | ? | proprietary | Commercial alternative to DeepSeek-V3 |
| **DeepSeek-Chat-V3-0324** | DeepSeek | 2025-03-24 | **2024-07** | H (extracted system prompt) | S | `deepseek/deepseek-chat-v3-0324` | Yes (671B MoE, 2×8×H100 minimum) | Yes if local | 671B (37B active) | DeepSeek LM license | **FLEET #4.** User already has DeepSeek API access |
| DeepSeek-R1 | DeepSeek | 2025-01-20 | 2024-07 | H | S | `deepseek/deepseek-r1` | Yes (huge) | Yes | 671B | MIT | Same cutoff as V3, reasoning overhead unnecessary for CMMD |
| InternLM3-8B-Instruct | Shanghai AI Lab | 2025-01-15 | ~2024-10 (unstated) | L | S | limited | Yes | Yes | 8B | Apache 2.0 | Backup if GLM-4-9B fails |
| MiniCPM3-4B | OpenBMB | 2024-09-05 | ~2024-06 | L | S | rare | Yes | Yes | 4B | MiniCPM license | Small, cheap, but cutoff undocumented |
| Yi-1.5-34B-Chat | 01.AI | 2024-05 | ~2024-03 | L | S | limited | Yes | Yes | 34B | Yi license | 01.AI gone quiet; avoid for reproducibility |
| **Qwen3-14B** | Alibaba | 2025-04-29 | **2025-01** | M (community, matches tech report) | S | `qwen/qwen3-14b` | **Yes** | Yes | 14B | Apache 2.0 | **FLEET #5.** Best Chinese open-weight with early-2025 cutoff |
| Qwen3-32B | Alibaba | 2025-04-29 | 2025-01 | M | S | `qwen/qwen3-32b` | Yes | Yes | 32B | Apache 2.0 | Upgrade of #5 if GPU budget allows |
| Qwen3-235B-A22B | Alibaba | 2025-04-29 | ~2025-03 | M | S | `qwen/qwen3-235b-a22b` | Yes (heavy) | Yes | 235B MoE | Apache 2.0 | Too heavy for local, OR only |
| Gemini 2.5 Pro | Google | 2025-03 | 2025-01 | H | M–S | `google/gemini-2.5-pro` | No | No (limited) | ? | proprietary | Good backup commercial model |
| Claude Opus 4 | Anthropic | 2025-05-22 | 2025-03 | H | M | `anthropic/claude-opus-4` | No | No | ? | proprietary | Pinned OK |
| **Claude Sonnet 4.5** (`20250929`) | Anthropic | 2025-09-29 | **2025-01 reliable / 2025-07 extended** | H | M | `anthropic/claude-sonnet-4.5` | No | No | ? | proprietary | **FLEET #6.** Commercial non-Chinese-vendor diversity |
| Claude Opus 4.5 | Anthropic | 2025-11-24 | 2025-03 | H | M | `anthropic/claude-opus-4.5` | No | No | ? | proprietary | Overkill for this task; cost prohibitive |
| Doubao-Pro / ERNIE 4.0 / Hunyuan | ByteDance / Baidu / Tencent | various | **undocumented** | L | S | not on OR | No | No | ? | proprietary | Cutoffs unpublished → unusable for CMMD |
| Mistral / Mixtral | Mistral AI | various | various | H | **W** | OR available | Yes | Yes | 7B–141B | Apache 2.0 | Chinese too weak for CLS telegraph; skip |

---

## 4. Access Cost Estimate

**Budget: 3,200 cases × 6 models = 19,200 total calls.** Assume avg 300 input tokens (CLS item + instruction) + 50 output tokens per call.

Per-model cost via OpenRouter (using pricing snapshot from earlier in doc):

| Model | Input $/M | Output $/M | Per-call $ | 3,200 calls $ |
|---|---|---|---|---|
| Qwen 2.5-7B (local vLLM) | 0 | 0 | 0 | **$0** (GPU time only) |
| DeepSeek-V2.5 | ~$0.14 | ~$0.28 | ~$0.000056 | **$0.18** |
| GLM-4-9B (local vLLM) | 0 | 0 | 0 | **$0** (GPU time only) |
| DeepSeek-V3-0324 | $0.20 | $0.77 | ~$0.0001 | **$0.32** |
| Qwen3-14B (local vLLM) | 0 | 0 | 0 | **$0** (GPU time only) |
| Claude Sonnet 4.5 | $3.00 | $15.00 | ~$0.0018 | **$5.76** |

**Total OpenRouter cost: ~$6.30** for 3,200 cases × 6 models. Essentially free — Claude dominates the bill. If Claude Sonnet 4.5 is swapped for Claude 3.5 Sonnet (cheaper at $3/$15 same, but smaller context), cost is identical. If Gemini 2.5 Pro is substituted, cost ~$4-6 total.

**Hidden compute cost:** three local white-box models × 3,200 cases. At ~3 s/case on a single A100 for the 7–14B tier, that's ≈ 3 × 3,200 × 3 s ≈ **8 GPU-hours**, fits easily inside project GPU budget.

**Recommend $30 Claude budget headroom** for re-runs and ablations.

---

## 5. Known Risks and Landmines

### 5.1 Silent-update landmines (critical)
- **`gpt-4o`, `gpt-4o-latest`, `gpt-4-turbo-preview`** have all been silently re-pointed to newer checkpoints in the past. **Never use unpinned slugs.** Always pin to `gpt-4o-2024-05-13`, `gpt-4o-2024-08-06`, etc.
- **`claude-3.5-sonnet` (v1 vs v2)** — the "new Claude 3.5 Sonnet" in 2024-10 has the same marketing name but a later cutoff. Use `claude-3-5-sonnet-20240620` vs `claude-3-5-sonnet-20241022` explicitly.
- **`deepseek-chat`** on DeepSeek's own API silently moved from V2 → V2.5 → V3 → V3.1 → V3.2 over 2024-2025. If the user calls `deepseek-chat` today, they get V3.2 (2025-09 cutoff). **Project must call pinned `deepseek-chat-v3-0324` via OpenRouter, not `deepseek-chat` via DeepSeek direct.**
- **Qwen on DashScope** — `qwen-plus` / `qwen-max` are also updated silently. Prefer open-weight HF snapshots for Qwen.

### 5.2 Financial-prompt refusal
- Claude Sonnet/Opus has historically declined explicit "predict stock price direction" prompts. Mitigation: frame as sentiment classification (which is already our prompt schema), not forecasting. **Verify on 10 pilot cases before freezing.**
- GPT-4o / GPT-4.1 sometimes add "not financial advice" disclaimers that poison structured output parsing. Mitigation: use `response_format=json_object`.
- Gemini 2.5 Pro occasionally refuses Chinese financial content citing "regulated industries." Same mitigation.

### 5.3 Cutoff-documentation confidence
- Qwen family cutoffs are **community-inferred**, not official. The Qwen3 tech report (2505.09388) is the most authoritative source, but never states an explicit ISO date.
- DeepSeek cutoffs come from **extracted system prompts** (Knostic 2025), not official documentation. Treat as medium-confidence.
- GLM-4-9B-0414 is the one model with an **explicit official cutoff** (2024-06-30). Anchor the fleet around it.
- Commercial models (GPT/Claude/Gemini) publish cutoffs in model cards, which is high-confidence, **but the actual training-data distribution tail can extend later** (see "All Leaks Count" paper in project library).

### 5.4 Chinese financial domain weakness
- Even Chinese-native models may *not* have seen CLS telegraph (paid, real-time wire). Training corpora typically include Wikipedia, Common Crawl, and news aggregators — not CLS. This is actually **good** for CMMD's null hypothesis: if a model "knows" a CLS-exclusive event, that's a strong memorization signal.
- Qwen 2.5 pre-training explicitly mentions Chinese financial corpus ingestion ("multilingual finance documents"). Treat Qwen family as **highest memorization risk** and weight CMMD accordingly.

### 5.5 OpenRouter routing variance
- OpenRouter routes to multiple providers per slug (e.g., `qwen/qwen-2.5-72b-instruct` may go to Together, Fireworks, Novita, etc.). **Different backends may have different quantization → different logits.** Set `provider.order` explicitly in OpenRouter requests, or pin one provider.
- For white-box members, **prefer local vLLM over OpenRouter** to eliminate this variance entirely.

---

## 6. R5 Pre-commit Freeze (copy into pre-registration)

**The CMMD fleet is frozen at R5 pre-commit as follows.** Any post-commit changes require an amendment.

| Slot | Model | Access path | Exact identifier |
|---|---|---|---|
| 1 | Qwen 2.5-7B-Instruct | Local vLLM (Docker) | HF: `Qwen/Qwen2.5-7B-Instruct`, commit SHA **TO-PIN-AT-R5** |
| 2 | DeepSeek-V2.5 | OpenRouter | `deepseek/deepseek-chat-v2.5` |
| 3 | GLM-4-9B-0414 | Local vLLM (Docker) | HF: `zai-org/GLM-4-9B-0414`, commit SHA **TO-PIN-AT-R5** |
| 4 | DeepSeek-V3 (2024-07 cutoff) | OpenRouter | `deepseek/deepseek-chat-v3-0324` |
| 5 | Qwen3-14B | Local vLLM (Docker) | HF: `Qwen/Qwen3-14B`, commit SHA **TO-PIN-AT-R5** |
| 6 | Claude Sonnet 4.5 | OpenRouter | `anthropic/claude-sonnet-4.5` → resolved to `claude-sonnet-4-5-20250929` |

**Generation parameters (all models):** `temperature=0.0`, `top_p=1.0`, `max_tokens=200`, `seed=20260501`, `response_format=json_object` for API models. Retry on JSON parse failure up to 3x with identical parameters (determinism checks).

**Provider pinning:** OpenRouter requests must include `provider={"order": ["Fireworks", "Together"]}` (or equivalent single-provider pin) and `provider.allow_fallbacks=false` to avoid quantization variance.

**Reproducibility artifacts to preserve:** (a) exact HF commit SHAs for all 3 local models, (b) OpenRouter request headers including resolved provider, (c) sha256 of every raw JSON response.

---

## 7. Fallback Fleet (if preferred fleet has availability issues)

Ordered by substitutability:

| If unavailable | Replacement | Trade-off |
|---|---|---|
| DeepSeek-V2.5 | **Yi-1.5-34B-Chat** (HF local) | Loses reproducibility (01.AI quiet); weaker finance domain |
| GLM-4-9B-0414 | **InternLM3-8B-Instruct** (HF local) | Cutoff less documented (~2024-10 unofficial) |
| DeepSeek-V3-0324 | **GPT-4.1 (`2025-04-14`)** (OR) | Same cutoff (2024-06), commercial non-Chinese vendor |
| Qwen3-14B | **Qwen3-30B-A3B-Instruct-2507** (OR) | Later cutoff (~2025-03), MoE compute-cheap |
| Claude Sonnet 4.5 | **Gemini 2.5 Pro** (OR) | Cheaper, same cutoff (2025-01), Google diversity |

**Minimal 4-model emergency fleet** (if budget/compute collapses): Qwen 2.5-7B + GLM-4-9B + DeepSeek-V3-0324 + Qwen3-14B. All Chinese-native, all have logprobs, total API cost < $1, cutoff span 2023-10 → 2025-01 (15 months).

---

## 8. Sources (key references)

- Qwen 2.5 cutoff discussion: https://github.com/QwenLM/Qwen3/discussions/1093
- DeepSeek cutoff extraction: https://www.knostic.ai/blog/exposing-deepseek-system-prompts
- DeepSeek-V3 tech report: https://arxiv.org/abs/2412.19437
- Qwen3 tech report: https://arxiv.org/pdf/2505.09388
- GLM-4-9B-0414 model card: https://huggingface.co/zai-org/GLM-4-9B-0414
- InternLM3 announcement: https://x.com/intern_lm/status/1879513004011896969
- Claude Sonnet 4.5 model card: https://www.prompthub.us/models/claude-sonnet-4-5
- Claude 3.5 Sonnet model card addendum: https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf
- GPT-4.1 release: https://openai.com/index/gpt-4-1/
- GPT-4o model card: https://platform.openai.com/docs/models/gpt-4o
- Gemini 2.5 Pro docs: https://ai.google.dev/gemini-api/docs/models
- OpenRouter Qwen catalog: https://openrouter.ai/qwen/
- OpenRouter DeepSeek catalog: https://openrouter.ai/deepseek
- MiniCPM3-4B release: https://www.marktechpost.com/2024/09/11/minicpm3-4b-released-by-openbmb-...
- Roy & Roy 2026 CMMD detector: arxiv 2603.26797 (in project `related papers/`)
