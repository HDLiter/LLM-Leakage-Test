# Task Design as Leakage Control: Identifying Look-Ahead Contamination Across Task Types in Chinese Financial News LLM Pipelines

## 1. Abstract
Large language models (LLMs) are increasingly inserted into financial NLP pipelines, yet evaluation is vulnerable to look-ahead contamination: models may encode future market-relevant facts from pretraining rather than infer from text. This risk is consequential in Chinese A-share settings, where recent vendor models can appear highly predictive on archived news while exploiting parametric memory. This proposal argues that leakage is not only a model property but also a task-design property. Using more than one million CLS telegraph articles from 2020 to 2026 and a 1,000-item benchmark, the study tests whether contamination declines monotonically as tasks move from direct return prediction to sentiment classification and then to decomposed, text-grounded indicators such as authority and novelty. Methodologically, the project combines white-box auditing on Qwen 2.5 7B with Min-K% probability, black-box counterfactual auditing on DeepSeek-chat, and item-level differential item functioning (DIF) analysis, embedded in a causal and econometric framework of look-ahead bias. The last stage tests whether contaminated LLM features survive XGBoost aggregation and inflate return predictability. The project will release the CLS-Leak benchmark, prompt templates, and a temporal decay dataset. Its central contribution is a design principle for financial LLM systems: task decomposition can function as leakage control, not merely prompt engineering.

## 2. Introduction and Motivation
Large language models are increasingly used to transform financial text into signals for prediction, ranking, and trading. Their attraction is obvious: they are flexible, inexpensive at inference time, and strong at extracting structure from unstructured news. Their evaluation problem is equally obvious but more serious. When an LLM is tested on historical financial news, it may already encode the same article, a close paraphrase, or the later market outcome in its parameters. Apparent performance may therefore reflect hidden future knowledge rather than text-grounded inference. In finance, this is not merely benchmark contamination. It is a form of false alpha.

Recent studies describe this failure as profit mirage, temporal contamination, or look-ahead bias, but the evidence is still concentrated in English-language, U.S.-market settings and outcome-proximal tasks such as QA, direct forecasting, and agentic trading. Chinese A-share news remains underexplored, and most existing studies use a single detector family at a time. That leaves two unresolved questions: whether leakage behaves similarly in Chinese financial text, and whether it is a stable phenomenon across access regimes rather than an artifact of one method.

This project addresses both questions by treating leakage as a function of task design. Direct prediction gives memorized outcomes the shortest route to the answer. Sentiment classification reduces, but does not remove, that route. Decomposed prompts for text-grounded indicators such as authority and novelty should weaken the memorization channel by forcing the model to attend to evidence instead of outcomes. The idea comes from the Thales quantamental engine, where LLMs produce intermediate features that are later aggregated by XGBoost. If those features are contaminated, the whole pipeline inherits look-ahead bias; if decomposition attenuates contamination, task design becomes a practical control mechanism. The proposal therefore asks not only whether leakage exists, but whether task decomposition offers a defensible way to limit it in Chinese financial news pipelines.

## 3. Literature Review

### 3.1 Financial Leakage and Look-Ahead Bias
Li et al. (2025) show in *Profit Mirage* that financial LLM agents can look strong in backtests yet collapse after the training cutoff, establishing contamination as an economically material problem. Zhang, Chen, and Stadie (2026) add an important refinement: not all leakage matters equally, and decision-critical contamination should be separated from peripheral contamination. Gao, Jiang, and Yan (2026) explicitly recast the problem as look-ahead bias in forecasting, while Benhenda (2026) and Yan et al. (2026) move toward standardized finance-specific benchmarks and temporally bounded baselines. The main limitation of this literature is its scope: it is largely U.S.-centric, English-only, focused on direct decision tasks, and usually organized around binary pre/post-cutoff comparisons rather than continuous temporal decay.

