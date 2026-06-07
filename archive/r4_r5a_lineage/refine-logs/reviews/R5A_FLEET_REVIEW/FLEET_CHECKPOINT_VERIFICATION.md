---
title: Fleet Checkpoint Verification
generated: 2026-04-15
source: Codex MCP xhigh
thread_id: 019d946f-ed1b-7cf1-a088-2d5fc07259b3
---

# Fleet Checkpoint Verification

Audit date: `2026-04-15`. For OpenAI, only the official **knowledge cutoff** dates published in model docs could be verified, not separate training-data cutoff dates. For Hugging Face models, the SHA below is the official repo SHA from the HF model metadata API, which pins the repo state as of today.

## Summary Table

| Model | Published cutoff | Status | Pinnable checkpoint / ID | Official source |
| --- | --- | --- | --- | --- |
| Qwen2.5-7B-Instruct | No explicit cutoff found | UNVERIFIED | `Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28` | [card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [meta](https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct), [blog](https://qwenlm.github.io/blog/qwen2.5/) |
| Qwen2.5-14B-Instruct | No explicit cutoff found | UNVERIFIED | `Qwen/Qwen2.5-14B-Instruct@cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8` | [card](https://huggingface.co/Qwen/Qwen2.5-14B-Instruct), [meta](https://huggingface.co/api/models/Qwen/Qwen2.5-14B-Instruct), [blog](https://qwenlm.github.io/blog/qwen2.5/) |
| GLM-4-9B-0414 | No explicit cutoff found | UNVERIFIED | `zai-org/GLM-4-9B-0414@645b8482494e31b6b752272bf7f7f273ef0f3caf` | [card](https://huggingface.co/zai-org/GLM-4-9B-0414), [meta](https://huggingface.co/api/models/zai-org/GLM-4-9B-0414) |
| DeepSeek-V3-0324 | No explicit cutoff found | UNVERIFIED | `deepseek-ai/DeepSeek-V3-0324@e9b33add76883f293d6bf61f6bd89b497e80e335` | [card](https://huggingface.co/deepseek-ai/DeepSeek-V3-0324), [meta](https://huggingface.co/api/models/deepseek-ai/DeepSeek-V3-0324), [API updates](https://api-docs.deepseek.com/zh-cn/updates) |
| GPT-4.1 | `2024-06-01` knowledge cutoff | CONFIRMED | `gpt-4.1-2025-04-14` | [docs](https://developers.openai.com/api/docs/models/gpt-4.1) |
| GPT-5.1 | `2024-09-30` knowledge cutoff | CONFIRMED | `gpt-5.1-2025-11-13` | [docs](https://developers.openai.com/api/docs/models/gpt-5.1) |
| Qwen3-8B | No explicit cutoff found | UNVERIFIED | `Qwen/Qwen3-8B@b968826d9c46dd6066d109eabc6255188de91218` | [card](https://huggingface.co/Qwen/Qwen3-8B), [meta](https://huggingface.co/api/models/Qwen/Qwen3-8B), [blog](https://qwenlm.github.io/blog/qwen3/) |
| Qwen3-14B | No explicit cutoff found | UNVERIFIED | `Qwen/Qwen3-14B@40c069824f4251a91eefaf281ebe4c544efd3e18` | [card](https://huggingface.co/Qwen/Qwen3-14B), [meta](https://huggingface.co/api/models/Qwen/Qwen3-14B), [blog](https://qwenlm.github.io/blog/qwen3/) |
| Claude Sonnet 4.6 | `Jan 2026` training cutoff; `Aug 2025` reliable knowledge cutoff | CONFIRMED | `claude-sonnet-4-6` | [overview](https://platform.claude.com/docs/en/about-claude/models/overview), [announcement](https://www.anthropic.com/news/claude-4-6) |
| GPT-5.4 | `2025-08-31` knowledge cutoff | CONFIRMED | `gpt-5.4-2026-03-05` | [docs](https://developers.openai.com/api/docs/models/gpt-5.4) |
| Qwen3-32B | No explicit cutoff found | UNVERIFIED | `Qwen/Qwen3-32B@9216db5781bf21249d130ec9da846c4624c16137` | [card](https://huggingface.co/Qwen/Qwen3-32B), [meta](https://huggingface.co/api/models/Qwen/Qwen3-32B), [blog](https://qwenlm.github.io/blog/qwen3/) |
| Qwen3-30B-A3B | No explicit cutoff found | UNVERIFIED | `Qwen/Qwen3-30B-A3B@ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` | [card](https://huggingface.co/Qwen/Qwen3-30B-A3B), [meta](https://huggingface.co/api/models/Qwen/Qwen3-30B-A3B), [blog](https://qwenlm.github.io/blog/qwen3/) |

## Per-Model Notes

- **Qwen2.5-7B-Instruct**: exact repo path is `Qwen/Qwen2.5-7B-Instruct`; no official statement confirming the commonly repeated `2023-10` cutoff was found.
- **Qwen2.5-14B-Instruct**: exact repo path is `Qwen/Qwen2.5-14B-Instruct`; same cutoff caveat as the 7B model.
- **GLM-4-9B-0414**: the canonical current HF repo is `zai-org/GLM-4-9B-0414`; some official examples still reference `THUDM/GLM-4-9B-0414`. The `0414` suffix appears to be an April 14 snapshot tag, but this was not found explicitly defined.
- **DeepSeek-V3-0324**: the exact API model string at launch was `deepseek-chat`, but that is a mutable alias, not a dated API checkpoint.
- **GPT-4.1**: `gpt-4.1-2025-04-14` is explicitly listed on the official model page, so the dated model ID is confirmed to exist.
- **GPT-5.1**: `gpt-5.1-2025-11-13` is explicitly listed on the official model page; the tentative checkpoint was correct.
- **Qwen3-8B**: exact repo path is `Qwen/Qwen3-8B`; no official statement confirming `2025-01` was found.
- **Qwen3-14B**: exact repo path is `Qwen/Qwen3-14B`; no official statement confirming `2025-01` was found.
- **Claude Sonnet 4.6**: the exact API model ID is `claude-sonnet-4-6`; Anthropic publishes both a training cutoff and a separate reliable knowledge cutoff.
- **GPT-5.4**: `gpt-5.4-2026-03-05` is the current docs-listed snapshot; no `gpt-5.4-2026-02-20` entry was found.
- **Qwen3-32B**: exact repo path is `Qwen/Qwen3-32B`; no official cutoff statement found.
- **Qwen3-30B-A3B**: exact repo path is `Qwen/Qwen3-30B-A3B`; no official cutoff statement found.

## Risks

1. **Qwen, GLM, and DeepSeek cutoff dates are all UNVERIFIED** — the expected dates may be plausible, but could not be verified from official vendor documentation. This is the single largest gap: 8 of 12 models lack confirmed cutoffs.
2. **HuggingFace repo SHA pins the full repo state**, not necessarily a vendor-labeled "launch commit" for weights only. Repo updates (README edits, config tweaks) can change the HEAD SHA without changing weights.
3. **`deepseek-chat` is not a durable historical pin** for DeepSeek-V3-0324; DeepSeek later repointed that alias to newer V3.x releases. There is no dated API model ID for DeepSeek.
4. **OpenAI publishes knowledge cutoff, not training-data cutoff**, on model pages. Anthropic is the only vendor in this set where both a training cutoff and a reliable knowledge cutoff are published separately.
5. **GLM repo ownership uncertainty**: the model appears under both `zai-org` and `THUDM` on HuggingFace; the canonical source may shift.
