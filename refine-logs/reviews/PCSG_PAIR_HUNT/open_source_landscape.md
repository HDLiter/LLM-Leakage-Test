# Open-Source LLM Landscape for PCSG Pair Selection

**Date:** 2026-04-26
**Author:** Web research scan (Claude Opus 4.7)
**Scope:** Find PCSG-eligible "early vs late cutoff" pairs that share tokenizer + density type + paradigm, suitable to repair the R5A fleet's missing within-pair cutoff contrast.
**Constraint reminder:** PCSG L1=tokenizer match (HARD), L2=same density (HARD), L3=different cutoff (HARD), L4=same paradigm (medium).

---

## 1. Executive summary

The current R5A fleet's failure mode is unambiguous: **within every "tokenizer-matched" pair, both members share the same training-data cutoff** (Qwen2.5 7B/14B = 2023-10; Qwen3 8B/14B = 2025-01). The only intra-fleet capacity-vs-cutoff confound that could be cleanly disentangled is **across the Qwen2.5 ↔ Qwen3 family boundary (different tokenizer; both Qwen2Tokenizer class but with extra `<think>` tokens at IDs 151667-151668 in Qwen3)**.

Three viable PCSG repair strategies emerge from this scan, in descending preference:

1. **(BEST, FREE) Add Qwen2-7B-Instruct-AWQ → Qwen2.5-7B-Instruct-AWQ within-family pair.** Same `Qwen2Tokenizer` (vocab 151643 + 22 added tokens up to ID 151664, identical IDs), same dense topology, same instruct paradigm, both have official Alibaba AWQ-INT4 checkpoints. Cutoff gap is ~9-12 months by community consensus (Qwen2 ≈ end-2023 marketing, Qwen2.5 = "end of 2023" per HaoooWang's curated table — see caveat below). However the cutoff gap is **smaller than ideal** and partially overlapping; needs empirical probe.
2. **(STRONG, gated) Llama-3-8B vs Llama-3-70B as a within-Llama-3 pair.** Meta's official model card explicitly states **8B cutoff = March 2023, 70B cutoff = December 2023** — a clean 9-month gap inside the SAME tokenizer (tiktoken-based, vocab 128k). Risks: (a) Llama gating; (b) parameter count differs (7B-vs-7B not satisfied — comparable to fleet's existing 7B/14B); (c) AWQ is community-only (hugging-quants), not Meta-official; (d) Chinese-language coverage weaker than the Qwen family — concerning for the financial-news pilot.
3. **(NEW LINEAGE) Replace fleet with InternLM2-7B → InternLM2.5-7B pair.** Same `InternLM2Tokenizer` (verified — both use vocab tip at token 92543 `<|im_start|>`), same dense, same family, both 7B. Gap: InternLM2 released Jan 2024 vs InternLM2.5 released Jul 2024. **CAUTION: the cutoff dates are NOT publicly stated** — must be empirically probed before use. If they actually share data, this collapses.

**Top 3 caveats parent must hear:**

- **C1 — Cutoff dates are mostly unverified across the open-source landscape.** Even the much-cited HaoooWang/llm-knowledge-cutoff-dates GitHub list is "community consensus from model cards / forums," not vendor-grade. For Qwen2/2.5/3 the *vendor-stated* cutoff is essentially absent from blog posts and tech reports; vendors prefer to dodge the question. Only Meta's Llama family states cutoffs in the model cards.
- **C2 — "Same tokenizer" is fragile across version bumps.** Qwen3 adds two new tokens (`<think>` 151667, `</think>` 151668) on top of Qwen2.5's 22-added-token block. GLM-4.5/4.6 add ~22 new tokens on top of GLM-4-9B's 14. Yi-1.5 has tokenizer additions vs Yi 1.0 (community-reported). For paired logprob comparison this matters: any sequence containing only "core" vocab IDs (≤151342 for GLM, ≤151645 for Qwen) is fully alignable; sequences with extension tokens diverge. Operationally we should restrict probes to the intersection vocabulary.
- **C3 — The MoE confound is unavoidable in the GLM and DeepSeek modern lineages.** GLM-4-9B is the *last dense* in the GLM-4 series; GLM-4.5/4.6/4.7 are all MoE. DeepSeek-V2/V3 are MoE. Mixing dense GLM-4-9B with MoE GLM-4.5-Air to hunt cutoff differential is L2-violating and PCSG-disqualified.

---

## 2. Methodology and sources

**Search strategy:**
- Direct WebFetch of `https://huggingface.co/<repo>/raw/main/tokenizer_config.json` to verify tokenizer class + special-token IDs + vocab range. This is the most reliable evidence of tokenizer identity short of comparing `tokenizer.json` SHA-256.
- Vendor blog posts and HF model cards for cutoff and density.
- Cross-checked HaoooWang/llm-knowledge-cutoff-dates community list as a fallback when vendor docs are silent.
- WebSearch for tertiary signals (Hacker News, Reddit-tier blogs, vendor GitHub discussions).

**Limitations:**
- Llama tokenizer files (meta-llama org) are gated behind license click-through — could not WebFetch tokenizer_config.json directly. Llama tokenizer details below are sourced from the public model card on llama.com and from community summaries, not from a raw HF JSON read.
- GLM-4.5 / 4.6 don't publish cutoff dates in their HF cards or arxiv 2508.06471 abstract; only third-party "list of LLM cutoffs" sites quote dates, which we mark as low confidence.
- We did NOT verify SHA-256 of tokenizer.json files — only inspected tokenizer_config.json contents. Two models can have identical tokenizer_config.json but slightly different merges in tokenizer.json (rare but possible).

---

## 3. Family-by-family analysis

### 3.1 Qwen family

**Lineage timeline:**

| Version | Release | Tokenizer class | Vocab core / added max | Density | Sizes (dense) | Cutoff |
|---|---|---|---|---|---|---|
| Qwen-7B / 14B / 72B | 2023-09 | `QWenTokenizer` (custom, tiktoken-based, ~152K BPE, different name) | n/a | dense | 7B, 14B, 72B | "over 2.4T tokens" — date not stated; arxiv 2309.16609 |
| Qwen1.5 | 2024-02 | `Qwen2Tokenizer` (renamed) | 151643 / 151645 | dense (incl. 14B-MoE-A2.7B) | 0.5/1.8/4/7/14/32/72 + MoE 14B-A2.7 | ~late 2023 (community) |
| Qwen2 | 2024-06 | `Qwen2Tokenizer` | 151643 / 151645 (≤151645) | dense + 1 MoE | 0.5/1.5/7/57B-A14B/72 | "end of 2023" per community list |
| Qwen2.5 | 2024-09 | `Qwen2Tokenizer` | 151643 / 151664 (added vision/tool/FIM tokens) | dense | 0.5/1.5/3/7/14/32/72 | "end of 2023" per community list; one Codex/Coder variant inherits Sept 2024 |
| Qwen3 | 2025-04 | `Qwen2Tokenizer` (same class!) | 151643 / 151668 (adds `<think>`, `</think>` at 151667-151668) | dense + MoE | 0.6/1.7/4/8/14/32 + 30B-A3B + 235B-A22B | unknown — vendor declines; user reports dec-2024 events |
| QwQ-32B | 2024-11 | `Qwen2Tokenizer` | shares Qwen2.5 base | dense | 32B only | 2024-11-28 per community |

