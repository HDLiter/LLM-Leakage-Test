# Literature Search: Scenario 1

Search date: 2026-04-05

## Scenario 1

Orthogonal low-leakage micro-factors -> ML ensemble -> prediction.

Working interpretation for this search:

- Prefer papers where many weak, diverse, or carefully isolated intermediate features are combined to outperform a single strong but brittle predictor.
- Include decomposition -> aggregation papers even when the "micro-factors" are scales, spans, alignments, concepts, or clinician-interpretable evidence units rather than hand-built tabular features.
- Include anti-leakage papers when they explicitly motivate designing features and splits so the model cannot win through contamination.

## Quick takeaways

The strongest direct matches are in four clusters:

1. Ensemble/diversity theory showing that complementary weak predictors can beat a single stronger but less diverse predictor.
2. Signal decomposition papers in forecasting, where a hard problem is broken into weak multi-scale components and reassembled by an ensemble.
3. Clinical/radiomics papers, where many small interpretable factors beat coarse biomarkers, plus leakage papers that explain why "clean" factors matter.
4. Recent clinical NLP papers where LLMs extract structured concepts/evidence first, and a simpler downstream model aggregates those outputs for prediction.

The most S1-like papers overall are:

- Krogh and Vedelsby 1995
- Hong and Page 2004
- Benaouda et al. 2006
- Yu, Wang, and Lai 2008
- Lambin et al. 2012
- Aerts et al. 2014
- CHiLL (McInerney et al. 2023)
- McInerney et al. 2024
- Woo et al. 2025
- Davis et al. 2023 and REFORMS 2024 for the anti-leakage design logic

## A. Ensemble, Diversity, and Wisdom-of-Crowds Theory

### Neural Network Ensembles, Cross Validation, and Active Learning

Authors: Anders Krogh, Jesper Vedelsby  
Year: 1995  
Venue: Advances in Neural Information Processing Systems (NeurIPS 7)  
URL: https://proceedings.neurips.cc/paper/1994/file/b8c37e33defde51cf91e1e03e51657da-Paper.pdf

Summary: This paper gives one of the cleanest formal arguments for ensembles: ensemble error can be decomposed into average member error minus an ambiguity/diversity term. In other words, weak members are useful when they err differently, not just when they are individually strong.

Relation to S1: This is the mathematical backbone for the "many weak but orthogonal micro-factors" idea. S1 is essentially a feature-level version of their ambiguity decomposition.

### Ensemble Methods in Machine Learning

Authors: Thomas G. Dietterich  
Year: 2000  
Venue: Multiple Classifier Systems  
URL: https://link.springer.com/chapter/10.1007/3-540-45014-9_1

Summary: Dietterich surveys why ensembles improve prediction, emphasizing variance reduction, escaping local optima, and correcting for representational mismatch. A recurring theme is that diverse imperfect learners can be more reliable than a single best-looking model.

Relation to S1: This is a good general reference for why aggregating many weak pieces of evidence can outperform a single direct predictor, especially when the direct predictor is noisy or unstable.

### Measures of Diversity in Classifier Ensembles and Their Relationship with the Ensemble Accuracy

Authors: Ludmila I. Kuncheva, Christopher J. Whitaker  
Year: 2003  
Venue: Machine Learning  
URL: https://doi.org/10.1023/A:1022859003006

Summary: The paper studies multiple formal diversity measures and tests how well they track ensemble accuracy. It shows that diversity is not a vague intuition only; it is measurable and materially tied to when an ensemble actually improves.

Relation to S1: Useful for arguing that orthogonality among micro-factors is not cosmetic. If your intermediate features are correlated replicas of one contaminated signal, the expected S1 gain should shrink.

### Diversity Creation Methods: A Survey and Categorisation

Authors: Gavin Brown, Jeremy Wyatt, Rachel Harris, Xin Yao  
Year: 2005  
Venue: Information Fusion  
URL: https://doi.org/10.1016/S1566-2535(04)00037-5

Summary: This survey organizes methods for deliberately creating diversity in ensembles through data resampling, output manipulation, feature subspacing, and hybridization. The paper treats diversity as something to engineer, not just observe.

Relation to S1: This is directly relevant if S1 is framed as a deliberate orthogonalization strategy. It supports building many deliberately differentiated low-leakage factors rather than hoping useful diversity appears automatically.

