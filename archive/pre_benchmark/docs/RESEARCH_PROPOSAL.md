# Task Design Shapes Look-Ahead Leakage: Measuring Contamination Across Task Types in Chinese Financial News LLM Pipelines

## 1. Abstract
Large language models (LLMs) are increasingly inserted into financial NLP pipelines, yet evaluation is vulnerable to look-ahead contamination: models may encode future market-relevant facts from pretraining rather than infer from text. This risk is consequential in Chinese A-share settings, where recent vendor models can appear highly predictive on archived news while exploiting parametric memory. This proposal investigates whether leakage is shaped not only by model properties but also by task design. Using more than one million CLS telegraph articles from 2020 to 2026 and a 1,000-item benchmark, the study measures whether contamination attenuates as tasks move from direct return prediction to sentiment classification and then to decomposed, text-grounded indicators such as authority and novelty, while controlling for output format, token budget, and answer entropy to separate the task-design channel from format confounds. Methodologically, the project combines white-box auditing on Qwen 2.5 7B with Min-K% probability as an article-familiarity prior, black-box counterfactual auditing on DeepSeek-chat, and item-level heterogeneity analysis, embedded in a measurement and econometric framework of look-ahead bias. An orthogonalization sensitivity analysis tests whether contaminated LLM features survive XGBoost aggregation and inflate historical return predictability. The project will release the CLS-Leak benchmark, prompt templates, and a temporal decay dataset. Its central contribution is an empirical finding with design implications: task formulation materially shapes the degree of leakage exposure in financial LLM pipelines, and decomposed text-grounded extraction attenuates contamination relative to outcome-proximal tasks.

## 2. Introduction and Motivation
Large language models are increasingly used to transform financial text into signals for prediction, ranking, and trading. Their attraction is obvious: they are flexible, inexpensive at inference time, and strong at extracting structure from unstructured news. Their evaluation problem is equally obvious but more serious. When an LLM is tested on historical financial news, it may already encode the same article, a close paraphrase, or the later market outcome in its parameters. Apparent performance may therefore reflect hidden future knowledge rather than text-grounded inference. In finance, this is not merely benchmark contamination. It is a form of false alpha.

Recent studies describe this failure as profit mirage, temporal contamination, or look-ahead bias, but the evidence is still concentrated in English-language, U.S.-market settings and outcome-proximal tasks such as QA, direct forecasting, and agentic trading. Chinese A-share news remains underexplored, and most existing studies use a single detector family at a time. That leaves two unresolved questions: whether leakage behaves similarly in Chinese financial text, and whether it is a stable phenomenon across access regimes rather than an artifact of one method.

Before proceeding, it is necessary to distinguish several related but distinct phenomena. **Pretraining memorization** refers to an LLM encoding specific training sequences verbatim or nearly so. **Benchmark contamination** refers to evaluation data appearing in training data, inflating scores. **Look-ahead leakage** — the focus of this study — refers to a model's parametric memory encoding future-relevant facts (market outcomes, later developments) that were temporally available at training time but should not be available at inference time for fair evaluation. **Task-answer inferability** refers to the degree to which a task's answer can be derived from text-internal evidence alone, independent of memorization. This study measures look-ahead leakage through indirect proxies (article familiarity and counterfactual sensitivity), not through direct observation of training data.

This project addresses both questions by investigating leakage as a function of task design. Direct prediction gives memorized outcomes the shortest route to the answer. Sentiment classification reduces, but does not remove, that route. Decomposed prompts for text-grounded indicators such as authority and novelty should weaken the memorization channel by forcing the model to attend to textual evidence instead of recalled outcomes. The idea comes from the Thales quantamental engine, where LLMs produce intermediate features that are later aggregated by XGBoost. If those features are contaminated, the whole pipeline inherits look-ahead bias; if decomposition attenuates contamination, task design becomes a practical mitigation lever. A key methodological challenge is that task types differ not only in their proximity to outcomes but also in output format, answer entropy, and difficulty. The study therefore includes matched-format ablations and a sham-decomposition control to help distinguish the task-design channel from these confounds. The proposal asks not only whether leakage exists, but whether task formulation measurably shapes its magnitude in Chinese financial news pipelines.

## 3. Literature Review

