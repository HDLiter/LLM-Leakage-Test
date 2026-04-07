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
