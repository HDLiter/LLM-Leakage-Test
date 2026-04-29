**Sources Read**

[Decision memo](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md), [frozen shortlist](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md), [Phase 7 plan](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md), [WS1 cloud plan](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md), [fleet YAML](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml), [OSS landscape scan](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/PCSG_PAIR_HUNT/open_source_landscape.md).

## A1. PCSG Cross-Version Confounding

**Attack:** PCSG is now anchored on `qwen2.5-7B` versus `qwen3-8B`, but that is not a clean late-vs-early exposure contrast. It is a cross-generation product comparison. Qwen3 differs from Qwen2.5 in pretraining corpus composition, data scale, reasoning/thinking behavior, post-training, instruction recipe, EOS/chat template behavior, likely filtering, and maybe finance-domain coverage. Even if the tokenizer core overlaps, the model family changed. A higher logprob on 2024 CLS articles could mean “Qwen3 is a better Chinese financial-news model,” not “Qwen3 saw the article.” The design turns a vendor lineage jump into a causal cutoff estimator and then hides the confound behind tokenizer compatibility.

**Defense status:** **Partial defense.** The design has real controls: common-vocab restriction `max_token_id <= 151664`, same dense paradigm, same official AWQ regime, Path E `cutoff_observed`, and an exploratory within-family capacity curve. But none controls Qwen2.5→Qwen3 recipe/data-composition drift. The current design defends token alignment, not causal attribution.

**Paper-day suggestion:** State that E_PCSG is a “Qwen cross-version exposure-correlated contrast,” not a causal cutoff estimator; add a same-family same-cutoff falsification panel and make any causal language conditional on it being small.

## A2. Path E Knee Is Market-Regime Artifact

**Attack:** CLS financial news is not temporally exchangeable. 2023-2024 Chinese finance news had regime shifts: real estate distress, policy rescue cycles, anti-corruption campaigns, capital-flow narratives, and repeated templates. A monthly Min-K% curve can drop because market language changed, article templates changed, or entity mix shifted, not because model training stopped. Without a negative-control corpus or date-shuffled/topic-matched controls, “knee detection” is just financial-cycle detection dressed up as cutoff inference.

**Defense status:** **Partial defense.** The design has post-cutoff BL2 and same-cutoff warning checks in the Phase 7 plan, and Path E uses both Min-K% and P_extract. But Path E itself is CLS-only; non-financial Chinese control is explicitly stretch-only, not a gate. There is no topic-regime negative control for knee detection.

**Paper-day suggestion:** Add a matched Chinese non-financial news corpus or a CLS topic/category/date-shuffled placebo knee test; require model-specific knees to survive category/date-window adjustment.

## A3. AWQ Qwen Versus fp16 GLM Pooling

**Attack:** E_CTS pools Min-K% tail logprobs across AWQ-INT4 Qwen and fp16 GLM. That is not a harmless implementation detail. Quantization distorts the low-probability tail non-uniformly, and Min-K%++ is explicitly a bottom-tail statistic. GLM’s fp16 scores and Qwen’s INT4 scores are not on the same measurement scale. A `quant_scheme` label documents the confound but does not remove it.

**Defense status:** **No defense** for raw cross-family pooled E_CTS. The fleet records `quant_scheme`, and Qwen within-family comparisons are quantization-consistent, but the mixed model as described does not calibrate or normalize tail logprobs by quantization/backend.

**Paper-day suggestion:** Standardize CTS within model using calibration corpora, report GLM separately, or restrict confirmatory CTS to quantization-homogeneous Qwen models.

## A4. Cutoff Provenance Circularity

**Attack:** Most cutoffs are not facts. Qwen2.5 is community paraphrase, Qwen3 and GLM are operator inferred, GPT-5.1 is operator inferred, and only Claude has vendor-stated provenance. The study then “discovers” cutoff behavior using a probe designed around those same assumed dates. This risks circularity: the empirical cutoff probe validates the experimenter’s own guessed timestamps, not vendor ground truth.

**Defense status:** **Partial defense.** The design is unusually honest: `cutoff_source` is explicit, and confirmatory analysis may not rely on inferred cutoffs without Path E. It also stores both `cutoff_date_yaml` and `cutoff_observed`, with observed primary. But Path E estimates an empirical familiarity horizon, not a vendor training cutoff.

**Paper-day suggestion:** Rename `cutoff_observed` to `exposure_horizon_observed`; never claim vendor cutoff recovery unless vendor-stated dates exist.

## A5. 60 Articles/Month Cannot Give Day Precision

**Attack:** CLS publishes hundreds of items per day, but Path E samples 60 per month. That is maybe two articles per day equivalent, with strong topic clustering. The design invokes minute-resolution timestamps while using month-binned sampling. It cannot distinguish January 5 from January 25, or month X from spillover in month X+1, let alone support precise cutoff labels for E_PCSG.