### 3.1 Financial Leakage and Look-Ahead Bias
Li et al. (2025) show in *Profit Mirage* that financial LLM agents can look strong in backtests yet collapse after the training cutoff, establishing contamination as an economically material problem. Zhang, Chen, and Stadie (2026) add an important refinement: not all leakage matters equally, and decision-critical contamination should be separated from peripheral contamination. Gao, Jiang, and Yan (2026) explicitly recast the problem as look-ahead bias in forecasting, while Benhenda (2026) and Yan et al. (2026) move toward standardized finance-specific benchmarks and temporally bounded baselines. The main limitation of this literature is its scope: it is largely U.S.-centric, English-only, focused on direct decision tasks, and usually organized around binary pre/post-cutoff comparisons rather than continuous temporal decay.

### 3.2 Detection Methods Hierarchy
The detection literature is best understood by access level. Shi et al. (2024) provide the white-box anchor with Min-K% probability, while Zhang et al. (2025) show that calibrated variants can improve its reliability. Dong et al. (2024) demonstrate that grey-box or black-box signals can also reveal contamination through output behavior, and Ravaut et al. (2025) systematize these methods in LLMSanitize. At the same time, Duan et al. (2024) show that many membership-inference attacks are weak on realistic long-text settings, and Yang et al. (2023) show that paraphrases can evade naive decontamination. Oren et al. (2024) extend black-box contamination proof to settings without logprob access. Jiang et al. (2024) demonstrate that data contamination can cross language barriers, relevant because Chinese financial text may be contaminated through English paraphrases in pretraining data. Golchin and Surdeanu (2024) show that task-format contamination inflates few-shot performance beyond data-level leakage. The implication is clear: no single detector is sufficient, and contamination operates at both data and task levels. This motivates a cross-access design combining Qwen-based Min-K% auditing with DeepSeek counterfactual auditing on the same benchmark.

### 3.3 Task Decomposition in Finance
Work on financial task design suggests that decomposition matters, but not yet as leakage control. Bastianello et al. (2024), Li et al. (2025), Cao et al. (2024), and Liang et al. (2025) all show that staged or structured extraction can improve interpretability and predictive usefulness. Iacovides et al. (2025) add a cautionary result: standard fine-tuning can intensify memorization in financial sentiment tasks. Together, these studies imply that prompt and task structure shape what information the model expresses, but none directly tests whether decomposed, text-grounded indicators reduce contamination relative to direct prediction.

### 3.4 Cross-Disciplinary Tools
Cross-disciplinary tools strengthen the design. Jin et al. (2025) distinguish memory from reasoning in LLM evaluation; Arjovsky et al. (2019) and Geirhos et al. (2020) explain why models prefer shortcut solutions; Lalor et al. (2016), Vania et al. (2021), and Swaminathan and Rogers (1990) provide item-level tools for separating general difficulty from group-specific distortion. These literatures suggest a useful synthesis for the present project: a causal DAG for conceptual clarity, econometric testing for look-ahead bias, and DIF analysis for article-level heterogeneity. That combination is absent from the existing Chinese financial leakage literature.

## 4. Research Questions and Hypotheses
This study addresses three research questions aligned with the final project plan.

**RQ1 (Primary). Does measured leakage attenuate as tasks move from direct prediction to sentiment classification to decomposed text-grounded indicators on Chinese A-share news, after controlling for output format and task difficulty?**  
**H1.** For the same articles, black-box counterfactual sensitivity will follow the ordered pattern `direct > sentiment > decomposed`. This attenuation will survive matched-format ablations that equalize output schema and token budget, and will not be replicated by a sham-decomposition prompt that preserves structured output but replaces economically grounded sub-indicators with arbitrary ones. Each sub-indicator (authority, novelty) will be tested separately rather than pooled.

**RQ2 (Supporting). Do article-level contamination signals from different models and access regimes exhibit concordance?**  
**H2.** Article-level familiarity scores derived from Qwen Min-K% (as an article-familiarity prior) and DeepSeek counterfactual sensitivity will exhibit a positive partial Spearman rank correlation after controlling for article length, date, and prominence, and the clustered bootstrap confidence interval will exclude zero. This tests cross-model concordance, not mutual validation of methods measuring the same latent construct.

