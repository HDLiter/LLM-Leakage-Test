# Financial NLP & Sentiment Analysis

## Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models
**Authors & Year:** Lopez-Lira & Tang (2024)

**Summary:** We document the capability of large language models (LLMs) like ChatGPT to predict stock market reactions from news headlines without direct financial training. Using postknowledge-cutoff headlines, GPT-4 captures initial market responses, achieving approximately 90% portfolio-day hit rates for the non-tradable initial reaction. GPT-4 scores also significantly predict the subsequent drift, especially for small stocks and negative news.

**Key methods/findings**
- To rationalize these findings, we develop a theoretical model that incorporates LLM technology, information-processing capacity constraints, underreaction, and limits to arbitrage.
- Strategy returns decline as LLM adoption rises, consistent with improved price efficiency.
- GPT-4 scores also significantly predict the subsequent drift, especially for small stocks and negative news.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes.

---

## R1 Additions

- **InvestorBench:** Benchmarks LLM-based agents on financial decision-making tasks; this matters because the R1 Editor review uses it as a finance capability benchmark contrast, clarifying that FinMem-Bench should target temporally inadmissible dependence rather than generic finance ability.

---

## CFinBench: A Comprehensive Chinese Financial Benchmark for Large Language Models
**Authors & Year:** Nie et al. (2024)

**Summary:** Large language models (LLMs) have achieved remarkable performance on various NLP tasks, yet their potential in more challenging and domain-specific task, such as finance, has not been fully explored. In this paper, we present CFinBench: a meticulously crafted, the most comprehensive evaluation benchmark to date, for assessing the financial knowledge of LLMs under Chinese context. In practice, to better align with the career trajectory of Chinese financial practitioners, we build a systematic evaluation from 4 first-level categories: (1) Financial Subject : whether LLMs can memorize the necessary basic knowledge of financial subjects, such as economics, statistics and auditing.

**Key methods/findings**
- In this paper, we present CFinBench: a meticulously crafted, the most comprehensive evaluation benchmark to date, for assessing the financial knowledge of LLMs under Chinese context.
- The results show that GPT4 and some Chinese-oriented models lead the benchmark, with the highest average accuracy being 60.16%, highlighting the challenge presented by CFinBench.
- The dataset and evaluation code are available at https://cfinbench.github.io/ .

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes. It also maps directly to evidence-intrusion scoring.

---

## ECC Analyzer: Trading Signal from Earnings Calls
**Authors & Year:** Cao et al. (2024)

**Summary:** In the realm of financial analytics, leveraging unstructured data, such as earnings conference calls (ECCs), to forecast stock volatility is a critical challenge that has attracted both academics and investors. While previous studies have used multimodal deep learningbased models to obtain a general view of ECCs for volatility predicting, they often fail to capture detailed, complex information. Our research introduces a novel framework: ECC Analyzer , which utilizes large language models (LLMs) to extract richer, more predictive content from ECCs to aid the model’s prediction performance.

**Key methods/findings**
- Experimental results demonstrate that our model outperforms traditional analytical benchmarks, confirming the effectiveness of advanced LLM techniques in financial analysis.
- Our research introduces a novel framework: ECC Analyzer , which utilizes large language models (LLMs) to extract richer, more predictive content from ECCs to aid the model’s prediction performance.
- These features are then fused through multimodal feature fusion to perform volatility prediction.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes. It also maps directly to evidence-intrusion scoring.

---

## Evaluating Company-Specific Biases in Financial Sentiment Analysis Using Large Language Models
**Authors & Year:** Nakagawa et al. (2024)

**Summary:** —This study aims to evaluate the sentiment of financial texts using large language models (LLMs) and to empirically determine whether LLMs exhibit company-specific biases in sentiment analysis. Specifically, we examine the impact of general knowledge about firms on the sentiment measurement of texts by LLMs. Firstly, we compare the sentiment scores of financial texts by LLMs when the company name is explicitly included in the prompt versus when it is not.

**Key methods/findings**
- We define and quantify companyspecific bias as the difference between these scores.
- This model helps us understand how biased LLM investments, when widespread, can distort stock prices.
- Next, we construct an economic model to theoretically evaluate the impact of sentiment bias on investor behavior.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes. It is especially useful for entity-swap tests that measure entity-cue dependence.

---

## FinDPO: Financial Sentiment via Preference Optimization
**Authors & Year:** Iacovides et al. (2025)

**Summary:** Opinions expressed in online finance-related textual data are having an increasingly profound impact on trading decisions and market movements. This trend highlights the vital role of sentiment analysis as a tool for quantifying the nature and strength of such opinions. With the rapid development of Generative AI (GenAI), supervised fine-tuned (SFT) large language models (LLMs) have become the de facto standard for financial sentiment analysis.