### 3.2 Detection Methods Hierarchy
The detection literature is best understood by access level. Shi et al. (2024) provide the white-box anchor with Min-K% probability, while Zhang et al. (2025) show that calibrated variants can improve its reliability. Dong et al. (2024) demonstrate that grey-box or black-box signals can also reveal contamination through output behavior, and Ravaut et al. (2025) systematize these methods in LLMSanitize. At the same time, Duan et al. (2024) show that many membership-inference attacks are weak on realistic long-text settings, and Yang et al. (2023) show that paraphrases can evade naive decontamination. The implication is clear: no single detector is sufficient. This motivates a cross-access design combining Qwen-based Min-K% auditing with DeepSeek counterfactual auditing on the same benchmark.

### 3.3 Task Decomposition in Finance
Work on financial task design suggests that decomposition matters, but not yet as leakage control. Bastianello et al. (2024), Li et al. (2025), Cao et al. (2024), and Liang et al. (2025) all show that staged or structured extraction can improve interpretability and predictive usefulness. Iacovides et al. (2025) add a cautionary result: standard fine-tuning can intensify memorization in financial sentiment tasks. Together, these studies imply that prompt and task structure shape what information the model expresses, but none directly tests whether decomposed, text-grounded indicators reduce contamination relative to direct prediction.

### 3.4 Cross-Disciplinary Tools
Cross-disciplinary tools strengthen the design. Jin et al. (2025) distinguish memory from reasoning in LLM evaluation; Arjovsky et al. (2019) and Geirhos et al. (2020) explain why models prefer shortcut solutions; Lalor et al. (2016), Vania et al. (2021), and Swaminathan and Rogers (1990) provide item-level tools for separating general difficulty from group-specific distortion. These literatures suggest a useful synthesis for the present project: a causal DAG for conceptual clarity, econometric testing for look-ahead bias, and DIF analysis for article-level heterogeneity. That combination is absent from the existing Chinese financial leakage literature.

## 4. Research Questions and Hypotheses
This study addresses three research questions aligned with the final project plan.

**RQ1. Does leakage decrease monotonically from direct prediction to sentiment classification to decomposed text-grounded indicators on Chinese A-share news?**  
**H1.** For the same articles, contamination scores will follow the ordered pattern `direct > sentiment > decomposed` under both white-box Min-K% and black-box counterfactual metrics. The reduction will not be replicated by a sham-decomposition prompt that preserves structured output but removes economically grounded sub-indicators.

**RQ2. Do white-box and black-box methods produce convergent item-level leakage rankings?**  
**H2.** Item-level leakage scores derived from Qwen Min-K% and DeepSeek counterfactual sensitivity will exhibit a positive Spearman rank correlation, and the clustered bootstrap confidence interval for that correlation will exclude zero overall and within major temporal bins.

**RQ3. Does contamination in LLM-derived features survive XGBoost aggregation and inflate historical short-horizon return predictability?**  
**H3.** LLM feature sets with higher measured contamination will generate stronger in-sample or historical short-horizon predictability than contamination-residualized features, but that incremental performance will attenuate on the freshest holdout period. A positive contamination interaction in return regressions will indicate that part of the measured signal is explained by leakage rather than genuine predictive content.

These hypotheses are falsifiable. A null result is informative in every case: no monotonic ordering would reject the task-design thesis; no cross-method convergence would imply detector-specific artifacts; and no propagation through XGBoost would limit the practical importance of contamination for quant pipelines.

## 5. Theoretical Framework
The project adopts a three-layer hybrid framework: a causal model of leakage, an econometric identification strategy, and item-level DIF analysis.

### 5.1 Conceptual Layer: Causal DAG
The conceptual distinction is between a memorization path and a reasoning path. Let `M` denote memorization activation, `R` text-grounded reasoning, `T` task type, and `Y` the model output. Recency, prominence, and event type affect training familiarity `K`; cue masking and semantic edits intervene on the two paths differently.

```text
C (recency, prominence, event type) --> K (training familiarity) --> M (memorization) --> Y
X (article text) -------------------------------------------------> R (reasoning) -----^
Z (cue masking intervention) ------------------------------------> M
A (semantic counterfactual intervention) ------------------------> R
T (task type: direct / sentiment / decomposed) -----------------> M
T (task type: direct / sentiment / decomposed) -----------------> R
```

