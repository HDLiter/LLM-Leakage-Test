# Research Landscape: LLM Training Data Leakage in Financial NLP

> Last updated: 2026-04-05. This document provides context for research planning.

## 1. Problem Statement

When LLMs are used for financial tasks (sentiment analysis, price prediction, trading), their training data inevitably contains historical financial news and market outcomes. This creates a fundamental validity threat: the model may simply "recall" memorized facts rather than genuinely reasoning about market sentiment. This phenomenon has been called "profit mirage" (Li et al. 2025), "lookahead bias" (Gao et al. 2026), and "temporal contamination" (Zhang et al. 2026).

## 1.1 Project Origin: Thales Quantamental Engine

This research is derived from **Thales** (`D:\GitRepos\Thales`), a quantamental investment engine for A-share ETF rotation. In Thales, LLMs are used not for direct up/down prediction, but for decomposed, text-grounded signal extraction:

- **Event-Centric Architecture**: News → stateful Event nodes (Rumor → Announced → Completed → Dormant) with temporal decay
- **Two-Dimensional Impact**: Fund (fundamental, slow, mean-reverting) + Shock (sentiment, fast, asymmetric via Prospect Theory)
- **5-bin probability distributions**: Impact scored as distributions over asymmetric bins `[-6.0, -2.0, 0, 1.0, 3.0]`, yielding E[X] (direction), Var(X) (confidence), H(X) (market disagreement)
- **Three orthogonal factor dimensions**: Novelty, Expectation Surprise, Impact — computed in isolated SLM calls to prevent factor contamination
- **ML aggregation**: Features fed to XGBoost (rank:pairwise), not raw LLM predictions

**The leakage problem in Thales**: If the LLM's sentiment/impact scores are contaminated by training data memorization, then the entire backtest is inflated — the XGBoost model learns from "cheating" features, producing false alpha that vanishes in live trading.

### Key Insight: Task Decomposition as Leakage Mitigation

A crucial hypothesis from Thales: **the degree of leakage depends on how you use the LLM**:

1. **Direct prediction** ("Will this stock go up?") → maximum leakage risk (model recalls outcomes)
2. **Sentiment classification** ("Is this news positive?") → moderate leakage (model may recall market reactions)
3. **Decomposed text-grounded indicators** (novelty, expectation gap, information content, authority level) → potentially lower leakage (forces text-grounded reasoning, harder to "cheat" with memorized outcomes)

This suggests a **leakage spectrum** from outcome-proximal to text-grounded tasks. Testing this spectrum is a potential core contribution.

### Output Format as Leakage Detection Tool

Different output formats enable different leakage detection signals:
- **With reasoning/chain-of-thought**: Can inspect rationale for temporal fact leakage (claim-level audit à la Zhang et al.)
- **K-bin probability distributions**: Information entropy H(X) and distribution shape provide confidence/calibration signals that may correlate with memorization
- **Scalar outputs**: Least information for leakage detection

## 2. Our Project

- **Task**: Sentiment analysis on Chinese A-share financial news
- **Primary model**: DeepSeek-chat (API, grey/black-box access)
- **White-box reference**: Qwen 2.5 7B via local vLLM (full logprobs access)
- **Corpus**: 1M+ CLS (财联社) telegraph entries, 2020-01 to 2026-02
- **Test set**: 84 A-share news items (2021-2024) with counterfactual variants
- **GPU**: Local RTX 4060 Ti; 4090 rental within budget

### Preliminary Results (6 notebooks completed)
- Baseline leakage is high: Prediction Consistency (PC) = 0.119
- Best mitigation combo (year-masking + role-play + CoT): leakage score L = -3.477, accuracy maintained at 83.3%
- DSPy MIPROv2 prompt optimization further improved to L = -4.496, accuracy 84.6%
- Output format matters: binary/scalar formats show different leakage profiles

### Infrastructure Capabilities
| Model | Input logprobs | Output logprobs | Min-K% Prob | Black-box methods |
|-------|---------------|-----------------|-------------|-------------------|
| DeepSeek-chat API | ❌ (echo+logprobs forbidden) | ⚠️ Chat: all 0.0; Beta completions: real but no echo | ❌ | ✅ |
| Qwen 2.5 7B (vLLM) | ✅ (echo=True) | ✅ (real values) | ✅ (verified, gap ~2.4) | ✅ |

## 3. Key Papers

### 3.1 Financial Leakage (directly relevant)

