# Paper Index

> Last updated: 2026-04-05. Papers organized by research angle.

## A. Financial Leakage (Core Domain)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| A1 | Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents | Li et al. | 2025 | arXiv:2510.07920 | FinLakeBench + FactFin counterfactual framework; 50-72% return decay post-cutoff | ✅ Local |
| A2 | All Leaks Count, Some Count More: Interpretable Temporal Contamination Detection | Zhang, Chen, Stadie | 2026 | arXiv:2602.17234 | Shapley-DCLR claim-level leakage + TimeSPEC mitigation | ✅ Local |
| A3 | A Test of Lookahead Bias in LLM Forecasts | Gao, Jiang, Yan | 2026 | arXiv:2512.23847 | LAP = Min-K% Prob for financial forecasting; statistical test for look-ahead bias | ✅ Local |
| A4 | Your AI, Not Your View: The Bias of LLMs in Investment Analysis | Lee et al. | 2025 | arXiv:2507.20957 | Knowledge conflict / confirmation bias in LLM investment analysis | ✅ Local |
| A5 | Look-Ahead-Bench: Standardized Benchmark of Look-ahead Bias | Benhenda | 2026 | arXiv:2601.13770 | Finance-specific benchmark measuring alpha decay and behavioral look-ahead bias | ✅ Local |
| A6 | DatedGPT: Preventing Lookahead Bias with Time-Aware Pretraining | Yan et al. | 2026 | arXiv:2603.11838 | Date-bounded LLMs with strict annual cutoffs as gold-standard baseline | ✅ Local |
| A7 | FinDPO: Financial Sentiment via Preference Optimization | Iacovides et al. | 2025 | arXiv:2507.18417 | SFT over-memorizes financial sentiment; DPO improves OOS trading performance | ✅ Local |

## B. Detection Methods (Contamination / MIA)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| B1 | Detecting Pretraining Data from LLMs (Min-K% Prob) | Shi et al. | 2024 | ICLR 2024 | Reference-free MIA: avg log-likelihood of k% lowest-prob tokens | ✅ Local |
| B2 | Min-K%++ | Zhang et al. | 2025 | ICLR 2025 | Calibrated scoring improving Min-K% without reference model | ❌ No PDF |
| B3 | Generalization or Memorization: CDD/TED | Dong et al. | 2024 | ACL 2024 Findings | Black-box output distribution peakedness detection + correction | ✅ Local |
| B4 | How Much are LLMs Contaminated? LLMSanitize | Ravaut et al. | 2024 | TMLR 2025 | Unified Python library for contamination detection | ✅ Local |
| B5 | Investigating Data Contamination: TS-Guessing | Deng et al. | 2024 | NAACL 2024 | Slot-guessing contamination detection | ✅ Local |
| B6 | Do MIAs Work on LLMs? (MIMIR) | Duan et al. | 2024 | COLM 2024 | MIAs barely beat random on pretraining; MIMIR benchmark | ✅ Local |
| B7 | Rethinking Benchmark and Contamination with Rephrased Samples | Yang et al. | 2023 | arXiv:2311.04850 | Paraphrasing bypasses decontamination; LLM-based decontamination | ✅ Local |
| B8 | Scalable Extraction of Training Data | Carlini et al. | 2023 | arXiv:2311.17035 | Divergence attack; extracts GBs of training data from production LLMs | ✅ Local |

## C. Task Design / Prompt & Memorization Interaction (NEW - Round 2)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| C1 | ALPACA AGAINST VICUNA: Using LLMs to Uncover Memorization | Kassem et al. | 2025 | NAACL 2025 | Instruction-tuning and prompt optimization increase memorization exposure by 23.7% | ❌ No PDF |
| C2 | Unlocking Memorization with Dynamic Soft Prompting | Wang et al. | 2024 | EMNLP 2024 | Input-adaptive soft prompts amplify memorized content extraction | ❌ No PDF |
| C3 | Memorization ≠ Understanding: Scenario Cognition | Ma et al. | 2025 | EMNLP 2025 | Benchmark separating surface recall from contextual understanding | ❌ No PDF |
| C4 | A Multi-Perspective Analysis of Memorization in LLMs | Chen et al. | 2024 | EMNLP 2024 | Entropy changes around memorized spans; multi-perspective memorization analysis | ❌ No PDF |
| C5 | Measuring Memorization via Probabilistic Extraction | Hayes et al. | 2025 | NAACL 2025 | Probability-of-extraction replaces binary memorization measure | ❌ No PDF |

