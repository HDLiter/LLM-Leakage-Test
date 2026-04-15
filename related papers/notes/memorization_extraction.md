# Memorization & Training Data Extraction

## A Closer Look at Memorization in Deep Networks
**Authors & Year:** Arpit et al. (2017)

**Summary:** We examine the role of memorization in deep learning, drawing connections to capacity, generalization, and adversarial robustness. While deep networks are capable of memorizing noise data, our results suggest that they tend to prioritize learning simple patterns ﬁrst. In our experiments, we expose qualitative differences in gradient-based optimization of deep neural networks (DNNs) on noise vs. real data.

**Key methods/findings**
- We also demonstrate that for appropriately tuned explicit regularization (e.g., dropout) we can degrade DNN training performance on noise datasets without compromising generalization on real data.
- Our analysis suggests that the notions of effective capacity which are dataset independent are unlikely to explain the generalization performance of deep networks when trained with gradient based methods because training data itself plays an important role in determining the degree of memorization.
- We examine the role of memorization in deep learning, drawing connections to capacity, generalization, and adversarial robustness.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.

---

## R1 Additions

- **Measuring memorization in language models via probabilistic extraction:** Formalizes extraction as a probabilistic memorization measurement problem; this matters because the R1 NLP review cites it as the strongest extraction-style comparator if FinMem-Bench claims extraction compatibility.
- **OWL:** Probes cross-lingual recall of memorized texts; this matters because the R1 NLP review uses it to argue that cross-lingual memorization is no longer an open niche by itself.
- **Pretraining Data Detection for Large Language Models: A Divergence-based Calibration Method:** Calibrates pretraining-data detection beyond raw Min-K% scores; this matters because the R1 NLP review cites PatentMIA-style divergence calibration as realistic partial support for FinMem-Bench.
- **MemGuard-Alpha (Roy & Roy, 2026):** Combines MIA-style scores with temporal features (MemGuard Composite Score) and Cross-Model Memorization Disagreement across LLMs with different training cutoffs to flag memorization-contaminated trading signals; reports 7x return gap between clean and tainted signals and 49% Sharpe uplift. Directly relevant to FinMem-Bench because it operationalizes "memorization hurts downstream alpha" on the same CLS-style Chinese-news setting we target, and the cross-cutoff disagreement trick is a cheap black-box anchor we can reuse alongside CFLS and evidence intrusion.

---

## Counterfactual Memorization in Neural Language Models
**Authors & Year:** Zhang et al. (2021)

**Summary:** Modern neural language models that are widely used in various NLP tasks risk memorizing sensitive information from their training data. Understanding this memorization is important in real world applications and also from a learningtheoretical perspective. An open question in previous studies of language model memorization is how to filter out “common” memorization.

**Key methods/findings**
- We formulate a notion of counterfactual memorization which characterizes how a model’s predictions change if a particular document is omitted during training.
- We identify and study counterfactually-memorized training examples in standard text datasets.
- We estimate the influence of each memorized training example on the validation set and on generated texts, showing how this can provide direct evidence of the source of memorization at test time.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence. It especially supports our counterfactual testing design.

---

## Detecting Pretraining Data from LLMs (Min-K% Prob)
**Authors & Year:** Shi et al. (2024)

**Summary:** Although large language models (LLMs) are widely deployed, the data used to train them is rarely disclosed. Given the incredible scale of this data, up to trillions of tokens, it is all but certain that it includes potentially problematic text such as copyrighted materials, personally identifiable information, and test data for widely reported reference benchmarks. However, we currently have no way to know which data of these types is included or in what proportions.

**Key methods/findings**
- To facilitate this study, we introduce a dynamic benchmark WIKIMIA that uses data created before and after model training to support gold truth detection.
- Moreover, our experiments demonstrate that MIN-K% P ROB achieves a 7.4% improvement on WIKIMIA over these previous methods.
- In this paper, we study the pretraining data detection problem: given a piece of text and black-box access to an LLM without knowing the pretraining data, can we determine if the model was trained on the provided text?

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.

---

## Do Membership Inference Attacks Work on Large Language Models? Michael Duan*1Anshuman Suri*2
**Authors & Year:** Models Michael et al. (2024)

**Summary:** Membership inference attacks (MIAs) attempt to predict whether a particular datapoint is a member of a target model’s training data. Despite extensive research on traditional machine learning models, there has been limited work studying MIA on the pre-training data of large language models (LLMs). We perform a large-scale evaluation of MIAs over a suite of language models (LMs) trained on the Pile, ranging from 160M to 12B parameters.

**Key methods/findings**
- Further analyses reveal that this poor performance can be attributed to (1) the combination of a large dataset and few training iterations, and (2) an inherently fuzzy boundary between members and non-members.
- We find that MIAs barely outperform random guessing for most settings across varying LLM sizes and domains.
- We release our code and data as a unified benchmark package that includes all existing MIAs, supporting future work.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.

---

## Entity-level Memorization in LLMs
**Authors & Year:** Zhou et al. (2023)

**Summary:** Large language models (LLMs) have been proven capable of memorizing their training data, which can be extracted through specifically designed prompts. As the scale of datasets continues to grow, privacy risks arising from memorization have attracted increasing attention. Quantifying language model memorization helps evaluate potential privacy risks.

