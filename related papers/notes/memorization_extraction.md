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

---

## Quantifying Memorization and Detecting Training Data of Pre-trained Language Models using Japanese Newspaper
**Authors & Year:** Ishihara & Takahashi (2024)

**Summary:** Ishihara and Takahashi study memorization in a non-English news setting by pre-training Japanese GPT-2 models on newspaper corpora and then probing whether classic English-language findings still hold. They report the same core pattern: memorization risk rises with duplication in the training data, larger model size, and shorter prompts, and they further show that Japanese training examples remain detectable through membership inference.

**Key methods/findings**
- Pre-trains domain-specific Japanese GPT-2 models on newspaper articles rather than relying on general English benchmarks.
- Replicates the duplication, model-size, and prompt-length effects previously reported in English memorization studies.
- Demonstrates that membership inference can detect Japanese newspaper training data, warning that domain PLMs can copy and paste valuable text at scale.

**Insight for our project:** This directly strengthens Propagation Intensity and Template Rigidity in a news domain that is much closer to CLS than the usual English web corpora. It should seed R5 Min-K%, MIA, and extraction families on Chinese announcement text; the caveat is that the evidence comes from GPT-2-style domain PLMs rather than current frontier chat models.

---

## Deduplicating Training Data Makes Language Models Better
**Authors & Year:** Lee et al. (2021)

**Summary:** Lee et al. show that standard LM corpora contain extensive near-duplicates and long repeated substrings, with measurable consequences for memorization and evaluation. Their deduplication pipeline sharply reduces verbatim copying, lowers train-test overlap, and lets models reach equal or better accuracy with fewer training steps.

**Key methods/findings**
- Finds that over 1% of unprompted LM output can be copied verbatim from duplicated training data.
- Introduces practical tools for removing near-duplicates and long repeated substrings from large corpora such as C4.
- Shows that deduplication cuts memorized emission roughly tenfold while improving training efficiency and evaluation validity.

**Insight for our project:** This is foundational support for Template Rigidity and also backs Propagation Intensity because repeated substrings and near-duplicate templates materially raise copying risk. It should seed R5 extraction, Min-K%, and duplicate-aware calibration baselines; the caveat is that the paper studies general-language corpora rather than finance-specific or temporally controlled benchmarks.

---

## A Comparative Analysis of LLM Memorization at Statistical and Internal Levels: Cross-Model Commonalities and Model-Specific Signatures
**Authors & Year:** Chen et al. (2026)

**Summary:** Chen, Han, and Miyao compare memorization behavior across multiple open model families instead of treating one family as universal evidence. They connect statistical regularities such as log-linear scaling and frequency effects with internal analyses of layer decoding and attention-head importance, separating cross-model commonalities from family-specific signatures.

**Key methods/findings**
- Studies memorization across Pythia, OpenLLaMa, StarCoder, and OLMo families rather than within a single lineage.
- Finds log-linear scaling of memorization with model size and shared frequency and domain distribution patterns for memorized sequences.
- Shows that important memorization heads and internal decoding patterns have both shared structure and family-specific differences.

**Insight for our project:** This strengthens Propagation Intensity, Template Rigidity, and the case for cross-family comparison instead of single-model memorization claims. It should seed R5 CMMD alongside Min-K%, MIA, and extraction because the paper explicitly separates shared regularities from family-specific signatures; the caveat is that the experiments use open model families and generic corpora rather than finance-specific data.

---

## Membership Inference Attacks Against Machine Learning Models
**Authors & Year:** Shokri et al. (2016)

**Summary:** Shokri, Stronati, Song, and Shmatikov introduce the black-box membership inference attack in its now-standard form: given a record and query access to a model, infer whether that record appeared in training. Their attack trains shadow models and a separate inference model to distinguish the prediction patterns associated with members versus non-members, and demonstrates leakage on commercial ML-as-a-service systems and sensitive classification tasks.

**Key methods/findings**
- Formalizes black-box membership inference using shadow-model simulation of the target model's train/non-train confidence patterns.
- Demonstrates successful attacks on models trained by commercial providers such as Google and Amazon, including a privacy-sensitive hospital-discharge dataset.
- Analyzes which settings increase leakage and evaluates mitigation ideas rather than treating attack accuracy as a fixed property.

**Insight for our project:** This is the canonical anchor for the R5 MIA detector family. It justifies keeping membership-style probes in FinMem-Bench even when we move to finance text, because the core signal is still train-versus-non-train confidence asymmetry; the caveat is that the original evidence comes from supervised classifiers rather than generative LLMs on temporal news.

---

## Membership Inference Attacks From First Principles
**Authors & Year:** Carlini et al. (2021)

**Summary:** Carlini and coauthors argue that average-case attack accuracy is the wrong way to judge membership inference because it hides whether an attack can identify any members at very low false-positive rates. They derive a likelihood-ratio attack (LiRA) that combines prior ideas into a stronger decision rule and show that it is substantially more powerful than earlier attacks when evaluated in the low-FPR regime relevant to practical privacy claims.

**Key methods/findings**
- Reframes MIA evaluation around true-positive rate at very low false-positive rates rather than coarse average accuracy.
- Introduces LiRA, which compares a point's likelihood under member and non-member score distributions.
- Reports roughly an order-of-magnitude improvement over prior attacks in the low-FPR regime.