**RQ3 (Exploratory). Is measured contamination associated with inflated historical short-horizon return predictability in a downstream XGBoost pipeline?**  
**H3.** LLM feature sets with higher measured contamination will be associated with stronger historical short-horizon predictability than orthogonalized features, but that incremental association will attenuate on the freshest holdout period. A positive contamination-signal interaction coefficient in return regressions will serve as a diagnostic indicator (not a causal estimate) that part of the measured signal co-varies with leakage proxies.

These hypotheses are falsifiable. A null result is informative in every case: no ordered attenuation would weaken the task-design thesis; no cross-model concordance would imply detector-specific or model-specific artifacts; and no downstream association would limit the practical importance of contamination for quant pipelines.

## 5. Theoretical Framework
The project adopts a two-layer framework — a conceptual model of leakage pathways and an operational measurement strategy — supplemented by item-level heterogeneity analysis.

### 5.1 Conceptual Layer: Leakage Pathway Model
The conceptual distinction is between a memorization pathway and a reasoning pathway. Let `M` denote memorization activation (latent, partially observed through multiple imperfect indicators), `R` text-grounded reasoning, `T` task type, and `Y` the model output. Recency, prominence, and event type affect training familiarity `K`; cue masking and semantic edits intervene on the two pathways differently.

```text
C (recency, prominence, event type) --> K (training familiarity) --> M (memorization) --> Y
                                                                     ^                    ^
D (latent salience/difficulty) ----------------------------------------+------------------+
X (article text) -------------------------------------------------> R (reasoning) -----+
Z (cue masking intervention) ----> M, D
A (semantic counterfactual intervention) ----> R, D
T (task type: direct / sentiment / decomposed) ----> M, R
F (output format, token budget, answer entropy) ----> Y
```

Task type is hypothesized to moderate both pathways. Direct prediction gives memorization the shortest path to the answer; sentiment weakens that path; decomposed indicators should weaken it further by demanding text-grounded judgments. Crucially, `D` (latent salience/difficulty) and `F` (output format) represent confounding pathways: task types differ in difficulty and output structure, not only in outcome proximity. The sham-decomposition control and matched-format ablation are designed to separate the task-design channel from these confounds. The exclusion restrictions — that `Z` primarily affects `M` and `A` primarily affects `R` — are acknowledged as strong and approximately true rather than exact; both interventions also affect task difficulty `D`.

### 5.2 Operational Layer: Measurement and Diagnostic Regression
Operationally, contamination is treated as look-ahead bias and measured through imperfect proxies. The study does not observe `M` directly; it uses Min-K% scores as an article-familiarity prior and counterfactual response change as a behavioral contamination signal. Two operational ideas are central: temporal decay and contamination-signal association.

If leakage comes from latent future knowledge, measured contamination should vary with temporal distance from the model's effective knowledge frontier. If it co-varies with downstream signal quality, it suggests that part of measured performance is explained by leakage. Let `S_i` be an LLM-derived feature, `C_i` a contamination proxy, and `r_{i,h}` the `h`-day abnormal return:

```text
r_{i,h} = alpha + beta*S_i + theta*(S_i x C_i) + X_i'gamma + tau_t + eta_g + epsilon_i
```

where `X_i` contains article controls (length, prominence, event type), `tau_t` time effects, and `eta_g` group effects. A positive `theta` is interpreted as a diagnostic association — suggesting that predictive power co-varies with contamination — not as a causal estimate of leakage-induced alpha. Key threats to interpretation include omitted salience variables that raise both contamination and true predictability, measurement error in `C_i`, and the generated-regressor nature of the contamination proxy. These threats are addressed through cross-fitted estimation, sensitivity analysis, and bounded interpretation.

### 5.3 Item-Level Heterogeneity Analysis
Aggregate averages can hide strong item heterogeneity. The study uses mixed-effects item models to ask whether particular articles become unusually "easy" under contaminated conditions after controlling for baseline difficulty. Articles are items, model-task-condition combinations define the grouping structure, and the grouping variable distinguishes more contaminated from cleaner regimes. This analysis identifies which article types — such as prominent firms or highly propagated events — carry disproportionate leakage risk. Differential item functioning (DIF) is applied as an exploratory diagnostic tool rather than a headline contribution, given the limited "respondent" population in the model-task-condition space.

## 6. Methodology

### 6.1 Data and Benchmark Construction
The primary corpus contains more than one million CLS telegraph entries from January 2020 to February 2026. From this pool, the project will construct a curated 1,000-case event-level benchmark, **CLS-Leak**, rather than treating raw near-duplicate news items as independent observations.

