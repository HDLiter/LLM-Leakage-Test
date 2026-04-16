# Paper Index

> **Last sync:** 2026-04-16 (post-R5A-freeze cleanup)
> **Previous sync:** 2026-04-06
> **Total PDFs in `related papers/`:** 128
> **Status legend:** `IN_LIBRARY` = PDF on disk; `REFERENCED_ONLY` = cited in project docs / sweeps but no PDF in `related papers/`.

This index is a **categorical pointer view** for fast navigation. The richer per-paper records (sha256, abstract excerpts, page counts, author guesses) live alongside the PDFs:

- **Per-topic notes:** `related papers/notes/*.md` (ten thematic note files)
- **Machine-readable catalog:** `related papers/notes/_paper_catalog.json` (last machine sync covered ~86 of the 128 files; not authoritative for newest additions)

This file at repo root is the human-facing categorical index that ties paper filenames back to the R5A research design and the v6.2 decision document.

---

## 1. Memorization / extraction foundations

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Secret Sharer Unintended Memorization.pdf` | Carlini et al. 2019 | Canary-based unintended memorization | IN_LIBRARY |
| `Extracting Training Data from LLMs 2020.pdf` | Carlini et al. 2021 | Verbatim extraction from GPT-2 | IN_LIBRARY |
| `Scalable Extraction of Training Data from Language Models.pdf` | Nasr et al. 2023 | Production-LLM extraction (white/semi/black tiers) | IN_LIBRARY |
| `Quantifying Memorization Across Neural LMs.pdf` | Carlini et al. 2023 (ICLR) | Log-linear scaling of memorization with size | IN_LIBRARY |
| `Counterfactual Memorization in Neural Language Models.pdf` | Zhang, Ippolito, Carlini et al. 2021 | Counterfactual memorization definition | IN_LIBRARY |
| `Memorization Without Overfitting.pdf` | Tirumala et al. 2022 | Training dynamics of memorization | IN_LIBRARY |
| `What Neural Networks Memorize Long Tail.pdf` | Feldman / Feldman & Zhang | Long-tail necessity of memorization | IN_LIBRARY |
| `Closer Look at Memorization in Deep Networks.pdf` | Arpit et al. | Empirical look at memorization vs generalization | IN_LIBRARY |
| `Deduplicating Training Data Makes LMs Better.pdf` | Lee et al. 2022 | Dedup reduces memorization | IN_LIBRARY |
| `Detecting Pretraining Data from Large Language Models.pdf` | Shi et al. 2024 (ICLR, Min-K%) | Min-K% Prob + WikiMIA | IN_LIBRARY |
| `Min-K++ Detecting Pretraining Data.pdf` | Zhang et al. 2024/2025 (ICLR) | Per-token calibrated Min-K++ | IN_LIBRARY |
| `Probabilistic Extraction Memorization.pdf` | (extraction-detection variant) | Probabilistic extraction framing | IN_LIBRARY |
| `Pretraining Data Detection Divergence Calibration.pdf` | (Min-K family follow-up) | Divergence-calibrated detection | IN_LIBRARY |
| `Entity-level Memorization in LLMs.pdf` | Zhou et al. 2023 | Entity-level memorization / association leakage | IN_LIBRARY |
| `RAVEN Linguistic Novelty LMs.pdf` | McCoy et al. 2021 (TACL) | Memorization vs novelty in generation | IN_LIBRARY |
| `Japanese Newspaper Memorization PLM.pdf` | Ishihara & Takahashi 2024 (INLG) | Paywalled-news natural non-contamination control | IN_LIBRARY |
| `OWL Cross-Lingual Recall Memorized Texts.pdf` | 2025 | Cross-lingual recall of memorized text | IN_LIBRARY |
| `Cross-Model Memorization Statistical Internal.pdf` | Chen et al. 2026 | 20-model statistical + internal memorization comparison | IN_LIBRARY |
| `Disentangling Memory and Reasoning in LLMs.pdf` | — | Separating memorized from reasoned answers | IN_LIBRARY |
| `Time Encoded in Weights Finetuned LMs.pdf` | — | Time information stored in weights | IN_LIBRARY |
| `Whos Harry Potter Approximate Unlearning LLMs.pdf` | Eldan & Russinovich | Approximate unlearning | IN_LIBRARY |

## 2. MIA family + skepticism

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `MIA Against Machine Learning Models.pdf` | Shokri et al. 2017 | Foundational MIA framework | IN_LIBRARY |
| `MIA From First Principles.pdf` | Carlini et al. 2022 | LiRA / strongest post-Shokri MIA baseline | IN_LIBRARY |
| `Do Membership Inference Attacks Work on Large Language Models.pdf` | Duan et al. 2024 (COLM) | MIA scaling + near-random AUC across domains | IN_LIBRARY |
| `Inherent Challenges Post-Hoc MIA LLMs.pdf` | Meeus et al. 2024 (SaTML 2025, aka "SoK: Rushing Nowhere") | Post-hoc MIA distribution-shift critique | IN_LIBRARY |

## 3. Chronological controls / look-ahead bias

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Dated Data Tracing Knowledge Cutoffs.pdf` | Cheng et al. 2024 | Tracing knowledge cutoffs | IN_LIBRARY |
| `Set the Clock Temporal Alignment LMs.pdf` | Zhao et al. 2024 | Steerable temporal alignment | IN_LIBRARY |
| `Chronologically Consistent Large Language Models.pdf` | He et al. 2025 (ChronoBERT/ChronoGPT) | Chrono-controlled LM family | IN_LIBRARY |
| `DatedGPT Preventing Lookahead Bias.pdf` | Yan et al. 2026 | 12 × 1.3B annual-cutoff GPTs | IN_LIBRARY |
| `Time Machine GPT.pdf` | Drinkall et al. 2024 | Chrono-control precursor | IN_LIBRARY |
| `Lookahead Bias in Pretrained LMs.pdf` | Sarkar & Vafa 2024 | Direct conceptual predecessor | IN_LIBRARY |
| `Caution Ahead Numerical Reasoning Look-ahead.pdf` | Levy 2025 | Numerical reasoning + look-ahead in finance | IN_LIBRARY |
| `A Test of Lookahead Bias in LLM Forecasts.pdf` | Gao, Jiang & Yan 2026 | Lookahead Propensity (LAP) statistical test | IN_LIBRARY |
| `All Leaks Count, Some Count More Interpretable Temporal.pdf` | Zhang et al. 2026 | Shapley-DCLR + TimeSPEC claim-level temporal leakage | IN_LIBRARY |
| `Fake Date Tests LLM Macro Forecasting.pdf` | — 2026 | Fake-date prompt sensitivity test | IN_LIBRARY |
| `Fast Effective Solution Look-ahead Bias LLMs.pdf` | Merchant & Levy 2025 | Inference-time logit adjustment | IN_LIBRARY |
| `Do LLMs Understand Chronology.pdf` | Wongchamcharoen & Glasserman 2025 | Prerequisite for prompt-based chrono control | IN_LIBRARY |
| `RealTime QA.pdf` | Kasai et al. 2022 | Temporal-QA benchmark precursor | IN_LIBRARY |
| StoriesLM (Sarkar 2024, SSRN) | Sarkar 2024 | Time-indexed model family | REFERENCED_ONLY |
| NoLBERT | — | No-leakage BERT variant | REFERENCED_ONLY |
| FINSABER | — | Finance chrono-controlled survey | REFERENCED_ONLY |