### Groups of Diverse Problem Solvers Can Outperform Groups of High-Ability Problem Solvers

Authors: Lu Hong, Scott E. Page  
Year: 2004  
Venue: Proceedings of the National Academy of Sciences  
URL: https://doi.org/10.1073/pnas.0403723101

Summary: Hong and Page show theoretically that under broad conditions, diversity in heuristics can beat homogeneous high ability on hard search problems. The point is not that every weak solver wins individually, but that heterogeneous partial views cover more of the problem space.

Relation to S1: This is the closest non-ML conceptual analogue to your hypothesis. Many weak but distinct sub-judgments can outperform one strong, monolithic judgment because coverage beats raw strength when the task is complex.

### A Solution to the Single-Question Crowd Wisdom Problem

Authors: Drazen Prelec, H. Sebastian Seung, John McCoy  
Year: 2017  
Venue: Nature  
URL: https://doi.org/10.1038/nature21054

Summary: The paper shows how to recover better aggregate answers from a crowd even when there is only one question, using information contained in how common an answer is expected to be. It is a robustness paper about extracting signal from multiple weak viewpoints rather than trusting the plurality answer naively.

Relation to S1: This supports the broader "wisdom of many partial signals" motivation. It is especially relevant if you want to argue that diverse weak sub-judgments can be aggregated more intelligently than simple voting.

### The Wisdom of Model Crowds

Authors: Lisheng He, Pantelis P. Analytis, Sudeep Bhatia  
Year: 2022  
Venue: Management Science  
URL: https://doi.org/10.1287/mnsc.2021.4090

Summary: The authors compare 58 models of risky choice across 19 datasets and find that crowds of models outperform individual models. Their conclusion is that competing models are often complementary experts rather than substitutes.

Relation to S1: This is an unusually direct analogue outside standard ML benchmarking. It supports the claim that multiple partial theories or feature families can beat the best single direct model because each captures a different slice of the signal.

## B. Signal Decomposition and Forecast Aggregation

### Wavelet-Based Nonlinear Multiscale Decomposition Model for Electricity Load Forecasting

Authors: D. Benaouda, F. Murtagh, J.-L. Starck, O. Renaud  
Year: 2006  
Venue: Neurocomputing  
URL: https://doi.org/10.1016/j.neucom.2006.04.005

Summary: This paper decomposes load signals into multiple scales using wavelets, models the components separately, and then recombines them for final forecasting. The decomposition reduces complexity and improves accuracy relative to modeling the raw signal directly.

Relation to S1: This is a classic decomposition -> ML aggregation template. The "micro-factors" are scale-specific components, each weak alone but useful in combination.

### Forecasting Crude Oil Price with an EMD-Based Neural Network Ensemble Learning Paradigm

Authors: Lean Yu, Shouyang Wang, Kin Keung Lai  
Year: 2008  
Venue: Energy Economics  
URL: https://doi.org/10.1016/j.eneco.2008.05.003

Summary: The paper uses empirical mode decomposition to split a nonstationary crude-oil series into intrinsic mode functions, predicts each component with neural models, and re-aggregates them. The hybrid decomposition-ensemble setup beats more direct forecasting baselines.

Relation to S1: This is one of the cleanest forecasting examples of "break a contaminated/complex signal into cleaner weak parts, then let the learner reassemble them." It is a strong cross-domain precedent for S1.

### Hybrid Model with Secondary Decomposition, Randomforest Algorithm, Clustering Analysis and Long Short Memory Network Principal Computing for Short-Term Wind Power Forecasting on Multiple Scales

Authors: Zexian Sun, Mingyu Zhao, Yan Dong, Xin Cao, Hexu Sun  
Year: 2021  
Venue: Energy  
URL: https://doi.org/10.1016/j.energy.2021.119848

Summary: This paper stacks several decomposition and aggregation steps: secondary decomposition, clustering, random forests, and LSTMs across multiple scales. The authors show that structured multiscale modeling outperforms more direct forecasting pipelines on volatile wind-power data.

Relation to S1: The exact machinery differs from your use case, but the design logic matches closely: isolate weak structured components first, then let a downstream learner discover the predictive combination.

## C. Clinical and Biomedical Prediction with Clean or Decomposed Factors

### Radiomics: Extracting More Information from Medical Images Using Advanced Feature Analysis

