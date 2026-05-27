# LLM Training-Data Cutoff Dates and Reliability

## How to read these estimates

This report separates **reliable knowledge cutoff** from **training-data cutoff** whenever sources allow it. In practice, those are often not the same thing. Anthropic is the only vendor in this set that publicly defines the distinction in current docs: its API docs say “Reliable knowledge cutoff indicates the date through which a model’s knowledge is most extensive and reliable” while “Training data cutoff is the broader date range of training data used.” Meta and OpenAI publicly expose only a **knowledge cutoff** for the models in scope here; Qwen, GLM, and DeepSeek generally publish training scale and data composition, but not a dated cutoff. citeturn9view3turn9view0turn9view1turn41view0turn41view1turn43view0turn18view2turn16view0

A second important finding is that a “cutoff date” is rarely a knife-edge boundary. FreshQA-style work shows that LLMs struggle on fast-changing knowledge after their cutoff, but they do not instantly become ignorant the next day. Daily-news temporal studies show a steeper decline after cutoff rather than a perfectly sharp cliff, and newer contamination work shows that measured “post-cutoff decay” is itself sensitive to how the questions are constructed. In other words: **the date is useful, but the frontier is fuzzy**. citeturn37view1turn37view0turn37view2

For the summary table, I prioritize the **best public training-data estimate**. Where a vendor does **not** publish a separate training-data cutoff, I mark the estimate as a **proxy** based on the published knowledge cutoff. Where only community evidence exists, I mark that clearly.

## Open-weight Chinese-rooted families

**Qwen2.5 — Qwen/Qwen2.5-{1.5B,3B,7B,14B,32B}-Instruct**

**Official / vendor-stated cutoff.** I found **no official dated cutoff** in the public Qwen2.5 model card, blog, or technical report. The official materials say Qwen2.5 was trained on “up to 18 trillion tokens” and that the family has “significantly more knowledge,” but they do not attach a date to that freshness claim. citeturn20search18turn41view2turn22search0

**Academic / research-measured cutoff.** I found **no model-specific academic paper** that independently estimates a Qwen2.5 cutoff date. The closest relevant academic literature is cross-model temporal work showing that post-cutoff performance usually declines gradually and that contamination-style cutoff probes are highly method-sensitive. That matters for Qwen2.5 because it means a single probe question is weak evidence for or against a hard date. citeturn37view1turn37view2

**Community / user-probe evidence.** The strongest community evidence is a Qwen GitHub discussion where a commenter summarizes the estimate as “late 2023 for some subset of the training data,” and the community cutoff-date repository records Qwen2.5 as “end of 2023.” Another Qwen discussion starts from the widely repeated “October 2023” figure but never gets an authoritative maintainer confirmation. citeturn21view0turn22search1turn40view0

**Knowledge vs training cutoff.** Public Qwen docs do **not** separate knowledge cutoff from training-data cutoff for Qwen2.5. The best publicly available estimate is therefore a **community-inferred training tail**, not a vendor-declared reliable-knowledge date. citeturn20search18turn41view2turn21view0turn40view0

**Sharpness vs gradualness.** No Qwen2.5-specific date-decay curve surfaced in the sources I reviewed. The best evidence is therefore indirect: fast-changing-knowledge studies and contamination papers imply a **taper**, not a single-day collapse. citeturn37view1turn37view0turn37view2

**Cross-source spread.** The live spread is roughly **2023-10 to 2023-12**, with “late 2023 / end of 2023” better supported than any exact day. citeturn21view0turn22search1turn40view0

**Chinese / non-English freshness.** Qwen’s public materials emphasize multilingual strength, but I found **no direct evidence** that Chinese-language data extends materially later than the English-side estimate. So the safest reading is: **Chinese coverage is strong, but not demonstrably fresher**. citeturn20search18turn41view2

**Overall rating.** **Low.** There is no official dated cutoff; the best estimate rests on converging community inference rather than vendor disclosure or an independent probing paper. citeturn21view0turn40view0