## 4. Finance memorization / leakage benchmarks

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `MemGuard-Alpha Memorization Financial Forecasting.pdf` | Roy & Roy 2026 | MCS + CMMD detector framework; closest direct competitor | IN_LIBRARY |
| `Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf` | Li et al. 2025 | FinLake-Bench 2,000 QA memorization audit | IN_LIBRARY |
| `Look-Ahead-Bench Standardized Benchmark.pdf` | Benhenda 2026 | Standardized look-ahead bench for PiT LLMs | IN_LIBRARY |
| `LiveTradeBench Real-World Alpha LLM.pdf` | Yu et al. 2025 | Live-streaming real-world alpha; thinking-mode pair | IN_LIBRARY |
| `Memorization Problem LLMs Economic Forecasts.pdf` | Lopez-Lira, Tang & Zhu 2025 | Selective perfect memory in GPT-4o forecasts | IN_LIBRARY |
| `Lopez-Lira ChatGPT Stock Returns.pdf` | Lopez-Lira & Tang 2024 | LLM headline sentiment predicts returns | IN_LIBRARY |
| `Evaluating LLMs Finance Explicit Bias.pdf` | Kong et al. 2026 | Structural bias framework for finance LLMs | IN_LIBRARY |
| `Your AI, Not Your View The Bias of LLMs in Investment Analysis.pdf` | — | Bias of LLMs in investment analysis | IN_LIBRARY |
| `InvestorBench Financial Decision-Making Agent.pdf` | — | Agent-based financial decision benchmark | IN_LIBRARY |
| `CFinBench Chinese Financial Benchmark.pdf` | Nie et al. 2024 | 50-model Chinese financial capability bench | IN_LIBRARY |
| `LLMFactor Extracting Profitable Factors.pdf` | Wang, Izumi & Sakaji 2024 | LLM factor extraction prompts | IN_LIBRARY |
| `FinDPO Financial Sentiment Preference Optimization.pdf` | — | DPO for financial sentiment | IN_LIBRARY |
| `FinGPT Dissemination-Aware Context-Enriched LLMs.pdf` | — | Dissemination-aware FinGPT | IN_LIBRARY |
| `ECC Analyzer Trading Signal Earnings Calls.pdf` | — | Earnings-call trading-signal analyzer | IN_LIBRARY |
| `Structured Event Representation Stock Return.pdf` | — | Structured event vectors for stock returns | IN_LIBRARY |
| `Fine-Grained Chinese Stock Announcement Events.pdf` | — | Chinese stock announcement event taxonomy | IN_LIBRARY |
| AIs Predictable Memory Financial Analysis | Didisheim, Fraschini & Somoza 2025 (Econ Letters) | GPT-4.1 same-family size scaling for memorization | REFERENCED_ONLY (markdown only: `related papers/AIs Predictable Memory Financial Analysis.md`) |
| Total Recall: Macroeconomic Knowledge in LLMs | — | Macroeconomic memorization audit | REFERENCED_ONLY |