**Key methods/findings**
- To this end, we introduce FinDPO , the first finance-specific LLM framework based on post-training human preference alignment via Direct Preference Optimization (DPO).
- The proposed FinDPO achieves state-of-the-art performance on standard sentiment classification benchmarks, outperforming existing supervised fine-tuned models by 11% on the average.
- Uniquely, the FinDPO framework enables the integration of a fine-tuned causal LLM into realistic portfolio strategies through a novel ‘logit-toscore’ conversion, which transforms discrete sentiment predictions into continuous, rankable sentiment scores (probabilities).

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes.

---

## LLMFactor: Extracting Profitable Factors through Prompts for Explainable Stock Movement Prediction
**Authors & Year:** Wang, Izumi & Sakaji (2024)

**Summary:** Recently, Large Language Models (LLMs) have attracted significant attention for their exceptional performance across a broad range of tasks, particularly in text analysis. However, the finance sector presents a distinct challenge due to its dependence on time-series data for complex forecasting tasks. In this study, we introduce a novel framework called LLMFactor, which employs Sequential Knowledge-Guided Prompting (SKGP) to identify factors that influence stock movements using LLMs.

**Key methods/findings**
- In this study, we introduce a novel framework called LLMFactor, which employs Sequential Knowledge-Guided Prompting (SKGP) to identify factors that influence stock movements using LLMs.
- An extensive evaluation of the LLMFactor framework across four benchmark datasets from both the U.S. and Chinese stock markets demonstrates its superiority over existing state-of-the-art methods and its effectiveness in financial time-series forecasting.
- Our framework directs the LLMs to create background knowledge through a fill-in-the-blank strategy and then discerns potential factors affecting stock prices from related news.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes. It also maps directly to evidence-intrusion scoring.

---

## Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents
**Authors & Year:** Li et al. (2025)

**Summary:** LLM-based financial agents have attracted widespread excitement for their ability to trade like human experts. However, most systems exhibit a “profit mirage”: dazzling back-tested returns evaporate once the model’s knowledge window ends, because of the inherent information leakage in LLMs. In this paper, we systematically quantify this leakage issue across four dimensions and releaseFinLakeBench, a leakage-robust evaluation benchmark.

**Key methods/findings**
- Furthermore, to mitigate this issue, we introduceFactFin, a framework that applies counterfactual perturbations to compel LLM-based agents to learn causal drivers instead of memorized outcomes.
- Extensive experiments show that our method surpasses all baselines in out-of-sample generalization, delivering superior risk-adjusted performance.
- In this paper, we systematically quantify this leakage issue across four dimensions and releaseFinLakeBench, a leakage-robust evaluation benchmark.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes. It especially supports our counterfactual testing design.

---

## Structured Event Representation and Stock Return Predictability
**Authors & Year:** Li et al. (2025)

**Summary:** We find that event features extracted by large language models (LLMs) are effective for text-based stock return prediction. Using a pre-trained LLM to extract event features from news articles, we propose a novel deep learning model based on structured event representation (SER) and attention mechanisms to predict stock returns in the crosssection. Our SER-based model provides superior performance compared with other existing text-driven models to forecast stock returns out of sample and offers highly interpretable feature structures to examine the mechanisms underlying the stock return predictability.

**Key methods/findings**
- Using a pre-trained LLM to extract event features from news articles, we propose a novel deep learning model based on structured event representation (SER) and attention mechanisms to predict stock returns in the crosssection.
- We find that event features extracted by large language models (LLMs) are effective for text-based stock return prediction.
- We further provide various implications based on SER and highlight the crucial benefit of structured model inputs in stock return predictability.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes.

---

## Your AI, Not Your View: The Bias of LLMs in Investment Analysis
**Authors & Year:** Lee et al. (2025)

**Summary:** In finance, Large Language Models (LLMs) face frequent knowledge conflicts due to discrepancies between pre-trained parametric knowledge and real-time market data. These conflicts become particularly problematic when LLMs are deployed in real-world investment services, where misalignment between a model’s embedded preferences and those of the financial institution can lead to unreliable recommendations. Yet little research has examined what investment views LLMs actually hold.

**Key methods/findings**
- We propose an experimental framework to investigate such conflicts, offering the first quantitative analysis of confirmation bias in LLM-based investment analysis.
- Focusing on sector, size, and momentum, our analysis reveals distinct, model-specific tendencies.
- In finance, Large Language Models (LLMs) face frequent knowledge conflicts due to discrepancies between pre-trained parametric knowledge and real-time market data.