**Best estimate:** **late 2023**, with an uncertainty band of **October–December 2023**. citeturn21view0turn22search1turn40view0

**Qwen3 — Qwen/Qwen3-{4B,8B,14B,32B}**

**Official / vendor-stated cutoff.** I found **no official dated cutoff** for Qwen3. The Qwen3 launch post says the family supports **119 languages and dialects**, uses **approximately 36 trillion tokens**, and describes a three-stage pretraining process, but again gives no date. citeturn43view0

**Academic / research-measured cutoff.** I found **no model-specific academic cutoff estimate** for Qwen3. The relevant academic result is again methodological: temporal decay around a nominal cutoff is informative but fragile, and absence of a sharp decay does not prove absence of fresher training data. citeturn37view2

**Community / user-probe evidence.** Community evidence is sparse and inconsistent. A GitHub issue paraphrases a Qwen Chat self-report of **“2024-10”**, while a Reddit discussion says Qwen3 appears to have knowledge “until mid 2024.” The community cutoff repository still lists Qwen3 as **unknown**. That combination is helpful as a spread estimate, but not enough for a sharp date. citeturn3search3turn20search1turn40view0

**Knowledge vs training cutoff.** Qwen does not publish the distinction here. So any Qwen3 estimate is necessarily a **community probe of apparent knowledge freshness**, not a vendor-stated reliable-knowledge date and not a verified training-data endpoint. citeturn43view0turn3search3turn20search1

**Sharpness vs gradualness.** There is no Qwen3-specific temporal curve in the sources I found. The broader literature argues against treating the cutoff as crisp. citeturn37view1turn37view2

**Cross-source spread.** The meaningful spread is roughly **mid-2024 to 2024-10**. That is much weaker than the user’s current **2025-01** estimate; I found **no source** supporting a January 2025 Qwen3 training cutoff. citeturn3search3turn20search1

**Chinese / non-English freshness.** Qwen3’s multilingual story is much stronger than most models here: the official launch says **119 languages and dialects**, explicitly including simplified Chinese, traditional Chinese, and Cantonese. That is good evidence of deep Chinese coverage, but I still found **no direct proof of a later Chinese-only cutoff**. citeturn43view0

**Overall rating.** **Low.** Excellent official detail on training scale and languages, but no official date; community probes disagree and remain shallow. citeturn43view0turn3search3turn20search1

**Best estimate:** **late 2024**, centered around **2024-10**, with an uncertainty band of **mid-2024 to 2024-10**. citeturn3search3turn20search1

**GLM-4 — THUDM/glm-4-9b-chat**

**Official / vendor-stated cutoff.** I found **no official dated cutoff** for GLM-4-9B-Chat. The ChatGLM paper says the pretraining corpus is “around ten trillion tokens” and is multilingual, “mostly English and Chinese,” but it does not provide a dated cutoff. The model card likewise lists capabilities and context length, not data freshness dates. citeturn18view2turn44view0turn18view1

**Academic / research-measured cutoff.** I found **no academic paper** that independently estimates a GLM-4 cutoff date. The official research paper is descriptive rather than temporal-probing. citeturn18view2turn42search11

**Community / user-probe evidence.** Community/model-directory evidence is weak and inconsistent. ApX lists **“Apr 2024”** for GLM-4-9B, while the same site lists **“Jan 2024”** for GLM-4-9B-Chat-1M; another comparison page on llm-stats says GLM models often do **not** specify an official cutoff at all. That gives a rough range, but not a reliable estimate. citeturn42search1turn42search15turn42search4

**Knowledge vs training cutoff.** There is **no public split** between knowledge cutoff and training-data cutoff for the open GLM-4-9B-Chat snapshot. Community pages appear to treat “knowledge cutoff” as a guessed freshness date, not a vendor declaration. citeturn42search1turn42search15turn42search4

**Sharpness vs gradualness.** No GLM-4-specific curve surfaced. The general temporal-probing literature again counsels against assuming any hard cliff. citeturn37view1turn37view2

