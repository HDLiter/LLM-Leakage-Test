# Decision: Black-box Fleet Refresh

Date: 2026-05-03

## Inventory

OpenAI currently exposes GPT-5.5 as the latest frontier API model, with
snapshot `gpt-5.5-2026-04-23` and a Dec 01, 2025 knowledge cutoff. The
same official model catalog still exposes GPT-5.1 with snapshot
`gpt-5.1-2025-11-13` and a Sep 30, 2024 knowledge cutoff, and GPT-4.1
with snapshot `gpt-4.1-2025-04-14` and a Jun 01, 2024 knowledge cutoff.

Sources:
- OpenAI GPT-5.5 model page: <https://developers.openai.com/api/docs/models/gpt-5.5>
- OpenAI GPT-5.1 model page: <https://developers.openai.com/api/docs/models/gpt-5.1>
- OpenAI GPT-4.1 model page: <https://developers.openai.com/api/docs/models/gpt-4.1>

Anthropic currently lists Claude Opus 4.7, Claude Sonnet 4.6, and Claude
Haiku 4.5 in the current-model comparison. The Claude API ID for Sonnet
4.6 is `claude-sonnet-4-6`; the page lists a reliable knowledge cutoff
of Aug 2025 and a broader training data cutoff of Jan 2026. Sonnet 4.6
supports extended/adaptive thinking, so R5A keeps `extended_thinking_off`
for baseline P_predict.

Sources:
- Anthropic model overview: <https://platform.claude.com/docs/en/about-claude/models/overview>
- Anthropic Sonnet 4.6 announcement: <https://www.anthropic.com/news/claude-sonnet-4-6>

DeepSeek currently exposes V4 Flash and V4 Pro on the direct API as
`deepseek-v4-flash` and `deepseek-v4-pro`. DeepSeek's V4 preview release
note says `deepseek-chat` and `deepseek-reasoner` currently route to V4
Flash and will be retired on 2026-07-24, so `deepseek-chat` is no longer
an acceptable stable fleet pin. The public V4 model card describes the
V4 Flash and Pro model family, context length, precision regime, and
benchmarks, but does not publish a training or reliable-knowledge cutoff.
An authenticated `GET /v1/models` check against the official DeepSeek API
on 2026-05-03 returned only `deepseek-v4-flash` and `deepseek-v4-pro`,
so V3-0324 is not available as a stable official-direct API pin.

Sources:
- DeepSeek V4 preview release: <https://api-docs.deepseek.com/news/news260424>
- DeepSeek models and pricing: <https://api-docs.deepseek.com/quick_start/pricing>
- DeepSeek V4 Pro model card: <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md>

OpenRouter was checked as an availability cross-check, not as the chosen
execution route. Its catalog still lists `openai/gpt-4.1`,
`openai/gpt-5.1`, `anthropic/claude-sonnet-4.6`,
`deepseek/deepseek-chat-v3-0324`, `deepseek/deepseek-v4-flash`, and
`deepseek/deepseek-v4-pro`. SiliconFlow also lists V3 and V4 variants,
but the selected DeepSeek route is official direct because it is cheaper
and because the user's DeepSeek key already exposes both V4 models.

## Selection

The fleet remains 4 black-box models, 14 P_predict-eligible models, 12
P_logprob-eligible models, and 2 temporal PCSG pairs.

| Fleet key | Provider | API model name | Cutoff date | Cutoff source | Decision |
|---|---|---:|---|---|---|
| `deepseek-v4-pro` | DeepSeek | `deepseek-v4-pro` | 2026-04-24 | `operator_inferred` | Swapped from `deepseek-v3-0324` because the official DeepSeek API no longer provides a durable V3-0324 pin and `deepseek-chat` is now a mutable compatibility route. V4 Pro is selected over V4 Flash for the black-box P_predict slot because capability matters more than the small official-direct price delta. The date is the V4 API release date used as a conservative upper-bound proxy, not a vendor cutoff. |
| `gpt-4.1` | OpenAI | `gpt-4.1-2025-04-14` | 2024-06-01 | `vendor_stated` | Kept as the clean non-reasoning OpenAI control near GLM-4's 2024-06 cutoff. |
| `gpt-5.1` | OpenAI | `gpt-5.1-2025-11-13` | 2024-09-30 | `vendor_stated` | Kept instead of GPT-5.5 because it preserves a useful 2024-Q3 temporal anchor; GPT-5.5's Dec 2025 cutoff would push the OpenAI frontier slot too close to the late-bound Claude/DeepSeek end. |
| `claude-sonnet-4.6` | Anthropic | `claude-sonnet-4-6` | 2025-08-31 | `vendor_stated` | Kept instead of Opus 4.7 because Sonnet 4.6 is cheaper/faster, has the desired Aug 2025 reliable cutoff, and still gives Anthropic frontier coverage. |

## Risks

- DeepSeek V4 Pro has no published training or reliable-knowledge
  cutoff in the checked vendor/model-card sources. Treat `2026-04-24`
  as an operator-inferred release-date upper bound and a high-risk Path-E
  probe input, not as ground truth.
- Anthropic's `claude-sonnet-4-6` is versioned but not dated like older
  Claude snapshot IDs. The official API docs present it as the current
  Claude API ID. Preserve raw provider metadata and response hashes at
  run time.
- GPT-5.1 is no longer OpenAI's newest frontier model. This is an
  intentional statistical-design choice to preserve cutoff spread.

## Sub-decisions

- D1 DeepSeek: move to official-direct `deepseek-v4-pro`. The old direct
  `deepseek-chat` alias is mutable and scheduled for retirement, while
  authenticated official `/v1/models` exposes only V4 Flash and V4 Pro.
  `deepseek-v4-pro` is the better P_predict anchor; V3-0324 remains
  available through OpenRouter/SiliconFlow but is not selected because
  the project will use the cheaper official DeepSeek route.
- D2 Claude: keep Sonnet 4.6. Opus 4.7 is more capable but has a Jan 2026
  reliable cutoff and higher cost; Sonnet 4.6 better preserves the late
  2025 anchor while staying economical for P_predict.
- D3 GPT: keep dual `gpt-4.1` plus `gpt-5.1`. GPT-4.1 is the clean
  non-reasoning control; GPT-5.1 fills the 2024-Q3 anchor. GPT-5.5 is
  documented in inventory but not selected.

## Migration Impact

Files edited in this refresh:
- `config/fleet/r5a_fleet.yaml`: fleet version, DeepSeek key/API slug,
  OpenAI cutoff-source upgrades, GPT-5.1 slug, Claude slug.
- `config/prompts/R5A_OPERATOR_SCHEMA.md`: black-box roster text.
- `plans/phase7-pilot-implementation.md`: illustrative fleet block.
- `PENDING.md`: close the black-box API model-name item.

Historical review logs and archived documents retain their original
model names as contemporaneous records. This memo supersedes those names
for active fleet execution.
