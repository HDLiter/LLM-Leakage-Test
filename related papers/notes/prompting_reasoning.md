# Prompting & Reasoning Techniques

## CHiLL: Zero-Shot Feature Extraction with Large Language Models
**Authors & Year:** McInerney et al. (2022)

**Summary:** This paper describes our participation to the 2022 TREC Deep Learning challenge. We submitted runs to all four tasks, with a focus on the full retrieval passage task. The strategy is almost the same as 2021, with ﬁrst stage retrieval being based around SPLADE, with some added ensembling with ColBERTv2 an d DocT5.

**Key methods/findings**
- Initial result analysis show that the strategy is still strong, but is still uncle ar to us what next steps should we take.
- This paper describes our participation to the 2022 TREC Deep Learning challenge.
- We submitted runs to all four tasks, with a focus on the full retrieval passage task.

**Insight for our project:** This paper helps us separate reasoning behavior from recitation behavior at the prompt level. That is useful when building CFLS evaluation prompts, counterfactual testing scripts, and evidence-intrusion probes that minimize leakage introduced by the prompting format itself. It also maps directly to evidence-intrusion scoring.

---

## GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in LLMs
**Authors & Year:** Mirzadeh, Alizadeh, Shahrokhi, Tuzel, Bengio, Farajtabar (2024)

**Summary:** Introduces GSM-Symbolic, a templated variant of GSM8K that generates mathematically equivalent questions by perturbing surface tokens (names, numbers, entities). Measures robustness across rephrasings and difficulty-controlled complexity tiers, and adds a GSM-NoOp variant with irrelevant-but-plausible clauses inserted into problems.

**Key methods/findings**
- LLM accuracy varies significantly across equivalent instantiations of the same template, revealing variance hidden by single-seed GSM8K scores.
- Performance degrades as problems get longer/more clauses, even when reasoning depth is held constant.
- Inserting an irrelevant clause (NoOp) drops accuracy by up to 65%, which the authors interpret as evidence that models pattern-match training-set reasoning trajectories rather than execute symbolic logic.

**Insight for our project:** This is a near-perfect methodological analogue for FinMem-Bench in a different domain: surface-invariant perturbation of a memorized benchmark exposes recitation, which is exactly what our counterfactual entity/date swaps and evidence-intrusion probes do for CLS Chinese financial news. The NoOp result in particular justifies our "distractor clause" intrusion variant and gives us a citable precedent that distribution-preserving perturbation is a legitimate memorization-vs-reasoning separator.

---

## Disentangling Memory and Reasoning Ability in LLMs
**Authors & Year:** Jin et al. (2025)

**Summary:** —With the ever-increasing computing power of supercomputers and the growing scale of scientific applications, the efficiency of MPI collective communication turns out to be a critical bottleneck in large-scale distributed and parallel processing. The large message size in MPI collectives is particularly concerning because it can significantly degrade overall parallel performance. To address this issue, prior research simply applies off-the-shelf fixed-rate lossy compressors in the MPI collectives, leading to suboptimal performance, limited generalizability, and unbounded errors.

**Key methods/findings**
- In this paper, we propose a novel solution, called ZCCL, which leverages error-bounded lossy compression to significantly reduce the message size, resulting in a substantial reduction in communication costs.
- (1) We develop two general, optimized lossy-compression-based frameworks for both types of MPI collectives (collective data movement as well as collective computation), based on their particular characteristics.
- Our framework not only reduces communication costs but also preserves data accuracy.

**Insight for our project:** This paper helps us separate reasoning behavior from recitation behavior at the prompt level. That is useful when building CFLS evaluation prompts, counterfactual testing scripts, and evidence-intrusion probes that minimize leakage introduced by the prompting format itself.

---

## Language Models Don’t Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting
**Authors & Year:** Turpin et al. (2023)

**Summary:** Large Language Models (LLMs) can achieve strong performance on many tasks by producing step-by-step reasoning before giving a final output, often referred to as chain-of-thought reasoning (CoT). It is tempting to interpret these CoT explanations as the LLM’s process for solving a task. This level of transparency into LLMs’ predictions would yield significant safety benefits.

**Key methods/findings**
- However, we find that CoT explanations can systematically misrepresent the true reason for a model’s prediction.
- Our findings indicate that CoT explanations can be plausible yet misleading, which risks increasing our trust in LLMs without guaranteeing their safety.
- Building more transparent and explainable systems will require either improving CoT faithfulness through targeted efforts or abandoning CoT in favor of alternative methods.

**Insight for our project:** This paper helps us separate reasoning behavior from recitation behavior at the prompt level. That is useful when building CFLS evaluation prompts, counterfactual testing scripts, and evidence-intrusion probes that minimize leakage introduced by the prompting format itself. It also maps directly to evidence-intrusion scoring.

---

## Least-to-Most Prompting Complex Reasoning
**Authors & Year:** Zhou et al. (2023)

**Summary:** Chain-of-thought prompting has demonstrated remarkable performance on various natural language reasoning tasks. However, it tends to perform poorly on tasks which requires solving problems harder than the exemplars shown in the prompts. To overcome this challenge of easy-to-hard generalization, we propose a novel prompting strategy, least-to-most prompting .

**Key methods/findings**
- To overcome this challenge of easy-to-hard generalization, we propose a novel prompting strategy, least-to-most prompting .
- Chain-of-thought prompting has demonstrated remarkable performance on various natural language reasoning tasks.
- Our experimental results on tasks related to symbolic manipulation, compositional generalization, and math reasoning reveal that least-to-most prompting is capable of generalizing to more difﬁcult problems than those seen in the prompts.

**Insight for our project:** This paper helps us separate reasoning behavior from recitation behavior at the prompt level. That is useful when building CFLS evaluation prompts, counterfactual testing scripts, and evidence-intrusion probes that minimize leakage introduced by the prompting format itself.

---

## Rationalizing Neural Predictions
**Authors & Year:** Lei et al. (2016)

**Summary:** Prediction without justiﬁcation has limited applicability. As a remedy, we learn to extract pieces of input text as justiﬁcations – rationales – that are tailored to be short and coherent, yet sufﬁcient for making the same prediction. Our approach combines two modular components, generator and encoder, which are trained to operate well together.

**Key methods/findings**
- Our approach outperforms attention-based baseline by a significant margin.
- We also successfully illustrate the method on the question retrieval task.1
- Rationales are never given during training.

**Insight for our project:** This paper helps us separate reasoning behavior from recitation behavior at the prompt level. That is useful when building CFLS evaluation prompts, counterfactual testing scripts, and evidence-intrusion probes that minimize leakage introduced by the prompting format itself. It also maps directly to evidence-intrusion scoring.