**Defense status:** **No defense** for day-level cutoff precision. The current plan is month-stratified and outputs knee width, but the sampling design supports coarse month/quarter horizons, not precise dates.

**Paper-day suggestion:** Downclaim to month-level exposure horizons, or add adaptive dense resampling around candidate knees with confidence intervals.

## A6. Capacity Curve Novelty Is Zero

**Attack:** Capacity-mediated memorization is already established by Carlini-style scaling work. Five Qwen2.5 points and four Qwen3 points on Chinese news do not create a new scientific contribution. This is a single diagnostic figure, and if the paper sells it as novelty, reviewers will see filler.

**Defense status:** **We have defense.** The current design labels `E_PCSG_capacity_curve` exploratory, cites Carlini 2021/2022, and does not spend confirmatory alpha on it. That is appropriate if the paper treats it as a control/diagnostic.

**Paper-day suggestion:** Present it as a replication sanity check and confound diagnostic, not as a contribution.

## A7. Chinese Financial News Does Not Generalize

**Attack:** CLS is a narrow, highly templated, Chinese financial-news domain. Leakage signals there may reflect institutional templates, repeated entities, and market-reporting conventions, not general LLM data leakage. A title or conclusion implying general-purpose LLM leakage would overclaim from one domain.

**Defense status:** **Partial defense.** The plan frames CLS Chinese financial news as primary and treats English/non-financial expansion as stretch. But there is no empirical generalization study.

**Paper-day suggestion:** Put “Chinese financial news” in the title/abstract claim boundary; describe R5A as a domain benchmark, not a general leakage benchmark.

## A8. C_FO Confounds Memorization With Sycophancy

**Attack:** False-outcome override does not isolate memorization. If the prompt says a false outcome and the model follows it, that may be instruction-following; if it resists, that may be truthfulness prior, calibration, or refusal to accept contradiction. Wang et al. is sycophancy-oriented, so importing its mechanism stack does not make this memorization. WS6 would mechanize the same confound.

**Defense status:** **No defense** for a memorization-specific interpretation. The C_FO audit checks naturalness and slot validity, but no control separates memory from sycophancy, instruction hierarchy, or general factual priors.

**Paper-day suggestion:** Rename E_FO as “counterfactual outcome resistance,” add sycophancy controls, and make WS6 explicitly exploratory/discriminative rather than memorization-localization.

## A9. Fleet Is Mostly Qwen

**Attack:** Ten of fourteen models are Qwen-family, and the primary PCSG pair is Qwen-only. The white-box evidence is overwhelmingly Qwen evidence. Cross-vendor claims are unsupported because GLM is a singleton and black-box models do not enter P_logprob.

**Defense status:** **Partial defense.** The OSS scan gives a practical reason: no clearly better Chinese-capable same-tokenizer dense cutoff pair. But feasibility is not validity. The design supports Qwen-centered claims, not broad vendor generalization.

**Paper-day suggestion:** Split claims into “Qwen white-box temporal evidence” and “black-box behavioral corroboration”; avoid saying fleet-wide unless effects replicate outside Qwen.

## A10. WS1 Hidden-State Reproducibility Burden

**Attack:** Hidden-state extraction across 30 cases, 10 models, tens of layers, and fp16 activations is a large artifact pipeline. External teams need the same checkpoints, tokenizer SHAs, Docker digest, cloud GPU, trace serialization, and enough disk. Without a packaged reproduction recipe and artifact manifest, WS6 is effectively lab-specific.

**Defense status:** **Partial defense.** The design records tokenizer SHA, HF commit SHA, Docker digest, run manifests, and limits hidden states to 30 articles. WS1 estimates about 20 GB, which is manageable. But pins are still `<TBD>` until run time, and artifact publication is not specified.

**Paper-day suggestion:** Publish exact manifests, tokenizer/model SHAs, Docker digest, case IDs, artifact schema, and a recomputation script; keep WS6 out of the core claim.

## Most Threatening Attacks

1. **A1:** PCSG cross-version confounding. This directly attacks the main temporal-exposure estimator.
2. **A2:** Path E knee confounding. This attacks the empirical cutoff defense that the redesigned paper now depends on.
3. **A8:** C_FO sycophancy conflation. This attacks the behavioral memorization interpretation and WS6 mechanism story.

## Concedable Caveats

1. **A6:** Capacity curve novelty. Safe to concede if framed as diagnostic replication.
2. **A7:** Domain lock to Chinese financial news. Safe if title and conclusions are narrowed.
3. **A10:** Hidden-state reproducibility burden. Safe if WS6 is exploratory and manifests/artifacts are published.