Task type is the moderator. Direct prediction gives memorization the shortest path to the answer; sentiment weakens that path; decomposed indicators should weaken it further by demanding text-grounded judgments. The sham-decomposition control tests whether any reduction comes from meaningful factorization rather than mere structure.

### 5.2 Operational Layer: Econometric Identification
Operationally, contamination is treated as look-ahead bias. The study does not observe `M` directly; it uses Min-K% and counterfactual scores as proxies. Two econometric ideas are central: temporal decay and contamination interaction. If leakage comes from latent future knowledge, it should vary with temporal distance from the model's effective knowledge frontier. If it survives downstream modeling, it should also amplify apparent predictive power in return regressions. Let `S_i` be an LLM-derived feature, `C_i` a contamination proxy, and `r_{i,h}` the `h`-day abnormal return:

```text
r_{i,h} = alpha + beta*S_i + theta*(S_i x C_i) + X_i'gamma + tau_t + eta_g + epsilon_i
```

where `X_i` contains article controls, `tau_t` time effects, and `eta_g` group effects. A positive `theta` implies that predictive power rises with contamination, consistent with false alpha.

### 5.3 Item-Level Layer: DIF Analysis
Aggregate averages can hide strong item heterogeneity. DIF addresses that issue by asking whether particular articles become unusually "easy" under contaminated conditions after controlling for baseline difficulty. In this design, articles are items, model-task-condition combinations are respondents, and the grouping variable distinguishes more contaminated from cleaner regimes. DIF therefore identifies which article types, such as prominent firms or highly propagated events, carry disproportionate leakage risk.

## 6. Methodology

### 6.1 Data and Benchmark Construction
The primary corpus contains more than one million CLS telegraph entries from January 2020 to February 2026. From this pool, the project will construct a curated 1,000-case event-level benchmark, **CLS-Leak**, rather than treating raw near-duplicate news items as independent observations. Sampling will be stratified by six temporal bins, company prominence, and event type so that the benchmark can support both temporal decay analysis and heterogeneity tests.

Each event will include the original article, a neutral paraphrase control, and targeted counterfactual variants. For direct prediction and sentiment tasks, edits will reverse or materially alter decision-relevant semantics. For decomposed tasks, edits will target authority and novelty through provenance swaps and first-disclosure versus routine-follow-up manipulations. A 200-item audited anchor subset will validate decomposition labels and retrieval-based novelty proxies. Benchmark outputs will include texts, event identifiers, prompts, variants, and contamination scores. Market data are added only in the final stage for short-horizon abnormal-return validation.

### 6.2 Models and Access Regimes
The study uses two complementary access regimes. DeepSeek-chat is the deployment-relevant black-box model and is used for counterfactual auditing and the downstream economic pipeline. Qwen 2.5 7B, served through vLLM, provides token log-probabilities for white-box Min-K% auditing. Prompts will be frozen before the main run, temperature fixed at zero where possible, and inference metadata archived to limit reproducibility drift.

### 6.3 Detection Methods
The project combines two primary detection families. Qwen supplies white-box Min-K% scores, normalized for task and length effects. DeepSeek supplies black-box counterfactual metrics such as prediction consistency and item-level response change under semantic edits. DIF is then used as an explanatory layer rather than a standalone detector, asking which items become disproportionately easy under contaminated conditions for direct prediction, sentiment, and decomposed indicators.

### 6.4 Experimental Design
The experiments are intentionally ordered to support the paper's narrative while preserving an MVP cutline.

#### E1. Temporal leakage decay curve
E1 estimates how contamination changes across six temporal bins using both Qwen Min-K% and DeepSeek counterfactual scores. The goal is a temporal decay curve, not a binary pre/post comparison, with secondary splits by prominence and event type.

#### E2. White-box / black-box cross-validation
E2 tests whether the two access regimes agree on which items are leaky. For each article, white-box and black-box scores will be standardized within task and compared by Spearman rank correlation with clustered bootstrap confidence intervals.