**Insight for our project:** This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes.

---

## Fine-Grained Classification of Announcement News Events in the Chinese Stock Market
**Authors & Year:** Miu et al. (2022)

**Summary:** Miu et al. focus on Chinese stock announcement news and argue that existing event taxonomies are still too coarse for market-relevant analysis. They propose a two-step procedure that extracts candidate trigger words and co-occurrence expressions, then applies three criteria to finalize event types, producing a 54-type framework with high reported precision and F-score on real Chinese market data.

**Key methods/findings**
- Uses stock-announcement text rather than broad financial news, which keeps the taxonomy close to CLS-style disclosures.
- Builds event types by combining trigger-word extraction, co-occurrence support, and three explicit judgment criteria.
- Constructs 54 fine-grained event types and filters out classes that appear unhelpful to investors under the paper's unilateral-trading setup.

**Insight for our project:** This strengthens Structured Event Type and supports a more precise Modality or Disclosure-Regime split for Chinese announcement text, which is exactly the taxonomy gap exposed in R4. It should seed event-type-stratified SR/FO counterfactual probes and FinMem-NoOp variants on CLS announcements; the caveat is that the paper is event-typing prior art, not direct memorization prior art, and its investor-value filter uses a best-case unilateral-trading assumption.

---

## Evaluating LLMs in Finance Requires Explicit Bias Consideration
**Authors & Year:** Kong et al. (2026)

**Summary:** Kong et al. argue that financial LLM evaluations routinely overstate validity because multiple finance-specific biases go unreported. After reviewing 164 papers, they identify five recurring bias classes and propose a Structural Validity Framework plus a checklist meant to screen out results that cannot support deployment claims.

**Key methods/findings**
- Identifies look-ahead, survivorship, narrative, objective, and cost bias as recurring failure modes in financial LLM studies.
- Shows that no single bias is discussed in more than 28 percent of the reviewed literature from 2023 to 2025.
- Proposes a checklist and framework for minimum structural-validity requirements before performance claims are taken seriously.

**Insight for our project:** This paper directly strengthens Cutoff Exposure and forces the benchmark to report overlap with narrative, objective, and cost bias instead of treating leakage in isolation. It should seed R5 contamination and CMMD evaluation checklists, especially for deciding which detector outputs are strong enough to support deployment-facing claims; the caveat is that it is a position and framework paper rather than a detector benchmark.

---

## Anonymization and Information Loss
**Authors & Year:** Wu et al. (2025)

**Summary:** Wu et al. examine anonymization as a defense against firm-specific leakage in financial text analysis and find a sharp trade-off. While anonymization hides identity cues, it also strips away economically relevant information, especially when numbers and object entities are removed, and can degrade extraction more than the original look-ahead bias would have distorted it.

**Key methods/findings**
- Shows that anonymization does obscure firm identity but also weakens the model's ability to extract useful economic signal.
- Finds especially severe information loss when numerical entities and object entities are removed.
- Reports that, for earnings-call sentiment extraction, anonymization can be more damaging than look-ahead bias itself.

**Insight for our project:** This is direct support for Entity Salience and for the R5 detector-level stratification field Entity-Anonymization Sensitivity that the sweep routed out of the factor list. It should seed anonymized-versus-original comparisons inside Min-K%, MIA, and SR/FO probe families; the key caveat is that anonymization can destroy economically relevant signal more than it removes leakage.

---

## LiveTradeBench: Seeking Real-World Alpha with Large Language Models
**Authors & Year:** Yu et al. (2025)

**Summary:** Yu, Li, and You argue that static benchmarks miss the sequential uncertainty and non-stationarity that matter for real trading. LiveTradeBench therefore evaluates LLM agents in live markets with streaming data, portfolio-allocation decisions, and multi-market settings, and their results show that strong static benchmark scores do not reliably translate into good trading outcomes.

**Key methods/findings**
- Replaces offline backtests with live data streaming to reduce information leakage and preserve real-time uncertainty.
- Evaluates portfolio allocation rather than single-action trades, forcing cross-asset reasoning and risk management.
- Finds a clear gap between high static benchmark scores and real-world trading competence across 21 models.

**Insight for our project:** This strengthens Cutoff Exposure and Event Phase by insisting on live, uncertainty-preserving evaluation instead of retrospective static tests. It should seed R5 contamination and CMMD families as external-validity checks against backtest-only gains; the caveat is that the benchmark is U.S.-centric and portfolio-oriented rather than Chinese announcement-level memorization measurement.