**Cross-source spread.** The weak community spread is **2024-01 to 2024-04**. That is substantially earlier than a pure “2024-06 release-date proxy,” and I found nothing solid supporting a June 2024 training cutoff itself. citeturn42search1turn42search15turn42search3

**Chinese / non-English freshness.** GLM’s official paper explicitly says the corpus is “mostly English and Chinese,” which is better evidence of Chinese representation than most Western model cards provide. But, again, it does **not** imply a later Chinese cutoff. citeturn18view2

**Overall rating.** **Low.** No official date, no probing paper, and community directories disagree by months. citeturn18view2turn42search1turn42search15

**Best estimate:** **no reliable source found** for a true dated cutoff; the **weak community-only range is January–April 2024**. citeturn42search1turn42search15turn42search4

**DeepSeek — deepseek-v4-pro**

**Official / vendor-stated cutoff.** I found **no official dated cutoff** for DeepSeek-V4-Pro. The release materials say V4-Pro launched on **2026-04-24**, and the Hugging Face card says the family was trained on “more than 32T” tokens, but no dated training or knowledge cutoff is published in the official V4 release docs I reviewed. citeturn11search0turn11search2turn16view0

**Academic / research-measured cutoff.** I found **no direct academic cutoff estimate** for DeepSeek-V4-Pro. The closest research-like external signal is NIST/CAISI’s evaluation that DeepSeek V4’s capabilities “lag behind the frontier by about 8 months.” That is **not** a cutoff date, but it is at least directionally compatible with a mid/late-2025 freshness window rather than anything near the April 2026 release date. citeturn38search3

**Community / user-probe evidence.** Community/model-directory sources cluster around **2025-05**. TypingMind lists **“Knowledge Cutoff 2025-05”** for DeepSeek V4 Pro via OpenRouter, and 36Kr’s English write-up of Chinese probing says the model’s knowledge cutoff “currently still remains in 2025.” That is still community evidence, but it is much better than a release-date proxy. citeturn13view1turn15search11

**Knowledge vs training cutoff.** Public DeepSeek materials do not distinguish them for V4-Pro. So the best public date here is an **apparent-knowledge estimate** from community tooling, not an official training-data disclosure. citeturn16view0turn13view1

**Sharpness vs gradualness.** No model-specific decay curve surfaced. The safest reading is still gradualness. citeturn37view1turn37view2

**Cross-source spread.** The meaningful public spread is roughly **2025-05 through “some time in 2025,”** with NIST’s capability-lag signal loosely consistent with **late summer 2025** as a capability-freshness proxy. I would not sharpen that beyond a broad **Q2–Q3 2025** band. citeturn13view1turn15search11turn38search3

**Chinese / non-English freshness.** DeepSeek’s own card reports very strong **Chinese-SimpleQA** performance relative to its English **SimpleQA** score, which is indirect evidence that Chinese parametric knowledge is strong. But that is still not evidence of a later Chinese-only cutoff. citeturn16view0

**Overall rating.** **Low.** No vendor date; best estimate comes from community model tooling plus a qualitative Chinese probe. citeturn13view1turn15search11

**Best estimate:** **2025-05**, with an uncertainty band of roughly **Q2–Q3 2025**. citeturn13view1turn15search11turn38search3

## Meta Llama families

**Llama-3 — meta-llama/Meta-Llama-3-8B-Instruct**

**Official / vendor-stated cutoff.** Meta’s model card is explicit: in the table, the **8B** model is listed with a **“Knowledge cutoff” of “March, 2023,”** while the **70B** model is listed as **“December, 2023.”** That is a genuine within-family divergence, not a shared family cutoff. citeturn41view0

**Academic / research-measured cutoff.** I found no paper that revises Meta’s date, but the Daily Oracle paper uses Llama-3-8B in a continuous dated-news evaluation and finds that its temporal accuracy declines more steeply after the model’s own cutoff than before it. The same paper also notes that Llama-3-8B shows **smaller temporal declines than GPT-4** in that setup, which argues against a single hard cliff. citeturn37view0

