# Financial NLP & Sentiment Analysis

## Seeing the Goal, Missing the Truth: Human Accountability for AI Bias
**Authors & Year:** Cao, Jiang & Xu (2026)

**Summary:** This paper studies financial LLM measurement under purpose disclosure. Using earnings-call transcripts, it asks models to produce intermediate sentiment or competition scores, then compares goal-blind prompts with goal-aware prompts that disclose the downstream use in return or earnings prediction. The design is directly relevant to finance because the score itself is not the final forecast, yet the disclosed forecasting purpose still changes the score.

**Key methods/findings**
- Goal-aware sentiment and competition scores become more aligned with the disclosed downstream prediction target.
- The goal-aware advantage appears in pre-cutoff periods and disappears or weakens post-cutoff, consistent with purpose-conditioned use of information encoded before the model's knowledge cutoff.
- The paper frames this as a research-design problem: prompts and conversational context can leak the analyst's objective into what should be a neutral measurement step.

**Insight for our project:** This strengthens the case for prompt blinding in `P_predict` and for keeping the R5A baseline prompt free of research-goal language such as "leakage audit", "memorization test", or "downstream return model." It also motivates a Phase 8 exploratory `C_GoalFrame` arm: same CLS article, same target, same JSON schema, but different disclosed goals such as return prediction, earnings prediction, memory-leakage audit, or strict article-only measurement. The key control is BL2 post-cutoff: if a goal frame changes outputs equally in pre- and post-cutoff cases, it is generic framing or sycophancy; if the delta is pre-cutoff-specific, it is more relevant to leakage/memorization. Any internal-probe version should be a later white-box appendix after the core confirmatory experiments, not the primary estimand.

---

## AI Assisted Economics Measurement From Survey: Evidence from Public Employee Pension Choice
**Authors & Year:** Wang & Sharma (2026)

**Summary:** Wang and Sharma use LLMs to extract latent economic measurement structure from survey instruments, mapping survey items into sparse distributions over constructs and validating the resulting scores with out-of-sample incremental validity and discriminant-validity diagnostics.

**Key methods/findings**
- Treats LLM output as an intermediate measurement object, not as the final economic outcome.
- Uses iterative taxonomy refinement only when the added flexibility improves stable out-of-sample performance.
- Explicitly separates construct extraction, aggregation, and validation diagnostics.

**Insight for our project:** This belongs with the "LLM-generated intermediate variables" literature. It supports R5A's L3/L4 separation: `P_predict` outputs and goal-frame deltas should be treated as measurement objects that require validity checks, not as direct proof of forecasting skill or leakage.

---

## From Model Choice to Model Belief: Establishing a New Measure for LLM-Based Research
**Authors & Year:** Sun & Zhang (2025)

**Summary:** Sun and Zhang formalize "model belief" as a token-probability-based measure over choice alternatives, arguing that it can recover information that is lost when researchers record only a sampled discrete model choice.

**Key methods/findings**
- Converts token-level probabilities into a lower-variance measurement of model belief over alternatives.
- Shows asymptotic equivalence to repeated model-choice means while requiring fewer generations in limited-budget settings.
- Demonstrates the approach in an economics demand-estimation task.

**Insight for our project:** This is relevant to the operator boundary between `P_predict` and `P_logprob`. It does not change the current fleet or operator allocation, but it supports the long-run argument that internal probability structure can be a cleaner measurement target than sampled predictions when a white-box path exists.

---

## A Financial Brain Scan of the LLM
**Authors & Year:** Chen, Didisheim, Somoza & Tian (2025)

**Summary:** This paper applies interpretable internal-feature methods to financial forecasting, identifying concepts such as sentiment, technical analysis, timing, risk appetite, optimism, and pessimism inside model representations and then steering those concepts while holding other factors constant.

**Key methods/findings**
- Uses internal representations to map LLM financial forecasts to human-interpretable concepts.
- Shows that concept steering can change financial-forecast behavior without retraining.
- Frames internal analysis as a lightweight empirical tool for social-science and finance researchers.

**Insight for our project:** This is a useful bridge between `C_GoalFrame` and WS6. It supports an optional Phase 8 internal-probe appendix that asks whether goal disclosure changes late decision states, concept salience, or output calibration; it does not support moving `C_GoalFrame` into the current confirmatory family.

---

## Scaling Core Earnings Measurement with Large Language Models
**Authors & Year:** Shaffer & Wang (2024/2025 revision)

**Summary:** Shaffer and Wang use LLMs to estimate core earnings from 10-K filings and compare a one-shot prompt with a sequential prompt that decomposes the measurement task. The one-shot approach conflates related accounting concepts, while the sequential approach produces a measure with stronger validity properties.

**Key methods/findings**
- LLM-generated accounting variables are sensitive to prompt decomposition and task framing.
- Sequential prompting can improve construct validity but also introduces design degrees of freedom.
- The paper is a direct example of LLM outputs functioning as empirical finance measurements.

**Insight for our project:** This supports WS2 prompt lockdown and Phase 8 caution around `C_GoalFrame`: prompt engineering can legitimately improve measurement, but it can also move the target. PDF download from SSRN returned 403 during the 2026-05-07 sync, so this entry is referenced-only until a clean source is available.

---

## When LLMs Go Abroad: Foreign Bias in AI Financial Predictions
**Authors & Year:** Cao, Wang & Xiang (2025)

**Summary:** Cao, Wang, and Xiang compare ChatGPT and DeepSeek on Chinese-firm financial predictions and find model-specific foreign bias: ChatGPT is more optimistic about Chinese firms than DeepSeek. They trace the gap to differential information access, and report that supplying Chinese news in the prompt eliminates the prediction gap.

**Key methods/findings**
- Model predictions reflect the information environment represented in training data.
- Prompt-supplied local news can remove a cross-model prediction gap without changing model weights.
- The paper connects financial prediction bias to missing or asymmetric training exposure rather than generic capability alone.

**Insight for our project:** This is relevant as a caveat for fleet comparisons and as support for article-grounded prompt blinding. It does not imply any change to the black-box fleet; it only strengthens the reporting caveat that observed model differences can reflect training-data geography and language coverage. PDF download from SSRN returned 403 during the 2026-05-07 sync, so this entry is referenced-only until a clean source is available.

---

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