## 5. Counterfactual / perturbation methodology

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `GSM-Symbolic Understanding Reasoning Limits.pdf` | Mirzadeh et al. 2024 | Symbolic perturbation; seeds FinMem-NoOp probe | IN_LIBRARY |
| `Anonymization and Information Loss.pdf` | Wu et al. 2025 | Anonymization tradeoff in finance sentiment | IN_LIBRARY |
| `Assessing Look-Ahead Bias GPT Sentiment.pdf` | Glasserman & Lin 2023 | Look-ahead vs distraction bias separation | IN_LIBRARY |
| `Company-specific Biases Financial Sentiment LLMs.pdf` | Nakagawa et al. 2024 | Entity-name change shifts sentiment | IN_LIBRARY |
| `Reasoning or Reciting Counterfactual Tasks.pdf` | Wu et al. 2023 | Counterfactual tasks separate reasoning from recitation | IN_LIBRARY |
| `RE-IMAGINE Symbolic Benchmark Synthesis.pdf` | — | Symbolic benchmark synthesis | IN_LIBRARY |
| Entity Neutering (Engelberg et al. 2025, SSRN) | — | Identity-stripping for LLM bias mitigation | REFERENCED_ONLY |

## 6. Construct validity / benchmark methodology

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Quantifying Construct Validity LLM Evaluations.pdf` | Kearns 2026 | Latent factor vs scale vs measurement-error | IN_LIBRARY |
| `Construct Validity LLM Nomological Networks.pdf` | Freiesleben 2026 | Nomological-network argument for LLM benchmarks | IN_LIBRARY |
| `Evaluating NLG Metrics Measurement Theory.pdf` | Xiao et al. 2023 (EMNLP) | MTMM + factor analysis for NLP eval | IN_LIBRARY |
| `Structure of LM Capabilities Factor Analysis.pdf` | Burnell et al. 2023 | Factor analysis over 29 LLMs / 27 tasks | IN_LIBRARY |
| `BenchBench Benchmark Agreement.pdf` | Perlitz et al. 2024 | Benchmark-agreement instability | IN_LIBRARY |
| `Multiverse Analysis Fairness Hacking.pdf` | — 2025 | Multiverse analysis prevents fairness hacking | IN_LIBRARY |
| Cronbach & Meehl 1955, *Construct Validity in Psychological Tests* | Cronbach & Meehl 1955 | Foundational construct-validity theory | REFERENCED_ONLY (psychclassics.yorku.ca) |
| Bean et al. 2025, *Measuring What Matters* | Bean et al. 2025 (arxiv 2511.04703) | Systematic review of 445 LLM benchmarks | REFERENCED_ONLY |
| Alzahrani et al. 2024 — *Benchmark Sensitivity* | Alzahrani et al. 2024 (arxiv 2402.01781) | Sensitivity of benchmark scores | REFERENCED_ONLY (note: filename `Alzahrani2024 Benchmark Sensitivity.pdf` is on disk; if present treat as IN_LIBRARY) |

> Note: `Alzahrani2024 Benchmark Sensitivity.pdf` is present on disk -> treat as IN_LIBRARY.

## 7. Contamination detection

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `PaCoST Benchmark Contamination Detection.pdf` | EMNLP 2024 Findings | Paired confidence test | IN_LIBRARY |
| `CLEAN-EVAL Contaminated Language Models.pdf` | — | Cleaning contaminated benchmarks | IN_LIBRARY |
| `VarBench Dynamic Variable Perturbation.pdf` | — | Variable-perturbation bench | IN_LIBRARY |
| `LastingBench Knowledge Leakage.pdf` | — | Knowledge-leakage longitudinal bench | IN_LIBRARY |
| `Time Travel in LLMs Tracing Contamination.pdf` | Golchin & Surdeanu 2024 (ICLR) | Reconstruction-based contamination tracing | IN_LIBRARY |
| `AntiLeakBench Preventing Contamination.pdf` | Wu et al. 2024 (ACL 2025) | Auto-construction of contamination-free bench | IN_LIBRARY |
| `MMLU-CF Contamination-free Benchmark.pdf` | Fang et al. 2025 (ACL) | Contamination-free MMLU variant | IN_LIBRARY |
| `LiveBench A Challenging Contamination-Limited Benchmark.pdf` | White et al. 2024 (ICLR 2025 Spotlight) | Monthly-refreshed bench | IN_LIBRARY |
| `Proving Test Set Contamination Black Box.pdf` | Oren et al. 2024 (ICLR) | Black-box contamination via perturbation | IN_LIBRARY |
| `Task Contamination Not Few-Shot.pdf` | Li & Flanigan 2024 | Benchmark-age effect on apparent few-shot | IN_LIBRARY |
| `Investigating Data Contamination in Modern Benchmarks.pdf` | — | Modern-bench contamination audit | IN_LIBRARY |
| `Generalization or Memorization Data Contamination.pdf` | — 2024 | Generalization-vs-memorization framing | IN_LIBRARY |
| `How Much are LLMs Contaminated LLMSanitize.pdf` | Ravaut et al. 2024 (LLMSanitize) | Survey + 5-model size-matched study | IN_LIBRARY |
| `Rethinking Benchmark and Contamination with Rephrased Samples.pdf` | — 2023 | Rephrased-sample contamination | IN_LIBRARY |
| `Open-Source Data Contamination Report.pdf` | — | Open-source contamination report | IN_LIBRARY |
| `Leak Cheat Repeat Closed-Source LLMs.pdf` | — | Closed-source leak/cheat framing | IN_LIBRARY |
| `Data Contamination Cross Language Barriers.pdf` | — | Cross-lingual contamination | IN_LIBRARY |
| `Publish Benchmark Without Answers.pdf` | — | Answer-withheld benchmark protocol | IN_LIBRARY |
| `Benchmarking LLMs Data Contamination Static Dynamic.pdf` | Chen et al. 2025 (EMNLP) | Static-to-dynamic contamination survey | IN_LIBRARY |
| `Leakage Reproducibility Crisis ML Science.pdf` | Kapoor & Narayanan 2023 | Leakage as reproducibility crisis | IN_LIBRARY |
| `LLM Reproducibility Crisis Survey.pdf` | 2024 | LLM reproducibility crisis survey | IN_LIBRARY |

## 8. Cross-model / cross-fleet memorization

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Cross-Model Memorization Statistical Internal.pdf` | Chen 2026 | 20-model statistical + internal-level analysis | IN_LIBRARY (also listed in §1) |
| `OWL Cross-Lingual Recall Memorized Texts.pdf` | 2025 | 11-model cross-lingual recall | IN_LIBRARY (also listed in §1) |
| (See `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md` for the full 25-paper fleet-design review) | — | Fleet-design literature synthesis | doc-only |

