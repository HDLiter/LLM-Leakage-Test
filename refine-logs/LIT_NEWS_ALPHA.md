# Literature Search: Financial News/Text for Return Prediction

Search date: 2026-04-05

Scope: targeted search on financial news and related financial text for stock-return prediction, with emphasis on LLM-extracted features, Chinese-market evidence, decomposed text factors, robustness to leakage/distribution shift, and multi-step prompting before prediction.

## Bottom Line

- The strongest direct precedents for the Thales-style pipeline are [Guo and Hauptmann (2024)](https://aclanthology.org/2024.emnlp-industry.77/), [Li, Qiao, and Zheng (2025)](https://arxiv.org/abs/2512.19484), [Wang, Izumi, and Sakaji (2024)](https://aclanthology.org/2024.findings-acl.185/), [Cao et al. (2024)](https://arxiv.org/abs/2404.18470), and [Bastianello, Decaire, and Guenzel (2024)](https://ssrn.com/abstract=5004839): all extract intermediate text factors first, then use a downstream prediction layer or asset-pricing test.
- The literature is moving away from simple headline sentiment toward embeddings, structured event representations, factor extraction, and multi-step prompting.
- Chinese-market evidence exists, but the English-indexed literature is much thinner than the U.S. literature. I did not find a strong cluster of indexed papers that explicitly use CLS, Eastmoney, or Sina Finance named in the title/abstract; many Chinese-market papers instead use proprietary Chinese financial-news corpora, analyst reports, or social-comment datasets.
- Direct evidence that chain-of-thought or "show your work" reduces hallucination or memorization in financial prediction is still sparse. In finance, multi-step prompting is used mainly to improve intermediate factor extraction and explainability, not yet as a clean contamination-mitigation test.

## A. News-Based Return Prediction with LLMs

### Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models
- Authors: Alejandro Lopez-Lira, Yuehua Tang
- Year / venue: 2024, Financial Analysts Journal
- URL: https://journals.sagepub.com/doi/full/10.2469/faj.v80.n2.1
- Method: Prompts ChatGPT on firm-specific news headlines and maps the model's textual assessment into directional sentiment signals for short-horizon stock prediction. The paper tests whether those GPT-generated headline signals produce statistically meaningful return predictability and trading profits.
- Relevance: This is still the canonical "LLM sentiment from headlines predicts returns" paper. It is the cleanest direct baseline for any claim that decomposed or structured features should be compared against simple LLM sentiment.

### Fine-Tuning Large Language Models for Stock Return Prediction Using Newsflow
- Authors: Tian Guo, Emmanuel Hauptmann
- Year / venue: 2024, EMNLP 2024 Industry Track
- URL: https://aclanthology.org/2024.emnlp-industry.77/
- Method: Compares encoder-only and decoder-only LLMs as text representation backbones for stock-return forecasting on financial newsflow. The key comparison is not just model family, but also feature type: token-level embeddings are aggregated in different ways and then fed into a forecasting module for portfolio construction.
- Relevance: This is one of the closest published matches to the Thales architecture. It explicitly shows that LLM text representations can outperform conventional sentiment scores in downstream long-only and long-short portfolios.

### Enhancing Sentiment-Based Stock Movement Prediction with Dissemination-Aware and Context-Enriched Large Language Models
- Authors: Boyu Liang, Hancheng Tao, Yong Liu, Stuart J. Russell, Weinan Zhang
- Year / venue: 2024, arXiv:2412.01365
- URL: https://arxiv.org/abs/2412.01365
- Method: Builds a dissemination-aware and context-enriched LLM pipeline for stock movement prediction rather than using raw sentiment alone. The model tries to capture both the semantic content of news and how widely the news diffuses, then evaluates both predictive accuracy and trading profitability.
- Relevance: Highly relevant for novelty/freshness and propagation-style features. It is a direct precedent for enriching a text signal with non-sentiment intermediate variables before prediction.

### LLMFactor: Extracting Profitable Factors through Prompts for Explainable Stock Movement Prediction
- Authors: Meiyun Wang, Kiyoshi Izumi, Hiroki Sakaji
- Year / venue: 2024, Findings of ACL 2024
- URL: https://aclanthology.org/2024.findings-acl.185/
- Method: Introduces Sequential Knowledge-Guided Prompting to make the LLM first generate background knowledge and then extract stock-movement factors from related news. Those extracted factors are combined with historical price information to predict stock movement, and the authors report gains over prior methods on U.S. and Chinese stock-market benchmarks.
- Relevance: This is a direct "decomposition before prediction" paper. It is particularly useful because it explicitly argues that factor extraction is better than keyphrase or sentiment-only signals for explainable forecasting.

### Structured Event Representation and Stock Return Predictability
- Authors: Gang Li, Dandan Qiao, Mingxuan Zheng
- Year / venue: 2025, arXiv / SSRN working paper
- URL: https://arxiv.org/abs/2512.19484
- Method: Uses LLMs to transform financial text into structured event representations rather than scalar sentiment, then evaluates whether those event features improve stock-return prediction. The paper is centered on event decomposition and asks whether a richer representation of who did what, to whom, and in what context produces alpha beyond coarse sentiment.
- Relevance: This is one of the exact papers you asked to check, and it is arguably the single closest research precedent to a structured, event-centric Thales pipeline.

### ECC Analyzer: Extracting Trading Signal from Earnings Conference Calls using Large Language Model for Stock Volatility Prediction
- Authors: Yupeng Cao, Zhi Chen, Qingyun Pei, Nathan Lee, K. P. Subbalakshmi
- Year / venue: 2024, ACM International Conference on AI in Finance
- URL: https://arxiv.org/abs/2404.18470
- Method: Uses a hierarchical LLM pipeline to extract signal from earnings-call text and predicts post-call stock volatility. The architecture is staged: the LLM first distills structured content from long calls, and a downstream prediction layer converts that extraction into a tradable risk signal.
- Relevance: This is the closest published paper to "LLM extracts intermediate finance factors, downstream model turns them into a signal." It is not newswire-based, but it is still a strong template for a decomposed, leakage-aware finance-text pipeline.

### Mental Models and Financial Forecasts
- Authors: Francesca Bastianello, Paul Decaire, Marius Guenzel
- Year / venue: 2024, Jacobs Levy Equity Management Center Working Paper / SSRN
- URL: https://ssrn.com/abstract=5004839
- Method: Uses multi-step LLM prompting and diagnostics to extract analysts' valuation methods, attention topics, valuation channels, time horizons, and sentiments from 2.1 million analyst reports. The extracted "mental model" variables are then linked to differences in forecasts and to return predictability through overreaction and underreaction patterns.
- Relevance: This is one of the strongest examples of rich factor decomposition from long-form financial text. It is also one of the cleanest papers showing that multi-step prompting can produce economically meaningful intermediate variables, not just sentiment labels.

## B. Chinese A-Share and Chinese-Language Market Literature

### FAST: Financial News and Tweet Based Time Aware Network for Stock Trading
- Authors: Ramit Sawhney, Arnav Wadhwa, Shivam Agarwal, Rajiv Ratn Shah
- Year / venue: 2021, EACL 2021
- URL: https://aclanthology.org/2021.eacl-main.185/
- Method: Proposes a hierarchical learning-to-rank system optimized for trading rather than pure classification accuracy. The paper evaluates on two benchmarks, including Chinese financial news spanning major stock indexes and multiple markets, and reports better cumulative profit and risk-adjusted returns than prior baselines.
- Relevance: This is one of the best older neural baselines for Chinese financial news in an actual trading setting. It is not LLM-based, but it is important context for what a modern LLM-factor pipeline is trying to beat.

### Stock Price Prediction with Sentiment Analysis for Chinese Market
- Authors: Yuchen Luan, Haiyang Zhang, Chenlei Zhang, Yida Mu, Wei Wang
- Year / venue: 2024, FinNLP/KDF/ENLP joint workshop
- URL: https://aclanthology.org/2024.finnlp-1.16/
- Method: Studies Chinese-market stock prediction using sentiment extracted from Chinese-language investor text rather than newswire alone. The paper asks whether sentiment signals are useful beyond a narrow set of large-cap names and broadens the empirical coverage.
- Relevance: This is a useful Chinese-market sentiment baseline, but it is weaker than the Thales target setting because it is not really about decomposed news features. It helps frame what "simple sentiment" means in a Chinese setting.

### Analyst Reports and Stock Performance: Evidence from the Chinese Market
- Authors: Rui Liu, Jiayou Liang, Haolong Chen, Yujia Hu
- Year / venue: 2025, Asia-Pacific Financial Markets
- URL: https://ssrn.com/abstract=4563238
- Method: Uses LLM-based extraction from Chinese analyst reports to transform unstructured text into features for predicting stock performance. The paper's contribution is to show that report text contains predictive information that can be systematized rather than read manually.
- Relevance: Not newswire, but directly relevant to Chinese financial-text alpha generation. It is one of the clearer Chinese-market papers where LLMs are used as feature extractors instead of final forecasters.

### A Trading Strategy Based on Analysts' Industry Analyses: Evidence from Textual Analyses of Analyst Reports in Chinese Stock Market
- Authors: Lunwen Wu, Di Gao, Wanxuan Su, Dawei Liang, Qianqian Du
- Year / venue: 2023, Emerging Markets Finance and Trade
- URL: https://doi.org/10.1080/1540496X.2023.2218968
- Method: Constructs a trading strategy from textual analysis of industry-level analyst reports in the Chinese stock market. The paper is less about LLMs and more about showing that richer textual analysis of Chinese financial documents can be converted into tradable signals.
- Relevance: Useful as adjacent Chinese-market evidence that text decomposition matters for alpha. It supports the general claim that the Chinese literature is broader than pure sentiment, even if outlet-specific A-share news papers are sparse in English indexes.

### Search Gap on CLS / Eastmoney / Sina Finance

I specifically searched for papers using Chinese financial news from CLS, Eastmoney, or Sina Finance for A-share prediction. I did not find a strong English-indexed cluster with those outlet names explicitly surfaced in the title/abstract/metadata. The closest hits were Chinese-market papers using unnamed Chinese financial-news corpora, social-comment corpora, or analyst reports, which suggests a real literature gap and supports the positioning of a CLS-based benchmark paper.

## C. Feature Decomposition Beyond Simple Sentiment

### News versus Sentiment: Predicting Stock Returns from News Stories
- Authors: Steven L. Heston, Nitish R. Sinha
- Year / venue: 2016, Finance and Economics Discussion Series
- URL: https://doi.org/10.17016/FEDS.2016.048
- Method: Compares richer story-level textual information with conventional sentiment measures for return prediction. The central claim is that the information in news stories is not exhausted by positive-minus-negative tone and that broader text features better capture the market-relevant component of news.
- Relevance: This is a key pre-LLM paper for the thesis that decomposed or richer text signals should beat plain sentiment. It is a natural citation bridge from classical textual asset pricing to modern LLM feature engineering.

### Predicting Returns with Text Data
- Authors: Zheng Tracy Ke, Bryan Kelly, Dacheng Xiu
- Year / venue: 2019, NBER Working Paper 26186
- URL: https://www.nber.org/papers/w26186
- Method: Learns return-predictive text factors from a very large financial text corpus and integrates them into an asset-pricing framework. Rather than forcing text into a narrow sentiment label, the paper treats text as a high-dimensional signal source whose latent structure helps explain the cross section of returns.
- Relevance: This is one of the most important general references for "text factors" in asset pricing. It gives strong support for the idea that the right comparison is not sentiment versus no sentiment, but simple text summaries versus richer latent or structured factors.

### All the News That's Fit to Reprint: Do Investors React to Stale Information?
- Authors: Paul C. Tetlock
- Year / venue: 2011, Review of Financial Studies
- URL: https://doi.org/10.1093/rfs/hhq141
- Method: Studies whether investors underreact or overreact differently to fresh versus stale news and shows that repeated or recycled information behaves differently from new disclosures. The paper is explicitly about information freshness and the market value of novelty.
- Relevance: This is the core classical citation for any "novelty" factor in a news-based trading system. If Thales wants novelty/freshness as a decomposed signal, this is one of the most defensible economic anchors.

### Modeling News Interactions and Influence for Financial Market Prediction
- Authors: Mengyu Wang, Shay B. Cohen, Tiejun Ma
- Year / venue: 2024, Findings of EMNLP 2024
- URL: https://aclanthology.org/2024.findings-emnlp.189/
- Method: Introduces FININ, a model that captures not only links from news to prices but also interactions among news items. Across 2.7 million articles on the S&P 500 and NASDAQ 100, the paper finds delayed pricing, long-memory effects, and clear limits of pure sentiment analysis.
- Relevance: This is a strong modern paper arguing that sentiment alone leaves predictive power on the table. It is very useful for motivating interaction, propagation, and influence features in a decomposed pipeline.

### Financial News-Based Stock Movement Prediction Using Causality Analysis of Influence in the Korean Stock Market
- Authors: KiHwan Nam, NohYoon Seong
- Year / venue: 2019, Decision Support Systems
- URL: https://doi.org/10.1016/j.dss.2018.11.004
- Method: Goes beyond bag-of-words sentiment by analyzing the causal influence structure embedded in news and how that influence propagates into stock movements. The paper focuses on influence and source-linked effects rather than a one-dimensional tone score.
- Relevance: Not Chinese and not LLM-based, but relevant for "authority/credibility/source" style features. It supports the broader claim that structural influence signals can outperform flat sentiment proxies.

## D. Robustness, Distribution Stability, and Leakage Awareness

### Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis
- Authors: Paul Glasserman, Caden Lin
- Year / venue: 2024, The Journal of Financial Data Science
- URL: https://doi.org/10.3905/jfds.2023.1.143
- Method: Re-examines GPT-sentiment return prediction under stricter temporal controls, including time-constrained language models and headline filtering designed to reduce training-set overlap. The paper argues that a meaningful share of apparent predictability can be due to look-ahead bias rather than genuine real-time forecasting ability.
- Relevance: This is the most direct robustness check on the Lopez-Lira and Tang line of work. It is essential for any leakage-aware literature review because it shows that naive historical backtests of LLM sentiment can be materially inflated.

### Time Variation in the News-Returns Relationship
- Authors: Paul Glasserman, Fulin Li, Harry Mamaysky
- Year / venue: 2025, Journal of Financial and Quantitative Analysis
- URL: https://doi.org/10.1017/S0022109023001369
- Method: Studies how the predictive relationship between news and returns changes over time rather than assuming one stable mapping. The paper shows that the news-return link is state-dependent and unstable, which matters for training, validation, and out-of-sample deployment.
- Relevance: This is one of the best citations for distribution-shift and temporal instability in text-based trading signals. It supports your emphasis on OOD robustness and rolling-period evaluation.

### Chronologically Consistent Large Language Models
- Authors: Songrun He, Steve Yang, Alex Chinco, Marina Halac
- Year / venue: 2025, arXiv:2502.21206
- URL: https://arxiv.org/abs/2502.21206
- Method: Trains chronologically consistent language models that only see text available up to each date and tests them in an asset-pricing application predicting next-day stock returns from financial news. Despite the temporal restriction, the authors find Sharpe ratios comparable to a much larger unrestricted Llama baseline, implying that look-ahead bias is real but application-specific.
- Relevance: This is probably the cleanest current paper on leakage-aware feature design for finance. It is directly relevant to any argument that chronologically clean intermediate features may be preferable to contaminated but seemingly stronger backtests.

## E. Multi-Step Reasoning / Decomposition Before Prediction

This literature is still thin if the bar is "explicitly proves that chain-of-thought reduces hallucination or memorization." The finance papers I found are better described as evidence that multi-step prompting improves intermediate feature quality and interpretability:

- [Mental Models and Financial Forecasts](https://ssrn.com/abstract=5004839): multi-step prompting extracts attention topics, valuation channels, methods, horizons, and sentiment, then links those latent variables to forecasts and return predictability.
- [LLMFactor](https://aclanthology.org/2024.findings-acl.185/): sequential prompting plus background-knowledge generation beats keyphrase/sentiment baselines for stock-movement prediction and improves explainability.
- [ECC Analyzer](https://arxiv.org/abs/2404.18470): hierarchical extraction from long earnings calls yields downstream volatility signals, showing that staged extraction can outperform naive direct use of long text.

My read after the search: the best-supported claim is not "CoT lowers memorization," but "multi-step decomposition can produce more economically meaningful and often more robust intermediate features than direct sentiment or direct prediction."

## F. Closest Matches to the Thales Pipeline

If the target is "LLM extracts intermediate features, downstream model aggregates them, final output is a trading signal," the closest academic matches are:

1. [Fine-Tuning Large Language Models for Stock Return Prediction Using Newsflow](https://aclanthology.org/2024.emnlp-industry.77/): LLM embeddings -> forecasting module -> portfolios.
2. [Structured Event Representation and Stock Return Predictability](https://arxiv.org/abs/2512.19484): event decomposition -> structured features -> return prediction.
3. [LLMFactor](https://aclanthology.org/2024.findings-acl.185/): sequential prompting -> extracted factors -> stock-movement prediction.
4. [ECC Analyzer](https://arxiv.org/abs/2404.18470): hierarchical LLM extraction -> volatility signal.
5. [Mental Models and Financial Forecasts](https://ssrn.com/abstract=5004839): multi-step extraction of reasoning structure -> asset-pricing tests.

I did not find a distinct, named "Thales/quantamental signal community" paper cluster. The closest work is scattered across ACL/EMNLP/AI-in-Finance and SSRN, not a single branded literature stream.

## G. Implications for This Repo

- The strongest direct novelty for this project is not merely "LLMs can read news" but "decomposed text-grounded features may be more robust to contamination than direct prediction or naive sentiment."
- The Chinese A-share gap looks real enough to motivate a dedicated CLS-based paper, especially if the benchmark and leakage controls are clean.
- The safest comparison set for a paper or benchmark looks like:
  - direct prediction
  - simple sentiment
  - embeddings/newsflow representations
  - structured event/factor extraction
  - leakage-aware temporally clean variants
- For economic motivation of specific decomposed factors:
  - novelty / freshness: Tetlock (2011)
  - richer text beats sentiment: Heston and Sinha (2016), Ke-Kelly-Xiu (2019), Wang-Cohen-Ma (2024)
  - multi-step LLM factorization: Bastianello et al. (2024), Wang-Izumi-Sakaji (2024), Li-Qiao-Zheng (2025), Cao et al. (2024)