**Key methods/findings**
- To this end, we propose a finegrained, entity-level definition to quantify memorization with conditions and metrics closer to real-world scenarios.
- As the scale of datasets continues to grow, privacy risks arising from memorization have attracted increasing attention.
- The results demonstrate that LLMs not only memorize their training data but also understand associations between entities.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## Extracting Training Data from Large Language Models
**Authors & Year:** Carlini et al. (2021)

**Summary:** It has become common to publish large (billion parameter) language models that have been trained on private datasets. This paper demonstrates that in such settings, an adversary can perform a training data extraction attack to recover individual training examples by querying the language model. We demonstrate our attack on GPT-2, a language model trained on scrapes of the public Internet, and are able to extract hundreds of verbatim text sequences from the model’s training data.

**Key methods/findings**
- This paper demonstrates that in such settings, an adversary can perform a training data extraction attack to recover individual training examples by querying the language model.
- We demonstrate our attack on GPT-2, a language model trained on scrapes of the public Internet, and are able to extract hundreds of verbatim text sequences from the model’s training data.
- We comprehensively evaluate our extraction attack to understand the factors that contribute to its success.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.

---

## Quantifying Memorization Across Neural Language Models
**Authors & Year:** Carlini et al. (2023)

**Summary:** Large language models (LMs) have been shown to memorize parts of their training data, and when prompted appropriately, they will emit the memorized training data verbatim. This is undesirable because memorization violates privacy (exposing user data), degrades utility (repeated easy-to-memorize text is often low quality), and hurts fairness (some texts are memorized over others). We describe three log-linear relationships that quantify the degree to which LMs emit memorized training data.

**Key methods/findings**
- Large language models (LMs) have been shown to memorize parts of their training data, and when prompted appropriately, they will emit the memorized training data verbatim.
- We describe three log-linear relationships that quantify the degree to which LMs emit memorized training data.
- Surprisingly, we ﬁnd the situation becomes more complicated when generalizing these results across model families.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence. It also maps directly to evidence-intrusion scoring.

---

## Scalable Extraction of Training Data
**Authors & Year:** Carlini et al. (2023)

**Summary:** This paper studies extractable memorization : training data that an adversary can efficiently extract by querying a machine learning model without prior knowledge of the training dataset. We show an adversary can extract gigabytes of training data from open-source language models like Pythia or GPT-Neo, semi-open models like LLaMA or Falcon, and closed models like ChatGPT. Existing techniques from the literature suffice to attack unaligned models; in order to attack the aligned ChatGPT, we develop a new divergence attack that causes the model to diverge from its chatbot-style generations and emit training data at a rate 150×higher than when behaving properly.

**Key methods/findings**
- Existing techniques from the literature suffice to attack unaligned models; in order to attack the aligned ChatGPT, we develop a new divergence attack that causes the model to diverge from its chatbot-style generations and emit training data at a rate 150×higher than when behaving properly.
- Our methods show practical attacks can recover far more data than previously thought, and reveal that current alignment techniques do not eliminate memorization.
- This paper studies extractable memorization : training data that an adversary can efficiently extract by querying a machine learning model without prior knowledge of the training dataset.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.

---

## Secret Sharer Unintended Memorization
**Authors & Year:** Carlini et al. (2019)

**Summary:** This paper describes a testing methodology for quantitatively assessing the risk that rare or unique training-data sequences are unintentionally memorized by generative sequence models—a common type of machine-learning model. Because such models are sometimes trained on sensitive data (e.g., the text of users’ private messages), this methodology can beneﬁt privacy by allowing deep-learning practitioners to select means of training that minimize such memorization. In experiments, we show that unintended memorization is a persistent, hard-to-avoid issue that can have serious consequences.

**Key methods/findings**
- In experiments, we show that unintended memorization is a persistent, hard-to-avoid issue that can have serious consequences.
- This paper describes a testing methodology for quantitatively assessing the risk that rare or unique training-data sequences are unintentionally memorized by generative sequence models—a common type of machine-learning model.
- Because such models are sometimes trained on sensitive data (e.g., the text of users’ private messages), this methodology can beneﬁt privacy by allowing deep-learning practitioners to select means of training that minimize such memorization.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.

---

## What Neural Networks Memorize and Why: Discovering the Long Tail via Influence Estimation
**Authors & Year:** Feldman & Zhang (2020)

**Summary:** Deep learning algorithms are well-known to have a propensity for ﬁtting the training data very well and often ﬁt even outliers and mislabeled data points. Such ﬁtting requires memorization of training data labels, a phenomenon that has attracted signiﬁcant research interest but has not been given a compelling explanation so far. A recent work of Feldman [Fel19] proposes a theoretical explanation for this phenomenon based on a combination of two insights.

**Key methods/findings**
- Our experiments demonstrate the signiﬁcant beneﬁts of memorization for generalization on several standard benchmarks.
- Estimating these quantities directly is computationally prohibitive but we show that closely-related subsampled inﬂuence and memorization values can be estimated much more efﬁciently.
- In this work we design experiments to test the key ideas in this theory.

**Insight for our project:** This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.
