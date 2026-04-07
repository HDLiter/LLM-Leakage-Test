# Knowledge Editing & Localization

## Does Localization Inform Editing? Surprising Differences in Causality-Based Localization vs. Knowledge Editing in Language Models
**Authors & Year:** Hase et al. (2023)

**Summary:** Language models learn a great quantity of factual information during pretraining, and recent work localizes this information to specific model weights like mid-layer MLP weights [ 21]. In this paper, we find that we can change how a fact is stored in a model by editing weights that are in a different location than where existing methods suggest that the fact is stored. This is surprising because we would expect that localizing facts to specific model parameters would tell us where to manipulate knowledge in models, and this assumption has motivated past work on model editing methods.

**Key methods/findings**
- In this paper, we find that we can change how a fact is stored in a model by editing weights that are in a different location than where existing methods suggest that the fact is stored.
- For one of our editing problems, editing performance does relate to localization results from representation denoising, but we find that which layer we edit is a far better predictor of performance.
- Next, we consider several variants of the editing problem, including erasing and amplifying facts.

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence.

---

## Knowledge Neurons in Pretrained Transformers
**Authors & Year:** Dai et al. (2022)

**Summary:** Large-scale pretrained language models are surprisingly good at recalling factual knowledge presented in the training corpus (Petroni et al., 2019; Jiang et al., 2020b). In this paper, we present preliminary studies on how factual knowledge is stored in pretrained Transformers by introducing the concept of knowledge neurons . Speciﬁcally, we examine the ﬁll-in-the-blank cloze task for BERT.

**Key methods/findings**
- Given a relational fact, we propose a knowledge attribution method to identify the neurons that express the fact.
- In this paper, we present preliminary studies on how factual knowledge is stored in pretrained Transformers by introducing the concept of knowledge neurons .
- Speciﬁcally, we examine the ﬁll-in-the-blank cloze task for BERT.

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence.

---

## MEMIT: Mass-Editing Memory in a Transformer
**Authors & Year:** Meng et al. (2023)

**Summary:** Recent work has shown exciting promise in updating large language models with new memories, so as to replace obsolete information or add specialized knowledge. However, this line of work is predominantly limited to updating single associations. We develop MEMIT, a method for directly updating a language model with many memories, demonstrating experimentally that it can scale up to thousands of associations for GPT-J (6B) and GPT-NeoX (20B), exceeding prior work by orders of magnitude.

**Key methods/findings**
- We develop MEMIT, a method for directly updating a language model with many memories, demonstrating experimentally that it can scale up to thousands of associations for GPT-J (6B) and GPT-NeoX (20B), exceeding prior work by orders of magnitude.
- Recent work has shown exciting promise in updating large language models with new memories, so as to replace obsolete information or add specialized knowledge.
- Our code and data are at memit.baulab.info.

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence.

---

## MQuAKE: Assessing Knowledge Editing in Language Models via Multi-Hop Questions
**Authors & Year:** Zhong et al. (2023)

**Summary:** The information stored in large language models (LLMs) falls out of date quickly, and retraining from scratch is often not an option. This has recently given rise to a range of techniques for injecting new facts through updating model weights. Current evaluation paradigms are extremely limited, mainly validating the recall of edited facts, but changing one fact should cause rippling changes to the model’s related beliefs.

**Key methods/findings**
- In this work, we present a benchmark, MQ UAKE (Multi-hop Question Answering for Knowledge Editing), comprising multi-hop questions that assess whether edited models correctly answer questions where the answer should change as an entailed consequence of edited facts.
- While we find that current knowledge-editing approaches can recall edited facts accurately, they fail catastrophically on the constructed multi-hop questions.
- While MQ UAKE remains challenging, we show that MeLLo scales well with LLMs (e.g., OpenAI GPT-3.5-turbo) and outperforms previous model editors by a large margin.1

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence.

---

## Propagation Pitfalls Knowledge Editing
**Authors & Year:** Knowledge Editing et al. (2023)

**Summary:** Current approaches of knowledge editing struggle to effectively propagate updates to interconnected facts. In this work, we delve into the barriers that hinder the appropriate propagation of updated knowledge within these models for accurate reasoning. To support our analysis, we introduce a novel reasoningbased benchmark – ReCoE (Reasoning-based Counterfactual Editing dataset) – which covers six common reasoning schemes in real world.

**Key methods/findings**
- To support our analysis, we introduce a novel reasoningbased benchmark – ReCoE (Reasoning-based Counterfactual Editing dataset) – which covers six common reasoning schemes in real world.
- We found that all model editing methods show notably low performance on this dataset, especially in certain reasoning schemes.
- We will make our benchmark publicly available.

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence. It especially supports our counterfactual testing design.

---

## ROME: Locating and Editing Factual Associations in GPT
**Authors & Year:** Meng et al. (2022)

**Summary:** We analyze the storage and recall of factual associations in autoregressive transformer language models, ﬁnding evidence that these associations correspond to localized, directly-editable computations. We ﬁrst develop a causal intervention for identifying neuron activations that are decisive in a model’s factual predictions. This reveals a distinct set of steps in middle-layer feed-forward modules that mediate factual predictions while processing subject tokens.

**Key methods/findings**
- We ﬁnd that ROME is effective on a standard zero-shot relation extraction (zsRE) model-editing task.
- The code, dataset, visualizations, and an interactive demo notebook are available at https://rome.baulab.info/ .
- This reveals a distinct set of steps in middle-layer feed-forward modules that mediate factual predictions while processing subject tokens.

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence. It especially supports our counterfactual testing design.

---

## Who’s Harry Potter? Approximate Unlearning in LLMs
**Authors & Year:** Eldan & Russinovich (2023)

**Summary:** Large language models (LLMs) are trained on massive interne t corpora that often contain copyrighted content. This poses legal and ethical challeng es for the developers and users of these models, as well as the original authors and publishers . In this paper, we propose a novel technique for unlearning a subset of the training data from a LLM, without having to retrain it from scratch.

**Key methods/findings**
- While the model took over 184K GPU-hours to pretrain, we show that i n about 1 GPU hour of ﬁnetuning, we eﬀectively erase the model’s ability to genera te or recall Harry Potter-related content, while its performance on common benchmarks (such a s Winogrande, Hellaswag, arc, boolq and piqa) remains almost unaﬀected.
- In this paper, we propose a novel technique for unlearning a subset of the training data from a LLM, without having to retrain it from scratch.
- Large language models (LLMs) are trained on massive interne t corpora that often contain copyrighted content.

**Insight for our project:** Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence. It also maps directly to evidence-intrusion scoring.