**Community / user-probe evidence.** Community discussion immediately noticed the family split: one Reddit thread highlights that the **8B cutoff is March 2023** while the **70B cutoff is December 2023**, and the community cutoff repository mirrors the same values. citeturn24search10turn40view0

**Knowledge vs training cutoff.** Meta publishes only a **knowledge cutoff** here, not a separate training-data cutoff. So for the 8B snapshot, **March 2023 is the best public proxy**, but not a vendor-disclosed “latest training token” date. citeturn41view0

**Sharpness vs gradualness.** The strongest evidence points to a **gradual taper that steepens after the cutoff**, not a binary wall. citeturn37view0turn37view2

**Cross-source spread.** For the specific **8B** snapshot, the spread is essentially **March 2023 only**. The disagreement in public discourse is not about the 8B value itself; it is about whether people mistakenly generalize the 70B value to the whole family. citeturn41view0turn24search10

**Chinese / non-English freshness.** The Llama 3 card explicitly marks use in languages other than English as out of scope. I found **no evidence** of fresher Chinese-language data than the English-side cutoff. citeturn41view0

**Overall rating.** **Medium.** High confidence on the **knowledge-cutoff proxy** because Meta states it directly; medium confidence on “training-data cutoff” as a separate concept because Meta does not publish it. citeturn41view0

**Best estimate:** **March 2023 (proxy from Meta’s knowledge cutoff)**. citeturn41view0

**Llama-3.1 — meta-llama/Llama-3.1-8B-Instruct**

**Official / vendor-stated cutoff.** Meta’s Llama 3.1 model card states **“December 2023”** in the **Knowledge cutoff** column, and unlike Llama 3 it applies that date across the 8B, 70B, and 405B 3.1 variants shown in the table. citeturn41view1

**Academic / research-measured cutoff.** I found **no independent academic date estimate** specifically for Llama-3.1-8B. The most useful academic evidence remains generic: temporal decline around a declared cutoff is real but fuzzy, and contamination-style decay tests are method-sensitive. citeturn37view0turn37view2

**Community / user-probe evidence.** The community cutoff repository records **Llama-3.1-8B** and **Llama-3.1-70B** as **2023.12**, matching Meta’s own card. I did not find a serious conflicting community estimate for the 8B Llama-3.1 snapshot. citeturn40view0turn41view1

**Knowledge vs training cutoff.** As with Llama 3, Meta publishes a knowledge cutoff, not a separate training-data cutoff. So **December 2023 is best treated as a training-cutoff proxy**. citeturn41view1

**Sharpness vs gradualness.** No Llama-3.1-specific decay curve surfaced in the sources I found. The broader evidence still points to **gradual degradation** rather than a single-day drop. citeturn37view1turn37view2

**Cross-source spread.** For the 8B snapshot, the spread is effectively **December 2023 only**. citeturn41view1turn40view0

**Chinese / non-English freshness.** Llama 3.1 is more multilingual than Llama 3, and Meta says it was trained on a broader collection of languages than the eight languages it officially supports. Still, I found **no direct Chinese-specific cutoff evidence**, and Chinese is not in the short supported-language list in the card. citeturn41view1

**Overall rating.** **Medium.** Strong vendor agreement on the knowledge cutoff; no separate training-date disclosure. citeturn41view1turn40view0

**Best estimate:** **December 2023 (proxy from Meta’s knowledge cutoff)**. citeturn41view1

## OpenAI snapshots

**OpenAI — gpt-4.1-2025-04-14**

**Official / vendor-stated cutoff.** OpenAI’s launch post says GPT-4.1 has a **“refreshed knowledge cutoff of June 2024,”** and the model page gives **“Jun 01, 2024 knowledge cutoff.”** I found **no separate official training-data cutoff** for the pinned `gpt-4.1-2025-04-14` snapshot. citeturn35view2turn9view0

