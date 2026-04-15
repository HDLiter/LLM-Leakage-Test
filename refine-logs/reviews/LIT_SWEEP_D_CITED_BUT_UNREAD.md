# Sub-task D — Cited-but-Unread Sweep
Date: 2026-04-15
Persona: senior NLP / memorization researcher, fresh (no R1-R4 attachment)
Search method: Semantic Scholar Graph API for reference lists, cross-checked against `related papers/INDEX.md`, with arXiv HTML/PDF bibliography fallback when Semantic Scholar rate-limited or returned incomplete coverage

## URGENT findings (if any)
None this sub-task.

The strongest backward-reference misses are methodology papers, not hidden benchmark competitors: classic membership-inference foundations, newer Min-K/MIA follow-ups, and a small chrono-control cluster (`Time Machine GPT`, `Lookahead Bias in Pretrained Language Models`, `StoriesLM`, `Caution Ahead`).

## Methodology summary
- Seed papers successfully queried: 10/10
- Query mix:
  - 6 seeds via Semantic Scholar Graph API direct reference lists
  - 3 seeds via arXiv HTML bibliography fallback (`Profit Mirage`, `Dated Data`, `Set the Clock`)
  - 1 seed via arXiv PDF bibliography fallback (`MemGuard-Alpha`) after Semantic Scholar 429/incomplete coverage
- Total outgoing references collected across the 10 seeds: 334
- Unique cited papers after seed-to-seed deduplication: 292
- Unique papers not already in `INDEX.md` + the 4 notes files: 273
- Remaining after also excluding titles already surfaced in Sweep B: 271
- Priority triage on the 271 remaining titles:
  - P0: 0
  - P1: 10
  - P2: 7
  - P3: 254

Notes:
- I used conservative alias handling for title drift already known in the library, e.g. `Detecting Pretraining Data from Large Language Models`, `The Secret Sharer`, `Can ChatGPT Forecast Stock Price Movements?`, `Anonymization and Information Loss`, and `Chronologically Consistent Large Language Models`.
- One naming mismatch is worth a manual look later: the seed `Deduplicating Training Data Mitigates Privacy Risks` does not appear verbatim in `INDEX.md`; I treated it as a seed and did not count it as a download candidate.

## Seed-by-seed reference extraction

### Seed 1 — MemGuard-Alpha (arxiv 2603.26797)
- Total references: 30
- Already in library: 13
- Already surfaced by Sweep B: 1
- New candidates by priority:
  - P1: `Membership Inference Attacks From First Principles`; `Min-K%++`; `Inherent Challenges of Post-Hoc Membership Inference for Large Language Models` (MemGuard cites the older title `SoK: Membership Inference Attacks on LLMs are Rushing Nowhere ...`); `Time Machine GPT`; `Lookahead Bias in Pretrained Language Models`
  - P2: `Entity Neutering`; `Caution Ahead`; `Can Blindfolded LLMs Still Trade?`
- Interesting cross-seed observations:
  - This is the single most useful backward list.
  - Its unseen references cluster around practical MIA/pretraining-data detection and finance-specific chrono mitigation, not another hidden direct benchmark competitor.

### Seed 2 — Profit Mirage (arxiv 2510.07920)
- Total references: 36
- Already in library: 0
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - No new P1 after excluding Sweep-B titles.
  - P2: `BloombergGPT`; `Financial Statement Analysis with Large Language Models`
- Interesting cross-seed observations:
  - The backward list is mostly finance-LLM application context and generic model infrastructure, not contamination-detection method work.

### Seed 3 — Dated Data (arxiv 2403.12958)
- Total references: 38
- Already in library: 0
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - P1: `RealTime QA: What's the Answer Right Now?`
  - P2: `Datasheets for Datasets`; `Model Cards for Model Reporting`
- Interesting cross-seed observations:
  - This seed points backward into temporal-QA benchmark design and evaluation/reporting infrastructure more than into finance work.

### Seed 4 — Set the Clock (arxiv 2402.16797)
- Total references: 42
- Already in library: 0
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - P1: `RealTime QA: What's the Answer Right Now?`
  - P2: `Templama`; `TSQA`; `SituatedQA`
- Interesting cross-seed observations:
  - The main blind spot here is the temporal-QA benchmark lineage, not another look-ahead finance paper.

