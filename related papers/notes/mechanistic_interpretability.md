# Mechanistic Interpretability & Internal Representations

## A Causal View of Entity Bias in (Large) Language Models
**Authors & Year:** Wang et al. (2023)

**Summary:** Entity bias widely affects pretrained (large) language models, causing them to rely on (biased) parametric knowledge to make unfaithful predictions. Although causality-inspired methods have shown great potential to mitigate entity bias, it is hard to precisely estimate the parameters of underlying causal models in practice. The rise of black-box LLMs also makes the situation even worse, because of their inaccessible parameters and uncalibrated logits.

**Key methods/findings**
- Although causality-inspired methods have shown great potential to mitigate entity bias, it is hard to precisely estimate the parameters of underlying causal models in practice.
- Building upon this SCM, we propose causal intervention techniques to mitigate entity bias for both white-box and black-box settings.
- To address these problems, we propose a specific structured causal model (SCM) whose parameters are comparatively easier to estimate.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## Co-occurrence is not Factual Association in Language Models
**Authors & Year:** Xiao Zhang (Unknown)

**Summary:** Pretrained language models can encode a large amount of knowledge and utilize it for various reasoning tasks, yet they can still struggle to learn novel factual knowledge effectively from finetuning on limited textual demonstrations. In this work, we show that the reason for this deficiency is that language models are biased to learn word co-occurrence statistics instead of true factual associations. We identify the differences between two forms of knowledge representation in language models: knowledge in the form of co-occurrence statistics is encoded in the middle layers of the transformer model and does not generalize well to reasoning scenarios beyond simple question answering, while true factual associations are encoded in the lower layers and can be freely utilized in various reasoning tasks.

**Key methods/findings**
- Based on these observations, we propose two strategies to improve the learning of factual associations in language models.
- In this work, we show that the reason for this deficiency is that language models are biased to learn word co-occurrence statistics instead of true factual associations.
- We also propose a simple training method to actively forget the learned co-occurrence statistics, which unblocks and enhances the learning of factual associations when training on plain narrative text.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms.

---

## Dissecting Recall of Factual Associations in Auto-Regressive Language Models
**Authors & Year:** Geva et al. (2023)

**Summary:** Transformer-based language models (LMs) are known to capture factual knowledge in their parameters. While previous work looked into where factual associations are stored, only little is known about howthey are retrieved internally during inference. We investigate this question through the lens of information flow.

**Key methods/findings**
- Overall, our findings introduce a comprehensive view of how factual associations are stored and extracted internally in LMs, facilitating future research on knowledge localization and editing.1
- Given a subject-relation query, we study how the model aggregates information about the subject and relation to predict the correct attribute.
- We investigate this question through the lens of information flow.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms.

---

## Entity Cells in Language Models
**Authors & Year:** Yona et al. (2026)

**Summary:** Language models can answer many entitycentric factual questions, but it remains unclear which internal mechanisms are involved in this process. We study this question across multiple language models. We localize entity-selective MLP neurons using templated prompts about each entity, and then validate them with causal interventions on PopQA-based QA examples.

**Key methods/findings**
- We study this question across multiple language models.
- Robustness to aliases, acronyms, misspellings, and multilingual forms supports a canonicalization interpretation.
- Negative ablation produces entityspecific amnesia, while controlled injection at a placeholder token improves answer retrieval relative to mean-entity and wrong-cell controls.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## Entity Identification in Language Models
**Authors & Year:** Sakata et al. (2025)

**Summary:** We analyze the extent to which internal representations of language models (LMs) identify and distinguish mentions of named entities, focusing on the many-to-many correspondence between entities and their mentions. We first formulate two problems of entity mentions — ambiguity and variability — and propose a framework analogous to clustering quality metrics. Specifically, we quantify through cluster analysis of LM internal representations the extent to which mentions of the same entity cluster together and mentions of different entities remain separated.

**Key methods/findings**
- Our experiments examine five Transformer-based autoregressive models, showing that they effectively identify and distinguish entities with metrics analogous to precision and recall ranging from 0.66 to 0.9.
- Further analysis reveals that entity-related information is compactly represented in a low-dimensional linear subspace at early LM layers.
- We first formulate two problems of entity mentions — ambiguity and variability — and propose a framework analogous to clustering quality metrics.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## Explaining the Unexplained: Revealing Hidden Correlations for Better Interpretability
**Authors & Year:** Jiang et al. (Unknown)

**Summary:** Deep learning has achieved remarkable success in processing and managing unstructured data. However, its "black box" nature imposes significant limitations, particularly in sensitive application domains. While existing interpretable machine learning methods address some of these issues, they often fail to adequately consider feature correlations and provide insufficient evaluation of model decision paths.

**Key methods/findings**
- Experimental validations on two unstructured data tasks—image classification and text sentiment analysis—demonstrate that RealExp significantly outperforms existing methods in interpretability.
- Additionally, this paper proposes a novel interpretability evaluation criterion focused on elucidating the decision paths of deep learning models, going beyond traditional accuracy-based metrics.
- While existing interpretable machine learning methods address some of these issues, they often fail to adequately consider feature correlations and provide insufficient evaluation of model decision paths.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms.

---

## TRAK: Attributing Model Behavior at Scale
**Authors & Year:** Park et al. (2023)

**Summary:** The goal of data attribution is to trace model predictions back to training data. Despite a long line of work towards this goal, existing approaches to data attribution tend to force users to choose between computational tractability and efﬁcacy. That is, computationally tractable methods can struggle with accurately attributing model predictions in non-convex settings (e.g., in the context of deep neural networks), while methods that are effective in such regimes require training thousands of models, which makes them impractical for large models or datasets.

**Key methods/findings**
- In this work, we introduce TRAK (Tracing with the Randomly-projected After Kernel), a data attribution method that is both effective andcomputationally tractable for large-scale, differentiable models.
- In particular, by leveraging only a handful of trained models, TRAK can match the performance of attribution methods that require training thousands of models.
- We demonstrate the utility of TRAK across various modalities and scales: image classiﬁers trained on ImageNet, vision-language models ( CLIP ), and language models ( BERT and mT5).

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms. It also maps directly to evidence-intrusion scoring.

---

## Transformer Feed-Forward Layers Are Key-Value Memories
**Authors & Year:** Geva et al. (2021)

**Summary:** Feed-forward layers constitute two-thirds of a transformer model’s parameters, yet their role in the network remains under-explored. We show that feed-forward layers in transformerbased language models operate as key-value memories, where each key correlates with textual patterns in the training examples, and each value induces a distribution over the output vocabulary. Our experiments show that the learned patterns are human-interpretable, and that lower layers tend to capture shallow patterns, while upper layers learn more semantic ones.

**Key methods/findings**
- Our experiments show that the learned patterns are human-interpretable, and that lower layers tend to capture shallow patterns, while upper layers learn more semantic ones.
- Finally, we demonstrate that the output of a feed-forward layer is a composition of its memories, which is subsequently reﬁned throughout the model’s layers via residual connections to produce the ﬁnal output distribution.
- We show that feed-forward layers in transformerbased language models operate as key-value memories, where each key correlates with textual patterns in the training examples, and each value induces a distribution over the output vocabulary.

**Insight for our project:** This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms.