**Sampling protocol.** Events are clustered by entity and date (same company, same day) to deduplicate propagated rewrites; the effective sample size after clustering will be explicitly reported alongside the nominal 1,000-case count. Sampling is stratified by six temporal bins (2020, 2021, 2022, 2023, 2024, 2025+), three company-prominence tiers (SSE50 / CSI300-ex-SSE50 / small-cap), and four event types (policy, corporate, industry, macro). Each stratum targets proportional representation with minimum 30 events per temporal bin to support subgroup analysis. Subgroup analyses are labeled exploratory and report minimum detectable effect sizes.

**Counterfactual generation and quality control.** Each event will include the original article, a neutral paraphrase control (label-preserving), and targeted counterfactual variants. For direct prediction and sentiment tasks, edits reverse or materially alter decision-relevant semantics. For decomposed tasks, edits target authority (provenance swaps: regulator notice versus unattributed rumor) and novelty (first-disclosure versus routine-follow-up). All counterfactual variants undergo: (1) LLM-as-judge plausibility rating, (2) style and edit-distance matching to the original, (3) retrieval-based nonexistence check ensuring the variant does not accidentally reproduce a real article, and (4) human spot-check on a 200-item anchor subset with financial domain expertise. The anchor subset also validates decomposition labels and retrieval-based novelty proxies with weighted kappa inter-rater agreement.

**Release plan.** Benchmark outputs will include event identifiers, prompts, counterfactual variant metadata, and contamination scores. Full article text release depends on CLS licensing; if text cannot be shared, the release will include article hashes, metadata, and a reconstruction script. Market data are added only in the final stage for short-horizon abnormal-return validation.

### 6.2 Models and Access Regimes
The study uses two complementary access regimes. DeepSeek-chat is the deployment-relevant black-box model and is used for counterfactual auditing and the downstream economic pipeline. Qwen 2.5 7B, served through vLLM, provides token log-probabilities for white-box Min-K% auditing. Prompts will be frozen before the main run, temperature fixed at zero where possible, and inference metadata archived to limit reproducibility drift.

### 6.3 Detection Methods
The project combines two complementary detection families at different access levels. Qwen supplies white-box Min-K% scores as an **article-familiarity prior** — measuring how likely the article text itself was in the pretraining distribution, normalized within length bins and with digit/entity masking to reduce domain-specific token bias. This score is article-level and task-independent; it serves as a covariate and concordance anchor rather than a task-conditioned leakage measure.

DeepSeek supplies black-box **counterfactual sensitivity metrics** — prediction consistency, item-level response change under semantic edits, and response stability across neutral paraphrases. The key estimand is **excess invariance**: the degree to which a model's response is stable under decision-relevant semantic edits *relative to its stability under neutral paraphrases*. High excess invariance suggests the model's answer is driven by memorized knowledge rather than textual evidence. These metrics are task-conditioned because the same article is probed under different task prompts (direct, sentiment, decomposed), making them the primary evidence for the leakage spectrum hypothesis (RQ1). To validate that excess invariance reflects leakage rather than generic semantic robustness or prompt under-specification, the study includes a **placebo analysis** on articles clearly beyond the model's knowledge frontier (post-2025 news), where excess invariance should be minimal.

Item-level heterogeneity analysis (mixed-effects models, exploratory DIF) is used as a descriptive layer, asking which article types carry disproportionate leakage risk after controlling for baseline difficulty.

### 6.4 Experimental Design
The experiments are ordered to support the paper's narrative. The first four constitute the core; the remaining two are supplementary and can be deferred if the core results are strong.

#### E1. Temporal leakage decay curve (Core)
E1 estimates how contamination changes continuously with article age using both Qwen Min-K% and DeepSeek counterfactual scores. The goal is a continuous temporal decay function (not binary pre/post), estimated via local regression or penalized splines, with secondary splits by prominence and event type. As a descriptive robustness exercise, local-window analyses will be conducted around externally documented model release dates and any public training-data cutoff disclosures; no cutoff dates are selected from the data itself.