### Seed 5 — Chronologically Consistent LLMs / ChronoBERT (arxiv 2502.21206)
- Total references: 40
- Already in library: 3
- Already surfaced by Sweep B: 1
- New candidates by priority:
  - P1: `StoriesLM`; `Lookahead Bias in Pretrained Language Models`; `Caution Ahead`
  - P2: `Giving Content to Investor Sentiment`; `More than Words`; `Predicting Returns with Text Data`
- Interesting cross-seed observations:
  - This seed is the clearest bridge between chrono-control work and classical finance text-return literature.

### Seed 6 — DatedGPT (arxiv 2603.11838)
- Total references: 27
- Already in library: 2
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - P1: `StoriesLM`
  - P2: `Entity Neutering`; `The FineWeb Datasets`
- Interesting cross-seed observations:
  - The backward list leans toward data curation / model-construction precursors rather than contamination benchmarks.

### Seed 7 — Quantifying Memorization Across Neural LMs (arxiv 2202.07646)
- Total references: 32
- Already in library: 5
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - P1: `Membership Inference Attacks Against Machine Learning Models`; `How Much Do Language Models Copy From Their Training Data?` (RAVEN)
  - P2: `Privacy Risk in Machine Learning`; `Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures`
- Interesting cross-seed observations:
  - This seed pushes directly into privacy-attack foundations that the current library under-covers.

### Seed 8 — Deduplicating Training Data Mitigates Privacy Risks (arxiv 2202.06539)
- Total references: 41
- Already in library: 6
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - P1: `Membership Inference Attacks Against Machine Learning Models`; `Membership Inference Attacks From First Principles`; `How Much Do Language Models Copy From Their Training Data?` (RAVEN)
  - P2: `Privacy Risk in Machine Learning`
- Interesting cross-seed observations:
  - This is the strongest bridge from memorization/duplication into the older privacy/MIA literature.

### Seed 9 — Entity-level Memorization in LLMs (arxiv 2308.15727)
- Total references: 32
- Already in library: 5
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - No strong new P1 beyond the broader Kandpal/RAVEN/MIA cluster already surfaced elsewhere.
  - P2: `Quantifying Association Capabilities of Large Language Models and Its Implications on Privacy Leakage`
- Interesting cross-seed observations:
  - The backwards list is surprisingly generic-LM-heavy; the distinctive missing paper is the association/privacy-leakage angle rather than a separate entity-bias benchmark.

### Seed 10 — Assessing Look-Ahead Bias via GPT Sentiment (arxiv 2309.17322)
- Total references: 16
- Already in library: 2
- Already surfaced by Sweep B: 0
- New candidates by priority:
  - P1: `Memorization Without Overfitting`
  - P2: `Giving Content to Investor Sentiment`; `More than Words`; `Predicting Returns with Text Data`
- Interesting cross-seed observations:
  - This seed is the cleanest path into pre-LLM finance text-return baselines that still matter for framing look-ahead/bias papers.

## Cross-seed co-citation analysis
- Papers cited by 3+ seeds:
  - `Language Models are Unsupervised Multitask Learners` (Seeds 5, 6, 8)
  - `Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer` (Seeds 7, 8, 9)
  - `The Pile` (Seeds 7, 8, 9)
  - Judgment: all three are background model/data papers, not reviewer-killer missed prior art for FinMem-Bench.
- Papers cited by 2 seeds with substantive relevance:
  - `Membership Inference Attacks Against Machine Learning Models` (Seeds 7, 8)
  - `Membership Inference Attacks From First Principles` (Seeds 1, 8)
  - `How Much Do Language Models Copy From Their Training Data?` / RAVEN (Seeds 7, 8)
  - `StoriesLM` (Seeds 5, 6)
  - `Giving Content to Investor Sentiment` (Seeds 5, 10)
  - `More than Words` (Seeds 5, 10)
  - `Predicting Returns with Text Data` (Seeds 5, 10)
  - `Caution Ahead` (Seeds 1, 5)
- Noteworthy chrono ↔ memorization cross-domain edges:
  - `Giving Content to Investor Sentiment`, `More than Words`, and `Predicting Returns with Text Data` are cited by both a chrono-controlled seed (`Chronologically Consistent LLMs`) and an entity/look-ahead seed (`Assessing Look-Ahead Bias via GPT Sentiment`).
  - The privacy/MIA cluster (`Membership Inference...`, `RAVEN`) is cited by memorization seeds rather than chrono-control seeds, which is exactly the blind spot MemGuard makes newly operational in finance.