**Profit Mirage** (Li et al., arXiv:2510.07920, 2025)
- FinLakeBench: 2000 financial QA pairs for memorization audit
- FactFin: counterfactual framework (Strategy Code Gen, RAG, MCTS, Counterfactual Simulator)
- All LLM agents suffer 50-72% total return decay post-training-cutoff
- GPT-4o answers >85% of FinLakeBench correctly (near-encyclopedic recall)
- 82% prediction consistency under counterfactual perturbation → agents recite, not reason
- Market: US (NASDAQ-100), Language: English

**All Leaks Count, Some Count More** (Zhang, Chen, Stadie, arXiv:2602.17234, 2026)
- Claim-level framework: decomposes rationales into atomic claims, categorizes by temporal verifiability
- Shapley-DCLR: importance-weighted leakage rate (not all leaks matter equally)
- TimeSPEC: claim extraction → verification → regeneration (mitigation)
- Reduces decision-critical leakage by 75-99% while preserving performance
- Domains: Supreme Court, NBA salaries, S&P 500

**A Test of Lookahead Bias in LLM Forecasts** (Gao, Jiang, Yan, arXiv:2512.23847, 2026)
- LAP (Lookahead Propensity) = Min-K% Prob applied to financial forecast prompts
- Statistical test: positive LAP-accuracy correlation → evidence of lookahead bias
- Applied to: news headlines → stock returns, earnings call → capex prediction
- Bridges MIA literature to financial forecasting reliability

**Your AI, Not Your View** (Lee et al., arXiv:2507.20957, 2025)
- Knowledge conflict between LLM parametric memory and external evidence
- Three-stage: evidence generation → preference elicitation → bias verification
- LLMs show consistent large-cap/contrarian preferences hardening into confirmation bias
- Tangentially relevant: parametric memory bias mechanism

### 3.2 Contamination Detection Methods

**Min-K% Prob** (Shi et al., ICLR 2024, arXiv:2310.16789)
- Reference-free pretraining data detection: average log-likelihood of k% lowest-probability tokens
- WikiMIA benchmark; +7.4% AUC over strongest baseline
- No shadow/reference model needed
- **Foundation method for our white-box experiments on Qwen**

**Min-K%++** (Zhang et al., ICLR 2025)
- Calibrated scoring function improving Min-K%; matches reference-based methods
- Consistently outperforms Min-K% on MIMIR benchmark

**CDD/TED** (Dong et al., ACL 2024 Findings, arXiv:2402.15938)
- CDD: detect contamination via output distribution peakedness (black-box)
- TED: correct contaminated outputs at inference time
- +21.8-30.2% improvement over baselines; mitigates up to 66.9% of performance inflation
- **Applicable to DeepSeek in black-box mode**

**TS-Guessing** (Deng et al., NAACL 2024)
- Mask wrong answers in MCQs → prompt model to fill gaps
- ChatGPT/GPT-4: 52%/57% exact match on MMLU missing options
- **Slot-guessing idea adaptable to our masking experiments**

**Rephrased Samples** (Yang et al., LMSys, arXiv:2311.04850, 2023)
- Paraphrasing/translation bypasses n-gram decontamination
- 13B model fine-tuned on rephrased data → GPT-4-level on MMLU/GSM8k
- Validates counterfactual/paraphrasing approach to contamination testing

**KDS** (ICML 2025, arXiv:2502.00678)
- Kernel Divergence Score: embedding similarity divergence before/after fine-tuning
- Near-perfect correlation with contamination levels
- Requires fine-tuning access (less applicable to API-only)

### 3.3 Membership Inference Attacks (MIA)

**Do MIAs Work on LLMs?** (Duan et al., COLM 2024, arXiv:2402.07841)
- MIMIR benchmark with minimal distributional shift
- MIAs barely outperform random guessing for most pretraining settings
- **Important caveat**: large dataset + few iterations + fuzzy boundary

**Scaling Up MIA** (NAACL 2025 Findings)
- Document-level MIA ≈ random guessing
- Most methods focus on short texts (128-256 tokens)
- Informs our probe length design

**MIA against Fine-tuned LLMs via Self-prompt Calibration** (NeurIPS 2024)
- Self-prompt calibration for MIA without closely matching reference dataset
- Relevant if testing fine-tuned model variants

### 3.4 Surveys

**Benchmark Data Contamination: A Survey** (Xu et al., arXiv:2406.04244, 2024)
- Taxonomy: input-only vs input-label contamination
- Reviews: n-gram overlap, perplexity, output distribution, LLM-driven detection

