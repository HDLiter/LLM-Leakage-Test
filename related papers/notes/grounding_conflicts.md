# Factual Grounding & Knowledge Conflicts

## Chain-of-Note: Enhancing Robustness in Retrieval-Augmented Language Models
**Authors & Year:** Yu et al. (2024)

**Summary:** Retrieval-augmented language model (RALM) represents a significant advancement in mitigating factual hallucination by leveraging external knowledge sources. However, the reliability of the retrieved information is not always guaranteed, and the retrieval of irrelevant data can mislead the response generation. Moreover, standard RALMs frequently neglect their intrinsic knowledge due to the interference from retrieved information.

**Key methods/findings**
- In this paper, we introduces CHAIN -OF-NOTE (CON), a novel approach to improve robustness of RALMs in facing noisy, irrelevant documents and in handling unknown scenarios.
- Our experiments across four open-domain QA benchmarks show that fine-tuned RALMs equipped with CONsignificantly outperform standard fine-tuned RALMs.
- Our experimental results show that GPT-4, when equipped with CON, outperforms the CHAIN -OF-THOUGHT approach.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## Chain-of-Verification Reduces Hallucination in Large Language Models
**Authors & Year:** Dhuliawala et al. (2023)

**Summary:** Generation of plausible yet incorrect factual information, termed hallucination, is an unsolved issue in large language models. We study the ability of language models to deliberate on the responses they give in order to correct their mistakes. We develop the Chain-of-Verification (C OVE) method whereby the model first (i) drafts an initial response; then (ii) plans verification questions to fact-check its draft; (iii) answers those questions independently so the answers are not biased by other responses; and (iv) generates its final verified response.

**Key methods/findings**
- We develop the Chain-of-Verification (C OVE) method whereby the model first (i) drafts an initial response; then (ii) plans verification questions to fact-check its draft; (iii) answers those questions independently so the answers are not biased by other responses; and (iv) generates its final verified response.
- We study the ability of language models to deliberate on the responses they give in order to correct their mistakes.
- In experiments, we show COVEdecreases hallucinations across a variety of tasks, from list-based questions from Wikidata, closed book MultiSpanQA and longform text generation.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## Context-Faithful Prompting for Large Language Models
**Authors & Year:** Zhou et al. (2023)

**Summary:** Large language models (LLMs) encode parametric knowledge about world facts and have shown remarkable performance in knowledgedriven NLP tasks. However, their reliance on parametric knowledge may cause them to overlook contextual cues, leading to incorrect predictions in context-sensitive NLP tasks (e.g., knowledge acquisition tasks). In this paper, we seek to assess and enhance LLMs’ contextual faithfulness in two aspects: knowledge conflict and prediction with abstention.

**Key methods/findings**
- We demonstrate that LLMs’ faithfulness can be significantly improved using carefully designed prompting strategies.
- Large language models (LLMs) encode parametric knowledge about world facts and have shown remarkable performance in knowledgedriven NLP tasks.
- We conduct experiments on three datasets of two standard NLP tasks, machine reading comprehension and relation extraction, and the results demonstrate significant improvement in faithfulness to contexts.1

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It especially supports our counterfactual testing design.

---

## Entity-Based Knowledge Conflicts in Question Answering
**Authors & Year:** Longpre et al. (2021)

**Summary:** Knowledge-dependent tasks typically use two sources of knowledge: parametric , learned at training time, and contextual , given as a passage at inference time. To understand how models use these sources together, we formalize the problem of knowledge conﬂicts, where the contextual information contradicts the learned information. Analyzing the behaviour of popular models, we measure their over-reliance on memorized information (the cause of hallucinations), and uncover important factors that exacerbate this behaviour.