#### E2. Cross-model concordance (Core)
E2 tests whether article-level contamination signals agree across models and access regimes. For each article, white-box familiarity scores (Qwen Min-K%) and black-box counterfactual sensitivity (DeepSeek) will be compared by partial Spearman rank correlation controlling for article length, date, and prominence, with clustered bootstrap confidence intervals. This is framed as cross-model concordance — whether certain articles are broadly more contamination-prone — not as mutual validation of detection methods.

#### E3. Leakage spectrum across task types (Core — primary experiment)
E3 is the core experiment. The same articles will be run under direct prediction, sentiment classification, and decomposed extraction of authority and novelty separately. Because article content is fixed, task type becomes the main experimental variable, and the primary estimand is the ordered contrast in black-box counterfactual sensitivity: `direct > sentiment > decomposed`.

**Matched-format ablation.** To isolate the task-design channel from output format confounds, the study includes ablation variants that equalize output schema (structured multi-field format), token budget (matched completion length), and answer granularity across task types. If the leakage ordering persists after format matching, the effect is more consistent with task-semantic differences than with output-structure artifacts.

#### E4. Sham-decomposition control (Core — falsification)
E4 is the falsification check for E3. It preserves multi-field structure, token budget, evidence-citation burden, and answer difficulty but replaces economically meaningful sub-indicators with arbitrary text-grounded but economically irrelevant ones (e.g., "formality level," "geographic scope," "sentence complexity"). If sham decomposition reduces leakage as much as meaningful decomposition, the task-design claim weakens substantially and the effect is more consistent with output structure than with semantic decomposition.

#### E5. Item-level heterogeneity analysis (Supplementary)
E5 uses mixed-effects models to identify which article types (by prominence, event type, propagation breadth) carry disproportionate leakage risk. Exploratory DIF-style analysis compares older, more contaminated items with cleaner regimes after conditioning on baseline difficulty. This experiment is descriptive and exploratory.

#### E6. Downstream association: XGBoost pipeline sensitivity (Supplementary)
E6 links contamination to quant practice as a sensitivity analysis. Features from the three task types will feed an XGBoost model for short-horizon return prediction. The analysis compares raw, orthogonalized, and contamination-only feature sets using rank IC, hit rate, and abnormal-return spreads. Orthogonalization is cross-fitted and bootstrapped end-to-end, and results are explicitly presented as a diagnostic sensitivity analysis rather than causal contamination removal. The key estimand is whether the performance gap between full and orthogonalized features attenuates on the freshest holdout period.

### 6.5 Statistical Inference Protocol
All inference will respect event-level dependence. Confidence intervals will use clustered bootstrap resampling at the event-cluster level; within-article contrasts will use paired permutation or randomization tests where appropriate; and regressions will include temporal controls, grouped errors, and HAC-style corrections for overlapping return horizons.

**Primary estimand hierarchy.** To control multiplicity, the study pre-specifies two primary estimands: (1) the ordered contrast in black-box excess invariance across task types (E3), and (2) the partial Spearman ρ for cross-model concordance (E2). These two tests constitute the primary family, corrected via stepdown Romano-Wolf. The contamination-signal interaction coefficient θ in the return regression (E6) is a supplementary diagnostic estimand reported separately, not included in the primary family. All other comparisons — temporal bin splits, prominence subgroups, per-indicator breakdowns, DIF analyses — are labeled as exploratory with FDR correction.

**Generated-regressor adjustment.** Where contamination proxies C_i enter regressions as generated regressors, uncertainty from the first-stage estimation is propagated through cross-fitting and full-pipeline bootstrap resampling. One primary return horizon (3-day) is pre-specified; multi-horizon results are secondary.

Throughout, effect sizes and confidence intervals take precedence over isolated p-values.

## 7. Expected Contributions
The primary contribution is an empirical finding with design implications: **task formulation materially shapes leakage exposure** in financial LLM pipelines, and decomposed text-grounded extraction attenuates contamination relative to outcome-proximal tasks. This is supported by three subordinate contributions: (1) the CLS-Leak benchmark — the first leakage audit resource for Chinese A-share financial news, with counterfactual variants and multi-method contamination scores; (2) cross-model concordance evidence showing that article-level contamination signals are consistent across access regimes; and (3) a downstream sensitivity analysis linking contamination to inflated historical predictability in a quant pipeline. The study's claims are bounded: they apply to the tested model families (DeepSeek, Qwen) on Chinese financial telegraph text, and the task-design finding is framed as measured attenuation rather than causal control.

