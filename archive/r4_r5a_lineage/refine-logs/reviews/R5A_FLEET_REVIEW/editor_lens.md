---
role: Editor / narrative and venue-fit
session: R5A Fleet Review
thread_id: 019d9417-4472-72c0-8693-d0e2a1f53659
model_reasoning_effort: xhigh
generated: 2026-04-15
---

**Verdict**

From the editor/venue-fit lens, the main paper should carry **7 models, not more**. `6` is cleanest; `7` is still publishable; `8+` becomes a model-zoo problem unless most per-model detail is pushed to appendix. The absence of GPT is **not an automatic reject**, but if the paper claims coverage of "widely adopted" or "frontier" LLMs, it is a **serious reviewer-visible weakness**. Add exactly **one** OpenAI model.

Reviewer priority at EMNLP is usually: **frozen, well-documented, reproducible model choices first; one or two high-impact current references second**. They do not reward "we chased every new release" as much as they reward "the fleet is interpretable and pinnable."

**Concern-by-Concern**

1. **Capability ladder mismatch**
- Diagnosis: **Real**, especially for `PCSG`; **moderate** for `CMMD`.
- Recommended action: Replace `Qwen3-14B` with **`Qwen3-8B`** in the **main fleet**. That gives a much cleaner `7B / 8B / 9B` white-box ladder and creates a more defensible `Qwen2.5-7B -> Qwen3-8B` near-matched vendor pair.
- Trade-off: You give up some absolute model strength, but gain a much cleaner paper story. For EMNLP, that is worth it.

2. **Reasoning mode not unified**
- Diagnosis: **Real** and easy for reviewers to understand as a confound.
- Recommended action: Run `Qwen3` with **thinking OFF** in the main fleet. If you want, run thinking ON as an **appendix sensitivity** on a subset, not as a full second fleet.
- Trade-off: Slightly less "best possible" performance, but far less ambiguity in interpretation.

3. **No OpenAI model**
- Diagnosis: **Near-deal-breaker narratively**, though not methodologically fatal.
- Recommended action: Add **one** OpenAI model. My recommendation is **`gpt-5.1-2025-11-13`**.
- Why this one: It is snapshottable, officially documented, and its **Sep 30, 2024** knowledge cutoff adds a useful mid-late anchor instead of just duplicating the latest frontier slot.
- Estimated 3,200-case cost: about **$2.8** at `300 in / 50 out` tokens per case.
- Alternative: `gpt-5.4-2026-03-05` if you want maximum "latest OpenAI" prestige; estimated cost about **$4.8**. I would still prefer `GPT-5.1` for this paper because the temporal staircase is cleaner.

4. **SOTA timeliness**
- Diagnosis: The premise is already outdated. **As of April 15, 2026, Anthropic had already released Claude Sonnet 4.6 on February 17, 2026.**
- Recommended action: **Do not chase hypothetical Claude 4.7.** Either upgrade now to **Claude Sonnet 4.6** and freeze it, or stay on 4.5. From the editor lens, **4.6 is the better choice** if your access path can be pinned reliably.
- Estimated 3,200-case cost: about **$5.3**.
- Trade-off: Slightly more moving parts than staying on 4.5, but much better reviewer optics at submission time.

5. **Hardware and budget**
- Diagnosis: **Real** for white-box logprob detectors. Mixed `fp16 / Q8 / Q4` weakens the narrative.
- Recommended action: Use cloud GPU to **standardize precision**, not to add more models. If cloud is unavailable, I would rather **shrink** the white-box fleet than defend mixed-precision main results.
- Trade-off: More runtime cost, but stronger reproducibility and cleaner rebuttal language.

**Revised Fleet Proposal**

| # | Model | Cutoff | Access | Editorial role |
|---|---|---|---|---|
| 1 | Qwen 2.5-7B-Instruct | 2023-10 | white-box | oldest open Chinese anchor |
| 2 | DeepSeek-V2.5 | ~2024-03 | black-box | early hosted Chinese anchor |
| 3 | GLM-4-9B-0414 | 2024-06-30 | white-box | mid anchor with explicit cutoff |
| 4 | DeepSeek-V3-0324 | 2024-07 | black-box | later Chinese hosted anchor |
| 5 | GPT-5.1 (`gpt-5.1-2025-11-13`) | 2024-09-30 | black-box | must-have GPT reference |
| 6 | Qwen3-8B, thinking OFF | 2025-01 | white-box | near-matched late Qwen anchor |
| 7 | Claude Sonnet 4.6 | 2025-08 reliable | black-box | current Anthropic high-impact anchor |

If `Sonnet 4.6` cannot be pinned cleanly in your final infra, the fallback is to keep **`claude-sonnet-4-5-20250929`** and explain that choice explicitly.

**Design Principles**

- Keep the **main fleet at 7 max**; push extra checkpoints and mode variants to appendix.
- Include **exactly one GPT** and **exactly one Claude** for reviewer legitimacy.
- Maintain at least **one near-matched same-vendor cutoff pair** in the white-box set.
- Standardize inference regime in the main claim: **no mixed thinking modes** and preferably **no mixed precision**.
- Frame vendor diversity as **cross-vendor / cross-corpus-ecology robustness**, not as an overclaimed causal control.

**Entity Masking Figure**

For the paper figure, **Option B** reads best as the "category-preserving" arm, but keep it **minimal**. I would not use something as loaded as `某著名互联网巨头`; it injects salience cues. Use something closer to sector-only or sector-plus-coarse-tier. `Option C` is appendix material, not main-figure material.

**Sources**
- Anthropic model overview: https://platform.claude.com/docs/en/about-claude/models/overview
- Anthropic Sonnet 4.6 announcement: https://www.anthropic.com/news/claude-sonnet-4-6
- OpenAI GPT-5.1 model docs: https://developers.openai.com/api/docs/models/gpt-5.1
- OpenAI GPT-5.4 model docs: https://developers.openai.com/api/docs/models/gpt-5.4
- Qwen3 official blog: https://qwenlm.github.io/blog/qwen3/
- ARR Responsible NLP checklist: https://aclrollingreview.org/responsibleNLPresearch/