**Key methods/findings**
- Lastly, we propose a simple method to mitigate over-reliance on parametric knowledge which minimizes hallucination and improves out-of-distribution generalization by 4% 7%.
- To encourage these practices, we have released our framework for generating knowledge conﬂicts.1
- Knowledge-dependent tasks typically use two sources of knowledge: parametric , learned at training time, and contextual , given as a passage at inference time.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## How Well Do LLMs Truly Ground
**Authors & Year:** Lee et al. (2024)

**Summary:** To reduce issues like hallucinations and lack of control in Large Language Models (LLMs), a common method is to generate responses by grounding on external contexts given as input, known as knowledge-augmented models. However, previous research often narrowly defines “grounding” as just having the correct answer, which does not ensure the reliability of the entire response. To overcome this, we propose a stricter definition of grounding: a model is truly grounded if it (1) fully utilizes the necessary knowledge from the provided context, and (2) stays within the limits of that knowledge.

**Key methods/findings**
- We introduce a new dataset and a grounding metric to evaluate model capability under the definition.
- To reduce issues like hallucinations and lack of control in Large Language Models (LLMs), a common method is to generate responses by grounding on external contexts given as input, known as knowledge-augmented models.
- To overcome this, we propose a stricter definition of grounding: a model is truly grounded if it (1) fully utilizes the necessary knowledge from the provided context, and (2) stays within the limits of that knowledge.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## Interpreting and Mitigating Knowledge Conflicts in Language Models
**Authors & Year:** Jin et al. (2024)

**Summary:** Recently, retrieval augmentation and tool augmentation have demonstrated a remarkable capability to expand the internal memory boundaries of language models (LMs) by providing external context . However, internal memory and external context inevitably clash, leading to knowledge conflicts within LMs. In this paper, we aim to interpret the mechanism of knowledge conflicts through the lens of information flow, and then mitigate conflicts by precise interventions at the pivotal point.

**Key methods/findings**
- Inspired by the insights, we propose a novel method called Pruning Head via PatH PatcHing (PH3), which can efficiently mitigate knowledge conflicts by pruning conflicting attention heads without updating model parameters.
- We also conduct extensive experiments to demonstrate the cross-model, cross-relation, and cross-format generalization of our method.
- Moreover, PH3 can also improve the performance of LMs on open-domain QA tasks.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## Investigating Context-Faithfulness in Large Language Models: The Roles of Memory Strength and Evidence Style
**Authors & Year:** Li et al. (2024)

**Summary:** Retrieval-augmented generation (RAG) improves Large Language Models (LLMs) by incorporating external information into the response generation process. However, how context-faithful LLMs are and what factors influence LLMs’ context faithfulness remain largely unexplored. In this study, we investigate the impact of memory strength and evidence presentation on LLMs’ receptiveness to external evidence.

**Key methods/findings**
- These findings provide key insights for improving retrieval-augmented generation and context-aware LLMs.
- Our results show that for questions with high memory strength, LLMs are more likely to rely on internal memory.
- Retrieval-augmented generation (RAG) improves Large Language Models (LLMs) by incorporating external information into the response generation process.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## Mechanistic Circuits for Extractive Question Answering
**Authors & Year:** Basu et al. (2025)

**Summary:** Large language models are increasingly used to process documents and facilitate questionanswering on them. In our paper, we extract mechanistic circuits for this real-world language modeling task: context-augmented language modeling for extractive question-answering (QA) tasks and understand the potential benefits of circuits towards downstream applications such as data attribution to context information. We extract circuits as a function of internal model components (e.g., attention heads, MLPs) using causal mediation analysis techniques.

**Key methods/findings**
- Finally, we show the possibility to steer the language model towards answering from the context, instead of the parametric memory by using the attribution ATTNATTRIB as an additional signal during the forward pass.
- Using this insight, we then introduce ATTNATTRIB , a fast data attribution algorithm which obtains state-ofthe-art attribution results across various extractive QA benchmarks.
- Leveraging the extracted circuits, we first understand the interplay between the model’s usage of parametric memory and retrieved context towards a better mechanistic understanding of context-augmented language models.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## MiniCheck: Efficient Fact-Checking of LLM Outputs on Grounding Documents
**Authors & Year:** Tang, Laban & Durrett (2024)

