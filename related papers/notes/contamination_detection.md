# Benchmark Contamination & Leakage Detection

## AntiLeakBench: Preventing Data Contamination by Automatically Constructing Benchmarks with Updated Real-World Knowledge
**Authors & Year:** Wu et al. (2024)

**Summary:** Data contamination hinders fair LLM evaluation by introducing test data into newer models’ training sets. Existing studies solve this challenge by updating benchmarks with newly collected data. However, they fail to guarantee contamination-free evaluation as the newly collected data may contain pre-existing knowledge, and their benchmark updates rely on intensive human labor.

**Key methods/findings**
- This significantly reduces the cost of benchmark maintenance to accommodate emerging LLMs.
- Existing studies solve this challenge by updating benchmarks with newly collected data.
- We further design a fully automated workflow to build and update our benchmark without human labor.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## Generalization or Memorization: CDD/TED
**Authors & Year:** Dong et al. (2024)

**Summary:** Recent statements about the impressive capabilities of large language models (LLMs) are usually supported by evaluating on open-access benchmarks. Considering the vast size and wide-ranging sources of LLMs’ training data, it could explicitly or implicitly include test data, leading to LLMs being more susceptible to data contamination. However, due to the opacity of training data, the black-box access of models, and the rapid growth of synthetic training data, detecting and mitigating data contamination for LLMs faces significant challenges.

**Key methods/findings**
- To facilitate this study, we introduce two benchmarks, i.e., DETCONandCOMIEVAL, for data contamination detection and contamination mitigation evaluation tasks.
- In realworld applications, we reveal that ChatGPT exhibits a high potential to suffer from data contamination on HumanEval benchmark.1
- Extensive experimental results show that CDD achieves the average relative improvements of 21.8%-30.2% over other contamination detection approaches in terms of Accuracy, F1 Score, and AUC metrics, and can effectively detect implicit contamination.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## How Much are LLMs Contaminated? LLMSanitize
**Authors & Year:** Ravaut et al. (2024)

**Summary:** WiththeriseofLargeLanguageModels(LLMs)inrecentyears, abundantnewopportunities are emerging, but also new challenges, among which contamination is quickly becoming critical. Business applications and fundraising in Artificial Intelligence (AI) have reached a scale at which a few percentage points gained on popular question-answering benchmarks could translate into dozens of millions of dollars, placing high pressure on model integrity. At the same time, it is becoming harder and harder to keep track of the data that LLMs have seen; if not impossible with closed-source models like GPT-4 and Claude-3 not divulging any information on the training set.

**Key methods/findings**
- This limitation jeopardizes real capability improvement in the field of NLP, yet, there remains a lack of methods on how to efficiently detect contamination.
- In this paper, we survey all recent work on contamination detection with LLMs, analyzing their methodologies and use cases to shed light on the appropriate usage of contamination detection methods.
- Business applications and fundraising in Artificial Intelligence (AI) have reached a scale at which a few percentage points gained on popular question-answering benchmarks could translate into dozens of millions of dollars, placing high pressure on model integrity.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## Investigating Data Contamination: TS-Guessing
**Authors & Year:** Deng et al. (2024)

**Summary:** Recent observations have underscored a disparity between the inflated benchmark scores and the actual performance of LLMs, raising concerns about potential contamination of evaluation benchmarks. This issue is especially critical for closed-source models and certain open-source models where training data transparency is lacking. In this paper we study data contamination by proposing two methods tailored for both open-source and proprietary LLMs.

**Key methods/findings**
- In this paper we study data contamination by proposing two methods tailored for both open-source and proprietary LLMs.
- Specifically, in the MMLU benchmark, ChatGPT and GPT-4 demonstrated an exact match rate of 52% and 57%, respectively, in guessing the missing options in benchmark test data.
- We find that certain commercial LLMs could surprisingly guess the missing option in various test sets.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference. It also maps directly to evidence-intrusion scoring.

---

## R1 Additions