## 9. Mechanistic interpretability — knowledge storage / retrieval

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Dissecting Recall Factual Associations.pdf` | Geva et al. 2023 | 3-step factual recall | IN_LIBRARY |
| `FFN Key-Value Memories Transformers.pdf` | Geva et al. 2021 | FFN as key-value memories | IN_LIBRARY |
| `ROME Locating Editing Factual Associations GPT.pdf` | Meng et al. 2022 | Locating + editing facts | IN_LIBRARY |
| `MEMIT Mass-Editing Memory Transformer.pdf` | Meng et al. 2023 | Mass-editing facts | IN_LIBRARY |
| `Knowledge Neurons Pretrained Transformers.pdf` | Dai et al. 2022 | Knowledge neurons | IN_LIBRARY |
| `Does Localization Inform Editing.pdf` | Hase et al. 2023 | Edit success ≠ correct localization | IN_LIBRARY |
| `MQuAKE Knowledge Editing Multi-Hop.pdf` | Zhong et al. 2023 | Multi-hop edit propagation failure | IN_LIBRARY |
| `Propagation Pitfalls Knowledge Editing.pdf` | Hua et al. 2024 | Editing fails on reasoning chains | IN_LIBRARY |
| `MIRAGE Model Internals Answer Attribution.pdf` | — | Internals-based answer attribution | IN_LIBRARY |
| `TRAK Attributing Model Behavior at Scale.pdf` | Park et al. 2023 | Training-data attribution at scale | IN_LIBRARY |

## 10. Entity representation, temporal latents, knowledge conflicts

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Entity Identification Language Models.pdf` | Sakata et al. 2025 | Early-layer entity subspace | IN_LIBRARY |
| `Entity Cells Language Models.pdf` | Yona et al. 2026 | Entity-selective neurons | IN_LIBRARY |
| `Causal View Entity Bias LLMs.pdf` | Wang et al. 2023 | Entity-bound parametric shortcuts | IN_LIBRARY |
| `Co-occurrence Not Factual Association.pdf` | Zhang et al. 2024 | Co-occurrence ≠ factual association | IN_LIBRARY |
| `Entity Knowledge Conflicts QA.pdf` | Longpre et al. 2021 | Context-vs-parametric memory conflicts | IN_LIBRARY |
| `Cutting Off Head Knowledge Conflicts.pdf` | Jin et al. 2024 | Memory vs context heads | IN_LIBRARY |
| `Taming Knowledge Conflicts LMs.pdf` | Li et al. 2025 | Memory/context head superposition | IN_LIBRARY |
| `Mechanistic Circuits Extractive QA.pdf` | Basu et al. 2025 | Context vs memory circuits | IN_LIBRARY |
| `Context-faithful Prompting for LLMs.pdf` | Zhou et al. 2023 | Context-vs-memory prompting | IN_LIBRARY |
| `Context-Faithfulness Memory Strength Evidence.pdf` | — | Memory-strength evidence | IN_LIBRARY |
| `How Well Do LLMs Truly Ground.pdf` | Lee et al. 2024 | Grounding = use + stay-within | IN_LIBRARY |
| `Language Models Represent Space Time.pdf` | Gurnee & Tegmark 2024 | Time as linearly decodable latent | IN_LIBRARY |