#### E3. Leakage spectrum across task types
E3 is the core experiment. The same articles will be run under direct prediction, sentiment classification, and decomposed extraction of authority and novelty. Because article content is fixed, task type becomes the main experimental variable, and the primary estimand is the ordered contrast `direct > sentiment > decomposed`.

#### E11. Sham-decomposition control
E11 is the falsification check for E3. It preserves multi-field structure and token budget but replaces meaningful sub-indicators with arbitrary ones. If sham decomposition reduces leakage as much as meaningful decomposition, the main task-design claim weakens substantially.

#### E5. DIF analysis under contaminated and clean conditions
E5 applies DIF-style logistic models to compare older, more contaminated items with cleaner regimes after conditioning on baseline difficulty. It identifies which article types drive contamination most strongly.

#### E8 plus E10. Contamination propagation through XGBoost and economic validation
The final experiment links contamination to quant practice. Features from the three task types will feed an XGBoost model for short-horizon return prediction. Raw, contamination-residualized, and contamination-only feature sets will be compared using rank IC, hit rate, and abnormal-return spreads to test whether measured leakage survives downstream aggregation.

### 6.5 Statistical Inference Protocol
All inference will respect event-level dependence. Confidence intervals will use clustered bootstrap resampling; within-article contrasts will use paired permutation or randomization tests where appropriate; and regressions will include temporal controls and grouped errors. E1 and E3 focus on monotonic ordered contrasts, E2 on Spearman `rho`, E5 on uniform and non-uniform DIF, and E8/E10 on rolling-origin predictive comparisons with multiple-testing control. Throughout, effect sizes and confidence intervals take precedence over isolated `p`-values.

## 7. Expected Contributions
This project contributes substantively, methodologically, and conceptually. Substantively, it provides a first systematic leakage study for Chinese A-share news with benchmark and market-level validation. Methodologically, it cross-validates white-box and black-box auditing on the same corpus and adds item-level DIF analysis. Conceptually, it tests a practical design principle: LLMs should be more trustworthy when asked for text-grounded intermediate constructs than for outcome-proximal judgments.

## 8. Timeline and Feasibility
The project is scoped for ten weeks and is feasible under the stated compute and data constraints.

**Weeks 1-2:** finalize prompt schemas, event clustering, temporal bin definitions, and the 200-item audit subset.  
**Weeks 3-4:** construct the 1,000-case benchmark, generate neutral and targeted counterfactuals, and complete quality control.  
**Weeks 5-6:** run DeepSeek black-box experiments and Qwen white-box scoring; estimate E1 and E2.  
**Week 7:** complete E3 and E11, including sham-decomposition analysis.  
**Week 8:** run E5 DIF models and heterogeneity analysis.  
**Week 9:** run E8 plus E10 with XGBoost, rank IC, and abnormal return validation.  
**Week 10:** finalize robustness checks, figures, artifact packaging, and manuscript submission materials.

Feasibility rests on an already available in-domain corpus, completed pilot notebooks, and a fixed model stack. Qwen scoring is manageable locally or on a rented 4090, and DeepSeek API costs remain moderate at the proposed scale. The design fits JFDS as a primary venue and can support an EMNLP Findings submission if the benchmark and cross-method results are strong.

## 9. Risk Analysis and Contingency Plans
The main scientific risk is that decomposed indicators may not produce the predicted monotonic reduction in leakage. If that occurs, the project will pivot from a universal spectrum claim to a conditional one based on indicator type, prominence, or event class, with E11 distinguishing meaningful decomposition from mere output structuring.

A second risk is disagreement between Min-K% and counterfactual auditing. That outcome remains publishable because it would clarify which aspects of contamination each access regime captures. A third risk is weak validation for decomposed indicators, especially novelty; the contingency is to keep the decomposed core restricted to authority and novelty and rely on the audited anchor subset plus metadata and retrieval proxies.

The final practical risk is scope. If economic validation proves noisy, the MVP remains E1, E2, E3, and E11, with multi-horizon tests cut first and XGBoost simplified before any reduction of the core contamination experiments. API drift will be managed through prompt freezing, a tight execution window, and full inference logging.

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
```