- **CLEAN-EVAL:** Cleans evaluation on contaminated LLMs by rebuilding the test side rather than trusting raw benchmark scores; this matters because the R1 NLP review cites it as direct prior art in contamination-resistant benchmark construction.
- **PaCoST:** Uses paired variants plus significance testing to detect contamination; this matters because the R1 NLP review treats counterpart-based detection as already established, raising the bar for FinMem-Bench.
- **An Open-Source Data Contamination Report for Large Language Models:** Systematizes contamination reporting across open models; this matters because the R1 NLP review cites dataset-level contamination auditing as established infrastructure.
- **Leak, Cheat, Repeat:** Documents contamination and evaluation malpractice in closed-source LLMs; this matters because the R1 NLP review argues benchmark claims need tighter release and validity language.
- **Data Contamination Can Cross Language Barriers:** Shows contamination can transfer through translation/paraphrase; this matters because the R1 Stats review uses it to reject naive CN/EN independence assumptions.
- **LastingBench:** Designs a benchmark to stay useful despite knowledge leakage over time; this matters because the R1 NLP and Editor reviews cite it as prior art for leakage-resistant benchmark maintenance.
- **VarBench:** Perturbs benchmark variables dynamically to stress contamination-sensitive evaluation; this matters because the R1 NLP review uses it as another comparator in the crowded contamination-benchmark space.
- **How Can I Publish My LLM Benchmark Without Giving the True Answers Away?:** Proposes publication strategies that preserve benchmark validity; this matters because the R1 Stats review uses it to justify hidden-answer and dev/test separation for FinMem-Bench.

---

## Leakage and the Reproducibility Crisis in ML-Based Science
**Authors & Year:** Kapoor & Narayanan (2023)

**Summary:** The use of machine learning (ML) methods for prediction and forecasting has become widespread across the quantitative sciences. However, there are many known methodological pitfalls, including data leakage, in ML-based science. In this paper, we systematically investigate reproducibility issues in ML-based science.

**Key methods/findings**
- Based on our survey, we present a ﬁnegrained taxonomy of 8 types of leakage that range from textbook errors to open research problems.
- To that end, we propose model info sheets for reporting scientiﬁc claims based on ML models that would address all types of leakage identiﬁed in our survey.
- However, there are many known methodological pitfalls, including data leakage, in ML-based science.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## LiveBench: Contamination-Limited LLM Benchmark
**Authors & Year:** White et al. (2024)

**Summary:** Test set contamination, wherein test data from a benchmark ends up in a newer model’s training set, is a well-documented obstacle for fair LLM evaluation and can quickly render benchmarks obsolete. To mitigate this, many recent benchmarks crowdsource new prompts and evaluations from human or LLM judges; however, these can introduce significant biases, and break down when scoring hard questions. In this work, we introduce a new benchmark for LLMs designed to be resistant to both test set contamination and the pitfalls of LLM judging and human crowdsourcing.

**Key methods/findings**
- In this work, we introduce a new benchmark for LLMs designed to be resistant to both test set contamination and the pitfalls of LLM judging and human crowdsourcing.
- We welcome community engagement and collaboration for expanding the benchmark tasks and models.
- Test set contamination, wherein test data from a benchmark ends up in a newer model’s training set, is a well-documented obstacle for fair LLM evaluation and can quickly render benchmarks obsolete.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference. It also maps directly to evidence-intrusion scoring.

---

## MMLU-CF: A Contamination-Free Multi-Task Language Understanding Benchmark
**Authors & Year:** Fang et al. (2025)

**Summary:** Multiple-choice question (MCQ) datasets like Massive Multitask Language Understanding (MMLU) are widely used to evaluate the commonsense, understanding, and problem-solving abilities of large language models (LLMs). However, the open-source nature of these benchmarks and the broad sources of training data for LLMs have inevitably led to benchmark contamination, resulting in unreliable evaluation results. To alleviate this issue, we propose a contamination-free and more challenging MCQ benchmark called MMLU-CF.

**Key methods/findings**
- To alleviate this issue, we propose a contamination-free and more challenging MCQ benchmark called MMLU-CF.
- This benchmark reassesses LLMs’ understanding of world knowledge by averting both unintentional and malicious data leakage.
- To prevent malicious data leakage, we divide the benchmark into validation and test sets with similar difficulty and subject distributions.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## Proving Test Set Contamination in Black-Box Language Models
**Authors & Year:** Oren et al. (2024)

**Summary:** —Objective: Reconstructing freehand ultrasound in 3D without any external tracker has been a longstanding challenge in ultrasound-assisted procedures. We aim to define new ways of parameterising long-term dependencies, and evaluate the performance. Methods: First, long-term dependency is encoded by transformation positions within a frame sequence.

**Key methods/findings**
- Significance: The proposed new methodology with publicly available volunteer data and code1for parametersing the long-term dependency, experimentally shown to be valid sources of performance improvement, which could potentially
- Methods: First, long-term dependency is encoded by transformation positions within a frame sequence.
- Results: 1) The added long-term dependency up to 400 frames at 20 frames per second (fps) indeed improved reconstruction, with an up to 82.4% lowered accumulated error, compared with the baseline performance.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## RE-IMAGINE: Symbolic Benchmark Synthesis for Reasoning
**Authors & Year:** Xu et al. (2025)

