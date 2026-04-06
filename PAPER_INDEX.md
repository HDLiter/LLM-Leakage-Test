# Paper Index

> Last updated: 2026-04-06
> Total: 60 PDFs (34 pre-existing + 26 newly downloaded)
> Newly downloaded papers marked with [NEW]

---

## 1. Memorization, Contamination & Data Extraction

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Extracting Training Data from LLMs 2020.pdf | Carlini et al. | 2021 | Verbatim training data extraction from GPT-2 |
| Extracting Training Data from LLMs.pdf | Nasr et al. | 2023 | Scalable extraction from production LLMs |
| Secret Sharer Unintended Memorization.pdf | Carlini et al. | 2019 | Canary-based unintended memorization detection |
| [NEW] Counterfactual Memorization Neural LMs.pdf | Zhang, Ippolito, Carlini et al. | 2021 | Counterfactual memorization: behavior change when document removed |
| Entity-level Memorization in LLMs.pdf | Zhou et al. | 2023 | Entity-level memorization and entity-association leakage |
| [NEW] Causal View Entity Bias LLMs.pdf | Wang et al. | 2023 | Entity-bound parametric shortcuts cause unfaithful predictions |
| [NEW] Co-occurrence Not Factual Association.pdf | Zhang et al. | 2024 | Co-occurrence statistics ≠ true factual associations; different mechanisms |
| TRAK Attributing Model Behavior at Scale.pdf | Park et al. | 2023 | Training data attribution at scale |
| TRAK Attributing Model Behavior.pdf | Park et al. | 2023 | (Duplicate/variant) |

## 2. Contamination Detection & Benchmark Integrity

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Proving Test Set Contamination Black Box.pdf | Oren et al. | 2024 | Black-box contamination detection via perturbation |
| Time Travel in LLMs Tracing Contamination.pdf | Golchin & Surdeanu | 2024 | Reconstruction-based contamination tracing |
| Task Contamination Language Models Not Few-Shot.pdf | Li & Flanigan | 2024 | Benchmark age affects apparent few-shot ability |
| AntiLeakBench Preventing Data Contamination.pdf | Wu et al. | 2024 | Fresh benchmark construction to limit contamination |
| MMLU-CF Contamination-free Benchmark.pdf | Fang et al. | 2025 | Contamination-free MMLU variant |
| MMLU-CF Contamination-free.pdf | Fang et al. | 2025 | (Duplicate/variant) |
| Dated Data Tracing Knowledge Cutoffs.pdf | Cheng et al. | 2024 | Temporal knowledge cutoff tracing |
| Reasoning or Reciting Counterfactual Tasks.pdf | Wu et al. | 2023 | Counterfactual tasks separate reasoning from recitation |
| Leakage Reproducibility Crisis ML Science.pdf | Kapoor & Narayanan | 2023 | Leakage as a reproducibility crisis in ML |

## 3. LLM Financial NLP & Look-Ahead Bias

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Lopez-Lira ChatGPT Stock Returns.pdf | Lopez-Lira & Tang | 2024 | LLM headline sentiment predicts returns |
| Memorization Problem LLMs Economic Forecasts.pdf | Lopez-Lira, Tang & Zhu | 2025 | Selective perfect memory in LLM economic forecasts |
| [NEW] Assessing Look-Ahead Bias GPT Sentiment.pdf | Glasserman & Lin | 2024 | Look-ahead bias + distraction effect in GPT sentiment |
| [NEW] Test Lookahead Bias LLM Forecasts LAP.pdf | — | 2025 | Lookahead Propensity (LAP) metric |
| [NEW] Fake Date Tests LLM Macro Forecasting.pdf | — | 2026 | Fake date/prompt sensitivity to detect future knowledge |
| [NEW] Look-Ahead-Bench Finance LLMs.pdf | — | 2026 | Standardized look-ahead bias benchmark for finance LLMs |
| [NEW] Company-specific Biases Financial Sentiment LLMs.pdf | — | 2024 | Company name changes LLM sentiment — entity prior evidence |
| LLMFactor Extracting Profitable Factors.pdf | Wang, Izumi & Sakaji | 2024 | Extracting factors via LLM prompts |
| CFinBench Chinese Financial Benchmark.pdf | Nie et al. | 2024 | Chinese financial LLM benchmark |

