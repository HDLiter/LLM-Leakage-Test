---
role: Quant / alpha-bridge
lens: R5A Step 1 detector brainstorm
thread_id: 019d9149-20e2-7313-af6e-b0555accb3fd
model_reasoning_effort: xhigh
generated: 2026-04-15
---

## Candidate 1: CMMD
**1. Name:** CMMD

**2. Concept:** Compare the same CLS case across the cutoff-staggered 6-model fleet and score disagreement that is monotone in training access. The key signal is not generic disagreement but disagreement that lines up with which models plausibly could have memorized the case.

**3. Mechanism family:** Cross-model + temporal-cutoff-conditional.

**4. Access requirement:** Black-box text only. Runs on `Qwen 2.5-7B-Instruct`, `DeepSeek-V2.5`, `GLM-4-9B-0414`, `DeepSeek-V3-0324`, `Qwen3-14B`, and `Claude Sonnet 4.5`.

**5. Alpha-bridge rationale:** This is the cleanest detector for the paper’s alpha story because it asks whether “predictive” signal appears only in models that had temporal access to the event. If later-cutoff models agree on an alpha sign that earlier-cutoff models systematically reject, the naive backtest is plausibly monetizing training overlap rather than article-local inference. A Thales pipeline can consume CMMD as a case×model veto, a model-specific haircut, or a fleet-consensus gate.

**6. Factor relevance:** `Cutoff Exposure:` very high; this is the detector most directly tied to the spine factor. `event_burst:` medium; same-event duplication should magnify later-model memorization and widen disagreement. `historical_family_recurrence:` medium-high; recurring templates can create family-level contamination even absent exact duplicates. `target_salience:` medium; famous firms are more likely to trigger cutoff-linked priors. `max_non_target_entity_salience:` medium-high; disagreement can be driven by competing-entity distraction rather than the target article. `Tradability Tier:` medium-high; liquid firms should be more exposed in pretraining and therefore more cutoff-sensitive. `Structured Event Type:` medium; earnings, guidance, ratings, and M&A should show stronger cutoff effects than diffuse commentary. `Template Rigidity:` medium; rigid templates help later models lock onto memorized patterns.

**7. Bloc diversification:** Primarily Bloc 0; secondarily Bloc 2.

**8. Ensemble compatibility:** Best reported independently first, then optionally used as a gating feature for a downstream composite.

**9. Detector-level stratification fields (P5):** `cross_model_agreement_score`; `cutoff_monotonicity_score`. `Entity-Anonymization Sensitivity:` yes, because pre/post-masking CMMD helps separate entity-prior contamination from article-level memorization.

**10. Thales dependency:** (a) usable on raw CLS text now.

**11. Compute budget estimate:** `3,200 × 6 = 19,200` calls; roughly the project fleet baseline, about `8` local GPU-hours plus about `$6` hosted inference.