**Tokenizer continuity (verified by raw tokenizer_config.json reads):**

- Qwen-7B uses **`QWenTokenizer` (different class, NOT compatible)** — first-generation Qwen broke backward compat.
- Qwen1.5-7B-Chat: `Qwen2Tokenizer`, model_max_length 32768, eos `<|endoftext|>` 151643, added [`<|im_start|>` 151644, `<|im_end|>` 151645].
- Qwen2-7B: `Qwen2Tokenizer`, model_max_length 32768, eos `<|endoftext|>` 151643, same three special tokens 151643-151645.
- Qwen2.5-7B: `Qwen2Tokenizer`, model_max_length 131072, eos `<|endoftext|>` 151643, added tokens up to 151664 (`<|file_sep|>`).
- Qwen2.5-14B: `Qwen2Tokenizer`, identical max-token-id 151664.
- Qwen3-8B: `Qwen2Tokenizer`, eos shifted to `<|im_end|>` 151645 (chat template change), max-id 151668 (adds `<think>` 151667, `</think>` 151668).
- Qwen3-14B: `Qwen2Tokenizer`, max-id 151668.

So **Qwen1.5 ↔ Qwen2 share tokenizer exactly (vocab 151645)**, **Qwen2 → Qwen2.5 added 19 tokens (vision/tool/FIM, 151646-151664)**, **Qwen2.5 → Qwen3 added 4 more (151665 `<tool_response>`, 151666 `</tool_response>`, 151667 `<think>`, 151668 `</think>`) and changed default eos token from `<|endoftext|>` to `<|im_end|>`**. For PCSG: as long as probe sequences don't trigger any of the added tokens, paired logprob computation across all four versions is alignable.

**AWQ availability:** Qwen1.5 has official AWQ for 0.5/1.8/4/7/14/32/72B Chat. Qwen2 has official AWQ for 0.5/1.5/7/72 Instruct. Qwen2.5 has official AWQ for 0.5/1.5/3/7/14/32/72 Instruct. Qwen3 has official AWQ for 0.6/1.7/4/8/14/32. **All Alibaba-official, not community.**

**PCSG eligibility verdict:**