**Summary:** Recognizing if LLM output can be grounded in evidence is central to many tasks in NLP: retrieval-augmented generation, summarization, document-grounded dialogue, and more. Current approaches to this kind of factchecking are based on verifying each piece of a model generation against potential evidence using an LLM. However, this process can be very computationally expensive, requiring many calls to a model to check a single response.

**Key methods/findings**
- In this work, we show how to build small fact-checking models that have GPT-4level performance but for 400x lower cost.
- Our best system MiniCheck- FT5 (770M parameters) outperforms all systems of comparable size and reaches GPT-4 accuracy.
- For evaluation, we unify datasets from recent work on factchecking and grounding LLM generations into a new benchmark, LLM-A GGRE FACT.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## MIRAGE: Model Internals for Answer Attribution
**Authors & Year:** Unknown (Unknown)

**Summary:** Ensuring the verifiability of model answers is a fundamental challenge for retrieval-augmented generation (RAG) in the question answering (QA) domain. Recently, self-citation prompting was proposed to make large language models (LLMs) generate citations to supporting documents along with their answers. However, self-citing LLMs often struggle to match the required format, refer to non-existent sources, and fail to faithfully reflect LLMs’ context usage throughout the generation.

**Key methods/findings**
- We evaluate our proposed approach on a multilingual extractive QA dataset, finding high agreement with human answer attribution.
- In this work, we present MIRAGE –Model Internals-based RAG Explanations – a plug-and-play approach using model internals for faithful answer attribution in RAG applications.
- MIRAGE detects context-sensitive answer tokens and pairs them with retrieved documents contributing to their prediction via saliency methods.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## ReEval: Hallucination Evaluation for Retrieval-Augmented Generation
**Authors & Year:** Yu et al. (2023)

**Summary:** Despite remarkable advancements in mitigating hallucinations in large language models (LLMs) by retrieval augmentation, it remains challenging to measure the reliability of LLMs using static question-answering (QA) data. Specifically, given the potential of data contamination ( e.g., leading to memorization), good static benchmark performance does not ensure that model can reliably use the provided evidence for responding, which is essential to avoid hallucination when the required knowledge is new or private. Inspired by adversarial machine learning, we investigate the feasibility of automatically perturbing existing static one for dynamic evaluation.

**Key methods/findings**
- We find that our adversarial examples are transferable across all considered LLMs.
- We implement ReEval using ChatGPT and evaluate the resulting variants of two popular open-domain QA datasets on a collection of LLMs under various prompting settings.
- Specifically, this paper presents ReEval , an LLM-based framework using prompt chaining to perturb the original evidence for generating new test cases for evaluating the LLMs’ reliability in using new evidence for answering.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.

---

## Taming Knowledge Conflicts in Language Models
**Authors & Year:** Li et al. (2025)

**Summary:** Language Models (LMs) often encounter knowledge conflicts when parametric memory contradicts contextual knowledge. Previous works attribute this conflict to the interplay between “memory heads” and “context heads”, attention heads assumed to promote either memory or context exclusively. In this study, we go beyond this fundamental assumption by uncovering a critical phenomenon we term the superposition of contextual information and parametric memory , where highly influential attention heads simultaneously contribute to both memory and context.

**Key methods/findings**
- Building upon this insight, we propose Just Run Twice ( JUICE), a test-time attention intervention method that steers LMs toward either parametric beliefs or contextual knowledge without requiring fine-tuning.
- Extensive experiments across 11 datasets and 6 model architectures demonstrate thatJUICE sets the new state-of-the-art performance and robust generalization, achieving significant and consistent improvement across different domains under various conflict types.
- Language Models (LMs) often encounter knowledge conflicts when parametric memory contradicts contextual knowledge.

**Insight for our project:** This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows. It also maps directly to evidence-intrusion scoring.