## 11. Cognitive science: memory systems / LLM analogies

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Episodic Memories Benchmark LLMs.pdf` | Huet et al. 2025 | Episodic memory benchmark for LLMs | IN_LIBRARY |
| `Memory GAPS Tulving Test LLMs.pdf` | Chauvet 2024 | Tulving test framework on LLMs | IN_LIBRARY |
| `Memory Traces Transformers Tulving.pdf` | Chauvet 2024 | Tulving-Watkins on transformer memory traces | IN_LIBRARY |
| Tulving (1972, 1993, 2002) — episodic / semantic memory | — | Foundational psychology | REFERENCED_ONLY |
| Johnson, Hashtroudi & Lindsay 1993 — source monitoring | — | Source monitoring | REFERENCED_ONLY |
| Johnson & Raye 1981 — reality monitoring | — | Reality monitoring | REFERENCED_ONLY |
| McClelland, McNaughton & O'Reilly 1995 — Complementary Learning Systems | — | CLS theory | REFERENCED_ONLY |
| Tversky & Kahneman 1973, 1974 — availability / judgment | — | Heuristics & biases | REFERENCED_ONLY |
| Addis & Szpunar 2024 — MMMR | — | Multidimensional model | REFERENCED_ONLY |
| Spens & Burgess 2024 — generative memory model | — | Generative memory construction | REFERENCED_ONLY |
| Dong, Lu, Norman & Michelmann 2025 — LLMs with episodic memory | — | LLMs + human-like episodic memory | REFERENCED_ONLY |

## 12. Calibration, robustness, uncertainty

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Kernel Language Entropy Uncertainty Quantification.pdf` | — | Kernel language entropy for UQ | IN_LIBRARY |
| `BaseCal Unsupervised Confidence Calibration.pdf` | Tan et al. 2026 | Base-LLM-anchored calibration | IN_LIBRARY |
| `Towards Objective Fine-tuning Calibration.pdf` | — | Objective-based fine-tune calibration | IN_LIBRARY |
| `Interpretable Probability Estimation Shapley.pdf` | — | Shapley-based probability estimation | IN_LIBRARY |
| `Anchor Regression Heterogeneous Causality.pdf` | Rothenhausler et al. 2021 | Anchor regression for distribution stability | IN_LIBRARY |
| `Stable Prediction Unknown Environments.pdf` | — | Distributionally stable prediction | IN_LIBRARY |
| `Invariant Risk Minimization.pdf` | Arjovsky et al. | IRM | IN_LIBRARY |