## 8. Timeline and Feasibility
The project is scoped for ten weeks and is feasible under the stated compute and data constraints.

**Weeks 1-2:** Finalize prompt schemas (including matched-format ablation variants and sham-decomposition prompts), event clustering pipeline, temporal bin definitions, and the 200-item human-audited anchor subset.  
**Weeks 3-4:** Construct the 1,000-case benchmark: stratified sampling, counterfactual generation, LLM-as-judge + retrieval-based QC, human spot-check on anchor subset.  
**Weeks 5-6:** Run DeepSeek black-box experiments (E1: temporal decay, E2: concordance baseline) and Qwen white-box Min-K% scoring across all benchmark items.  
**Week 7:** Complete E3 (leakage spectrum with matched-format ablation) and E4 (sham-decomposition control).  
**Week 8:** Run E5 item-level heterogeneity analysis (mixed-effects models + exploratory DIF).  
**Week 9:** Run E6 XGBoost sensitivity analysis with cross-fitted orthogonalization and bootstrap.  
**Week 10:** Finalize robustness checks, figures, artifact packaging, and manuscript submission materials.

**MVP cutline.** If time or compute constraints bind, E5 and E6 are deferred. The minimum viable paper is E1 + E2 + E3 + E4.

Feasibility rests on an already available in-domain corpus, completed pilot notebooks (6 notebooks, 84 test cases), and a fixed model stack. Qwen scoring is manageable locally or on a rented 4090 (estimated ~20h for 1000 cases), and DeepSeek API costs remain moderate (~$10-15 for the full benchmark). The primary target venue is EMNLP Findings; JFDS is an alternative if the economic validation results are strong.

## 9. Risk Analysis and Contingency Plans

**Risk 1: No ordered attenuation across task types.** If decomposed indicators do not show lower leakage than sentiment or direct prediction, the task-design thesis weakens. Contingency: (a) report per-indicator results separately (authority may differ from novelty), (b) test whether attenuation is conditional on prominence or event type, (c) pivot framing to "leakage is task-invariant, making detection rather than task design the practical lever" — still publishable as a null result. E4 (sham control) distinguishes semantic decomposition from format effects regardless of direction.

**Risk 2: Task comparison confound.** Reviewers may argue that lower leakage in decomposed tasks reflects task difficulty or output format rather than task design. Mitigation: the matched-format ablation (E3) and sham-decomposition control (E4) are specifically designed to address this. If the effect survives both controls, the confound argument is weakened.

**Risk 3: Cross-model disagreement.** Qwen Min-K% and DeepSeek counterfactual scores may not correlate. That outcome remains publishable because it would clarify whether contamination is article-intrinsic or model/method-specific. Partial correlation controlling for article-level covariates may reveal concordance on subsets even if the overall correlation is weak.

**Risk 4: Weak decomposed indicator validation.** Novelty and authority lack clean ground truth. Contingency: restrict decomposed core to authority (has metadata quasi-ground-truth from regulator vs rumor provenance) and novelty (has retrieval-based proxy). The 200-item audited anchor subset validates both with weighted kappa inter-rater agreement.

**Risk 5: Scope and feasibility.** If economic validation proves noisy, the MVP remains E1 + E2 + E3 + E4. Multi-horizon tests are cut first, then XGBoost simplified, before any reduction of core contamination experiments. API drift is managed through prompt freezing, a tight execution window, and full inference logging with model version strings archived.

**Risk 6: Benchmark licensing.** If CLS text cannot be released, the benchmark release will include article hashes, metadata, prompts, and a reconstruction script. This limits but does not eliminate the benchmark contribution.