**Academic / research-measured cutoff.** I found **no public academic paper** that independently estimates GPT-4.1’s training-data cutoff date. citeturn35view2turn9view0

**Community / user-probe evidence.** Community sources largely just echo the OpenAI docs: the community cutoff repository records GPT-4.1 as **2024.06.01**, and Hacker News discussion around launch focuses on the June 2024 date rather than uncovering a later training tail. I did **not** find credible public probing that pushes GPT-4.1 materially later than OpenAI’s stated knowledge cutoff. citeturn40view0turn25search11

**Knowledge vs training cutoff.** OpenAI only gives the **knowledge cutoff**. So the best public “training cutoff” estimate is only a **proxy lower bound** from that knowledge date. citeturn35view2turn9view0

**Sharpness vs gradualness.** The best public guidance is cross-model rather than GPT-4.1-specific: temporal degradation is real but not perfectly sharp, and prompt-based self-reports of cutoff can be unreliable relative to the docs. OpenAI staff later confirmed, in a different cutoff bug thread, that documentation was the source of truth when a model self-reported an older date. citeturn37view1turn37view2turn26search6

**Cross-source spread.** For the published knowledge cutoff, the spread is basically **June 2024 only**. The actual training-data endpoint remains undisclosed. citeturn35view2turn9view0turn40view0

**Chinese / non-English freshness.** I found **no direct evidence** of a Chinese-specific cutoff differing from the headline June 2024 figure. citeturn35view2turn9view0

**Overall rating.** **Medium.** High confidence on the official **knowledge cutoff**; low visibility into the true training-data tail. citeturn35view2turn9view0

**Best estimate:** **June 2024 (proxy from OpenAI’s knowledge cutoff)**. citeturn35view2turn9view0

**OpenAI — gpt-5.1-2025-11-13**

**Official / vendor-stated cutoff.** OpenAI’s model page states **“Sep 30, 2024 knowledge cutoff.”** The broader GPT-5.1 launch materials identify November 2025 as the release window, but I found **no separate official training-data cutoff** for the pinned `gpt-5.1-2025-11-13` snapshot. citeturn9view1turn35view0turn35view1

**Academic / research-measured cutoff.** I found **no public academic paper** independently estimating GPT-5.1’s training-data endpoint. citeturn9view1turn35view0

**Community / user-probe evidence.** Community sources mostly repeat the doc value: the cutoff-date repository records **2024.09.30**, and public discussion on HN highlighted the long gap between the September 2024 knowledge date and the November 2025 release. I did not find reliable evidence of a later hidden training cutoff. citeturn40view0turn25search8

**Knowledge vs training cutoff.** As with GPT-4.1, public OpenAI materials provide only a **knowledge cutoff**, so the “training cutoff” here is a **proxy** rather than a disclosed fact. citeturn9view1turn35view0

**Sharpness vs gradualness.** Again, the best evidence is generic rather than GPT-5.1-specific: cutoff behavior should be interpreted as a fuzzy frontier, and vendor docs are more trustworthy than raw self-reporting from the model. citeturn37view1turn37view2turn26search6

**Cross-source spread.** Public knowledge sources converge on **2024-09-30**; the true training-data tail remains unreported. citeturn9view1turn40view0

**Chinese / non-English freshness.** I found **no direct Chinese-specific cutoff signal** for GPT-5.1. citeturn9view1

**Overall rating.** **Medium.** Strong confidence in the published knowledge date, but not in any deeper claim about actual latest training tokens. citeturn9view1turn40view0

**Best estimate:** **2024-09-30 (proxy from OpenAI’s knowledge cutoff)**. citeturn9view1

## Anthropic snapshot

**Anthropic — claude-sonnet-4-6**

This is the messiest case in the set, because **Anthropic’s own official sources disagree**.