Authors: Philippe Lambin, Emmanuel Rios-Velazquez, Ralph Leijenaar, Sara Carvalho, Ruud G. P. M. van Stiphout, Patrick Granton, Catharina M. L. Zegers, Robert Gillies, Ronald Boellard, Andre Dekker  
Year: 2012  
Venue: European Journal of Cancer  
URL: https://doi.org/10.1016/j.ejca.2011.11.036

Summary: Lambin et al. argue that medical images contain many quantitative descriptors of intensity, shape, and texture that are invisible to coarse human summaries. Their radiomics program explicitly replaces a small set of gross biomarkers with many machine-readable phenotype descriptors.

Relation to S1: Radiomics is almost a textbook S1 pattern. It decomposes a single rich but hard-to-use object into many weak/interpretable features and relies on downstream modeling to recover predictive value.

### Decoding Tumour Phenotype by Noninvasive Imaging Using a Quantitative Radiomics Approach

Authors: Hugo J. W. L. Aerts, Emmanuel Rios Velazquez, Ralph T. H. Leijenaar, Chintan Parmar, Patrick Grossmann, Sara Carvalho, Johan Bussink, Rene Monshouwer, Benjamin Haibe-Kains, Derek Rietveld, et al.  
Year: 2014  
Venue: Nature Communications  
URL: https://doi.org/10.1038/ncomms5006

Summary: Aerts et al. show that a large radiomics feature set from CT images captures prognostic and molecular information better than simple image summaries such as tumor size. The core contribution is that phenotype emerges from aggregating many quantitative image micro-descriptors.

Relation to S1: This is one of the best biomedical examples of decomposed feature extraction beating direct coarse prediction. It is especially useful when motivating why many weak but relatively "clean" descriptors can beat one strong-looking global variable.

### Conditional Mutual Information-Based Feature Selection for Congestive Heart Failure Recognition Using Heart Rate Variability

Authors: Yu S. N., Lee M. Y.  
Year: 2012  
Venue: Computer Methods and Programs in Biomedicine  
URL: https://doi.org/10.1016/j.cmpb.2011.12.015

Summary: The paper extracts 50 heart-rate-variability features, then uses conditional mutual information to pick a compact subset for an SVM classifier. The selected multi-feature system outperforms alternative selectors and simple single-measure baselines.

Relation to S1: This is a tight micro-factor example from physiological signal modeling. Many weak HRV descriptors, once selected and combined, beat relying on a single summary metric.

### Developing EHR-Driven Heart Failure Risk Prediction Models Using CPXR(Log) with the Probabilistic Loss Function

Authors: Vahid Taslimitehrani, Guozhu Dong, Nilay D. Pereira, et al.  
Year: 2016  
Venue: Journal of Biomedical Informatics  
URL: https://doi.org/10.1016/j.jbi.2016.01.009

Summary: This paper builds heart-failure prognostic models from EHR data using contrast-pattern-aided logistic regression, where subgroup-specific local patterns augment a global model. It reports strong performance gains over prior prognostic models and emphasizes heterogeneity rather than one-size-fits-all scoring.

Relation to S1: This is a useful precedent for letting many local patterns or subgroup-specific weak signals jointly outperform a single global predictor. It is especially relevant if your S1 aggregation model is meant to exploit interaction structure among weak factors.

## D. Anti-Contamination and Leakage-Aware Feature Engineering

### A Framework for Understanding Label Leakage in Machine Learning for Health Care

Authors: Sharon E. Davis, Michael E. Matheny, Suresh Balu, Mark P. Sendak  
Year: 2023  
Venue: Journal of the American Medical Informatics Association  
URL: https://doi.org/10.1093/jamia/ocad178

Summary: Davis et al. provide a concrete taxonomy of label leakage in healthcare, including post-outcome artifacts, treatment proxies, and hidden temporal violations. The paper is valuable because it turns leakage from a vague warning into a feature-design problem.

Relation to S1: This is one of the best references for the "low-leakage" half of your scenario. It supports deliberately engineering intermediate features that are temporally and causally legitimate rather than strong only because they leak the answer.

### Effect of Data Leakage in Brain MRI Classification Using 2D Convolutional Neural Networks

Authors: Ekin Yagis, Selamawet Workalemahu Atnafu, Alba Garcia Seco de Herrera, Chiara Marzi, Riccardo Scheda, Marco Giannelli, Carlo Tessa, Luca Citi, Stefano Diciotti  
Year: 2021  
Venue: Scientific Reports  
URL: https://doi.org/10.1038/s41598-021-01681-w