## D. Calibration / Entropy / Confidence Signals (NEW - Round 2)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| D1 | Towards Objective Fine-tuning: Prior Knowledge & Calibration | Wang et al. | 2025 | arXiv:2505.20903 | Pretraining-finetuning overlap induces overconfidence | ✅ Local |
| D2 | BaseCal: Unsupervised Confidence Calibration | Tan et al. | 2026 | arXiv:2601.03042 | Calibrates via base model reference; reduces ECE without labels | ✅ Local |
| D3 | Interpretable Probability Estimation via Shapley Reconstruction | Nan et al. | 2026 | arXiv:2601.09151 | Decomposes LLM probability into factor-level Shapley contributions | ✅ Local |
| D4 | Kernel Language Entropy | Nikitin et al. | 2024 | arXiv:2405.20003 | Kernelized semantic uncertainty measure for LLM outputs | ✅ Local |
| D5 | Cross-Layer Entropy for Decoding Factuality | Wu et al. | 2025 | NAACL 2025 Findings | Cross-layer entropy favors tokens with factual support | ❌ No PDF |
| D6 | Context Copying Modulation: Entropy Neurons | Tighidet et al. | 2025 | EMNLP 2025 Findings | "Entropy neurons" manage parametric vs contextual knowledge conflicts | ❌ No PDF |

## E. Financial Factor Decomposition (NEW - Round 2)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| E1 | Mental Models and Financial Forecasts | Bastianello et al. | 2024 | SSRN:5004839 | Multi-step LLM prompting extracts topic, valuation channel, time horizon, sentiment from analyst reports | ❌ No PDF |
| E2 | Structured Event Representation and Stock Return Predictability | Li et al. | 2025 | arXiv:2512.19484 | LLM-extracted structured event features for return prediction | ✅ Local |
| E3 | ECC Analyzer: Trading Signal from Earnings Calls | Cao et al. | 2024 | arXiv:2404.18470 | Hierarchical LLM extraction from earnings calls | ✅ Local |
| E4 | LLM Non-Responses in Earnings Calls → Analyst Forecasts | Liang et al. | 2025 | arXiv:2505.18419 | Three-step prompting extracts "non-response" signals | ❌ No PDF |

## F. Counterfactual Evaluation & Benchmark Design (NEW - Round 2)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| F1 | Fin-Force: Forward Counterfactual Generation Benchmark | Ong et al. | 2025 | EMNLP 2025 | Benchmark for forward counterfactual generation from financial news | ❌ No PDF |
| F2 | RE-IMAGINE: Symbolic Benchmark Synthesis for Reasoning | Xu et al. | 2025 | arXiv:2506.15455 | Controlled benchmark variants that cannot be solved by memorization | ✅ Local |
| F3 | PhantomWiki: On-Demand Datasets for Reasoning Evaluation | Gong et al. | 2025 | ICML 2025 | Synthetic corpora on demand to avoid contamination | ❌ No PDF |
| F4 | LiveBench: Contamination-Limited LLM Benchmark | White et al. | 2024 | arXiv:2406.19314 | Monthly-updated benchmark from recent data | ✅ Local |

## G. Pipeline Leakage / Contamination Propagation (NEW - Round 2)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| G1 | LeakageDetector 2.0: Data Leakage in ML Pipelines | Truong et al. | 2025 | arXiv:2509.15971 | Detects overlap/preprocessing/multi-test leakage in notebook ML pipelines | ❌ No PDF |
| G2 | VMDNet: Leakage-Free Samplewise Decomposition for Forecasting | Feng et al. | 2025 | arXiv:2509.15394 | Decomposition-based pipelines can leak future info unless done sample-wise | ❌ No PDF |

## H. Surveys (Background)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| H1 | Benchmark Data Contamination: A Survey | Xu et al. | 2024 | arXiv:2406.04244 | Contamination taxonomy and detection methods | ❌ No PDF |
| H2 | Unveiling the Spectrum of Data Contamination | Li et al. (Yale) | 2024 | ACL 2024 Findings | Detection to remediation taxonomy | ❌ No PDF |
| H3 | Static to Dynamic Evaluation | — | 2025 | EMNLP 2025 | Dynamic benchmarking paradigm survey | ❌ No PDF |

---

## Priority Reading by Research Angle

### For Leakage Spectrum Hypothesis
Must-read: C1 (prompt form changes leakage), C3 (memorization ≠ understanding), E2 (structured event features), A7 (SFT over-memorizes)

### For Entropy / Calibration as Leakage Signal
Must-read: D1 (prior knowledge → overconfidence), D4 (kernel entropy), C4 (entropy around memorized spans), D6 (entropy neurons)

### For Contamination Propagation
Must-read: G2 (decomposition leaks future info), G1 (ML pipeline leakage), A6 (DatedGPT as clean baseline)