## 4. Context-Faithfulness, Grounding & Knowledge Conflicts

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Context-faithful Prompting for LLMs.pdf | Zhou et al. | 2023 | Prompting changes context vs memory reliance |
| How Well Do LLMs Truly Ground.pdf | Lee et al. | 2024 | Grounding = using + staying within context |
| [NEW] Entity Knowledge Conflicts QA.pdf | Longpre et al. | 2021 | Context vs parametric memory conflict framework |
| [NEW] Cutting Off Head Knowledge Conflicts.pdf | Jin et al. | 2024 | Memory heads vs context heads in LMs |
| [NEW] Taming Knowledge Conflicts LMs.pdf | Li et al. | 2025 | Memory/context heads show superposition, not clean separation |
| [NEW] Mechanistic Circuits Extractive QA.pdf | Basu et al. | 2025 | Context-faithfulness circuit vs memory-faithfulness circuit |
| MiniCheck Efficient Fact-Checking Grounding.pdf | Tang, Laban & Durrett | 2024 | Fact-checking on grounding documents |
| MiniCheck Fact-Checking Grounding.pdf | Tang, Laban & Durrett | 2024 | (Duplicate/variant) |
| ReEval Hallucination Evaluation RAG.pdf | Yu et al. | 2023 | Hallucination evaluation for RAG |
| Chain-of-Note Enhancing RAG Robustness.pdf | Yu et al. | 2024 | RAG robustness via chain-of-note |
| Chain-of-Verification Reduces Hallucination.pdf | Dhuliawala et al. | 2023 | Verification chains reduce hallucination |

## 5. Mechanistic Interpretability: Knowledge Storage & Retrieval

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Dissecting Recall of Factual Associations.pdf | Geva et al. | 2023 | 3-step factual recall: subject enrichment → relation propagation → attribute extraction |
| [NEW] FFN Key-Value Memories Transformers.pdf | Geva et al. | 2021 | FFN layers as key-value memories |
| [NEW] ROME Locating Editing Factual Associations.pdf | Meng et al. | 2022 | Locating and editing facts in mid-layer MLPs |
| [NEW] MEMIT Mass-Editing Memory Transformer.pdf | Meng et al. | 2023 | Mass-editing multiple facts simultaneously |
| [NEW] Knowledge Neurons Pretrained Transformers.pdf | Dai et al. | 2022 | Knowledge neurons in pretrained transformers |
| [NEW] Does Localization Inform Editing.pdf | Hase et al. | 2023 | Edit success ≠ correct localization |
| [NEW] MQuAKE Knowledge Editing Multi-Hop.pdf | Zhong et al. | 2023 | Single fact edits don't propagate to multi-hop reasoning |
| [NEW] Propagation Pitfalls Knowledge Editing.pdf | Hua et al. | 2024 | Knowledge editing fails on reasoning chains |
| MIRAGE Model Internals Answer Attribution.pdf | — | — | Model internals for answer attribution |
| MIRAGE Model Internals Attribution.pdf | — | — | (Duplicate/variant) |

## 6. Entity Representation & Temporal Knowledge

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| [NEW] Entity Identification Language Models.pdf | Sakata et al. | 2025 | Entity info in early-layer low-dim linear subspace |
| [NEW] Entity Cells Language Models.pdf | Yona et al. | 2026 | Entity-selective neurons; ablation → entity-specific amnesia |
| [NEW] Language Models Represent Space Time.pdf | Gurnee & Tegmark | 2024 | Time as linearly decodable continuous latent variable; time neurons |
| [NEW] Set the Clock Temporal Alignment LMs.pdf | Zhao et al. | 2024 | LMs biased toward earlier knowledge; time as steerable latent state |

## 7. Cognitive Science: Memory Systems & LLM Analogies

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| [NEW] Episodic Memories Benchmark LLMs.pdf | Huet et al. | 2025 | Episodic memory benchmark with temporal/entity/confabulation tests |
| [NEW] Memory GAPS Tulving Test LLMs.pdf | Chauvet | 2024 | Applying Tulving's test framework to LLMs |
| [NEW] Memory Traces Transformers Tulving.pdf | Chauvet | 2024 | Tulving-Watkins experiments on transformer memory traces |