| Pair | L1 tok | L2 dens | L3 cutoff Δ | L4 paradigm | Verdict |
|---|---|---|---|---|---|
| Qwen2.5-7B ↔ Qwen2.5-14B | ✓ | ✓ | ✗ same | ✓ | invalid (current fleet's flaw) |
| Qwen3-8B ↔ Qwen3-14B | ✓ | ✓ | ✗ same | ✓ | invalid (current fleet's flaw) |
| Qwen2.5-7B ↔ Qwen3-8B | partial (Δ4 tokens, +eos change) | ✓ | likely ✓ (>12 mo) | ✓ | **conditionally valid** if probes avoid added tokens |
| Qwen2-7B ↔ Qwen2.5-7B | ✓ (Δ19 tokens but lower IDs unchanged) | ✓ | small (~3-9 mo, both in late-2023) | ✓ | weak — cutoff gap small |
| Qwen1.5-7B ↔ Qwen2.5-7B | ✓ (Δ19 tokens; Qwen1.5 stops at 151645) | ✓ | very small (both ~late 2023) | ✓ | invalid — cutoff overlap |

### 3.2 GLM family

**Lineage timeline:**

| Version | Release | Tokenizer class | Vocab core / added max | Density | Sizes | Cutoff |
|---|---|---|---|---|---|---|
| ChatGLM-6B | 2023-03 | `ChatGLMTokenizer` (~130K) | distinct vocab base | dense | 6B | "early 2023" |
| ChatGLM2-6B | 2023-06 | `ChatGLMTokenizer` (~65K, NEW vocab) | distinct vocab base | dense | 6B | early-2023 |
| ChatGLM3-6B | 2023-10 | `ChatGLMTokenizer` (~65K) | added [gMASK] sop at 64790-64792 | dense | 6B | mid-2023 |
| GLM-4-9B | 2024-06 | `ChatGLM4Tokenizer` (NEW vocab! ~151K) | 151329 / 151342 (14 added tokens) | dense | 9B (chat, chat-1M, base, V) | "GLM-4(0520) data" per Zhipu, no exact date |
| GLM-4-9B-0414 | 2025-04 | `PreTrainedTokenizer`, ChatGLM4 base | 151329 / 151342 (identical to GLM-4-9B!) | dense | 9B | undisclosed |
| GLM-4.5 / 4.5-Air | 2025-07 | `PreTrainedTokenizer` (GLM4) | 151329 / 151364 (extends with `<think>`, tool, audio) | **MoE** | 355B-A32B / 106B-A12B | "mid-late 2024" (3rd party) |
| GLM-4.6 | 2025-09 | `PreTrainedTokenizer` (GLM4) | 151329 / 151364 | **MoE** | 357B total | "September 2025" per third-party tracker |
| GLM-4.7 | 2025-12 | likely GLM4 | likely 151329-151364 | likely MoE | n/a yet | ~late 2024 per blog |

**Tokenizer continuity (verified):**

- ChatGLM3-6B uses `ChatGLMTokenizer`, eos `</s>` and pad `<unk>`, with [gMASK] at 64790 and sop at 64792 — completely incompatible with GLM-4-9B.
- GLM-4-9B uses `ChatGLM4Tokenizer`, eos `<|endoftext|>` at 151329, added tokens 151329-151342. **Verified.**
- GLM-4-9B-0414 uses `PreTrainedTokenizer` but the added-tokens range is **identical to GLM-4-9B (151329-151342)**, so it is the same vocabulary effectively.
- GLM-4.5-Air and GLM-4.6 extend the vocab to 151364 (adds `<think>`/`</think>`, tool, image, video, transcription, audio, box markers — 22 new tokens) but the core 151329-151342 region is byte-identical.

**Density:** ChatGLM, ChatGLM2, ChatGLM3, GLM-4-9B (all dense). **GLM-4.5/4.5-Air/4.6/4.7 are all MoE.** This is fatal for any PCSG pair attempting "GLM-4-9B vs GLM-4.5-Air" — L2 violation.

**Cutoff sourcing:** GLM-4-9B card says "pre-trained on approximately ten trillion tokens of multilingual corpus … shares pipeline with GLM-4 (0520)." No explicit date. GLM-4.5 / 4.6 cards likewise silent in their official HF READMEs. Third-party trackers (mindstudio.ai, allmo.ai) report GLM-4.6 cutoff as Sept 2025, GLM-4.6V as Dec 2025. **Cutoff for original GLM-4-9B is essentially unknown — flag for empirical probe.**

**AWQ availability:** **No vendor-official AWQ for GLM-4-9B.** Community-only (e.g., legraphista, second-state). For GLM-4.5/4.6 same — no Zhipu-official AWQ checkpoints found.

**PCSG eligibility verdict:**

| Pair | Verdict |
|---|---|
| GLM-4-9B ↔ GLM-4-9B-0414 | tokenizer ✓, density ✓, but **same family same nominal version** — cutoff gap unknown; needs probe |
| GLM-4-9B (dense) ↔ GLM-4.5-Air (MoE) | **L2 violation — invalid** |
| ChatGLM3-6B ↔ GLM-4-9B | **L1 violation — different tokenizer class entirely — invalid** |

### 3.3 DeepSeek family

**Lineage timeline:**

| Version | Release | Tokenizer class | Vocab | Density | Sizes | Cutoff |
|---|---|---|---|---|---|---|
| DeepSeek-LLM-7B/67B-base | 2023-12 | `LlamaTokenizerFast` | 100K BPE; eos `<｜end▁of▁sentence｜>` (FE69 chars), add_bos true | dense | 7B, 67B | 2023-05 per HaoooWang |
| DeepSeek-Coder | 2024-01 | distinct, 102400 BPE | 102400 | dense | 1.3/6.7/33B | 2023-03 |
| DeepSeek-Coder-V2 | 2024-06 | LlamaTokenizerFast 102400 | matches V2 | **MoE** | 16B-A2.4 / 236B-A21 | 2023-11 |
| DeepSeek-V2 | 2024-05 | `LlamaTokenizerFast` | matches V3 base | **MoE** | 236B-A21 | undisclosed |
| DeepSeek-V3 | 2024-12 | `LlamaTokenizerFast` | 128K BPE, eos shared with V2 | **MoE** | 671B-A37 | 2024-07 per HaoooWang |
| DeepSeek-V3-0324 | 2025-03 | same V3 tokenizer | identical | **MoE** | 671B-A37 | unknown |
| DeepSeek-R1 | 2025-01 | same V3 tokenizer | identical | **MoE** | 671B-A37 | 2024-07 per HaoooWang |
| DeepSeek-V3.2 | 2025-09 | same V3 tokenizer (verified) | identical | **MoE** | 671B-A37 | unknown |

**Tokenizer continuity:** DeepSeek-LLM 7B-base, V2, V3 all use LlamaTokenizerFast with the FE69-encoded `<｜begin▁of▁sentence｜>` BOS. V3 / R1 / V3.2 share tokenizer exactly (community-verified — V3.2 release notes state "no new vocabulary, only chat template / context update").

**Density:** DeepSeek-LLM-7B/67B = dense. **Everything from V2 onwards is MoE.** Coder-V2 is also MoE.

**PCSG eligibility verdict:**

- DeepSeek-LLM-7B ↔ DeepSeek-V3: L2 violation (dense vs MoE).
- DeepSeek-V2 ↔ DeepSeek-V3: L2 ✓ (both MoE), but if PCSG is restricted to dense (per fleet design), invalid.
- **No internal DeepSeek dense pair with cutoff differential.** DeepSeek-LLM has only one cutoff family.

### 3.4 Yi family

**Lineage timeline:**

| Version | Release | Tokenizer class | Vocab | Density | Sizes | Cutoff |
|---|---|---|---|---|---|---|
| Yi-6B / 9B / 34B | 2023-11 | `LlamaTokenizer` | 64K | dense | 6/9/34B | "Jan 2024 + Nov 2023" per community (different per size) |
| Yi-1.5-6B / 9B / 34B | 2024-05 | `LlamaTokenizer` (added a few tokens) | 64K base, +special tokens | dense | 6/9/34B (+32K context variants) | undisclosed; +500B-token continued pretraining on Yi |

**Tokenizer continuity (verified):** Both Yi 1.0 and Yi-1.5 use `LlamaTokenizer`, vocab 64000. Yi-1.5 adds extra special tokens (community discussions on HuggingFace mention BOS/EOS handling differences and added tokens not in Yi 1.0). **Largely compatible at the core BPE level**; treat with caution.

**Density:** All Yi and Yi-1.5 are dense.

**Cutoff sourcing:** Yi paper (arxiv 2403.04652) discusses 3.1T tokens but no date. Yi-1.5 GitHub says "continued pretraining on 500B tokens on top of Yi" — date unstated. Third-party pages report Yi-1.5 cutoff as "early 2024" but unverified.

**AWQ availability:** No vendor-official AWQ from 01-ai. Community-only.

**PCSG eligibility verdict:**

- **Yi-9B ↔ Yi-1.5-9B** is a structurally interesting pair: same tokenizer family, same dense, same paradigm (both base or both chat), same size. **But cutoff dates are not vendor-stated.** And no official AWQ. If we're willing to do fp16 (Yi-1.5-9B is ~18GB fp16, fits A6000 48GB) and trust community cutoff guesses, this is a usable B-tier pair. Empirical probing of cutoffs essential.

### 3.5 Baichuan family

| Version | Release | Tokenizer | Density | Sizes | Cutoff |
|---|---|---|---|---|---|
| Baichuan-7B / 13B | 2023-06 | custom `BaichuanTokenizer` (sentencepiece) | dense | 7/13B | mid-2023 |
| Baichuan2-7B / 13B-Base | 2023-09 | `BaichuanTokenizer` (different vocab from Baichuan1) | dense | 7/13B | mid-2023 |
| Baichuan2-Turbo / Baichuan-M (medical) | 2024-01 onward | varies; M1 has different tokenizer | dense | varies | undisclosed |

**Tokenizer continuity:** Baichuan → Baichuan2 broke vocab. Baichuan2 internally appears stable across 7B/13B sizes (same `BaichuanTokenizer` class).

**Density:** All dense.

**PCSG eligibility verdict:** Baichuan2-7B ↔ Baichuan2-13B: same cutoff likely (both released same timeframe). No clean cutoff differential within Baichuan2. **Not useful for PCSG.**

### 3.6 InternLM family

**Lineage timeline:**

| Version | Release | Tokenizer class | Vocab | Density | Sizes | Cutoff |
|---|---|---|---|---|---|---|
| InternLM-7B / 20B | 2023-09 | `InternLMTokenizer` | distinct | dense | 7/20B | 2023 mid |
| InternLM2-7B / 20B | 2024-01 | `InternLM2Tokenizer` | 92544; added tokens 92543 (`<|im_start|>` etc.) | dense | 7/20B | undisclosed |
| InternLM2.5-7B / 20B | 2024-07 | `InternLM2Tokenizer` (**SAME class!**) | 92544; verified identical added-tokens region | dense | 7/20B | undisclosed |
| InternLM3-8B-Instruct | 2025-01 | `InternLM3Tokenizer` (**NEW class**) | 128132 max; new reasoning tokens | dense | 8B | 2024 H2 (community) |

**Tokenizer continuity (verified):**
- InternLM2-7B: `InternLM2Tokenizer`, eos `</s>`, max added token 92543 (`<|im_start|>`).
- InternLM2.5-7B: `InternLM2Tokenizer`, eos `</s>`, max added token 92543 (`<|im_start|>`). **Identical tokenizer.**
- InternLM3-8B: `InternLM3Tokenizer` (new class!), eos `</s>`, max added token 128132. **Tokenizer broke between 2.5 and 3.**

**Density:** All InternLM variants are dense.

**Cutoff sourcing:** Neither InternLM2 nor InternLM2.5 model cards state a training cutoff date. InternLM2.5 adds 1M context, 20% reasoning improvement, and "leverages synthetic data." Release dates: InternLM2 = 2024-01-17, InternLM2.5 = 2024-07-03. **Whether they share or differ in pretraining-data cutoff is not vendor-stated.** This is the critical unknown.

**AWQ availability:** No vendor-official AWQ for InternLM2/2.5/3. Community AWQ (lmdeploy, study-hjt) exists for 7B variants.

**PCSG eligibility verdict:**

| Pair | Verdict |
|---|---|
| InternLM2-7B ↔ InternLM2.5-7B | tok ✓, dense ✓, both 7B ✓, paradigm ✓, **cutoff Δ unknown** — high-priority candidate **conditional on empirical cutoff probe** |
| InternLM2-7B ↔ InternLM2-20B | same family, same release window → no cutoff Δ likely |
| InternLM2.5-7B ↔ InternLM3-8B | tokenizer broke (different class) — L1 violation |

### 3.7 MiniCPM family

| Version | Release | Tokenizer | Density | Sizes | Cutoff |
|---|---|---|---|---|---|
| MiniCPM-2B (sft / dpo) | 2024-02 | `LlamaTokenizer` derivative ~127K | dense | 2.4B | undisclosed |
| MiniCPM-2B-128k | 2024-04 | extended vocab 127660 | dense | 2.4B | undisclosed |
| MiniCPM3-4B | 2024-09 | `LlamaTokenizer`, max added 73447 (`<|fim_suffix|>`) | dense | 4B | undisclosed |
| MiniCPM4 / 4.1 | 2025-06 onwards | varies, optimized for edge | dense | small | undisclosed |

**Tokenizer continuity:** MiniCPM-2B → MiniCPM-2B-128k extended vocab. MiniCPM3-4B has yet another tokenizer (BOS `<s>`, EOS `<|im_end|>`, max added token 73447). The family is not tokenizer-stable across versions.

**Density:** All dense.

**PCSG eligibility verdict:** MiniCPM has small-size models (good for white-box probing) but tokenizer-instability across versions kills L1. **Not recommended.**

### 3.8 LLaMA family

**Lineage timeline:**

| Version | Release | Tokenizer | Vocab | Density | Sizes | Cutoff (verbatim from model card) |
|---|---|---|---|---|---|---|
| LLaMA-2-7B/13B/70B | 2023-07 | `LlamaTokenizer` (sentencepiece) | 32000 | dense | 7/13/70B | "Pretraining 2022-09, Finetuning 2023-07" |
| Meta-Llama-3-8B | 2024-04 | tiktoken-based, NEW vocab | 128256 | dense | 8B | **"March 2023"** |
| Meta-Llama-3-70B | 2024-04 | tiktoken-based | 128256 | dense | 70B | **"December 2023"** |
| Llama-3.1-8B/70B/405B | 2024-07 | tiktoken (same as Llama-3) | 128256 | dense | 8/70/405B | **"December 2023"** for all three |
| Llama-3.2-1B/3B (text) | 2024-09 | tiktoken | 128256 | dense | 1/3B | **"December 2023"** |
| Llama-3.2-11B/90B (vision) | 2024-09 | tiktoken | 128256 | dense + vision adapter | 11/90B | December 2023 |
| Llama-3.3-70B-Instruct | 2024-12 | tiktoken | 128256 | dense | 70B (no 8B!) | **"December 2023"** |
| Llama-4-Scout / Maverick | 2025-04 | tiktoken extended | varies | **MoE** | 17B-A16E / 17B-A128E | 2024-08 per HaoooWang |

**Tokenizer continuity:** **Llama-2 and Llama-3 are NOT compatible.** Llama-2 = sentencepiece 32000-token vocab; Llama-3 = tiktoken-based 128256-token vocab. Within Llama-3 family (3, 3.1, 3.2, 3.3) the tokenizer is **stable**. Llama-4 reportedly extends the tokenizer.

**Density:** Llama-2, Llama-3, Llama-3.1, Llama-3.2 (text), Llama-3.3 are all dense. Llama-4 is MoE.

**Cutoff sourcing:** Llama-3 model card on github.com/meta-llama/llama3/blob/main/MODEL_CARD.md is **explicit** about the 8B vs 70B cutoff difference. This is one of the few publicly-stated within-family cutoff differentials in the entire OSS landscape. Llama-3.1+ then unifies cutoff at December 2023.

**AWQ availability:** **No Meta-official AWQ.** The most-cited community AWQ is `hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4` and `hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4`. For Llama-3 (original, no 3.1) AWQ, `study-hjt/Meta-Llama-3-8B-Instruct-AWQ` and `solidrust/Meta-Llama-3-70B-Instruct-AWQ` are community variants.

**PCSG eligibility verdict:**

| Pair | Verdict |
|---|---|
| **Llama-3-8B ↔ Llama-3-70B** | tok ✓, dense ✓, paradigm ✓, **cutoff Δ ≈ 9 months (March vs December 2023) — vendor-stated**. Size mismatch 8B vs 70B (similar to fleet's 7B/14B). **Top-tier candidate** modulo Llama gating + community AWQ + Chinese coverage |
| Llama-3-8B ↔ Llama-3.1-8B | tok ✓, dense ✓, both 8B ✓, paradigm ✓ (both base or both Instruct), cutoff Δ ≈ 9 months (March vs December 2023). **Even better than 8B/70B** if we want size match. |
| Llama-3.1-8B ↔ Llama-3.3-70B | both 2023-12 cutoff — no Δ |
| Llama-3.1-8B ↔ Llama-3-70B | same Dec 2023 vs Dec 2023 (3.1's 8B inherits 70B's data per Meta) — no Δ |

**!! This is the single best within-family cutoff differential in the open-source landscape with a vendor-stated date: Llama-3-8B (March 2023) vs Llama-3.1-8B (December 2023). Same tokenizer, same dense, same 8B size, instruct/base paradigm match available, +9 months data.**

### 3.9 Mistral family

**Lineage timeline:**

| Version | Release | Tokenizer | Vocab | Density | Sizes | Cutoff |
|---|---|---|---|---|---|---|
| Mistral-7B-v0.1 | 2023-09 | `LlamaTokenizer` (sentencepiece) | 32000 | dense | 7B | 2023 (community) |
| Mistral-7B-v0.2 | 2024-03 | sentencepiece | 32000 | dense | 7B | undisclosed |
| Mistral-7B-v0.3 | 2024-05 | extended sentencepiece | 32768 | dense | 7B | undisclosed |
| Mixtral-8x7B / 8x22B | 2023-12 / 2024-04 | sentencepiece 32000 | 32k | **MoE** | 56B / 141B | undisclosed |
| Mistral-Nemo-Base-2407 | 2024-07 | `Tekken` (tiktoken-based, NEW) | 131072 | dense | 12B | 2024 |
| Mistral-Small-22B (2409) | 2024-09 | Tekken (same family as Nemo) | 131072 | dense | 22B | undisclosed |
| Mistral-Small-24B-Base-2501 | 2025-01 | Tekken | 131072 | dense | 24B | "2023-10" per HF discussion (claim) |
| Mistral-Small-3.1-24B-Base-2503 | 2025-03 | Tekken | 131072 | dense | 24B | "2023-10" per HaoooWang |
| Mistral-Small-3.2-24B-Instruct-2506 | 2025-06 | Tekken | 131072 | dense | 24B | "Oct 31, 2023" per user reports |
| Mistral-Large-2 (2407) | 2024-07 | sentencepiece extended | 32768 | dense | 123B | undisclosed |

**Tokenizer continuity:**
- Mistral-7B-v0.1 vs v0.2: same sentencepiece 32000.
- v0.2 → v0.3: vocab extended 32000 → 32768 (NEW special tokens added). Tokenizer-incompatible at the tail.
- Mistral-7B / Mixtral series → Mistral-Nemo / Small series: **tokenizer broke from sentencepiece to Tekken (tiktoken-based, vocab 131072)**.
- Within Tekken family (Nemo / Small-2409 / Small-3 / Small-3.1 / Small-3.2): tokenizer appears stable.

**Density:** Mistral-7B / Mistral-Nemo / Mistral-Small (all dense). Mixtral 8x7B / 8x22B (MoE).

**Cutoff sourcing:** Mistral does not disclose cutoffs in HF model cards. HuggingFace discussion thread for Mistral-Small-3.2 contains community probes claiming Oct 31, 2023 — and this is unchanged for Small 3.0 / 3.1 / 3.2, suggesting Mistral keeps recycling pretraining checkpoints.

**AWQ availability:** Casper Hansen and others have community AWQ for Mistral-7B-v0.1/0.2/0.3 (`TheBloke/...`, `casperhansen/...`). For Mistral-Small-24B family, community AWQ on HF (`mistralai/...-AWQ` does NOT exist; `Modelscope/...` and `RedHatAI/...` versions are common).

**PCSG eligibility verdict:**

| Pair | Verdict |
|---|---|
| Mistral-7B-v0.1 ↔ Mistral-7B-v0.3 | size ✓ (both 7B), dense ✓, paradigm ✓, but **tokenizer extended 32000 → 32768** → L1 partial match, must intersect vocab. Cutoff Δ unknown but plausibly some. Useful B-tier. |
| Mistral-Small-24B-2501 ↔ Mistral-Small-3.1-24B-2503 | tokenizer ✓ (both Tekken), dense ✓, both 24B ✓ (large for 48GB AWQ), but **community evidence says cutoff is identical (Oct 2023) across all Mistral-Small revisions**. No Δ → invalid. |
| Mistral-Nemo-Base-2407 ↔ Mistral-Small-24B-2501 | tokenizer ✓ (Tekken), dense ✓, but size 12B vs 24B; cutoff unstated for Nemo. Speculative. |

### 3.10 Gemma family

| Version | Release | Tokenizer | Vocab | Density | Sizes | Cutoff |
|---|---|---|---|---|---|---|
| Gemma-1 2B / 7B | 2024-02 | `GemmaTokenizer` sentencepiece | 256000 | dense | 2/7B | early-2024 |
| Gemma-2 2B / 9B / 27B | 2024-06 | `GemmaTokenizer` sentencepiece (same family) | 256000 | dense | 2/9/27B | not in model card; community: 2024 |
| Gemma-3 4B / 12B / 27B | 2025-03 | likely GemmaTokenizer | 256000 | dense | 4/12/27B | **"August 2024" per official model card** |
| Gemma-3n | 2025-04 | varies | varies | dense | small | "June 2024" per official card |

**Tokenizer continuity:** Gemma-1 / Gemma-2 share sentencepiece 256K vocab. Gemma-3's tokenizer not directly verified against Gemma-2 in this scan (Gemma model files were 401-gated).

**Density:** All Gemma versions are dense.

**Cutoff sourcing:** **Google's official Gemma 3 model card explicitly states "knowledge cutoff date for the training data was August 2024"**. Gemma 2 model card does NOT state a cutoff (verified via WebFetch). Gemma 3n states June 2024.

**AWQ availability:** No vendor-official AWQ. Community (e.g., `bartowski/gemma-2-9b-it-AWQ`, `solidrust/gemma-2-9b-it-AWQ`) exists.

**PCSG eligibility verdict:**

| Pair | Verdict |
|---|---|
| Gemma-2-9B ↔ Gemma-3-12B | tokenizer continuity uncertain (likely same sentencepiece 256K), both dense, but **vocab modifications likely between Gemma 2 → Gemma 3**. Cutoff Δ ≈ 2-6 months (Gemma 2 mid-2024 inferred vs Gemma 3 Aug 2024) — small. Size mismatch 9B vs 12B. Workable B-tier. |
| Gemma-1-7B ↔ Gemma-2-9B | tokenizer ✓, dense ✓, but **size mismatch and cutoff Δ uncertain**. |
| Within Gemma-2 (9B vs 27B) | same cutoff likely; no Δ. |

---

## 4. Cross-family options

**Cross-family same-tokenizer pairs.** A small number of vendor families share base tokenizers via direct fork:

- **Yi (01-ai)** uses `LlamaTokenizer` and could in principle pair with **MiniCPM3** (same `LlamaTokenizer`), but they have different added-tokens (Yi: 64000 base, MiniCPM3: 73447 max added) → vocab mismatch at the tail. Not L1-clean.
- **DeepSeek-LLM-7B-Base (dense)** uses `LlamaTokenizerFast` → **could** pair with another LlamaTokenizerFast model with same FE69 special tokens, but few exist outside the DeepSeek family.
- **Llama-3 derivatives (e.g. Hermes-3, Tulu-3, Nous-Hermes-3-8B)** all use the Llama-3 tokenizer and could in principle pair with Meta-Llama-3-8B as a "same-tokenizer + cutoff Δ" pair *if* the derivative did continued pretraining on data after Dec 2023. Most of these are SFT/DPO post-training only — they don't add pretraining data, so they don't shift cutoffs.

**No PCSG-valid cross-family pair surfaced** with stronger evidence than the within-family options. Cross-family is dominated by tokenizer mismatch at the special-token tail.

---

## 5. Ranked candidate list

Score = 3·tok_match + 3·density_match + 2·cutoff_gap_clarity + 1·size_match + 1·awq_official + 1·vendor_cutoff_stated. Max = 11.

| Rank | Early model | Late model | Tok match | Density | Cutoff_early | Cutoff_late | Gap (mo) | Size match | AWQ official | vLLM | Score | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Llama-3-8B | Llama-3.1-8B | exact (Llama-3 tiktoken 128256) | dense ✓ | 2023-03 | 2023-12 | 9 | exact (8B/8B) | community only (hugging-quants) | yes (≥0.5) | 10 | **Best PCSG candidate.** Vendor-stated cutoffs. Size match. Llama gating clears via meta-llama org. Risk: weak Chinese performance for the financial-news pilot. |
| 2 | Llama-3-8B | Llama-3-70B | exact | dense ✓ | 2023-03 | 2023-12 | 9 | 8B vs 70B (mirrors fleet's 7/14 mismatch) | community only | yes | 9 | Same tokenizer, same generation. Capacity ratio bigger than ideal. Shares the Llama gating concern. |
| 3 | Qwen2-7B-Instruct-AWQ | Qwen2.5-7B-Instruct-AWQ | partial (Qwen2 stops at 151645; Qwen2.5 extends to 151664; lower IDs identical) | dense ✓ | "end 2023" (community) | "end 2023" (community) | 0-9 (uncertain) | exact (7B/7B) | **Alibaba-official both** | yes | 9 | **Best practical pair** (no Llama gating, official AWQ, Chinese coverage). Cutoff Δ is the weakness. Run empirical probe before relying on it. |
| 4 | InternLM2-7B | InternLM2.5-7B | exact (`InternLM2Tokenizer`, max=92543) | dense ✓ | undisclosed | undisclosed | unknown (release Δ ~6 mo, plausible cutoff Δ ~3-6 mo) | exact (7B/7B) | community only | yes | 8 | Strong on tokenizer + density + size. Cutoff is the gamble. Strong Chinese-language support. Empirical probe required. |
| 5 | Qwen2.5-7B-AWQ | Qwen3-8B-AWQ | partial (Qwen2.5 max=151664, Qwen3 max=151668; extra `<think>`, `</think>`, `<tool_response>` tokens). Default eos differs. | dense ✓ | ~end-2023 | "late 2024" (uncertain) | ~12+ | near (7B vs 8B) | **Alibaba-official both** | yes | 8 | Plausible Δ12 mo gap. Caveat: probes must avoid `<think>` and tool_response special tokens for clean alignment. |
| 6 | Yi-9B | Yi-1.5-9B | partial (LlamaTokenizer 64K base, plus added-tokens drift) | dense ✓ | "Nov 2023" (community) | "early 2024" (community) | 2-4 | exact (9B/9B) | community only | yes | 7 | Cutoff dates are community guesses. fp16 fits A6000 48GB. Worth empirical probe. |
| 7 | Mistral-7B-v0.1 | Mistral-7B-v0.3 | partial (32000 → 32768 vocab extension) | dense ✓ | undisclosed | undisclosed | unknown | exact (7B/7B) | community AWQ (TheBloke etc.) | yes | 6 | Tokenizer broke at the tail. Mistral has consistently silent cutoff disclosures. |
| 8 | GLM-4-9B | GLM-4-9B-0414 | exact (151329-151342, both stop at same boundary) | dense ✓ | "GLM-4(0520) data" | undisclosed (released April 2025) | unknown | exact (9B/9B) | community only | yes | 6 | Tokenizer match is a coincidence (GLM-4-9B-0414 didn't extend vocab). Cutoff Δ totally undisclosed. fp16 fits 48GB. **Most interesting if probed for cutoff differential.** |
| 9 | Gemma-2-9B | Gemma-3-12B | likely partial (sentencepiece 256K base, possibly extended) | dense ✓ | unstated officially | **Aug 2024 (vendor-stated for Gemma-3)** | 2-6 plausible | 9B vs 12B near | community only | yes | 6 | Gemma-3 is the only one with a vendor-stated cutoff. Tokenizer drift unverified. |
| 10 | Mistral-Nemo-Base-2407 | Mistral-Small-24B-Base-2501 | exact (Tekken 131072) | dense ✓ | undisclosed | "Oct 2023" (community user-probed) | possibly tiny or zero | 12B vs 24B | community only | yes | 5 | Mistral evidence suggests pretraining is recycled; cutoff Δ may be ~0. Skip unless probed otherwise. |

---

## 6. Tokenizer-break atlas

Where in each family did the tokenizer break? "Break" = different `tokenizer_class` or vocab-base change, not just adding a few special tokens.

| Family | Break point | Pre-break tokenizer | Post-break tokenizer | Evidence |
|---|---|---|---|---|
| Qwen | Qwen-* → Qwen1.5 (2024-02) | `QWenTokenizer` (custom tiktoken) | `Qwen2Tokenizer` (151643 BPE) | Verified: Qwen-7B `tokenizer_config.json` lists `QWenTokenizer`; Qwen1.5-7B-Chat lists `Qwen2Tokenizer` |
| GLM | ChatGLM3-6B → GLM-4-9B (2024-06) | `ChatGLMTokenizer` (~65K) | `ChatGLM4Tokenizer` (~151K) | Verified |
| GLM (cont.) | GLM-4-9B → GLM-4.5+ (2025-07) | `ChatGLM4Tokenizer` 151342-max | `PreTrainedTokenizer` (GLM4-extended) 151364-max | Vocab-extension only; lower 151329-151342 region byte-identical |
| DeepSeek | DeepSeek-LLM-7B → DeepSeek-Coder (2024-01) | LlamaTokenizerFast 100K | LlamaTokenizerFast 102400 (Coder) | Different vocab |
| DeepSeek (cont.) | DeepSeek-Coder → DeepSeek-V2 (2024-05) | 102400 | 102400 same family but different special tokens | Verified |
| DeepSeek (cont.) | DeepSeek-V2 → DeepSeek-V3 (2024-12) | 102400 | 128000 BPE | Vocab extended significantly per V3 tech report |
| Yi | Yi-1.0 → Yi-1.5 (2024-05) | LlamaTokenizer 64000 | LlamaTokenizer 64000 + few added | Special-tokens additions only |
| Baichuan | Baichuan-1 → Baichuan-2 (2023-09) | sentencepiece 64K | sentencepiece 125k+ | Different vocab |
| InternLM | InternLM-1 → InternLM2 (2024-01) | `InternLMTokenizer` | `InternLM2Tokenizer` 92544 | New class |
| InternLM (cont.) | InternLM2.5 → InternLM3 (2025-01) | `InternLM2Tokenizer` 92544 | `InternLM3Tokenizer` 128132 | Verified — major vocab change, new class |
| LLaMA | Llama-2 → Llama-3 (2024-04) | sentencepiece 32000 | tiktoken 128256 | Major break |
| LLaMA (cont.) | Llama-3.x → Llama-4 (2025-04) | tiktoken 128256 | tiktoken extended | Llama-4 added tokens (community reports) |
| Mistral | Mistral-7B-v0.2 → v0.3 (2024-05) | sentencepiece 32000 | sentencepiece 32768 | Vocab extension only |
| Mistral (cont.) | Mistral-7B → Mistral-Nemo (2024-07) | sentencepiece 32k | Tekken 131072 | Major break |
| Gemma | Gemma-2 → Gemma-3 (2025-03) | sentencepiece 256K | sentencepiece (likely modified) 256K | Verification gated; check before relying |

---

## 7. Recommendations

### 7.1 Best 1-2 pairs to add to the fleet

**Recommendation A (preferred): Add `Qwen2-7B-Instruct-AWQ` to the fleet alongside `Qwen2.5-7B-Instruct-AWQ`.**

- Identical `Qwen2Tokenizer` core (vocab 151643), no quantization-pipeline changes required, official Alibaba AWQ-INT4, vLLM ≥0.5 supported.
- Same dense, same instruct paradigm, same 7B size — the tightest possible PCSG-aligned pair.
- *Risk:* the cutoff differential between Qwen2 (released June 2024, claimed "end of 2023" data) and Qwen2.5 (released September 2024, also "end of 2023" data) may be **near zero**. The Qwen blog and tech report explicitly avoid stating cutoffs; Qwen2.5 tech report (arxiv 2412.15115) talks about 18T tokens but no date.
- *Mitigation:* run an empirical "year-stratified factual recall" probe over 2023-Q3, 2023-Q4, 2024-Q1, 2024-Q2 events to localize each model's actual data horizon before committing to PCSG inference.

**Recommendation B (alternative if Llama gating clearable): Add `Llama-3-8B` and `Llama-3.1-8B` (base or Instruct, choose one paradigm).**

- This is the **only intra-family pair in the entire OSS landscape with a vendor-stated 9-month cutoff differential and identical tokenizer + density + size**.
- L4 paradigm: choose pair from `meta-llama/Meta-Llama-3-8B` ↔ `meta-llama/Meta-Llama-3.1-8B` (both base) or `…-Instruct` (both instruct).
- *Risk 1:* AWQ is community-only (hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4). The original Llama-3 8B AWQ comes from study-hjt or similar community uploaders. We need to **verify the AWQ quantization pipeline was the same** for both checkpoints — any difference in calibration data, group size, or AWQ version invalidates paired logprob.
- *Risk 2:* Llama-3 was trained primarily on English; financial-news pilot is on Chinese A-share news. Tokenization of Chinese characters in tiktoken 128K vs Qwen's 151K is materially different (Llama-3 is less efficient on Chinese), and Chinese-task quality is ~10-15 pts lower than Qwen.

### 7.2 Best alternative — fleet redesign

If we can tolerate one round of fleet rebuild, the **InternLM2-7B / InternLM2.5-7B / InternLM2-20B / InternLM2.5-20B** quartet is structurally appealing:

- All four share `InternLM2Tokenizer` exactly (verified).
- All dense.
- 7B and 20B sizes give us the "capacity axis" the existing fleet already provides.
- 6-month release gap between InternLM2 (Jan 2024) and InternLM2.5 (Jul 2024) gives a plausible cutoff differential.
- Strong Chinese-language coverage.
- *Critical risk:* the cutoff dates are NOT vendor-stated. Without empirical probing this is gambling.
- *Operational risk:* no vendor-official AWQ. Community AWQ (lmdeploy, study-hjt, etc.) needs validation.

### 7.3 Risks specifically called out

- **Qwen3 cutoff is a marketing void.** Despite the model being released April 2025, neither the Qwen3 blog nor the Qwen3 tech report (arxiv 2505.09388) state a cutoff date. Community probes (GitHub issues #1442, #1122) suggest the model knows about events through late-2024 inconsistently — it's likely a moving cutoff per data source. Do NOT cite "Qwen3 cutoff = January 2025" as if it's vendor-confirmed in a paper. The current fleet entry's "cutoff 2025-01-31" for qwen3 should be marked as **operator-asserted, not vendor-stated**.
- **Qwen2.5 cutoff = "end of 2023" is a community paraphrase, not an Alibaba official statement.** The Qwen2.5 tech report (arxiv 2412.15115) says "18 trillion tokens" but contains no cutoff date. The HaoooWang community list says "end of 2023" with no citation. Treat as **inferred, not stated.**
- **GLM-4-9B cutoff is a black box.** "Pre-trained on approximately ten trillion tokens, post-trained with same pipeline as GLM-4 (0520)" — the 0520 reference (May 2024 release of GLM-4) doesn't constrain pretraining cutoff.
- **DeepSeek V2/V3 cutoff dates from HaoooWang's list (2024-07) are themselves community-sourced, not from DeepSeek tech report.** The DeepSeek-V3 tech report (arxiv 2412.19437) discusses 14.8T tokens but no date.
- **All Mistral cutoffs are community-probed.** Mistral has a documented history of recycling pretraining checkpoints across "Small" generations — the same Oct 2023 cutoff is reported for Small-3.0, 3.1, and 3.2.

---

## 8. Sources

- **Qwen tokenizer/config files (verified directly via WebFetch):**
  - <https://huggingface.co/Qwen/Qwen-7B/raw/main/tokenizer_config.json> — confirms `QWenTokenizer` class for first-gen Qwen
  - <https://huggingface.co/Qwen/Qwen1.5-7B/raw/main/tokenizer_config.json> — `Qwen2Tokenizer`, model_max 32768, eos `<|endoftext|>` 151643
  - <https://huggingface.co/Qwen/Qwen2-7B/raw/main/tokenizer_config.json> — `Qwen2Tokenizer`, identical to Qwen1.5 base
  - <https://huggingface.co/Qwen/Qwen2.5-7B/raw/main/tokenizer_config.json> — `Qwen2Tokenizer`, max ID 151664
  - <https://huggingface.co/Qwen/Qwen2.5-14B/raw/main/tokenizer_config.json> — same as 7B max 151664
  - <https://huggingface.co/Qwen/Qwen3-8B/raw/main/tokenizer_config.json> — `Qwen2Tokenizer`, max 151668, adds `<think>`/`</think>`, eos changed to `<|im_end|>`
  - <https://huggingface.co/Qwen/Qwen3-14B/raw/main/tokenizer_config.json> — same as Qwen3-8B
- **Qwen AWQ vendor confirmation:**
  - <https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-AWQ> — Alibaba-official
  - <https://huggingface.co/Qwen/Qwen2.5-14B-Instruct-AWQ> — Alibaba-official
  - <https://huggingface.co/Qwen/Qwen3-8B-AWQ> — Alibaba-official, base model `Qwen/Qwen3-8B-Base`
  - <https://huggingface.co/Qwen/Qwen3-14B-AWQ> — Alibaba-official
  - <https://huggingface.co/Qwen/Qwen2-7B-Instruct-AWQ> — Alibaba-official
  - <https://huggingface.co/Qwen/Qwen1.5-7B-Chat-AWQ> — Alibaba-official
  - <https://huggingface.co/Qwen/Qwen1.5-14B-Chat-AWQ> — Alibaba-official
- **Qwen blogs (cutoff sourcing):**
  - <https://qwenlm.github.io/blog/qwen2/> — Qwen2 blog; no cutoff stated
  - <https://qwenlm.github.io/blog/qwen2.5/> — Qwen2.5 blog; mentions 18T tokens, no cutoff date
  - <https://qwenlm.github.io/blog/qwen3/> — Qwen3 blog; mentions 36T tokens, no cutoff date
  - <https://github.com/QwenLM/Qwen3/discussions/1093> — community discussion of cutoffs; only one community member's opinion — no Qwen-official answer
  - <https://github.com/QwenLM/Qwen3/discussions/1122> — user reports inconsistent late-2024 knowledge in Qwen3
  - <https://arxiv.org/pdf/2412.15115> — Qwen2.5 tech report; no cutoff date
  - <https://arxiv.org/pdf/2505.09388> — Qwen3 tech report; no explicit cutoff date
- **GLM family:**
  - <https://huggingface.co/THUDM/glm-4-9b/raw/main/tokenizer_config.json> — `ChatGLM4Tokenizer`, vocab 151329-151342
  - <https://huggingface.co/zai-org/GLM-4-9B-0414/raw/main/tokenizer_config.json> — `PreTrainedTokenizer`, identical 151329-151342 (verified to match GLM-4-9B)
  - <https://huggingface.co/zai-org/GLM-4.5-Air/raw/main/tokenizer_config.json> — extends to 151364
  - <https://huggingface.co/zai-org/GLM-4.6/raw/main/tokenizer_config.json> — extends to 151364
  - <https://huggingface.co/THUDM/chatglm3-6b/raw/main/tokenizer_config.json> — `ChatGLMTokenizer`, vocab ~65k, [gMASK] at 64790
  - <https://huggingface.co/zai-org/GLM-4.5> — confirms MoE 355B-A32B
  - <https://huggingface.co/zai-org/GLM-4.6> — confirms MoE 357B
  - <https://arxiv.org/abs/2406.12793> — ChatGLM family paper
  - <https://github.com/zai-org/GLM-4> — GLM-4 GitHub
- **DeepSeek family:**
  - <https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/tokenizer_config.json> — `LlamaTokenizerFast`, eos `<｜end▁of▁sentence｜>`
  - <https://huggingface.co/deepseek-ai/DeepSeek-V2/raw/main/tokenizer_config.json> — same `LlamaTokenizerFast` family
  - <https://huggingface.co/deepseek-ai/deepseek-llm-7b-base/raw/main/tokenizer_config.json> — `LlamaTokenizerFast`, max length 4096 (older variant)
  - <https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-V3_2.html> — V3.2 keeps V3 tokenizer
  - <https://arxiv.org/pdf/2412.19437> — DeepSeek-V3 tech report
- **Yi family:**
  - <https://huggingface.co/01-ai/Yi-1.5-9B/raw/main/tokenizer_config.json> — `LlamaTokenizer`, 4096 max-length, BOS `<|startoftext|>`
  - <https://huggingface.co/01-ai/Yi-9B/raw/main/tokenizer_config.json> — same `LlamaTokenizer`
  - <https://huggingface.co/01-ai/Yi-1.5-9B> — Yi-1.5 model card; says +500B-token continued pretraining on Yi
  - <https://arxiv.org/abs/2403.04652> — Yi paper (March 2024)
- **InternLM family:**
  - <https://huggingface.co/internlm/internlm2-7b/raw/main/tokenizer_config.json> — `InternLM2Tokenizer`, max 92543
  - <https://huggingface.co/internlm/internlm2_5-7b/raw/main/tokenizer_config.json> — same `InternLM2Tokenizer`, max 92543 (verified identical)
  - <https://huggingface.co/internlm/internlm3-8b-instruct/raw/main/tokenizer_config.json> — `InternLM3Tokenizer`, max 128132 (NEW class)
  - <https://huggingface.co/internlm/internlm2_5-7b> — model card; no cutoff stated
  - <https://github.com/InternLM/InternLM> — official repo
  - <https://arxiv.org/abs/2403.17297> — InternLM2 tech report (March 2024)
- **LLaMA family:**
  - <https://github.com/meta-llama/llama3/blob/main/MODEL_CARD.md> — **Llama-3 8B = March 2023, 70B = December 2023** explicitly stated
  - <https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_1/> — Llama-3.1 cutoff December 2023
  - <https://www.prompthub.us/models/llama-3-3-70b> — Llama-3.3 cutoff December 1, 2023
  - <https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct/discussions/7> — community discussion of 8B vs 70B cutoff differential
  - <https://www.llama.com/docs/how-to-guides/quantization/> — Meta's official quantization (no AWQ for 8B/70B; only QAT/SpinQuant for 1B/3B)
  - <https://huggingface.co/hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4> — community canonical AWQ
- **Mistral family:**
  - <https://huggingface.co/mistralai/Mistral-7B-v0.1/raw/main/tokenizer_config.json> — `LlamaTokenizer` (sentencepiece 32000)
  - <https://huggingface.co/mistralai/Mistral-7B-v0.3/raw/main/tokenizer_config.json> — extended sentencepiece 32768
  - <https://huggingface.co/mistralai/Mistral-Nemo-Base-2407/raw/main/tokenizer_config.json> — Tekken (LlamaTokenizer-shaped wrapper, 131072), 565+ control tokens
  - <https://docs.mistral.ai/cookbooks/concept-deep-dive-tokenization-chat_templates> — Tekken tokenizer details
  - <https://mistral.ai/news/mistral-nemo> — Nemo announcement
  - <https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506/discussions/11> — community claim of "Oct 31, 2023" cutoff
- **Gemma family:**
  - <https://ai.google.dev/gemma/docs/core/model_card_2> — Gemma 2 official model card; **does not state cutoff** (verified)
  - <https://ai.google.dev/gemma/docs/core/model_card_3> — Gemma 3 cutoff "August 2024" (verified verbatim)
  - <https://ai.google.dev/gemma/docs/gemma-3n/model_card> — Gemma 3n cutoff June 2024
- **MiniCPM:**
  - <https://huggingface.co/openbmb/MiniCPM3-4B/raw/main/tokenizer_config.json> — `LlamaTokenizer`, max added 73447
  - <https://arxiv.org/html/2404.06395v1> — MiniCPM paper
- **Cross-cutting cutoff lists (community, low confidence):**
  - <https://github.com/HaoooWang/llm-knowledge-cutoff-dates> — most-cited community curation; explicit "Llama-3 8B = 2023.03, 70B = 2023.12, Llama-3.1 = 2023.12"; "DeepSeek-V3/R1 = 2024.07"; "Qwen2 = 2023, Qwen2.5 = end of 2023, Qwen3 = Unknown"; "Mistral-Small-3.x = 2023.10"
  - <https://www.allmo.ai/articles/list-of-large-language-model-cut-off-dates> — third-party tracker; partial data
  - <https://docs.hatz.ai/en/articles/11961691-understanding-llm-training-dates> — explanation of why most vendors don't disclose cutoffs

---

**End of report.**