**Official / vendor-stated cutoff.** The current API docs overview says **“Reliable knowledge cutoff Aug 2025”** and **“Training data cutoff Jan 2026”** for Claude Sonnet 4.6, and also says that Claude 4.6 model IDs are **pinned snapshots**, not evergreen aliases. But Anthropic’s Transparency Hub says **“Claude Sonnet 4.6 has a knowledge cutoff date of May 2025”** and that it was trained on public internet data **“as of May 2025.”** The Sonnet 4.6 system card itself also says the model was trained on internet data **“up to May 2025.”** Meanwhile Anthropic’s Help Center says **“Claude Sonnet 4.6 was trained on data up until August 2025.”** citeturn9view3turn28view0turn31view1turn33view0turn28view1

**Academic / research-measured cutoff.** I found **no independent academic paper** resolving this conflict. citeturn9view3turn28view0

**Community / user-probe evidence.** The community cutoff-date repository adopts the **Jan 2026 training / Aug 2025 reliable-knowledge** interpretation, matching Anthropic’s current API docs rather than the release-time system card and Transparency Hub language. That is useful, but it is still downstream of Anthropic’s own conflicting docs. citeturn40view0turn9view3

**Knowledge vs training cutoff.** Anthropic is the only vendor here that formally distinguishes them, but Sonnet 4.6 is also the clearest example of **why that distinction must be handled carefully**: the official range spans **May 2025** (Transparency Hub and system card), **Aug 2025** (Help Center, and reliable-knowledge in API docs), and **Jan 2026** (training-data cutoff in the API docs overview). citeturn9view3turn28view0turn28view1turn31view1

**Sharpness vs gradualness.** Anthropic’s own distinction between “reliable knowledge cutoff” and “training data cutoff” already implies a **taper** rather than a hard wall. The external temporal-probing literature points the same way. citeturn9view3turn37view1turn37view2

**Cross-source spread.** The official spread is very large: **May 2025 to Jan 2026**. That is not normal vendor noise; it is a real contradiction across first-party sources. citeturn9view3turn28view0turn28view1turn31view1

**Chinese / non-English freshness.** I found **no direct Chinese-specific cutoff evidence** for Claude Sonnet 4.6. citeturn9view3turn28view0

**Overall rating.** **Low.** The vendor is unusually transparent in principle, but the official first-party documents for this exact pinned snapshot are internally inconsistent. citeturn9view3turn28view0turn28view1turn31view1

**Best estimate:** If forced to pick a single value for the **pinned release snapshot**, I would anchor on **May 2025** because it appears in both the **release-time system card** and the **Transparency Hub**, which are the most snapshot-tethered artifacts I found. But the full honest uncertainty range is **May 2025 to Jan 2026**. citeturn28view0turn31view1turn9view3turn28view1

## What the evidence says about sharpness, disagreement, and non-English freshness

Across all nine targets, the most robust conclusion is not the exact dates; it is the **shape of uncertainty**. Public model cards and API docs often expose only a **knowledge cutoff**, not the latest token actually ingested during pretraining or post-training. When vendors do publish a separate training-corpus endpoint, as Anthropic does, the resulting picture is more nuanced and sometimes contradictory. citeturn9view3turn28view0turn28view1

On **sharpness**, the literature points strongly toward **gradual decay**. FreshQA shows LLM weakness on fast-changing knowledge; Daily Oracle shows noticeably steeper degradation after cutoff than before it; and the newer contamination literature shows that the measured “drop” depends heavily on whether benchmark questions are verbatim, cloze-style, or LLM-transformed. That means any cutoff date should be read as a **fuzzy frontier with a tail of partial familiarity**, not as a crisp line where knowledge disappears. citeturn37view1turn37view0turn37view2

On **Chinese / non-English freshness**, the strongest positive evidence is for the Chinese-rooted families. Qwen3 explicitly covers **119 languages and dialects**, including multiple Chinese varieties. GLM-4’s paper says its corpus is “mostly English and Chinese.” DeepSeek’s own reported **Chinese-SimpleQA** score is stronger than its English **SimpleQA** score. But none of those facts, by themselves, proves a later China-web cutoff than the headline estimate. For Llama 3 and Llama 3.1, the public evidence is weaker still, and for GPT-4.1, GPT-5.1, and Claude Sonnet 4.6 I found **no vendor-published Chinese-specific cutoff evidence at all**. citeturn43view0turn18view2turn16view0turn41view0turn41view1turn9view0turn9view1turn9view3