## PDF download candidates (for user approval — do NOT auto-download)

### P0 — must get
- None this sub-task.

### P1 — strongly recommended
- [Membership Inference Attacks Against Machine Learning Models](https://arxiv.org/abs/1610.05820), Shokri et al., 2016/2017, `arXiv:1610.05820`, citation count: 5056
  - Why: classic MIA foundation cited by both `Quantifying Memorization...` and `Deduplicating Training Data Mitigates Privacy Risks`; the most obvious missing privacy-method precursor to MemGuard-style contamination scoring.
  - Seeds: 7, 8
- [Membership Inference Attacks From First Principles](https://arxiv.org/abs/2112.03570), Carlini et al., 2021/2022, `arXiv:2112.03570`, citation count: 1026
  - Why: strongest post-Shokri MIA baseline in the backward graph; MemGuard explicitly builds on it and Kandpal also cites it.
  - Seeds: 1, 8
- [Min-K%++: Improved Baseline for Detecting Pre-Training Data from Large Language Models](https://arxiv.org/abs/2404.02936), Zhang et al., 2024/2025, `arXiv:2404.02936`, citation count: not recovered in-session
  - Why: direct detector-family follow-up to the library’s Min-K% paper; MemGuard treats it as one of its core MIA components.
  - Seeds: 1
- [Inherent Challenges of Post-Hoc Membership Inference for Large Language Models](https://arxiv.org/abs/2406.17975), Meeus et al., 2024, `arXiv:2406.17975`, citation count: not recovered in-session
  - Why: MemGuard cites this under the earlier title `SoK: Membership Inference Attacks on LLMs are Rushing Nowhere (and How to Fix It)`; worth reading because it is the skepticism/limitations paper for exactly the MIA family MemGuard operationalizes.
  - Seeds: 1
- [Time Machine GPT](https://arxiv.org/abs/2404.18543), Drinkall et al., 2024, `arXiv:2404.18543`, citation count: not recovered in-session
  - Why: direct chrono-control precursor cited by MemGuard; fills a gap between general temporal benchmarks and finance-facing point-in-time model construction.
  - Seeds: 1
- [Lookahead Bias in Pretrained Language Models](https://ssrn.com/abstract=4754678), Sarkar and Vafa, 2024, SSRN, citation count: not recovered in-session
  - Why: direct conceptual predecessor to chrono-controlled finance evaluation; cited by ChronoBERT and MemGuard.
  - Seeds: 1, 5
- [Caution Ahead: Numerical Reasoning and Look-ahead Bias in AI Models](https://ssrn.com/abstract=5082861), Bradford (Lynch) Levy, 2025, SSRN, citation count: not recovered in-session
  - Why: narrow but on-target finance look-ahead follow-up, cited by both ChronoBERT and MemGuard.
  - Seeds: 1, 5
- [How Much Do Language Models Copy From Their Training Data? Evaluating Linguistic Novelty in Text Generation Using RAVEN](https://aclanthology.org/2023.tacl-1.38/), McCoy et al., 2021, TACL, citation count: 167
  - Why: direct cited-but-unread bridge between memorization and output novelty/copying; cited by both `Quantifying Memorization...` and Kandpal.
  - Seeds: 7, 8
- [Memorization Without Overfitting: Analyzing the Training Dynamics of Large Language Models](https://arxiv.org/abs/2205.10770), Tirumala et al., 2022, `arXiv:2205.10770`, citation count: 259
  - Why: Glasserman & Lin cite it to connect finance look-ahead concerns back to memorization dynamics; useful for theory framing, not just benchmarking.
  - Seeds: 10
- [RealTime QA: What's the Answer Right Now?](https://arxiv.org/abs/2207.13332), Kasai et al., 2022, `arXiv:2207.13332`, citation count: 277
  - Why: direct temporal-QA benchmark precursor surfaced by the cutoff-exposure seeds; worth reading if FinMem-Bench discusses temporal-evaluation lineage rather than only finance papers.
  - Seeds: 4

### P2 — worth noting
- [Entity Neutering: Removing Identifying Information for LLM Bias Mitigation](https://ssrn.com/abstract=5182756), Engelberg et al., 2025, SSRN, citation count: not recovered in-session
  - Why: cited by the chrono-control seeds, and MemGuard cites the fuller title variant; this is direct additional evidence for the already-queued `Entity-Anonymization Sensitivity` concept.
  - Seeds: 5, 6; MemGuard cites a fuller title variant
- `StoriesLM: A family of language models with time-indexed training data`, Sarkar, 2024, SSRN Electronic Journal, citation count: not recovered in-session
  - Why: cited by both `Chronologically Consistent LLMs` and `DatedGPT`; a chrono-model predecessor worth knowing even though I did not recover a stable primary URL in-session.
  - Seeds: 5, 6
- `Giving Content to Investor Sentiment: The Role of Media in the Stock Market`, Tetlock, 2007, citation count: 4079
  - Why: old but still visibly upstream of both chrono-control and look-ahead-sentiment work.
  - Seeds: 5, 10
- `More than Words: Quantifying Language to Measure Firms' Fundamentals`, Tetlock, Saar-Tsechansky, and Macskassy, 2008, citation count: 2137
  - Why: same reason as Tetlock 2007; classical finance text baseline still echoed in modern chrono/look-ahead papers.
  - Seeds: 5, 10
- [Predicting Returns with Text Data](https://ssrn.com/abstract=3431434), Ke, Kelly, and Xiu, 2019, SSRN, citation count: 131
  - Why: the more modern text-return bridge paper cited by both ChronoBERT and Glasserman & Lin.
  - Seeds: 5, 10
- `Privacy Risk in Machine Learning: Analyzing the Connection to Overfitting`, Yeom et al., 2017, citation count: 1449
  - Why: classic general privacy/MIA framing paper behind the memorization-privacy bridge.
  - Seeds: 7, 8
- `Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures`, Fredrikson et al., 2015, citation count: 3221
  - Why: not language-model-specific, but part of the same privacy-attack ancestry cited by the core memorization papers.
  - Seeds: 7, 8

## Candidate new-factor queue (if any)
None.

Evidence that only strengthens already-queued concepts:
- `Entity Neutering` is additional cited-but-unread support for the already-queued `Entity-Anonymization Sensitivity` idea.
- The finance-text classics (`Giving Content...`, `More than Words`, `Predicting Returns with Text Data`) are visibility/coverage-adjacent, but they are not clean enough evidence to open a new factor beyond the existing queue.

## Sweep-D summary memo
- Biggest findings
  - No hidden direct benchmark competitor surfaced from the seed bibliographies.
  - The clearest misses are older privacy/MIA papers plus a small cluster of finance-specific chrono-control papers that MemGuard now makes operationally relevant.
  - MemGuard-Alpha’s bibliography is the most useful single backward list; it points straight at `MIA from First Principles`, `Min-K%++`, the `SoK/Inherent Challenges` paper, `Time Machine GPT`, and `Lookahead Bias in Pretrained Language Models`.
  - The chrono-control seeds unexpectedly pull in classical finance text-return papers (`Tetlock 2007`, `More than Words`, `Predicting Returns with Text Data`), which means the chrono-control story is more tightly connected to old finance NLP than the current library suggests.
  - The 3+ co-cited misses (`GPT-2`, `T5`, `The Pile` tier papers) are generic infrastructure, not novelty-threatening reviewer killers.
- What the seed reference lists revealed about blind spots
  - The library is thinner on privacy/MIA foundations than on extraction papers.
  - The library is also thinner on chrono-control predecessors than on chrono-control contemporaries.
  - Finance-specific look-ahead follow-ups around numerical reasoning and anonymization are still easy to miss unless one walks backward from MemGuard/ChronoBERT.
- Top priority recommendations for the user
  - Download the 10 P1 papers above before R5, especially the two classic MIA papers, `Min-K%++`, the `SoK/Inherent Challenges` paper, `Time Machine GPT`, and `Lookahead Bias in Pretrained Language Models`.
  - If the paper’s related-work section claims coverage of the memorization/privacy lineage, add `Shokri 2016/2017`, `Carlini et al. 2021/2022`, and `RAVEN` explicitly.
  - If the paper’s related-work section claims coverage of chrono-control evaluation, add `Time Machine GPT`, `Lookahead Bias in Pretrained Language Models`, and `Caution Ahead` explicitly.
  - Keep the novelty claim narrow: no new direct competitor appeared, but the backwards references make the methodology ancestry denser than the current library alone would suggest.