## 13. Grounding, RAG, hallucination

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `MiniCheck Efficient Fact-Checking Grounding.pdf` | Tang, Laban & Durrett 2024 | Efficient grounding fact-check | IN_LIBRARY |
| `ReEval Hallucination Evaluation RAG.pdf` | Yu et al. 2023 | Hallucination eval for RAG | IN_LIBRARY |
| `Chain-of-Note Enhancing RAG Robustness.pdf` | Yu et al. 2024 | Chain-of-note RAG robustness | IN_LIBRARY |
| `Chain-of-Verification Reduces Hallucination.pdf` | Dhuliawala et al. 2023 | Verification chains | IN_LIBRARY |

## 14. Prompting, reasoning, rationalization

| Filename | Authors / Year | Key contribution | Status |
|---|---|---|---|
| `Rationalizing Neural Predictions.pdf` | Lei et al. 2016 | Extractive rationale generation | IN_LIBRARY |
| `Unfaithful Explanations in CoT.pdf` | Turpin et al. 2023 | CoT explanations can be unfaithful | IN_LIBRARY |
| `Least-to-Most Prompting Complex Reasoning.pdf` | Zhou et al. 2023 | Decomposition-based prompting | IN_LIBRARY |
| `CHiLL Zero-Shot Feature Extraction Clinical.pdf` | McInerney et al. | LLM-extract → ML-aggregate pattern | IN_LIBRARY |

## 15. Adjacent / background (cited in project docs)

| Reference | Where used | Status |
|---|---|---|
| Tetlock 2007 — *Giving Content to Investor Sentiment* | Chrono / look-ahead provenance | REFERENCED_ONLY |
| Tetlock, Saar-Tsechansky & Macskassy 2008 — *More Than Words* | Chrono / look-ahead provenance | REFERENCED_ONLY |
| Ke, Kelly & Xiu 2019 — *Predicting Returns with Text Data* | Chrono / look-ahead provenance | REFERENCED_ONLY |
| Boukes & Vliegenthart 2020 — *Economic Newsworthiness* | Construct-validity sweep (E) | REFERENCED_ONLY |
| Kasai et al. 2022 — *RealTime QA* (also listed in §3) | Temporal-QA precursor | IN_LIBRARY |
| Yeom et al. 2017 — *Privacy Risk in ML* | MIA ancestry | REFERENCED_ONLY |
| Fredrikson et al. 2015 — *Model Inversion* | MIA ancestry | REFERENCED_ONLY |
| Ludwig, Mullainathan & Rambachan — *LLMs: Applied Econometric Framework* (NBER w33344) | Finance methodology | REFERENCED_ONLY |
| BloombergGPT, FinanceBench, Financial Statement Analysis with LLMs | Finance background | REFERENCED_ONLY |

---

## Cross-reference: which papers ground which R5A estimands

(Ties the index back to `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`.)