Summary: The paper demonstrates how slice-level rather than patient-level splitting causes severe leakage in brain MRI classification, dramatically inflating reported performance. It is a clean empirical warning that a "strong" predictor may simply be exploiting contamination.

Relation to S1: This is useful as a contrast case. S1 explicitly prefers many weaker but valid predictors over one apparently strong signal that is secretly contaminated by split leakage.

### Leakage and the Reproducibility Crisis in Machine-Learning-Based Science

Authors: Sayash Kapoor, Arvind Narayanan  
Year: 2023  
Venue: Patterns  
URL: https://doi.org/10.1016/j.patter.2023.100804

Summary: Kapoor and Narayanan argue that leakage is a major reason many scientific ML claims fail to reproduce, and they catalog recurring leakage patterns across domains. Their core message is that predictive power is often illusory when features are unavailable or illegitimate at deployment time.

Relation to S1: This is a strong general-purpose citation for why S1 should privilege feature legitimacy and deployment-faithful intermediate variables over headline accuracy from contaminated predictors.

### REFORMS: Consensus-Based Recommendations for Machine-Learning-Based Science

Authors: Sayash Kapoor, Emily M. Cantrell, Kenny Peng, Thanh Hien Pham, Christopher A. Bail, Odd Erik Gundersen, Jake M. Hofman, Jessica Hullman, Michael A. Lones, Momin M. Malik, et al.  
Year: 2024  
Venue: Science Advances  
URL: https://doi.org/10.1126/sciadv.adk3452

Summary: REFORMS gives consensus recommendations for more reliable ML science, including leakage checks, appropriate unit-of-analysis splits, and deployment-consistent feature construction. It is more methodological than task-specific, but highly actionable.

Relation to S1: This is a practical design guide for building the "clean factor" side of S1. It supports feature extraction pipelines that are intentionally conservative about what information is allowed into intermediate variables.

## E. LLM-Extracted Intermediate Features for Downstream Prediction

### Zero-Shot Interpretable Phenotyping of Postpartum Hemorrhage Using Large Language Models

Authors: Emily Alsentzer, Matthew J. Rasmussen, Romy Fontoura, Alexis L. Cull, Brett K. Beaulieu-Jones, Kathryn J. Gray, David W. Bates, Vesela P. Kovacheva  
Year: 2023  
Venue: npj Digital Medicine  
URL: https://www.nature.com/articles/s41746-023-00957-x

Summary: The paper uses Flan-T5 to extract 24 granular concepts related to postpartum hemorrhage from discharge notes without task-specific fine-tuning. These concept-level outputs support an interpretable phenotype, identify substantially more cases than claims-code baselines, and enable subtype analysis.

Relation to S1: This is a strong LLM-side precedent for S1. The LLM does not directly make one opaque final prediction; it produces many smaller clinically meaningful sub-judgments that can be recombined downstream.

### CHiLL: Zero-Shot Custom Interpretable Feature Extraction from Clinical Notes with Large Language Models

Authors: Denis McInerney, Geoffrey Young, Jan-Willem van de Meent, Byron C. Wallace  
Year: 2023  
Venue: Findings of EMNLP 2023  
URL: https://doi.org/10.18653/v1/2023.findings-emnlp.568

Summary: CHiLL prompts an LLM with expert-written queries to infer high-level interpretable features from EHR text, then trains a simple linear classifier on those inferred features. The resulting models are comparably performant to models using reference features, while remaining substantially more interpretable than bag-of-words or dense neural representations.

Relation to S1: This is one of the clearest direct matches to your scenario. It is almost exactly "LLM-extracted weak/interpretable micro-factors -> downstream ML aggregation -> prediction."

### Towards Reducing Diagnostic Errors with Interpretable Risk Prediction

Authors: Denis Jered McInerney, William Dickinson, Lucy C. Flynn, Andrea C. Young, Geoffrey S. Young, Jan-Willem van de Meent, Byron C. Wallace  
Year: 2024  
Venue: NAACL 2024  
URL: https://doi.org/10.18653/v1/2024.naacl-long.399

