# Sub-task B - Broad 2024-2026 Prior-Art Sweep
Date: 2026-04-14
Persona: senior NLP / memorization researcher, fresh (no R1-R4 attachment)
Search method: arXiv API + web_search + Semantic Scholar API, every citation verified in-session

## URGENT findings (P0 direct prior art / reviewer killers)
None this sub-task.

## Query-by-query results

### Query 1 - "LLM memorization" + "financial" + "benchmark"
- Search method: arXiv API query `(all:"memorization" OR all:"leakage") AND all:"financial" AND all:"benchmark"` with `sortBy=submittedDate`, `sortOrder=descending`, `max_results=30`; web_search terms `"LLM memorization financial benchmark 2024 2025 2026"`, `"financial LLM memorization benchmark arXiv 2025 2026"`, and exact-title checks for surfaced hits.
- Null results: the arXiv top-30 was dominated by noisy finance benchmarks unrelated to memorization. No new direct benchmark-level memorization paper surfaced beyond already-known overlap papers (`Look-Ahead-Bench`, `Profit Mirage`, `MemGuard-Alpha`).
- Hits:
  - [LiveTradeBench: Seeking Real-World Alpha with Large Language Models](https://arxiv.org/abs/2511.03628), Yu et al. 2025, priority: P1
    - Why relevant: it is not a memorization benchmark, but it is a reviewer-visible adjacent financial benchmark that explicitly rejects offline backtesting and uses live data streaming to avoid information leakage.
    - Already in library? no
    - Recommended action: read
  - [The Memorization Problem: Can We Trust LLMs' Economic Forecasts?](https://arxiv.org/abs/2504.14765), Lopez-Lira et al. 2025, priority: P1
    - Why relevant: direct finance-domain memorization/look-ahead prior art. It argues that forecasting skill is non-identified inside the training window and shows exact-value recall before cutoff.
    - Already in library? yes
    - Recommended action: read
  - [AI's predictable memory in financial analysis](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392), Didisheim et al. 2025, priority: P1
    - Why relevant: journal paper on quantifying look-ahead bias in financial applications via memorization-driven predictability. This is exactly the kind of finance-specific adjacent prior art that a reviewer could reasonably expect.
    - Already in library? no
    - Recommended action: read

### Query 2 - "LLM contamination detection" + "financial forecasting"
- Search method: arXiv API query `all:"contamination" AND all:"financial forecasting"`; web_search terms `"financial forecasting memorization LLM arXiv"`, `"AI's predictable memory in financial analysis"`, `"Total Recall? Evaluating the Macroeconomic Knowledge of Large Language Models"`, and exact-title checks for finance-facing hits.
- Null results: the direct arXiv query itself was nearly empty; relevant papers had to be recovered via broader finance/memorization web_search.
- Hits:
  - [AI's predictable memory in financial analysis](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392), Didisheim et al. 2025, priority: P1
    - Why relevant: proposes a practical proxy for memorization-driven predictability in finance and studies how bias changes with data frequency, model size, and aggregation level.
    - Already in library? no
    - Recommended action: read
  - [The Memorization Problem: Can We Trust LLMs' Economic Forecasts?](https://arxiv.org/abs/2504.14765), Lopez-Lira et al. 2025, priority: P1
    - Why relevant: direct economic/financial forecast contamination argument with recall tests, prompt-instruction failure, and embedding-memory claims.
    - Already in library? yes
    - Recommended action: read
  - [Total Recall? Evaluating the Macroeconomic Knowledge of Large Language Models](https://www.federalreserve.gov/econres/feds/files/2025044pap.pdf), Crane et al. 2025, priority: P2
    - Why relevant: Federal Reserve FEDS paper measuring LLM recall of historical macro values and release dates, with explicit look-ahead and release-timing contamination tests.
    - Already in library? no
    - Recommended action: read
  - [A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs](https://arxiv.org/abs/2512.06607), Merchant and Levy 2025, priority: P1
    - Why relevant: finance-motivated mitigation paper that tries to remove both verbatim and semantic future knowledge at inference time rather than retraining a point-in-time model.
    - Already in library? no
    - Recommended action: read

### Query 3 - "factor-controlled benchmark" + "memorization"
- Search method: arXiv API query `all:"controlled benchmark" AND all:"memorization"`; web_search terms `"factor-controlled benchmark memorization LLM"` and exact-title checks for contamination-benchmark design papers.
- Null results: I did not find a 2024-2026 paper that is genuinely a factor-controlled memorization benchmark in the FinMem-Bench sense.
- Hits:
  - [Benchmarking Large Language Models Under Data Contamination: A Survey from Static to Dynamic Evaluation](https://aclanthology.org/2025.emnlp-main.511/), Chen et al. 2025, priority: P1
    - Why relevant: strong methodological precedent. It explicitly argues that dynamic contamination-aware benchmarks need design principles and standardized criteria.
    - Already in library? no
    - Recommended action: read
  - [Evaluating LLMs in Finance Requires Explicit Bias Consideration](https://arxiv.org/abs/2602.14233), Kong et al. 2026, priority: P1
    - Why relevant: not factor-controlled itself, but it proposes a Structural Validity Framework and checklist for finance evaluation. That is directly useful for benchmark-design justification and reviewer-risk mitigation.
    - Already in library? no
    - Recommended action: read

### Query 4 - "Chinese financial NLP" + "memorization"
- Search method: arXiv API query `all:"Chinese" AND all:"financial" AND all:"LLM" AND all:"memorization"`; web_search terms `"Chinese financial NLP memorization benchmark contamination LLM 2024 2025 2026"`, `"中文 金融 大语言模型 数据污染 基准"`, and exact-title checks for surfaced Chinese finance benchmarks.
- Null results: no verified Chinese financial memorization paper or contamination benchmark surfaced. The only direct arXiv hit was already-known [CFinBench](https://arxiv.org/abs/2407.02301).
- Hits:
  - [FinGAIA: A Chinese Benchmark for AI Agents in Real-World Financial Domain](https://arxiv.org/abs/2507.17186), Zeng et al. 2025, priority: P2
    - Why relevant: Chinese financial benchmark, but agent-focused rather than contamination-focused. Useful mainly as blind-spot context: the Chinese finance benchmark space is moving, just not yet toward memorization-aware evaluation.
    - Already in library? no
    - Recommended action: read
  - [FinMCP-Bench: Benchmarking LLM Agents for Real-World Financial Tool Use under the Model Context Protocol](https://arxiv.org/abs/2603.24943), Zhu et al. 2026, priority: P2
    - Why relevant: another Chinese financial benchmark, again useful mostly as evidence that the Chinese benchmark blind spot is real but currently pointed toward agent/tool evaluation rather than contamination.
    - Already in library? no
    - Recommended action: skip unless Chinese benchmark-mapping is needed

### Query 5 - "cross-model memorization" / "CMMD"
- Search method: arXiv API queries `all:"cross-model" AND all:"memorization"` and `all:"CMMD"`; web_search term `"cross-model memorization LLM 2026 arXiv"` plus exact-title verification.
- Null results: the `CMMD` acronym search was mostly unrelated image/medical noise. The useful signal came from the `cross-model memorization` query.
- Hits:
  - [A Comparative Analysis of LLM Memorization at Statistical and Internal Levels: Cross-Model Commonalities and Model-Specific Signatures](https://arxiv.org/abs/2603.21658), Chen et al. 2026, priority: P1
    - Why relevant: strongest non-finance follow-up I found to cross-model memorization logic. It explicitly studies shared vs family-specific memorization behavior across multiple model series.
    - Already in library? no
    - Recommended action: read

### Query 6 - "look-ahead bias" + "LLM"
- Search method: arXiv API query `all:"look-ahead bias" AND all:"LLM"`; web_search exact-title checks for surfaced 2025-2026 papers.
- Null results: none. This query returned the highest density of useful finance-adjacent hits.
- Hits:
  - [Evaluating LLMs in Finance Requires Explicit Bias Consideration](https://arxiv.org/abs/2602.14233), Kong et al. 2026, priority: P1
    - Why relevant: names look-ahead bias as one of five recurring finance evaluation biases and proposes minimal validity requirements.
    - Already in library? no
    - Recommended action: read
  - [A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs](https://arxiv.org/abs/2512.06607), Merchant and Levy 2025, priority: P1
    - Why relevant: direct mitigation paper for the exact finance backtesting problem, positioned as a cheaper alternative to retraining point-in-time models.
    - Already in library? no
    - Recommended action: read
  - [Do Large Language Models (LLMs) Understand Chronology?](https://arxiv.org/abs/2511.14214), Wongchamcharoen and Glasserman 2025, priority: P1
    - Why relevant: strong prerequisite paper for any prompt-based anti-look-ahead story. If models do not reliably understand chronology, prompt-only historical-boundary instructions are weaker than they look.
    - Already in library? no
    - Recommended action: read
  - [Toward Reliable Evaluation of LLM-Based Financial Multi-Agent Systems: Taxonomy, Coordination Primacy, and Cost Awareness](https://arxiv.org/abs/2603.27539), Nguyen and Pham 2026, priority: P2
    - Why relevant: survey paper that explicitly documents look-ahead bias among five pervasive evaluation failures in financial multi-agent systems.
    - Already in library? no
    - Recommended action: read if the paper will discuss financial-agent evaluation more broadly

### Query 7 - "temporal contamination" + "LLM" + "benchmark"
- Search method: arXiv API query `all:"temporal contamination" AND all:"LLM" AND all:"benchmark"`; web_search terms `"temporal contamination LLM benchmark 2026 arXiv"` and exact-title checks for adjacent live-evaluation work.
- Null results: the direct arXiv query returned one unrelated software-engineering benchmark and no new finance-specific benchmark from the exact string.
- Hits:
  - [LiveTradeBench: Seeking Real-World Alpha with Large Language Models](https://arxiv.org/abs/2511.03628), Yu et al. 2025, priority: P1
    - Why relevant: strong adjacent benchmark precedent because it replaces offline backtesting with live streaming data and explicitly frames this as information-leakage prevention.
    - Already in library? no
    - Recommended action: read
  - [Benchmarking Large Language Models Under Data Contamination: A Survey from Static to Dynamic Evaluation](https://aclanthology.org/2025.emnlp-main.511/), Chen et al. 2025, priority: P1
    - Why relevant: directly relevant methodological synthesis on dynamic benchmarks and contamination-resistant evaluation.
    - Already in library? no
    - Recommended action: read

### Query 8 - "pretraining data detection" + "finance"
- Search method: arXiv API query `all:"pretraining data detection" AND all:"finance"`; web_search terms `"pretraining data detection finance LLM"` and exact-title checks for finance-facing detection papers.
- Null results: the direct arXiv query returned zero 2024-2026 hits.
- Hits:
  - [AI's predictable memory in financial analysis](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392), Didisheim et al. 2025, priority: P1
    - Why relevant: closest finance-facing detection-style paper I found. It uses recall of historical stock returns as a practical memorization proxy.
    - Already in library? no
    - Recommended action: read
  - [The Memorization Problem: Can We Trust LLMs' Economic Forecasts?](https://arxiv.org/abs/2504.14765), Lopez-Lira et al. 2025, priority: P1
    - Why relevant: closest in-library finance paper to pretraining-data detection logic; shows exact-value recall and instruction failure inside the training period.
    - Already in library? yes
    - Recommended action: read

### Query 9 - "news coverage" + "LLM" + "memorization"
- Search method: arXiv API queries `all:"news coverage" AND all:"LLM" AND all:"memorization"`, `all:"media coverage" AND all:"LLM" AND all:"memorization"`, and `all:"news prevalence" AND all:"memorization"`; web_search terms `"news coverage LLM memorization"`, `"media coverage LLM memorization"`, and `"news prevalence memorization"`.
- Null results: no direct 2024-2026 paper surfaced that validates media/news coverage breadth as an explicit LLM memorization factor.
- Hits:
  - [Uncovering Representation Bias for Investment Decisions in Open-Source Large Language Models](https://arxiv.org/abs/2510.05702), Dimino et al. 2025, priority: P2
    - Why relevant: indirect support only. It shows firm size, valuation, and sector strongly influence model confidence, which is adjacent to visibility/prominence effects but not a direct media-coverage memorization paper.
    - Already in library? no
    - Recommended action: skip unless the A-queued coverage-breadth concept is revisited

### Query 10 - "entity anonymization" + "LLM" + "bias"
- Search method: arXiv API query `all:"entity anonymization" AND all:"LLM" AND all:"bias"`; web_search terms `"entity anonymization LLM finance bias arXiv"`, `"company-specific bias financial sentiment LLM 2025 arXiv"`, and exact-title verification.
- Null results: the direct arXiv query returned zero hits. The useful result came from web_search exact-title recovery.
- Hits:
  - [Anonymization and Information Loss](https://arxiv.org/abs/2511.15364), Wu et al. 2025, priority: P1
    - Why relevant: direct finance follow-up on anonymization. It argues that anonymization-induced information loss can be more severe than look-ahead bias in earnings-call sentiment extraction.
    - Already in library? no
    - Recommended action: read

### Query 11 - "Chinese" + "financial news" + "benchmark" + "contamination"
- Search method: arXiv API query `all:"Chinese" AND all:"financial news" AND all:"benchmark" AND all:"contamination"`; web_search terms `"中文 金融 新闻 大模型 污染 基准"`, `"Chinese financial news benchmark contamination LLM"`, and exact-title checks for surfaced Chinese finance benchmarks.
- Null results: no verified Chinese financial news contamination benchmark surfaced.
- Hits:
  - [FinGAIA: A Chinese Benchmark for AI Agents in Real-World Financial Domain](https://arxiv.org/abs/2507.17186), Zeng et al. 2025, priority: P2
    - Why relevant: closest Chinese financial benchmark hit from this search family, but not news-specific and not contamination-aware.
    - Already in library? no
    - Recommended action: skip unless mapping the Chinese benchmark landscape
  - [FinMCP-Bench: Benchmarking LLM Agents for Real-World Financial Tool Use under the Model Context Protocol](https://arxiv.org/abs/2603.24943), Zhu et al. 2026, priority: P2
    - Why relevant: closest 2026 Chinese financial benchmark hit, again not news-specific and not contamination-aware.
    - Already in library? no
    - Recommended action: skip unless mapping the Chinese benchmark landscape

### Query 12 - "disclosure" + "source type" + "LLM" + "evaluation"
- Search method: arXiv API query `all:"disclosure" AND all:"source type" AND all:"LLM" AND all:"evaluation"`; web_search terms `"disclosure source type LLM evaluation finance"`, `"source disclosure LLM evaluation"`, and `"financial disclosure quality benchmark Chinese LLM"`.
- Null results: I found no memorization or contamination benchmark that validates disclosure regime / source type as a leakage factor.
- Hits:
  - [FinTruthQA: A Benchmark for AI-Driven Financial Disclosure Quality Assessment in Investor -- Firm Interactions](https://arxiv.org/abs/2406.12009), Zhou et al. 2024, priority: P2
    - Why relevant: closest in-domain disclosure benchmark I found. It is Chinese and finance-specific, but disclosure-quality focused rather than contamination-focused.
    - Already in library? no
    - Recommended action: read if the paper needs disclosure-task related work
  - [Reference decisions enhance LLM performance, amplified by source disclosure](https://journals.sagepub.com/doi/10.1177/20552076251342078), Zhang et al. 2025, priority: P2
    - Why relevant: outside finance, but directly shows that source disclosure changes LLM performance in a controlled factorial study. This is indirect methodological evidence for source-type effects.
    - Already in library? no
    - Recommended action: skip unless defending the Disclosure Regime concept

### Query 13 - browse 2026-Q1 arXiv cs.CL + q-fin.GN recent listings
- Search method: arXiv API category browse over `cat:cs.CL` and `cat:q-fin.GN`, `sortBy=submittedDate`, `sortOrder=descending`, `max_results=120`, filtered to the last 3 months before 2026-04-14 and manually scanned for `benchmark`, `memorization`, `contamination`, `leakage`, `look-ahead`, `temporal`, `finance`, and `forecast`.
- Null results: no new P0 benchmark-clone surfaced from the recency browse.
- Hits:
  - [Evaluating LLMs in Finance Requires Explicit Bias Consideration](https://arxiv.org/abs/2602.14233), Kong et al. 2026, priority: P1
    - Why relevant: strongest 2026-Q1 finance-evaluation framework hit.
    - Already in library? no
    - Recommended action: read
  - [A Comparative Analysis of LLM Memorization at Statistical and Internal Levels: Cross-Model Commonalities and Model-Specific Signatures](https://arxiv.org/abs/2603.21658), Chen et al. 2026, priority: P1
    - Why relevant: strongest memorization-focused cs.CL hit from the recency browse.
    - Already in library? no
    - Recommended action: read
  - [Toward Reliable Evaluation of LLM-Based Financial Multi-Agent Systems: Taxonomy, Coordination Primacy, and Cost Awareness](https://arxiv.org/abs/2603.27539), Nguyen and Pham 2026, priority: P2
    - Why relevant: useful if the paper needs up-to-date adjacent evaluation criticism in financial LLM systems.
    - Already in library? no
    - Recommended action: read if expanding adjacent-work coverage
  - [FinMCP-Bench: Benchmarking LLM Agents for Real-World Financial Tool Use under the Model Context Protocol](https://arxiv.org/abs/2603.24943), Zhu et al. 2026, priority: P2
    - Why relevant: notable Chinese-finance benchmark release, but outside the contamination/memorization problem family.
    - Already in library? no
    - Recommended action: skip unless mapping benchmark space

### Query 14 - Semantic Scholar citing-paper sweep
- Search method: Semantic Scholar Graph API
  - `https://api.semanticscholar.org/graph/v1/paper/arXiv:2603.26797?fields=title,year,citations.title,citations.year,citations.externalIds,citations.abstract`
  - `https://api.semanticscholar.org/graph/v1/paper/arXiv:2510.07920?fields=title,year,citations.title,citations.year,citations.externalIds,citations.abstract`
- Null results:
  - MemGuard-Alpha ([arXiv:2603.26797](https://arxiv.org/abs/2603.26797)) had zero Semantic Scholar citations in-session as of 2026-04-14.
- Hits:
  - [All Leaks Count, Some Count More: Interpretable Temporal Contamination Detection in LLM Backtesting](https://arxiv.org/abs/2602.17234), Zhang et al. 2026, priority: P1
    - Why relevant: cites Profit Mirage and proposes claim-level leakage detection plus a filtering pipeline. Already known in-library, but the citation edge confirms reviewer-visible adjacency.
    - Already in library? yes
    - Recommended action: read if not already read
  - [LiveTradeBench: Seeking Real-World Alpha with Large Language Models](https://arxiv.org/abs/2511.03628), Yu et al. 2025, priority: P1
    - Why relevant: cites Profit Mirage and shifts from static/offline evaluation to live markets, making it a relevant adjacent benchmark comparator.
    - Already in library? no
    - Recommended action: read

## Direct competitors discovered
- None newly discovered.
- I did not find a new benchmark that is simultaneously Chinese-financial, memorization-aware, and factor-controlled in the FinMem-Bench design space.
- Closest adjacent benchmarks from this sweep were [LiveTradeBench](https://arxiv.org/abs/2511.03628), [FinGAIA](https://arxiv.org/abs/2507.17186), [FinMCP-Bench](https://arxiv.org/abs/2603.24943), and [XFinBench](https://aclanthology.org/2025.findings-acl.457/), but none matches the core FinMem-Bench problem formulation.

## Methodological precedents for factor-controlled benchmark design
- [Benchmarking Large Language Models Under Data Contamination: A Survey from Static to Dynamic Evaluation](https://aclanthology.org/2025.emnlp-main.511/) (P1)
  - Explicitly argues that dynamic contamination-aware benchmarks need standardized design principles rather than ad hoc freshness claims.
- [Evaluating LLMs in Finance Requires Explicit Bias Consideration](https://arxiv.org/abs/2602.14233) (P1)
  - Strongest finance-specific framework paper found in this sweep. It is directly useful for structural-validity language in the paper.
- [LiveTradeBench: Seeking Real-World Alpha with Large Language Models](https://arxiv.org/abs/2511.03628) (P1)
  - Important adjacent precedent for replacing leakage-prone offline backtests with live evaluation.
- [Toward Reliable Evaluation of LLM-Based Financial Multi-Agent Systems: Taxonomy, Coordination Primacy, and Cost Awareness](https://arxiv.org/abs/2603.27539) (P2)
  - Useful adjacent survey framing on evaluation failure modes in financial LLM systems.

## Citing-paper sweep
### Citing MemGuard-Alpha (arXiv 2603.26797)
- None found via Semantic Scholar API as of 2026-04-14.

### Citing Profit Mirage (arXiv 2510.07920)
- [All Leaks Count, Some Count More: Interpretable Temporal Contamination Detection in LLM Backtesting](https://arxiv.org/abs/2602.17234), priority: P1
- [LiveTradeBench: Seeking Real-World Alpha with Large Language Models](https://arxiv.org/abs/2511.03628), priority: P1

## Candidate new-factor queue
- None beyond the two candidate concepts already queued by Sub-task A.
- Evidence that strengthens A's existing queue only:
  - [Anonymization and Information Loss](https://arxiv.org/abs/2511.15364) strengthens the already-queued `Entity-Anonymization Sensitivity` concept.
  - [Uncovering Representation Bias for Investment Decisions in Open-Source Large Language Models](https://arxiv.org/abs/2510.05702) gives indirect support to the already-queued `Coverage Breadth / Media Coverage` idea via size/visibility-driven confidence, but it does not validate a clean news-coverage memorization factor.

## PDF download candidates (for user approval - do NOT auto-download)
- P1: [AI's predictable memory in financial analysis](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392)
  - Why: finance-specific journal paper on memorization-driven predictability and look-ahead bias measurement; not in library.
- P1: [A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs](https://arxiv.org/abs/2512.06607)
  - Why: direct mitigation paper for finance backtesting contamination; not in library.
- P1: [Evaluating LLMs in Finance Requires Explicit Bias Consideration](https://arxiv.org/abs/2602.14233)
  - Why: strongest finance-evaluation framework paper found in this sweep; not in library.
- P1: [Do Large Language Models (LLMs) Understand Chronology?](https://arxiv.org/abs/2511.14214)
  - Why: directly tests a hidden assumption behind prompt-based anti-leakage protocols; not in library.
- P1: [Anonymization and Information Loss](https://arxiv.org/abs/2511.15364)
  - Why: direct finance follow-up on anonymization vs look-ahead tradeoffs; not in library.
- P1: [LiveTradeBench: Seeking Real-World Alpha with Large Language Models](https://arxiv.org/abs/2511.03628)
  - Why: reviewer-visible adjacent live benchmark; not in library.
- P1: [A Comparative Analysis of LLM Memorization at Statistical and Internal Levels: Cross-Model Commonalities and Model-Specific Signatures](https://arxiv.org/abs/2603.21658)
  - Why: strongest cross-model memorization follow-up surfaced; not in library.
- P1: [Benchmarking Large Language Models Under Data Contamination: A Survey from Static to Dynamic Evaluation](https://aclanthology.org/2025.emnlp-main.511/)
  - Why: methodological benchmark-design synthesis; not in library.
- P2: [Total Recall? Evaluating the Macroeconomic Knowledge of Large Language Models](https://www.federalreserve.gov/econres/feds/files/2025044pap.pdf)
  - Why: useful macro look-ahead and release-date contamination paper; not in library.

## Sweep-B summary memo
- Biggest findings
  - No new P0 direct benchmark competitor surfaced. I did not find a new Chinese-financial, memorization-aware, factor-controlled benchmark that would collapse FinMem-Bench's novelty claim.
  - The strongest new P1 additions were [AI's predictable memory in financial analysis](https://econpapers.repec.org/RePEc:eee:ecolet:v:256:y:2025:i:c:s0165176525004392), [A Fast and Effective Solution to the Problem of Look-ahead Bias in LLMs](https://arxiv.org/abs/2512.06607), [Evaluating LLMs in Finance Requires Explicit Bias Consideration](https://arxiv.org/abs/2602.14233), [Do Large Language Models (LLMs) Understand Chronology?](https://arxiv.org/abs/2511.14214), [Anonymization and Information Loss](https://arxiv.org/abs/2511.15364), [LiveTradeBench](https://arxiv.org/abs/2511.03628), and [A Comparative Analysis of LLM Memorization at Statistical and Internal Levels](https://arxiv.org/abs/2603.21658).
  - The Chinese blind spot remains open: I found Chinese financial benchmarks, but no Chinese financial news contamination benchmark.
  - The `Coverage Breadth / Media Coverage` and `Disclosure Regime` probes remained mostly null. I found only indirect support, not direct validation as memorization factors.
  - MemGuard-Alpha currently has zero Semantic Scholar citations in-session; Profit Mirage already has citation edges into [All Leaks Count](https://arxiv.org/abs/2602.17234) and [LiveTradeBench](https://arxiv.org/abs/2511.03628).
- What we still don't know
  - CNKI-first or paywalled Chinese literature may still hide relevant non-arXiv contamination work.
  - Whether any venue-only 2026 finance paper appears after 2026-04-14 that explicitly cites MemGuard-Alpha.
  - Whether there is a stable primary-source paper for `BizFinBench`; I saw secondary references but did not verify a primary citable paper in-session, so I excluded it.
- Top priority recommendations for the user
  - Add the new P1 papers above to the R5 reading/citation queue, especially `AI's predictable memory`, `Anonymization and Information Loss`, `Evaluating LLMs in Finance Requires Explicit Bias Consideration`, `A Fast and Effective Solution`, `Do LLMs Understand Chronology?`, and `LiveTradeBench`.
  - Keep the paper's novelty claim narrow and precise: I found no new direct competitor, but the adjacent finance look-ahead / validity literature is now visibly denser than the R4 materials suggested.
  - If the paper discusses Disclosure Regime or entity anonymization, cite the new indirect evidence carefully and do not overstate it as settled memorization-factor precedent.