**LLMSanitize** (Ravaut et al., TMLR 2025, arXiv:2404.00699)
- Unified Python library implementing major detection algorithms
- String matching, embedding similarity, likelihood-based, LLM-driven
- **Practical tool we can integrate**

**Unveiling the Spectrum of Data Contamination** (Li et al., Yale NLP, ACL 2024 Findings)
- Full taxonomy from detection to remediation

**Static to Dynamic Evaluation** (EMNLP 2025, arXiv:2502.17521)
- Evolution from static to dynamic benchmarking paradigms

### 3.5 Training Data Extraction & Privacy

**Scalable Extraction of Training Data** (Carlini et al., arXiv:2311.17035, 2023)
- Divergence attack against aligned models; extracts GBs of training data
- ChatGPT: 150x higher extraction rate under divergence attack

**Rethinking Verbatim Memorization** (Sander et al., NeurIPS 2025)
- Better verbatim memorization ≠ more privacy leakage
- Nuance: relationship depends on knowledge encoding

### 3.6 Dynamic Benchmarks

**LiveBench** (White et al., arXiv:2406.19314, 2024)
- Monthly-updated benchmark from recent data; contamination-limited by design

**LatestEval** (arXiv:2312.12343, 2024)
- Auto-creates evaluations from recent-only texts

## 4. Detection Methods Hierarchy

| Level | Access needed | Methods | Applicable to |
|-------|--------------|---------|---------------|
| White-box | Token logprobs (input) | Min-K% Prob, Min-K%++, LAP | Qwen (vLLM) |
| Grey-box | Output distributions | CDD, output logprob analysis | DeepSeek (beta completions) |
| Black-box | Predictions only | Counterfactual perturbation (PC/CI/IDS), Shapley-DCLR, TS-Guessing | Both models |

## 5. Field Consensus

1. **"Profit mirage" is real** — LLM financial agents mostly recall, not reason (50-72% return decay post-cutoff)
2. **Counterfactual perturbation is the dominant black-box paradigm** — if predictions don't change when inputs change, the model is reciting
3. **Not all leakage matters equally** — Shapley weighting distinguishes decision-critical vs peripheral leakage
4. **MIA has limitations at scale** — but works better for domain-specific, high-visibility texts (like financial news)
5. **Blocking verbatim memorization is insufficient** — information leaks through paraphrased/semantic channels

## 6. Open Gaps (Our Opportunity)

| Dimension | Prior work | Our differentiation |
|-----------|-----------|---------------------|
| Market | US equities (NASDAQ-100, DJIA, S&P 500) | **A-shares** |
| Language | English only | **Chinese** |
| Model | GPT-4, ChatGPT, open-source (LLaMA, Qwen) | **DeepSeek** (understudied) + Qwen white-box |
| Task | Price prediction, trading, investment decisions | **Sentiment analysis** (simpler, more isolatable) |
| Scale | FinLakeBench: 2000 QA pairs | **1M+ real news entries** |
| Methodology | Single-method studies | **Cross-validation: white-box + black-box on same corpus** |
| Temporal analysis | Before/after cutoff binary | **Continuous temporal decay curves** (6 years of daily data) |

## 7. Cross-Disciplinary Connections (Potential)

### Software Testing / Metamorphic Testing
Counterfactual perturbation is essentially metamorphic testing — changing inputs while expecting invariant or predictable output changes. The SE community has formalized perturbation design principles (metamorphic relations) that could systematize our ad-hoc reverse_outcome + alter_numbers approach.

### Computational Journalism / News Propagation
The same financial event gets rephrased across dozens of sources. News propagation breadth directly correlates with training data frequency, which should predict memorization strength. Hot-event decay curves from journalism research could explain why certain news is more "leaky."

### Knowledge Engineering / Temporal Knowledge Graphs
Claim-level temporal verification (as in Zhang et al.'s Shapley-DCLR) maps onto temporal knowledge graph frameworks — facts have valid time intervals, and "leakage" is accessing a fact outside its valid temporal scope. TKG formalism could provide structure for claim taxonomy.

## 8. Key Methodological Questions

1. Can white-box detection (Min-K% on Qwen) and black-box detection (counterfactual on DeepSeek) produce consistent leakage signals on the same corpus?
2. How does leakage vary with news recency, company prominence, and event type?
3. Does Chinese financial text exhibit different memorization patterns than English (due to tokenization, training data coverage)?
4. Can we build temporal leakage decay curves from 1M+ news entries spanning 6 years?