## 8. Prompting, Reasoning & Rationalization

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Rationalizing Neural Predictions.pdf | Lei et al. | 2016 | Extractive rationale generation |
| Unfaithful Explanations in CoT.pdf | Turpin et al. | 2023 | CoT explanations can be unfaithful |
| Least-to-Most Prompting Complex Reasoning.pdf | Zhou et al. | 2023 | Decomposition-based prompting |
| CHiLL Zero-Shot Feature Extraction Clinical.pdf | McInerney et al. | — | LLM extract → ML aggregate pattern |

## 9. Causal Inference & Robustness

| File | Authors | Year | Key Contribution |
|------|---------|------|-----------------|
| Anchor Regression Heterogeneous Causality.pdf | Rothenhausler et al. | 2021 | Anchor regression for distribution stability |

---

## Not Yet Downloaded (Non-ArXiv, Manual Download Needed)

### Cognitive Psychology Classics
- Tulving (1972) *Episodic and semantic memory* — book chapter
- Tulving (1993) *What Is Episodic Memory?* — journal
- Tulving (2002) *Episodic Memory: From Mind to Brain* — Annual Reviews
- Johnson, Hashtroudi & Lindsay (1993) *Source monitoring* — Psychological Bulletin
- Johnson & Raye (1981) *Reality Monitoring* — Psychological Review
- Simons et al. (2017) *Brain Mechanisms of Reality Monitoring* — TICS
- McClelland, McNaughton & O'Reilly (1995) *Complementary Learning Systems* — Psych Review
- Tversky & Kahneman (1973) *Availability heuristic* — Cognitive Psychology
- Tversky & Kahneman (1974) *Judgment under Uncertainty* — Science
- Addis & Szpunar (2024) *Multidimensional model of mental representations (MMMR)* — PMC
- Spens & Burgess (2024) *Generative model of memory construction* — Nature Human Behaviour
- Dong, Lu, Norman & Michelmann (2025) *LLMs with human-like episodic memory* — TICS

### Finance / Economics
- Ludwig, Mullainathan & Rambachan — *LLMs: An Applied Econometric Framework* — NBER w33344
- He et al. (2025) — *Chronologically Consistent LLMs* — SSRN 5348747

---

## Category Cross-Reference for Project

### Directly supports Type A/B memory taxonomy
- Counterfactual Memorization Neural LMs.pdf
- Co-occurrence Not Factual Association.pdf
- Episodic Memories Benchmark LLMs.pdf
- Memory GAPS Tulving Test LLMs.pdf

### Directly supports entity-prior leakage channel
- Causal View Entity Bias LLMs.pdf
- Entity-level Memorization in LLMs.pdf
- Company-specific Biases Financial Sentiment LLMs.pdf
- Entity Cells Language Models.pdf
- Entity Identification Language Models.pdf

### Directly supports event-outcome leakage channel
- Assessing Look-Ahead Bias GPT Sentiment.pdf
- Memorization Problem LLMs Economic Forecasts.pdf
- Test Lookahead Bias LLM Forecasts LAP.pdf
- Fake Date Tests LLM Macro Forecasting.pdf
- Look-Ahead-Bench Finance LLMs.pdf

### Directly supports context vs memory competition
- Context-faithful Prompting for LLMs.pdf
- Entity Knowledge Conflicts QA.pdf
- Cutting Off Head Knowledge Conflicts.pdf
- Taming Knowledge Conflicts LMs.pdf
- Mechanistic Circuits Extractive QA.pdf

### Directly supports temporal leakage mechanism
- Language Models Represent Space Time.pdf
- Set the Clock Temporal Alignment LMs.pdf
- Dated Data Tracing Knowledge Cutoffs.pdf

### Supports knowledge storage mechanism understanding
- Dissecting Recall of Factual Associations.pdf
- FFN Key-Value Memories Transformers.pdf
- ROME Locating Editing Factual Associations.pdf
- Knowledge Neurons Pretrained Transformers.pdf
- MEMIT Mass-Editing Memory Transformer.pdf
- Does Localization Inform Editing.pdf
- MQuAKE Knowledge Editing Multi-Hop.pdf
- Propagation Pitfalls Knowledge Editing.pdf