**Summary:** Recent Large Language Models (LLMs) have reported high accuracy on reasoning benchmarks. However, it is still unclear whether the observed results arise from true “reasoning” or from statistical recall of the training set. Inspired by the ladder of causation (Pearl, 2009) and its three levels (associations, interventions and counterfactuals), this paper introduces RE-IMAGINE : a framework to characterize a hierarchy of reasoning ability in LLMs, alongside a scalable pipeline to generate problem variations across all the levels of the hierarchy.

**Key methods/findings**
- We demonstrate the type of insights that RE-IMAGINE can generate on four widely-used benchmarks, which we use to evaluate reasoning on several families of LLMs.
- Recent Large Language Models (LLMs) have reported high accuracy on reasoning benchmarks.
- The framework is general and can work across reasoning domains, including math, code, and logic.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference. It especially supports our counterfactual testing design.

---

## Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks
**Authors & Year:** Wu et al. (2023)

**Summary:** The impressive performance of recent language models across a wide range of tasks suggests that they possess a degree of abstract reasoning skills. Are these skills general and transferable, or specialized to specific tasks seen during pretraining? To disentangle these effects, we propose an evaluation framework based on “counterfactual” task variants that deviate from the default assumptions underlying standard tasks.

**Key methods/findings**
- To disentangle these effects, we propose an evaluation framework based on “counterfactual” task variants that deviate from the default assumptions underlying standard tasks.
- Acrossa suite of 11 tasks, we observe nontrivial performance on the counterfactual variants, but nevertheless find that performance substantially and consistently degrades compared to the default conditions.
- Are these skills general and transferable, or specialized to specific tasks seen during pretraining?

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference. It especially supports our counterfactual testing design.

---

## Rethinking Benchmark and Contamination with Rephrased Samples
**Authors & Year:** Yang et al. (2023)

**Summary:** Large language models are increasingly trained on all the data ever produced by humans. Many have raised concerns about the trustworthiness of public benchmarks due to potential contamination in pre-training or fine-tuning datasets. While most data decontamination efforts apply string matching (e.g., n-gram overlap) to remove benchmark data, we show that these methods are insufficient, and simple variations of test data (e.g., paraphrasing, translation) can easily bypass these decontamination measures.

**Key methods/findings**
- To address this growing risk, we propose a stronger LLM-based decontamination method and apply it to popular pre-training and fine-tuning datasets, revealing significant previously unknown test overlap.
- Interestingly, we also find such contamination in synthetic dataset generated by GPT-3.5/4, suggesting a potential risk of unintentional contamination.
- Furthermore, we demonstrate that if such variation of test data is not eliminated, a 13B model can easily overfit a test benchmark and achieve drastically high performance, on par with GPT-4.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## Task Contamination: Language Models May Not Be Few-Shot Anymore
**Authors & Year:** Li & Flanigan (2024)

**Summary:** Largelanguagemodels(LLMs)offerimpressiveperformance in various zero-shot and few-shot tasks. However, their success in zero-shot and few-shot settings may be affected by task contamination, a potential limitation that has not been thoroughly examined. This paper investigates how zero-shot and few-shot performance of LLMs has changed chronologically over time.

**Key methods/findings**
- Additionally, we utilize training data inspection, task example extraction, and a membership inference attack, which reveal further evidence of task contamination.
- Utilizing GPT-3 series models and several other recent open-sourced LLMs, and controlling for dataset difficulty, we find that on datasets released before the LLM training data creation date, LLMs perform surprisingly better than on datasets released after.
- This strongly indicates that,formanyLLMs,thereexiststaskcontaminationonzeroshot and few-shot evaluation for datasets released prior to the LLMs’ training data creation date.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.

---

## Time Travel in LLMs: Tracing Contamination Through Language Reconstruction
**Authors & Year:** Golchin & Surdeanu (2024)

**Summary:** Data contamination, i.e., the presence of test data from dow nstream tasks in the training data of large language models (LLMs), is a potentia l major issue in measuring LLMs’ real effectiveness on other tasks. We propose a straightforward yet effective method for identifying data contamination withi n LLMs. At its core, our approach starts by identifying potential contaminatio n at the instance level ; using this information, our approach then assesses wider co ntamination at the partition level .

**Key methods/findings**
- We propose a straightforward yet effective method for identifying data contamination withi n LLMs.
- To und erstand if an entire partition is contaminated, we propose two ideas.
- Our best method ach ieves an accuracy between 92% and 100% in detecting if an LLM is contaminated with seven datasets, containing train and test/validation partitions, when con trasted with manual evaluation by human experts.

**Insight for our project:** This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference. It also maps directly to evidence-intrusion scoring.