## 10. References
```bibtex
@article{arjovsky2019irm,
  author = {Arjovsky et al.},
  title = {Invariant Risk Minimization},
  year = {2019},
  journal = {arXiv}
}

@article{bastianello2024mentalmodels,
  author = {Bastianello et al.},
  title = {Mental Models and Financial Forecasts},
  year = {2024},
  journal = {SSRN}
}

@article{benhenda2026lookaheadbench,
  author = {Benhenda},
  title = {Look-Ahead-Bench: Standardized Benchmark of Look-ahead Bias},
  year = {2026},
  journal = {arXiv:2601.13770}
}

@article{cao2024ecc,
  author = {Cao et al.},
  title = {ECC Analyzer: Trading Signal from Earnings Calls},
  year = {2024},
  journal = {arXiv:2404.18470}
}

@inproceedings{dong2024cdd,
  author = {Dong et al.},
  title = {Generalization or Memorization: CDD/TED},
  year = {2024},
  booktitle = {ACL Findings}
}

@inproceedings{duan2024mimir,
  author = {Duan et al.},
  title = {Do Membership Inference Attacks Work on Large Language Models?},
  year = {2024},
  booktitle = {COLM}
}

@article{gao2026lap,
  author = {Gao and Jiang and Yan},
  title = {A Test of Lookahead Bias in LLM Forecasts},
  year = {2026},
  journal = {arXiv:2512.23847}
}

@article{geirhos2020shortcut,
  author = {Geirhos et al.},
  title = {Shortcut Learning in Deep Neural Networks},
  year = {2020},
  journal = {Nature Machine Intelligence}
}

@article{iacovides2025findpo,
  author = {Iacovides et al.},
  title = {FinDPO: Financial Sentiment via Preference Optimization},
  year = {2025},
  journal = {arXiv:2507.18417}
}

@inproceedings{jin2025memoryreasoning,
  author = {Jin et al.},
  title = {Disentangling Memory and Reasoning Ability in LLMs},
  year = {2025},
  booktitle = {ACL}
}

@inproceedings{lalor2016irt,
  author = {Lalor and Wu and Yu},
  title = {Building Evaluation Scales using Item Response Theory},
  year = {2016},
  booktitle = {EMNLP}
}

@article{li2025profitmirage,
  author = {Li et al.},
  title = {Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents},
  year = {2025},
  journal = {arXiv:2510.07920}
}

@article{li2025structuredevent,
  author = {Li et al.},
  title = {Structured Event Representation and Stock Return Predictability},
  year = {2025},
  journal = {arXiv:2512.19484}
}

@article{ravaut2025llmsanitize,
  author = {Ravaut et al.},
  title = {How Much are LLMs Contaminated? LLMSanitize},
  year = {2025},
  journal = {TMLR}
}

@inproceedings{shi2024mink,
  author = {Shi et al.},
  title = {Detecting Pretraining Data from LLMs},
  year = {2024},
  booktitle = {ICLR}
}

@article{swaminathan1990dif,
  author = {Swaminathan and Rogers},
  title = {Detecting Differential Item Functioning Using Logistic Regression Procedures},
  year = {1990},
  journal = {Journal of Educational Measurement}
}

@inproceedings{vania2021irt,
  author = {Vania et al.},
  title = {Comparing Test Sets with Item Response Theory},
  year = {2021},
  booktitle = {ACL-IJCNLP}
}

@article{white2024livebench,
  author = {White et al.},
  title = {LiveBench: A Challenging, Contamination-Limited LLM Benchmark},
  year = {2024},
  journal = {arXiv:2406.19314}
}

@article{yan2026datedgpt,
  author = {Yan et al.},
  title = {DatedGPT: Preventing Lookahead Bias with Time-Aware Pretraining},
  year = {2026},
  journal = {arXiv:2603.11838}
}

@article{yang2023rephrased,
  author = {Yang et al.},
  title = {Rethinking Benchmark and Contamination with Rephrased Samples},
  year = {2023},
  journal = {arXiv:2311.04850}
}

@article{zhang2026allleaks,
  author = {Zhang and Chen and Stadie},
  title = {All Leaks Count, Some Count More: Interpretable Temporal Contamination Detection},
  year = {2026},
  journal = {arXiv:2602.17234}
}

@inproceedings{oren2024proving,
  author = {Oren et al.},
  title = {Proving Test Set Contamination in Black-Box Language Models},
  year = {2024},
  booktitle = {ICLR}
}

@inproceedings{jiang2024contamination,
  author = {Jiang et al.},
  title = {Data Contamination Can Cross Language Barriers},
  year = {2024},
  booktitle = {EMNLP}
}

@inproceedings{golchin2024task,
  author = {Golchin and Surdeanu},
  title = {Task Contamination: Language Models May Not Be Few-Shot Anymore},
  year = {2024},
  booktitle = {AAAI}
}

@inproceedings{deng2024tsguessing,
  author = {Deng et al.},
  title = {Investigating Data Contamination via TS-Guessing},
  year = {2024},
  booktitle = {NAACL}
}
```
