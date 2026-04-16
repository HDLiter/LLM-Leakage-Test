---
title: Compute Platform Comparison for FinMem-Bench Fleet
generated: 2026-04-15
source: Codex MCP xhigh
thread_id: 019d946f-586e-79f2-8315-29d499c3eb97
---

## FinMem-Bench compute survey
**Assumptions**
- `Qwen2.5-14B` and `Qwen3-14B` need either `1×48GB+` GPU or `2×24GB` tensor parallel for bf16/fp16; the 7B/8B/9B models fit on `1×24GB`.
- White-box cost estimates use the cheapest **verified** feasible config on each platform. For `24GB-only` budget plans, I assume `56–112 GPU-hours` total across the 5 local models; for `48GB+` single-GPU plans, `40–80 GPU-hours`.
- Full-run API estimate uses `3,200 cases × 8 detectors = 25,600 calls/model`, with a mid-case prompt of `2,000 input + 200 output tokens/call`.

### A+B. GPU rental platforms
| Platform | Region | Publicly visible GPUs | Public pricing model | 5-model white-box est. | vLLM | Mainland no-VPN | Credits / research |
|---|---|---|---|---:|---|---|---|
| [AutoDL](https://www.autodl.com/docs/gpu/) | CN | `3090/4090/4090D/A40/A100/A800/L20/H20/H800...` | Pay-as-you-go + packages; live hourly floors are login-gated | `N/A` public live floor | Yes, self-managed | Yes | [1 month member on signup + student member pricing](https://www.autodl.com/docs/member/), [student verification](https://www.autodl.com/docs/student/) |
| [FeatherCloud / 羽毛云](https://idc.ym6.xyz/) | CN | Product catalog visible, but live GPU price pages were not crawlable | Likely hourly marketplace/cart pricing | `N/A` public live floor | Likely yes, inferred | Yes | No public academic program found |
| [矩池云](https://matgo.cn/) | CN | `A2000 / RTX 3090 / RTX 4090 / A100` | Hourly | `¥72–145` on `3090` (`¥1.29/GPU-h`) | Yes, self-managed | Yes | [Education discount + coupons/experience credit](https://matgo.cn/supports/news/) |
| [潞晨云](https://cloud.luchentech.com/) | CN | `3090 / 4090 / 4090D / A100 40/80 / H800 / H100 / H200` | Hourly, [minute billing](https://cloud.luchentech.com/doc/docs/billing/) | `¥46–92` on `3090` (`¥0.82/GPU-h`) | Yes; [Docker/vLLM-friendly](https://cloud.luchentech.com/doc/docs/docker/) | Yes | [Recharge bonus vouchers](https://cloud.luchentech.com/doc/docs/welfare/invitation-bonus/) |
| [Vast.ai](https://storage.googleapis.com/vast-gpu-pricing/gpu-price-history.json) | US | `3090 / 4090 / A5000 / A6000 / A100 / H100 / H200...` | Marketplace hourly; I quote current **p25** | `$7.5–14.9` on `3090` p25 (`$0.133/GPU-h`) | Yes, [official vLLM docs](https://docs.vast.ai/vllm-llm-inference-and-serving) | Yes* | [Startup program up to $2.5k](https://vast.ai/article/vast-ai-startup-program) |
| [Runpod](https://www.runpod.io/gpu-pricing) | US | `A5000 / 3090 / 4090 / A40 / A6000 / A100 / H100...` | Hourly | `$9.0–17.9` on `A5000` (`$0.16/GPU-h`) | Yes, [official vLLM docs](https://docs.runpod.io/serverless/vllm/get-started) | Yes* | [Startup credits](https://www.runpod.io/startup-program), [referral bonus](https://www.runpod.io/referral-and-affiliate-program) |
| [Modal](https://modal.com/pricing) | US | `L4 / A10 / A100 40/80 / RTX PRO 6000 / H100 / H200 / B200` | Serverless per-second | `$51–103` using `L4` for 7/8/9B + `A100-40GB` for 14B | Yes, [official vLLM examples](https://modal.com/docs/examples/ministral3_inference) | Yes* | `$30/mo` starter, [up to `$10k` academic credits](https://modal.com/academics) |
| [Lambda Cloud](https://lambda.ai/pricing) | US | `A10 / A6000 48GB / A100 40/80 / H100 / GH200 / B200` | Hourly | `$32–64` on `A6000 48GB` (`$0.80/GPU-h`) | Yes, self-managed VM | Yes* | No standing free tier found |
| [TensorDock](https://www.tensordock.com/cloud-gpus) | US | `3090 / 4090 / RTX A6000 / RTX 6000 Ada / A100 / H100` | Hourly, host-variable | `$11.2–22.4` on `3090` (`$0.20/GPU-h`) | Yes; KVM + root access | Yes* | No public academic tier found |

`*` = inferred from public site/API reachability and global service posture, not measured from a mainland-China network.

### C. Chinese API providers for the small open models
| Provider | Relevant current pricing | Mainland no-VPN | Free / credits | Good replacement for local white-box? |
|---|---|---|---|---|
| [SiliconFlow](https://cloud.siliconflow.cn/open/models) | `Qwen2.5-7B 0/0`, `Qwen2.5-14B ¥0.7/¥0.7`, `GLM-4-9B 0/0`, `Qwen3-8B 0/0`, `Qwen3-14B ¥0.5/¥2`, `DeepSeek-V3.2 ¥2/¥3` per 1M tokens | Yes | Many listed small models are free | No, if you need vLLM logprobs/control |
| [Alibaba Model Studio / 百炼](https://help.aliyun.com/zh/model-studio/models) | Mainland deploy: `Qwen2.5-7B ¥0.5/¥1`, `Qwen2.5-14B ¥1/¥3`, `Qwen3-8B ¥0.5/¥2` non-thinking, `Qwen3-14B ¥1/¥4` non-thinking | Yes | `qwen2.5-7b/14b -1m` variants include `1M` free tokens for 90 days | No |
| [Zhipu AI / 智谱](https://open.bigmodel.cn/pricing) | `GLM-4-9B` public instance on the official pricing bundle is `¥0.002/1k` = `¥2/¥2` per 1M tokens | Yes | Promo vouchers exist; no clear standing academic tier found | No |
| [DeepSeek official](https://api-docs.deepseek.com/zh-cn/quick_start/pricing) | Current direct endpoint `deepseek-chat` = `DeepSeek-V3.2`: `¥2` input, `¥3` output, `¥0.2` cache-hit input per 1M | Yes | No standing free tier found | No |

### D+E. OpenRouter and direct black-box APIs
| Provider | Model | Input / Output per 1M | Availability / note | Mainland no-VPN |
|---|---|---:|---|---|
| [OpenRouter](https://openrouter.ai/api/v1/models) | `deepseek/deepseek-chat-v3-0324` | `$0.20 / $0.77` | Best exact-ish `DeepSeek-V3` listing I found | Yes* |
| [OpenRouter](https://openrouter.ai/api/v1/models) | `anthropic/claude-sonnet-4.6` | `$3 / $15` | Same list price as Anthropic direct | Yes* |
| [OpenRouter](https://openrouter.ai/api/v1/models) | `qwen/qwen-2.5-7b-instruct` | `$0.04 / $0.10` | Available | Yes* |
| [OpenRouter](https://openrouter.ai/api/v1/models) | `qwen/qwen3-8b` | `$0.05 / $0.40` | Available | Yes* |
| [OpenRouter](https://openrouters.ai/api/v1/models) | `qwen/qwen3-14b` | `$0.06 / $0.24` | Available | Yes* |
| [OpenRouter](https://openrouter.ai/api/v1/models) | `GLM-4-9B` | `N/A` | Not in the live `/api/v1/models` list on 2026-04-15 | Yes* |
| [OpenAI direct](https://platform.openai.com/docs/pricing/) | `GPT-4.1` | `$2 / $8` | Cheapest clean path is direct OpenAI | [No official mainland support](https://help.openai.com/en/articles/5347006-which-countries-and-territories-are-supported-by-openai) |
| [OpenAI direct](https://platform.openai.com/docs/pricing/) | `GPT-5.1` | `$1.25 / $10` | Cheapest clean path is direct OpenAI | [No official mainland support](https://help.openai.com/en/articles/5347006-which-countries-and-territories-are-supported-by-openai) |
| [Anthropic direct](https://platform.claude.com/docs/en/about-claude/pricing) | `Claude Sonnet 4.6` | `$3 / $15` | Same list price as OpenRouter; direct is simpler | [China not in supported regions](https://platform.claude.com/docs/en/api/supported-regions) |
| [DeepSeek direct](https://api-docs.deepseek.com/zh-cn/quick_start/pricing) | `deepseek-chat` (`V3.2`) | `¥2 / ¥3` | Naming caveat: direct API has rolled to `V3.2`, not legacy `V3` | Yes |

### Recommendation
- **Cheapest white-box path:** `潞晨云 + RTX 3090`. If you are okay running the 14B models with `tensor_parallel_size=2` on `2×24GB`, it is the cheapest fully public China quote I could verify: about `¥46–92` for the whole 5-model local fleet.
- **Cheapest black-box path by model:** `GPT-4.1 -> OpenAI direct`, `GPT-5.1 -> OpenAI direct`, `Claude Sonnet 4.6 -> Anthropic direct` (OpenRouter ties on price), `DeepSeek-V3 -> OpenRouter deepseek-chat-v3-0324` if you need the V3 lineage specifically; otherwise `DeepSeek direct` is the best default if `V3.2` is acceptable.
- **Operationally easiest mainland-China stack:** local white-box on `潞晨云` or `矩池云`, plus `DeepSeek direct` and China-accessible small-model APIs from `SiliconFlow`/`百炼`. `OpenAI` and `Anthropic` direct are not mainland-supported.

### Full-run cost estimate
Using the mid-case token assumption above for the **4 black-box models**:
- `DeepSeek-V3` via OpenRouter `v3-0324`: about **`$14.2`**
- `GPT-4.1`: about **`$143.4`**
- `GPT-5.1`: about **`$115.2`**
- `Claude Sonnet 4.6`: about **`$230.4`**
- **Black-box subtotal:** about **`$503`**
- **White-box subtotal:** about **`¥46–92`** on the cheapest verified local-GPU plan
- **Full experiment total:** roughly **`$510–516 equivalent`** in the mid case; a practical low/high band is about **`$260` to `$760`** depending on prompt length

Two caveats matter:
- If you can use **Batch APIs**, `OpenAI` and `Anthropic` can cut their portions by roughly `50%`, pushing the mid-case total much lower.
- If you relax the **white-box + logprob** requirement, `SiliconFlow` is so cheap on the listed Qwen/GLM small models that renting GPUs stops being obviously better.
