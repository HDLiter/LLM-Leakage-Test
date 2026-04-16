---
role: Stats / power and identification
lens: R5A Step 1 detector brainstorm
thread_id: 019d914a-5835-7053-b20e-903aaa2243b7
model_reasoning_effort: xhigh
generated: 2026-04-15
---

Below is the detector slate I would take forward from the Stats lens. I would preregister **5 primary detectors** and keep **2 reserve/validation detectors**. The primary principle is: favor **paired or cross-cutoff contrasts** and keep heterogeneous mechanisms **independent**, because that preserves identifiability and keeps the multiplicity problem tractable.

## Min-K++ Tail Surprise
- **Concept:** Sequence-level detector based on the lower tail of token probabilities; high scores mean the text looks unusually easy for the model in exactly the way training examples tend to. This is the cleanest cheap surface-form baseline.
- **Mechanism family:** Surface-form.
- **Access requirement / fleet availability:** Requires token logprobs. Feasible now on the 3 local white-box models: Qwen 2.5-7B-Instruct, GLM-4-9B-0414, Qwen3-14B. Not a reliable full-fleet detector because hosted DeepSeek and Claude logprob access is limited or unstable.
- **Identification rationale:** The causal reading is only conditional: after jointly adjusting for Bloc 1 mates, length, and salience, residual tail-easiness is interpretable as exposure-like signal. The nearest negative control is a matched paraphrase or entity-swapped placebo that preserves length and syntax. The main non-memorization confounds are boilerplate wire style, tokenization artifacts, and generic company-name frequency. This is exactly where [Meeus et al. 2024](https://arxiv.org/abs/2406.17975) matters.
- **Power rationale:** High. At about 2,560 scorable cases, a continuous standardized score like this should have roughly 80% power for main effects around `beta ≈ 0.10-0.12`, or binary contrasts around `d ≈ 0.22-0.26`, after a conservative family correction. The bottleneck is not N; it is collinearity with Template Rigidity and the two Propagation terms.
- **Independence from correlation blocs:** Low. It loads mainly on Bloc 1 and is the detector most at risk of construct collapse with repetition/surface reuse.
- **Factor relevance:** Cutoff Exposure should be positive post-cutoff. `event_burst` should be moderately positive. `historical_family_recurrence` should be strongly positive. Target Prominence should be mildly positive. Competing-Entity Prominence should attenuate the signal if the detector is clean; a positive coefficient there would indicate contamination by distraction. Tradability Tier should be mildly positive within companies. Template Rigidity should be strongly positive.
- **Ensemble compatibility:** Only as a **surface-family** summary with other near-duplicate likelihood features. I would not mix it into a heterogeneous MCS-style confirmatory ensemble.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity` via raw-vs-masked Min-K++ delta; `tail_concentration` (share of score carried by the lowest-probability tokens).
- **Interaction menu contribution:** Strong candidate for `cutoff × propagation_intensity` and `template_rigidity × cutoff_exposure`.
- **Thales dependency:** Usable on raw CLS text immediately.
- **Compute budget estimate:** Nominal full-fleet budget would be `1 × 6 × 2,560 = 15,360`, but feasible full-fidelity run is `1 × 3 × 2,560 = 7,680`; anonymization stratification doubles that.
- **Key citations:** [Shi et al. 2023](https://arxiv.org/abs/2310.16789), [Zhang et al. 2024](https://arxiv.org/abs/2404.02936), [Meeus et al. 2024](https://arxiv.org/abs/2406.17975).
- **Risks / caveats:** Biggest threat is that it mostly rediscovers duplication and template reuse, not memorization per se.

## Paired Cutoff Surprise Gap
- **Concept:** New detector: compute a standardized surprise score in earlier-cutoff and later-cutoff models, then take the within-case late-minus-early gap. This turns cutoff into a paired contrast rather than a nuisance covariate.
- **Mechanism family:** Temporal-cutoff-conditional.
- **Access requirement / fleet availability:** Same logprob requirement as Min-K++; strongest on the 3 local white-box models. If hosted logprobs stabilize later, it can expand.
- **Identification rationale:** This is one of the strongest designs here. Under model-pair fixed effects and a preregistered calibration step, I would interpret the residual late-minus-early advantage as exposure-like rather than generic easiness. The nearest negative controls are cases far before the earliest cutoff and placebo pseudo-cutoff assignments. The main confound is model-family quality differences masquerading as date effects.
- **Power rationale:** Better than ordinary surface detectors because the paired contrast removes a lot of case difficulty variance. Roughly 80% power for `beta ≈ 0.08-0.10` or `d ≈ 0.18-0.22`; in the company-only tradability subset that rises to about `d ≈ 0.24-0.28`. The bottleneck is only 3-model availability, not per-case noise.
- **Independence from correlation blocs:** Good. It is still partly surface-driven, but it cuts across Bloc 0 and Bloc 1 rather than sitting inside Bloc 1 alone.
- **Factor relevance:** Cutoff Exposure should be the dominant effect. `event_burst` should be positive when duplication was temporally concentrated near later cutoffs. `historical_family_recurrence` should be positive and likely larger than burst. Target Prominence should be positive. Competing-Entity Prominence should weaken the gap. Tradability Tier should be mildly positive. Template Rigidity should be moderately positive.
- **Ensemble compatibility:** Poor fit for a bigger ensemble because it is already a structured contrast. I would keep it independent.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity` of the paired gap; `pair_calibration_residual` after model-pair normalization.
- **Interaction menu contribution:** Strong candidate for `cutoff × propagation_intensity` and `template_rigidity × cutoff_exposure`.
- **Thales dependency:** Usable immediately; better with Thales masks and better covariates.
- **Compute budget estimate:** Marginal cost is near-zero if it reuses Min-K++ traces; standalone feasible budget is `1 × 3 × 2,560 = 7,680`.
- **Key citations:** [Merchant & Levy 2025](https://arxiv.org/abs/2512.06607), [Meeus et al. 2024](https://arxiv.org/abs/2406.17975), [Duan et al. 2024](https://arxiv.org/abs/2402.07841).
- **Risks / caveats:** If model-pair calibration is sloppy, this becomes a model-quality detector, not a memorization detector.

## CMMD
- **Concept:** Cross-model disagreement detector keyed to staggered cutoffs. Memorized cases should induce a structured disagreement pattern: later-cutoff models converge while earlier-cutoff models diverge or lag.
- **Mechanism family:** Cross-model.
- **Access requirement / fleet availability:** Black-box compatible; available on all 6 fleet models.
- **Identification rationale:** Interpretable if disagreement is decomposed into within-cutoff-band noise versus across-cutoff-band separation. The nearest negative controls are same-cutoff or near-same-cutoff model pairs and shuffled cutoff labels. The main confounds are architecture/vendor heterogeneity, Chinese capability differences, and hosted-model nondeterminism. I infer from [Roy & Roy 2026](https://arxiv.org/abs/2603.26797) that CMMD is more defensible as an **independent detector** than as just one feature inside their broader composite.
- **Power rationale:** Solid but not elite. Full-fleet coverage gives enough information for about `beta ≈ 0.10-0.12` or `d ≈ 0.22-0.27` on main effects after multiplicity control. The bottleneck is detector noise from heterogeneous model families.
- **Independence from correlation blocs:** High. This is one of the detectors that genuinely cuts across blocs.
- **Factor relevance:** Cutoff Exposure should dominate. `event_burst` should be positive when the burst created late-window ingestion. `historical_family_recurrence` should be strongly positive. Target Prominence should be positive. Competing-Entity Prominence can create false disagreement and is therefore partly a purity diagnostic. Tradability Tier should be mildly positive. Template Rigidity should be moderately positive.
- **Ensemble compatibility:** I would not stack it into another confirmatory ensemble. Treat it as its own detector family.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity`; `cross_cutoff_band_ratio` = across-band disagreement / within-band disagreement.
- **Interaction menu contribution:** Strong candidate for `cutoff × propagation_intensity`; useful for `disclosure_regime × event_type`.
- **Thales dependency:** Usable immediately; gains from better entity normalization and source annotations.
- **Compute budget estimate:** `1 × 6 × 2,560 = 15,360` if built from existing responses; `2 × 6 × 2,560 = 30,720` if a verifier pass is added.
- **Key citations:** [Roy & Roy 2026](https://arxiv.org/abs/2603.26797), [Chen et al. 2026](https://arxiv.org/abs/2603.21658), [Meeus et al. 2024](https://arxiv.org/abs/2406.17975).
- **Risks / caveats:** Architecture differences can look like memorization unless same-cutoff controls are pre-registered.

## Counterfactual Fact Inertia
- **Concept:** Apply Semantic Reversal and False Outcome perturbations, then score how strongly the model snaps back toward the real-world original. That snap-back is a more causally informative signal than raw likelihood.
- **Mechanism family:** Counterfactual.
- **Access requirement / fleet availability:** Black-box compatible; available on all 6 models.
- **Identification rationale:** This is close to an intervention design: hold most of the text fixed, change the key fact, and measure whether the detector reverts. The nearest negative control is a semantically neutral paraphrase or formatting edit; another is the same intervention on clearly pre-cutoff cases. The main confounds are bad perturbations, refusals, and generic prompt robustness.
- **Power rationale:** Medium. With 2,560 cases, expect about 80% power only for `beta ≈ 0.13-0.16` or `d ≈ 0.28-0.35`. The hardest menu item is the low-salience tail diagnostic because effective cell counts there can get small fast.
- **Independence from correlation blocs:** High. This is another detector that meaningfully cuts across blocs.
- **Factor relevance:** Cutoff Exposure should be positive. `event_burst` should be mildly positive. `historical_family_recurrence` should be moderately positive. Target Prominence should be positive. Competing-Entity Prominence should ideally be negative; if positive, the detector is partly measuring distraction. Tradability Tier should be mildly positive. Template Rigidity should be low-to-moderate positive.
- **Ensemble compatibility:** Keep independent. Mixing it into a logistic ensemble with surface detectors would destroy the causal interpretation.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity` of snap-back; `counterfactual_compliance` so low-quality interventions can be down-weighted or stratified.
- **Interaction menu contribution:** Best fit for `cutoff × anchor_strength` and `target_salience × propagation_intensity | target_salience=low`.
- **Thales dependency:** Degraded without Thales; substantially better with entity/relation spans and anchor tags.
- **Compute budget estimate:** Base + SR + FO is `3 × 6 × 2,560 = 46,080`.
- **Key citations:** [Meeus et al. 2024](https://arxiv.org/abs/2406.17975), [Cronbach & Meehl 1955](https://pubmed.ncbi.nlm.nih.gov/13245896/), [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).
- **Risks / caveats:** If perturbation quality is inconsistent, this becomes a noisy prompting artifact.

## Entity-Anonymization Delta
- **Concept:** Compare raw-text score versus target-anonymized score. Large raw-minus-anonymized gaps indicate identity-keyed memory or identity-driven distraction; this is the cleanest operationalization of the mandatory P5 field.
- **Mechanism family:** Counterfactual.
- **Access requirement / fleet availability:** Black-box compatible; available on all 6 models.
- **Identification rationale:** Strong, because it is a within-case intervention. The nearest negative controls are placebo masking of a non-target noun and masking of a competing entity. The main confound is information loss from masking itself, which is why mask design matters more here than model choice.
- **Power rationale:** Good. Paired differences should support about `beta ≈ 0.09-0.11` or `d ≈ 0.20-0.24` on main effects. The bottleneck is mask validity, not N.
- **Independence from correlation blocs:** High. It is not reducible to Bloc 1 and should diagnose across salience, tradability, and cutoff.
- **Factor relevance:** Cutoff Exposure should be positive when memory is identity keyed. `event_burst` should be mildly positive. `historical_family_recurrence` should be moderately positive. Target Prominence should be strongly positive. Competing-Entity Prominence is diagnostic: sign and magnitude tell you whether masking isolates the target or simply shifts attention to distractors. Tradability Tier should be strongly positive within companies. Template Rigidity should be modestly positive.
- **Ensemble compatibility:** Independent detector or universal stratifier, not an ensemble feature.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity` itself; `mask_type` (`target_only` vs `target_plus_numeric_anchor`).
- **Interaction menu contribution:** Best fit for `entity_salience × tradability_tier | target_type=company`; also useful for `disclosure_regime × event_type`.
- **Thales dependency:** Degraded without Thales; much better with reliable target/competitor spans.
- **Compute budget estimate:** `2 × 6 × 2,560 = 30,720`.
- **Key citations:** [Glasserman & Lin 2023](https://arxiv.org/abs/2309.17322), [Nakagawa et al. 2024](https://arxiv.org/abs/2411.00420), [Wu et al. 2025](https://arxiv.org/abs/2511.15364).
- **Risks / caveats:** If anonymization strips economically essential content, the detector measures information-loss sensitivity rather than memorization sensitivity.

## FinMem-NoOp Stability
- **Concept:** Inject an irrelevant-but-plausible CLS-style clause and measure invariance of the detector output, relative to a placebo edit. Memorized cases should be less perturbed than cases solved by local pattern-matching.
- **Mechanism family:** Counterfactual.
- **Access requirement / fleet availability:** Black-box compatible; available on all 6 models.
- **Identification rationale:** Only acceptable if the clause generator is deterministic, time-matched, target-irrelevant, and preregistered. The nearest negative control is a style-matched empty clause or punctuation edit. The main confound is generic attention dilution from longer prompts.
- **Power rationale:** Weakest of the primary-style detectors unless the clause generator is very clean. Roughly `beta ≈ 0.14-0.18` or `d ≈ 0.30-0.38` for 80% power. I would not make it confirmatory unless a pilot shows high reliability.
- **Independence from correlation blocs:** Moderate in theory, lower in practice; it will otherwise over-load on salience and prompt fragility.
- **Factor relevance:** Cutoff Exposure should be weakly positive. `event_burst` should be mildly positive. `historical_family_recurrence` should be moderately positive. Target Prominence should be positive. Competing-Entity Prominence should be negative. Tradability Tier should be mildly positive. Template Rigidity should be weakly positive.
- **Ensemble compatibility:** Exploratory independent detector only.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity`; `clause_family_id` (`same-sector`, `same-day other ticker`, `macro-only`).
- **Interaction menu contribution:** Useful for `target_salience × propagation_intensity | target_salience=low`; secondarily `disclosure_regime × event_type`.
- **Thales dependency:** Degraded without Thales; needs entity typing, sector tags, and time-window retrieval.
- **Compute budget estimate:** Raw + NoOp + placebo is `3 × 6 × 2,560 = 46,080`.
- **Key citations:** [Mirzadeh et al. 2024](https://arxiv.org/abs/2410.05229), [Yang et al. 2025](https://arxiv.org/abs/2505.18761), [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/).
- **Risks / caveats:** Biggest threat is construct drift into generic prompt-robustness.

## Extraction-Lite Continuation Hit
- **Concept:** Prompt short article stems or prefixes and score whether the model emits exact or near-exact continuations matching the CLS case or its family. This is sparse but high-specificity evidence.
- **Mechanism family:** Extraction.
- **Access requirement / fleet availability:** Black-box generation works on all 6 models; white-box scores help rerank prefixes but are not required.
- **Identification rationale:** Strong specificity. The nearest negative controls are off-cluster matched prefixes and pre-cutoff cases that should not continue correctly. The main confound is generic wire-style boilerplate, especially for templated corporate actions.
- **Power rationale:** Low because hits are rare. At this N, I would expect usable power only for large effects, around `OR ≈ 1.8-2.2` or a 4-6 pp risk difference when baseline hit rate is at least about 10%. This is a validation detector, not a primary workhorse for interaction discovery.
- **Independence from correlation blocs:** Low-to-moderate; mostly Bloc 1 plus cutoff.
- **Factor relevance:** Cutoff Exposure should be strongly positive. `event_burst` should be moderately positive. `historical_family_recurrence` should be strongly positive. Target Prominence should be strongly positive. Competing-Entity Prominence should be negative. Tradability Tier should be moderately positive. Template Rigidity should be very strongly positive.
- **Ensemble compatibility:** Keep independent. Sparse high-PPV detectors do not behave well inside logistic composites.
- **Detector-level stratification fields (P5):** `entity_anonymization_sensitivity`; `prefix_rarity_tier`.
- **Interaction menu contribution:** Best fit for `template_rigidity × cutoff_exposure`; secondarily `cutoff × propagation_intensity`.
- **Thales dependency:** Usable now; improved by exact-span rarity and family indexing.
- **Compute budget estimate:** With four prefix probes, `4 × 6 × 2,560 = 61,440`.
- **Key citations:** [Carlini et al. 2020](https://arxiv.org/abs/2012.07805), [Nasr et al. 2023](https://arxiv.org/abs/2311.17035), [Lee et al. 2021](https://arxiv.org/abs/2107.06499).
- **Risks / caveats:** Very low base rate; excellent corroboration, poor omnibus power.

**Stats-Lens Synthesis**
- **Top 3 picks by identifiability × power:** `Paired Cutoff Surprise Gap`, `Entity-Anonymization Delta`, and `CMMD`. PCSG is the cleanest cutoff-identified contrast. EAD is the best paired within-case intervention and directly serves P5. CMMD is the best all-fleet cross-bloc detector. `Counterfactual Fact Inertia` is fourth and becomes top-3 if Thales can guarantee high-quality perturbations.
- **What I would preregister as primary vs reserve:** Primary = PCSG, CMMD, EAD, Counterfactual Fact Inertia, Min-K++. Reserve/validation = Extraction-Lite, FinMem-NoOp. I would not let FinMem-NoOp into the confirmatory family until a pilot shows acceptable reliability.
- **Ensemble vs independent:** Independent. From an FWER standpoint, a heterogeneous logistic ensemble is a bad trade: it creates another detector, obscures construct meaning, and inherits the post-hoc identification concerns in [Meeus et al. 2024](https://arxiv.org/abs/2406.17975). If you insist on a composite, make it one **surface-only descriptive composite**, train it on a held-out calibration split, and count it as one extra detector outside the confirmatory family. I infer from [Roy & Roy 2026](https://arxiv.org/abs/2603.26797) that their MCS is useful operationally, but not the right primary estimand for this benchmark paper.
- **Most under-powered bloc:** **Bloc 3: Institutional stage / source.** Even with event-phase balancing, it contains the most categorical structure, the most correlation, and one unfrozen factor (`Disclosure Regime` vs possible `Modality` replacement). That is the bloc most likely to lose precision once bloc-mates are jointly conditioned on.
- **Joint-modeling specification:** Fit one stacked mixed model on detector-standardized scores:
  `z_imd = alpha_d + a_im + b_m + sum_j x_ijm (beta_j + u_jd) + sum_p∈P4 w_pijm (theta_p + v_pd) + e_imd`
  where `i` = case, `m` = model, `d` = detector; `a_im` is a case×model random intercept capturing shared memorability across detectors; `b_m` is a model intercept; `u_jd` and `v_pd` are detector-specific random-slope deviations with strong shrinkage. Include all bloc-mates jointly, never bloc summaries. Use coarse Event Type confirmatorily, fine Event Type descriptively with partial pooling. Then control the confirmatory family with **Westfall-Young stepdown max-T** across all primary `detector × factor` coefficients, which is much less wasteful than Bonferroni because the tests are dependent. Report all P4 interactions with shrinkage estimates and simultaneous CIs, but do not spend confirmatory alpha there.
- **Power warning on interactions:** The hardest menu cells are the tail-restricted ones. In particular, `target_salience × propagation_intensity | target_salience=low` and any company-only Tradability interaction will need large effects unless low-salience prevalence is healthier than I expect.
- **Questions for Quant / NLP / Editor before R5A Step 2:**
  1. Quant: what is the expected realized distribution of `cutoff_gap_days` by model after gray-band exclusion, and can you preregister placebo pseudo-cutoff controls?
  2. NLP: can Thales produce deterministic target spans, competitor spans, placebo masks, and counterfactual edits with auditable pass rates?
  3. Editor: will `Disclosure Regime` be frozen before detector lock, and what is the finalized anchor-strength rubric reliability threshold?
  4. NLP + Editor: can you define a rule-based FinMem-NoOp clause bank with explicit proofs of target irrelevance? If not, keep NoOp reserve-only.

Core measurement references for the paper framing: [Cronbach & Meehl 1955](https://pubmed.ncbi.nlm.nih.gov/13245896/), [Xiao et al. 2023](https://aclanthology.org/2023.emnlp-main.676/), [Perlitz et al. 2024](https://aclanthology.org/2024.naacl-long.139/), [Kearns 2026](https://arxiv.org/abs/2602.15532), [Nomological Networks for LLM Benchmarks 2026](https://arxiv.org/abs/2603.15121).