| R5A confirmatory estimand | Anchor papers in library |
|---|---|
| **E_CMMD** (cross-model disagreement) | MemGuard-Alpha, AntiLeakBench, MMLU-CF, LiveBench, Cross-Model Memorization Statistical Internal, FLEET_SELECTION_LITERATURE.md |
| **E_PCSG** (paired cutoff surprise gap) | Detecting Pretraining Data (Min-K%), Min-K++, Quantifying Memorization, MIA From First Principles, Inherent Challenges Post-Hoc MIA |
| **E_CTS** (calibrated tail surprise) | Min-K++, Pretraining Data Detection Divergence Calibration, Probabilistic Extraction Memorization |
| **E_FO** (false-outcome resistance) | Reasoning or Reciting Counterfactual Tasks, GSM-Symbolic, Assessing Look-Ahead Bias GPT Sentiment, Anonymization and Information Loss |
| **E_NoOp** (NoOp clutter sensitivity) | GSM-Symbolic, RE-IMAGINE Symbolic Benchmark Synthesis, RAVEN Linguistic Novelty LMs |
| **E_extract** (masked span extraction, reserve) | Extracting Training Data 2020, Scalable Extraction, Probabilistic Extraction Memorization, Entity-level Memorization, OWL Cross-Lingual Recall |
| **E_EAD_t / E_EAD_nt** (entity anonymization, exploratory) | Anonymization and Information Loss, Company-specific Biases Financial Sentiment LLMs, Assessing Look-Ahead Bias GPT Sentiment, Causal View Entity Bias LLMs, Entity Cells, Entity Identification |
| **E_TDR** (temporal dose × cutoff interaction) | Dated Data, Set the Clock, Time Machine GPT, DatedGPT, Chronologically Consistent LLMs, Lookahead Bias in Pretrained LMs, Caution Ahead, Do LLMs Understand Chronology, A Test of Lookahead Bias, Fast Effective Solution Look-ahead Bias, Fake Date Tests, All Leaks Count Some Count More |
| **E_ADG** (as-of-date prompt gating) | Do LLMs Understand Chronology, Set the Clock, Memorization Problem LLMs Economic Forecasts |
| **Construct validity / framework** | Quantifying Construct Validity LLM Evaluations, Construct Validity LLM Nomological Networks, Evaluating NLG Metrics Measurement Theory, Structure of LM Capabilities Factor Analysis, BenchBench Benchmark Agreement |

---

## Footer

**Last sync:** 2026-04-16 (post-R5A-freeze cleanup).
**Previous sync:** 2026-04-06.

**What changed since 2026-04-06:**
- Total PDFs grew from 60 -> 128 (+68 net of dedupe). Most additions came from the **R4 literature sweep Sessions 1 + 2** (~25 papers added 2026-04-14/15: MIA foundations + skepticism, chrono-control precursors, look-ahead-bench family, finance memorization papers, construct-validity stack) and from the **R5A fleet review** (cross-model + cross-fleet contamination & memorization comparators).
- New top-level categories: **MIA family + skepticism** (§2), **Chronological controls / look-ahead bias** (§3), **Finance memorization / leakage benchmarks** (§4, expanded), **Counterfactual / perturbation methodology** (§5), **Construct validity / benchmark methodology** (§6), **Cross-model / cross-fleet memorization** (§8).
- Existing "Memorization, Contamination & Data Extraction" was split into §1 (foundations) + §7 (contamination detection) + §2 (MIA) for clarity.
- Added cross-reference table tying papers to R5A confirmatory + exploratory estimands defined in `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`.
- The previous "Not Yet Downloaded" section is folded into per-category `REFERENCED_ONLY` rows.

**Source documents consulted for this sync:**
- `refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md`
- `refine-logs/reviews/R5A_FLEET_REVIEW/FLEET_SELECTION_LITERATURE.md`
- `refine-logs/reviews/LIT_SWEEP_DOWNLOAD_SUMMARY.md`
- `archive/r4_r5a_lineage/refine-logs/reviews/BENCHMARK_R5_KICKOFF.md`
- `archive/r4_r5a_lineage/refine-logs/reviews/LIT_SWEEP_D_CITED_BUT_UNREAD.md`
- `archive/r4_r5a_lineage/refine-logs/reviews/LIT_SWEEP_E_CONSTRUCT_VALIDATION.md`
- `related papers/notes/_paper_catalog.json` (machine catalog, 86 entries — partially stale vs 128 PDFs on disk)
- Filesystem listing of `related papers/*.pdf` (128 files, sorted alphabetically)