## Summary table

| Model | Best training-cutoff estimate | Uncertainty range | Sharp or gradual | Reliability | Key sources |
|---|---|---|---|---|---|
| Qwen2.5 | **Late 2023** | 2023-10 to 2023-12 | Gradual / tapered | **L** | Qwen blog + HF card; GitHub discussion + community repo citeturn20search18turn41view2turn21view0turn40view0 |
| Qwen3 | **Late 2024** | Mid-2024 to 2024-10 | Gradual / tapered | **L** | Qwen3 launch post; GitHub issue snippet; Reddit probe citeturn43view0turn3search3turn20search1 |
| Llama-3 8B | **March 2023** † | Essentially fixed at 2023-03 | Gradual after cutoff | **M** | Meta HF card; Daily Oracle; community cross-check citeturn41view0turn37view0turn24search10 |
| Llama-3.1 8B | **December 2023** † | Essentially fixed at 2023-12 | Gradual / tapered | **M** | Meta HF card; community repo citeturn41view1turn40view0 |
| GLM-4-9B-Chat | **No reliable source found** ‡ | Weak community-only range: 2024-01 to 2024-04 | Gradual / tapered | **L** | ChatGLM paper; ApX community pages citeturn18view2turn42search1turn42search15 |
| DeepSeek V4 Pro | **2025-05** ‡ | Roughly 2025-Q2 to 2025-Q3 | Gradual / tapered | **L** | DeepSeek release/card; TypingMind; 36Kr; NIST/CAISI proxy citeturn16view0turn13view1turn15search11turn38search3 |
| gpt-4.1-2025-04-14 | **June 2024** † | Knowledge sources converge; true training tail unknown | Gradual / tapered | **M** | OpenAI launch post + model page citeturn35view2turn9view0 |
| gpt-5.1-2025-11-13 | **2024-09-30** † | Knowledge sources converge; true training tail unknown | Gradual / tapered | **M** | OpenAI model page + launch materials citeturn9view1turn35view0turn35view1 |
| claude-sonnet-4-6 | **May 2025** § | 2025-05 to 2026-01 | Explicitly gradual in Anthropic framing | **L** | Anthropic API docs, Transparency Hub, Help Center, system card citeturn9view3turn28view0turn28view1turn31view1 |

† Vendor publishes a **knowledge cutoff**, not a separate training-data cutoff; the date shown is the best public **proxy**.  
‡ No reliable vendor cutoff found; estimate is **community-only** and weak.  
§ Anthropic’s **official sources conflict**; the table uses the release-time system-card / Transparency-Hub reading as the anchor, but the full official spread is shown.

## Open questions and limitations

The biggest open problem is that **true training-data cutoff dates are usually underreported**. For OpenAI and Meta, the public record is strong on knowledge-cutoff dates but weak on the latest token actually ingested. For Qwen, GLM, and DeepSeek, public docs emphasize training scale and multilingual breadth more than dated freshness. For Claude Sonnet 4.6, the opposite problem appears: Anthropic publishes the distinction, but its first-party sources for this exact snapshot are inconsistent enough that the uncertainty band is wide. citeturn9view3turn28view0turn28view1turn20search18turn43view0turn18view2turn16view0

The second limitation is methodological. Public “probe the model by asking it about recent events” evidence is useful, but weak. Academic temporal work shows why: apparent cutoff effects depend on question construction, and model self-report about its own cutoff can be wrong. So the most trustworthy hierarchy, in this research pass, was: **release-time model card / system card > current vendor API docs > academic temporal probes > community model directories / forum probes**. citeturn37view2turn37view0turn26search6