Summary: This paper uses an LLM to retrieve diagnosis-relevant evidence snippets from longitudinal EHR notes and then feeds those snippets into a ClinicalBERT-based Neural Additive Model for diagnosis risk prediction. The model aggregates per-evidence contributions rather than relying on a single end-to-end black-box note classifier.

Relation to S1: This is a very strong direct analogue. It explicitly decomposes the prediction problem into many LLM-generated evidence units and lets a simpler downstream model learn how to combine them.

### Predicting Postpartum Hemorrhage Using Clinical Features Extracted With Large Language Models

Authors: Elizabeth G. Woo, Israel Zighelboim, Tyler Gifford, Joseph G. Bell, Hannah Milthorpe, Emily Alsentzer, Ryan E. Longman, Jorge E. Tolosa, Brett K. Beaulieu-Jones  
Year: 2025  
Venue: O&G Open  
URL: https://doi.org/10.1097/OG9.0000000000000128

Summary: Woo et al. compare three pipelines on a temporally held-out test set: structured-data-only ML, direct LLM prediction from notes, and interpretable models that combine structured data with LLM-extracted features. Direct LLM prediction scores best, but the LLM-extract pipeline comes close while surfacing 47 clinically meaningful predictors and substantially beating structured-data-only baselines.

Relation to S1: This is highly relevant because it explicitly compares direct prediction against a decomposed-feature pipeline. It shows the tradeoff space S1 cares about: slightly lower raw accuracy than end-to-end LLM prediction, but much better interpretability and cleaner feature-level control.

## F. Structured Prediction and Intermediate Structure in NLP

### Discriminative Learning over Constrained Latent Representations

Authors: Ming-Wei Chang, Dan Goldwasser, Dan Roth, Vivek Srikumar  
Year: 2010  
Venue: NAACL-HLT 2010  
URL: https://aclanthology.org/N10-1066/

Summary: This paper studies NLP tasks where success depends on recovering a latent intermediate structure first, such as alignments for paraphrase identification or textual entailment. Instead of fixing that structure heuristically and then training the final classifier, the authors jointly learn the representation and the end task, improving transliteration, paraphrase identification, and textual entailment.

Relation to S1: This is a strong classical reference for "feature decomposition -> ML aggregation beats direct prediction." It argues that the intermediate representation should be optimized for final predictive value, not chosen independently.

### Backpropagating through Structured Argmax using a SPIGOT

Authors: Hao Peng, Sam Thomson, Noah A. Smith  
Year: 2018  
Venue: ACL 2018  
URL: https://doi.org/10.18653/v1/P18-1173

Summary: SPIGOT makes it possible to include hard structured predictions, such as parses, as intermediate layers in neural pipelines and still train end to end. The paper shows downstream gains over modular pipelines and soft-attention alternatives on syntactic-then-semantic dependency parsing and semantic-parsing-assisted sentiment classification.

Relation to S1: This is important because it shows that explicit intermediate structure can help downstream prediction more than going direct. It is the NLP version of "decompose first, aggregate later."

### Syntactic Scaffolds for Semantic Structures

Authors: Swabha Swayamdipta, Sam Thomson, Kenton Lee, Luke Zettlemoyer, Chris Dyer, Noah A. Smith  
Year: 2018  
Venue: EMNLP 2018  
URL: https://doi.org/10.18653/v1/D18-1412

Summary: The paper uses syntax as an auxiliary scaffold during training to improve semantic role labeling, frame semantics, and coreference resolution, but discards the scaffold at test time. The key finding is that intermediate syntactic structure gives the semantic model a better inductive bias than direct training alone.

Relation to S1: This is slightly more indirect than CHiLL or McInerney 2024, but still relevant. It supports the claim that a decomposed intermediate layer can improve downstream robustness and generalization even when the final task is what matters.

## Most useful citations for writing the S1 argument

If you only need a short core stack for the paper/proposal, I would cite:

1. Krogh and Vedelsby 1995 for the ensemble/diversity principle.
2. Hong and Page 2004 for the broader diversity-beats-strength intuition.
3. Benaouda et al. 2006 or Yu et al. 2008 for decomposition -> aggregation in forecasting.
4. Lambin et al. 2012 and Aerts et al. 2014 for decomposed biomedical micro-features.
5. Davis et al. 2023 plus REFORMS 2024 for why "clean" low-leakage features matter.
6. CHiLL 2023, McInerney et al. 2024, and Woo et al. 2025 for the most direct LLM-era precedents.