### For Counterfactual Design
Must-read: F1 (Fin-Force), F2 (RE-IMAGINE sham control), A5 (Look-Ahead-Bench)

### For Financial Factor Decomposition
Must-read: E1 (mental models), E2 (structured events), E3 (ECC Analyzer), E4 (non-response signals)

---

## I. Cross-Disciplinary (Round 3 — Divergent Search)

### Cognitive Science / Memory–Reasoning Separation

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I1 | Disentangling Memory and Reasoning Ability in LLMs | Jin et al. | 2025 | ACL 2025 | Evaluation framework separating memory-driven vs reasoning-driven performance | ✅ Local |
| I2 | A Closer Look at Memorization in Deep Networks | Arpit et al. | 2017 | ICML 2017 | Distinguishes pattern learning from instance memorization via training dynamics | ✅ Local |

### Psychometrics / Item Response Theory

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I3 | Building Evaluation Scales using Item Response Theory | Lalor, Wu, Yu | 2016 | EMNLP 2016 | IRT for NLP benchmark item difficulty/discrimination estimation | ❌ No PDF |
| I4 | Comparing Test Sets with Item Response Theory | Vania et al. | 2021 | ACL-IJCNLP 2021 | Latent difficulty profiles for benchmark comparison | ❌ No PDF |
| I5 | DIF via Logistic Regression | Swaminathan & Rogers | 1990 | J. Edu. Measurement | Classic DIF method for detecting item bias across groups | ❌ No PDF |

### Knowledge Editing / Unlearning (Causal Probes)

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I6 | ROME: Locating and Editing Factual Associations in GPT | Meng et al. | 2022 | NeurIPS 2022 | Localizes and edits single factual associations with limited collateral | ✅ Local |
| I7 | MEMIT: Mass-Editing Memory in a Transformer | Meng et al. | 2023 | ICLR 2023 | Scales model editing to large sets of memories | ❌ No PDF |
| I8 | Who's Harry Potter? Approximate Unlearning in LLMs | Eldan & Russinovich | 2023 | arXiv | Targeted entity/fact removal from LLMs | ✅ Local |

### Temporal Knowledge / Time in Models

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I9 | Time is Encoded in the Weights of Finetuned LMs | Nylund et al. | 2024 | ACL 2024 | Time vectors: temporal info encoded directionally in weights | ✅ Local |
| I10 | QA Over Temporal Knowledge Graphs | Saxena et al. | 2021 | ACL-IJCNLP 2021 | Valid-time formalism for temporal QA | ❌ No PDF |

### Robustness / Shortcut Learning

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I11 | Invariant Risk Minimization | Arjovsky et al. | 2019 | arXiv | Learns predictors stable across environments, not exploiting spurious correlations | ✅ Local |
| I12 | Shortcut Learning in Deep Neural Networks | Geirhos et al. | 2020 | Nature MI | Deep models prefer easy shortcuts (memorization) over robust features | ❌ No PDF |

### Chinese Financial Benchmarks

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I13 | CFinBench: Chinese Financial Benchmark for LLMs | Nie et al. | 2025 | NAACL 2025 | Comprehensive Chinese finance multi-task benchmark | ❌ No PDF |
| I14 | Golden Touchstone: Bilingual Financial LLM Benchmark | Wu et al. | 2025 | EMNLP 2025 Findings | Chinese-English bilingual finance benchmark | ❌ No PDF |

### LLM Self-Knowledge / Calibration

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I15 | Do LLMs Know How Much They Know? | Prato et al. | 2024 | EMNLP 2024 | LLM confidence vs actual knowledge; uncertainty gaps reveal memorization | ❌ No PDF |

### Financial Microstructure

| # | Paper | Authors | Year | Venue | Key Contribution | Status |
|---|-------|---------|------|-------|-----------------|--------|
| I16 | Industry Information Diffusion and Lead-lag Effect | Hou | 2007 | RFS | Info diffusion breadth as proxy for training data frequency | ❌ No PDF |

---

## Priority Reading by Research Angle (Updated)

### For Leakage Spectrum Hypothesis
Must-read: C1, C3, E2, A7, **I1 (memory vs reasoning separation — directly operationalizes the spectrum)**

### For Statistical Rigor
Must-read: **I3 (IRT for NLP)**, **I5 (DIF for contamination detection)**, I4

### For Causal Probes on Memorized Knowledge
Must-read: **I6 (ROME)**, I8 (unlearning), **I9 (time vectors)**

### For Theoretical Framing
Must-read: **I11 (IRM — leakage as shortcut)**, **I12 (shortcut learning)**, I2 (memorization in deep nets)

### For Chinese-Specific Resources
Must-read: **I13 (CFinBench)**, I14 (Golden Touchstone)