**12. Key citations:** [Roy & Roy 2026](https://arxiv.org/abs/2603.26797); [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322); [Wongchamcharoen & Glasserman 2025](https://arxiv.org/abs/2511.14214).

**13. Risks / caveats:** Cross-model disagreement can reflect capability, Chinese-finance fluency, or instruction-following differences rather than contamination; it needs placebo checks in clearly post-cutoff windows and a cutoff-monotonic interpretation rule.

## Candidate 2: Cutoff Min-K++
**1. Name:** Cutoff Min-K++

**2. Concept:** Score each CLS text with Min-K++ on white-box models, then interpret the score conditional on that model’s cutoff gap. The contaminated pattern is “high familiarity where training access is possible, low familiarity where it is not.”

**3. Mechanism family:** Surface-form + temporal-cutoff-conditional.

**4. Access requirement:** White-box logprobs. Runs on `Qwen 2.5-7B-Instruct`, `GLM-4-9B-0414`, and `Qwen3-14B`.

**5. Alpha-bridge rationale:** This is the cheapest direct article-familiarity prior that still talks the language of backtest contamination. If a case looks like pretraining material exactly in the models that can have seen it, then any alpha extracted from that case is suspect as memorization-assisted. Thales can use the score as a per-case exclusion flag or as a continuous contamination prior alongside the raw alpha score.

**6. Factor relevance:** `Cutoff Exposure:` high; the score becomes much more interpretable once tied to model-specific access windows. `event_burst:` high; same-event duplication should sharply increase familiarity. `historical_family_recurrence:` very high; repeated CLS-style templates are exactly what this detector will like. `target_salience:` medium; names and numbers are often the first memorized anchors. `max_non_target_entity_salience:` medium; competing names can also lower tail surprise. `Tradability Tier:` medium; large liquid firms should have more surface exposure. `Structured Event Type:` low-medium; formulaic disclosure types should score higher. `Template Rigidity:` very high; this detector is almost mechanically aligned with rigid lexical reuse.

**7. Bloc diversification:** Mostly Bloc 1, with a useful Bloc 0 interaction.

**8. Ensemble compatibility:** Strong component in an MCS-style composite, but also worth reporting alone because it is interpretable.

**9. Detector-level stratification fields (P5):** `logprob_tail_length`; `min_kpp_margin`. `Entity-Anonymization Sensitivity:` yes, because masking tests whether familiarity is carried by entity tokens versus the broader article.

**10. Thales dependency:** (a) usable on raw CLS text now.

**11. Compute budget estimate:** `3,200 × 3 = 9,600` scoring passes; roughly `6-8` local GPU-hours.

**12. Key citations:** [Shi et al. 2023/2024](https://arxiv.org/abs/2310.16789); [Zhang et al. 2024/2025](https://arxiv.org/abs/2404.02936); [Meeus et al. 2024/2025](https://arxiv.org/abs/2406.17975); [Tirumala et al. 2022](https://arxiv.org/abs/2205.10770).

**13. Risks / caveats:** It is still a surface-form detector, so it can collapse into “CLS repetition detector” if over-interpreted; paraphrastic or semantic contamination can evade it, and Bloc 1 can dominate the paper if this family is over-weighted.

## Candidate 3: False-Outcome Gap
**1. Name:** False-Outcome Gap

**2. Concept:** Replace the outcome-bearing clause with a plausible false or sign-reversed outcome while keeping setup, timing, and entities fixed. Score how much the model’s alpha-relevant output fails to follow the visible counterfactual.

**3. Mechanism family:** Counterfactual.

**4. Access requirement:** Black-box text only. Runs on `Qwen 2.5-7B-Instruct`, `DeepSeek-V2.5`, `GLM-4-9B-0414`, `DeepSeek-V3-0324`, `Qwen3-14B`, and `Claude Sonnet 4.5`.

**5. Alpha-bridge rationale:** This is the most behaviorally direct contamination assay for the alpha narrative: if the model keeps producing the same bullish or bearish signal after the visible outcome is falsified, it is not reading the article, it is importing latent world knowledge. Thales can treat a large FO gap as a hard rejection for that case×model signal, because the model is visibly non-faithful to the tradable information set.

**6. Factor relevance:** `Cutoff Exposure:` high; the gap should widen inside the memorization-possible region. `event_burst:` medium; duplicated events are easier to memorize and ignore counterfactually. `historical_family_recurrence:` medium-high; recurring templates can trigger stored outcome priors. `target_salience:` high; famous firms invite stronger parametric priors. `max_non_target_entity_salience:` very high; competing-entity distraction is a direct alternative mechanism this probe can reveal. `Tradability Tier:` high; liquid names should show larger prior-driven persistence. `Structured Event Type:` medium-high; earnings, ratings, and official disclosures are likely strongest. `Template Rigidity:` medium; rigid surface forms make hidden outcome recall easier.

**7. Bloc diversification:** Mainly Bloc 0 and Bloc 2, with some Bloc 3.

**8. Ensemble compatibility:** Better reported independently; also useful as an external validity check on white-box familiarity scores.

**9. Detector-level stratification fields (P5):** `text_reversibility_score`; `counterfactual_response_gap`. `Entity-Anonymization Sensitivity:` yes, because if masking collapses the gap, the contamination channel is entity prior rather than article memory.

**10. Thales dependency:** (c) degrades gracefully without Thales; clustering helps produce cleaner false outcomes.

**11. Compute budget estimate:** Original plus one FO edit gives about `38,400` calls; roughly `16` local GPU-hours plus about `$12` hosted inference.

**12. Key citations:** [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322); [Nakagawa et al. 2024](https://arxiv.org/abs/2411.00420); [Wu et al. 2025](https://arxiv.org/abs/2511.15364); [Mirzadeh et al. 2024](https://arxiv.org/abs/2410.05229).

**13. Risks / caveats:** Bad edits will look like contamination. This detector only works if the Chinese counterfactuals are tight enough that a clean model should genuinely change its answer.

## Candidate 4: FinMem-NoOp
**1. Name:** FinMem-NoOp

**2. Concept:** Insert a rule-based irrelevant-but-plausible clause, ideally about an unrelated same-day ticker or market detail that should not change the target signal. Score how much the prediction moves under this semantic no-op.

**3. Mechanism family:** Counterfactual.

**4. Access requirement:** Black-box text only. Runs on `Qwen 2.5-7B-Instruct`, `DeepSeek-V2.5`, `GLM-4-9B-0414`, `DeepSeek-V3-0324`, `Qwen3-14B`, and `Claude Sonnet 4.5`.

**5. Alpha-bridge rationale:** A backtestable alpha signal should not materially move when you add an irrelevant clause. If it does, the model is trading on brittle stored associations or template-triggered priors rather than the tradable content of the article. Thales can use NoOp sensitivity as a robustness veto even when the raw forecast looks profitable.

**6. Factor relevance:** `Cutoff Exposure:` medium; memorization should amplify no-op brittleness, but this is not a pure temporal detector. `event_burst:` high; repeated templates encourage cue-triggered behavior. `historical_family_recurrence:` high; long-running schemas make irrelevant clauses more likely to activate stale patterns. `target_salience:` medium-high; salient firms make the model easier to distract. `max_non_target_entity_salience:` high; injected side entities are the point of the test. `Tradability Tier:` medium; liquid names should be more cue-sensitive. `Structured Event Type:` high for formulaic event types. `Template Rigidity:` high; rigid forms make spurious cue matching more likely.

**7. Bloc diversification:** Mostly Bloc 1 and Bloc 2.

**8. Ensemble compatibility:** Best used as an independent robustness detector or as a veto feature, not as the core ensemble score.

**9. Detector-level stratification fields (P5):** `noop_sensitivity`; `irrelevant_clause_type`. `Entity-Anonymization Sensitivity:` yes, because pre/post masking tells you whether no-op instability is being driven by entity triggers.

**10. Thales dependency:** (c) degrades gracefully without Thales; entity and cluster metadata improve clause construction.

**11. Compute budget estimate:** Original plus one NoOp edit gives about `38,400` calls; roughly `16` local GPU-hours plus about `$12` hosted inference.

**12. Key citations:** [Mirzadeh et al. 2024](https://arxiv.org/abs/2410.05229); [McCoy et al. 2023](https://aclanthology.org/2023.tacl-1.38/); [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322).

**13. Risks / caveats:** This can measure generic prompt fragility rather than memorization. If the no-op clause is not truly irrelevant in Chinese market context, the detector becomes uninterpretable.

## Candidate 5: Entity Mask Delta
**1. Name:** Entity Mask Delta

**2. Concept:** Compare the model’s signal on original CLS text versus entity-anonymized or neighbor-entity-substituted text. The detector score is the drop or reversal induced by removing firm identity cues.

**3. Mechanism family:** Counterfactual.

**4. Access requirement:** Black-box text only. Runs on `Qwen 2.5-7B-Instruct`, `DeepSeek-V2.5`, `GLM-4-9B-0414`, `DeepSeek-V3-0324`, `Qwen3-14B`, and `Claude Sonnet 4.5`.

**5. Alpha-bridge rationale:** From the alpha lens, this is the cleanest Bloc 2 detector. If a signal vanishes once the company name is removed, the model may be monetizing firm familiarity, distraction, or post-hoc company knowledge rather than article-local information. A Thales pipeline can consume this as a “name-prior haircut,” which is operationally closer to production risk control than a generic memorization score.

**6. Factor relevance:** `Cutoff Exposure:` medium; later-cutoff models should carry stronger entity priors inside the overlap window. `event_burst:` low-medium; same-event duplication matters less than firm familiarity here. `historical_family_recurrence:` medium; recurring event families can harden entity-event priors. `target_salience:` very high; this is the main axis. `max_non_target_entity_salience:` very high; competing-entity distraction is explicitly targeted. `Tradability Tier:` very high; firm familiarity should scale with liquidity and attention. `Structured Event Type:` medium; earnings, M&A, and ratings are likely strongest. `Template Rigidity:` low-medium; the mechanism is more entity-driven than template-driven.

**7. Bloc diversification:** Primarily Bloc 2.

**8. Ensemble compatibility:** Best reported independently and then used as a stratifier across the other detectors.

**9. Detector-level stratification fields (P5):** `entity_anonymization_sensitivity`; `neighbor_entity_substitution_gap`. `Entity-Anonymization Sensitivity:` yes, by definition.

**10. Thales dependency:** (c) degrades gracefully without Thales; proper entity extraction makes it much cleaner.

**11. Compute budget estimate:** Original plus one masked variant gives about `38,400` calls; if neighbor-entity substitution is also run, about `57,600` calls.

**12. Key citations:** [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322); [Nakagawa et al. 2024](https://arxiv.org/abs/2411.00420); [Wu et al. 2025](https://arxiv.org/abs/2511.15364).

**13. Risks / caveats:** It can remove genuine economic signal, not just leakage. If masking is crude, the detector will punish Chinese syntax damage rather than entity-prior dependence.

## Candidate 6: Masked Suffix Extraction
**1. Name:** Masked Suffix Extraction

**2. Concept:** Hide the back half of the CLS wire, especially numeric and entity-bearing spans, and ask the model to continue or reconstruct it. Score exact or fuzzy recovery of the hidden text.

**3. Mechanism family:** Extraction + surface-form hybrid.

**4. Access requirement:** Black-box text only, with optional white-box calibration. Runs on `Qwen 2.5-7B-Instruct`, `DeepSeek-V2.5`, `GLM-4-9B-0414`, `DeepSeek-V3-0324`, `Qwen3-14B`, and `Claude Sonnet 4.5`.

**5. Alpha-bridge rationale:** This is the highest-precision detector in the slate. If the model can recover hidden CLS spans, especially numbers and named outcome phrases, then any alpha measured on that article is at serious risk of being contaminated by source memorization. Thales can use a high extraction score as a hard exclusion even when softer detectors disagree.

**6. Factor relevance:** `Cutoff Exposure:` high when interpreted model-by-model against the cutoff. `event_burst:` very high; same-event duplication should strongly raise recoverability. `historical_family_recurrence:` very high; repeated templates create near-verbatim extraction opportunities. `target_salience:` high; names and numbers are the most memorable anchors. `max_non_target_entity_salience:` medium; competing entities matter but less than literal overlap. `Tradability Tier:` medium-high; liquid firms should have more memorized numeric context. `Structured Event Type:` medium-high for formal disclosures and templated notices. `Template Rigidity:` very high; this detector is almost a direct readout of rigid reuse.

**7. Bloc diversification:** Mostly Bloc 1, with a high-precision anchor role.

**8. Ensemble compatibility:** Best reported independently as a high-precision audit detector; useful for calibrating false positives in broader detectors.

**9. Detector-level stratification fields (P5):** `extractable_span_density`; `numeric_span_hit_rate`. `Entity-Anonymization Sensitivity:` no, because masking changes the literal target string and makes the extraction score non-comparable.

**10. Thales dependency:** (a) usable on raw CLS text now.

**11. Compute budget estimate:** One masked continuation prompt per case×model is `19,200` calls; two masks or retry sampling pushes it toward `38,400`.

**12. Key citations:** [Carlini et al. 2019](https://www.usenix.org/conference/usenixsecurity19/presentation/carlini); [Carlini et al. 2020/2021](https://arxiv.org/abs/2012.07805); [Nasr et al. 2023](https://arxiv.org/abs/2311.17035); [McCoy et al. 2023](https://aclanthology.org/2023.tacl-1.38/).

**13. Risks / caveats:** Excellent precision, weak recall. It will miss semantic contamination and may under-fire on closed models that paraphrase instead of quoting.

## Candidate 7: Debias Delta
**1. Name:** Debias Delta

**2. Concept:** Run a Merchant-Levy-style inference-time debiasing pass and measure how much the article-level signal changes between raw and debiased decoding. The detector score is the removable contamination component.

**3. Mechanism family:** Temporal-cutoff-conditional.

**4. Access requirement:** Hybrid; needs a white-box base model plus small retain/forget models or equivalent logit-control machinery. Realistically runs first on `Qwen 2.5-7B-Instruct`, `GLM-4-9B-0414`, and `Qwen3-14B`.

**5. Alpha-bridge rationale:** This is the most directly deployable detector in the slate because it produces an explicit contamination haircut: “how much alpha disappears when post-cutoff knowledge is suppressed?” That is exactly the quantity a downstream pipeline wants if the goal is not just measurement but safe portfolio construction. It translates naturally into a case-level exclusion or a score adjustment.

**6. Factor relevance:** `Cutoff Exposure:` very high; the whole detector is built around removable post-cutoff knowledge. `event_burst:` medium; duplicated events should create a larger removable component. `historical_family_recurrence:` medium-high; recurring templates create retrievable stale knowledge. `target_salience:` medium-high; famous firms likely carry more removable entity knowledge. `max_non_target_entity_salience:` high; debiasing should also suppress competing-entity priors. `Tradability Tier:` high; liquid names should show larger deltas. `Structured Event Type:` medium; outcome-heavy event types should be strongest. `Template Rigidity:` medium; literal memorization helps, but this detector is broader than surface reuse.

**7. Bloc diversification:** Primarily Bloc 0 and Bloc 2.

**8. Ensemble compatibility:** Best reported independently as both a detector and a mitigation baseline.

**9. Detector-level stratification fields (P5):** `debias_delta`; `retained_signal_ratio`. `Entity-Anonymization Sensitivity:` yes, because pre/post masking helps distinguish removable entity priors from removable article memory.

**10. Thales dependency:** (a) usable on raw CLS text now.

**11. Compute budget estimate:** About `9,600` debiased inference passes plus one-time training or fitting of small retain/forget components; roughly `15-25` GPU-hours total.

**12. Key citations:** [Merchant & Levy 2025](https://arxiv.org/abs/2512.06607); [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322); [Wongchamcharoen & Glasserman 2025](https://arxiv.org/abs/2511.14214); [Roy & Roy 2026](https://arxiv.org/abs/2603.26797).

**13. Risks / caveats:** It is mitigation-first, not a canonical detector. A large delta can reflect useful generic knowledge removal, not just contamination, and the engineering burden is materially higher than the rest of the slate.

## Quant-Lens Synthesis
- **Top 3 picks:** `CMMD` is the best spine detector because it directly operationalizes cutoff-driven alpha contamination and localizes which model’s signal is suspect. `Cutoff Min-K++` is the best cheap white-box familiarity prior and gives Thales an immediate article-level filter on the three local models. `False-Outcome Gap` is the strongest behavioral proof that “predictive” alpha is really latent future knowledge rather than text-faithful inference.
- **Best secondary add-ons:** `Entity Mask Delta` is the cleanest Bloc 2 detector and the one most likely to matter for Tradability Tier and competing-entity salience. `Masked Suffix Extraction` is the high-precision anchor that keeps the paper honest even if it under-covers the main alpha channel. `Debias Delta` is the most deployment-friendly option, but I would treat it as a heavier Step 2 candidate.
- **Family most likely to remain uncovered by a Quant-only shortlist:** Extraction, because a Quant-only slate will naturally over-prefer cutoff-aware filters and under-invest in an expensive high-precision verbatim audit.
- **Ensemble vs independent reporting:** Independent detectors should be primary; if you want one MCS-style scalar, build it only as a secondary deployment translation layer after the paper shows the independent detector×factor matrix.
- **Question for NLP, Stats, and Editor before R5A Step 2:** What is the minimum Chinese counterfactual-edit audit standard that makes `False-Outcome Gap`, `FinMem-NoOp`, and `Entity Mask Delta` admissible as contamination evidence rather than prompt-artifact evidence?
