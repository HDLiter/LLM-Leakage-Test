## 1. E_PCSG

**Verdict: partially sound.**

The token restriction is necessary, but it only solves token-level comparability: the design restricts Qwen2.5/Qwen3 PCSG to `max(token_id) <= 151664` and computes `logprob(qwen3-8B) - logprob(qwen2.5-7B)` on matched tokens [decision](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:48). It does not isolate cutoff exposure from Qwen3 recipe/data-mixture/RL/post-training changes; the shortlist explicitly admits E_PCSG also reflects “pretraining-recipe / training-data-composition differences” [shortlist](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:60). Treat it as a cutoff-consistent temporal contrast, not yet a clean cutoff-exposure estimand.

**Remediation:** require a second confirmatory-quality temporal pair before E_PCSG carries primary weight: ideally Llama-3-8B vs Llama-3.1-8B for vendor-stated same-size cutoff contrast, or an empirically probed Qwen2-7B vs Qwen2.5-7B bridge if the cutoff gap is real [landscape](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/PCSG_PAIR_HUNT/open_source_landscape.md:387). At minimum, pre-register a difference-in-differences calibration: common-pre-cutoff articles estimate Qwen3-vs-Qwen2.5 baseline fluency, between-cutoff articles estimate excess familiarity, and post-cutoff BL2 must be near zero.

**Silent assumption:** Qwen2.5 and Qwen3 differ mainly by data horizon, not by financial-domain corpus weighting, post-training, thinking policy, or Qwen3’s reasoning template.

## 2. E_PCSG Capacity Curve

**Verdict: partially sound.**

Within-family curves are better controlled than the cross-family PCSG because tokenizer, cutoff, paradigm, and quantization are intended to stay fixed while parameter count varies [ws1 plan](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:68). But a positive log2(params) slope identifies capacity-sensitive likelihood, not necessarily memorization: larger models can score higher on Chinese financial-news register, entity priors, and boilerplate even when they have not memorized the article. The local docs correctly keep this exploratory, not confirmatory [shortlist](D:/GitRepos/LLM-Leakage-Test/refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md:94).

**Remediation:** test whether the slope is selectively larger for likely-exposed/high-recurrence pre-cutoff articles than for post-cutoff controls, synthetic CLS-style nonmembers, and topic/length/category-matched negatives. Use recurrence, salience, template rigidity, category, date-window, and event type as covariates; the pilot already plans metadata-only and text-light baselines for this purpose [phase7](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:779).

**Silent assumption:** capacity-mediated memorization has a separable signature from general capacity-mediated language modeling.

## 3. Path E Cutoff Probe

**Verdict: partially sound.**

Path E’s 36-month, 2,160-article month-stratified CLS probe is a good empirical check against unsupported cutoff dates [decision](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:113). But a month-vs-Min-K% knee estimates an observed familiarity horizon, not the true training cutoff, unless the monthly article distribution is stable. In 2023-2025 A-share news, knees could be induced by regime/topic shifts: COVID reopening exit, CSRC policy tightening, real-estate distress, foreign-capital flow coverage, AI-stock bubble, IPO/STAR-board themes, source-template changes, or entity churn.

**Remediation:** add topic/category/source/length/template-rigidity/numeric-density/entity-salience covariates, and require the knee to persist within matched topic strata. Add negative controls: post-all-cutoff articles, non-financial Chinese news from the same months, and pseudo-cutoff permutations; BL2 already specifies post-cutoff equivalence logic for temporal signals [phase7](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:798).

**Silent assumption:** month is acting as exposure time, not as a proxy for news regime, corpus pipeline, or register drift.

## 4. C_FO Override / E_FO

**Verdict: partially sound, bordering unsound if interpreted alone as memorization.**

The perturbation quality design is careful: C_FO requires verified outcomes, clean slotability, span metadata, and full audit [phase7](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:366). But behavioral E_FO measures “signed-score non-compliance to visible false outcome” [phase7](D:/GitRepos/LLM-Leakage-Test/plans/phase7-pilot-implementation.md:701), which can arise from memorized truth, instruction-following differences, truthfulness tuning, refusal style, or sycophancy dynamics. The WS6 rationale itself invokes Wang et al. 2025, where sycophancy appears as late-layer preference shift plus representational divergence, so the same machinery can explain override without proving training exposure [decision](D:/GitRepos/LLM-Leakage-Test/docs/DECISION_20260427_pcsg_redefinition.md:152); [arXiv 2508.02087](https://arxiv.org/abs/2508.02087).

**Remediation:** include nonmember C_FO controls: post-cutoff events, fabricated CLS-style articles with no real-world outcome, and low-salience events unlikely to be memorized. Also vary instruction framing (“use only the article” vs neutral vs user-opinion framing) to estimate sycophancy/instruction-following susceptibility separately from cutoff exposure.

**Silent assumption:** resistance to a false visible outcome is caused by memorized article knowledge rather than a general truthfulness or anti-user-belief override.

## 5. AWQ-INT4 vs fp16 E_CTS Pooling

**Verdict: unsound for raw pooled fleet-level E_CTS; partially sound for within-Qwen contrasts.**

The fleet logs `quant_scheme`, with Qwen2.5/Qwen3 in AWQ-INT4 and GLM-4-9B in fp16 because no official GLM AWQ exists [fleet](D:/GitRepos/LLM-Leakage-Test/config/fleet/r5a_fleet.yaml:65), [ws1 plan](D:/GitRepos/LLM-Leakage-Test/plans/ws1-cloud-execution.md:57). But a categorical field records the threat; it does not remove precision-induced shifts in token logprobs, and the effect is model-, domain-, kernel-, group-size-, and calibration-dependent. The AWQ paper reports INT4 AWQ WikiText2 perplexity deltas such as Llama-2-7B 5.47→5.60 and LLaMA-7B 5.68→5.78, about 0.02 nats/token when converted from PPL, while also showing calibration-distribution sensitivity in other settings [AWQ](https://ar5iv.labs.arxiv.org/html/2306.00978v5). That is small on average, but Min-K tail scores amplify token-level perturbations; without measuring the R5A cutoff signal scale, you cannot assert it is negligible.

**Remediation:** do not pool raw E_CTS across AWQ and fp16 as a cutoff estimand. Calibrate within model, include model random effects, run sensitivity excluding GLM, and rescore a stratified Qwen subset in fp16/bf16 versus AWQ to estimate `delta_min_k = AWQ - fp16` directly on Chinese financial news.

**Silent assumption:** AWQ perturbs Min-K% scores by a stable additive offset that is smaller than the cutoff signal.

## Load-Bearing Assumptions To Pre-Register

1. **Cutoff exposure is empirically recoverable.** Defend by making Path E mandatory, reporting `cutoff_observed`, knee width, topic-stratified robustness, and BL2/pseudo-cutoff failures before confirmatory claims.

2. **Cross-version Qwen PCSG is not mostly recipe/data-mixture drift.** Defend with common-pre-period calibration, post-cutoff equivalence, same-cutoff early-warning ratios, and at least one independent temporal pair or bridge pair.

3. **Logprob metrics are comparable after tokenizer/quantization controls.** Defend by enforcing vocab intersection, recording tokenizer/checkpoint/quant provenance, calibrating scores within model, and publishing an AWQ-vs-fp16 rescoring audit on the R5A corpus.