**Insight for our project:** This sharpens the R5 MIA family by telling us what a credible detector threshold should look like when false accusations of memorization are costly. For FinMem-Bench, it argues for reporting low-FPR operating points or calibrated score tails, not just average separation between contaminated and clean items.

---

## Min-K%++: Improved Baseline for Detecting Pre-Training Data from LLMs
**Authors & Year:** Zhang et al. (2024)

**Summary:** Zhang and colleagues revisit pretraining-data detection and argue that earlier Min-K%-style heuristics lack a sound theoretical basis. They reinterpret the task as detecting whether an input behaves like a local mode of the model's learned distribution, derive Min-K%++ from that view, and show state-of-the-art detection performance on both WikiMIA and the harder MIMIR benchmark.

**Key methods/findings**
- Gives a local-maxima interpretation of why training examples should be distinguishable under maximum-likelihood training.
- Designs Min-K%++ to test whether an input forms a mode or unusually high-probability region under conditional token distributions.
- Improves AUROC over prior baselines on WikiMIA and remains competitive on the more difficult MIMIR setting.

**Insight for our project:** This directly supports the R5 Min-K% detector family and strengthens Propagation Intensity as a token-level signature of memorized exposure. It matters for FinMem-Bench because Min-K%++ is a stronger black-box screening baseline for Chinese announcement text than raw likelihood heuristics, though the benchmark evidence still comes from generic corpora rather than finance-specific disclosures.

---

## Inherent Challenges of Post-Hoc Membership Inference for LLMs
**Authors & Year:** Meeus et al. (2024)

**Summary:** The current arXiv version of this paper is retitled as a SoK on LLM membership inference, but its central claim is the same: post-hoc MIA evaluation for LLMs is fundamentally confounded by distribution shift between guessed members and guessed non-members. Meeus and coauthors review recent LLM MIA work, show that widely used post-hoc datasets are separable even by a model-free bag-of-words classifier, and argue that many strong memorization claims are therefore not methodologically secure.

**Key methods/findings**
- Reviews recent LLM MIA work and highlights that most methods are evaluated on member/non-member sets assembled after model release rather than randomized at collection time.
- Uses a model-less bag-of-words classifier to show substantial member/non-member distribution shift in six post-hoc datasets.
- Recommends randomized splits, injected unique sequences, randomized fine-tuning, and stronger post-hoc controls as more defensible evaluation designs.

**Insight for our project:** This is a crucial caution for the R5 MIA family: detector wins on post-hoc splits may reflect dataset shift rather than true memorization. For FinMem-Bench, it supports explicit clean/control construction, randomized counterfactuals, and cross-family triangulation before we interpret a positive MIA score as evidence of article-level leakage.

---

## How Much Do Language Models Copy From Their Training Data? Evaluating Linguistic Novelty in Text Generation Using RAVEN
**Authors & Year:** McCoy et al. (2023)

**Summary:** McCoy, Smolensky, Linzen, Gao, and Celikyilmaz propose RAVEN, a set of novelty analyses that separate local sequential overlap from larger-scale structural novelty in generated text. Across four English language models, they find that generated text is substantially less novel than human text at the local n-gram and dependency level, while sentence-level structure can remain novel; nevertheless, models sometimes still reproduce extremely long copied passages from training data.

**Key methods/findings**
- Introduces RAVEN to measure both sequential novelty and syntactic novelty rather than relying on a single overlap score.
- Shows that local linguistic structure in model generations is much less novel than human-written baselines from the test set.
- Documents cases where models duplicate training passages longer than 1,000 words despite apparently novel higher-level structure.

**Insight for our project:** This strengthens Template Rigidity and the extraction-style branch of R5 by showing that copying can hide beneath superficially varied surface text. For FinMem-Bench, it supports novelty-sensitive checks on announcement narratives and motivates pairing Min-K% or MIA scores with textual-novelty diagnostics before declaring an output clean.

---

## Memorization Without Overfitting: Analyzing the Training Dynamics of LLMs
**Authors & Year:** Tirumala et al. (2022)

**Summary:** Tirumala, Markosyan, Zettlemoyer, and Aghajanyan study exact memorization through training rather than only at the end of training. They show that larger language models memorize faster and forget less, can absorb more exact training data before classic overfitting appears, and tend to lock onto nouns and numbers early - suggesting that entity-like and value-like tokens act as anchors for memorizing individual examples.

**Key methods/findings**
- Tracks exact memorization in both causal and masked language modeling across model sizes and training stages.
- Finds that larger models memorize faster, retain more memorized material, and can do so before standard overfitting diagnostics trigger.
- Shows that nouns and numbers are memorized especially early, supporting the idea that they act as identifiers for memorized examples.

**Insight for our project:** This directly supports Propagation Intensity and the entity/date-sensitive side of FinMem-Bench because dates, ticker-linked entities, and numeric outcomes are exactly the tokens we worry about in Chinese disclosures. It should inform R5 Min-K%, extraction, and entity-conditioned probes; the caveat is that the paper studies training dynamics in general LLMs rather than downstream finance prompting.
