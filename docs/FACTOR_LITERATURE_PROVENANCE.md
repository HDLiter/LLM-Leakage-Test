# FinMem-Bench — Per-Factor Literature Provenance Audit

**Date:** 2026-04-14
**Sweep:** R4 Literature Sweep Sub-task A (see `refine-logs/reviews/BENCHMARK_R4_LIT_SWEEP_KICKOFF.md`)
**Reviewer persona:** senior NLP / memorization researcher, fresh session, no R1-R4 attachment, systematic bibliographer
**Search method:** arxiv API + web_search, every citation verified in-session
**Scope:** 15 factors in the v5.3 active+reserve shortlist + 2 possible additions under investigation (Modality, Authority)

---

## URGENT — reviewer-visible adjacent prior art (already in library as of 2026-04-14)

- `Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents` (Li et al.; [arXiv:2510.07920](https://arxiv.org/abs/2510.07920)) — already in `related papers/Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf`.
- `Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance` (Benhenda; [arXiv:2601.13770](https://arxiv.org/abs/2601.13770)) — already in `related papers/Look-Ahead-Bench Standardized Benchmark.pdf`.

Neither paper is an exact factor-level clone of FinMem-Bench, but both are reviewer-visible related-work obligations. Flag is a **citation obligation reminder**, not a new discovery — ensure these are cited prominently alongside MemGuard-Alpha in the paper's related-work section, not buried.

## Factor 1 — Propagation Intensity
### Prior art
- Direct precedent exists. `Deduplicating Training Data Mitigates Privacy Risks in Language Models` (Kandpal et al.; [arXiv:2202.06539](https://arxiv.org/abs/2202.06539)) shows regeneration is superlinearly related to duplication count in training data.
- `Quantifying Memorization Across Neural Language Models` (Carlini et al.; [arXiv:2202.07646](https://arxiv.org/abs/2202.07646)) gives log-linear memorization laws and ties memorization to duplicate/frequent content.
- `Counterfactual Memorization in Neural Language Models` (Zhang et al.; [arXiv:2112.12938](https://arxiv.org/abs/2112.12938)) explicitly warns that standard memorization criteria correlate with repeated data, templated text, and public/common phrases.
- Strong language/domain-adjacent replication: `Quantifying Memorization and Detecting Training Data of Pre-trained Language Models using Japanese Newspaper` (Ishihara and Takahashi; [arXiv:2404.17143](https://arxiv.org/abs/2404.17143)) reports the same duplication/model-size/prompt-length pattern in Japanese newspaper PLMs.
- Search log: arXiv query `all:"duplication" AND all:"memorization" AND all:"language model"` was noisy, so exact-title/arXiv-author verification was used; web query `"Deduplicating Training Data Mitigates Privacy Risks in Language Models"` and related exact-title searches returned direct hits.
### Operationalization precedent
- Published work usually operationalizes this family as duplicate count, exposure/frequency, or near-duplicate detection.
- Our split into `event_burst` and `historical_family_recurrence` is literature-aligned in spirit but is still a new decomposition: same-event burstiness inside CLS versus historical recurrence of an event family/template.
- The robustness companion `surface_template_recurrence` is close to prior near-duplicate / repetitive-substring logic, but char-5gram TF-IDF cosine is our benchmark-specific implementation, not a copied recipe.
### Known failure modes
- Repetition measures can confound genuine public/common knowledge with model-specific memorization.
- Exact-duplicate counts miss paraphrase-level or template-level recurrence.
- Effects differ across model families; Carlini et al. explicitly caution against over-generalizing one fitted law across families.
### Effect direction precedent
- Validated in the literature: more duplication/frequency predicts more memorization/extraction risk.
- Ishihara's Japanese newspaper study points in the same direction and adds prompt-length amplification in a news domain.
### Alternative names
- Duplication
- Frequency
- Exposure count
- Repetition / redundancy
- Near-duplicate prevalence
### Novel vs prior-art verdict
- STRONG_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Strengthen. Suggested edit: `Propagation Intensity has strong memorization precedent, but our decomposition into event_burst and historical_family_recurrence is new. Treat these as exposure proxies rather than direct measures of true pretraining exposure; report them separately, with surface_template_recurrence as a robustness companion rather than a third co-equal construct.`
### New candidate papers to download
- P1: `Quantifying Memorization and Detecting Training Data of Pre-trained Language Models using Japanese Newspaper` ([arXiv:2404.17143](https://arxiv.org/abs/2404.17143))
- P1: `Deduplicating Training Data Makes Language Models Better` ([arXiv:2107.06499](https://arxiv.org/abs/2107.06499))

## Factor 2 — Cutoff Exposure
### Prior art
- Very strong precedent exists. `Dated Data: Tracing Knowledge Cutoffs in Large Language Models` (Cheng et al.; [arXiv:2403.12958](https://arxiv.org/abs/2403.12958)) directly studies effective cutoffs.
- `Set the Clock: Temporal Alignment of Pretrained Language Models` (Zhao et al.; [arXiv:2402.16797](https://arxiv.org/abs/2402.16797)) shows claimed cutoffs and actual time use can diverge.
- `Chronologically Consistent Large Language Models` (He et al.; [arXiv:2502.21206](https://arxiv.org/abs/2502.21206)), `Fake Date Tests` ([arXiv:2601.07992](https://arxiv.org/abs/2601.07992)), `A Test of Lookahead Bias in LLM Forecasts` ([arXiv:2512.23847](https://arxiv.org/abs/2512.23847)), `All Leaks Count, Some Count More` ([arXiv:2602.17234](https://arxiv.org/abs/2602.17234)), and `Look-Ahead-Bench` ([arXiv:2601.13770](https://arxiv.org/abs/2601.13770)) all treat temporal overlap / temporal leakage as central.
- Search log: arXiv query `all:"lookahead bias" AND all:"LLM"` returned direct hits; exact-title web searches returned the expected temporal papers.
- Specific search target not found: no verified published paper was found that uses a symmetric gray-band exclusion zone around the cutoff as a factor design. That appears to be your design choice, not a lifted precedent.
### Operationalization precedent
- Signed `cutoff_gap_days` and pre/post-cutoff binning match the literature's logic closely.
- The gray-band exclusion is defensible, but I did not verify a direct published precedent for that exact choice.
### Known failure modes
- Reported cutoff dates are not equivalent to effective/resource-level exposure.
- Temporal instructions alone do not reliably suppress leakage.
- Evidence of memorization is only a lower bound on encoded post-event knowledge.
- In finance, in-sample performance can also be distorted by non-temporal mechanisms such as entity distraction.
### Effect direction precedent
- Strongly validated: overlap with the model's training era inflates in-sample performance and threatens causal interpretation.
- Important counterweight: Glasserman and Lin ([arXiv:2309.17322](https://arxiv.org/abs/2309.17322); venue record via EconBiz) find that distraction can dominate look-ahead bias in some in-sample sentiment setups.
### Alternative names
- Look-ahead bias
- Temporal contamination
- Training-window overlap
- Point-in-time admissibility
- Knowledge-cutoff overlap
### Novel vs prior-art verdict
- STRONG_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Strengthen. Suggested edit: `Cutoff Exposure has strong temporal-contamination precedent, but it measures timing relative to a reported or estimated cutoff, not actual exposure. Add that the ±K gray-band exclusion is a benchmark-specific design choice to reduce misclassification around uncertain cutoffs, not a literature-standard convention.`
### New candidate papers to download
- None beyond already-indexed temporal papers.

## Factor 3 — Anchor Strength
### Prior art
- Conceptual precedent exists, but not a direct scalar benchmark factor. `Episodic Memories Generation and Evaluation Benchmark for Large Language Models` (Huet et al.; [arXiv:2501.13121](https://arxiv.org/abs/2501.13121)) represents events via temporal context, spatial context, entities, and detailed descriptions.
- `Language Models Represent Space and Time` (Gurnee and Tegmark; [arXiv:2310.02207](https://arxiv.org/abs/2310.02207)) shows time/space are encoded in model representations, which supports the construct's plausibility.
- Search log: arXiv query `all:"episodic memory" AND all:"benchmark" AND all:"LLM"` was noisy and required exact-title verification; web query `"Episodic Memories Generation and Evaluation Benchmark for Large Language Models"` returned a direct arXiv/ICLR hit. Web searches for `"event anchorability"` did not surface a published rubric.
### Operationalization precedent
- I did not find a published rubric that matches your proposed 3-way pre-registered comparison of density-count, triple-specificity, and ordinal 0-3 scoring.
- Huet et al. provide the closest structured event representation, but not a benchmark-side scalar anchorability score.
### Known failure modes
- Complex spatiotemporal relations and multiple related events degrade episodic performance even in short contexts.
- Representation results do not by themselves validate a monotone benchmark factor.
- Anchorability will likely correlate with text length and exact-span rarity unless explicitly checked.
### Effect direction precedent
- The literature supports the intuition that more explicit time/place/entity grounding should aid episodic recall.
- I did not verify a published result that validates your exact predicted monotone effect as a memorization factor in news benchmarks.
### Alternative names
- Episodic grounding
- Spatiotemporal anchoring
- Event specificity
- Episodic distinctiveness
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Extend. Suggested edit: `Anchor Strength has conceptual precedent in episodic-memory work, but the benchmark-side scalar rubric is novel. Treat the construct as grounded-event specificity, and state explicitly that the final operationalization will be chosen by a pre-registered comparison rather than inherited from prior literature.`
### New candidate papers to download
- None.

## Factor 4 — Entity Salience
### Prior art
- Direct precedent exists. `Quantifying and Analyzing Entity-level Memorization in Large Language Models` (Zhou et al.; [arXiv:2308.15727](https://arxiv.org/abs/2308.15727)) defines entity-level memorization and shows LLMs memorize entity-linked data.
- `Assessing Look-Ahead Bias in Stock Return Predictions Generated By GPT Sentiment Analysis` (Glasserman and Lin; [arXiv:2309.17322](https://arxiv.org/abs/2309.17322); 2024 journal record via EconBiz) introduces the finance-specific distraction effect from company names.
- `Evaluating Company-Specific Biases in Financial Sentiment Analysis using Large Language Models` (Nakagawa et al.; [arXiv:2411.00420](https://arxiv.org/abs/2411.00420)) is direct evidence that firm identity changes model sentiment judgments.
- Search log: arXiv query `all:"entity-level memorization" AND all:"language models"` returned Zhou directly; exact-title web queries returned Glasserman/Lin and Nakagawa.
### Operationalization precedent
- Zhou operationalizes entity-linked memorization; Glasserman/Lin and Nakagawa operationalize entity effects via anonymization / entity removal.
- Your dual-field split into `target_salience` and `max_non_target_entity_salience` is new, but it is better aligned to the literature than a single blended salience score would be.
### Known failure modes
- High-salience entity cues can distract rather than help.
- Partial leakage and associative knowledge can masquerade as memorization.
- Large, famous firms can induce bias even out of sample.
### Effect direction precedent
- Validated direction: stronger target prominence can increase memorization opportunity, while competing-entity prominence can reduce evidence-faithful reading via distraction.
- Glasserman/Lin specifically report anonymized headlines outperforming originals in-sample, with stronger effects for larger companies.
### Alternative names
- Entity-level memorization
- Company-specific bias
- Distraction effect
- Entity prominence
### Novel vs prior-art verdict
- STRONG_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Strengthen. Suggested edit: `Entity Salience combines two literature-backed but distinct mechanisms: target prominence (memorization opportunity) and competing-entity prominence (distraction/interference). Report them separately and avoid any single combined coefficient or narrative.`
### New candidate papers to download
- None beyond already-indexed papers.

## Factor 5 — Target Scope
### Prior art
- Only partial precedent. Financial benchmarks such as `CFinBench` ([arXiv:2407.02301](https://arxiv.org/abs/2407.02301)), `InvestorBench` ([arXiv:2412.18174](https://arxiv.org/abs/2412.18174)), and `EDINET-Bench` ([arXiv:2506.08762](https://arxiv.org/abs/2506.08762)) stratify by task family, product family, or document family.
- Those are benchmark-organization precedents, not memorization-factor precedents for company vs non-company targets.
- Search log: arXiv query `all:"financial benchmark" AND all:"company" AND all:"LLM"` returned benchmark papers; web query exact-title searches for financial benchmarks surfaced no direct memorization-factor use.
### Operationalization precedent
- The literature typically uses product/task/document classes, not a clean issuer-vs-non-issuer binary.
- Your binary scope variable is a pragmatic stratifier, but it is not a standard published memorization factor.
### Known failure modes
- Likely to collapse with event type, tradability, and entity salience.
- The non-company bucket is highly heterogeneous.
- Easy to over-interpret a coarse control as a mechanism.
### Effect direction precedent
- No verified direct effect-direction precedent for memorization.
- Adjacent finance bias work implies company-targeted cases may carry more parametric background knowledge, but that is not a clean scope result.
### Alternative names
- Entity class
- Issuer vs non-issuer
- Company-level vs macro/non-company target
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Strengthen. Suggested edit: `Target Scope is a coarse stratifier/control with weak direct memorization precedent. Use it to stabilize sampling and interpretation, not as a causal construct.`
### New candidate papers to download
- P2: `EDINET-Bench: Evaluating LLMs on Complex Financial Tasks using Japanese Financial Statements` ([arXiv:2506.08762](https://arxiv.org/abs/2506.08762))

## Factor 6 — Structured Event Type
### Prior art
- Partial precedent exists. `Structured Event Representation and Stock Return Predictability` (Li et al.; [arXiv:2512.19484](https://arxiv.org/abs/2512.19484)) uses structured event representation from news for return prediction.
- `Fine-Grained Classification of Announcement News Events in the Chinese Stock Market` (MDPI Electronics 2022; [URL](https://www.mdpi.com/2079-9292/11/13/2058)) constructs a fine-grained taxonomy for Chinese stock-announcement news.
- Search log: arXiv query `all:"structured event representation" AND all:"stock return"` returned a direct finance hit; web query exact-title search returned the Chinese event-taxonomy paper.
### Operationalization precedent
- Fine-grained taxonomies and structured event labels are well precedented in finance NLP and event studies.
- Your exact 15-20 primary labels plus 5-7 coarse bins are still benchmark-specific and should be presented as adapted, not copied.
### Known failure modes
- Fine-grained schemes are expert-heavy and hard to reproduce.
- Clustering-based taxonomies miss low-frequency event types.
- Event-type labels can entangle source form, topic, and market consequence.
### Effect direction precedent
- No direct memorization-direction validation found.
- Prior finance papers use event type for predictability and interpretability, not contamination measurement.
### Alternative names
- Event taxonomy
- Event category
- Structured event representation
- Event label
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Extend. Suggested edit: `Structured Event Type has good finance-NLP precedent as a taxonomy, but weak memorization-factor precedent. Treat fine labels as descriptive and coarse bins as the only confirmatory level.`
### New candidate papers to download
- P1: `Fine-Grained Classification of Announcement News Events in the Chinese Stock Market` ([URL](https://www.mdpi.com/2079-9292/11/13/2058))

## Factor 7 — Disclosure Regime
### Prior art
- I did not verify a published memorization/contamination benchmark that uses formal disclosure vs commentary/secondary coverage as a factor.
- Adjacent finance literature does distinguish official clarifications, regulatory filings, press releases, rumors, and commentary, but not as a memorization factor.
- Search log: arXiv query `all:"disclosure" AND all:"LLM" AND all:"memorization"` returned privacy-disclosure papers, not benchmark papers; web query `"disclosure type" memorization benchmark LLM finance` returned no direct hit.
### Operationalization precedent
- Your binary regime is novel. Closest operationalizations in the literature are richer source/modality taxonomies rather than a contamination factor.
### Known failure modes
- Collapses source authority, document modality, legal-disclosure status, and templated language into one binary.
- Likely to correlate with Modality, Authority, Template Rigidity, and Session Timing.
### Effect direction precedent
- No validated direction found.
- Plausible mechanisms point in both directions, so a strong prior should not be claimed.
### Alternative names
- Source provenance
- Disclosure type
- Document modality
- Announcement channel
### Novel vs prior-art verdict
- NOVEL
### Recommended construct-caveat update for decision doc v6
- Strengthen substantially. Suggested edit: `Disclosure Regime currently has no direct memorization-factor precedent and should be framed as an exploratory source-structure moderator. If retained, justify it mechanistically and report its overlap with Modality and Authority rather than implying a settled literature.`
### New candidate papers to download
- P2: `Market reactions for targets of M&A rumours—evidence from China` ([URL](https://www.tandfonline.com/doi/full/10.1080/1331677X.2020.1865826))

## Factor 8 — Template Rigidity
### Prior art
- Strong precedent exists. `Deduplicating Training Data Makes Language Models Better` ([arXiv:2107.06499](https://arxiv.org/abs/2107.06499)) explicitly finds many near-duplicate examples and long repetitive substrings in LM datasets.
- `Counterfactual Memorization in Neural Language Models` ([arXiv:2112.12938](https://arxiv.org/abs/2112.12938)) warns that repeated data and templated text inflate memorization criteria.
- `Deduplicating Training Data Mitigates Privacy Risks in Language Models` ([arXiv:2202.06539](https://arxiv.org/abs/2202.06539)) connects duplication to regeneration directly.
- Search log: arXiv query `all:"template" AND all:"memorization" AND all:"language model"` was noisy; exact-title web verification returned the deduplication papers and their memorization claims.
### Operationalization precedent
- Surface similarity, near-duplicate detection, and repetitive-substring analysis are well precedented.
- A char-5gram TF-IDF cosine score is a reasonable benchmark implementation, but I did not verify it as a standard named measure of “rigidity.”
### Known failure modes
- Surface similarity is not deeper linguistic rigidity.
- High scores may be driven by disclosure genre or event burst instead of reusable syntax per se.
- Paraphrase-level memorization can escape surface measures.
### Effect direction precedent
- Validated direction: more repetitive / near-duplicate / templated text increases memorization risk.
### Alternative names
- Surface-form overlap
- Template overlap
- Near-duplicate similarity
- Repetitive substrings
### Novel vs prior-art verdict
- STRONG_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Keep and strengthen. Suggested edit: `Template Rigidity has strong surface-form precedent, but the operational variable measures only surface similarity. Present it as a surface-template proxy, not as a deep linguistic property, and treat it as complementary to propagation rather than a substitute for it.`
### New candidate papers to download
- P1: `Deduplicating Training Data Makes Language Models Better` ([arXiv:2107.06499](https://arxiv.org/abs/2107.06499))

## Factor 9 — Tradability Tier
### Prior art
- No direct memorization-factor precedent was verified.
- Adjacent evidence exists: Glasserman and Lin ([arXiv:2309.17322](https://arxiv.org/abs/2309.17322)) report stronger distraction effects for larger companies; classic finance work on media coverage and attention motivates an exposure/attention story, but not an LLM memorization factor story.
- Search log: arXiv query `all:"liquidity" AND all:"LLM" AND all:"stock"` returned trading-agent benchmarks, not memorization factors; web query on tradability/liquidity surfaced finance-attention papers, not contamination-factor papers.
### Operationalization precedent
- `ADV20` percentile at `first_seen_time - 1` is your own operationalization.
- Adjacent papers more often use firm size, analyst coverage, or media coverage, not liquidity percentile.
### Known failure modes
- Likely collinear with size, analyst/media attention, target salience, and coverage breadth.
- It is the only active extra-corpus factor, so it increases reproducibility burden.
### Effect direction precedent
- Weak/indirect only: more tradable/larger firms likely have more background knowledge and more competing priors.
- No clean verified monotone memorization-direction result exists.
### Alternative names
- Liquidity tier
- Size/liquidity stratum
- Attention proxy
- Coverage-intensity proxy
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Strengthen. Suggested edit: `Tradability Tier is an extra-corpus attention proxy with only indirect literature support for memorization. Keep its interpretation narrow and require sensitivity checks against size/salience proxies.`
### New candidate papers to download
- P2: Fang and Peress (2009), `Media Coverage and the Cross-Section of Stock Returns` ([URL](https://www.insead.edu/faculty-research/publications/journal-articles/media-coverage-and-cross-section-stock-returns))

## Factor 10 — Session Timing
### Prior art
- I did not verify a memorization/contamination paper that uses announcement timing as a factor.
- Only finance-adjacent timing literature was found.
- Search log: arXiv query `all:"announcement timing" AND all:"LLM"` returned no results; web query `"announcement timing" memorization LLM finance` surfaced finance timing papers but no LLM contamination precedent.
### Operationalization precedent
- `pre_open / intraday / post_close / non_trading_day` is your own operationalization.
- Adjacent finance literature more often uses Friday vs other weekdays, after-hours vs trading-hours, or non-trading-day adjustments for event studies.
### Known failure modes
- Mechanism to memorization is weak and likely mediated by source type or market processing, not training exposure.
- Timing bins are market-structure dependent and may not transport well across markets.
### Effect direction precedent
- No validated memorization direction found.
### Alternative names
- Announcement timing
- Trading-session timing
- After-hours release timing
- Market-calendar timing
### Novel vs prior-art verdict
- NOVEL
### Recommended construct-caveat update for decision doc v6
- Strengthen substantially. Suggested edit: `Session Timing has finance-market precedent but no direct memorization-factor precedent. Treat it as a low-confidence auxiliary factor with a weak proposed mechanism.`
### New candidate papers to download
- None strong enough beyond finance-adjacent timing papers.

## Factor 11 — Text Length
### Prior art
- Partial precedent exists as nuisance-control logic rather than as a scientific factor. `Detecting Pretraining Data from Large Language Models` (Shi et al.; [arXiv:2310.16789](https://arxiv.org/abs/2310.16789)) uses token-level statistics, and `Measuring memorization in language models via probabilistic extraction` (Hayes et al.; [arXiv:2410.19482](https://arxiv.org/abs/2410.19482)) studies extraction under prefix/suffix settings where sequence length matters mechanically.
- The Japanese newspaper memorization work ([arXiv:2404.17143](https://arxiv.org/abs/2404.17143)) explicitly reports prompt-length effects.
- Search log: broad arXiv query `all:"memorization" AND all:"length" AND all:"language model"` was mostly tangential; targeted arXiv/web verification was needed.
### Operationalization precedent
- Token count as a nuisance control is standard and defensible.
- The literature more often length-normalizes detection/extraction scores than elevates text length into a named benchmark construct.
### Known failure modes
- Length interacts with rarity, anchor strength, and extraction difficulty.
- Over-controlling can wash out meaningful specificity differences if longer texts are also more anchored.
### Effect direction precedent
- Longer prompts/prefixes often increase detection or extraction power, but the effect is not a clean monotone scientific claim about memorization across tasks.
### Alternative names
- Sequence length
- Prompt length
- Token length
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Keep narrow. Suggested edit: `Text Length is a nuisance control only. Its role is to absorb mechanical score sensitivity, not to support a substantive memorization claim.`
### New candidate papers to download
- P1: `Quantifying Memorization and Detecting Training Data of Pre-trained Language Models using Japanese Newspaper` ([arXiv:2404.17143](https://arxiv.org/abs/2404.17143))

## Factor 12 — Event Phase
### Prior art
- Partial adjacency exists. Finance/event-study literature distinguishes rumor, clarification, and official announcement phases, and rumor-detection work treats rumor vs non-rumor as a meaningful stage distinction.
- `Information Transmission Through Rumors in Stock Markets: A New Evidence` ([URL](https://www.tandfonline.com/doi/abs/10.1080/15427560.2016.1238373)) and `Market reactions for targets of M&A rumours—evidence from China` ([URL](https://www.tandfonline.com/doi/full/10.1080/1331677X.2020.1865826)) are the closest finance precedents I verified.
- Search log: arXiv query `all:"rumor" AND all:"financial" AND all:"LLM"` returned no results; web queries on rumor/confirmed/event-phase surfaced finance lifecycle papers, not memorization benchmarks.
### Operationalization precedent
- Your two-stage sampling design over `{rumor, official, clarification, recap}` is novel.
- Published work usually studies rumor vs announcement as an event-study distinction, not as a memorization-benchmark factor.
### Known failure modes
- Phase is partly a sampling-design choice, not a property measured independently of the cluster definition.
- Strong expected overlap with source/modality, propagation intensity, and timing.
- Phase boundaries can be ambiguous for clustered media stories.
### Effect direction precedent
- Adjacent finance work supports different market behavior by phase.
- No direct memorization-direction precedent was verified.
### Alternative names
- News lifecycle stage
- Rumor-confirmation phase
- Rumor/clarification lifecycle
- Buy-the-rumor-sell-the-news stage
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Extend. Suggested edit: `Event Phase has lifecycle precedent in finance, but here it functions partly as a sampling design. State explicitly that phase is used to diversify clusters and reduce construct collapse, not because the memorization literature has already validated it.`
### New candidate papers to download
- P2: `Information Transmission Through Rumors in Stock Markets: A New Evidence` ([URL](https://www.tandfonline.com/doi/abs/10.1080/15427560.2016.1238373))
- P2: `Market reactions for targets of M&A rumours—evidence from China` ([URL](https://www.tandfonline.com/doi/full/10.1080/1331677X.2020.1865826))

## Factor 13 — Exact-Span Rarity
### Prior art
- Strong direct precedent exists. `The Secret Sharer: Evaluating and Testing Unintended Memorization in Neural Networks` (Carlini et al.; [arXiv:1802.08232](https://arxiv.org/abs/1802.08232)) is the foundational rare-sequence/exposure paper.
- `Extracting Training Data from Large Language Models` ([arXiv:2012.07805](https://arxiv.org/abs/2012.07805)), `Quantifying Memorization Across Neural Language Models` ([arXiv:2202.07646](https://arxiv.org/abs/2202.07646)), and `Counterfactual Memorization in Neural Language Models` ([arXiv:2112.12938](https://arxiv.org/abs/2112.12938)) all reinforce rarity/extractability logic.
- Japanese newspaper memorization work ([arXiv:2404.17143](https://arxiv.org/abs/2404.17143)) is especially relevant because it extends the discussion to a news/paywall setting.
- Search log: broad arXiv query `all:"rare" AND all:"memorization" AND all:"language model"` was noisy; exact-title verification recovered the foundational papers.
### Operationalization precedent
- Prior work operationalizes rarity via exposure, canaries, unique/rare sequences, or exact extraction.
- Your trigram-based annotation subproject would be a benchmark-specific implementation, not a published standard.
### Known failure modes
- Exact-span rarity is highly surface-form dependent.
- Rare spans miss paraphrase-level and association-level recall.
- Annotation cost is high relative to active-shortlist factors.
### Effect direction precedent
- Validated direction: unique/rare spans are the most diagnostic and most privacy-sensitive when extracted.
### Alternative names
- Exposure
- Canary rarity
- Unique-sequence risk
- Exact-span extractability
### Novel vs prior-art verdict
- STRONG_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Keep reserve and strengthen. Suggested edit: `Exact-Span Rarity has strong memorization precedent, but its operationalization is annotation-heavy and surface-biased. If activated later, present it as a specialized reserve factor for high-specificity analyses rather than a general headline property.`
### New candidate papers to download
- P1: `Quantifying Memorization and Detecting Training Data of Pre-trained Language Models using Japanese Newspaper` ([arXiv:2404.17143](https://arxiv.org/abs/2404.17143))

## Factor 14 — Cluster Temporal Span / Repost Persistence
### Prior art
- Only partial adjacency exists. `Dated Data` ([arXiv:2403.12958](https://arxiv.org/abs/2403.12958)) is the closest LLM precedent because it studies resource-level temporal spread rather than a single hard cutoff.
- I found news-lifecycle and rumor-duration literature on the web, but not a published LLM memorization factor matching cluster time span or repost persistence.
- Search log: arXiv query `all:"news lifecycle" AND all:"memorization"` returned no results; web query on news lifespan/event-cluster persistence returned adjacent lifecycle work only.
### Operationalization precedent
- Measuring cluster duration or repost persistence is your own design.
- The literature does not provide a standard operational formula for it as a contamination factor.
### Known failure modes
- Easy collapse with Propagation Intensity and Event Phase.
- Long-lived clusters can reflect genuine event evolution rather than redundant exposure.
### Effect direction precedent
- Plausible but unvalidated: longer persistence may widen exposure opportunity.
### Alternative names
- News lifespan
- Cluster half-life
- Repost persistence
- Persistence window
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Extend. Suggested edit: `Cluster Temporal Span / Repost Persistence has only adjacent support from resource-level cutoff and news-lifecycle work. Keep it reserve-only and define precisely whether it captures within-cluster duration, cross-source repost duration, or both.`
### New candidate papers to download
- None strong enough beyond already-indexed temporal papers.

## Factor 15 — Pre-registered interaction menu
### Prior art
- This is methodology precedent, not factor precedent. Preregistration, registered reports, and multiverse/specification-curve analysis give the closest support.
- Verified methodological adjacency: `One Model Many Scores: Using Multiverse Analysis to Prevent Fairness Hacking and Evaluate the Influence of Model Design Decisions` ([arXiv:2308.16681](https://arxiv.org/abs/2308.16681)).
- Search log: arXiv/web searches for preregistration/interactions returned multiverse/preregistration methodology rather than benchmark-factor papers.
### Operationalization precedent
- Pre-committing a limited interaction menu is consistent with open-science practice.
- It is not a borrowed factor from memorization papers.
### Known failure modes
- Hidden multiverse if the menu is too large.
- Hard to interpret if factors are strongly collinear.
### Effect direction precedent
- Not applicable.
### Alternative names
- Preregistered heterogeneity plan
- Pre-analysis interaction set
- Multiverse-lite interaction menu
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- Extend. Suggested edit: `The interaction menu is justified by open-science methodology, not factor-specific precedent. State the cap, rationale, and correlation-aware screening rule explicitly.`
### New candidate papers to download
- P2: `One Model Many Scores: Using Multiverse Analysis to Prevent Fairness Hacking and Evaluate the Influence of Model Design Decisions` ([arXiv:2308.16681](https://arxiv.org/abs/2308.16681))

## Factor 16 — Modality
### Prior art
- No direct memorization-factor precedent was verified.
- Adjacent source/event-type literature is real: official announcement vs rumor vs analysis distinctions appear in finance event-taxonomy and rumor studies, including the Chinese announcement-news taxonomy paper ([URL](https://www.mdpi.com/2079-9292/11/13/2058)).
- Search log: arXiv query `all:"news type" AND all:"financial NLP"` returned no results; web queries on official announcement/press release/rumor classifications returned adjacent finance NLP papers only.
### Operationalization precedent
- The proposed 7-way Thales modality enum is finer and more benchmark-specific than most published source-type taxonomies I found.
### Known failure modes
- Strong overlap with Disclosure Regime, Authority, Event Phase, and Template Rigidity.
- Some labels blend discourse function with source channel.
### Effect direction precedent
- No validated memorization direction found.
### Alternative names
- Source type
- Document type
- Register
- Channel
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- If later activated, suggested edit: `Modality has adjacent finance-NLP/source-type precedent but no direct memorization-factor precedent. Describe it as a document/source taxonomy whose relationship to memorization remains to be established empirically.`
### New candidate papers to download
- P1: `Fine-Grained Classification of Announcement News Events in the Chinese Stock Market` ([URL](https://www.mdpi.com/2079-9292/11/13/2058))

## Factor 17 — Authority
### Prior art
- No direct memorization-factor precedent was verified.
- Adjacent literature uses `source credibility`, `publisher authority`, and `provenance trustworthiness` in rumor detection and information-ecosystem work; these are not memorization factors.
- Search log: arXiv query `all:"source credibility" AND all:"LLM"` returned generic trust papers; web query on publisher credibility/source authority returned adjacent publisher-authority work, not contamination benchmarks.
### Operationalization precedent
- The proposed 8-way authority enum is novel as a memorization factor.
- Closest published ideas are source-credibility and publisher-authority features in misinformation / rumor work.
### Known failure modes
- Text-inferred authority is noisy.
- High authority in network terms is not identical to epistemic reliability.
- Likely collapse with Modality and Disclosure Regime.
### Effect direction precedent
- No validated memorization direction found.
### Alternative names
- Source credibility
- Publisher authority
- Provenance trustworthiness
- Media credibility
### Novel vs prior-art verdict
- PARTIAL_PRIOR_ART
### Recommended construct-caveat update for decision doc v6
- If later activated, suggested edit: `Authority has adjacent source-credibility precedent but no direct memorization-factor precedent. Frame it as exploratory provenance structure, not as a literature-established leakage driver.`
### New candidate papers to download
- P2: `Bursts of contemporaneous publication among high- and low-credibility online information providers` ([URL](https://journals.sagepub.com/doi/10.1177/14614448231183617))

## Cross-factor observations
- The strongest shared-paper bloc is `{Propagation Intensity, Template Rigidity, Exact-Span Rarity, Text Length}`. Kandpal/Carlini/Zhang/Ishihara all point to a common repetition-frequency-surface family. This is exactly the Risk R4 construct-collapse axis.
- `{Cutoff Exposure, Cluster Temporal Span}` share the temporal-cutoff literature, but the direct support is much stronger for cutoff overlap than for cluster persistence.
- `{Entity Salience, Tradability Tier}` share finance-specific bias/distraction evidence, especially Glasserman and Lin. That literature supports background-knowledge interference more clearly than it supports a liquidity-based memorization mechanism.
- `{Disclosure Regime, Modality, Authority, Event Phase}` are the weakest bloc. Published work supports source/lifecycle taxonomies in finance and misinformation, but not these as memorization factors.
- The cleanest “no direct factor precedent” cases are `Disclosure Regime` and `Session Timing`.
- Novelty distribution summary:
- `STRONG_PRIOR_ART`: 5 factors (`Propagation Intensity`, `Cutoff Exposure`, `Entity Salience`, `Template Rigidity`, `Exact-Span Rarity`)
- `PARTIAL_PRIOR_ART`: 10 factors (`Anchor Strength`, `Target Scope`, `Structured Event Type`, `Tradability Tier`, `Text Length`, `Event Phase`, `Cluster Temporal Span`, `Pre-registered interaction menu`, `Modality`, `Authority`)
- `NOVEL`: 2 factors (`Disclosure Regime`, `Session Timing`)

## Candidate new-factor queue (if any)
- `Coverage Breadth / Media Coverage`: finance attention literature and publisher-network literature suggest exposure may depend on how broadly an item is covered, not only on within-corpus duplication. Evidence is adjacent rather than direct, and this partly overlaps `Propagation Intensity` plus `Authority`.
- `Entity-Anonymization Sensitivity`: Glasserman/Lin and Nakagawa show outputs change when entity names are removed. This looks more like a detector/probe feature than a stable article-side factor, but it is a distinct literature-backed concept not currently in the 15+2 list.

## Sweep-A summary memo
- Biggest findings:
- The literature strongly backs only the repetition/surface family, temporal cutoff overlap, entity-level salience/distraction, and exact-span rarity. Much of the finance-specific shortlist is only partially backed.
- I did not find a published gray-band exclusion precedent for the cutoff boundary. That looks like a sensible but new design choice and should be labeled as such.
- `Disclosure Regime` and `Session Timing` are the most exposed constructs. Both have adjacent finance intuition, but not direct memorization-factor precedent.
- `Anchor Strength` is conceptually supported by episodic-memory work, but the actual rubric is novel and should be presented that way.
- Benchmark-level adjacent prior art is already substantial: `Profit Mirage` and `Look-Ahead-Bench` should be treated as mandatory cites.
- Blind spots the sweep could not cover (and why):
- Venue-only finance papers behind paywalls are only partially visible through web snippets; no PDFs were downloaded by design.
- CNKI-first Chinese literature is under-covered because the search flow relied on arXiv plus open web, not a dedicated Chinese academic index session.
- Some arXiv factor queries were noisy and needed exact-title recovery; null results are still informative but should not be over-read as proof of absence.
- Recommendations for the user (prioritized):
- In v6, explicitly separate strong, partial, and novel factors instead of describing the whole shortlist as equally literature-backed.
- Cite `Profit Mirage` and `Look-Ahead-Bench` alongside MemGuard-Alpha in the paper-facing prior-art discussion before R5 decisions.
- Keep `Entity Salience` split into target and competing-entity channels; the literature strongly supports that separation.
- Treat `Disclosure Regime` and `Session Timing` as exploratory or placeholder constructs unless later detector work produces stronger empirical justification.
- Download first: `arXiv:2404.17143` / INLG 2024 Japanese newspaper memorization paper, `arXiv:2107.06499` on near-duplicate/repetitive substrings, and the 2022 Chinese stock-announcement event-taxonomy paper.
